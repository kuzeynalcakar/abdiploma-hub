import json
import sqlite3
import difflib
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

items = [i for i in json.loads(JSON_PATH.read_text(encoding="utf-8")) if i.get("course_code") == "BIO30"]
conn = sqlite3.connect(DB)
db_rows = conn.execute(
    """
    SELECT q.id, q.question_text, q.answer, q.explanation
    FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
    WHERE c.code='BIO30'
    """
).fetchall()
db_texts = {r[1]: r for r in db_rows}
json_texts = {i["question_text"] for i in items}

missing = [i for i in items if i["question_text"] not in db_texts]
extra = [r for r in db_rows if r[1] not in json_texts]

print(f"missing json: {len(missing)} extra db: {len(extra)}")
for m in missing:
    close = difflib.get_close_matches(m["question_text"], [r[1] for r in db_rows], n=1, cutoff=0.85)
    print("\nJSON:", repr(m["question_text"][:100]))
    if close:
        db = db_texts[close[0]]
        print("DB :", repr(close[0][:100]))
        print(" id", db[0], "ans", db[2], "expl", (db[3] or "")[:50])
        print(" json ans", m.get("answer"), "json expl", (m.get("explanation") or "")[:50])
        if m["question_text"] != close[0]:
            for i, (a, b) in enumerate(zip(m["question_text"], close[0])):
                if a != b:
                    print(f"  char diff at {i}: JSON {a!r} ({ord(a)}) vs DB {b!r} ({ord(b)})")
                    break
            if len(m["question_text"]) != len(close[0]):
                print(f"  len JSON {len(m['question_text'])} DB {len(close[0])}")

conn.close()
