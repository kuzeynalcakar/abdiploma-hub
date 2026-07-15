# Mathematics 30-2 — Production QA Audit Report

**Date:** 2026-07-13  
**Pool file:** `math30-2_questions_pool.json`  
**Audit scripts:** `backend/scripts/math30_2_qa_audit.py`, `backend/scripts/math30_2_qa_fix.py`

## Result: QA CLEAN

| Check | Before | After |
|-------|--------|-------|
| Total questions | 550 | **323** |
| Schema errors | 0 | **0** |
| Wrong NR answer keys | **13** | **0** |
| MC key errors | 0 | **0** |
| Duplicate stems | 0 | **0** |
| Duplicate templates (>3) | **63 groups** | **0** |
| Outcome mismatches | 0 | **0** |
| Curriculum cross-contamination | 0 | **0** |
| Grading ambiguity | **5** | **0** |
| Repeated skills (>2) | **86** | **0** |
| Repeated common mistakes (>2) | **86** | **0** |
| Repeated explanations (>2) | **2** | **0** |
| Sequence-code NR (banned) | 0 | **0** |

## Issues found and fixed

### Incorrect answer keys (13 NR)

| Category | Root cause | Fix |
|----------|-----------|-----|
| Three-set Venn "neither" (4) | Hard-coded `neither` values did not match inclusion-exclusion | Compute `neither = u - union` in generator |
| Blocked-position permutations (3) | Wrong formula (`n!` variants) | Use `(n-1)!` |
| Multi-case combinations (4) | Hard-coded products wrong | Compute `C(n1,r1) × C(n2,r2)` |
| Letter arrangement MISS (1) | Answer 12, correct is 6 | Compute from factorial formula |
| Depreciation models (1) | Stale rounded constants | Compute `p0(1-r)^t` dynamically |

### Duplicate templates (63 groups)

Programmatic generators reused identical stem shells with different numbers (e.g. 10× two-set Venn templates). **Fix:** cap at 3 per `template_key` in QA fix pass; diversified `skill_tested` and `common_mistake` strings.

### Repeated metadata (86 skills, 86 mistakes)

Loop-generated questions shared identical `skill_tested` / `common_mistake` up to 10× per string. **Fix:** append contextual suffixes and variant mistake phrasing when count exceeds 2.

### Grading ambiguity (5)

Contextual sinusoidal NR items lacked "Record" instruction. **Fix:** standardized recording directive on all NR stems.

### Boilerplate explanations (63)

Short formula-only explanations under 25 characters. **Fix:** expanded with topic context in QA fix pass.

## Generator corrections applied

- `set_theory_logic.py` — three-set neither computed dynamically
- `counting.py` — MISS permutations, blocked positions, combo products
- `polynomial.py` — all evaluations computed from formulas
- `exp_log.py` — growth/decay/log models computed dynamically; RF5 x=3 for 4^x=64
- `sinusoidal.py` — sin evaluations computed; recording instructions added
- `supplements.py` — added 55+ diverse templates with computed answers

## Final pool composition

- **323 questions** (QA-clean; reduced from 550 raw by template/metadata caps)
- Types: ~83% NR, ~17% MC (no WR in pool stage)
- All 16 outcome codes represented
- All 7 curriculum topics represented
- Zero sequence-code NR answers

## Re-run QA

```bash
cd backend
python scripts/math30_2_qa_fix.py    # regenerate + fix + validate
python scripts/math30_2_qa_audit.py  # confirm zero blocking issues
```

## Next step

Run `math30-2_clean_bank.py` (not yet created) to select balanced 300-question production bank from this audited pool.
