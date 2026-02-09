# ERPCenter Inventory & Order Management API

FastAPI-based, stateless, token-authenticated API for multi-branch inventory, orders, and audit logging.

## Features
- Stateless JWT authentication (access + refresh tokens)
- RBAC: Admin, Manager, Worker, Auditor
- Branches, items, stock, orders, and fulfillment
- Audit logging for sensitive actions
- Async SQLAlchemy 2.x + Alembic migrations
- Docker Compose dev environment
- Health and readiness endpoints

## Quick Start (Docker Compose)
```bash
cp .env.example .env
make up
```

API docs available at: `http://localhost:8000/docs`

## Migrations
```bash
make upgrade
```

## Tests
```bash
make test
```

## Seed data
Creates an Admin user, a sample branch, and items/stock.
```bash
make seed
```

## Stateless Token Auth
- No server-side sessions or cookies are used.
- Every protected request must include a valid JWT access token.
- Refresh tokens are hashed and stored server-side to support revocation.

## API Examples
See [docs/api_examples.md](docs/api_examples.md).
