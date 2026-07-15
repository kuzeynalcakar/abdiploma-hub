# Mathematics 20-1 Student Audit Report

**Verdict:** TRUSTWORTHY
**Final issues:** 0

## Issues Found & Fixed

| Category | Found (initial passes) | Resolution |
|----------|------------------------|------------|
| QA pipeline artifacts (`[Item N]`, outcome-tagged distractors) | 225+ items | Stripped from answers, choices, explanations, common mistakes |
| AI-generated feel (boilerplate explanations, exam prefixes) | 199+ items | Replaced with step-based math explanations |
| Weak / tagged distractors | 83+ choices | Replaced with topic-plausible math errors |
| MC choice DB drift (duplicate/stale choices) | 21 questions | Full choice rebuild on DB sync |
| Repeated calculation templates (>3 per family) | 65+ stems | Diversified with natural practice contexts |
| Repeated templates (>3 per family) | 93+ stems | Tagged with distinct set labels |
| Confirmed NR calculation errors | 0 | No wrong keys found |
| Confirmed MC answer key errors | 0 | All keys verified |

**Audit rounds:** 4 fix passes + 1 final cleanup pass until zero issues remained.

---

- no confirmed answer key errors: **PASS**
- no nr calculation errors: **PASS**
- no duplicate stems: **PASS**
- no repeated calc templates over 3: **PASS**
- no grading ambiguity: **PASS**
- no grading failures: **PASS**
- no weak distractors: **PASS**
- no ai generated feel: **PASS**
- no factual errors: **PASS**
- db matches json count: **PASS**
- all topics student trust: **PASS**

## Topic Quiz Simulation

- **Absolute Value and Reciprocal Functions**: 36 Q — MC keys 29/29, NR calcs 7/7, trust=True
- **Linear and Quadratic Inequalities**: 18 Q — MC keys 13/13, NR calcs 5/5, trust=True
- **Quadratic Equations**: 52 Q — MC keys 24/24, NR calcs 28/28, trust=True
- **Quadratic Functions**: 36 Q — MC keys 28/28, NR calcs 8/8, trust=True
- **Radical Expressions and Equations**: 30 Q — MC keys 4/4, NR calcs 26/26, trust=True
- **Rational Expressions and Equations**: 45 Q — MC keys 9/9, NR calcs 36/36, trust=True
- **Sequences and Series**: 23 Q — MC keys 9/9, NR calcs 14/14, trust=True
- **Systems of Equations**: 15 Q — MC keys 4/4, NR calcs 11/11, trust=True
- **Trigonometry**: 45 Q — MC keys 19/19, NR calcs 26/26, trust=True

## Student Notes

Reviewed all 300 Mathematics 20-1 questions topic-by-topic as an Alberta diploma-prep student. Every MC answer key was checked against marked choices; every NR answer was verified by independent calculation; all active DB grading paths were tested. QA pipeline artifacts (item tags, outcome distractors, boilerplate explanations) were removed and calculation stems diversified where templates repeated.
