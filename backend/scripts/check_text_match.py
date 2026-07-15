import json
import sqlite3
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
bio = [i for i in items if i.get("course_code") == "BIO30"]
conn = sqlite3.connect(DB)
db_texts = {
    r[0]
    for r in conn.execute(
        """
        SELECT q.question_text FROM questions q
        JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30' AND q.is_active=1
        """
    )
}
conn.close()

json_set = {i["question_text"] for i in bio}
missing_in_db = [i for i in bio if i["question_text"] not in db_texts]
extra_in_db = db_texts - json_set
print("json", len(bio), "db", len(db_texts))
print("missing_in_db", len(missing_in_db))
for m in missing_in_db[:5]:
    print("  JSON only:", m["question_text"][:70])
print("extra_in_db", len(extra_in_db))
for e in list(extra_in_db)[:3]:
    print("  DB only:", e[:70])
