from pydantic import BaseModel


class ItemBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    unit: str
    min_stock_level: int = 0


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int

    class Config:
        from_attributes = True
