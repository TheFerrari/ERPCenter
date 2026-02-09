from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.rbac import Role
from app.core.security import hash_password
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, dependencies=[Depends(require_roles(Role.ADMIN))])
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> UserOut:
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
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


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_roles(Role.ADMIN))])
async def list_users(session: AsyncSession = Depends(get_session)) -> list[UserOut]:
    result = await session.execute(select(User))
    return list(result.scalars().all())
