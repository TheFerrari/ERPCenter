from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    actor_user_id: int
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    ip: str
    details: dict

    class Config:
        from_attributes = True
