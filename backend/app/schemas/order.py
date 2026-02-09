from datetime import datetime

from pydantic import BaseModel


class OrderBase(BaseModel):
    branch_id: int


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    id: int
    status: str
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderLineBase(BaseModel):
    item_id: int
    requested_qty: int


class OrderLineCreate(OrderLineBase):
    pass


class OrderLineRead(OrderLineBase):
    fulfilled_qty: int

    class Config:
        from_attributes = True
