"""统计看板接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Organization, Ticket, TicketType, User
from ..schemas import StatsOut

router = APIRouter(prefix="/stats", tags=["统计"])


def _scope(user: User) -> bool:
    """True 表示可查看全部工单统计。"""
    codes = {p.code for p in (user.role.permissions if user.role else [])}
    return "ticket:read_all" in codes


@router.get("", response_model=StatsOut)
def stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base = db.query(Ticket)
    if not _scope(user):
        base = base.filter(Ticket.creator_id == user.id)

    total = base.count()
    by_status = {s: 0 for s in ("pending", "processing", "resolved", "closed")}
    for status, cnt in base.with_entities(Ticket.status, func.count()).group_by(Ticket.status).all():
        by_status[status] = cnt

    by_type = []
    for row in (
        base.join(TicketType, Ticket.type_id == TicketType.id, isouter=True)
        .with_entities(TicketType.name, func.count())
        .group_by(TicketType.name)
        .all()
    ):
        by_type.append({"name": row[0] or "待分类", "value": row[1]})

    by_org = []
    for row in (
        base.join(Organization, Ticket.site_org_id == Organization.id, isouter=True)
        .with_entities(Organization.name, func.count())
        .group_by(Organization.name)
        .all()
    ):
        by_org.append({"name": row[0] or "未指定工地", "value": row[1]})

    recent = base.order_by(Ticket.id.desc()).limit(10).all()

    return StatsOut(
        total=total,
        by_status=by_status,
        by_type=by_type,
        by_org=by_org,
        recent=recent,
    )
