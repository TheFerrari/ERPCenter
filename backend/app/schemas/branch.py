from pydantic import BaseModel


class BranchBase(BaseModel):
    name: str
    location: str
    timezone: str


class BranchCreate(BranchBase):
    pass


class BranchRead(BranchBase):
    id: int

    class Config:
        from_attributes = True
