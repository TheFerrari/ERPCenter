from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_audit(
    session: AsyncSession,
    actor_user_id: int,
    action: str,
    entity_type: str,
    entity_id: str,
    ip: str,
    details: dict,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip=ip,
        details=details,
    )
    session.add(entry)
    await session.flush()
    return entry
