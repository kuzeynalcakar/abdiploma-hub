# Social Studies 30-1 Production Readiness Report

**Date (UTC):** 2026-07-15
**Status:** READY
**Database:** `backend/albertaprep.db`

---

## Import Summary

| Item | Result |
|------|--------|
| Source JSON | `soc30-1_questions_final.json` |
| Initial import | **300 new questions** (SOC30-1 was 0 → 300) |
| Duplicate-import recheck | **0 new rows** (all 300 stems skipped) |
| SOC30-1 total after import | **300** |
| Pre-import backup (initial) | `backend/backups/albertaprep_pre_soc30_1_import_20260715_012456.db` |
| Pre-recheck backup | `backend/backups/albertaprep_pre_soc30_1_import_20260715_012609.db` |

---

## Data Preservation

| Asset | Before | After | Preserved |
|-------|--------|-------|-----------|
| BIO30 questions | 300 | 300 | Yes |
| MATH30-1 questions | 293 | 293 | Yes |
| MATH20-1 questions | 300 | 300 | Yes |
| MATH30-2 questions | 300 | 300 | Yes |
| CHEM30 questions | 300 | 300 | Yes |
| PHYS30 questions | 300 | 300 | Yes |
| SCI10 questions | 300 | 300 | Yes |
| SCI30 questions | 300 | 300 | Yes |
| Users | 117 | 117 | Yes |
| User answers | 452 | 452 | Yes |
| Question history | 289 | 289 | Yes |
| Quiz attempts | 141 | 141 | Yes |
| Topic performance | 87 | 87 | Yes |

**Production IDs preserved:** True

---

## Course & Topic Counts

### SOC30-1 total: 300 (target 300)

| Topic | Count | Target |
|-------|-------|--------|
| Ideology and Identity | 48 | 48 |
| Origins of Liberalism | 50 | 50 |
| Resistance to Liberalism | 70 | 70 |
| The Viability of Contemporary Liberalism | 92 | 92 |
| Citizenship and Ideology | 40 | 40 |

### By question type

| Type | Count | Target |
|------|-------|--------|
| Multiple Choice | 277 | 277 |
| Numerical Response | 23 | 23 |

---

## API Verification

| Endpoint | Result |
|----------|--------|
| `GET /courses` (dashboard counts) | SOC30-1 listed, count=300; courses_with_questions=9 |
| `GET /courses/{id}/topics` | 5 topics |
| `GET /quiz/available-count` | 300 available |
| `GET /quiz/questions?count=10` | 10 returned |
| `GET /progress` | 0 courses, streak=True |
| `GET /daily-practice` | 10 configured |
| `POST /daily-practice/start` | 10 returned |
| `GET /weakness-map` | 5 topics |
| `POST /quiz/guest/grade` (MC) | True |
| `POST /quiz/guest/grade` (NR) | True |

---

## Artifacts

| File | Purpose |
|------|---------|
| `questions.json/soc30-1_questions_final.json` | Production question bank |
| `questions.json/course_questions_final.json` | Alias copy |
| `questions.json/SOC30-1_PRODUCTION_VALIDATION.md` | Pre-import JSON validation |
| `questions.json/soc30-1_production_readiness_report.json` | Machine-readable import report |
| `questions.json/SOC30-1_PRODUCTION_READINESS_REPORT.md` | This report |
| `backend/scripts/import_soc30_1_production.py` | Import + verify script |

