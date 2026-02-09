from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.rbac import Role
from app.db.session import get_session
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchOut

router = APIRouter(prefix="/branches", tags=["branches"])


@router.post("", response_model=BranchOut, dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))])
async def create_branch(payload: BranchCreate, session: AsyncSession = Depends(get_session)) -> BranchOut:
    branch = Branch(**payload.model_dump())
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return branch


@router.get("", response_model=list[BranchOut], dependencies=[Depends(get_current_user)])
async def list_branches(session: AsyncSession = Depends(get_session)) -> list[BranchOut]:
    result = await session.execute(select(Branch))
    return list(result.scalars().all())
