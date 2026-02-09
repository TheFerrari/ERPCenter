import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.branch import Branch
from app.models.item import Item
from app.models.order import Order
from app.models.order_line import OrderLine
from app.models.stock import Stock
from app.models.user import User


@pytest.mark.asyncio
async def test_fulfill_order_decrements_stock_and_audit(client, session):
    branch = Branch(name="B3", location="Loc", timezone="UTC")
    session.add(branch)
    await session.flush()
    manager = User(
        email="manager@example.com",
        password_hash=hash_password("Password123!"),
        role="Manager",
        branch_id=branch.id,
    )
    session.add(manager)
    item = Item(sku="SKU-2", name="Item2", unit="pcs", min_stock_level=0)
    session.add(item)
    await session.flush()
    session.add(Stock(branch_id=branch.id, item_id=item.id, quantity=50))
    order = Order(branch_id=branch.id, created_by_user_id=manager.id, status="submitted")
    session.add(order)
    await session.flush()
    session.add(OrderLine(order_id=order.id, item_id=item.id, requested_qty=10, fulfilled_qty=0))
    await session.commit()

    resp = await client.post("/v1/auth/login", json={"email": "manager@example.com", "password": "Password123!"})
    token = resp.json()["access_token"]

    fulfill = await client.post(
        f"/v1/orders/{order.id}/fulfill",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fulfill.status_code == 200

    refreshed = await session.execute(
        select(Stock).where(Stock.branch_id == branch.id, Stock.item_id == item.id)
    )
    stock = refreshed.scalar_one()
    assert stock.quantity == 40

    audits = await session.execute(select(AuditLog).where(AuditLog.entity_type == "Order"))
    assert audits.scalars().all()
