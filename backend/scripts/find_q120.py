import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "albertaprep.db")
rows = c.execute(
    "SELECT id, LENGTH(explanation), explanation FROM questions WHERE question_text LIKE '%Progesterone rises%'"
).fetchall()
print(rows)
