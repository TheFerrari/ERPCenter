from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(500))
    unit: Mapped[str] = mapped_column(String(32))
    min_stock_level: Mapped[int] = mapped_column(default=0)

    stocks = relationship("Stock", back_populates="item")
    order_lines = relationship("OrderLine", back_populates="item")
