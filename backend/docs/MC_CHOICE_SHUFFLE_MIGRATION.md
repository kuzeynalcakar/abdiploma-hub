# MC answer-choice shuffle migration report

**Date:** 2026-07-15 (UTC)  
**Script:** `backend/scripts/migrate_shuffle_mc_choice_order.py`  
**Seed:** `20260715`  
**DB backup:** `backend/backups/albertaprep.db.bak-mc-shuffle-20260715_045915`

## Goal

Correct answers were almost always stored in position A because generators never shuffled choices. This migration reorders existing `answer_choices.sort_order` only. Stems, explanations, choice text, `is_correct`, question IDs, history, attempts, and user answers were not modified. No question JSON was regenerated.

## Questions updated

**1693** active multiple-choice questions (all with ≥2 choices).

## Distribution

| Position | Before | After | After share |
|----------|-------:|------:|------------:|
| A | 1483 | 421 | 25.0% |
| B | 68 | 399 | 23.7% |
| C | 80 | 463 | 27.5% |
| D | 62 | 401 | 23.8% |

Target ≈25% per letter — achieved within small variation.

## Integrity verification

| Check | Result |
|-------|--------|
| Exactly one correct answer per MC question | Pass |
| Zero questions with multiple correct answers | Pass (`multi_correct=0`) |
| Zero questions with zero correct answers | Pass (`zero_correct=0`) |
| `production_audit.py` | Pass (0 issues; pre-existing cross-course WARN only) |
| `audit_integrity.py` | Pass (`INTEGRITY OK`) |
| Backend tests (`python -m unittest discover -s tests`) | Pass — 96 tests |
| Frontend build (`npm run build`) | Pass |

## Permanent generator / import fix

1. Shared helpers: `backend/question_tools/mc_choices.py`
   - `shuffle_mc_choices` — shuffle before export; preserves `is_correct` with each choice
   - `assert_mc_position_balanced` — fails if any letter exceeds **35%** of MC items (target 20–30%)
2. All course `mc()` helpers now shuffle before export:
   - `bio30`, `chem30`, `phys30`, `sci10`, `sci30`, `math20_1`, `math30_2`, `soc30`
   - Plus `generate_radical_rational.py` (MATH30-1 supplemental)
3. Export / import gates call `assert_mc_position_balanced`:
   - `generate_*.py` course pool exporters
   - `app.database.question_import` (blocks biased banks on import)
   - Related production QA writers (`math20_1_qa_fix`, `math30_2_production_validate`, `soc30_questions/qa_validate_production`)
4. Unit coverage: `backend/tests/test_mc_choice_order.py`

## What was not changed

- Question text / stems
- Explanations / common mistakes
- Choice text
- Question IDs and relational history
- Attempts / user_answers
- Source JSON bank files (not regenerated)

## Rollback

Restore the stamped SQLite backup:

```text
backend/backups/albertaprep.db.bak-mc-shuffle-20260715_045915
```
over `backend/albertaprep.db` if needed.
