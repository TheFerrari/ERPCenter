from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, require_role
from app.core.security import hash_password
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
async def list_users(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    require_role(current_user.role, {ROLE_ADMIN})
    result = await session.execute(select(User))
    return result.scalars().all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    require_role(current_user.role, {ROLE_ADMIN})
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        branch_id=payload.branch_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
