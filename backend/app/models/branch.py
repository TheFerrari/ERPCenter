from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    location: Mapped[str] = mapped_column(String(200))
    timezone: Mapped[str] = mapped_column(String(64))

    users = relationship("User", back_populates="branch")
    stocks = relationship("Stock", back_populates="branch")
    orders = relationship("Order", back_populates="branch")
