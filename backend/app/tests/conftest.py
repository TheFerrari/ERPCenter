from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-should-be-long-enough")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_session


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(bind=db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest.fixture()
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    os.environ.setdefault("SECRET_KEY", "test-secret-key-should-be-long-enough")
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
    from app.main import app as fastapi_app

    app: FastAPI = fastapi_app

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
