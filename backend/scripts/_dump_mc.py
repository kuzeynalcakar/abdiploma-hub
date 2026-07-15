import json, sys
from pathlib import Path
BANK = Path(__file__).resolve().parents[2] / "questions.json" / "science10_questions_final.json"
d = json.loads(BANK.read_text(encoding="utf-8"))
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else len(d)
mc = [(i, q) for i, q in enumerate(d) if q["question_type"] == "Multiple Choice"]
mc = [x for x in mc if lo <= x[0] < hi]
for i, q in mc:
    corr = [c["text"] for c in q["choices"] if c["is_correct"]]
    dis = [c["text"] for c in q["choices"] if not c["is_correct"]]
    print(f'{i}| {q["topic"][:6]} | {q["question_text"]}')
    print(f'    A={corr}')
    print(f'    D={dis}')
