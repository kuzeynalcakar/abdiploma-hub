"""Second audit: review WR questions, revert auto-gradable items to MC/NR."""
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.database.question_validator import validate_question

HERE = Path(__file__).parent
BANK = HERE / "biology30_questions_final.json"
POOL = HERE / "biology30_questions_pool.json"

NUMBERED = re.compile(r"\((\d+)\)\s*([^()]+?)(?=\s*\(\d+\)|\s*\.|\s*Record|\s*Write|$)")


def parse_items(text: str) -> dict[int, str]:
    items = {}
    for m in NUMBERED.finditer(text):
        items[int(m.group(1))] = m.group(2).strip().rstrip(".,;")
    return items


def decode_order(code: str, items: dict[int, str]) -> list[str]:
    return [items[int(d)] for d in str(code) if d.isdigit() and int(d) in items]


def find_pool_match(q: dict, pool: list) -> dict | None:
    key = q["question_text"][:50]
    for p in pool:
        pt = p["question_text"]
        if pt[:50] == key or pt in q["question_text"] or q["question_text"][:35] in pt:
            return p
        # match by outcome + skill
        if (
            p.get("outcome_code") == q.get("outcome_code")
            and p.get("skill_tested") == q.get("skill_tested")
            and abs(len(pt) - len(q["question_text"])) < 80
        ):
            return p
    return None


items = json.loads(BANK.read_text(encoding="utf-8"))
pool = json.loads(POOL.read_text(encoding="utf-8"))

wr_idx = [i for i, q in enumerate(items) if q["question_type"] == "Written Response"]
print(f"WR count: {len(wr_idx)}\n")

for i in wr_idx:
    q = items[i]
    text = q["question_text"]
    ans = q["answer"]
    word_count = len(ans.split())
    
    flags = []
    if re.search(r"\b(order|place the following|sequence)\b", text, re.I):
        flags.append("SEQUENCE")
    if word_count <= 3 and not re.search(r"explain|describe|compare|discuss|evaluate|justify", text, re.I):
        flags.append("SHORT_ANSWER")
    if re.match(r"^\d{3,4}$", str(ans).strip()):
        flags.append("NUMERIC_CODE")
    if "State the resting" in text or "state both values" in text.lower():
        flags.append("STEM_RECALL")
    if re.search(r"\b(explain|describe|compare|discuss|evaluate|justify|predict)\b", text, re.I):
        flags.append("GENUINE_WR")
    
    print(f"[{i}] {flags}")
    print(f"  Q: {text[:90]}...")
    print(f"  A: {ans[:70]}")
    print()
