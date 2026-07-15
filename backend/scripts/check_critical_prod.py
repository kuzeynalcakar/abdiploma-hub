import json
import sqlite3
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

stems = [
    "Order light pathway",
    "auditory pathway structures in the order",
    "insulin response to high blood glucose",
    "Order implantation events",
    "Pp × Pp show the dominant phenotype",
    "Aa × Aa show the dominant phenotype",
]

items = {i["question_text"]: i for i in json.loads(JSON_PATH.read_text(encoding="utf-8")) if i.get("course_code") == "BIO30"}
conn = sqlite3.connect(DB)
for s in stems:
    db_row = conn.execute(
        """
        SELECT q.id, q.answer, q.explanation, q.question_text
        FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30' AND q.question_text LIKE ?
        """,
        (f"%{s[:30]}%",),
    ).fetchone()
    json_row = next((v for k, v in items.items() if s[:20].lower() in k.lower()), None)
    print("---", s)
    if db_row:
        print(" DB", db_row[0], db_row[1], (db_row[2] or "")[:60])
        print("    text match JSON:", db_row[3] in items)
    if json_row:
        print(" JSON answer", json_row.get("answer"), "expl", (json_row.get("explanation") or "")[:60])
conn.close()
