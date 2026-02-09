from __future__ import annotations

from pydantic import BaseModel


class StockAdjust(BaseModel):
    branch_id: int
    item_id: int
    quantity: int


class StockOut(BaseModel):
    branch_id: int
    item_id: int
    quantity: int

    model_config = {"from_attributes": True}
