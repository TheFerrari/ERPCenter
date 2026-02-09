from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.rbac import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role
    branch_id: int | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    branch_id: int | None

    model_config = {"from_attributes": True}
