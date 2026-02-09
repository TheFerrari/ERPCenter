from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderLine(Base):
    __tablename__ = "order_lines"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    requested_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    fulfilled_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    order = relationship("Order", back_populates="lines")
    item = relationship("Item", back_populates="order_lines")
