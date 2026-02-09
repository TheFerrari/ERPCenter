from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.routes import audit, auth, branches, items, orders, stock, users
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine
from app.middleware.request_id import RequestIdMiddleware

configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(auth.router, prefix="/v1")
app.include_router(branches.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(items.router, prefix="/v1")
app.include_router(stock.router, prefix="/v1")
app.include_router(orders.router, prefix="/v1")
app.include_router(audit.router, prefix="/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ready"}
