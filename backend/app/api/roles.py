"""角色管理接口（需 role:manage 权限）。角色权限可在此自行配置。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_permission
from ..models import Permission, Role, User
from ..schemas import PermissionOut, RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["角色管理"])


def _set_permissions(db: Session, role: Role, permission_ids: List[int]):
    perms = db.query(Permission).filter(Permission.id.in_(permission_ids)).all() if permission_ids else []
    role.permissions = perms
    db.add(role)


@router.get("", response_model=List[RoleOut])
def list_roles(
    _: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db),
):
    roles = db.query(Role).order_by(Role.id).all()
    return roles


@router.get("/permissions", response_model=List[PermissionOut])
def list_permissions(
    _: User = Depends(require_permission("role:read")),
    db: Session = Depends(get_db),
):
    return db.query(Permission).order_by(Permission.id).all()


@router.post("", response_model=RoleOut, status_code=201)
def create_role(
    data: RoleCreate,
    _: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
):
    if db.query(Role).filter(Role.code == data.code).first():
        raise HTTPException(400, "角色编码已存在")
    role = Role(name=data.name, code=data.code, description=data.description)
    _set_permissions(db, role, data.permission_ids)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    data: RoleUpdate,
    _: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(404, "角色不存在")
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    if data.permission_ids:
        _set_permissions(db, role, data.permission_ids)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", response_model=dict)
def delete_role(
    role_id: int,
    _: User = Depends(require_permission("role:manage")),
    db: Session = Depends(get_db),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(404, "角色不存在")
    if role.is_system:
        raise HTTPException(400, "系统内置角色不能删除")
    if db.query(User).filter(User.role_id == role_id).count():
        raise HTTPException(400, "该角色下存在用户，无法删除")
    db.delete(role)
    db.commit()
    return {"ok": True}
