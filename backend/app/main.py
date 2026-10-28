"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .api import auth, orgs, roles, stats, tickets, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 建表
    Base.metadata.create_all(bind=engine)
    if settings.auto_seed:
        with SessionLocal() as db:
            from .seed import seed_all

            seed_all(db)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, users.router, orgs.router, roles.router, tickets.router, stats.router):
    app.include_router(r, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok", "docs": "/docs"}
