from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.rbac import Role
from app.db.session import get_session
from app.models.stock import Stock
from app.schemas.stock import StockAdjust, StockOut
from app.services.inventory_service import StockError, adjust_stock

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("", response_model=list[StockOut])
async def list_stock(session: AsyncSession = Depends(get_session), user=Depends(get_current_user)) -> list[StockOut]:
    stmt = select(Stock)
    if user.role in {Role.MANAGER, Role.WORKER}:
        stmt = stmt.where(Stock.branch_id == user.branch_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.patch("", response_model=StockOut, dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))])
async def update_stock(
    request: Request,
    payload: StockAdjust,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> StockOut:
    if user.role == Role.MANAGER and user.branch_id != payload.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    try:
        stock = await adjust_stock(
            session,
            branch_id=payload.branch_id,
            item_id=payload.item_id,
            quantity=payload.quantity,
            actor_user_id=user.id,
            actor_role=user.role,
            ip=request.client.host if request.client else "unknown",
        )
        await session.commit()
        return stock
    except StockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
