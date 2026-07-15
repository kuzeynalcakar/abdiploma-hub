"""Export SCI10 bank samples for manual student review."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
d = json.loads((ROOT / "questions.json" / "science10_questions_final.json").read_text(encoding="utf-8"))

nrs = [(i, q) for i, q in enumerate(d) if q["question_type"] == "Numerical Response"]
out = []
for i, q in nrs:
    stem = q["question_text"].replace("\n", " ")[:180]
    out.append(f"{i}|{q['topic'][:24]}|{q.get('answer')}|{stem}")
(ROOT / "questions.json" / "_sci10_nr_review.txt").write_text("\n".join(out), encoding="utf-8")
print("NR", len(nrs))

mcs = [(i, q) for i, q in enumerate(d) if q["question_type"] == "Multiple Choice"]
lines = []
for n, (i, q) in enumerate(mcs):
    if n % 3:
        continue
    correct = next(c["text"] for c in q["choices"] if c.get("is_correct"))
    wrong = [c["text"] for c in q["choices"] if not c.get("is_correct")]
    lines.append(f"--- {i} ---")
    lines.append(q["question_text"].replace("\n", " "))
    lines.append("CORRECT: " + correct)
    lines.append("WRONG: " + " | ".join(wrong))
    lines.append("EXPL: " + (q.get("explanation") or "")[:220])
(ROOT / "questions.json" / "_sci10_mc_sample.txt").write_text("\n".join(lines), encoding="utf-8")
print("MC sample blocks", sum(1 for L in lines if L.startswith("---")))

conn = sqlite3.connect(ROOT / "backend" / "albertaprep.db")
n = conn.execute(
    """
    SELECT COUNT(*) FROM user_answers ua
    JOIN questions q ON ua.question_id = q.id
    JOIN topics t ON q.topic_id = t.id
    JOIN courses c ON t.course_id = c.id
    WHERE c.code = 'SCI10'
    """
).fetchone()[0]
print("sci10 user answers", n)
