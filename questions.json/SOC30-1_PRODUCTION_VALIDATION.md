# SOC30-1 Production Bank Validation

**Status: CLEAN**
**Items:** 300

Validated files:
- `soc30-1_questions_final.json`
- `course_questions_final.json`

## Checks enforced
- schema
- duplicate texts
- duplicate explanations
- duplicate calculations (NR stem+answer pattern)
- duplicate distractors (max reuse 2)
- duplicate MC answer patterns (max reuse 3; NR numerics exempt)
- invalid outcome codes
- invalid skills
- invalid explanations
- missing metadata
- MC correctness
- NR numeric validity

## Pass history
- Pass 1: `{'duplicate_answer_patterns': 4, 'duplicate_distractors': 109}`
- Pass 2: `{}`

## Final: `{}`

All production validation checks passed.
