"""工单管理接口：提交（自动归类）、查询、处理、流转、类型维护。"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_permission
from ..models import Organization, Ticket, TicketLog, TicketType, User
from ..schemas import (
    ClassifyRequest,
    TicketCreate,
    TicketHandleRequest,
    TicketOut,
    TicketTypeCreate,
    TicketTypeOut,
    TicketTypeUpdate,
    TicketUpdate,
)
from ..services.classifier import classify_ticket

router = APIRouter(prefix="/tickets", tags=["工单"])

# 状态可推进关系
_NEXT = {
    "pending": {"processing", "resolved"},
    "processing": {"resolved"},
    "resolved": {"closed"},
    "closed": set(),
}


def _gen_code(db: Session) -> str:
    """生成工单编号 GD-YYYYMMDD-序号。"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"GD-{today}-"
    last = (
        db.query(Ticket)
        .filter(Ticket.code.like(f"{prefix}%"))
        .order_by(Ticket.code.desc())
        .first()
    )
    seq = 1
    if last and last.code[-4:].isdigit():
        seq = int(last.code[-4:]) + 1
    return f"{prefix}{seq:04d}"


def _add_log(db: Session, ticket: Ticket, action: str, operator: Optional[User], remark: Optional[str] = None):
    db.add(TicketLog(ticket_id=ticket.id, action=action, operator_id=operator.id if operator else None, remark=remark))


def _read_permission(user: User) -> str:
    """读取工单：拥有 ticket:read_all 可看全部，否则只能看自己提交的。"""
    codes = {p.code for p in (user.role.permissions if user.role else [])}
    if "ticket:read_all" in codes:
        return "all"
    return "own"


# ---------- 工单类型 ----------
@router.get("/types", response_model=List[TicketTypeOut])
def list_types(db: Session = Depends(get_db)):
    return db.query(TicketType).order_by(TicketType.sort, TicketType.id).all()


@router.post("/types", response_model=TicketTypeOut, status_code=201)
def create_type(
    data: TicketTypeCreate,
    _: User = Depends(require_permission("ticket:manage")),
    db: Session = Depends(get_db),
):
    if db.query(TicketType).filter(TicketType.code == data.code).first():
        raise HTTPException(400, "类型编码已存在")
    t = TicketType(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/types/{type_id}", response_model=TicketTypeOut)
def update_type(
    type_id: int,
    data: TicketTypeUpdate,
    _: User = Depends(require_permission("ticket:manage")),
    db: Session = Depends(get_db),
):
    t = db.get(TicketType, type_id)
    if not t:
        raise HTTPException(404, "类型不存在")
    for field in ("name", "keywords", "sort", "description"):
        val = getattr(data, field)
        if val is not None:
            setattr(t, field, val)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/types/{type_id}", response_model=dict)
def delete_type(
    type_id: int,
    _: User = Depends(require_permission("ticket:manage")),
    db: Session = Depends(get_db),
):
    t = db.get(TicketType, type_id)
    if not t:
        raise HTTPException(404, "类型不存在")
    db.delete(t)
    db.commit()
    return {"ok": True}


# ---------- 工单 ----------
@router.get("", response_model=List[TicketOut])
def list_tickets(
    status: Optional[str] = Query(None),
    type_id: Optional[int] = Query(None),
    org_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None, description="标题/编号/描述搜索"),
    mine: bool = Query(False, description="只看我提交的"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Ticket)
    scope = _read_permission(user)
    if scope == "own" or mine:
        q = q.filter(Ticket.creator_id == user.id)
    if status:
        q = q.filter(Ticket.status == status)
    if type_id:
        q = q.filter(Ticket.type_id == type_id)
    if org_id:
        q = q.filter(Ticket.site_org_id == org_id)
    if priority:
        q = q.filter(Ticket.priority == priority)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Ticket.title.like(like)) | (Ticket.code.like(like)) | (Ticket.description.like(like)))
    return q.order_by(Ticket.id.desc()).limit(500).all()


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "工单不存在")
    if _read_permission(user) == "own" and t.creator_id != user.id:
        raise HTTPException(403, "只能查看自己提交的工单")
    return t


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    data: TicketCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 自动归类：未指定类型时，由系统根据标题/描述自动判定
    type_id = data.type_id
    if not type_id:
        matched = classify_ticket(db, data.title, data.description)
        type_id = matched.id if matched else None

    site_org_id = data.site_org_id or user.org_id

    ticket = Ticket(
        code=_gen_code(db),
        title=data.title,
        description=data.description,
        type_id=type_id,
        priority=data.priority,
        status="pending",
        creator_id=user.id,
        site_org_id=site_org_id,
    )
    db.add(ticket)
    db.flush()
    _add_log(db, ticket, "create", user, "提交工单")
    db.commit()
    db.refresh(ticket)
    return ticket


@router.put("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "工单不存在")
    if _read_permission(user) == "own" and t.creator_id != user.id:
        raise HTTPException(403, "无权修改")
    changed = False
    if data.title is not None and data.title != t.title:
        t.title = data.title
        changed = True
    if data.description is not None and data.description != t.description:
        t.description = data.description
        changed = True
    if data.priority is not None and data.priority != t.priority:
        t.priority = data.priority
        changed = True
    if data.type_id is not None and data.type_id != t.type_id:
        t.type_id = data.type_id
        _add_log(db, t, "classify", user, "手动调整类型")
        changed = True
    if data.assignee_id is not None and data.assignee_id != t.assignee_id:
        t.assignee_id = data.assignee_id
        _add_log(db, t, "assign", user, "指派处理人")
        changed = True
    if changed:
        db.commit()
        db.refresh(t)
    return t


@router.put("/{ticket_id}/classify", response_model=TicketOut)
def reclassify(
    ticket_id: int,
    data: ClassifyRequest,
    user: User = Depends(require_permission("ticket:handle")),
    db: Session = Depends(get_db),
):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "工单不存在")
    t.type_id = data.type_id
    _add_log(db, t, "classify", user, "重新归类")
    db.commit()
    db.refresh(t)
    return t


@router.put("/{ticket_id}/handle", response_model=TicketOut)
def handle_ticket(
    ticket_id: int,
    data: TicketHandleRequest,
    user: User = Depends(require_permission("ticket:handle")),
    db: Session = Depends(get_db),
):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "工单不存在")
    if data.status not in _NEXT.get(t.status, set()):
        raise HTTPException(400, f"不允许从「{t.status}」直接变更为「{data.status}」")

    t.status = data.status
    if data.resolution is not None:
        t.resolution = data.resolution
    if data.assignee_id is not None:
        t.assignee_id = data.assignee_id
        _add_log(db, t, "assign", user, "指派处理人")
    if data.status == "resolved":
        t.resolved_at = datetime.now()
    if data.status == "closed":
        t.closed_at = datetime.now()

    label = {"processing": "开始处理", "resolved": "标记已解决", "closed": "关闭工单"}[data.status]
    _add_log(db, t, "status", user, f"{label}" + (f"：{data.resolution}" if data.resolution else ""))
    db.commit()
    db.refresh(t)
    return t
