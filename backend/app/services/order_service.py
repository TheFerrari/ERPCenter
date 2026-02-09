from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_line import OrderLine
from app.models.stock import Stock
from app.services.audit_service import log_audit


async def fulfill_order(
    session: AsyncSession,
    order: Order,
    actor_user_id: int,
    actor_ip: str,
    allow_negative: bool,
) -> Order:
    if order.status != "submitted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not submitted")

    async with session.begin():
        result = await session.execute(
            select(OrderLine).where(OrderLine.order_id == order.id)
        )
        lines = result.scalars().all()
        if not lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order has no lines")

        for line in lines:
            stock_result = await session.execute(
                select(Stock)
                .where(Stock.branch_id == order.branch_id, Stock.item_id == line.item_id)
                .with_for_update()
            )
            stock = stock_result.scalar_one_or_none()
            if stock is None:
                stock = Stock(branch_id=order.branch_id, item_id=line.item_id, quantity=0)
                session.add(stock)
                await session.flush()
            new_qty = stock.quantity - line.requested_qty
            if new_qty < 0 and not allow_negative:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
            stock.quantity = new_qty
            line.fulfilled_qty = line.requested_qty

        order.status = "fulfilled"
        await log_audit(
            session=session,
            actor_user_id=actor_user_id,
            action="order_fulfilled",
            entity_type="Order",
            entity_id=str(order.id),
            ip=actor_ip,
            details={"lines": [line.item_id for line in lines]},
        )
    return order
