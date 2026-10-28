"""应用配置。通过环境变量或 .env 覆盖默认值。"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- 数据库（MySQL 8.0.43）----
    # 形如: mysql+pymysql://<用户>:<密码>@<主机>:<端口>/<库名>?charset=utf8mb4
    database_url: str = (
        "mysql+pymysql://root:123456@localhost:3306/gongdan?charset=utf8mb4"
    )
    database_echo: bool = False

    # ---- 安全 ----
    jwt_secret: str = "change-me-to-a-long-random-secret-key-9f2c4b7d"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 小时

    # ---- 应用 ----
    app_name: str = "工地工单管理系统"
    api_prefix: str = "/api"

    # 首次启动自动创建数据库表并写入种子数据
    auto_seed: bool = True

    # 允许跨域的前端地址
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
