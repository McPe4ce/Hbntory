# Decision Record — Communication Strategies

> Task 2 — For each decision: the option chosen, its main benefit, its main trade-off / limitation.
> The most complex option is not the goal. Choose what fits the requirements and the team's capacity.

---

## Decision 1 — Backoffice

**Options:** REST + HTML/CSS/JS · or · Server-Side Rendering (SSR)

- **Chosen:** REST + HTML/CSS/JS
- **Benefit:** Clear front/back separation; the REST API (documented with Swagger) can be reused
  by other services and tested independently.
- **Trade-off / limitation:** More client-side JS to write than server-rendered templates, and
  weaker SEO / first-load — irrelevant for an internal authenticated interface.

## Decision 2 — Client Web Interface

**Options:** REST · or · WebSockets

- **Chosen:** REST
- **Benefit:** Each question is independent (no conversation history to keep), so the request/
  response model fits naturally and stays simple — no persistent connections to manage.
- **Trade-off / limitation:** No streaming / real-time push; the answer arrives in one block
  instead of word-by-word (a WebSocket would only be justified for a live chat experience).

## Decision 3 — AI Query Service ↔ MCP Tools

**Question:** How does the AI Query Service communicate with the MCP tools?

- **Chosen:** TBD
- **Benefit:** …
- **Trade-off / limitation:** …

## Decision 4 — Authentication (Backoffice)

**Options:** Flask signed-session cookie (bare user id) · or · JWT stored in the cookie

- **Chosen:** JWT stored in the cookie, carrying only `{user_id, exp}`.
- **Benefit:** A standard, explicitly-signed token with a real server-enforced
  expiry (`exp`) — the natural credential for the client-rendered REST + JS
  frontend chosen in Decision 1, where the JS calls the API with each request.
  Authorization (`is_admin` / `is_active`) is still re-checked against the DB
  on every request, so deactivating a user takes effect instantly.
- **Trade-off / limitation:** Adds a dependency (`pyjwt`) and token-lifecycle
  code (issue / decode / verify / expiry) over the near-zero-code built-in
  session. A JWT cannot be revoked before it expires — which is exactly why
  permissions are kept out of the token and read from the DB instead.

## Decision 5 — Password storage

**Options:** plain SHA256 · or · a dedicated password hash (scrypt / bcrypt / Argon2)

- **Chosen:** scrypt, via Werkzeug's `generate_password_hash` default. Routes only
  ever go through `User.set_password()` / `User.verify_password()`, so a plain-text
  password never reaches the DB — including in `seed.py`.
- **Benefit:** scrypt is deliberately slow and memory-hard, and salts every hash
  automatically. SHA256 is the opposite: built for speed, so a GPU can guess
  billions of passwords per second against a stolen table, and being unsalted, one
  precomputed rainbow table cracks every user at once. The memory cost is also what
  scrypt adds over bcrypt — it removes the GPU's parallelism advantage.
- **Trade-off / limitation:** Every login genuinely costs CPU and memory (that's the
  point, but it isn't free). We take Werkzeug's default cost parameters rather than
  tuning them, and depend on its hash format — acceptable, Flask ships it anyway.

## Decision 6 — Where authorization is enforced

**Options:** hide the controls a role shouldn't see · or · enforce in backend route logic

- **Chosen:** Backend, via three decorators in `auth/decorators.py` —
  `login_required` (any active user), `admin_required` (active admins),
  `common_user_required` (active non-admins; this is what keeps the admin out of
  stock). Each decodes the JWT for a `user_id`, re-loads the user from the DB, and
  checks from there.
- **Benefit:** Hiding a button only changes what the browser draws — the endpoint is
  still callable with `curl`. Enforcing server-side also means permissions reflect
  current DB state rather than what was true at login, so a soft-delete takes effect
  on the user's next request. This is why the token carries `user_id` and `exp` only,
  never the role.
- **Trade-off / limitation:** One extra DB read per request — negligible here, and
  it's what buys instant revocation. Decorators cover *role* but not *scope*: they
  can't know which branch a request targets, so `user.branch_id == stock.branch_id`
  is checked inside the stock routes themselves.

---

### Known limitations

- **An admin can deactivate their own account.** `DELETE /admin/users/<id>` has no
  self-target check, and with exactly one admin that locks the team out of user
  management. Accepted deliberately — the spec requires no second admin and no
  recovery flow. Re-running `seed.py` restores access.
- **A token stays valid until it expires.** No logout-everywhere or blacklist;
  impact limited by keeping permissions out of the token (Decision 4).

---

### Summary

| Decision | Choice | Main benefit | Main trade-off |
|---|---|---|---|
| Backoffice | REST + HTML/CSS/JS | Reusable, documented API; front/back separation | More client-side JS to write |
| Client Web Interface | REST | Independent questions; no persistent connection | No streaming / real-time push |
| AI Query ↔ MCP | *TBD* | *TBD* | *TBD* |
| Auth (Backoffice) | JWT in cookie (`{user_id, exp}`) | Standard signed token + real expiry; DB still checked | Extra dep + token lifecycle; no pre-expiry revocation |
| Password storage | scrypt (Werkzeug default) | Slow, memory-hard, auto-salted — unlike fast unsalted SHA256 | Real CPU/memory cost per login; untuned defaults |
| Authorization | Backend decorators, role read from DB | Safe against direct API calls; revocation is instant | One DB read per request; scope still checked in-route |
