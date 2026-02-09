from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditOut(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    ip: str
    details: dict

    model_config = {"from_attributes": True}
