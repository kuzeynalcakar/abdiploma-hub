"""Verify sequence NR answers and genetics probabilities."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
items = json.loads((Path(__file__).parent / "biology30_questions_final.json").read_text(encoding="utf-8"))

NUMBERED = re.compile(r"\((\d+)\)\s*([^()]+?)(?=\s*\(\d+\)|\s*\.|\s*Record|$)")

def decode(q):
    items_map = {int(m.group(1)): m.group(2).strip().rstrip(".,;") for m in NUMBERED.finditer(q["question_text"])}
    code = str(q["answer"])
    order = [items_map[int(d)] for d in code if d.isdigit() and int(d) in items_map]
    return items_map, code, order

print("=== SEQUENCE NR ===")
for i, q in enumerate(items):
    if q["question_type"] != "Numerical Response":
        continue
    if not re.search(r"\b(order|place the following)\b", q["question_text"], re.I):
        continue
    m, code, order = decode(q)
    print(f"\n[{i}] ans={code} ({len(code)} digits, {len(m)} items)")
    print(" Q:", q["question_text"][:110])
    for j, step in enumerate(order, 1):
        print(f"  {j}. {step}")

print("\n=== DOMINANT PHENOTYPE NR (should be 0.75 for Aa×Aa, Pp×Pp) ===")
for i, q in enumerate(items):
    t = q["question_text"]
    if "dominant phenotype" in t.lower() and q["question_type"] == "Numerical Response":
        print(f"[{i}] ans={q['answer']} | {t[:90]}")

print("\n=== GENETICS MC probability ===")
for i, q in enumerate(items):
    if q["question_type"] != "Multiple Choice":
        continue
    if re.search(r"probability|fraction|percent|0\.\d|punnett|offspring", q["question_text"], re.I):
        correct = [c["text"] for c in q["choices"] if c["is_correct"]]
        print(f"[{i}] key={correct[0] if correct else '?'} | {q['question_text'][:85]}")
