from __future__ import annotations

from pydantic import BaseModel


class ItemCreate(BaseModel):
    sku: str
    name: str
    description: str
    unit: str
    min_stock_level: int = 0


class ItemOut(ItemCreate):
    id: int

    model_config = {"from_attributes": True}
