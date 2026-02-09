from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    branch = relationship("Branch", back_populates="stocks")
    item = relationship("Item", back_populates="stocks")
