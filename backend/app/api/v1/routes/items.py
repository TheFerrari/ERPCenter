from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, ROLE_MANAGER, require_role
from app.db.session import get_session
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemRead])
async def list_items(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ItemRead]:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER})
    result = await session.execute(select(Item))
    return result.scalars().all()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ItemRead:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER})
    item = Item(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
