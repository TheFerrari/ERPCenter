from datetime import datetime
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str
    password: str

class ItemBase(BaseModel):
    sku: str
    name: str
    unit: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    unit: str | None = None

class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True

class StockOut(BaseModel):
    item_id: int
    quantity: int

    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    quantity: int

class OrderLineCreate(BaseModel):
    item_id: int
    qty: int

class OrderLineOut(BaseModel):
    id: int
    item_id: int
    qty: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    created_at: datetime
    lines: list[OrderLineOut] = []

    class Config:
        from_attributes = True
