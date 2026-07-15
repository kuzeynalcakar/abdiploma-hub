# API_SECURITY_IMPLEMENTATION_REPORT.md

**Project:** ABDiploma Hub  
**Date:** 14 July 2026  
**Scope:** API security & data exposure (phase 2 from `SECURITY_AUDIT_REPORT.md`)  
**Preserved:** Auth architecture, quiz/grading logic, question bank content, frontend UX  

---

## Vulnerabilities fixed

| ID | Issue | Fix |
|----|--------|-----|
| Guest answer oracle | `/quiz/guest/grade` graded any `question_id` without a prior fetch | HttpOnly signed guest-quiz cookie binds grade calls to IDs from `/guest/questions` |
| Pre-submit answer leak | Risk of leaking keys/explanations on fetch | All quiz fetches serialize through `QuestionOut` / `ChoiceOut` only |
| Choice cross-question | Choice ID from another question could be submitted | Choice must belong to the target question (guest + authenticated grade) |
| Feedback IDOR | Guests could attach feedback to any `quiz_attempt_id` | Linking an attempt now requires auth + ownership |
| Public OpenAPI | `/docs` always on | `ENABLE_API_DOCS` (default **false**); off ⇒ `/docs`, `/redoc`, `/openapi.json` absent (404) |
| CORS footgun | No allowlist | `FRONTEND_URL` explicit origins; `*` rejected; credentials only with allowlist |
| Oversized payloads | No body cap | `MAX_REQUEST_BODY_BYTES` (default 64 KiB) → **413** |
| Missing headers | Incomplete browser hardening | API: CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`; SPA meta aligned (KaTeX/GA preserved) |

---

## Endpoints audited

| Endpoint | Result |
|----------|--------|
| `GET /quiz/guest/questions` | Safe fetch schema; sets guest cookie |
| `POST /quiz/guest/grade` | Session required; post-submit feedback only |
| `GET /quiz/questions` | Auth required; `QuestionOut` only |
| `POST /quiz/answer` | Ownership + choice↔question check |
| `GET /quiz/attempt/{id}/results` | Owner only |
| `GET /progress` | Auth + current user only |
| `GET /weakness-map` | Auth + current user only |
| `GET/POST /daily-practice*` | Auth + current user only |
| `POST /feedback` | Attempt link requires owner; guests cannot bind attempts |
| `POST /question-reports` | Length-limited; rate-limited |
| `/admin/*`, `/feedback/admin` | `require_admin` |
| `/docs`, `/redoc` | Gated by `ENABLE_API_DOCS` |

**Before submission (fetch):** never returns `is_correct`, `correct_choice_id`, `expected_answer`, `explanation`, `common_mistake`, or `answer`.  

**After grading:** returns intended product feedback (`is_correct`, choice/answer, explanation, common mistake, progress).

---

## Configuration (env)

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENABLE_API_DOCS` | `false` | Enable Swagger/ReDoc locally |
| `FRONTEND_URL` | localhost Vite ports if empty | Comma-separated CORS origins (never `*`) |
| `MAX_REQUEST_BODY_BYTES` | `65536` | JSON body size cap |
| `GUEST_QUIZ_SIGNING_SECRET` | derived fallback | HMAC for guest quiz cookies |

Local `.env.example` sets `ENABLE_API_DOCS=true` and sample `FRONTEND_URL` for development.

**Production:** `ENABLE_API_DOCS=false`, `FRONTEND_URL=https://your-domain`, `AUTH_COOKIE_SECURE=true`, set `GUEST_QUIZ_SIGNING_SECRET`.

---

## Request validation

| Surface | Limit |
|---------|--------|
| Feedback `message` | max 2000 |
| Question report `comment` | max 2000 |
| Answer / guest `response_text` | max 2000 |
| Quiz `count` | 1–50 |
| JSON body | `MAX_REQUEST_BODY_BYTES` → 413 |

---

## Guest quiz binding (no UX change)

1. `GET /guest/questions` issues HttpOnly cookie `albertaprep_guest_quiz` (HMAC payload of question IDs + expiry).  
2. Frontend already sends `credentials: 'include'` — no UI/API call-shape change.  
3. `POST /guest/grade` requires cookie and `question_id ∈ issued set`.  

---

## Security headers

**API middleware:** `Content-Security-Policy` (API-safe `default-src 'none'`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`.

**SPA (`index.html`):** CSP allowing self + GA + `'unsafe-inline'` styles for KaTeX/Tailwind; Permissions-Policy; nosniff; referrer meta. KaTeX and GA remain functional.

---

## Tests added

`backend/tests/test_api_security.py` (20 cases), including:

- Guest fetch has no answer fields  
- Authenticated fetch has no answer fields  
- Guest grade without cookie → 401  
- Guest grade after fetch → intended feedback keys only  
- Guest cannot grade foreign question ID → 403  
- Docs flag behavior / factory 404 when disabled  
- CORS allowlist / unknown origin / wildcard rejection  
- Feedback/report length, quiz count max, oversized body 413  
- Cross-user attempt results & feedback IDOR  
- Guest cannot link feedback to attempt  
- Progress / weakness / daily practice require auth  
- Admin unauthorized / student denied  
- Security headers present  

---

## Verification

```
backend:  python -m pytest tests -q   → 70 passed
frontend: npm run build               → OK
smoke:    guest bind, orphan grade 401, headers, admin/progress 401/403 → OK
```

---

## Remaining risks

| Risk | Notes |
|------|--------|
| Post-grade explanations still scrapable | Bound to issued IDs + rate limits; motivated scrapers can still complete quizzes |
| Multi-worker guest cookies | Require shared `GUEST_QUIZ_SIGNING_SECRET` |
| In-process rate limits | Pair with CDN/nginx for multi-instance |
| CSP `'unsafe-inline'` styles | Needed for KaTeX/Tailwind; prefer nonce at CDN long-term |
| Same-origin proxy | CORS less critical when SPA and API share origin; still required for split hosts |
| Admin email in old docs | Still a doc hygiene item from prior audit |

---

## Files changed

**Backend:** `main.py`, `core/config.py`, `routes/quiz.py`, `routes/feedback.py`, `routes/answers.py`, `schemas/{quiz,guest,answer}.py`, `services/guest_quiz_session.py` (new), `.env.example`, `tests/test_api_security.py` (new)

**Frontend:** `index.html` (headers only; no UX)

**Docs:** this report  

*End of report.*

