"""初始化数据：建表 + 权限 + 角色 + 组织 + 工单类型 + 默认账号。"""
from sqlalchemy.orm import Session

from .core.security import hash_password
from .models import (
    Organization,
    Permission,
    Role,
    TicketType,
    User,
)

# 权限点定义：(code, name, module, description)
PERMISSIONS = [
    ("user:read", "查看用户", "user", "查看用户列表与详情"),
    ("user:manage", "管理用户", "user", "新增/编辑/删除用户"),
    ("org:read", "查看组织", "org", "查看组织架构"),
    ("org:manage", "管理组织", "org", "新增/编辑/删除组织"),
    ("role:read", "查看角色", "role", "查看角色及权限"),
    ("role:manage", "配置角色权限", "role", "新增/编辑角色，勾选权限"),
    ("ticket:create", "提交工单", "ticket", "提交新工单"),
    ("ticket:read_all", "查看全部工单", "ticket", "查看所有工地的工单"),
    ("ticket:handle", "处理工单", "ticket", "处理/指派/重新归类工单"),
    ("ticket:manage", "管理工单类型", "ticket", "维护工单类型与自动分类关键词"),
    ("ticket:delete", "删除工单", "ticket", "删除工单"),
    ("stats:read", "查看统计", "stats", "查看统计看板"),
]

# 角色定义：(name, code, description, is_system, [permission codes])
ROLES = [
    ("系统管理员", "super_admin", "拥有全部权限", True, [p[0] for p in PERMISSIONS]),
    (
        "项目管理员",
        "project_admin",
        "查看并处理全部工单、查看统计",
        True,
        ["user:read", "org:read", "role:read", "ticket:create", "ticket:read_all",
         "ticket:handle", "ticket:manage", "stats:read"],
    ),
    (
        "现场人员",
        "site_staff",
        "在所属工地提交工单、查看自己提交的工单",
        True,
        ["ticket:create", "org:read"],
    ),
]

# 组织树：(name, code, type, parent_code)
ORGS = [
    ("公司总部", "HQ", "company", None),
    ("第一项目部", "P1", "project", "HQ"),
    ("一号工地", "S1", "site", "P1"),
    ("二号工地", "S2", "site", "P1"),
    ("第二项目部", "P2", "project", "HQ"),
    ("三号工地", "S3", "site", "P2"),
]

# 工单类型：(name, code, keywords, sort)
TICKET_TYPES = [
    ("安全类", "safety", "坍塌,坠落,高处,临边,防护,脚手架,漏电,触电,火灾,爆炸,安全帽,基坑,围挡,警示,隐患", 1),
    ("质量类", "quality", "裂缝,渗漏,蜂窝,麻面,空鼓,钢筋,混凝土,强度,平整,偏差,回弹,脱落,质检", 2),
    ("进度类", "schedule", "延误,延期,停工,窝工,滞后,拖期,进度,工期,误工,加班", 3),
    ("设备类", "equipment", "塔吊,吊车,起重机,挖掘机,搅拌机,发电机,设备,故障,停机,损坏,机械,泵", 4),
    ("材料类", "material", "水泥,钢材,砂石,混凝土,缺料,断供,进场,材料,不合格,库存,耗材,砂浆", 5),
    ("人员类", "personnel", "工伤,纠纷,考勤,打架,投诉,缺员,旷工,人员,劳务,工资", 6),
    ("环保类", "environment", "扬尘,噪音,噪声,污水,废水,废弃物,垃圾,扰民,环保,污染,灰尘", 7),
    ("待分类", "uncategorized", "", 99),
]


def seed_all(db: Session) -> None:
    # 权限
    perm_objs = {}
    for code, name, module, desc in PERMISSIONS:
        p = db.query(Permission).filter(Permission.code == code).first()
        if not p:
            p = Permission(code=code, name=name, module=module, description=desc)
            db.add(p)
            db.flush()
        perm_objs[code] = p

    # 角色
    role_objs = {}
    for name, code, desc, is_system, perm_codes in ROLES:
        r = db.query(Role).filter(Role.code == code).first()
        if not r:
            r = Role(name=name, code=code, description=desc, is_system=is_system)
            db.add(r)
            db.flush()
        r.permissions = [perm_objs[c] for c in perm_codes]
        role_objs[code] = r

    # 组织
    org_objs = {}
    for name, code, otype, parent_code in ORGS:
        o = db.query(Organization).filter(Organization.code == code).first()
        if not o:
            o = Organization(name=name, code=code, type=otype)
            db.add(o)
            db.flush()
        if parent_code:
            o.parent_id = org_objs[parent_code].id
        org_objs[code] = o

    # 工单类型
    for name, code, keywords, sort in TICKET_TYPES:
        t = db.query(TicketType).filter(TicketType.code == code).first()
        if not t:
            t = TicketType(name=name, code=code, keywords=keywords, sort=sort, description=name)
            db.add(t)

    db.flush()

    # 默认账号
    default_users = [
        # (username, password, real_name, role_code, org_code)
        ("admin", "admin123", "系统管理员", "super_admin", "HQ"),
        ("project1", "project123", "项目经理", "project_admin", "P1"),
        ("site01", "site123", "一号工地现场员", "site_staff", "S1"),
        ("site02", "site123", "二号工地现场员", "site_staff", "S2"),
    ]
    for username, password, real_name, role_code, org_code in default_users:
        if db.query(User).filter(User.username == username).first():
            continue
        u = User(
            username=username,
            password_hash=hash_password(password),
            real_name=real_name,
            org_id=org_objs[org_code].id,
            role_id=role_objs[role_code].id,
            is_active=True,
        )
        db.add(u)

    db.commit()
