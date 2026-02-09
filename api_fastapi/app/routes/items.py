from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, require_role

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[schemas.ItemOut])
def list_items(db: Session = Depends(get_db), user=Depends(require_role("Admin", "Manager", "Viewer"))):
    items = db.query(models.Item).all()
    return items


@router.post("", response_model=schemas.ItemOut)
def create_item(
    payload: schemas.ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    item = models.Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    stock = models.Stock(item_id=item.id, quantity=0)
    db.add(stock)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager", "Viewer")),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(
    item_id: int,
    payload: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("Admin", "Manager")),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
