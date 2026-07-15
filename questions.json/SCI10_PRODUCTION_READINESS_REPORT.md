# Science 10 Production Readiness Report

**Date (UTC):** 2026-07-14
**Status:** READY
**Database:** `backend/albertaprep.db`

---

## Import Summary

| Item | Result |
|------|--------|
| Source JSON | `C:\AlbertaPrep\questions.json\science10_questions_final.json` |
| Questions imported | **0** new (total **300**) |
| Pre-import backup | `C:\AlbertaPrep\backend\backups\albertaprep_pre_sci10_import_20260714_090033.db` |

---

## Data Preservation

| Asset | Before | After | Preserved |
|-------|--------|-------|-----------|
| User answers | 451 | 451 | Yes |
| Question history | 288 | 288 | Yes |
| Quiz attempts | 119 | 119 | Yes |
| Topic performance | 86 | 86 | Yes |
| Production IDs preserved | — | — | Yes |
| BIO30 questions | 300 | 300 | Yes |
| MATH30-1 questions | 293 | 293 | Yes |
| CHEM30 questions | 300 | 300 | Yes |
| PHYS30 questions | 300 | 300 | Yes |
| MATH30-2 questions | 300 | 300 | Yes |
| MATH20-1 questions | 300 | 300 | Yes |
| SCI30 questions | 300 | 300 | Yes |

---

## Science 10 Course & Topic Counts

**Total:** 300 / 300

| Topic | Count | Target |
|-------|-------|--------|
| Energy and Matter in Chemical Change | 90 | 90 |
| Energy Flow in Technological Systems | 85 | 85 |
| Cycling of Matter in Living Systems | 85 | 85 |
| Energy Flow in Global Systems | 40 | 40 |

### Question types

| Type | Count | Target |
|------|-------|--------|
| multiple_choice | 218 | 218 |
| numerical_response | 82 | 82 |

---

## API Verification

| Endpoint | Result |
|----------|--------|
| Server available | True |
| GET /courses (SCI10 listed) | True |
| Course question_count | 300 |
| GET /courses/{id}/topics | 4 topics |
| GET /quiz/available-count | 300 |
| GET /quiz/questions (10) | 10 returned |
| GET /progress | 0 courses |
| GET /daily-practice | 10 questions |
| POST /daily-practice/start | 10 questions |
| GET /weakness-map | 4 topics |
| POST /quiz/guest/grade (MC) | True |
| POST /quiz/guest/grade (NR) | True |

---

## Verdict

**Science 10 is production-ready.** All 300 questions imported, existing user data preserved, duplicate imports blocked, and API surfaces operational for quiz generation, dashboard, daily practice, and weakness mapping.
