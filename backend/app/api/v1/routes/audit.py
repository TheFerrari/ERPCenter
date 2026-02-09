from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routes.deps import get_current_user
from app.core.rbac import ROLE_ADMIN, ROLE_AUDITOR, require_role
from app.db.session import get_session
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=list[AuditLogRead])
async def list_audits(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[AuditLogRead]:
    require_role(current_user.role, {ROLE_ADMIN, ROLE_AUDITOR})
    result = await session.execute(select(AuditLog))
    return result.scalars().all()
