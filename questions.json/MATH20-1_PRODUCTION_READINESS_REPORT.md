# Mathematics 20-1 Production Readiness Report

**Date (UTC):** 2026-07-14
**Status:** READY
**Database:** `backend/albertaprep.db`

---

## Import Summary

| Item | Result |
|------|--------|
| Source JSON | `math20-1_questions_final.json` |
| Questions imported | **0** |
| MATH20-1 total after import | **300** |
| Pre-import backup | `C:\AlbertaPrep\backend\backups\albertaprep_pre_math20_1_import_20260714_001413.db` |

---

## Data Preservation

| Asset | Before | After | Preserved |
|-------|--------|-------|-----------|
| BIO30 questions | 300 | 300 | Yes |
| MATH30-1 questions | 293 | 293 | Yes |
| CHEM30 questions | 300 | 300 | Yes |
| PHYS30 questions | 300 | 300 | Yes |
| User answers | 451 | 451 | Yes |
| Question history | 288 | 288 | Yes |
| Quiz attempts | 107 | 107 | Yes |
| Topic performance | 86 | 86 | Yes |

**Production IDs preserved:** True

---

## Course & Topic Counts

### MATH20-1 total: 300 (target 300)

| Topic | Count | Target |
|-------|-------|--------|
| Quadratic Equations | 52 | 52 |
| Rational Expressions and Equations | 45 | 45 |
| Trigonometry | 45 | 45 |
| Quadratic Functions | 36 | 36 |
| Absolute Value and Reciprocal Functions | 36 | 36 |
| Radical Expressions and Equations | 30 | 30 |
| Sequences and Series | 23 | 23 |
| Linear and Quadratic Inequalities | 18 | 18 |
| Systems of Equations | 15 | 15 |

### By question type

| Type | Count | Target |
|------|-------|--------|
| Multiple Choice | 139 | 139 |
| Numerical Response | 161 | 161 |

---

## API Verification

| Endpoint | Result |
|----------|--------|
| `GET /courses` | MATH20-1 listed, count=300 |
| `GET /courses/{id}/topics` | 9 topics |
| `GET /quiz/available-count` | 300 available |
| `GET /quiz/questions?count=10` | 10 returned |
| `GET /progress` | 0 courses, streak=True |
| `GET /daily-practice` | 10 configured |
| `POST /daily-practice/start` | 10 returned |
| `GET /weakness-map` | 9 topics |
| `POST /quiz/guest/grade` (MC) | True |
| `POST /quiz/guest/grade` (NR) | True |

---

## Artifacts

| File | Purpose |
|------|---------|
| `questions.json/math20-1_questions_final.json` | Production question bank |
| `questions.json/course_questions_final.json` | Alias copy |
| `questions.json/math20-1_production_validation_report.json` | Pre-import JSON validation |
| `questions.json/math20-1_production_readiness_report.json` | Machine-readable import report |
| `backend/scripts/import_math20_1_production.py` | Import + verify script |
