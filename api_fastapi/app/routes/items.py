from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db, require_roles

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[schemas.ItemOut])
def list_items(db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager", "viewer"))):
    return db.query(models.Item).all()

@router.post("", response_model=schemas.ItemOut)
def create_item(
    payload: schemas.ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "manager")),
):
    item = models.Item(sku=payload.sku, name=payload.name, unit=payload.unit)
    db.add(item)
    db.commit()
    db.refresh(item)
    if not item.stock:
        stock = models.Stock(item_id=item.id, quantity=0)
        db.add(stock)
        db.commit()
    return item

@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db), user=Depends(require_roles("admin", "manager", "viewer"))):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(
    item_id: int,
    payload: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "manager")),
):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item
