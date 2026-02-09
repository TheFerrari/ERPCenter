# Requirements Summary

- **HTML + Django portal**: Implemented in `portal_django/` using Django templates (`webui/templates/webui/*`).
- **FastAPI + Uvicorn backend**: Implemented in `api_fastapi/app/` with `main.py` and route modules.
- **HTTP/JSON between portal and API**: Django uses `requests` in `webui/views.py` to call FastAPI endpoints.
- **Multi-client WAN concept**: Explained in `ARCHITECTURE.md` with a WAN-style diagram and notes.
- **Security + ethics**: RBAC enforced in API dependencies (`app/deps.py`), with docs in `docs/acl_rbac.md` and `docs/ethics_code.md`.
- **Inventory & Orders domain**: Models and endpoints in `api_fastapi/app/models.py` and routes under `api_fastapi/app/routes/`.
- **PostgreSQL**: Docker Compose includes `postgres` service; API uses SQLAlchemy.
- **Auth**: `/auth/login` returns JWT, configured by `API_JWT_SECRET`.
- **Health endpoints**: `/health` and `/ready` in API.
- **Docs**: API examples in `docs/api_examples.md`; setup and usage in `README.md`.

