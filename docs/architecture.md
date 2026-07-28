# Architecture Document

System design for HBntory — an inventory management system for a multi-branch
retail company. This document defines the services, their responsibilities, how
they communicate, and which data is held locally versus fetched from the external
Product API.

Companion documents: [`decisions.md`](decisions.md) records the reasoning behind
each communication strategy, [`mvp.md`](mvp.md) defines delivery scope, and the
project [README](../README.md) covers setup and API usage.

---

## 1. Services

The application services (system components).

| Service              | Purpose (one line)                                            |
|----------------------|---------------------------------------------------------------|
| Backoffice Service   | Authenticated internal web app: manages users & branch stock  |
| Relational Database  | Stores users, branches, stock quantities (product_id only)    |
| External Product API | Read-only source of product data (provided Docker container)  |
| Product MCP Server   | Bridge exposing tools to query the Product API                |
| Client Web Interface | Public page for anonymous product & stock queries             |

### Tech Stack

| Tool                 | Role                                          |
|----------------------|-----------------------------------------------|
| Flask                | Backoffice and MCP REST bridge framework      |
| SQLAlchemy           | ORM                                           |
| SQLite               | Database                                      |
| PyJWT                | Signed session tokens                         |
| Werkzeug (scrypt)    | Password hashing                              |
| FastMCP              | MCP server framework                          |
| Docker / Compose     | Containers and service orchestration          |
| nginx                | Static hosting for the Client Web Interface   |
| Mermaid              | Class, service and deployment diagrams        |

## 2. Responsibilities

What each service is responsible for — and what it is **not**.

- **Backoffice Service** — Authenticated web app. Manages users (admin) and branch stock
  (common users) through SQLAlchemy. Reaches product data via the Product MCP Server, and
  answers the Client Web Interface's product & stock queries.
  *Not:* storing product details; calling the Product API directly.

- **Relational Database** — Persists users, branches, and stock quantities keyed by `product_id`.
  *Not:* product name / description / price / image / metadata.

- **External Product API** — Read-only source of product data (Docker container we consume).
  *Not:* part of our codebase; never written to.

- **Product MCP Server** — Single gateway to the Product API. Exposes `list_products` and
  `get_product_details` as MCP tools, plus a thin REST wrapper over the same client logic.
  Normalises the external API's responses and turns its failure modes into explicit results
  (not found · API unreachable · API error). Handles catalog pagination so callers never see it.
  *Not:* Backoffice business logic; writing data; caching or persisting products.

- **Client Web Interface** — Simple public page (search-box / chat style) for anonymous users to
  ask about products and stock, via the Backoffice.
  *Not:* authentication; direct database or Product API access.

## 3. Communication Between Services

How does each service talk to the others? (protocol, direction, sync/async)

| From → To | Protocol | Direction | Sync |
|---|---|---|---|
| Backoffice → Relational Database | SQLAlchemy (ORM) | read / write | sync |
| Backoffice → Product MCP Server | HTTP REST (`GET /products`, `GET /products/<sku>`) | read-only | sync |
| Product MCP Server → External Product API | HTTP REST | read-only | sync |
| Client Web Interface → Backoffice | HTTP REST (`POST /api/query`) | request/response | sync |
| MCP client → Product MCP Server | MCP over stdio (`list_products`, `get_product_details`) | read-only | sync |

The Product MCP Server exposes the **same** catalog logic twice: as MCP tools in
`server.py` for MCP-speaking clients, and as a thin REST wrapper in `rest_api.py`
for the Backoffice. Both delegate to `product_api_client.py`, so the two surfaces
cannot drift apart. The Backoffice deliberately uses the REST wrapper rather than
MCP transport — see Decision 3b in [`decisions.md`](decisions.md).

All services run on one Docker Compose network and address each other by **service
name**, never `localhost`, which inside a container refers to that container itself.

## 4. Local Data

Which data do we store on our side, and where? (Relational Database)

- Users (credentials, role, assigned branch)
- Branches
- Stock: `branch_id` + `product_id` + `quantity`

## 5. External Data (Product API)

Which data comes from the external Product API? What do we consume, and how often?

- Product list
- Product details (name, description, price, image, metadata) — never persisted locally
- https://github.com/hbtn-edu/hbntory-products-api

## 6. How the AI agent accesses product and stock information

The AI Query Service is deferred for this phase (Decision 3 in
[`decisions.md`](decisions.md)), so the access path is defined rather than driven by
an agent. The path itself is built and in use:

1. A question arrives at the Backoffice on `POST /api/query` — unauthenticated.
2. The Backoffice resolves **stock** from its own database, since stock is local data
   no external service knows about.
3. It resolves **product data** through the Product MCP Server, which is the only
   component permitted to call the external Product API.
4. The two are combined into a single answer. Nothing about the product is persisted.

Substituting an LLM agent later means replacing step 4's engine. It would consume the
MCP tools directly instead of the REST wrapper, and the `POST /api/query` contract the
Client Web Interface depends on would not change.

## 7. Deployment

One Docker Compose network, four services:

| Service | Port | Image / build | Notes |
|---|---|---|---|
| `backoffice` | 5000 | `./backoffice` | Owns the SQLite volume |
| `product_mcp_server` | 8001 | `./product_mcp_server` | REST bridge; MCP tools run over stdio |
| `product-api` | 8000 | provided image, or local stand-in | Aliased as `product-api` under both Compose profiles |
| `client_web` | 8080 | `nginx:alpine` | Serves static files only |

The SQLite file lives in a named volume so it survives rebuilds. Setup and run
instructions are in the project [README](../README.md).

## 8. Diagrams

See the **Class Diagram**, **Service Diagram** and **Deployment Diagram** in
[`diagrams/diagrams.md`](diagrams/diagrams.md).
