# Deployment guide — ABDiploma Hub

Production launch checklist for HTTPS, domain, env separation, and safe deploys. Does **not** auto-deploy; CI validates build/tests only.

Related: [SSL_SETUP.md](./SSL_SETUP.md), [.env.production.example](./.env.production.example), [DISASTER_RECOVERY.md](./DISASTER_RECOVERY.md).

## Recommended architecture

```
Internet
   │
   ▼
CDN / reverse proxy (TLS terminate, HSTS, HTTP→HTTPS)
   │
   ├── /          → static SPA (frontend/dist)
   └── /api/*     → FastAPI (uvicorn)  ←── SQLite or Postgres
```

**Preferred:** same-origin SPA + API so cookies stay simple and `VITE_API_URL` can stay empty.

**Alternatives:**

| Layer | Options |
|-------|---------|
| Frontend | Cloudflare Pages, Netlify, S3+CloudFront, nginx |
| Backend | Fly.io, Render, Railway, a small VPS (systemd + uvicorn) |
| Database | Managed Postgres (recommended for HA); SQLite OK for single node |
| Backups | Cron + `python scripts/backup_db.py` (see DISASTER_RECOVERY.md) |

## Environment setup

1. Copy [.env.production.example](./.env.production.example).
2. Fill **secrets** in the host secret store (never commit `.env`):
   - `SECRET_KEY` (required)
   - `DATABASE_URL`
   - `FRONTEND_URL=https://your-domain`
   - `ADMIN_EMAILS` / `ADMIN_API_KEY`
   - Optional: `SENTRY_DSN`, backup paths, analytics IDs
3. Frontend build-time vars (`VITE_*`) must be present when running `npm run build`.
4. Verify:

```bash
cd backend
ENVIRONMENT=production SECRET_KEY=… FRONTEND_URL=https://… \
  python scripts/check_production_config.py
```

## Frontend deployment

```bash
cd frontend
cp ../.env.production.example .env.production   # or export VITE_* in CI
# Edit .env.production — only VITE_* lines matter for the SPA
npm ci
npm run lint
npm run build    # regenerates robots.txt / sitemap.xml from VITE_SITE_URL
```

Deploy the contents of `frontend/dist/` to your static host.

SPA routing: configure the host to serve `index.html` for client routes (`/welcome`, `/login`, etc.).

Same-origin API: proxy `/api` to the backend (see SSL_SETUP.md). If the API is on another origin, set `VITE_API_URL` and ensure `FRONTEND_URL` CORS includes the site origin.

## Backend deployment

```bash
cd backend
python -m venv .venv
# activate venv
pip install -r requirements.txt
# load production env
python -m app.database.init_db   # create/upgrade tables (additive)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Production notes:

- `ENVIRONMENT=production`
- `ENABLE_API_DOCS=false` (default)
- Structured logging on automatically in production
- Sentry when `SENTRY_DSN` is set
- Bind to localhost behind the proxy; do not expose uvicorn directly to the internet

### Workers / SQLite

SQLite + multiple uvicorn workers can contend on writes. Use **one worker** with SQLite, or switch to Postgres for multi-worker.

## Database migration steps

This project uses SQLAlchemy models + `init_db` (create tables). There is no separate Alembic chain in the default layout.

1. **Backup first** (production):

   ```bash
   python scripts/backup_db.py
   python scripts/verify_backup.py
   ```

2. Deploy new code.

3. Run schema create/upgrade path used by the app (e.g. `init_db` on startup or explicit script). Confirm `/api/v1/ready` returns healthy.

4. If a release adds migrations, apply them in a maintenance window after backup.

5. Smoke-test: login, guest quiz, daily practice, admin health.

## Rollback procedure

1. **Stop** routing new traffic if the release is broken (platform rollback or proxy swap).
2. **Redeploy** the previous known-good frontend `dist` artifact and backend image/commit.
3. **Database:** only restore from backup if the bad release wrote corrupt data:

   ```bash
   python scripts/restore_db.py --help   # follow DISASTER_RECOVERY.md
   ```

4. Confirm `check_production_config.py`, `/health`, `/ready`, and a manual login.
5. File an incident note (Sentry release, git SHA, backup filename used).

Never restore over a live DB without a verified backup and a downtime window.

## CI

GitHub Actions (`.github/workflows/ci.yml`) on every push / PR:

- Frontend: `npm ci`, lint, production build
- Backend: compileall, pytest, production config check (with CI dummy secrets)

**No automatic deploy** — promote artifacts manually or add a gated deploy job later.

## Post-deploy smoke checklist

- [ ] `https://domain/` loads; HTTP redirects to HTTPS
- [ ] `/api/v1/health` and `/api/v1/ready` OK
- [ ] Login sets Secure HttpOnly session cookie
- [ ] robots.txt / sitemap.xml use the production host
- [ ] CORS: browser console has no origin errors
- [ ] Admin Reliability / Health views (if used) look normal
- [ ] Backup cron is scheduled
