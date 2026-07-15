import json, re
from pathlib import Path
BANK = Path(__file__).resolve().parents[2] / "questions.json" / "science10_questions_final.json"
d = json.loads(BANK.read_text(encoding="utf-8"))

def is_boiler(e):
    e = e or ""
    return ("to the values given" in e or "This aligns with Alberta Science 10 outcome" in e
            or "accepted numeric response is" in e or "reflect common misconceptions within" in e
            or "is correct because it matches" in e)

print("### BOILERPLATE / AI-TELL EXPLANATIONS ###")
for i, q in enumerate(d):
    if is_boiler(q.get("explanation")):
        print(f'{i}|{q["question_type"][:2]}|ans={q.get("answer")}|{q["question_text"]}')
        print(f'    OLD: {q["explanation"]}')

print("\n### 'Express as a decimal' with percent wording ###")
for i, q in enumerate(d):
    t = q["question_text"].lower()
    if "percent" in t and "as a decimal" in t:
        print(f'{i}|ans={q.get("answer")}|{q["question_text"]}')

print("\n### Prefixed stems ###")
for i, q in enumerate(d):
    if re.match(r'^(Checkpoint|Review|Practice|Warm-up|Recap)\s*:', q["question_text"]):
        print(f'{i}|{q["question_text"]}')
