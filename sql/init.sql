-- ============================================
-- 工地工单管理系统 - 数据库初始化脚本
-- 目标数据库：MySQL 8.0.43
-- 说明：表结构由后端启动时通过 SQLAlchemy 自动创建，
--       本脚本只需负责创建数据库即可。表与种子数据会自动生成。
-- ============================================

CREATE DATABASE IF NOT EXISTS `gongdan`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE `gongdan`;

-- 可选：创建一个专用账号（根据实际需要调整密码）
-- CREATE USER IF NOT EXISTS 'gongdan'@'localhost' IDENTIFIED BY 'gongdan123';
-- GRANT ALL PRIVILEGES ON `gongdan`.* TO 'gongdan'@'localhost';
-- FLUSH PRIVILEGES;

-- 提示：
-- 后端会自动创建以下表：
--   organizations 组织（公司/项目部/工地）
--   permissions   权限点
--   roles         角色
--   role_permissions 角色-权限关联
--   users         用户
--   ticket_types  工单类型（含自动分类关键词）
--   tickets       工单
--   ticket_logs   工单流转日志
