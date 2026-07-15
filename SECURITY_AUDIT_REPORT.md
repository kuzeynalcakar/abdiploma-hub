# ABDiploma Hub — Security Audit Report

**Role:** Senior security engineer (pre-launch audit)  
**Scope:** Full-stack codebase (`frontend/`, `backend/`)  
**Date:** 14 July 2026  
**Mode:** Analysis only — **no application fixes implemented** in this pass  

---

## Executive summary

ABDiploma Hub uses **opaque database-backed session tokens** (not JWTs), **PBKDF2-SHA256** password hashing, and generally sound **ownership checks** on student quiz/progress APIs. Admin endpoints are gated when configured.

**No Critical findings** (no confirmed unauthenticated admin access, no SQL injection on request input, no committed live API keys found in source).

Launch blockers and near-term priorities cluster around:

1. **Missing rate limiting** on auth / guest grading / feedback  
2. **Never-expiring sessions** + **plaintext tokens in DB** + **localStorage** exposure  
3. **Unauthenticated guest grading** as a full answer-key oracle  
4. **OpenAPI `/docs` enabled** by default in production  
5. **Admin identity leaked** in committed docs  

| Severity | Count |
|----------|------:|
| Critical | 0 |
| High     | 6 |
| Medium   | 9 |
| Low      | 8 |

---

## Positive controls (do not regress)

| Control | Location |
|---------|----------|
| PBKDF2-HMAC-SHA256 (200k iterations), per-password salt, `hmac.compare_digest` | `backend/app/core/security.py` |
| Opaque bearer sessions; logout deletes server row | `backend/app/routes/auth.py`, `backend/app/models/user_session.py` |
| Quiz attempt ownership (`403` if `attempt.user_id != current_user.id`) | `backend/app/routes/answers.py` (`_get_owned_attempt`) |
| Progress / weakness map / daily practice scoped by `current_user.id` | `progress.py`, `weakness_map.py`, `daily_practice.py` |
| Admin routes use `Depends(require_admin)` | `backend/app/routes/admin.py`, `feedback.py` |
| Multiple-choice API omits `is_correct` on choices | `backend/app/schemas/quiz.py` |
| Validation errors strip `input`/`ctx` (password leakage) | `backend/app/main.py` |
| Unhandled exceptions return generic 500 body | `backend/app/main.py` |
| `.env` listed in `backend/.gitignore` and `frontend/.gitignore` | gitignore files |
| Frontend token telemetry filters password/token fields | `frontend/src/lib/errors.js` |

---

## Findings

Findings are ordered by severity, then by launch impact.

---

### HIGH-01 — No rate limiting on authentication or abuse-prone endpoints

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `backend/app/main.py` (no limiter middleware); `backend/app/routes/auth.py`; `backend/app/routes/quiz.py` (`/guest/*`); `backend/app/routes/feedback.py` |
| **Explanation** | There is no application-level or documented reverse-proxy rate limiting. Attackers can brute-force logins, spam registrations, bulk-call guest grading, and flood feedback/question reports. |
| **Recommended fix** | Enforce per-IP (and per-email) limits at the reverse proxy **and** in-app (e.g. SlowAPI/Redis): stricter on `/auth/login`, `/auth/register`, `/quiz/guest/grade`, `/feedback`, `/question-reports`. Add lockout/backoff after repeated failures. |

---

### HIGH-02 — Sessions never expire

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `backend/app/models/user_session.py`; `backend/app/core/deps.py`; `backend/app/core/security.py` |
| **Explanation** | `UserSession` stores `created_at` only — no `expires_at` and no age check in `get_current_user`. A stolen bearer token remains valid until that row is deleted. The client message “Session expired or invalid” is misleading for age-based expiry. |
| **Recommended fix** | Add absolute TTL (and optionally idle timeout). Reject/delete expired sessions on each request; run a periodic purge. Consider rotating tokens on login and capping concurrent sessions per user. |

---

### HIGH-03 — Session tokens stored in plaintext in the database

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `backend/app/models/user_session.py`; `backend/app/core/deps.py`; `backend/app/core/admin.py` |
| **Explanation** | The full bearer secret is stored in `user_sessions.token`. A database backup leak or SQLite file theft yields immediate impersonation of every active session (passwords remain hashed). |
| **Recommended fix** | Store only a one-way hash of the token (e.g. SHA-256 of a high-entropy secret). Look up by hash; present the raw token to the client once at login. |

---

### HIGH-04 — Auth token in `localStorage` (XSS → full account takeover)

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `frontend/src/lib/api.js` (`TOKEN_KEY = 'albertaprep_token'`); compounded by `frontend/src/components/math/MathText.jsx` |
| **Explanation** | The session bearer lives in `localStorage`, readable by any XSS in the SPA origin. Combined with KaTeX `dangerouslySetInnerHTML` on question-bank content (MEDIUM-03), a single injected payload can steal sessions. Bearer-in-header is CSRF-light, but token theft risk is high. |
| **Recommended fix** | Prefer `HttpOnly; Secure; SameSite=Strict` (or `Lax`) session cookies set by the API, with CSRF strategy if cookies are used for mutating requests; **or** short-lived access token + refresh. Add a strict Content-Security-Policy. Keep treating question content as trusted-admin-only. |

---

### HIGH-05 — Unauthenticated guest grading is an answer-key oracle

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `backend/app/routes/quiz.py` (`GET /quiz/guest/questions`, `POST /quiz/guest/grade`) |
| **Explanation** | Anyone can request guest questions and grade arbitrary `question_id` values without auth. Responses include `correct_choice_id`, `expected_answer`, `explanation`, and `common_mistake`. This enables systematic scraping of the entire question bank and answer key — a business/IP and exam-integrity risk. |
| **Recommended fix** | Bind grading to a short-lived guest session listing issued question IDs; rate-limit aggressively; optionally CAPTCHA; refuse grading IDs not previously issued to that guest session. Consider delaying full explanations until after a constrained attempt. |

---

### HIGH-06 — OpenAPI / Swagger UI enabled by default

| | |
|---|---|
| **Severity** | High |
| **Affected files** | `backend/app/main.py` (`FastAPI(title=...)` with default docs); docs also advertised in `README.md` |
| **Explanation** | Production deployments expose `/docs`, `/redoc`, and `/openapi.json` unless disabled. That publishes the full API surface (including admin route shapes and auth details) to reconnaissance. |
| **Recommended fix** | In production: `docs_url=None`, `redoc_url=None`, `openapi_url=None` (or gate behind admin/VPN and an env flag such as `ENABLE_API_DOCS=true`). |

---

### MEDIUM-01 — Guest feedback can associate any `quiz_attempt_id` (integrity / oracle)

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `backend/app/routes/feedback.py` (`submit_feedback`, lines ~31–36) |
| **Explanation** | Ownership is enforced only when `current_user is not None`. Guests (or clients with invalid Bearer treated as anonymous via `get_optional_user`) can attach feedback to **any** existing `quiz_attempt_id`. Impact is data integrity and attempt-existence oracle (`404` vs success), not reading another user’s answers. |
| **Recommended fix** | If `quiz_attempt_id` is provided, **require** authentication and always enforce `attempt.user_id == current_user.id`. Disallow attempt linkage for anonymous submitters. |

---

### MEDIUM-02 — No request body size limits

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `backend/app/main.py`; input schemas under `backend/app/schemas/` |
| **Explanation** | No Starlette/uvicorn body-size middleware. Oversized JSON can drive CPU cost (especially PBKDF2 on huge passwords) and inflate DB text fields. |
| **Recommended fix** | Cap body size at the reverse proxy; add app middleware; set `max_length` on `name`, `password`, `response_text`, etc. |

---

### MEDIUM-03 — KaTeX renders HTML via `dangerouslySetInnerHTML`

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `frontend/src/components/math/MathText.jsx` |
| **Explanation** | LaTeX segments are rendered with KaTeX and injected as HTML. Plain text segments use React text nodes (safer). Risk is mainly from **compromised or malicious question-bank content**, not typical user free-text answers. With localStorage tokens (HIGH-04), XSS here is high impact. |
| **Recommended fix** | Treat bank content as privileged; restrict who can edit questions; keep KaTeX updated; add CSP; migrate sessions off `localStorage`. Avoid rendering untrusted user HTML through this path. |

---

### MEDIUM-04 — Missing max-length constraints on several inputs

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `backend/app/schemas/auth.py` (`name`, `password`); quiz/answer/`response_text` schemas |
| **Explanation** | Auth passwords require min length and letter/number mix but have no `max_length`. Names and textual answers lack upper bounds. Feedback messages correctly use `max_length=2000`. |
| **Recommended fix** | e.g. `name` ≤ 100, `password` ≤ 128, `response_text` ≤ 2000–5000 with Pydantic `Field(max_length=…)`. |

---

### MEDIUM-05 — CORS not explicitly configured (deployment footgun)

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `backend/app/main.py` (no `CORSMiddleware`); `frontend/vite.config.js` (dev same-origin proxy) |
| **Explanation** | Dev uses Vite proxy (same-origin `/api`) — good. If production serves API on another origin without a careful allowlist, teams often add `allow_origins=["*"]` under pressure. Current code has no CORS middleware (safe for same-origin; fragile if split). |
| **Recommended fix** | Prefer same-origin reverse-proxy `/api`. If cross-origin is required, allowlist exact origins from env — never `*`. with credentials carefully controlled. |

---

### MEDIUM-06 — HTTPS / TLS not enforced in application guidance

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `README.md`, `FINAL_LAUNCH_REPORT.md` (uvicorn `--host 0.0.0.0` over HTTP) |
| **Explanation** | App speaks plain HTTP. Bearer tokens on the wire are trivially stolen without TLS at the edge. |
| **Recommended fix** | Require TLS termination (Caddy/nginx/Cloudflare); bind uvicorn to localhost/private network only; add HSTS at the edge; never expose `:8000` publicly. |

---

### MEDIUM-07 — Admin email published in repository documentation

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `ADMIN_SETUP_REPORT.md` (and related admin reports); local `backend/.env` mirrors the same address |
| **Explanation** | A real admin email (`kuzeynalcakar@gmail.com`) appears in committed markdown. That aids phishing and targeted social engineering. `.env` itself is gitignored; the docs are not. |
| **Recommended fix** | Scrub PII from committed docs; replace with placeholders; treat publish history as leaked (monitor phishing); ensure only `.env` (private) holds admin emails. |

---

### MEDIUM-08 — Unauthenticated feedback and question reports (spam)

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `backend/app/routes/feedback.py` |
| **Explanation** | Guests may submit feedback and question reports. Text length helps; without rate limits this is an easy spam/abuse channel into admin workflows. |
| **Recommended fix** | Require auth for reports, or keep anonymous with strong rate limits + CAPTCHA + abuse monitoring. |

---

### MEDIUM-09 — No security headers / CSP on the SPA

| | |
|---|---|
| **Severity** | Medium |
| **Affected files** | `frontend/index.html`; production static hosting / reverse proxy config (not present in-repo) |
| **Explanation** | No Content-Security-Policy, `X-Frame-Options` / `frame-ancestors`, `X-Content-Type-Options`, or Referrer-Policy defined for the app shell. Increases impact of XSS and clickjacking. |
| **Recommended fix** | Set headers at CDN/nginx: strict CSP, `frame-ancestors 'none'`, `nosniff`, HSTS (with TLS). |

---

### LOW-01 — Admin API key compared with `==` (non-constant-time)

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | `backend/app/core/admin.py` (~line 63) |
| **Explanation** | `x_admin_key == settings.admin_api_key` may leak timing information in theory. |
| **Recommended fix** | Use `hmac.compare_digest` after normalizing both sides; reject empty keys. |

---

### LOW-02 — Email enumeration on registration

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | `backend/app/routes/auth.py` |
| **Explanation** | Registration returns a distinct message when the email already exists. Login uses a generic failure message (good). |
| **Recommended fix** | Consider generic copy + always-constant work; combined with rate limiting (HIGH-01) this is lower priority. |

---

### LOW-03 — Password policy floor is modest

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | `backend/app/schemas/auth.py` (`MIN_PASSWORD_LENGTH = 8`, letter+number mix) |
| **Explanation** | Meets a basic bar but is below stricter modern guidance (length 12+, breached-password checks). PBKDF2 at 200k is acceptable but Argon2id is preferred. |
| **Recommended fix** | Raise minimum length; optional haveibeenpwned k-anonymity check; consider Argon2id. |

---

### LOW-04 — `/health` discloses database connectivity

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | `backend/app/routes/health.py` |
| **Explanation** | Public response includes `"database": "unavailable"` on failure, aiding infrastructure mapping. |
| **Recommended fix** | Public probe returns liveness only; detailed dependency checks on an internal path. |

---

### LOW-05 — Foreign keys omit explicit `ondelete` behavior

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | Models such as `user_session.py`, quiz/report FK columns |
| **Explanation** | SQLite foreign keys are enabled in `session.py`, but many FKs rely on defaults. Risk is data hygiene / unexpected delete failures rather than direct exploit. |
| **Recommended fix** | Declare intentional `ondelete="CASCADE"|"SET NULL"|"RESTRICT"` per relationship. |

---

### LOW-06 — JWT mentioned in audit brief but not used

| | |
|---|---|
| **Severity** | Informational / Low (design note) |
| **Affected files** | `backend/app/core/security.py` (documents “No JWT”) |
| **Explanation** | Auth is **not** JWT-based. Tokens are opaque DB sessions — correct for server-side revoke on logout. Misconfiguration risk is assuming JWT expiry claims exist; they do not (see HIGH-02). |
| **Recommended fix** | Document session TTL clearly for operators; do not add unsigned/homemade JWTs without careful key management. |

---

### LOW-07 — Root `.gitignore` absent

| | |
|---|---|
| **Severity** | Low |
| **Affected files** | Repository root (no `.gitignore`); relies on `backend/.gitignore` / `frontend/.gitignore` |
| **Explanation** | A root-level `.env` would not inherit subdirectory ignore rules. Subproject `.env` files appear correctly ignored. |
| **Recommended fix** | Add a root `.gitignore` covering `.env`, `*.db`, secrets, and OS junk. Confirm with `git ls-files '*.env'` before publish. |

---

### LOW-08 — `/admin` UI blocked only by frontend + server — robots.txt is not security

| | |
|---|---|
| **Severity** | Low (informational) |
| **Affected files** | `frontend/public/robots.txt`; `frontend/src/components/auth/AdminRoute.jsx`; `backend/app/core/admin.py` |
| **Explanation** | Client route guards and robots disallow are not access control. Server `require_admin` is the real gate — currently present. |
| **Recommended fix** | Keep relying on server checks; never treat SPA redirects as authorization. |

---

## Authorization matrix (IDOR review)

| Endpoint area | Cross-user risk | Notes |
|---------------|-----------------|-------|
| `POST /quiz/answer`, `GET /quiz/attempt/{id}/results` | **Protected** | Ownership via `_get_owned_attempt` |
| `GET /progress`, `GET /weakness-map`, daily practice | **Protected** | Filtered by `current_user.id` |
| `GET /auth/me` | **Protected** | Current user only |
| `/admin/*`, `GET /feedback/admin` | **Protected** | `require_admin` (503 if unset) |
| `POST /feedback` + `quiz_attempt_id` as guest | **Weak** | MEDIUM-01 |
| `POST /quiz/guest/grade` | **N/A (public)** | HIGH-05 answer oracle |
| No student `user_id` query param for private data | **Good** | Reduces classic IDOR surface |

**Student-only UI gates** (`AuthGate`, `AdminRoute`) are UX only — API must remain the source of truth (it largely is).

---

## Authentication checklist (requested topics)

| Topic | Status |
|-------|--------|
| Password storage | **Good** — PBKDF2-SHA256, salted, constant-time verify |
| JWT implementation | **Not used** — opaque DB sessions instead |
| Token expiration | **Missing** — HIGH-02 |
| Session handling | Multi-device sessions OK; plaintext in DB — HIGH-03 |
| Logout | **Good** — deletes presented session server-side |
| Unauthorized access | Student private data largely locked; guest grade + feedback gaps above |

---

## Production configuration checklist

| Item | Status |
|------|--------|
| DEBUG / stack traces to clients | Handlers sanitize 500s; FastAPI not started with `debug=True` in `main.py` |
| Secret management | `.env` gitignored under backend/frontend; admin email in **docs** is a problem |
| CORS | Not configured (OK for same-origin proxy; document carefully) |
| Allowed origins | Not defined — recommend explicit env if cross-origin ever used |
| HTTPS readiness | App HTTP-only; **edge TLS required** before public launch |
| API docs | Enabled — disable in prod (HIGH-06) |
| Rate limiting | Absent — HIGH-01 |

---

## Recommended remediation order (before public launch)

1. **HIGH-01** Rate limit auth + guest grade + feedback at proxy and app  
2. **HIGH-05** Bind guest grading to issued question sets; throttle scrapers  
3. **HIGH-02 / HIGH-03** Session TTL + hash tokens at rest  
4. **HIGH-06** Disable `/docs` / OpenAPI in production  
5. **HIGH-04 / MEDIUM-03 / MEDIUM-09** Prefer HttpOnly cookies or CSP; treat KaTeX content as trusted  
6. **MEDIUM-01 / MEDIUM-08** Tighten feedback ownership and anonymous abuse controls  
7. **MEDIUM-02 / MEDIUM-04** Body size and field length caps  
8. **MEDIUM-06 / MEDIUM-07** TLS-only public exposure; scrub admin PII from git docs  
9. Remaining Low items as hardening 

---

## Out of scope / residual risks

- Dependency CVE scanning (`npm audit` / `pip-audit`) not fully enumerated in this pass — run before launch.  
- Host OS, cloud IAM, backup encryption, and WAF configuration are operator responsibilities.  
- Question bank integrity is a content-trust assumption; compromised admin accounts remain high impact.  
- This report did **not** implement fixes (per engagement instructions).

---

## Sign-off

| | |
|---|---|
| **Audit type** | Static code review + route/auth/IDOR analysis |
| **Code changes** | Report file only (`SECURITY_AUDIT_REPORT.md`) |
| **Next step** | Prioritize High findings; schedule a fix pass and re-audit |

*End of report.*
