from fastapi import HTTPException, status

ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_WORKER = "Worker"
ROLE_AUDITOR = "Auditor"

ROLE_HIERARCHY = {
    ROLE_ADMIN: 3,
    ROLE_MANAGER: 2,
    ROLE_WORKER: 1,
    ROLE_AUDITOR: 1,
}


def require_role(user_role: str, allowed: set[str]) -> None:
    if user_role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")


def require_min_role(user_role: str, minimum: str) -> None:
    if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(minimum, 0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
