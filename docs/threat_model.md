# Threat Model Summary

| Threat | Risk | Mitigation |
| --- | --- | --- |
| Token theft | Unauthorized access | Short-lived access tokens, hashed refresh tokens, HTTPS/TLS, no token logging. |
| SQL injection | Data corruption | SQLAlchemy parameterization, no raw user input in SQL. |
| Privilege escalation | Data exposure | Strict RBAC checks per route, branch scoping for managers/workers. |
| Replay attacks | Duplicate transactions | Access token expiry + refresh rotation strategy, audit logs for sensitive actions. |
| Insider misuse | Data loss | Least privilege, audit logging, immutable logs. |
| Denial of service | Service disruption | Rate limiting recommended via gateway, health checks and autoscaling. |
| Data loss | Compliance risk | Backups, PITR, restore drills, replication. |
