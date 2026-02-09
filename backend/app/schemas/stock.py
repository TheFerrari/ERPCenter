from datetime import datetime

from pydantic import BaseModel


class StockBase(BaseModel):
    branch_id: int
    item_id: int
    quantity: int


class StockUpdate(BaseModel):
    quantity: int


class StockRead(StockBase):
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
