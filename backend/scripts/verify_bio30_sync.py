import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

CRITICAL = [
    ("Order light pathway", "2413"),
    ("auditory pathway structures in the order", "2143"),
    ("insulin response to high blood glucose", "3124"),
    ("Order implantation events", "2413"),
    ("Pp × Pp show the dominant phenotype", "0.75"),
    ("Aa × Aa show the dominant phenotype", "0.75"),
]

items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
conn = sqlite3.connect(DB)

print("=== SIX CRITICAL QUESTIONS ===")
for frag, expected in CRITICAL:
    row = conn.execute(
        """
        SELECT q.id, q.answer, substr(q.explanation,1,80), q.question_text
        FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30' AND q.question_text LIKE ?
        """,
        (f"%{frag[:25]}%",),
    ).fetchone()
    ok = row and str(row[1]) == expected
    print(f"{'OK' if ok else 'FAIL'} Q{row[0] if row else '?'} expected={expected} got={row[1] if row else None}")
    if row:
        print(f"  expl: {row[2]}")

print("\n=== REMAINING BOILERPLATE ===")
for r in conn.execute(
    """
    SELECT q.id, q.explanation FROM questions q
    JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
    WHERE c.code='BIO30' AND q.explanation LIKE 'The correct answer is%'
    """
):
    print(r)

print("\n=== UNMATCHED JSON ITEMS (8) ===")
db_texts = {
    r[0]
    for r in conn.execute(
        """
        SELECT q.question_text FROM questions q
        JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30'
        """
    )
}
for item in items:
    if item.get("course_code") != "BIO30":
        continue
    if item["question_text"] not in db_texts:
        print("-", item["question_text"][:90])

print("\n=== ORPHANS ===")
for label, sql in [
    ("user_answers", "SELECT COUNT(*) FROM user_answers ua LEFT JOIN questions q ON ua.question_id=q.id WHERE q.id IS NULL"),
    ("answer_choices", "SELECT COUNT(*) FROM answer_choices ac LEFT JOIN questions q ON ac.question_id=q.id WHERE q.id IS NULL"),
    ("question_history", "SELECT COUNT(*) FROM question_history qh LEFT JOIN questions q ON qh.question_id=q.id WHERE q.id IS NULL"),
]:
    print(label, conn.execute(sql).fetchone()[0])

print("\n=== QUIZ ATTEMPTS SAMPLE ===")
for r in conn.execute(
    "SELECT id, user_id, course_id, mode, questions_total, completed_at IS NOT NULL FROM quiz_attempts ORDER BY id DESC LIMIT 5"
):
    print(r)

conn.close()
