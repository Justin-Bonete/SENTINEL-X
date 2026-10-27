# Roadmap

| Phase | Focus | Status | You verify |
|---|---|---|---|
| 0 | Planning | Done | Blueprint reviewed |
| 1 | Foundation | In progress (prototype runs on SQLite) | Clean install; registered website shows up/down |
| 2 | Identity | Not started | Passkey login on 2 devices; bad challenge rejected (T-01 to T-04) |
| 3 | Authorization | Not started | Employee gets 403 on admin; cannot guess other IDs (T-05 to T-07, T-13) |
| 4 | Monitoring, alerts, revocation | Not started | Revoked session fails; audit tamper detected (T-08, T-10, T-11) |
| 5 | Hardening | Not started | Rate limits and no secret leakage (T-09, T-14) |
| 6 | Showcase | Not started | Reviewer runs it from the README |

## Phase 1 remaining
- [ ] Split `app/main.py` into `modules/monitoring` and `modules/audit`
- [ ] PostgreSQL + SQL migrations in `database/migrations`
- [ ] `/health` endpoint and passing foundation tests
- [ ] Port `apps/web/prototype` to React in `apps/web/src`
- [ ] Docker Compose brings up the whole stack
