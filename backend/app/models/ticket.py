"""工单相关模型。"""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from ..database import Base


class TicketType(Base):
    """工单类型，同时承载自动分类所需的关键词。"""

    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="类型名称，如：安全类")
    code = Column(String(64), nullable=False, unique=True, comment="类型编码")
    keywords = Column(Text, nullable=True, comment="自动分类关键词，逗号分隔")
    sort = Column(Integer, default=0)
    description = Column(String(255), nullable=True)

    tickets = relationship("Ticket", back_populates="type")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), nullable=False, unique=True, comment="工单编号，如 GD-20261028-0001")
    title = Column(String(128), nullable=False, comment="问题标题")
    description = Column(Text, nullable=True, comment="问题详细描述")
    type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="SET NULL"), nullable=True)
    priority = Column(String(16), default="medium", comment="low/medium/high/urgent")
    status = Column(String(16), default="pending", comment="pending/processing/resolved/closed")
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    site_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution = Column(Text, nullable=True, comment="处理说明/解决方案")
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    type = relationship("TicketType", back_populates="tickets", lazy="selectin")
    creator = relationship("User", foreign_keys=[creator_id], lazy="selectin")
    assignee = relationship("User", foreign_keys=[assignee_id], lazy="selectin")
    site_org = relationship("Organization", lazy="selectin")
    logs = relationship(
        "TicketLog",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketLog.id",
        lazy="selectin",
    )


class TicketLog(Base):
    """工单流转日志。"""

    __tablename__ = "ticket_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(32), nullable=False, comment="create/assign/status/resolve/classify/comment")
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    ticket = relationship("Ticket", back_populates="logs")
    operator = relationship("User", lazy="selectin")
