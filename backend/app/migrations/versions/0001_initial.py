"""initial

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
    )
    op.create_index(op.f("ix_branches_name"), "branches", ["name"], unique=True)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("min_stock_level", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(op.f("ix_items_sku"), "items", ["sku"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("Admin", "Manager", "Worker", "Auditor", name="role"), nullable=False),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=True),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "stocks",
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), primary_key=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "submitted", "fulfilled", "cancelled", name="orderstatus"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "order_lines",
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), primary_key=True),
        sa.Column("requested_qty", sa.Integer(), nullable=False),
        sa.Column("fulfilled_qty", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=200), nullable=False),
        sa.Column("entity_type", sa.String(length=200), nullable=False),
        sa.Column("entity_id", sa.String(length=200), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("audit_logs")
    op.drop_table("order_lines")
    op.drop_table("orders")
    op.drop_table("stocks")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_items_sku"), table_name="items")
    op.drop_table("items")
    op.drop_index(op.f("ix_branches_name"), table_name="branches")
    op.drop_table("branches")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS role")
