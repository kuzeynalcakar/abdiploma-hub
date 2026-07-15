import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "albertaprep.db")
bio = c.execute(
    """
    SELECT q.id, q.question_type, LENGTH(TRIM(COALESCE(q.explanation,''))) len, q.question_text
    FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c2 ON t.course_id=c2.id
    WHERE c2.code='BIO30' AND q.is_active=1
    AND (q.explanation IS NULL OR LENGTH(TRIM(q.explanation)) < 10)
    """
).fetchall()
math = c.execute(
    """
    SELECT q.id, q.question_type, q.answer, q.explanation, q.question_text
    FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c2 ON t.course_id=c2.id
    WHERE c2.code='MATH30-1' AND q.is_active=1 AND q.question_type='written_response'
    AND (q.answer IS NULL OR LENGTH(TRIM(q.answer)) < 10
         OR q.explanation IS NULL OR LENGTH(TRIM(q.explanation)) < 20)
    """
).fetchall()
print("BIO30", bio)
print("MATH", math)
