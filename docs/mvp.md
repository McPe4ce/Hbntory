# Minimum Viable Product (MVP)

Scope definition for HBntory. The MVP covers every mandatory requirement and
deliberately avoids extras, so that integration is complete rather than broad and
half-finished.

Companion documents: [`architecture.md`](architecture.md) for the system design,
[`decisions.md`](decisions.md) for the reasoning behind each choice, and the
project [README](../README.md) for setup and API usage.

---

## 1. Core scope

**Data & database**

- [x] SQLAlchemy models: `User`, `Branch`, `Stock`
- [x] Stock keyed by `branch_id` + `product_id` + `quantity`, never negative
- [x] No product details stored locally — only `product_id`
- [x] Idempotent seed script: admin, branches, common users, sample stock

**Authentication & authorization**

- [x] Login required for the Backoffice
- [x] Passwords hashed with scrypt — no plain text anywhere, including the seed
- [x] Roles enforced in backend route logic, not by hiding controls
- [x] Deactivated users rejected at login and on every subsequent request

**Backoffice — Admin**

- [x] List users
- [x] Create common users and assign them to an existing branch
- [x] Modify users: change password, change branch
- [x] Soft-delete users
- [x] Admin cannot manage stock

**Backoffice — Interface**

- [x] Lightweight HTML/CSS/JS interface over the REST API
- [x] Sign-in screen, with expired sessions returning to it
- [x] The branch a common user operates on is stated in the header
- [x] Views selected by role, with authorization still enforced server-side

**Backoffice — Common users**

- [x] Bound to exactly one branch
- [x] Add / remove / consult stock on their own branch, with validated quantities
- [x] List products currently in stock for their branch
- [x] Cannot manage users or act on another branch

**Product data**

- [x] Consume the external Product API: list products, get details
- [x] All product access routed through the Product MCP Server
- [x] Catalog pagination handled transparently
- [x] External API failures surfaced as explicit, distinguishable results

**Client Web Interface**

- [x] Public page for anonymous product & stock queries
- [x] Loading state and error handling for network and server failures
- [x] Realistic worked examples covering each supported question type

**Integration**

- [x] All services start together under Docker Compose
- [x] Services address each other by name on a shared network
- [x] Database persisted in a named volume across rebuilds

---

## 2. Deferred

Useful, but outside the MVP.

- Swagger / OpenAPI specification for the REST API
- Product search and filtering for Backoffice users
- Richer stock listings that inline full product details
- UI styling, pagination and filtering beyond the functional minimum

---

## 3. Descoped for this phase

- **AI Query Service.** Confirmed with the professor. The Product MCP Server
  remains mandatory and is fully implemented; the LLM agent that would consume it
  is deferred. `POST /api/query` is answered directly by the Backoffice against a
  stable contract, so an agent can be substituted later without touching the
  Client Web Interface. See Decision 3 in [`decisions.md`](decisions.md).

---

## 4. Optional extensions

Attempted only once the MVP is complete.

- [x] Multi-branch query: "to buy 3× X and 2× Y, which branch should I visit?"
- [ ] Viewing the stock of other branches from the Backoffice

The multi-branch query was delivered ahead of scope: the client answers shopping
lists by first looking for a single branch holding everything, then falling back
to a per-branch breakdown.

---

## Scope boundary

The MVP is a working Backoffice — admin user management and common-user stock
operations, both under backend-enforced authorization — served by product data
read live from the external API through the MCP server, plus a public query page
for anonymous users. Cross-branch stock visibility from the Backoffice sits
outside that boundary.
