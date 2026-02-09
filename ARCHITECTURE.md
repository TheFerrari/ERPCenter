# Architecture

## High-level diagram

```mermaid
flowchart LR
  subgraph Clients[Student PCs / Clients over WAN]
    Browser[Browser]
  end
  subgraph Server[Server PC]
    Portal[Django Portal (HTML Templates)]
    API[FastAPI API]
    DB[(PostgreSQL)]
  end

  Browser -->|HTTP| Portal
  Portal -->|HTTP/JSON| API
  API -->|SQL| DB
```

## HTTP/JSON flow
- The Django portal renders HTML templates and sends HTTP requests to the FastAPI service.
- FastAPI returns JSON responses; the portal parses them and renders results in templates.
- Authentication uses a JWT token returned by `/auth/login` and stored in the Django session.

## WAN considerations
- Client PCs connect to the portal over a WAN-like network, introducing latency and intermittent connectivity.
- The server PC should be placed in a stable network segment with public or VPN access.
- The API and database stay on the server-side network; only the portal is exposed to clients.

## Infrastructure choices
- **Docker Compose** provides a minimal, repeatable dev environment for the API, portal, and database.
- **PostgreSQL** is used for durable storage of inventory and orders.

## Security and access control
- Token auth (JWT) is issued by FastAPI; Django forwards the token in `Authorization` headers.
- RBAC (Admin, Manager, Viewer) is enforced on API routes using dependencies.

## Ethics & Security
- See `docs/ethics_code.md` for the code of ethics.
- See `docs/acl_rbac.md` for the RBAC/ACL table.
