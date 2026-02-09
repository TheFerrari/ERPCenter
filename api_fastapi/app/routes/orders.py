from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db, require_roles

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager", "viewer"))):
    return db.query(models.Order).all()

@router.post("", response_model=schemas.OrderOut)
def create_order(db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager"))):
    order = models.Order(status="draft")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/lines", response_model=schemas.OrderOut)
def add_line(
    order_id: int,
    payload: schemas.OrderLineCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "manager")),
):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "draft":
        raise HTTPException(status_code=400, detail="Can only add lines to draft orders")
    item = db.get(models.Item, payload.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.qty <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    line = models.OrderLine(order_id=order.id, item_id=item.id, qty=payload.qty)
    db.add(line)
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/submit", response_model=schemas.OrderOut)
def submit_order(order_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager"))):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.lines:
        raise HTTPException(status_code=400, detail="Add at least one line before submitting")
    order.status = "submitted"
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/fulfill", response_model=schemas.OrderOut)
def fulfill_order(order_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager"))):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted orders can be fulfilled")
    for line in order.lines:
        stock = db.get(models.Stock, line.item_id)
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock missing for item {line.item_id}")
        if stock.quantity - line.qty < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock to fulfill order")
    for line in order.lines:
        stock = db.get(models.Stock, line.item_id)
        stock.quantity -= line.qty
    order.status = "fulfilled"
    db.commit()
    db.refresh(order)
    return order
