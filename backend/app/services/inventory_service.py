from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock


async def adjust_stock(
    session: AsyncSession,
    branch_id: int,
    item_id: int,
    quantity: int,
    allow_negative: bool,
) -> Stock:
    result = await session.execute(
        select(Stock).where(Stock.branch_id == branch_id, Stock.item_id == item_id).with_for_update()
    )
    stock = result.scalar_one_or_none()
    if stock is None:
        stock = Stock(branch_id=branch_id, item_id=item_id, quantity=0)
        session.add(stock)
        await session.flush()
    new_qty = quantity
    if not allow_negative and new_qty < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Negative stock not allowed")
    stock.quantity = new_qty
    await session.flush()
    return stock
