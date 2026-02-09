from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER, require_role
from app.db.session import get_session
from app.models.stock import Stock
from app.models.user import User
from app.schemas.stock import StockRead, StockUpdate
from app.services.audit_service import log_audit

router = APIRouter(prefix="/stock", tags=["stock"])


def enforce_branch_scope(user: User, branch_id: int) -> None:
    if user.role != ROLE_ADMIN and user.branch_id != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch scope violation")


@router.get("/", response_model=list[StockRead])
async def list_stock(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[StockRead]:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    query = select(Stock)
    if current_user.role != ROLE_ADMIN:
        query = query.where(Stock.branch_id == current_user.branch_id)
    result = await session.execute(query)
    return result.scalars().all()


@router.patch("/{branch_id}/{item_id}", response_model=StockRead)
async def update_stock(
    branch_id: int,
    item_id: int,
    payload: StockUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StockRead:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER})
    enforce_branch_scope(current_user, branch_id)
    if payload.quantity < 0 and current_user.role != ROLE_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Negative stock not allowed")
    result = await session.execute(
        select(Stock).where(Stock.branch_id == branch_id, Stock.item_id == item_id)
    )
    stock = result.scalar_one_or_none()
    if not stock:
        stock = Stock(branch_id=branch_id, item_id=item_id, quantity=0)
        session.add(stock)
        await session.flush()
    stock.quantity = payload.quantity
    await log_audit(
        session,
        actor_user_id=current_user.id,
        action="stock_adjusted",
        entity_type="Stock",
        entity_id=f"{branch_id}:{item_id}",
        ip="-",
        details={"quantity": payload.quantity},
    )
    await session.commit()
    await session.refresh(stock)
    return stock
