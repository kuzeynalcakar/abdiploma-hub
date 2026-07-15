# Math 30-1 Question Bank — Cleaning Report

**Output file:** `math30-1_questions_final.json` (import-ready)
**Pipeline:** `clean_bank.py` (rerunnable; records every drop and correction)

## Summary

| Metric | Count |
| --- | --- |
| Source JSON files read | 14 |
| Files merged | 13 (`gemini-code-1783734897329.json` skipped — raw twin of the already-cleaned 10-question file) |
| Total questions loaded | 252 |
| Questions removed | 9 |
| **Remaining questions** | **243** |

### Final composition

| Type | Count |
| --- | --- |
| Multiple Choice | 151 |
| Numerical Response | 79 |
| Written Response | 13 |

| Difficulty | Count |
| --- | --- |
| Easy | 84 |
| Medium | 99 |
| Hard | 60 |

### Questions by topic

| Topic | Count |
| --- | --- |
| Transformations of Functions | 41 |
| Permutations, Combinations and the Binomial Theorem | 40 |
| Function Operations and Composition | 38 |
| Logarithmic Functions | 21 |
| Trigonometric Functions and Graphs | 21 |
| Trigonometric Identities | 21 |
| Trigonometry and the Unit Circle | 21 |
| Exponential Functions | 20 |
| Polynomial Functions | 20 |

No source file provided Radical Functions or Rational Functions questions.

---

## Removals (9)

### Broken generations — 3

The generator sometimes self-corrected mid-explanation and left the wrong choice marked correct:

| ID | Reason |
| --- | --- |
| 42 | Composition-table question: correct value is −2, but 1 was marked correct; explanation ends with "Wait… let me correct the choices mapping". Corrected duplicate (#43) kept. |
| 58 | Nested composition f(f(f(1))): correct value is 8, but 4 was marked correct. Corrected duplicate (#59) kept. |
| 50 | Composition through intercepts: g(2) is not determined by the given information; explanation admits "let's rewrite this question". No fixed variant existed. |

### Ambiguous multiple choice — 2

Two defensibly correct options; fixed variants that followed were kept instead:

| ID | Reason |
| --- | --- |
| 62 | Inverse ordered pairs: distractor (−3, 0) was also a valid pair of the inverse. |
| 64 | Invariant point on y = x: distractor (0, 0) is also invariant. |

### Near-duplicates — 4

Same skill tested with nearly identical numbers or identical computation:

| ID | Reason |
| --- | --- |
| 77 | Identical inverse of (2x + 1)/(x − 3) — NR version (#244) kept. |
| 90 | 9^(x+1) = 27^(x−1) vs 27^(x−1) = 9^(2x+3): same common-base-3 skill. |
| 129 | Two find-k-via-remainder-theorem questions on near-identical cubics. |
| 249 | "Vowels never adjacent" arrangements: identical math (6 items, 2 forbidden adjacent; 720 − 240 = 480) as #216. |

---

## Mathematical corrections (8 questions)

| ID | Fix |
| --- | --- |
| 28 | Coefficient sum of (2x − 3)(x² + 4): answer −7 → **−5** (explanation's own arithmetic gave −5). |
| 30 | (f − g)(2) = 15 solve for k: answer 2 → **1**. |
| 39 | Quotient-domain written response: answer summary corrected to [−4, −1) ∪ (−1, 4]. |
| 60 | Self-inverse rational function: rewritten to f(x) = (x + 2)/(x − 1) where f(f(x)) = x holds. |
| 82 | Exponential decay MC: distractor −3(4)^x also decreasing; replaced with −3(¼)^x. |
| 114 | log₃(3x) transformed point: distractor (9, 3) also on graph; replaced with (3, 3). |
| 210 | VECTOR arrangements (vowel first, consonant last): answer 96 → **192**. |
| 238 | Constant term of (x³ − 2/x)⁸: answer 1120 → **1792**. |

---

## Curriculum fixes

### Topic names — 142 questions renamed

Mapped to exactly match `backend/app/database/curriculum_seed.py` (MATH30-1):

- "Transformations" / "Inverse Functions" → **Transformations of Functions**
- "Operations on Functions" / "Compositions of Functions" → **Function Operations and Composition**
- "The Unit Circle" → **Trigonometry and the Unit Circle**
- "Trigonometric Functions" → **Trigonometric Functions and Graphs**
- "Trigonometric Equations and Identities" → **Trigonometric Identities**
- "Permutations and Combinations" / "Binomial Theorem" / "The Binomial Theorem" → **Permutations, Combinations and the Binomial Theorem**

### Units

Aligned to the three Alberta Math 30-1 units:

- Relations and Functions
- Trigonometry
- Permutations, Combinations and Binomial Theorem

### Outcome codes — 106 questions corrected

- **24** auto-corrected when the stored code was outside the valid set for its topic
- **82** manually overridden to match the specific skill tested (e.g. stretches → RF3, reflections → RF5, log laws → RF8, factoring → RF11, trig equations → T5, combinations → PC3, binomial theorem → PC4)

20 unique outcome codes appear in the final bank (RF1–RF14, T1–T6, PC1–PC4).

---

## Metadata and format corrections

| Category | Count |
| --- | --- |
| `question_type` fixes | 0 (already canonical) |
| `difficulty` fixes | 0 (already canonical) |
| Missing `common_mistake` fields filled | 5 |
| JSON escape repairs (LaTeX backslashes) | 1 file (`gemini-code-1783800772449.json`) |
| `\begin{tabular}` → KaTeX `\begin{array}` tables | 4 |
| Control-character corruption repairs (`\r`, `\t`, `\f`, `\b`, `\n` eating LaTeX commands) | Applied across all files |

### Structural checks (all 243 pass)

- Every Multiple Choice question: exactly 4 unique choices, exactly 1 correct
- Every Numerical Response question: numeric answer, empty choices
- Every Written Response question: non-empty answer and explanation (rubric), empty choices
- All 14 required JSON fields present on every question

---

## Verification

| Check | Result |
| --- | --- |
| Mathematical review (all 243 questions) | Answers, explanations, distractors, NR values, and WR rubrics verified |
| `python -m app.database.question_validator` | **243 valid, 0 invalid** |
| Dry-run import into fresh database | **243 imported, 0 errors, 0 skipped** |
| Canonical topic names | All 243 match curriculum seed |
| Near-duplicate groups remaining | 0 |

### Import command

From `backend/`:

```
python -m app.database.question_import ../questions.json/math30-1_questions_final.json
```
