# ERPCenter (FastAPI)

Stateless, token-based inventory and order management API for multi-branch operations.

## Features
- JWT access + refresh tokens with no server-side sessions
- RBAC (Admin/Manager/Worker/Auditor)
- Branches, items, stock, orders, audit logs
- Health and readiness endpoints
- Docker Compose for local infra

## Local development (Docker Compose)
1. Copy env:
   ```bash
   cp .env.example .env
   ```
2. Start services:
   ```bash
   docker compose up --build
   ```
3. Open docs: `http://localhost:8000/docs`

## Migrations
```bash
make upgrade
```

## Seed data
```bash
docker compose run --rm backend python -m app.seed
```

## Tests
```bash
make test
```

## Example API usage
See [docs/api_examples.md](docs/api_examples.md) for full curl examples.

## Stateless token auth
- No server-side sessions or cookies are used.
- Each protected request must include `Authorization: Bearer <access_token>`.
- Access tokens are short-lived; refresh tokens are stored hashed in the database and can be revoked on logout.

