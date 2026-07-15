import json
import sqlite3
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

items = [i for i in json.loads(JSON_PATH.read_text(encoding="utf-8")) if i.get("course_code") == "BIO30"]
conn = sqlite3.connect(DB)
db_rows = conn.execute(
    """
    SELECT q.id, q.question_text, q.question_type, q.answer, q.explanation, q.common_mistake
    FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
    WHERE c.code='BIO30'
    """
).fetchall()
json_texts = {i["question_text"] for i in items}
extra = [r for r in db_rows if r[1] not in json_texts]
missing = [i for i in items if i["question_text"] not in {r[1] for r in db_rows}]

print("=== DB ONLY (8) ===")
for r in extra:
    print(f"\nQ{r[0]} [{r[2]}] ans={r[3]!r}")
    print(f"  {r[1][:120]}")
    print(f"  expl: {(r[4] or '')[:80]}")

print("\n=== JSON ONLY (8) ===")
for m in missing:
    print(f"\n[{m['question_type']}] ans={m.get('answer')!r}")
    print(f"  {m['question_text'][:120]}")
    print(f"  expl: {(m.get('explanation') or '')[:80]}")

conn.close()
