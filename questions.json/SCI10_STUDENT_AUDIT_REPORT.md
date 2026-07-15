# Science 10 Student Audit Report

**Role:** Alberta secondary student preparing under diploma-exam standards of scrutiny  
**Course:** SCI10 (Science 10 — four units; not a provincial diploma exam course, but audited to diploma-prep quality)  
**Date (UTC):** 2026-07-14  
**Bank:** `questions.json/science10_questions_final.json` (300) → `backend/albertaprep.db`  
**Status:** COMPLETE — production student-trust criteria met

---

## Method

Worked every topic as a student would (Chemistry, Technological Systems, Living Systems, Global Systems):

1. Recomputed NR keys (auto-verifier + hand-check of non-auto items)
2. Solved MC for wrong keys, factual mistakes, grading traps
3. Flagged AI-tell wording, meta leakage, silly distractors, length tells
4. Checked templates/duplicates and curriculum stretch items
5. Auto-fixed confirmed issues; re-synced DB with backups
6. Re-ran audits until automated student findings = **0**

Passes: initial student audit → deep review → confirmed fixes → stem polish → stretch/curriculum pass → NR re-verify → integrity check

---

## Confirmed Issues Found and Fixed

| # | Index | Issue type | Fix |
|---|-------|------------|-----|
| 1 | 243 | Misleading wording / grading ambiguity | Stem said lake “absorbs” energy that math treated as **incoming**; rewrote to “receives … incoming”; key **70** unchanged |
| 2 | 176 | Factual / answer-key error | Claimed protein hormones enter by diffusion; corrected to **surface-receptor signalling** |
| 3 | 173 | Off-curriculum / AI feel | Replaced confocal (CLSM) item with **compound light microscope** |
| 4 | 177 | Curriculum stretch | Replaced HIV/liposome drug stem with **soap/liposome membrane model** |
| 5 | 109, 201, 211, 214, 218, 223, 281 | Weak / silly distractors & length tells | Replaced with plausible Science 10 misconceptions; rebalanced option length |
| 6 | 255, 256, 258, 261, 286 | Climate distractors (stock market, attendance, mantle lava, etc.) | Replaced with realistic wrong ideas |
| 7 | 9, 28, 90, 98, 108, 112 | Meta / AI leakage | Removed outcome-code refs, “Alberta Science 10 emphasizes…”, “item N” skill artifacts |
| 8 | 123 stems | Awkward `_______?` style | Converted to incomplete diploma-style stems |

**Automated NR check:** 72/82 auto-verified OK, **0 mismatches**; remaining 10 hand-verified (mole calcs, microscope mag, plasmolysis %, lake absorption %).

---

## What Was Checked Clean

| Check | Result |
|-------|--------|
| Exact duplicate stems (JSON + DB) | 0 |
| MC answer ↔ correct choice sync | Pass (218/218) |
| NR answer-key recomputation | 0 mismatches |
| Within-course duplicate stems | 0 |
| Placeholder/meta distractors | Cleared |
| AI-tell explanations | Cleared |
| Neutral pH / phenolphthalein / light reactions keys | Correct |
| Topic distribution | 90 / 85 / 85 / 40 |
| Type mix | 218 MC / 82 NR |
| Other courses preserved | BIO30, MATH30-1, CHEM30, PHYS30, MATH30-2, MATH20-1, SCI30 unchanged |
| Non-SCI10 user_answers | 451 preserved |

---

## Residual Non-Blocking Notes

- Science 10 has **no provincial diploma exam**; rigor matches high-quality diploma-prep banks, not diploma blueprint weighting.
- One longstanding **cross-course** stem overlap remains with SCI30 on a simple pH classification idea (SCI10 wording is distinct: “pH of 3 is best classified as”). Not a within-SCI10 duplicate.
- Incomplete stems (no trailing `?`) are intentional Alberta MC style.
- A few Hard Unit C history-of-science items (e.g. Boysen-Jensen) remain; they are curriculum-aligned for Science 10 plant responses.

---

## Database Sync

- Backups created under `backend/backups/albertaprep_pre_sci10_student_resync_*.db`
- SCI10 questions replaced from fixed JSON (no SCI10 user history existed)
- Import idempotency: stem-dedupe still prevents duplicate SCI10 rows on re-import

---

## Final Verdict

**Science 10 is complete for student trust.**

- No confirmed answer-key errors remain  
- No duplicate questions remain within SCI10  
- No grading ambiguity remains on previously flagged items  
- Bank feel is comparable to solid Alberta diploma-prep resources in clarity, distractor quality, and factual care  

Scripts used:  
`sci10_student_audit.py`, `sci10_verify_nr.py`, `sci10_deep_student_review.py`,  
`sci10_student_audit_final_fix.py`, `sci10_student_audit_pass2.py`,  
`sci10_student_audit_pass3.py`, `sci10_student_resync_db.py`
