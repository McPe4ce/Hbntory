# Architecture Document

> Task 1 — Define the system architecture.
> Fill each section. Keep it clear enough for another team to understand the design.

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

| Tool       | Role                          |
|------------|-------------------------------|
| Flask      | Framework                     |
| SQLAlchemy | ORM                           |
| SQLite     | Database                      |
| Swagger    | REST API documentation format |
| Mermaid    | Class diagrams                |
| VSCode     | IDE                           |
| Docker     | Containers                    |
| FastMCP    | MCP framework                 |

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

- **Product MCP Server** — Single gateway to the Product API. Exposes tools to `list products`
  and `get product details`. *Not:* Backoffice business logic; writing data.

- **Client Web Interface** — Simple public page (search-box / chat style) for anonymous users to
  ask about products and stock, via the Backoffice.
  *Not:* authentication; direct database or Product API access.

## 3. Communication Between Services

How does each service talk to the others? (protocol, direction, sync/async)

- Backoffice → Relational Database : SQLAlchemy (ORM)
- Backoffice → Product MCP Server : MCP tools (`list products`, `get product details`)
- Product MCP Server → External Product API : REST, read-only
- Client Web Interface → Backoffice : REST or WebSocket (product & stock queries — see `decisions.md`)

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

## 6. Service Diagram

See the **Service Diagram** and **Class Diagram** in [`docs/diagrams/`](diagrams/README.md).
