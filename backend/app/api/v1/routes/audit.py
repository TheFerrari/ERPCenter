from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.rbac import Role
from app.db.session import get_session
from app.models.audit import AuditLog
from app.schemas.audit import AuditOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut], dependencies=[Depends(require_roles(Role.ADMIN, Role.AUDITOR))])
async def list_audit_logs(session: AsyncSession = Depends(get_session)) -> list[AuditOut]:
    result = await session.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
    return list(result.scalars().all())
