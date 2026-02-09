from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, require_role

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), user=Depends(require_role("Admin", "Manager", "Viewer"))):
    orders = db.query(models.Order).all()
    return orders


@router.post("", response_model=schemas.OrderOut)
def create_order(
    payload: schemas.OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    order = models.Order(status=payload.status)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/lines", response_model=schemas.OrderOut)
def add_line(
    order_id: int,
    payload: schemas.OrderLineCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    item = db.query(models.Item).filter(models.Item.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    line = models.OrderLine(order_id=order_id, item_id=payload.item_id, qty=payload.qty)
    db.add(line)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/submit", response_model=schemas.OrderOut)
def submit_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "submitted"
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/fulfill", response_model=schemas.OrderOut)
def fulfill_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "submitted":
        raise HTTPException(status_code=400, detail="Order must be submitted first")
    for line in order.lines:
        stock = db.query(models.Stock).filter(models.Stock.item_id == line.item_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        if stock.quantity < line.qty:
            raise HTTPException(status_code=400, detail="Insufficient stock")
    for line in order.lines:
        stock = db.query(models.Stock).filter(models.Stock.item_id == line.item_id).first()
        stock.quantity -= line.qty
    order.status = "fulfilled"
    db.commit()
    db.refresh(order)
    return order
