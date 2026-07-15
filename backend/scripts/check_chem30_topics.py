import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path(__file__).resolve().parents[1] / "albertaprep.db")
for r in conn.execute(
    """
    SELECT t.id, t.name, COUNT(q.id)
    FROM topics t
    JOIN courses c ON t.course_id = c.id
    LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
    WHERE c.code = 'CHEM30'
    GROUP BY t.id, t.name
    ORDER BY t.name
    """
):
    print(r)
conn.close()
