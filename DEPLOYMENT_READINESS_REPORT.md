# Deployment readiness report — ABDiploma Hub

**Date:** 2026-07-14  
**Scope:** Production environment separation, HTTPS/cookie safety, domain via env, CI, deployment docs  
**Out of scope (unchanged):** Quiz logic, authentication architecture, database schema, frontend UX

---

## Verdict

**Ready for public launch from an application-config perspective**, provided operators:

1. Set real production secrets (`SECRET_KEY`, admin, DB, optional Sentry/GA)
2. Terminate TLS and HTTP→HTTPS at the edge ([SSL_SETUP.md](./SSL_SETUP.md))
3. Deploy SPA + API per [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

Automated verification (this session): **backend 90 passed**, **frontend build OK**, **production config check OK** (SQLite + empty Sentry warnings only; exit 0).

---

## What was delivered

| Item | Location |
|------|----------|
| Production env template | [.env.production.example](./.env.production.example) |
| Env ignore hardening | Root + backend + frontend `.gitignore` |
| Secure cookies / HSTS defaults | `backend/app/core/config.py`, session + guest cookies, `main.py` |
| `SECRET_KEY` + signing fallback | config + guest quiz signing |
| Domain via env (canonical/OG/SEO) | `VITE_SITE_URL`, `write-seo-public.mjs`, Vite HTML transform |
| `VITE_API_URL` | `frontend/src/lib/api.js` (default same-origin `/api/v1`) |
| CORS | existing `FRONTEND_URL` (documented for production HTTPS origins) |
| Prod config gate | `backend/scripts/check_production_config.py` |
| SSL docs | [SSL_SETUP.md](./SSL_SETUP.md) |
| Deploy docs | [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) |
| CI (no auto-deploy) | [.github/workflows/ci.yml](./.github/workflows/ci.yml) |

---

## 1. Environment audit

### Frontend (`VITE_*`)

| Variable | Purpose | Safe default |
|----------|---------|--------------|
| `VITE_API_URL` | API origin; empty = same-origin `/api/v1` | empty |
| `VITE_SITE_URL` | Canonical / OG / JSON-LD / sitemap / robots | `https://abdiplomahub.com` |
| `VITE_GA_MEASUREMENT_ID` | GA4 | empty (disabled) |
| `VITE_SENTRY_DSN` | Browser Sentry | empty (disabled) |

### Backend

| Variable | Purpose | Production expectation |
|----------|---------|------------------------|
| `DATABASE_URL` | DB | Postgres preferred; SQLite OK single-node |
| `FRONTEND_URL` | CORS allowlist | HTTPS site origin(s), never `*` |
| `ENVIRONMENT` | Mode | `production` |
| `SECRET_KEY` | Signing | **Required** (≥32 chars recommended) |
| `SESSION_TTL_HOURS` / cookie settings | Sessions | Secure auto-on in production |
| `ADMIN_EMAILS` / `ADMIN_API_KEY` | Admin | At least one set |
| `SENTRY_DSN` | Errors | Optional but recommended |
| `BACKUP_DIR` / `BACKUP_RETENTION_DAYS` | DR | Non-web-served path |
| `ENABLE_API_DOCS` | OpenAPI UI | `false` |
| `ENABLE_HSTS` | HSTS header | Auto-on in production |

Secrets are not committed; `.env` / `.env.*` ignored with example exceptions.

---

## 2. HTTPS / SSL readiness

| Control | Status |
|---------|--------|
| Cookie `Secure` in production | **Yes** (`settings.cookie_secure`) |
| Guest quiz cookie Secure | **Yes** (same flag) |
| HSTS only in production | **Yes** (`settings.hsts_enabled`) |
| HTTP→HTTPS redirect | **Documented** at edge (not app-only) |
| Docs | [SSL_SETUP.md](./SSL_SETUP.md) |

---

## 3. Domain configuration

| Surface | Mechanism |
|---------|-----------|
| Canonical / Open Graph / JSON-LD | `VITE_SITE_URL` via `seo.js` + `index.html` build transform |
| `robots.txt` / `sitemap.xml` | Generated at build from `VITE_SITE_URL` |
| CORS | `FRONTEND_URL` env list |

No domain hardcoding required for a custom launch host beyond setting env vars.

---

## 4. Frontend production build

| Check | Result |
|-------|--------|
| `npm run lint` | Pass (existing warnings only) |
| `npm run build` | Pass (~0.5s); SEO files written |
| Main entry gzip | ~10 kB (`index-*.js`) |
| Note | `react-vendor` ~229 kB gzip (expected); KaTeX lazy-split |

API base remains `/api/v1` unless `VITE_API_URL` is set (no UX change).

---

## 5. Backend production mode

| Control | Status |
|---------|--------|
| Debug / OpenAPI docs | Off by default (`ENABLE_API_DOCS=false`) |
| Secure headers | Present (nosniff, frame deny, CSP, referrer, permissions) |
| HSTS | Production only |
| Structured logging | Auto-on when `ENVIRONMENT=production` |
| Error reporting | Sentry when prod + DSN |
| Prod config script | Enforces secret, CORS, docs off, secure cookies |

---

## 6–7. Documentation & CI

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) — architecture, FE/BE steps, migrations, rollback  
- [SSL_SETUP.md](./SSL_SETUP.md) — domain, certs, renewal, HSTS  
- CI on push/PR: frontend lint+build, backend compileall+pytest+config check — **no deploy job**

---

## Verification log

```
backend:  python -m pytest tests -q     → 90 passed
frontend: npm run lint                  → exit 0
frontend: npm run build                 → exit 0
backend:  check_production_config.py    → passed (SQLite + empty Sentry warnings OK)
```

### Security configuration notes (audit)

- Production defaults favor Secure cookies + HSTS + docs disabled.
- CORS still requires explicit `FRONTEND_URL` (fail closed if mis-set as `*`).
- Same-origin proxy recommended so session cookies stay `SameSite=Lax` without cross-site pain.
- Operators must still harden the edge (TLS, redirects, rate limits, backup cron).

---

## Remaining operator actions before public traffic

1. Purchase/attach domain + TLS ([SSL_SETUP.md](./SSL_SETUP.md))
2. Fill real secrets from [.env.production.example](./.env.production.example)
3. Schedule DB backups (`scripts/backup_db.py`)
4. Deploy FE `dist` + BE behind reverse proxy
5. Post-deploy smoke checklist in DEPLOYMENT_GUIDE.md
6. Optionally add a gated deploy job later (CI currently validates only)
