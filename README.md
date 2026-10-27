# SENTINEL X

Prototype zero-trust access gateway: passkey login (planned), server-side authorization, session control, and a tamper-evident audit log, with a registry of the websites and systems it monitors. This is a prototype; it makes no certification or compliance claims.

## Run the Phase 1 prototype (SQLite, single page UI)
```
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```
Open http://localhost:8000 and paste the admin token printed in the console. Python 3.10+.

## Layout
| Path | Purpose |
|---|---|
| `apps/api/app/main.py` | Working Phase 1 prototype (to be split into modules) |
| `apps/api/app/modules/` | One folder per domain: monitoring, audit, identity, sessions, rbac, policy, resources, risk, alerts, gateway, admin |
| `apps/web/prototype/` | Working single-file dashboard |
| `apps/web/src/` | React + TypeScript app (pages, components, API client) |
| `infra/` | Docker Compose (Postgres, optional Redis, optional HTTPS proxy) |
| `database/` | SQL migrations and synthetic seed data |
| `tests/` | `api/`, `security/`, `e2e/`, with skipped tests mapped to T-01 to T-14 |
| `docs/` | Requirements, architecture, DFD, ERD, API, threat model, test plan, roadmap |

See `docs/roadmap.md` for phases and what to verify at each.
