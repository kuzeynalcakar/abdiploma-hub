# ABDiploma Hub — API Contract

Planning document for the MVP backend API. No implementation code — endpoints, formats, and error cases only.

**Data model:** see `DATABASE_SCHEMA.md`. Entity and field names below match that document.

---

## Architecture rule: pre-generated questions

Questions are created **before** any student session (by LLM or manual authoring) and stored in the question database. The API only ever **reads** existing questions.

```
LLM / manual generation (beforehand)
        |
        v
Question database
        |
        v
Backend API serves existing questions
```

- No AI API calls happen while a student uses the app.
- No question is generated, modified, or regenerated during a quiz or practice session.
- Correct answers live only in the database (`answer_choices.is_correct`); they are never sent to the client before an answer is submitted.

---

## Conventions

- Base path: `/api/v1` (omitted from the endpoint titles below for readability).
- All request and response bodies are JSON.
- The student is identified by an authentication token on every request (mechanism out of scope for this document). Requests without a valid token receive `401`.
- **MVP note:** Authentication is not implemented in MVP. Quiz attempts currently use a temporary demo user created by the backend. This must be replaced by a token-derived `user_id` when authentication is added.
- Error responses share one format:

```json
{
  "error": {
    "code": "not_found",
    "message": "Course not found."
  }
}
```

- Common status codes: `200` success, `400` invalid input, `401` not authenticated, `403` accessing another user's data, `404` resource not found.

---

## Courses

### GET /courses

**Purpose:** Return available Alberta curriculum courses, used to populate the course selector on the Quiz screen.

**Request:** No parameters. Only `is_active` courses are returned.

**Response `200`:**

```json
{
  "courses": [
    { "id": 1, "code": "MATH30-1", "name": "Mathematics 30-1" },
    { "id": 2, "code": "MATH30-2", "name": "Mathematics 30-2" }
  ]
}
```

An empty list is a valid response (`"courses": []`).

**Errors:**

| Status | Case |
|--------|------|
| `401` | Missing or invalid token |

---

## Topics

### GET /courses/{course_id}/topics

**Purpose:** Return curriculum topics belonging to one course, used for the topic selector and Weakness Map grouping.

**Request:**

| Parameter | In | Type | Notes |
|-----------|----|------|-------|
| `course_id` | path | integer | Required |

**Response `200`:** Topics ordered by `sort_order`.

```json
{
  "course_id": 1,
  "topics": [
    { "id": 10, "name": "Logarithms" },
    { "id": 11, "name": "Quadratic Functions" },
    { "id": 12, "name": "Trigonometry" }
  ]
}
```

**Errors:**

| Status | Case |
|--------|------|
| `401` | Missing or invalid token |
| `404` | `course_id` does not exist or is inactive |

---

## Quiz

### GET /quiz/questions

**Purpose:** Retrieve existing questions from the database for a quiz or practice session. Questions were stored before the session; this endpoint only selects and returns them.

**Request (query parameters):**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `course_id` | integer | yes | Course to draw questions from |
| `topic_id` | integer | no | Restrict to one topic; omit for all topics in the course |
| `count` | integer | no | Number of questions, default `10`, maximum `50` |
| `mode` | string | no | `quiz` (default) or `practice`; recorded on the attempt |

**Filtering logic:**

1. Start from all `questions` where `is_active` is true.
2. Keep questions whose topic belongs to `course_id` (via `topics.course_id`).
3. If `topic_id` is given, keep only that topic's questions.
4. Randomly select up to `count` questions from the filtered set.
5. If fewer questions exist than requested, return all available ones — this is not an error; the response simply contains fewer items.

**Response `200`:** Also opens a new `quiz_attempts` row and returns its id so answers can be grouped. `is_correct` is **never** included on choices.

```json
{
  "quiz_attempt_id": 501,
  "course_id": 1,
  "topic_id": 10,
  "mode": "quiz",
  "questions": [
    {
      "id": 1001,
      "topic_id": 10,
      "question_type": "multiple_choice",
      "question_text": "What is the value of log2(8)?",
      "choices": [
        { "id": 4001, "label": "2" },
        { "id": 4002, "label": "3" },
        { "id": 4003, "label": "4" },
        { "id": 4004, "label": "8" }
      ]
    }
  ]
}
```

**Errors:**

| Status | Case |
|--------|------|
| `400` | `count` not a positive integer or above maximum; unknown `mode` |
| `400` | `topic_id` does not belong to `course_id` |
| `401` | Missing or invalid token |
| `404` | `course_id` or `topic_id` does not exist |
| `404` | No active questions match the filters (empty pool, code `no_questions_available`) — frontend shows its EmptyState |

---

### POST /quiz/answer

**Purpose:** Store the student's answer to an existing question. The backend checks correctness against stored answer data, saves the attempt record, and updates topic performance — the full data flow from `DATABASE_SCHEMA.md` in one request.

**Request body:**

```json
{
  "quiz_attempt_id": 501,
  "question_id": 1001,
  "answer_choice_id": 4002
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `quiz_attempt_id` | integer | yes | From the `GET /quiz/questions` response |
| `question_id` | integer | yes | Must be part of this attempt's question set |
| `answer_choice_id` | integer | yes | Must belong to `question_id` |

**Backend behavior (in order):**

1. Look up the stored `answer_choices` row and compare against the choice with `is_correct = true`. No recalculation, no AI — a database read.
2. Insert a `user_answers` row with the result copied into `is_correct`.
3. Create or update the student's `topic_performance` row for the question's topic: increment counts, recompute `accuracy`, re-derive `weakness_level`.
4. If this was the attempt's final unanswered question, fill in `quiz_attempts.questions_correct` and `completed_at`.

**Response `200`:** Includes the correct choice and explanation so Practice can show instant feedback; in `quiz` mode the frontend may ignore these until the results screen.

```json
{
  "is_correct": true,
  "correct_choice_id": 4002,
  "explanation": "log2(8) = 3 because 2^3 = 8.",
  "attempt_progress": {
    "answered": 4,
    "total": 10,
    "completed": false
  }
}
```

**Errors:**

| Status | Case |
|--------|------|
| `400` | `answer_choice_id` does not belong to `question_id`, or `question_id` is not in this attempt |
| `400` | Question already answered in this attempt (code `already_answered`) |
| `401` | Missing or invalid token |
| `403` | `quiz_attempt_id` belongs to a different user |
| `404` | Attempt, question, or choice does not exist |

---

## Weakness Map

### GET /users/{id}/weakness-map

**Purpose:** Return the student's existing topic performance data. Reads the `topic_performance` aggregate directly — raw `user_answers` are **not** scanned or recalculated on request.

**Request:**

| Parameter | In | Type | Notes |
|-----------|----|------|-------|
| `id` | path | integer | Must match the authenticated user |
| `course_id` | query | integer, optional | Restrict to one course's topics |

**Response `200`:** Topics the student has attempted, grouped by course, plus summary counts derived from the stored levels. Topics never attempted have no `topic_performance` row and are omitted.

```json
{
  "user_id": 42,
  "summary": {
    "strong_topics": 1,
    "topics_needing_improvement": 2
  },
  "courses": [
    {
      "course_id": 1,
      "course_name": "Mathematics 30-1",
      "topics": [
        {
          "topic_id": 10,
          "name": "Logarithms",
          "questions_attempted": 20,
          "questions_correct": 5,
          "accuracy": 0.25,
          "weakness_level": "weak"
        },
        {
          "topic_id": 12,
          "name": "Trigonometry",
          "questions_attempted": 12,
          "questions_correct": 10,
          "accuracy": 0.83,
          "weakness_level": "strong"
        }
      ]
    }
  ]
}
```

If the student has no performance data yet, `courses` is an empty list — the frontend shows its EmptyState ("Complete quizzes or practice…").

**Errors:**

| Status | Case |
|--------|------|
| `401` | Missing or invalid token |
| `403` | `id` is not the authenticated user |
| `404` | User or `course_id` does not exist |

---

## Practice

### GET /practice/recommendations

**Purpose:** Return recommended topics (with available question counts) using existing weakness data. A ranking over stored `topic_performance` rows — no AI generation, no new questions.

**Request (query parameters):**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `course_id` | integer | no | Restrict recommendations to one course |
| `limit` | integer | no | Maximum topics returned, default `3` |

**Recommendation logic (MVP):**

1. Read the authenticated user's `topic_performance` rows (filtered by course if given).
2. Order by `weakness_level` (`weak` first, then `medium`), then by ascending `accuracy`.
3. Return the top `limit` topics that still have active questions available.

**Response `200`:**

```json
{
  "recommendations": [
    {
      "topic_id": 10,
      "topic_name": "Logarithms",
      "course_id": 1,
      "weakness_level": "weak",
      "accuracy": 0.25,
      "available_questions": 34
    }
  ]
}
```

The frontend starts a session for a recommended topic by calling `GET /quiz/questions?course_id=1&topic_id=10&mode=practice`. An empty `recommendations` list is valid (new student or nothing weak) — the frontend may fall back to letting the student pick any topic.

**Errors:**

| Status | Case |
|--------|------|
| `400` | `limit` not a positive integer |
| `401` | Missing or invalid token |
| `404` | `course_id` does not exist |

---

## Out of scope for MVP

- AI generation endpoints (generation happens offline, before sessions)
- Admin panel or content management endpoints
- Payments, notifications, chat, leaderboards
- Pagination (question and topic counts are small at MVP scale)
- Rate limiting, caching headers, and versioning beyond the `/api/v1` prefix
