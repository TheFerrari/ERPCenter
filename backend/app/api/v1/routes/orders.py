from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.rbac import Role
from app.db.session import get_session
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderLineCreate, OrderLineOut, OrderOut
from app.services.order_service import OrderError, add_order_line, create_order, fulfill_order, submit_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
async def create_order_endpoint(
    payload: OrderCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> OrderOut:
    if user.role == Role.MANAGER and user.branch_id != payload.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    order = await create_order(session, branch_id=payload.branch_id, user_id=user.id)
    await session.commit()
    await session.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
async def list_orders(session: AsyncSession = Depends(get_session), user=Depends(get_current_user)) -> list[OrderOut]:
    stmt = select(Order).options(selectinload(Order.lines))
    if user.role in {Role.MANAGER, Role.WORKER}:
        stmt = stmt.where(Order.branch_id == user.branch_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session), user=Depends(get_current_user)) -> OrderOut:
    stmt = select(Order).options(selectinload(Order.lines)).where(Order.id == order_id)
    order = (await session.execute(stmt)).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if user.role in {Role.MANAGER, Role.WORKER} and order.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    return order


@router.post("/{order_id}/lines", response_model=OrderLineOut)
async def add_line_endpoint(
    order_id: int,
    payload: OrderLineCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> OrderLineOut:
    order = (await session.execute(select(Order).where(Order.id == order_id))).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != OrderStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not editable")
    if user.role in {Role.MANAGER, Role.WORKER} and order.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    line = await add_order_line(
        session,
        order_id=order_id,
        item_id=payload.item_id,
        requested_qty=payload.requested_qty,
    )
    await session.commit()
    await session.refresh(line)
    return line


@router.post("/{order_id}/submit", response_model=OrderOut)
async def submit_order_endpoint(
    request: Request,
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> OrderOut:
    order = (await session.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.lines)))).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if user.role in {Role.MANAGER, Role.WORKER} and order.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    try:
        order = await submit_order(
            session,
            order=order,
            actor_user_id=user.id,
            ip=request.client.host if request.client else "unknown",
        )
        await session.commit()
        await session.refresh(order)
        return order
    except OrderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{order_id}/fulfill", response_model=OrderOut)
async def fulfill_order_endpoint(
    request: Request,
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> OrderOut:
    stmt = select(Order).options(selectinload(Order.lines)).where(Order.id == order_id)
    order = (await session.execute(stmt)).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if user.role in {Role.MANAGER, Role.WORKER} and order.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch mismatch")
    try:
        async with session.begin():
            order = await fulfill_order(
                session,
                order=order,
                actor_user_id=user.id,
                actor_role=user.role,
                ip=request.client.host if request.client else "unknown",
            )
        await session.refresh(order)
        return order
    except (OrderError, Exception) as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
