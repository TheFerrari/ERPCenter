from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import audit, auth, branches, health, items, orders, stock, users
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(branches.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(items.router, prefix=settings.api_v1_prefix)
app.include_router(stock.router, prefix=settings.api_v1_prefix)
app.include_router(orders.router, prefix=settings.api_v1_prefix)
app.include_router(audit.router, prefix=settings.api_v1_prefix)
