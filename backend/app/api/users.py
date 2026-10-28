"""用户管理接口（需 user:manage 权限）。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..database import get_db
from ..deps import get_current_user, require_permission
from ..models import User
from ..schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["用户管理"])


def _q(db: Session):
    return db.query(User)


@router.get("", response_model=List[UserOut])
def list_users(
    keyword: str = Query("", description="按账号/姓名模糊搜索"),
    org_id: int | None = Query(None),
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
):
    q = _q(db)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((User.username.like(like)) | (User.real_name.like(like)))
    if org_id:
        q = q.filter(User.org_id == org_id)
    return q.order_by(User.id).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    return user


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "账号已存在")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        real_name=data.real_name,
        phone=data.phone,
        email=data.email,
        org_id=data.org_id,
        role_id=data.role_id,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    for field in ("real_name", "phone", "email", "org_id", "role_id", "is_active"):
        val = getattr(data, field)
        if val is not None:
            setattr(user, field, val)
    if data.password:
        user.password_hash = hash_password(data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    if user.id == 1:
        raise HTTPException(400, "不能删除内置超级管理员")
    db.delete(user)
    db.commit()
    return {"ok": True}
