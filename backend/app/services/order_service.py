from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Role
from app.models.order import Order, OrderStatus
from app.models.order_line import OrderLine
from app.models.stock import Stock
from app.services.audit_service import record_audit
from app.services.inventory_service import StockError


class OrderError(Exception):
    pass


async def create_order(session: AsyncSession, *, branch_id: int, user_id: int) -> Order:
    order = Order(branch_id=branch_id, created_by_user_id=user_id)
    session.add(order)
    await session.flush()
    return order


async def add_order_line(
    session: AsyncSession,
    *,
    order_id: int,
    item_id: int,
    requested_qty: int,
) -> OrderLine:
    line = OrderLine(order_id=order_id, item_id=item_id, requested_qty=requested_qty, fulfilled_qty=0)
    session.add(line)
    await session.flush()
    return line


async def submit_order(session: AsyncSession, *, order: Order, actor_user_id: int, ip: str) -> Order:
    if order.status != OrderStatus.DRAFT:
        raise OrderError("Order cannot be submitted")
    order.status = OrderStatus.SUBMITTED
    await record_audit(
        session,
        actor_user_id=actor_user_id,
        action="order_submit",
        entity_type="order",
        entity_id=str(order.id),
        ip=ip,
        details={"status": order.status},
    )
    return order


async def fulfill_order(
    session: AsyncSession,
    *,
    order: Order,
    actor_user_id: int,
    actor_role: Role,
    ip: str,
) -> Order:
    if order.status != OrderStatus.SUBMITTED:
        raise OrderError("Order not submitted")
    for line in order.lines:
        stmt = (
            select(Stock)
            .where(Stock.branch_id == order.branch_id, Stock.item_id == line.item_id)
            .with_for_update()
        )
        stock = (await session.execute(stmt)).scalar_one_or_none()
        if stock is None:
            raise StockError("Stock record missing")
        if stock.quantity < line.requested_qty and actor_role != Role.ADMIN:
            raise StockError("Insufficient stock")
        stock.quantity -= line.requested_qty
        line.fulfilled_qty = line.requested_qty
    order.status = OrderStatus.FULFILLED
    await record_audit(
        session,
        actor_user_id=actor_user_id,
        action="order_fulfill",
        entity_type="order",
        entity_id=str(order.id),
        ip=ip,
        details={"status": order.status, "lines": len(order.lines)},
    )
    return order
