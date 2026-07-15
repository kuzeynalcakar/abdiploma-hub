import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
c = sqlite3.connect(DB)

stats = {}
for code in ("BIO30", "MATH30-1"):
    row = c.execute(
        """
        SELECT COUNT(*),
          SUM(CASE WHEN question_type='multiple_choice' THEN 1 ELSE 0 END),
          SUM(CASE WHEN question_type='numerical_response' THEN 1 ELSE 0 END),
          SUM(CASE WHEN question_type='written_response' THEN 1 ELSE 0 END)
        FROM questions q JOIN topics t ON q.topic_id=t.id JOIN courses c2 ON t.course_id=c2.id
        WHERE c2.code=? AND q.is_active=1
        """,
        (code,),
    ).fetchone()
    stats[code] = row

print("COURSE_STATS", stats)
print("users", c.execute("select count(*) from users").fetchone()[0])
print("attempts", c.execute("select count(*) from quiz_attempts").fetchone()[0])
print("answers", c.execute("select count(*) from user_answers").fetchone()[0])
print("history", c.execute("select count(*) from question_history").fetchone()[0])
courses = c.execute("select code, name, (select count(*) from questions q join topics t on q.topic_id=t.id where t.course_id=courses.id and q.is_active=1) from courses where is_active=1").fetchall()
print("courses", courses)
