# Minimum Viable Product (MVP)

> Task 3 — Define the MVP. It must include all mandatory requirements and avoid unnecessary extras.
> A clear MVP reduces the risk of incomplete integration at the end of the project.

---

## 1. Implement First (mandatory)

**Data & database**
- [ ] SQLAlchemy models: `User`, `Branch`, `Stock`
- [ ] Stock keyed by `branch_id` + `product_id` + `quantity` (never negative)
- [ ] No product details stored locally (only `product_id`)

**Authentication & authorization**
- [ ] Login required for the Backoffice
- [ ] Passwords hashed (no plain text)
- [ ] Roles enforced on the backend, not only in the UI

**Backoffice — Admin**
- [ ] List users
- [ ] Create common users and assign them to a branch
- [ ] Modify users, change password, change branch
- [ ] Soft-delete users
- [ ] Admin does **not** manage stock

**Backoffice — Common users**
- [ ] Bound to exactly one branch
- [ ] Add / remove / consult stock on their own branch (validated quantity)
- [ ] List products currently in stock for their branch
- [ ] Cannot manage users or act on another branch

**Product data**
- [ ] Consume the external Product API (list products, get details)
- [ ] Product info reached through the Product MCP Server

**Client Web Interface**
- [ ] Simple public page for anonymous product & stock queries

## 2. Leave for Later

Useful, but not required for a working first version.

- [ ] Polished Swagger / API documentation
- [ ] Improved UI (styling, filtering, pagination)
- [ ] List products in stock with richer product details

## 3. Optional — Only if Time Allows

Nice-to-have, attempted only after the MVP is complete.

- [ ] View stock of **other** branches
- [ ] Multi-branch query: "to buy 3× X, 2× Y, 4× Z, which branch(es) should I visit?"

---

### Scope Boundary

> The MVP stops at a working Backoffice (admin user management + common-user stock operations,
> with backend-enforced auth) served by product data from the external API. Cross-branch views
> and multi-branch optimization are out of the MVP scope.
