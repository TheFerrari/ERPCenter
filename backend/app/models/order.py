from __future__ import annotations

from datetime import datetime

from enum import StrEnum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.DRAFT)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    branch = relationship("Branch", back_populates="orders")
    created_by = relationship("User", back_populates="orders")
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
