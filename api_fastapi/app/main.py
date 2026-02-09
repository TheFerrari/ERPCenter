from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import Base, engine
from . import models
from .security import hash_password
from .deps import get_db
from .routes import auth, items, stock, orders

app = FastAPI(title="ERP Center API", version="0.1.0")

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(stock.router)
app.include_router(orders.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_data()


def seed_data():
    with engine.begin() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar_one()
        if count == 0:
            connection.execute(
                text("INSERT INTO users (email, password_hash, role) VALUES (:email, :password_hash, :role)"),
                [
                    {"email": "admin@example.com", "password_hash": hash_password("admin123"), "role": "admin"},
                    {"email": "manager@example.com", "password_hash": hash_password("manager123"), "role": "manager"},
                    {"email": "viewer@example.com", "password_hash": hash_password("viewer123"), "role": "viewer"},
                ],
            )
            connection.execute(
                text("INSERT INTO items (sku, name, unit) VALUES (:sku, :name, :unit)"),
                [
                    {"sku": "SKU-100", "name": "Widget", "unit": "pcs"},
                    {"sku": "SKU-200", "name": "Gadget", "unit": "pcs"},
                ],
            )
            connection.execute(text("INSERT INTO stock (item_id, quantity) VALUES (1, 25), (2, 10)"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}
