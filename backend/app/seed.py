import asyncio

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.branch import Branch
from app.models.item import Item
from app.models.stock import Stock
from app.models.user import User


async def seed() -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(Branch).where(Branch.name == "HQ"))
        branch = result.scalar_one_or_none()
        if not branch:
            branch = Branch(name="HQ", location="Main", timezone="UTC")
            session.add(branch)
            await session.flush()

        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        if not result.scalar_one_or_none():
            session.add(
                User(
                    email="admin@example.com",
                    password_hash=hash_password("ChangeMe123!"),
                    role="Admin",
                    branch_id=None,
                )
            )

        result = await session.execute(select(Item).where(Item.sku == "SKU-001"))
        if not result.scalar_one_or_none():
            item = Item(sku="SKU-001", name="Widget", description="Example item", unit="pcs", min_stock_level=10)
            session.add(item)
            await session.flush()
            session.add(Stock(branch_id=branch.id, item_id=item.id, quantity=100))

        await session.commit()


if __name__ == "__main__":
    print(f"Seeding database at {settings.database_url}")
    asyncio.run(seed())
