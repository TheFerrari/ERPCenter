from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Role
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.branch import Branch
from app.models.item import Item
from app.models.stock import Stock
from app.models.user import User


async def seed() -> None:
    async with SessionLocal() as session:  # type: AsyncSession
        branch = Branch(name="HQ", location="Headquarters", timezone="UTC")
        session.add(branch)
        await session.flush()

        admin = User(
            email="admin@example.com",
            password_hash=hash_password("ChangeMe123!"),
            role=Role.ADMIN,
            branch_id=None,
        )
        session.add(admin)

        item = Item(sku="SKU-100", name="Starter Widget", description="Seed item", unit="each", min_stock_level=5)
        session.add(item)
        await session.flush()

        stock = Stock(branch_id=branch.id, item_id=item.id, quantity=25)
        session.add(stock)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
