# Diagrams

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

## Service Diagram (system architecture)

```mermaid
flowchart TD
    Internal["Internal Users<br/>(admin / common)"]
    Public["Anonymous Users"]

    Internal -->|authenticated HTTP| BO["Backoffice Service<br/>(Flask)"]
    Public -->|REST / WebSocket| CW["Client Web Interface"]

    CW -->|REST: product & stock queries| BO
    BO -->|SQLAlchemy| DB[("Relational Database<br/>(SQLite)")]
    BO -->|MCP tools: list / get product| MCP["Product MCP Server<br/>(FastMCP)"]
    MCP -->|REST read-only| API["External Product API<br/>(Docker)"]
```
