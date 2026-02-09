from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text

from .db import init_db, SessionLocal
from . import models
from .security import hash_password
from .routes import auth, items, stock, orders

app = FastAPI(title="ERP Center API")

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(stock.router)
app.include_router(orders.router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_data()


def seed_data() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            users = [
                models.User(
                    email="admin@example.com",
                    hashed_password=hash_password("admin123"),
                    role="Admin",
                ),
                models.User(
                    email="manager@example.com",
                    hashed_password=hash_password("manager123"),
                    role="Manager",
                ),
                models.User(
                    email="viewer@example.com",
                    hashed_password=hash_password("viewer123"),
                    role="Viewer",
                ),
            ]
            db.add_all(users)
            db.commit()
        if db.query(models.Item).count() == 0:
            items = [
                models.Item(sku="SKU-001", name="Notebook", unit="pcs"),
                models.Item(sku="SKU-002", name="Pen", unit="pcs"),
            ]
            db.add_all(items)
            db.commit()
            for item in items:
                db.add(models.Stock(item_id=item.id, quantity=100))
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    finally:
        db.close()
