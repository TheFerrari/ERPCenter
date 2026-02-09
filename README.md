# ERP Center MVP (Django Portal + FastAPI API)

This repository provides a simple, MVP-grade monorepo for an academic assignment. It includes:
- Django 5.x HTML portal that calls a FastAPI backend over HTTP/JSON.
- FastAPI + Uvicorn API with RBAC, JWT auth, and basic Inventory & Orders domain.
- PostgreSQL via Docker Compose.

## One-command startup

```bash
docker compose up --build
```

## Access
- Django portal: http://localhost:8000
- FastAPI docs: http://localhost:8001/docs

## Demo credentials
- Admin: `admin@example.com` / `admin123`
- Manager: `manager@example.com` / `manager123`
- Viewer: `viewer@example.com` / `viewer123`

## Seed data
The API auto-creates tables and seeds demo users, items, and stock at startup using SQLAlchemy `create_all()` and a simple seed routine. See `api_fastapi/app/db.py` and `api_fastapi/app/main.py` for details.

## Project docs
- Requirements summary: `REQUIREMENTS_SUMMARY.md`
- Architecture: `ARCHITECTURE.md`
- Ethics code: `docs/ethics_code.md`
- RBAC rules: `docs/acl_rbac.md`
- API examples: `docs/api_examples.md`

