# AUTH_SECURITY_IMPLEMENTATION_REPORT.md

**Project:** ABDiploma Hub  
**Date:** 14 July 2026  
**Scope:** Authentication hardening from `SECURITY_AUDIT_REPORT.md`  
**Architecture preserved:** Opaque DB-backed sessions (not JWT); quiz/grading/question bank unchanged  

---

## Summary

| Finding | Status |
|---------|--------|
| Session expiration | **Done** — `expires_at` + TTL env + auto-delete on use |
| Hashed session tokens | **Done** — SHA-256 at rest; one-time plaintext → hash migration |
| Frontend token storage | **Done** — HttpOnly cookie primary; localStorage secret removed |
| Rate limiting | **Done** — auth + guest grade + feedback + reports |
| Password security | **Verified/tightened** — PBKDF2, max length, clearer validation |

**Tests:** backend `50 passed` · frontend `npm run build` OK  

---

## Changes made

### 1. Session expiration

- Model `UserSession.expires_at` (`backend/app/models/user_session.py`)
- TTL from `SESSION_TTL_HOURS` (default **168** = 7 days) in `backend/app/core/config.py`
- On every auth lookup (`deps.py`, `admin.py`): if expired (or missing expiry), **delete** row and return **401**  
  `"Session expired or invalid. Log in again."`
- New sessions get `expires_at = now + TTL` at login/register

### 2. Session token hashing

- Raw token generated with `secrets.token_urlsafe(32)` (client / cookie / Bearer only)
- DB stores `SHA-256(hex)` via `hash_session_token()` (`backend/app/core/security.py`)
- Lookups always hash the presented secret before querying
- Passwords remain PBKDF2-HMAC-SHA256 (200k) with `hmac.compare_digest`

### 3. Frontend session storage (HttpOnly cookies)

**Evaluation:** Same-origin Vite/reverse-proxy architecture supports cookies without JWT rewrite.

**Implemented:**

| Layer | Behavior |
|-------|----------|
| Backend | `Set-Cookie` HttpOnly, `Path=/`, `SameSite` (default `lax`), `Secure` from `AUTH_COOKIE_SECURE` |
| Backend | Still accepts `Authorization: Bearer` for scripts/tests |
| Backend | Login/register JSON still includes `token` for API clients — **SPA must not store it** |
| Frontend | `credentials: 'include'` on all API fetches |
| Frontend | Non-secret hint `localStorage.albertaprep_session=1` only |
| Frontend | Clears legacy `albertaprep_token` on successful login/restore |
| Frontend | CSP meta in `index.html` + API security headers middleware |

Login UX unchanged: register/login → dashboard; `/auth/me` restores cookie sessions.

### 4. Rate limiting

In-process limiter (`backend/app/core/rate_limit.py`):

| Scope | Endpoints | Default |
|-------|-----------|---------|
| `auth` | `/auth/login`, `/auth/register` | 10 / minute / IP |
| `public` | `/quiz/guest/grade`, `/feedback`, `/question-reports` | 30 / minute / IP |

Env: `RATE_LIMIT_ENABLED`, `RATE_LIMIT_AUTH_PER_MINUTE`, `RATE_LIMIT_PUBLIC_PER_MINUTE`  
429 body: `"Too many requests. Please wait a moment and try again."` (no secrets)

### 5. Password security

- Still never returned in API responses (`UserOut` / `AuthResponse`)
- Still never logged by error handlers (validation `input` stripped)
- Register: min 8, max 128, must mix letters and numbers; name max 100
- Register UI hint updated

### 6. Related hardening

- Admin API key compare → `hmac.compare_digest`
- API middleware: `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, restrictive CSP for JSON API

---

## Migrations

### Additive (automatic via `init_db()`)

1. `ALTER TABLE user_sessions ADD COLUMN expires_at DATETIME` if missing  
2. **Token hash migration** (`_migrate_session_token_hashes_and_expiry`):
   - If `token` is **not** already 64-char lowercase hex → treat as legacy plaintext → replace with `SHA-256(token)`
   - If `expires_at` is NULL → set `now + SESSION_TTL_HOURS`
3. Idempotent: re-running does not double-hash (hex64 rows skipped)

### Migration strategy (operators)

1. Deploy backend with new code  
2. Start app / run `python -m app.database.init_db` (or normal startup that calls `init_db`)  
3. Existing browsers holding **plaintext** tokens continue to work (server hashes on lookup)  
4. Ask users to log in again after TTL if any edge case leaves orphan rows  
5. Production: set `AUTH_COOKIE_SECURE=true` behind HTTPS; tune TTL and rate limits  

**No Alembic revision required** — additive SQLite/`create_all` path already used by this project.  
**No mass logout required** for hashing (preserve existing users/sessions as specified).

---

## Files touched

**Backend:**  
`security.py`, `config.py`, `deps.py`, `admin.py`, `session_cookie.py` (new), `rate_limit.py` (new), `routes/auth.py`, `routes/quiz.py`, `routes/feedback.py`, `models/user_session.py`, `schemas/auth.py`, `database/init_db.py`, `main.py`, `.env.example`, `tests/test_auth_security.py` (new)

**Frontend:**  
`lib/api.js`, `context/AuthContext.jsx`, `pages/Home.jsx`, `pages/Register.jsx`, `index.html`

**Docs:** this file  

---

## Security improvements

1. Stolen DB dump no longer yields usable session secrets (hashes only)  
2. Stolen old tokens eventually fail (TTL + delete)  
3. XSS cannot read session secret from `localStorage` (HttpOnly cookie)  
4. Brute-force / spam surfaces get friendly 429s  
5. Stronger password bounds and messages; admin key timing hardened  

---

## Remaining limitations

| Limitation | Notes |
|------------|--------|
| In-process rate limits | Per uvicorn worker only — still need nginx/Cloudflare limits in multi-instance prod |
| Login response still returns `token` JSON | Need for scripts; XSS at login instant can still steal if it reads the response body — mitigated by not storing afterward |
| Session presence hint in `localStorage` | Not a secret; spoofable only to trigger `/auth/me` (401 if no cookie) |
| Guest answer-key oracle | Rate-limited only; full bind-to-guest-session still open from audit HIGH-05 |
| Guest feedback ownership | Pre-existing MEDIUM-01 not changed in this pass |
| OpenAPI `/docs` | Still enabled (audit HIGH-06) — separate production toggle recommended |
| CSP meta | Good baseline; prefer HTTP headers at CDN; `'unsafe-inline'` styles needed for KaTeX/Tailwind |
| `AUTH_COOKIE_SECURE=false` default | Required for local HTTP; **must** be `true` in production HTTPS |
| Argon2id | Still PBKDF2-200k — adequate; Argon2id remains a future upgrade |

---

## Test coverage (`tests/test_auth_security.py`)

- Normal register/login + cookie + Bearer `/auth/me`  
- Token stored hashed ≠ raw  
- Active session accepted  
- Expired session → 401 + row deleted  
- Invalid session → 401  
- Unauthorized `/progress` → 401  
- Password validation messages (no password echo)  
- Brute-force login → 429  
- Logout invalidates session  
- Login response never contains password fields  

---

## Verification run

```
backend:  python -m pytest tests -q   → 50 passed
frontend: npm run build               → OK
```

---

## Production checklist

1. `AUTH_COOKIE_SECURE=true`  
2. `SESSION_TTL_HOURS` to product preference (e.g. 72–168)  
3. Edge rate limits mirroring auth/public scopes  
4. TLS termination; same-origin `/api` proxy  
5. Consider `docs_url=None` for public API hosts  

*End of report.*
