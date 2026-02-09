from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER, require_role
from app.db.session import get_session
from app.models.order import Order
from app.models.order_line import OrderLine
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderLineCreate,
    OrderLineRead,
    OrderRead,
)
from app.services.audit_service import log_audit
from app.services.order_service import fulfill_order

router = APIRouter(prefix="/orders", tags=["orders"])


def enforce_branch_scope(user: User, branch_id: int) -> None:
    if user.role != ROLE_ADMIN and user.branch_id != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch scope violation")


@router.get("/", response_model=list[OrderRead])
async def list_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[OrderRead]:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    query = select(Order)
    if current_user.role != ROLE_ADMIN:
        query = query.where(Order.branch_id == current_user.branch_id)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderRead:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    enforce_branch_scope(current_user, payload.branch_id)
    order = Order(branch_id=payload.branch_id, created_by_user_id=current_user.id)
    session.add(order)
    await log_audit(
        session,
        actor_user_id=current_user.id,
        action="order_created",
        entity_type="Order",
        entity_id="new",
        ip="-",
        details={"branch_id": payload.branch_id},
    )
    await session.commit()
    await session.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderRead:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    enforce_branch_scope(current_user, order.branch_id)
    return order


@router.post("/{order_id}/lines", response_model=OrderLineRead, status_code=status.HTTP_201_CREATED)
async def add_order_line(
    order_id: int,
    payload: OrderLineCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderLineRead:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    enforce_branch_scope(current_user, order.branch_id)
    if order.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not editable")
    line = OrderLine(order_id=order_id, item_id=payload.item_id, requested_qty=payload.requested_qty)
    session.add(line)
    await log_audit(
        session,
        actor_user_id=current_user.id,
        action="order_line_added",
        entity_type="Order",
        entity_id=str(order_id),
        ip="-",
        details={"item_id": payload.item_id, "qty": payload.requested_qty},
    )
    await session.commit()
    await session.refresh(line)
    return line


@router.post("/{order_id}/submit")
async def submit_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER, ROLE_WORKER})
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    enforce_branch_scope(current_user, order.branch_id)
    if order.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not draft")
    order.status = "submitted"
    await log_audit(
        session,
        actor_user_id=current_user.id,
        action="order_submitted",
        entity_type="Order",
        entity_id=str(order_id),
        ip="-",
        details={},
    )
    await session.commit()
    return {"status": "submitted"}


@router.post("/{order_id}/fulfill")
async def fulfill(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_MANAGER})
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    enforce_branch_scope(current_user, order.branch_id)
    allow_negative = current_user.role == ROLE_ADMIN
    await fulfill_order(session, order, current_user.id, "-", allow_negative)
    return {"status": "fulfilled"}
