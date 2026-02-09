# ERP Center MVP

Simple monorepo that delivers a Django HTML portal + FastAPI JSON API + PostgreSQL for an Inventory & Orders assignment.

## One-command startup
```bash
cp .env.example .env
make up
```

## Access URLs
- Django portal: http://localhost:8001/
- FastAPI docs: http://localhost:8000/docs

## Demo credentials
- Admin: `admin@example.com` / `admin123`
- Manager: `manager@example.com` / `manager123`
- Viewer: `viewer@example.com` / `viewer123`

## Seed data
Tables and sample data are created automatically on API startup (SQLAlchemy `create_all`).

## Project layout
- `portal_django/`: Django portal (HTML templates + Requests to API)
- `api_fastapi/`: FastAPI backend with JWT auth and RBAC
- `docs/`: API examples, ethics code, and RBAC rules

## Notes
- The Django portal connects to FastAPI using the `API_BASE_URL` from `.env`.
- `docker compose up --build` starts Postgres, the API, and the portal.
