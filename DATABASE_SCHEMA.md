# ABDiploma Hub — Database Schema

Planning document for the backend data model. No implementation code — entities, fields, relationships, and data flow only.

**Scope:** MVP for the six existing screens (Login, Dashboard, Quiz, Practice, Weakness Map, Options). Nothing is included that the current frontend cannot display.

---

## 1. Entities

### users

**Purpose:** A student account. Owns all attempts and performance data.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `name` | text | Shown on Options profile card |
| `email` | text, unique | Login identifier; shown on Options |
| `password_hash` | text | Stored credential (implementation details out of scope) |
| `created_at` | timestamp | |

**Relationships:**

- Has many `quiz_attempts`
- Has many `topic_performance` rows (one per topic practiced)

---

### courses

**Purpose:** An Alberta course a student can study (e.g. Mathematics 30-1). Top level of the content hierarchy.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `code` | text, unique | e.g. `MATH30-1` |
| `name` | text | e.g. "Mathematics 30-1" — shown in the Quiz course selector |
| `is_active` | boolean | Hide a course without deleting it |

**Relationships:**

- Has many `topics`
- Has many `quiz_attempts` (an attempt is taken within one course)

---

### topics

**Purpose:** A curriculum topic within a course (e.g. Logarithms). The unit for filtering questions and measuring weakness.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `course_id` | FK → courses | |
| `name` | text | e.g. "Logarithms" |
| `sort_order` | integer | Display order in selectors and the Weakness Map |

**Relationships:**

- Belongs to one `course`
- Has many `questions`
- Has many `topic_performance` rows (one per user)

---

### questions

**Purpose:** A single question presented in Quiz or Practice.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `topic_id` | FK → topics | |
| `question_text` | text | |
| `explanation` | text, nullable | Shown as Practice feedback after checking |
| `question_type` | text | `multiple_choice` for MVP; enables other types later |
| `difficulty` | text, nullable | Optional difficulty classification; values may include `easy`, `medium`, `hard` |
| `source` | text | `manual` for MVP; `ai` reserved for generated questions |
| `is_active` | boolean | Retire questions without breaking past attempts |
| `created_at` | timestamp | |

**Relationships:**

- Belongs to one `topic` (course is reachable through the topic)
- Has many `answer_choices` (four for MVP)
- Has many `user_answers`

---

### answer_choices

**Purpose:** One selectable option for a question, including which option is correct.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `question_id` | FK → questions | |
| `choice_text` | text | |
| `is_correct` | boolean | Exactly one `true` per question for MVP |
| `sort_order` | integer | Display order |

**Relationships:**

- Belongs to one `question`
- Referenced by `user_answers` as the selected choice

---

### quiz_attempts

**Purpose:** One quiz or practice session by one student. Groups the individual answers and holds the final score shown on the results card.

> **MVP note:** Authentication is not implemented in MVP, so quiz attempts are currently owned by a temporary demo user. `user_id` must come from the authenticated token once authentication is added.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `user_id` | FK → users | |
| `course_id` | FK → courses | |
| `topic_id` | FK → topics, nullable | Null means "all topics" |
| `mode` | text | `quiz` (scored) or `practice` (instant feedback) |
| `questions_total` | integer | |
| `questions_correct` | integer | Filled in on completion |
| `started_at` | timestamp | |
| `completed_at` | timestamp, nullable | Null while in progress or abandoned |

**Relationships:**

- Belongs to one `user` and one `course` (optionally one `topic`)
- Has many `user_answers`

---

### user_answers

**Purpose:** A single answered question inside an attempt. The raw event record that everything else is calculated from.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `quiz_attempt_id` | FK → quiz_attempts | |
| `question_id` | FK → questions | |
| `answer_choice_id` | FK → answer_choices | The choice the student selected |
| `is_correct` | boolean | Copied at answer time so history survives later edits to choices |
| `answered_at` | timestamp | Powers the Dashboard recent-activity list |

**Relationships:**

- Belongs to one `quiz_attempt`
- References one `question` and one `answer_choice`

---

### topic_performance

**Purpose:** Per-student, per-topic aggregate. Read directly by the Weakness Map and Dashboard so those screens never scan raw answers.

**Fields:**

| Field | Type | Notes |
|-------|------|-------|
| `id` | primary key | |
| `user_id` | FK → users | |
| `topic_id` | FK → topics | Unique together with `user_id` |
| `questions_attempted` | integer | |
| `questions_correct` | integer | |
| `accuracy` | numeric | `questions_correct / questions_attempted` |
| `weakness_level` | text | `strong`, `medium`, or `weak` — matches the frontend indicator states |
| `updated_at` | timestamp | |

**Relationships:**

- Belongs to one `user` and one `topic`
- One row per user–topic pair, updated in place

**Level thresholds (MVP):** accuracy ≥ 75% → `strong`, 50–74% → `medium`, below 50% → `weak`. Store the level rather than recomputing on every read so thresholds can be tuned without a frontend change.

---

### Relationship overview

```
users ──< quiz_attempts ──< user_answers >── questions ──< answer_choices
  │                                              │
  └──< topic_performance >── topics ──────────────┘
                                │
                            courses
```

---

## 2. Data flow

How one answered question moves through the system:

**Step 1 — Student solves a question.**
The frontend submits the selected `answer_choice_id` for a question within the current `quiz_attempt` (in `practice` mode, checking an answer submits immediately; in `quiz` mode, submission happens per question or at the end of the session).

**Step 2 — Answer stored.**
The backend compares the selected choice against `answer_choices.is_correct`, then inserts a `user_answers` row with the result copied into `is_correct`. When the session ends, `quiz_attempts.questions_correct` and `completed_at` are filled in.

**Step 3 — Performance calculated.**
The student's `topic_performance` row for the question's topic is created or updated: increment `questions_attempted`, increment `questions_correct` if right, recompute `accuracy`, and re-derive `weakness_level` from the thresholds. For MVP this happens synchronously in the same request — no queues or background jobs.

**Step 4 — Weakness map updated.**
No extra work is needed: the Weakness Map and Dashboard simply read `topic_performance`, so the next page load reflects the new state. The summary counts (strong topics vs. needing improvement) are computed from the levels at read time.

---

## 3. Future compatibility

Designed-in extension points — none of these require new work now:

**AI-generated questions.**
`questions.source` distinguishes `manual` from `ai` rows. Generated questions use the same `questions` + `answer_choices` shape, so quiz, practice, and analytics work on them unchanged. If review workflow is needed later, a status field can be added to `questions` — no structural change.

**Multiple Alberta courses.**
The `courses → topics → questions` hierarchy already supports any number of courses (Math 30-2, Physics 30, etc.). Adding a course is a data insert, not a schema change. Per-course progress views filter `topic_performance` through `topics.course_id`.

**Different question types.**
`question_type` marks each question. New types (numeric response, true/false) keep the `questions` row and vary the answer side: true/false uses two `answer_choices` rows; numeric response would add a nullable expected-answer field or a small companion table when the type is actually built. `user_answers` stays the single record of "student answered question X correctly or not," which keeps analytics type-agnostic.

**Practice recommendations.**
"Practice weak areas" is already answerable: the weakest topics for a user are the `topic_performance` rows with the lowest accuracy. Because raw history lives in `user_answers` with timestamps, smarter recommendations later (recency-weighted accuracy, spaced repetition) can be computed from existing data without schema changes.

---

## Out of scope for MVP

- Authentication/session mechanics (only the `users` credential field is noted)
- Question tagging or versioning
- Leaderboards, streaks, or notification storage
- Soft deletes and audit trails beyond `is_active` flags
- Caching layers or background aggregation jobs
