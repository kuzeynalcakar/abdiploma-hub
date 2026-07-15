"""Clean and merge the Math 30-1 question bank.

Stage 1 (this script):
- Load every gemini-code-*.json file plus math30-1_questions_cleaned.json
  (the raw twin of the cleaned file is skipped).
- Repair invalid JSON escapes (single backslashes in LaTeX).
- Normalize question_type, difficulty, unit, topic and outcome codes to
  the platform's curriculum seed.
- Check required fields.
- Remove exact duplicates and flag near-duplicates (same digit-stripped
  template in the same topic).
- Write merged_normalized.json and review_sheet.txt for manual
  mathematical verification.
"""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

# The cleaned file supersedes this raw original (same 10 questions).
SKIP_FILES = {"gemini-code-1783734897329.json"}

REQUIRED_FIELDS = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]

# Canonical topics from backend/app/database/curriculum_seed.py (MATH30-1)
TOPIC_MAP = {
    "Transformations": "Transformations of Functions",
    "Transformations of Functions": "Transformations of Functions",
    "Inverse Functions": "Transformations of Functions",
    "Operations on Functions": "Function Operations and Composition",
    "Compositions of Functions": "Function Operations and Composition",
    "Function Operations and Composition": "Function Operations and Composition",
    "The Unit Circle": "Trigonometry and the Unit Circle",
    "Trigonometry and the Unit Circle": "Trigonometry and the Unit Circle",
    "Trigonometric Functions": "Trigonometric Functions and Graphs",
    "Trigonometric Functions and Graphs": "Trigonometric Functions and Graphs",
    "Trigonometric Identities": "Trigonometric Identities",
    "Trigonometric Equations": "Trigonometric Identities",
    "Trigonometric Equations and Identities": "Trigonometric Identities",
    "Binomial Theorem": (
        "Permutations, Combinations and the Binomial Theorem"
    ),
    "Exponential Functions": "Exponential Functions",
    "Logarithmic Functions": "Logarithmic Functions",
    "Polynomial Functions": "Polynomial Functions",
    "Radical Functions": "Radical Functions",
    "Rational Functions": "Rational Functions",
    "Permutations and Combinations": (
        "Permutations, Combinations and the Binomial Theorem"
    ),
    "Permutations, Combinations and the Binomial Theorem": (
        "Permutations, Combinations and the Binomial Theorem"
    ),
    "The Binomial Theorem": (
        "Permutations, Combinations and the Binomial Theorem"
    ),
}

TOPIC_UNIT = {
    "Transformations of Functions": "Relations and Functions",
    "Function Operations and Composition": "Relations and Functions",
    "Exponential Functions": "Relations and Functions",
    "Logarithmic Functions": "Relations and Functions",
    "Polynomial Functions": "Relations and Functions",
    "Radical Functions": "Relations and Functions",
    "Rational Functions": "Relations and Functions",
    "Trigonometry and the Unit Circle": "Trigonometry",
    "Trigonometric Functions and Graphs": "Trigonometry",
    "Trigonometric Identities": "Trigonometry",
    "Permutations, Combinations and the Binomial Theorem": (
        "Permutations, Combinations and Binomial Theorem"
    ),
}

# Valid Alberta Math 30-1 outcome codes per canonical topic.
TOPIC_OUTCOMES = {
    "Transformations of Functions": {"RF2", "RF3", "RF4", "RF5", "RF6"},
    "Function Operations and Composition": {"RF1"},
    "Exponential Functions": {"RF9", "RF10"},
    "Logarithmic Functions": {"RF7", "RF8", "RF9", "RF10"},
    "Polynomial Functions": {"RF11", "RF12"},
    "Radical Functions": {"RF13"},
    "Rational Functions": {"RF14"},
    "Trigonometry and the Unit Circle": {"T1", "T2", "T3", "T5"},
    "Trigonometric Functions and Graphs": {"T4", "T5"},
    "Trigonometric Identities": {"T5", "T6"},
    "Permutations, Combinations and the Binomial Theorem": {
        "PC1", "PC2", "PC3", "PC4"
    },
}

DEFAULT_OUTCOME = {
    "Transformations of Functions": "RF4",
    "Function Operations and Composition": "RF1",
    "Exponential Functions": "RF10",
    "Logarithmic Functions": "RF8",
    "Polynomial Functions": "RF12",
    "Radical Functions": "RF13",
    "Rational Functions": "RF14",
    "Trigonometry and the Unit Circle": "T2",
    "Trigonometric Functions and Graphs": "T4",
    "Trigonometric Identities": "T6",
    "Permutations, Combinations and the Binomial Theorem": "PC2",
}

TYPE_MAP = {
    "multiple choice": "Multiple Choice",
    "multiple_choice": "Multiple Choice",
    "multiplechoice": "Multiple Choice",
    "mc": "Multiple Choice",
    "numerical response": "Numerical Response",
    "numerical_response": "Numerical Response",
    "numeric response": "Numerical Response",
    "nr": "Numerical Response",
    "written response": "Written Response",
    "written_response": "Written Response",
    "wr": "Written Response",
}

DIFF_MAP = {
    "easy": "Easy", "medium": "Medium", "moderate": "Medium",
    "hard": "Hard", "difficult": "Hard", "challenging": "Hard",
}

# A backslash not starting a valid JSON escape begins a raw LaTeX
# command (e.g. \pi); double it so the file parses. Valid escape pairs
# are consumed first so their second character is never re-inspected.
ESCAPE_SCAN = re.compile(r'\\[\\"/bfnrtu]|\\')


def _fix_escape(match: re.Match) -> str:
    token = match.group(0)
    return token if len(token) == 2 else "\\\\"


def load_repaired(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text), False
    except json.JSONDecodeError:
        return json.loads(ESCAPE_SCAN.sub(_fix_escape, text)), True


# LaTeX commands whose leading letter was eaten by a JSON escape when the
# generator wrote single backslashes: "\right" parsed as CR + "ight", etc.
CONTROL_FIXES = [
    ("\r", "ightarrow", "\\rightarrow"),
    ("\r", "ight", "\\right"),
    ("\t", "herefore", "\\therefore"),
    ("\t", "heta", "\\theta"),
    ("\t", "imes", "\\times"),
    ("\t", "riangle", "\\triangle"),
    ("\t", "ext", "\\text"),
    ("\t", "an", "\\tan"),
    ("\t", "o ", "\\to "),
    ("\f", "rac", "\\frac"),
    ("\f", "orall", "\\forall"),
    ("\b", "inom", "\\binom"),
    ("\b", "egin", "\\begin"),
    ("\b", "eta", "\\beta"),
    ("\b", "ig", "\\big"),
    ("\n", "eq", "\\neq"),
    ("\n", "otin", "\\notin"),
    ("\n", "abla", "\\nabla"),
]

CONTROL_CHARS = re.compile(r"[\r\t\f\b\v]|\n(?=eq|otin|abla)")


def repair_control_chars(value: str, found: list[str]) -> str:
    if not isinstance(value, str):
        return value
    for ctrl, suffix, replacement in CONTROL_FIXES:
        value = value.replace(ctrl + suffix, replacement)
    for match in CONTROL_CHARS.finditer(value):
        start = max(0, match.start() - 25)
        found.append(repr(value[start:match.start() + 25]))
    return value


def repair_item_text(item: dict, found: list[str]) -> dict:
    fixed = {}
    for key, value in item.items():
        if isinstance(value, str):
            fixed[key] = repair_control_chars(value, found)
        elif key == "choices" and isinstance(value, list):
            fixed[key] = [
                {
                    **choice,
                    "text": repair_control_chars(
                        choice.get("text", ""), found
                    ),
                }
                for choice in value
            ]
        else:
            fixed[key] = value
    return fixed


def normalize(item: dict, source_file: str, notes: list[str]) -> dict:
    q = dict(item)
    q["_source_file"] = source_file

    for field in REQUIRED_FIELDS:
        if field not in q:
            notes.append(f"MISSING FIELD {field}")

    raw_type = str(q.get("question_type", "")).strip().lower()
    canonical_type = TYPE_MAP.get(raw_type)
    if canonical_type is None:
        notes.append(f"UNKNOWN TYPE {q.get('question_type')!r}")
        canonical_type = "Multiple Choice"
    if q.get("question_type") != canonical_type:
        notes.append(f"type: {q.get('question_type')!r} -> {canonical_type}")
    q["question_type"] = canonical_type

    raw_diff = str(q.get("difficulty", "")).strip().lower()
    canonical_diff = DIFF_MAP.get(raw_diff)
    if canonical_diff is None:
        notes.append(f"UNKNOWN DIFFICULTY {q.get('difficulty')!r}")
        canonical_diff = "Medium"
    if q.get("difficulty") != canonical_diff:
        notes.append(f"difficulty: {q.get('difficulty')!r} -> {canonical_diff}")
    q["difficulty"] = canonical_diff

    raw_topic = str(q.get("topic", "")).strip()
    canonical_topic = TOPIC_MAP.get(raw_topic)
    if canonical_topic is None:
        notes.append(f"UNKNOWN TOPIC {raw_topic!r}")
        canonical_topic = raw_topic
    elif raw_topic != canonical_topic:
        notes.append(f"topic: {raw_topic!r} -> {canonical_topic!r}")
    q["topic"] = canonical_topic

    canonical_unit = TOPIC_UNIT.get(canonical_topic)
    if canonical_unit and q.get("unit") != canonical_unit:
        notes.append(f"unit: {q.get('unit')!r} -> {canonical_unit!r}")
        q["unit"] = canonical_unit

    code = str(q.get("outcome_code", "")).strip().upper().replace(" ", "")
    allowed = TOPIC_OUTCOMES.get(canonical_topic, set())
    if code not in allowed:
        fixed = DEFAULT_OUTCOME.get(canonical_topic, code)
        notes.append(f"outcome: {q.get('outcome_code')!r} -> {fixed!r}")
        q["outcome_code"] = fixed
    else:
        q["outcome_code"] = code

    q["course_code"] = "MATH30-1"
    q.setdefault("source", "ai")

    # Structural choice checks (multiple choice only).
    choices = q.get("choices") or []
    if q["question_type"] == "Multiple Choice":
        if len(choices) != 4:
            notes.append(f"BAD CHOICE COUNT {len(choices)}")
        correct = [c for c in choices if c.get("is_correct")]
        if len(correct) != 1:
            notes.append(f"BAD CORRECT COUNT {len(correct)}")
        texts = [" ".join(str(c.get("text", "")).split()) for c in choices]
        if len(set(texts)) != len(texts):
            notes.append("DUPLICATE CHOICE TEXT")
    else:
        if choices:
            notes.append(f"NON-MC HAS {len(choices)} CHOICES (cleared)")
            q["choices"] = []

    return q


# ---------------------------------------------------------------------------
# Manual review results (ids are stable indices in file-sorted load order).
# ---------------------------------------------------------------------------

# Questions removed after mathematical review.
DROPS = {
    42: "broken generation: wrong choice marked correct, explanation "
        "self-corrects mid-text; corrected duplicate kept as #43",
    50: "unsolvable: g(2) is not determined by the given information; "
        "explanation admits the flaw ('let's rewrite this question')",
    58: "broken generation: f(f(f(1))) = 8 but 4 marked correct; corrected "
        "duplicate kept as #59",
    62: "two valid answers: (-3, 0) is also a pair of the inverse; fixed "
        "variant kept as #63",
    64: "two valid answers: (0, 0) is also invariant on y = x; fixed "
        "variant kept as #65",
    77: "near-duplicate of #244: identical inverse of (2x+1)/(x-3)",
    90: "near-duplicate of #247: same solve-9^a=27^b-by-common-base-3 "
        "skill with nearly identical structure",
    129: "near-duplicate of #250: same find-k-from-remainder-theorem "
         "problem on a cubic with nearly identical numbers",
    249: "near-duplicate of #216: identical 6-item non-adjacent counting "
         "problem (720 - 240 = 480) with a different story",
}

# Mathematical corrections to kept questions.
MATH_FIXES: dict[int, dict] = {
    28: {
        "answer": "-5",
        "explanation": (
            "Find the product function by expanding the expression:\n"
            "$(f \\cdot g)(x) = (2x - 3)(x^2 + 4) = 2x^3 + 8x - 3x^2 - 12$.\n"
            "Arranging in descending powers of $x$: $2x^3 - 3x^2 + 8x - 12$.\n"
            "Extracting the parameters: $a = 2$, $b = -3$, $c = 8$, and "
            "$d = -12$.\n"
            "The sum of these coefficients is $2 + (-3) + 8 + (-12) = -5$.\n"
            "Note: An alternate rapid method is evaluating "
            "$(f \\cdot g)(1) = f(1) \\cdot g(1) = (2(1)-3)(1^2+4) "
            "= (-1)(5) = -5$."
        ),
    },
    30: {
        "answer": "1",
        "explanation": (
            "The expression $(f - g)(2) = f(2) - g(2) = 15$. Evaluate each "
            "function at $x = 2$:\n"
            "$f(2) = 4(2)^2 - k(2) + 2 = 16 - 2k + 2 = 18 - 2k$.\n"
            "$g(2) = 3(2) - 5 = 1$.\n"
            "Set up the equation for the difference:\n"
            "$(18 - 2k) - 1 = 15$\n"
            "$17 - 2k = 15$\n"
            "$-2k = -2 \\Rightarrow k = 1$.\n"
            "Check: with $k = 1$, $f(2) = 16$ and $f(2) - g(2) = 16 - 1 = 15$."
        ),
    },
    39: {
        "answer": (
            "Domain of $f(x)$: $[-4, 4]$; Domain of $g(x)$: $\\mathbb{R}$; "
            "Quotient domain: $[-4, -1) \\cup (-1, 4)$"
        ),
    },
    60: {
        "question_text": (
            "Consider the function $f(x) = \\frac{x + 2}{x - 1}$, where "
            "$x \\neq 1$.\n\n"
            "a) Algebraically determine the explicit equation for the "
            "composite function $f(f(x))$. Simplify completely.\n\n"
            "b) Explain what your result from part a) implies about the "
            "geometric relationship between the graph of $f(x)$ and the "
            "line $y = x$."
        ),
        "answer": (
            "a) $f(f(x)) = x$; b) The graph is symmetric with respect to "
            "the line $y = x$, meaning the function is its own inverse."
        ),
        "explanation": (
            "a) To find $f(f(x))$, substitute the entire expression for "
            "$f(x)$ into its own input variable:\n"
            "$$f(f(x)) = \\frac{\\frac{x + 2}{x - 1} + 2}"
            "{\\frac{x + 2}{x - 1} - 1}$$\n"
            "Multiply the numerator and denominator by the common "
            "denominator $(x - 1)$:\n"
            "$$f(f(x)) = \\frac{(x + 2) + 2(x - 1)}{(x + 2) - (x - 1)} "
            "= \\frac{3x}{3} = x$$\n"
            "So $f(f(x)) = x$ for all $x \\neq 1$.\n\n"
            "b) Since $f(f(x)) = x$, the function is its own inverse "
            "($f^{-1} = f$). Graphically, this means the graph of "
            "$y = f(x)$ is symmetric about the line $y = x$: reflecting "
            "the graph across that line maps it onto itself."
        ),
        "common_mistake": (
            "Students often forget to multiply every term of the complex "
            "fraction by the common denominator $(x - 1)$, which leads to "
            "an incorrectly simplified quotient."
        ),
    },
    114: {
        "explanation": (
            "The change from $y = \\log_3(x)$ to $y = \\log_3(3x)$ is a "
            "horizontal compression by a factor of $\\frac{1}{3}$, mapping "
            "$(x, y) \\rightarrow \\left(\\frac{1}{3}x, y\\right)$. "
            "Applying this to $(9, 2)$ gives $(3, 2)$. Check: "
            "$\\log_3(3 \\cdot 3) = \\log_3(9) = 2$, so the point $(3, 2)$ "
            "lies on the transformed graph."
        ),
        "_choice_fix": {3: "$(3, 3)$"},
    },
    210: {
        "answer": "192",
        "explanation": (
            "The word VECTOR has 6 unique letters (Vowels: E, O; "
            "Consonants: V, C, T, R).\n"
            "- Choices for 1st position (Vowel) = 2\n"
            "- Choices for 5th position (Consonant) = 4\n"
            "- Remaining positions (2nd, 3rd, 4th) must be filled by 3 of "
            "the remaining 4 letters: $_4P_3 = 4 \\times 3 \\times 2 = 24$.\n"
            "Total arrangements = $2 \\times 4 \\times 24 = 192$."
        ),
    },
    238: {
        "answer": "1792",
        "explanation": (
            "The general term is $T_{k+1} = _8C_k (x^3)^{8-k} "
            "(-2x^{-1})^k = _8C_k (-2)^k x^{24-3k-k} "
            "= _8C_k (-2)^k x^{24-4k}$.\n"
            "To find the constant term, set the exponent of $x$ to 0: "
            "$24 - 4k = 0 \\Rightarrow k = 6$.\n"
            "Substitute $k = 6$ back into the term expression:\n"
            "$T_7 = _8C_6 (-2)^6 = 28 \\cdot 64 = 1792$."
        ),
    },
}

# Ambiguous multiple choice: a distractor was also a correct answer.
CHOICE_FIXES = {
    # (D) -3(4)^x is also strictly decreasing; replace with an increasing
    # curve so exactly one choice shows decay.
    82: {3: "$y = -3\\left(\\frac{1}{4}\\right)^x$"},
}

# KaTeX cannot render \begin{tabular} (and it sat outside math delimiters
# anyway, showing raw LaTeX to students). Convert tables to $$\begin{array}$$.
FORMAT_FIXES = {
    21: (
        "Selected values for the functions $f(x)$ and $g(x)$ are shown in "
        "the table below:\n\n"
        "$$\\begin{array}{|c|c|c|}\\hline x & f(x) & g(x) \\\\ \\hline "
        "-1 & 4 & 2 \\\\ 0 & 1 & -3 \\\\ 2 & -5 & 6 \\\\ 5 & 0 & -1 \\\\ "
        "\\hline\\end{array}$$\n\n"
        "Determine the value of $(f - g)(2)$."
    ),
    43: (
        "Selected values for functions $f(x)$ and $g(x)$ are provided in "
        "the table below:\n\n"
        "$$\\begin{array}{|c|c|c|}\\hline x & f(x) & g(x) \\\\ \\hline "
        "-2 & 3 & 1 \\\\ 1 & -2 & 4 \\\\ 3 & 1 & -2 \\\\ 4 & 0 & 3 \\\\ "
        "\\hline\\end{array}$$\n\n"
        "Determine the value of $(f \\circ f)(3)$."
    ),
    68: (
        "A table of values for a function $g(x)$ is shown below:\n\n"
        "$$\\begin{array}{|c|c|}\\hline x & g(x) \\\\ \\hline "
        "-1 & 5 \\\\ 2 & 0 \\\\ 4 & -1 \\\\ 7 & 2 \\\\ "
        "\\hline\\end{array}$$\n\n"
        "Determine the value of $g^{-1}(2)$."
    ),
    96: (
        "An investment grows according to the data table below:\n\n"
        "$$\\begin{array}{|c|c|}\\hline \\text{End of Year } (t) & "
        "\\text{Value } (V) \\\\ \\hline 2 & \\$1210 \\\\ 3 & \\$1331 \\\\ "
        "4 & \\$1464.10 \\\\ \\hline\\end{array}$$\n\n"
        "If the growth is modeled by $V = a(b)^t$, what is the exact "
        "growth factor $b$?"
    ),
}

# Fill the six questions missing the common_mistake field.
COMMON_MISTAKE_FILLS = {
    98: "Students often forget to rewrite $\\frac{1}{4}$ as $2^{-2}$ "
        "before equating exponents, or select the negative root of the "
        "quadratic instead of the required positive one.",
    132: "Students often substitute $x = \\frac{4}{3}$ instead of "
         "$x = -\\frac{4}{3}$ when applying the factor theorem to the "
         "factor $3x + 4$.",
    138: "Students often stop after one synthetic division and conclude "
         "the multiplicity is 1 without testing whether $x = 1$ is also a "
         "root of the quotient.",
    190: "Students often expand with the cosine form "
         "$\\cos(A)\\cos(B) + \\sin(A)\\sin(B)$ by mistake, or forget to "
         "find $\\cos(A)$ and $\\sin(B)$ using Pythagorean triples first.",
    193: "Students often substitute $\\cos(2x) = 1 - 2\\sin^2(x)$, which "
         "mixes sine and cosine terms and makes the equation impossible "
         "to factor directly.",
}

# Alberta 30-1 outcome corrections found during review.
# RF2 translations / RF3 stretches / RF5 reflections / RF6 inverses;
# RF7 log meaning / RF8 log laws / RF9 graphs / RF10 equations;
# RF11 factoring / RF12 polynomial graphs;
# T1 angles / T3 ratios / T4 graphs / T5 equations / T6 identities;
# PC1 counting principle / PC2 permutations / PC3 combinations /
# PC4 binomial theorem.
OUTCOME_OVERRIDES = {
    0: "RF5", 1: "RF5", 2: "RF3", 3: "RF3", 4: "RF5", 5: "RF3",
    6: "RF5", 7: "RF5", 8: "RF3", 9: "RF3", 10: "RF5", 11: "RF5",
    12: "RF5", 13: "RF5", 14: "RF3", 15: "RF5", 16: "RF5", 17: "RF3",
    18: "RF5", 19: "RF5", 243: "RF5",
    102: "RF7", 103: "RF7", 104: "RF9", 105: "RF9", 109: "RF7",
    110: "RF9", 114: "RF9",
    122: "RF12", 123: "RF12", 124: "RF12", 125: "RF11", 126: "RF11",
    129: "RF11", 130: "RF11", 131: "RF11", 132: "RF11", 134: "RF12",
    137: "RF11", 141: "RF11",
    156: "T3",
    166: "T5", 167: "T5", 172: "T5", 173: "T5", 177: "T5", 178: "T5",
    180: "T5",
    182: "T6", 183: "T6", 186: "T6", 187: "T6", 189: "T5", 191: "T6",
    192: "T6", 193: "T5", 195: "T6", 196: "T6", 197: "T5", 199: "T6",
    200: "T5", 201: "T6",
    203: "PC2", 204: "PC3", 205: "PC2", 207: "PC3", 208: "PC2",
    209: "PC2", 210: "PC2", 211: "PC3", 212: "PC2", 213: "PC3",
    214: "PC3", 215: "PC3", 216: "PC2", 217: "PC2", 218: "PC3",
    219: "PC2", 220: "PC3", 221: "PC3", 223: "PC4", 231: "PC4",
}


def apply_review_fixes(merged: list[dict]) -> dict:
    """Apply drops, math fixes, metadata fills and outcome overrides."""
    stats = {"dropped": 0, "math_fixed": 0, "mistake_filled": 0,
             "outcome_overridden": 0}
    for q in merged:
        qid = q["_id"]
        if qid in DROPS:
            q["_drop"] = DROPS[qid]
            stats["dropped"] += 1
            continue
        if qid in MATH_FIXES:
            fix = MATH_FIXES[qid]
            for key, value in fix.items():
                if key == "_choice_fix":
                    for idx, text in value.items():
                        q["choices"][idx]["text"] = text
                else:
                    q[key] = value
            stats["math_fixed"] += 1
        if qid in CHOICE_FIXES:
            for idx, text in CHOICE_FIXES[qid].items():
                q["choices"][idx]["text"] = text
            stats["math_fixed"] += 1
        if qid in FORMAT_FIXES:
            q["question_text"] = FORMAT_FIXES[qid]
            stats.setdefault("format_fixed", 0)
            stats["format_fixed"] += 1
        if qid in COMMON_MISTAKE_FILLS:
            q["common_mistake"] = COMMON_MISTAKE_FILLS[qid]
            stats["mistake_filled"] += 1
        if qid in OUTCOME_OVERRIDES:
            new_code = OUTCOME_OVERRIDES[qid]
            if q["outcome_code"] != new_code:
                q["outcome_code"] = new_code
                stats["outcome_overridden"] += 1
    return stats


FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]


def to_final(q: dict) -> dict:
    out = {field: q[field] for field in FIELD_ORDER if field in q}
    return out


def text_key(q: dict) -> str:
    return " ".join(str(q.get("question_text", "")).split()).casefold()


def template_key(q: dict) -> str:
    text = text_key(q)
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    return f"{q['topic']}|{re.sub(r'[^a-z#]+', '', text)}"


def main() -> None:
    all_items = []
    repaired_files = []
    for path in sorted(HERE.glob("*.json")):
        if path.name in SKIP_FILES or path.name.startswith("math30-1_questions_final"):
            continue
        if path.name == "merged_normalized.json":
            continue
        items, was_repaired = load_repaired(path)
        if was_repaired:
            repaired_files.append(path.name)
        for item in items:
            all_items.append((path.name, item))

    print(f"Loaded {len(all_items)} questions from files")
    if repaired_files:
        print(f"Repaired invalid JSON escapes in: {repaired_files}")

    merged = []
    all_notes = []
    control_leftovers = []
    for index, (fname, item) in enumerate(all_items):
        notes: list[str] = []
        found: list[str] = []
        item = repair_item_text(item, found)
        if found:
            control_leftovers.append((index, found))
        q = normalize(item, fname, notes)
        q["_id"] = index
        merged.append(q)
        if notes:
            all_notes.append((index, fname, notes))

    fix_stats = apply_review_fixes(merged)
    print(f"\nReview fixes applied: {fix_stats}")

    # Exact duplicates (by normalized question text). Reviewed drops are
    # excluded first so the corrected copy of a broken pair survives.
    seen: dict[str, int] = {}
    exact_dupes = []
    for q in merged:
        if "_drop" in q:
            continue
        key = text_key(q)
        if key in seen:
            exact_dupes.append((q["_id"], seen[key]))
            q["_drop"] = f"exact duplicate of #{seen[key]}"
        else:
            seen[key] = q["_id"]

    # Near-duplicates: same digit-stripped template within a topic.
    templates: dict[str, list[int]] = {}
    for q in merged:
        if "_drop" in q:
            continue
        templates.setdefault(template_key(q), []).append(q["_id"])
    near_groups = [ids for ids in templates.values() if len(ids) > 1]

    with open(HERE / "merged_normalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # Compact review sheet for manual math verification.
    with open(HERE / "review_sheet.txt", "w", encoding="utf-8") as f:
        for q in merged:
            if "_drop" in q:
                continue
            f.write(f"### {q['_id']} [{q['topic']} | {q['outcome_code']} | "
                    f"{q['question_type']} | {q['difficulty']}]\n")
            f.write(f"Q: {q.get('question_text','')}\n")
            if q["question_type"] == "Multiple Choice":
                for i, c in enumerate(q.get("choices", [])):
                    mark = "*" if c.get("is_correct") else " "
                    f.write(f"  ({'ABCD'[i]}){mark} {c.get('text','')}\n")
            f.write(f"ANS: {q.get('answer','')}\n")
            f.write(f"EXPL: {q.get('explanation','')}\n\n")

    print(f"\nMetadata notes ({len(all_notes)} questions):")
    counts = Counter()
    for _, _, notes in all_notes:
        for n in notes:
            counts[n.split(':')[0].split(' ')[0]] += 1
    for k, v in counts.most_common():
        print(f"  {k}: {v}")

    print(f"\nUnrepaired control chars: {len(control_leftovers)}")
    for index, found in control_leftovers:
        print(f"  #{index}: {found}")

    print(f"\nExact duplicates removed: {len(exact_dupes)}")
    for dup, orig in exact_dupes:
        print(f"  #{dup} == #{orig}")

    print(f"\nNear-duplicate groups to review: {len(near_groups)}")
    for ids in near_groups:
        print(f"  {ids}")

    structural = [
        (i, f, [n for n in notes if n.isupper() or n.startswith(('MISSING', 'BAD', 'UNKNOWN', 'DUPLICATE', 'NON-MC'))])
        for i, f, notes in all_notes
    ]
    structural = [(i, f, ns) for i, f, ns in structural if ns]
    print(f"\nStructural problems: {len(structural)}")
    for i, f, ns in structural:
        print(f"  #{i} ({f}): {ns}")

    final = [to_final(q) for q in merged if "_drop" not in q]
    with open(HERE / "math30-1_questions_final.json", "w",
              encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"\nFinal question count: {len(final)}")
    type_counts = Counter(q["question_type"] for q in final)
    topic_counts = Counter(q["topic"] for q in final)
    print(f"By type: {dict(type_counts)}")
    print("By topic:")
    for topic, count in sorted(topic_counts.items()):
        print(f"  {topic}: {count}")


if __name__ == "__main__":
    main()
