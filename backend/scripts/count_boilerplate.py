import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "albertaprep.db")
boiler = c.execute(
    """
    SELECT COUNT(*) FROM questions q
    JOIN topics t ON q.topic_id=t.id JOIN courses co ON t.course_id=co.id
    WHERE co.code='BIO30' AND q.explanation LIKE 'The correct answer is%'
    """
).fetchone()[0]
short = c.execute(
    """
    SELECT COUNT(*) FROM questions q
    JOIN topics t ON q.topic_id=t.id JOIN courses co ON t.course_id=co.id
    WHERE co.code='BIO30' AND LENGTH(TRIM(COALESCE(q.explanation,''))) < 15
    """
).fetchone()[0]
print("boilerplate", boiler)
print("short", short)
for r in c.execute(
    """
    SELECT q.id, q.explanation FROM questions q
    JOIN topics t ON q.topic_id=t.id JOIN courses co ON t.course_id=co.id
    WHERE co.code='BIO30' AND q.explanation LIKE 'The correct answer is%'
    """
):
    print(r)
