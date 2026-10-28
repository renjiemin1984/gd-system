# 工地工单管理系统（全栈）

工地现场人员在本系统提交问题工单 → 系统自动归类问题类型 → 管理员查看、处理、指派、重新归类。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus + Axios（Node.js 环境） |
| 后端 | Python + FastAPI + SQLAlchemy 2.0 + PyJWT（密码 PBKDF2） |
| 数据库 | MySQL 8.0.43 |

## 目录结构

```
gongdanxitong/
├── backend/               FastAPI 后端
│   ├── app/
│   │   ├── main.py        应用入口（启动建表+种子数据）
│   │   ├── config.py      配置（数据库连接、JWT）
│   │   ├── database.py    数据库引擎/会话
│   │   ├── seed.py        初始化：权限/角色/组织/工单类型/默认账号
│   │   ├── models/        ORM 模型（组织/角色/权限/用户/工单/类型/日志）
│   │   ├── schemas/       Pydantic 校验模型
│   │   ├── core/          安全（密码哈希、JWT）
│   │   ├── services/      自动归类服务（关键词规则）
│   │   └── api/           路由（认证/用户/组织/角色/工单/统计）
│   ├── requirements.txt
│   ├── run.py             本地启动入口
│   └── .env.example       环境变量示例
├── frontend/              Vue 前端
│   └── src/
│       ├── router/        路由（含权限守卫）
│       ├── stores/        状态（认证）
│       ├── api/           axios 封装与接口
│       ├── utils/         状态/优先级文案
│       └── views/         页面
└── sql/init.sql           建库脚本
```

## 核心功能

- **用户管理**：账号、姓名、所属组织、角色、启用/停用、重置密码。
- **组织架构**：公司 → 项目部 → 工地 层级树；工地用户提交的工单自动归属其所在工地。
- **角色权限（RBAC，可自行配置）**：管理员在「角色权限」页勾选权限即可授予/回收角色权限；权限点涵盖用户/组织/角色/工单/统计五大模块。
- **工单流转**：待处理 → 处理中 → 已解决 → 已关闭；支持指派处理人、填写处理说明、重新归类；全程记录流转日志。
- **自动归类**：提交工单时，系统按标题/描述命中关键词自动匹配问题类型（如安全类/质量类/设备类等），关键词可在「工单类型」页维护。
- **统计看板**：工单总数、状态分布、按类型/工地分布、最新工单。

## 启动步骤

### 1. 准备数据库（MySQL 8.0.43）

1. 确认 MySQL 服务已启动（端口 3306）。
2. 在 MySQL 中执行建库脚本：

```bash
mysql -uroot -p < sql/init.sql
```

3. 配置后端数据库连接。复制 `backend/.env.example` 为 `backend/.env`，按你的账号密码修改 `database_url`：

```
database_url=mysql+pymysql://root:你的密码@localhost:3306/gongdan?charset=utf8mb4
```

### 2. 启动后端（端口 8000）

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python run.py
```

启动后自动建表并写入种子数据。接口文档：http://127.0.0.1:8000/docs

### 3. 启动前端（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173

## 默认账号

| 账号 | 密码 | 角色 | 说明 |
|---|---|---|---|
| admin | admin123 | 系统管理员 | 全部权限 |
| project1 | project123 | 项目管理员 | 查看/处理全部工单、统计 |
| site01 | site123 | 现场人员 | 一号工地提交工单 |
| site02 | site123 | 现场人员 | 二号工地提交工单 |

> 首次登录后请尽快在「个人中心」修改默认密码。

## 权限点一览

| 模块 | 权限码 | 说明 |
|---|---|---|
| 用户 | user:read / user:manage | 查看 / 增删改用户 |
| 组织 | org:read / org:manage | 查看 / 管理组织架构 |
| 角色 | role:read / role:manage | 查看 / 配置角色权限 |
| 工单 | ticket:create | 提交工单 |
| 工单 | ticket:read_all | 查看全部工单 |
| 工单 | ticket:handle | 处理/指派/重新归类 |
| 工单 | ticket:manage | 管理工单类型与分类关键词 |
| 工单 | ticket:delete | 删除工单 |
| 统计 | stats:read | 查看统计看板 |

## 自动分类规则

- 提交工单时若未指定类型，系统将「标题 + 描述」与各类型关键词做匹配，命中关键词最多的类型即为自动归类结果。
- 未命中任何关键词时归为「待分类」，可手动重新归类。
- 关键词维护：「工单类型」页编辑对应类型的关键词（逗号分隔）。

## 已知边界

- 工单图片上传为预留字段，当前未实现文件上传，后续可按需扩展。
- 前端为单点部署，需与后端在同一台机器或配置 CORS 白名单。
