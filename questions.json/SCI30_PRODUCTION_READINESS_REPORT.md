# Science 30 Production Readiness Report

**Date (UTC):** 2026-07-14
**Status:** READY
**Database:** `backend/albertaprep.db`

---

## Import Summary

| Item | Result |
|------|--------|
| Source JSON | `C:\AlbertaPrep\questions.json\science30_questions_final.json` |
| Questions imported | **0** new (total **300**) |
| Pre-import backup | `C:\AlbertaPrep\backend\backups\albertaprep_pre_sci30_import_20260714_051354.db` |

---

## Data Preservation

| Asset | Before | After | Preserved |
|-------|--------|-------|-----------|
| User answers | 451 | 451 | Yes |
| Question history | 288 | 288 | Yes |
| Quiz attempts | 115 | 115 | Yes |
| Topic performance | 86 | 86 | Yes |
| Production IDs preserved | — | — | Yes |
| BIO30 questions | 300 | 300 | Yes |
| MATH30-1 questions | 293 | 293 | Yes |
| CHEM30 questions | 300 | 300 | Yes |
| PHYS30 questions | 300 | 300 | Yes |
| MATH30-2 questions | 300 | 300 | Yes |
| MATH20-1 questions | 300 | 300 | Yes |

---

## Science 30 Course & Topic Counts

**Total:** 300 / 300

| Topic | Count | Target |
|-------|-------|--------|
| Circulatory and Immune Systems | 38 | 38 |
| Genetics and Molecular Biology | 38 | 38 |
| Environmental Chemistry | 75 | 75 |
| Field Theory and Electrical Energy | 46 | 46 |
| Electromagnetic Spectrum | 29 | 29 |
| Energy and the Environment | 74 | 74 |

### Question types

| Type | Count | Target |
|------|-------|--------|
| multiple_choice | 211 | 211 |
| numerical_response | 89 | 89 |

---

## API Verification

| Endpoint | Result |
|----------|--------|
| Server available | True |
| GET /courses (SCI30 listed) | True |
| Course question_count | 300 |
| GET /courses/{id}/topics | 6 topics |
| GET /quiz/available-count | 300 |
| GET /quiz/questions (10) | 10 returned |
| GET /progress | 0 courses |
| GET /daily-practice | 10 questions |
| POST /daily-practice/start | 10 questions |
| GET /weakness-map | 6 topics |
| POST /quiz/guest/grade (MC) | True |
| POST /quiz/guest/grade (NR) | True |

---

## Verdict

**Science 30 is production-ready.** All 300 questions imported, existing user data preserved, duplicate imports blocked, and API surfaces operational for quiz generation, dashboard, daily practice, and weakness mapping.
