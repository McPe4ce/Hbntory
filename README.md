# Hbntory — System Architecture

> Team project · Architecture & design phase
> **No implementation code in this phase.** The goal is to design the system before building it.

---

## 🎯 Goal

Define the architecture of the system **before** implementing any feature.

As a team, we must identify:

- the **services** that make up the system,
- the **responsibility** of each service,
- the **data flow** between them,
- the main **technical decisions** and their trade-offs.

The design must be clear enough for **another team** to understand it without extra explanation.

---

## 📦 Context

The system is an inventory / product platform composed of several parts:

| Component | Short description |
|-----------|-------------------|
| Backoffice | Internal interface to manage the catalog and stock |
| Client Web Interface | Public-facing interface for end users |
| AI Query Service | Answers questions using an AI agent |
| MCP Tools | Tools the AI agent can call to fetch data |
| External Product API | Source of product data outside our system |

> This table only lists the pieces. **Defining how they connect is the work of this project.**

---

## 🧩 Task 1 — System Architecture

Produce an architecture document that answers:

- [ ] Which services the system will include.
- [ ] The responsibility of each service.
- [ ] How the services communicate with each other.
- [ ] Which data is stored **locally**.
- [ ] Which data comes from the **external Product API**.
- [ ] How the AI agent accesses product and stock information.

📄 **Deliverable:** `docs/architecture.md` + an initial **service diagram**.

---

## 🔌 Task 2 — Communication Strategies

For each decision below, record: **the option chosen**, **its main benefit**, and **its main trade-off / limitation**.

- [ ] **Backoffice** → REST + HTML/CSS/JS **or** Server-Side Rendering?
- [ ] **Client Web Interface** → REST **or** WebSockets?
- [ ] **AI Query Service** → how does it communicate with the MCP tools?

> The most complex option is not the goal. Choose what fits the requirements **and** the team's capacity.

📄 **Deliverable:** a written **Decision Record** (`docs/decisions.md`).

---

## 🚀 Task 3 — Minimum Viable Product (MVP)

Define an MVP that includes **all mandatory requirements** and avoids unnecessary extras.

- [ ] What we implement **first**.
- [ ] What we leave for **later**.
- [ ] **Optional** features attempted only if time allows.

> A clear MVP reduces the risk of incomplete integration at the end of the project.

📄 **Deliverable:** `docs/mvp.md`.

---

## ✅ Expected Deliverables

- [ ] Architecture document
- [ ] Initial service diagram
- [ ] Decision record for communication strategies
- [ ] MVP definition

---

## 📁 Suggested Repository Layout

```
Hbntory/
├── README.md
└── docs/
    ├── architecture.md      # Task 1
    ├── decisions.md         # Task 2
    ├── mvp.md               # Task 3
    └── diagrams/            # service diagram(s)
```

---

## 👥 Team

| Name | Role / Focus |
|------|--------------|
|      |              |
|      |              |

---

*Design phase only — no implementation code committed at this stage.*
