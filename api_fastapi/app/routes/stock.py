from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db, require_roles

router = APIRouter(prefix="/stock", tags=["stock"])

@router.get("/{item_id}", response_model=schemas.StockOut)
def get_stock(item_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager", "viewer"))):
    stock = db.get(models.Stock, item_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.put("/{item_id}", response_model=schemas.StockOut)
def update_stock(
    item_id: int,
    payload: schemas.StockUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "manager")),
):
    stock = db.get(models.Stock, item_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    if payload.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be non-negative")
    stock.quantity = payload.quantity
    db.commit()
    db.refresh(stock)
    return stock
