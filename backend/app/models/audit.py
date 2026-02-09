from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(200))
    entity_type: Mapped[str] = mapped_column(String(200))
    entity_id: Mapped[str] = mapped_column(String(200))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON)

    actor = relationship("User", back_populates="audit_logs")
