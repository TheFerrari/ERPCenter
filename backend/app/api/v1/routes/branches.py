from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, ROLE_MANAGER, require_role
from app.db.session import get_session
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchRead
from app.models.user import User

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=list[BranchRead])
async def list_branches(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[BranchRead]:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER})
    result = await session.execute(select(Branch))
    return result.scalars().all()


@router.post("/", response_model=BranchRead, status_code=status.HTTP_201_CREATED)
async def create_branch(
    payload: BranchCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BranchRead:
    require_role(current_user.role, {ROLE_ADMIN})
    branch = Branch(**payload.model_dump())
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return branch
