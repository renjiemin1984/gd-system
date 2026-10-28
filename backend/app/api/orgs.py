"""组织管理接口（需 org:manage 权限）。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_permission
from ..models import Organization, User
from ..schemas import OrganizationCreate, OrganizationOut, OrganizationUpdate

router = APIRouter(prefix="/orgs", tags=["组织管理"])


def _tree(db: Session) -> List[OrganizationOut]:
    orgs = db.query(Organization).order_by(Organization.id).all()
    # 递归组装树
    by_id: dict[int, OrganizationOut] = {}
    for o in orgs:
        by_id[o.id] = OrganizationOut.model_validate(o)

    roots: List[OrganizationOut] = []
    for o in orgs:
        node = by_id[o.id]
        parent = by_id.get(o.parent_id) if o.parent_id else None
        if parent is not None:
            parent.children.append(node)
        else:
            roots.append(node)
    return roots


@router.get("", response_model=List[OrganizationOut])
def list_orgs(
    flat: bool = False,
    _: User = Depends(require_permission("org:read")),
    db: Session = Depends(get_db),
):
    if flat:
        return db.query(Organization).order_by(Organization.id).all()
    return _tree(db)


@router.get("/{org_id}", response_model=OrganizationOut)
def get_org(
    org_id: int,
    _: User = Depends(require_permission("org:read")),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "组织不存在")
    return org


@router.post("", response_model=OrganizationOut, status_code=201)
def create_org(
    data: OrganizationCreate,
    _: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
):
    if db.query(Organization).filter(Organization.code == data.code).first():
        raise HTTPException(400, "组织编码已存在")
    org = Organization(**data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.put("/{org_id}", response_model=OrganizationOut)
def update_org(
    org_id: int,
    data: OrganizationUpdate,
    _: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "组织不存在")
    if data.parent_id == org.id:
        raise HTTPException(400, "父组织不能是自己")
    for field in ("name", "type", "parent_id", "description"):
        val = getattr(data, field)
        if val is not None:
            setattr(org, field, val)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.delete("/{org_id}", response_model=dict)
def delete_org(
    org_id: int,
    _: User = Depends(require_permission("org:manage")),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "组织不存在")
    if db.query(Organization).filter(Organization.parent_id == org_id).count():
        raise HTTPException(400, "该组织下存在子组织，无法删除")
    if db.query(User).filter(User.org_id == org_id).count():
        raise HTTPException(400, "该组织下存在用户，无法删除")
    db.delete(org)
    db.commit()
    return {"ok": True}
