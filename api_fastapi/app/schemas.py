from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ItemCreate(BaseModel):
    sku: str
    name: str
    unit: str


class ItemUpdate(BaseModel):
    name: str
    unit: str


class StockUpdate(BaseModel):
    quantity: int


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    quantity: int


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    unit: str
    stock: StockOut | None


class OrderCreate(BaseModel):
    status: str = "draft"


class OrderLineCreate(BaseModel):
    item_id: int
    qty: int


class OrderLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    qty: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    lines: list[OrderLineOut]
