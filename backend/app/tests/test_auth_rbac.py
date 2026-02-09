import pytest

from app.core.security import hash_password
from app.models.branch import Branch
from app.models.item import Item
from app.models.stock import Stock
from app.models.user import User


@pytest.mark.asyncio
async def test_login_and_token_verification(client, session):
    branch = Branch(name="B1", location="Loc", timezone="UTC")
    session.add(branch)
    await session.flush()
    user = User(
        email="user@example.com",
        password_hash=hash_password("Password123!"),
        role="Worker",
        branch_id=branch.id,
    )
    session.add(user)
    await session.commit()

    resp = await client.post("/v1/auth/login", json={"email": "user@example.com", "password": "Password123!"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    items_resp = await client.get("/v1/items", headers={"Authorization": f"Bearer {token}"})
    assert items_resp.status_code == 403


@pytest.mark.asyncio
async def test_rbac_worker_cannot_adjust_stock(client, session):
    branch = Branch(name="B2", location="Loc", timezone="UTC")
    session.add(branch)
    await session.flush()
    user = User(
        email="worker@example.com",
        password_hash=hash_password("Password123!"),
        role="Worker",
        branch_id=branch.id,
    )
    session.add(user)
    item = Item(sku="SKU-1", name="Item", unit="pcs", min_stock_level=0)
    session.add(item)
    await session.flush()
    session.add(Stock(branch_id=branch.id, item_id=item.id, quantity=10))
    await session.commit()

    resp = await client.post("/v1/auth/login", json={"email": "worker@example.com", "password": "Password123!"})
    token = resp.json()["access_token"]
    adjust = await client.patch(
        f"/v1/stock/{branch.id}/{item.id}",
        json={"quantity": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert adjust.status_code == 403
