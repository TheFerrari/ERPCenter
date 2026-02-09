from __future__ import annotations

from pydantic import BaseModel


class BranchCreate(BaseModel):
    name: str
    location: str
    timezone: str


class BranchOut(BranchCreate):
    id: int

    model_config = {"from_attributes": True}
