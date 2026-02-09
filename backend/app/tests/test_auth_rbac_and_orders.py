from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.rbac import Role
from app.core.security import hash_password
from app.models.branch import Branch
from app.models.item import Item
from app.models.order import Order, OrderStatus
from app.models.order_line import OrderLine
from app.models.stock import Stock
from app.models.user import User
from app.models.audit import AuditLog


async def seed_user(session, *, role: Role, branch_id: int | None = None, email: str = "user@example.com"):
    user = User(email=email, password_hash=hash_password("password123"), role=role, branch_id=branch_id)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def seed_branch(session):
    branch = Branch(name="Main", location="HQ", timezone="UTC")
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return branch


async def seed_item(session):
    item = Item(sku="SKU-1", name="Widget", description="Test", unit="each", min_stock_level=1)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@pytest.mark.asyncio
async def test_login_and_token_verification(client, session):
    branch = await seed_branch(session)
    await seed_user(session, role=Role.ADMIN, branch_id=branch.id, email="admin@example.com")

    resp = await client.post("/v1/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    auth_headers = {"Authorization": f"Bearer {token}"}
    branches = await client.get("/v1/branches", headers=auth_headers)
    assert branches.status_code == 200


@pytest.mark.asyncio
async def test_worker_cannot_adjust_stock(client, session):
    branch = await seed_branch(session)
    item = await seed_item(session)
    await seed_user(session, role=Role.WORKER, branch_id=branch.id, email="worker@example.com")

    login = await client.post("/v1/auth/login", json={"email": "worker@example.com", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.patch(
        "/v1/stock",
        json={"branch_id": branch.id, "item_id": item.id, "quantity": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_fulfill_order_decrements_stock_and_audits(client, session):
    branch = await seed_branch(session)
    item = await seed_item(session)
    manager = await seed_user(session, role=Role.MANAGER, branch_id=branch.id, email="manager@example.com")
    stock = Stock(branch_id=branch.id, item_id=item.id, quantity=10)
    session.add(stock)
    order = Order(branch_id=branch.id, created_by_user_id=manager.id, status=OrderStatus.SUBMITTED)
    session.add(order)
    await session.flush()
    line = OrderLine(order_id=order.id, item_id=item.id, requested_qty=3, fulfilled_qty=0)
    session.add(line)
    await session.commit()

    login = await client.post("/v1/auth/login", json={"email": "manager@example.com", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.post(
        f"/v1/orders/{order.id}/fulfill",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    refreshed_stock = (await session.execute(select(Stock).where(Stock.branch_id == branch.id))).scalar_one()
    assert refreshed_stock.quantity == 7

    audit_entries = (await session.execute(select(AuditLog).where(AuditLog.entity_type == "order"))).scalars().all()
    assert audit_entries
