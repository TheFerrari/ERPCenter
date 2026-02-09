# Threat Model

## Assets
- Inventory and order data
- User credentials and tokens
- Audit logs

## Threats and mitigations
| Threat | Risk | Mitigation |
| --- | --- | --- |
| Token theft | Unauthorized access | Short-lived access tokens, refresh token revocation |
| Credential stuffing | Account takeover | Strong password policy, MFA (future), gateway rate limiting |
| Insider misuse | Data tampering | RBAC, audit logs, least privilege |
| SQL injection | Data exfiltration | ORM with parameterized queries |
| Network interception | Data leakage | TLS, VPN/SD-WAN |

## Residual risks
- Misconfigured gateway or TLS termination could expose traffic.
- Excessive token TTLs could increase exposure.
