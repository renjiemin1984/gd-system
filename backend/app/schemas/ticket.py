"""工单相关请求与响应模型。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .user import OrganizationOut, UserOut


class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- 工单类型 ----------
class TicketTypeCreate(BaseModel):
    name: str = Field(..., max_length=64)
    code: str = Field(..., max_length=64)
    keywords: Optional[str] = None
    sort: int = 0
    description: Optional[str] = None


class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    keywords: Optional[str] = None
    sort: Optional[int] = None
    description: Optional[str] = None


class TicketTypeOut(ORMSchema):
    id: int
    name: str
    code: str
    keywords: Optional[str] = None
    sort: int = 0
    description: Optional[str] = None


# ---------- 工单 ----------
class TicketCreate(BaseModel):
    title: str = Field(..., max_length=128)
    description: Optional[str] = None
    site_org_id: Optional[int] = None
    type_id: Optional[int] = None  # 不填则由系统自动归类
    priority: str = "medium"
    images: List[str] = []


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    type_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TicketHandleRequest(BaseModel):
    """处理工单：填写处理说明并推进状态。"""

    status: str = Field(..., pattern="^(processing|resolved|closed)$")
    resolution: Optional[str] = None
    assignee_id: Optional[int] = None


class TicketLogOut(ORMSchema):
    id: int
    action: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    operator: Optional[UserOut] = None


class TicketOut(ORMSchema):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    type_id: Optional[int] = None
    priority: str = "medium"
    status: str = "pending"
    creator_id: Optional[int] = None
    site_org_id: Optional[int] = None
    assignee_id: Optional[int] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    type: Optional[TicketTypeOut] = None
    creator: Optional[UserOut] = None
    assignee: Optional[UserOut] = None
    site_org: Optional[OrganizationOut] = None
    logs: List[TicketLogOut] = []


class ClassifyRequest(BaseModel):
    type_id: int


# ---------- 统计 ----------
class StatusCount(BaseModel):
    pending: int = 0
    processing: int = 0
    resolved: int = 0
    closed: int = 0


class StatsOut(BaseModel):
    total: int = 0
    by_status: StatusCount = StatusCount()
    by_type: List[dict] = []
    by_org: List[dict] = []
    recent: List[TicketOut] = []
