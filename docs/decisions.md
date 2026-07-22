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

---

### Summary

| Decision | Choice | Main benefit | Main trade-off |
|---|---|---|---|
| Backoffice | REST + HTML/CSS/JS | Reusable, documented API; front/back separation | More client-side JS to write |
| Client Web Interface | REST | Independent questions; no persistent connection | No streaming / real-time push |
| AI Query ↔ MCP | *TBD* | *TBD* | *TBD* |
