"""Post-correction verification."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(__file__).parent.joinpath("biology30_questions_final.json").read_text(encoding="utf-8"))

stems = {}
dups = []
for i, q in enumerate(d):
    k = re.sub(r"\s+", " ", q["question_text"].lower().strip())
    if k in stems:
        dups.append((stems[k], i))
    stems[k] = i
print("Duplicate stems:", len(dups), dups)

for idx, exp in [(218, "0.75"), (222, "0.75"), (46, "2413"), (49, "2143"), (108, "2143"), (110, "2413")]:
    got = str(d[idx]["answer"])
    print(f"Q{idx}: {'OK' if got == exp else 'FAIL'} ({got})")

bp = [i for i, q in enumerate(d) if q.get("explanation", "").startswith("The correct answer is")]
print("Boilerplate remaining:", bp)

q = d[295]
print("Q295 metadata:", q["unit"], "|", q["topic"], "|", q["outcome_code"])
print("Q50 answer:", d[50]["answer"])
print("Distribution:", dict(Counter(x["question_type"] for x in d)))
