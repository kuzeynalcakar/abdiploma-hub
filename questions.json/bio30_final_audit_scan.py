"""Automated pre-audit checks for Biology 30 question bank."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.database.question_validator import validate_question, is_numerical_answer

sys.stdout.reconfigure(encoding="utf-8")

BANK = Path(__file__).parent / "biology30_questions_final.json"
items = json.loads(BANK.read_text(encoding="utf-8"))

issues = defaultdict(list)

BOILERPLATE = re.compile(r"^The correct answer is ", re.I)
ABSURD = re.compile(
    r"(always|never|all organisms|no organisms|100% of the time|impossible to|"
    r"eliminates all|guarantees|proven to extend human lifespan|200 years)",
    re.I,
)
NUMBERED = re.compile(r"\((\d+)\)\s*([^()]+?)(?=\s*\(\d+\)|\s*\.|\s*Record|$)")


def parse_items(text):
    return {int(m.group(1)): m.group(2).strip().rstrip(".,;") for m in NUMBERED.finditer(text)}


# --- structural ---
for i, q in enumerate(items):
    reasons = validate_question(q, i)
    if reasons:
        issues["validation_fail"].append((i, reasons))

    if not q.get("common_mistake", "").strip():
        issues["missing_common_mistake"].append(i)

    if q["question_type"] == "Written Response":
        if not q["explanation"].lower().startswith("marking guide"):
            issues["wr_no_marking_guide"].append(i)
        if len(q.get("answer", "")) < 80:
            issues["wr_short_model_answer"].append((i, len(q.get("answer", ""))))

    if q["question_type"] == "Numerical Response":
        if BOILERPLATE.match(q.get("explanation", "")):
            issues["nr_boilerplate_explanation"].append(i)
        if not is_numerical_answer(q.get("answer")):
            issues["nr_non_numeric_answer"].append((i, q.get("answer")))
        if "round" not in q["question_text"].lower() and re.search(r"\d+\.\d+", str(q.get("answer"))):
            issues["nr_decimal_no_rounding_instruction"].append(i)

    if q["question_type"] == "Multiple Choice":
        choices = q.get("choices", [])
        texts = [c["text"] for c in choices]
        correct = [c["text"] for c in choices if c.get("is_correct")]
        if len(correct) != 1:
            issues["mc_correct_count"].append((i, len(correct)))
        # absurd distractors
        for c in choices:
            if not c.get("is_correct") and ABSURD.search(c["text"]):
                issues["mc_absurd_distractor"].append((i, c["text"][:80]))
        # duplicate choice text
        if len(set(t.lower().strip() for t in texts)) < len(texts):
            issues["mc_duplicate_choices"].append(i)
        # key not matching any choice
        if correct and q.get("answer") and q["answer"] not in texts:
            issues["mc_answer_key_mismatch"].append((i, q["answer"][:60], correct[0][:60]))

# --- genetics probability MC/NR ---
for i, q in enumerate(items):
    t = q["question_text"].lower()
    if "carrier" in t and ("cc" in t or "×" in t or "x" in t):
        issues["genetics_carrier_cross"].append((i, q["question_type"], q.get("answer"), t[:80]))
    if "pp" in t and "×" in q["question_text"]:
        issues["genetics_pp_cross"].append((i, q["question_type"], q.get("answer")))
    if "aa" in t and "×" in q["question_text"] and "aa" in t:
        issues["genetics_aa_cross"].append((i, q["question_type"], q.get("answer")))

# --- sequence NR decode check ---
for i, q in enumerate(items):
    if q["question_type"] != "Numerical Response":
        continue
    if not re.search(r"\b(order|place the following|sequence)\b", q["question_text"], re.I):
        continue
    items_map = parse_items(q["question_text"])
    code = str(q["answer"]).strip()
    if len(items_map) >= 3 and len(code) != len(items_map):
        issues["sequence_digit_count_mismatch"].append((i, code, len(items_map)))

# --- outcome/topic mismatch heuristics ---
TOPIC_OUTCOME_HINTS = {
    "Nervous and Endocrine Systems": ("A",),
    "Reproduction and Development": ("B",),
    "Cell Division": ("C",),
    "Genetics and Molecular Biology": ("C", "D"),  # some D in genetics topic?
    "Population and Community Dynamics": ("D",),
}
for i, q in enumerate(items):
    topic = q["topic"]
    oc = q.get("outcome_code", "")
    if topic in TOPIC_OUTCOME_HINTS:
        prefixes = TOPIC_OUTCOME_HINTS[topic]
        if oc and not any(oc.startswith(p) for p in prefixes):
            issues["outcome_topic_mismatch"].append((i, topic, oc))

# --- duplicate stems ---
seen = {}
for i, q in enumerate(items):
    key = re.sub(r"\s+", " ", q["question_text"].lower().strip())[:100]
    if key in seen:
        issues["duplicate_stem"].append((seen[key], i, key[:60]))
    seen[key] = i

# --- NR template duplicates ---
nr_templates = Counter()
for i, q in enumerate(items):
    if q["question_type"] == "Numerical Response":
        tmpl = re.sub(r"\$?\d+\.?\d*\$?", "N", q["question_text"][:60])
        nr_templates[tmpl] += 1
        if nr_templates[tmpl] > 3:
            issues["nr_template_repeat"].append((i, tmpl))

print("=== AUTOMATED ISSUE SUMMARY ===")
for k, v in sorted(issues.items(), key=lambda x: -len(x[1])):
    print(f"{k}: {len(v)}")
    for item in v[:8]:
        print(f"  {item}")
    if len(v) > 8:
        print(f"  ... +{len(v)-8} more")
