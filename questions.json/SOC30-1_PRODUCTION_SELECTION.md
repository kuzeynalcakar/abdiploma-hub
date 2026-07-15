# SOC30-1 Production Selection Summary

**Outputs**
- `soc30-1_questions_final.json` (300)
- `course_questions_final.json` (alias copy)

**Selector:** `soc30_1_clean_bank.py`  
**Source pool:** `soc30-1_questions_pool.json` (364 QA-validated)

## Type mix (adjusted)

| Type | Count | Share |
|------|------:|------:|
| Multiple Choice | 277 | 92.3% |
| Numerical Response | 23 | 7.7% |

Requested 60% MC / 40% NR is **not feasible**: Alberta SS diploma Part B is MC-only, and the validated pool contains only **23** objectively auto-gradable NR items. Selection retains **all** valid NR and fills with MC.

## Topic mix (diploma-adjusted to pool)

Diploma Part B midpoints imply ~40 / 115 / 115 / 30 across RI1–RI4 (RI2 split Origins+Resistance). Pool caps Viability at 92 and Origins at 51.

| Topic | n | Rationale |
|-------|--:|-----------|
| Ideology and Identity | 48 | RI1 (diploma light strip, slightly raised) |
| Origins of Liberalism | 50 | RI2a (near pool max) |
| Resistance to Liberalism | 70 | RI2b |
| The Viability of Contemporary Liberalism | 92 | RI3 (full pool — diploma wanted ~115) |
| Citizenship and Ideology | 40 | RI4 |

## Other optimization results

- **Difficulty:** Easy 105 / Medium 115 / Hard 80 (pool Medium max 116; house 105/120/75 adjusted)
- **Cognitive:** Understanding & Analysis 175 / Evaluation & Synthesis 125 (diploma ranges each 24–38/60; pool is UA-heavier)
- **Outcomes:** 32 distinct PoS codes covered
- **Templates / skills:** 300 unique each (max repeat 1)
