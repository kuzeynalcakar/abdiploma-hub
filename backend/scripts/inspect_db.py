import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "albertaprep.db"
c = sqlite3.connect(db)
print("db", db)
print("max id", c.execute("select max(id) from questions").fetchone())
print("count bio30", c.execute(
    "select count(*) from questions q join topics t on q.topic_id=t.id "
    "join courses c on t.course_id=c.id where c.code='BIO30'"
).fetchone())
for qid in [36, 46, 330, 340, 594]:
    row = c.execute("select id, substr(question_text,1,55) from questions where id=?", (qid,)).fetchone()
    print(qid, row)
