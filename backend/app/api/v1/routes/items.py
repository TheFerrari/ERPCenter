from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.rbac import Role
from app.db.session import get_session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemOut, dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))])
async def create_item(payload: ItemCreate, session: AsyncSession = Depends(get_session)) -> ItemOut:
    item = Item(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("", response_model=list[ItemOut], dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.WORKER))])
async def list_items(session: AsyncSession = Depends(get_session)) -> list[ItemOut]:
    result = await session.execute(select(Item))
    return list(result.scalars().all())
