"""用户/组织/角色/权限相关请求与响应模型。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- 通用 ----------
class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- 认证 ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# ---------- 组织 ----------
class OrganizationCreate(BaseModel):
    name: str = Field(..., max_length=64)
    code: str = Field(..., max_length=64)
    type: str = "site"
    parent_id: Optional[int] = None
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class OrganizationOut(ORMSchema):
    id: int
    name: str
    code: str
    type: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    children: List["OrganizationOut"] = []


# ---------- 权限 ----------
class PermissionOut(ORMSchema):
    id: int
    code: str
    name: str
    module: str
    description: Optional[str] = None


# ---------- 角色 ----------
class RoleCreate(BaseModel):
    name: str = Field(..., max_length=64)
    code: str = Field(..., max_length=64)
    description: Optional[str] = None
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: List[int] = []


class RoleOut(ORMSchema):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_system: bool = False
    permission_ids: List[int] = []
    permissions: List[PermissionOut] = []


class RoleAssignRequest(BaseModel):
    role_id: Optional[int] = None


# ---------- 用户 ----------
class UserCreate(BaseModel):
    username: str = Field(..., max_length=64)
    password: str = Field(..., min_length=6, max_length=64)
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    org_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    org_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=64)


class UserOut(ORMSchema):
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    org_id: Optional[int] = None
    role_id: Optional[int] = None
    org: Optional[OrganizationOut] = None
    role: Optional[RoleOut] = None
    created_at: Optional[datetime] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=64)


TokenResponse.model_rebuild()
OrganizationOut.model_rebuild()
RoleOut.model_rebuild()
