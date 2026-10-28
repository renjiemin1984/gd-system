"""组织、角色、权限、用户模型（RBAC）。"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from ..database import Base


# ---- 角色-权限 多对多关联表 ----
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(Base):
    """组织：可表示 公司 -> 项目部 -> 工地 的层级，工地用户挂在对应工地组织下。"""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="组织名称，如：某某工地")
    code = Column(String(64), nullable=False, unique=True, comment="组织编码，如 SITE-A01")
    type = Column(String(16), nullable=False, default="site", comment="company/project/site")
    parent_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("User", back_populates="org")


class Permission(Base):
    """权限点。code 形如 ticket:create / user:manage / role:manage。"""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True, comment="权限编码")
    name = Column(String(64), nullable=False, comment="权限名称")
    module = Column(String(32), nullable=False, default="ticket", comment="所属模块")
    description = Column(String(255), nullable=True)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(Base):
    """角色。角色的权限由管理员在界面上自行勾选配置（RBAC）。"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="角色名称")
    code = Column(String(64), nullable=False, unique=True, comment="角色编码")
    description = Column(String(255), nullable=True)
    is_system = Column(Boolean, default=False, comment="系统内置角色，禁止删除")
    created_at = Column(DateTime, default=datetime.now)

    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles", lazy="selectin"
    )
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True, comment="登录账号")
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(64), nullable=True, comment="姓名")
    phone = Column(String(32), nullable=True)
    email = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True, comment="是否启用")
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    org = relationship("Organization", back_populates="users", lazy="selectin")
    role = relationship("Role", back_populates="users", lazy="selectin")
