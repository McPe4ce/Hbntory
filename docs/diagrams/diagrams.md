# Diagrams

Class, service and deployment views of HBntory. See
[`../architecture.md`](../architecture.md) for the written architecture and
[`../decisions.md`](../decisions.md) for the reasoning behind each choice.

## Class Diagram (data model)

```mermaid
classDiagram
    note "Hbntory class Diagram"

    class Basemodel {
        +str id
        +datetime created_at
        +datetime updated_at
        +save()
    }

    class User {
        +str email
        -str password_hash
        +str branch_id
        +bool is_admin
        +bool is_active
        +datetime deleted_at
        +set_password(raw_password)
        +verify_password(raw_password)
        +deactivate()
    }

    class Branch {
        +str branch_name
    }

    class Stock {
        +str product_id
        +int quantity
        +str branch_id
        +add_stock(amount) 
        +remove_stock(amount)
        +consult_stock()
    }

    Basemodel <|-- User
    Basemodel <|-- Branch
    Basemodel <|-- Stock

    Branch "1" --> "*" User : has
    Branch "1" --> "*" Stock : has
```

**Constraints enforced at the database level:**

- `Stock.quantity >= 0` — a check constraint, so stock cannot go negative even if a
  route is bypassed.
- `UNIQUE (branch_id, product_id)` on `Stock` — one stock line per product per branch.
- `UNIQUE (email)` on `User`.

`Stock` holds only `product_id`; no product name, description or price is ever
persisted. `Branch` is a plain entity, not a join table — `User` and `Stock` each
carry `branch_id`, so there is no direct `Stock` ↔ `User` relationship.
`User.branch_id` is nullable at the schema level solely because the admin belongs
to no branch; common users always have one, enforced in the admin create and edit
flows.

## Service Diagram (system architecture)

```mermaid
flowchart TD
    Internal["Internal Users<br/>(admin / common)"]
    Public["Anonymous Users"]

    Internal -->|"REST + JWT cookie"| BO["Backoffice Service<br/>(Flask)"]
    Public -->|"HTTP"| CW["Client Web Interface<br/>(static HTML/CSS/JS)"]

    CW -->|"POST /api/query"| BO
    BO -->|"SQLAlchemy"| DB[("Relational Database<br/>(SQLite)")]
    BO -->|"REST: GET /products, /products/:sku"| MCP["Product MCP Server<br/>(FastMCP + REST bridge)"]
    MCP -->|"REST read-only"| API["External Product API<br/>(provided Docker image)"]

    Agent["AI Query Service<br/>(deferred — Decision 3)"]
    Agent -.->|"MCP tools over stdio"| MCP

    style Agent stroke-dasharray: 5 5
```

The Backoffice reaches the MCP server over its REST wrapper rather than MCP
transport (Decision 3b). The MCP tools remain the canonical interface and are the
path a future AI Query Service would take — shown dashed because it is deferred
for this phase.

## Deployment Diagram (Docker Compose)

```mermaid
flowchart LR
    subgraph host["Developer machine"]
        B1["localhost:8080"]
        B2["localhost:5000"]
    end

    subgraph net["Docker network: hbntory_default"]
        CW["client_web<br/>nginx :80"]
        BO["backoffice<br/>flask :5000"]
        MCP["product_mcp_server<br/>flask :8001"]
        API["product-api<br/>:8000"]
        VOL[("volume<br/>backoffice_db")]
    end

    B1 --> CW
    B2 --> BO
    BO --> VOL
    BO -->|"http://product_mcp_server:8001"| MCP
    MCP -->|"http://product-api:8000"| API
```

Services address each other by Compose **service name**. The `product-api` node is
either the provided image (`--profile real`) or the local stand-in
(`--profile stub`); both are published under the same network alias, so no other
service changes between profiles.
