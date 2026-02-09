# Requirements Summary

- **Frontend in HTML + Django**: Portal uses Django templates in `portal_django/webui/templates/webui/` and views in `portal_django/webui/views.py`.
- **Backend API in FastAPI + Uvicorn**: API implemented in `api_fastapi/app` and served via Uvicorn in `api_fastapi/Dockerfile`.
- **Multi-client WAN concept**: Documented in `ARCHITECTURE.md` with clients (student PCs) connecting over WAN to server.
- **Security + ethics**: RBAC enforced in `api_fastapi/app/deps.py`; ethics code in `docs/ethics_code.md` and RBAC table in `docs/acl_rbac.md`.
- **Inventory & Orders domain**: Models and routes in `api_fastapi/app/models.py` and `api_fastapi/app/routes/`.
- **PostgreSQL**: Provided via Docker Compose service `postgres` in `docker-compose.yml`.
- **Django portal calls API via HTTP/JSON**: Requests in `portal_django/webui/views.py`.
- **JWT auth**: `/auth/login` implemented in `api_fastapi/app/routes/auth.py`.
- **CRUD endpoints**: Implemented in `api_fastapi/app/routes/items.py`, `stock.py`, and `orders.py`.
- **Health/ready**: `api_fastapi/app/main.py` includes `/health` and `/ready`.
- **Seed data**: `api_fastapi/app/main.py` seeds users, items, and stock on startup.
- **Documentation**: `README.md`, `ARCHITECTURE.md`, and `docs/*` provide setup, architecture, and examples.
