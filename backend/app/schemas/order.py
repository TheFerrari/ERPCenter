from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    branch_id: int


class OrderSubmit(BaseModel):
    pass


class OrderLineCreate(BaseModel):
    item_id: int
    requested_qty: int


class OrderLineOut(BaseModel):
    order_id: int
    item_id: int
    requested_qty: int
    fulfilled_qty: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    branch_id: int
    status: OrderStatus
    created_by_user_id: int
    created_at: datetime
    lines: list[OrderLineOut] = []

    model_config = {"from_attributes": True}
