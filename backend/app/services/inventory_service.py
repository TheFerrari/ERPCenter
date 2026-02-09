from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Role
from app.models.stock import Stock
from app.services.audit_service import record_audit


class StockError(Exception):
    pass


async def adjust_stock(
    session: AsyncSession,
    *,
    branch_id: int,
    item_id: int,
    quantity: int,
    actor_user_id: int | None,
    actor_role: Role,
    ip: str,
    allow_negative: bool = False,
) -> Stock:
    stmt = select(Stock).where(Stock.branch_id == branch_id, Stock.item_id == item_id).with_for_update()
    result = await session.execute(stmt)
    stock = result.scalar_one_or_none()
    if stock is None:
        stock = Stock(branch_id=branch_id, item_id=item_id, quantity=0)
        session.add(stock)
        await session.flush()
    new_quantity = stock.quantity + quantity
    if new_quantity < 0 and not allow_negative and actor_role != Role.ADMIN:
        raise StockError("Insufficient stock")
    stock.quantity = new_quantity
    await record_audit(
        session,
        actor_user_id=actor_user_id,
        action="stock_adjust",
        entity_type="stock",
        entity_id=f"{branch_id}:{item_id}",
        ip=ip,
        details={"change": quantity, "new_quantity": new_quantity},
    )
    return stock
