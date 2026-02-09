from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    WORKER = "Worker"
    AUDITOR = "Auditor"


def can_manage_branch(role: Role) -> bool:
    return role in {Role.ADMIN, Role.MANAGER}


def can_manage_users(role: Role) -> bool:
    return role == Role.ADMIN


def can_read_audit(role: Role) -> bool:
    return role in {Role.ADMIN, Role.AUDITOR}


def can_adjust_stock(role: Role) -> bool:
    return role in {Role.ADMIN, Role.MANAGER}
