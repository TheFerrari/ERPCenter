from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    stock = relationship("Stock", back_populates="item", uselist=False)
    lines = relationship("OrderLine", back_populates="item")

class Stock(Base):
    __tablename__ = "stock"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    item = relationship("Item", back_populates="stock")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="lines")
    item = relationship("Item", back_populates="lines")
