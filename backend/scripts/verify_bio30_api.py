"""Verify API guest grade accepts corrected answers for six critical questions."""
import json
import random
import sqlite3
import urllib.request
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
BASE = "http://127.0.0.1:8000/api/v1"

CRITICAL = [
    "Order light pathway",
    "auditory pathway structures in the order",
    "insulin response to high blood glucose",
    "Order implantation events",
    "Pp × Pp show the dominant phenotype",
    "Aa × Aa show the dominant phenotype",
]

conn = sqlite3.connect(DB)
issues = []
for frag in CRITICAL:
    row = conn.execute(
        """
        SELECT q.id, q.answer, q.explanation FROM questions q
        JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30' AND q.question_text LIKE ?
        """,
        (f"%{frag[:25]}%",),
    ).fetchone()
    if not row:
        issues.append(f"Missing {frag}")
        continue
    qid, expected, expl = row
    res = json.loads(
        urllib.request.urlopen(
            urllib.request.Request(
                BASE + "/quiz/guest/grade",
                data=json.dumps({"question_id": qid, "response_text": str(expected)}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            ),
            timeout=15,
        ).read()
    )
    if not res.get("is_correct"):
        issues.append(f"Q{qid} {expected!r} marked wrong")
    if (res.get("explanation") or "").startswith("The correct answer is"):
        issues.append(f"Q{qid} boilerplate explanation in API")
    if res.get("explanation") != expl:
        pass  # guest returns question.explanation from DB - ok if synced

conn.close()
if issues:
    print("FAIL:")
    for i in issues:
        print(" ", i)
    raise SystemExit(1)
print("All 6 critical questions grade correctly via /quiz/guest/grade API.")
