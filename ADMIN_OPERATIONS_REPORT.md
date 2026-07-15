# Admin operations report — ABDiploma Hub

**Date:** 2026-07-14  
**Scope:** Admin reports workflow, feedback management, impact metrics, question quality, admin safety  
**Unchanged:** Quiz logic, grading, authentication architecture, question bank content, student UX

---

## Verdict

Admin tools are improved for day-to-day platform operations: report triage with reason filters + notes + timestamps, feedback unread/date/sentiment views, impact/growth metrics from real DB rows, question quality monitoring, and append-only action logging. Access remains admin-only (`ADMIN_EMAILS` / `X-Admin-Key`).

---

## 1. Question reports workflow

| Capability | Status |
|------------|--------|
| Filter by status (`pending` / `resolved` / `ignored`) | Existing + retained |
| Filter by reason (wrong answer, confusing wording, wrong explanation, other) | **Added** (`reason` query + UI) |
| Sort newest / oldest first | **Focused** in UI (API still supports extras) |
| Resolve / Ignore / Reopen | Existing + retained |
| `status_changed_at` | **Added** (set on every status change) |
| `admin_note` | **Added** (optional; saved with PATCH) |
| Action audit log | **Added** (`admin_action_logs` + structured logger) |

**API:** `GET /api/v1/admin/reports?status=&reason=&sort=&search=`  
**API:** `PATCH /api/v1/admin/reports/{id}` `{ status, admin_note? }`

Additive columns on `question_reports`: `admin_note`, `status_changed_at`.

---

## 2. Student feedback management

| Capability | Status |
|------------|--------|
| Unread / new indicator | **Added** (`admin_reviewed_at` null = unread; “New” badge) |
| Mark reviewed | **Added** `POST /api/v1/admin/feedback/{id}/review` |
| Date filtering | **Added** (`since` / `until`) |
| Sentiment grouping | **Added** (`by_sentiment` counts from stored ratings; no AI) |
| Sentiment filter | **Added** (`rating=positive|negative`) |

Additive column on `quiz_feedback`: `admin_reviewed_at`.  
No AI summaries — word counts and stored messages only.

---

## 3. Impact Overview

Tab renamed to **Impact Overview**. Metrics from real DB aggregates:

- Registered users, quiz attempts, questions answered  
- Courses practiced (distinct `course_id` on attempts)  
- Feedback submitted, reports submitted  
- Existing learning outcome metrics retained  
- **Growth:** `users_last_7_days`, `quizzes_last_7_days`

---

## 4. Question quality monitoring

On the Question Reports tab + `GET /api/v1/admin/question-quality`:

- Unanswered (pending) reports count  
- Questions with multiple reports  
- Most reported questions (count, pending subset, preview, course)

---

## 5. Admin safety

| Control | Implementation |
|---------|----------------|
| Admin-only routes | `require_admin` on all `/admin/*` endpoints |
| SPA gate | `AdminRoute` (`user.is_admin`) |
| Reduced PII | Overview emails → `email_masked`; feedback drops `user_id`; reports expose `has_reporter` only |
| Action logging | `AdminActionLog` + `log_admin_action()` for resolve/ignore/reopen/review |

---

## Verification

```
backend:  python -m pytest tests -q   → 93 passed
frontend: npm run build               → OK
DB:       additive columns applied via init_db
```

---

## Operator notes

1. Ensure `ADMIN_EMAILS` (and optional `ADMIN_API_KEY`) are set in production.  
2. Run `python -m app.database.init_db` (or app startup that calls it) so new columns/tables exist.  
3. Use report admin notes when resolving so content edits remain traceable without changing question bank in this task.  
4. Audit rows live in `admin_action_logs` (no full emails/tokens stored).
