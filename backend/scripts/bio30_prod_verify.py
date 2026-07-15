"""Verify production albertaprep.db used by live API."""
import json
import random
import sqlite3
import urllib.request
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
BASE = "http://127.0.0.1:8000/api/v1"
issues = []

c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row


def add(sev, msg):
    issues.append((sev, msg))
    print(f"[{sev}] {msg}")


# MC keys in production DB
rows = c.execute(
    """
    SELECT q.id, q.answer, q.question_text, t.name as topic
    FROM questions q
    JOIN topics t ON q.topic_id = t.id
    JOIN courses co ON t.course_id = co.id
    WHERE co.code = 'BIO30' AND q.is_active = 1 AND q.question_type = 'multiple_choice'
    """
).fetchall()
for r in rows:
    choices = c.execute(
        "SELECT choice_text, is_correct FROM answer_choices WHERE question_id = ?",
        (r["id"],),
    ).fetchall()
    correct = [x for x in choices if x["is_correct"]]
    if len(correct) != 1:
        add("CRITICAL", f"Q{r['id']} MC: {len(correct)} correct flags")
    elif r["answer"] and correct[0]["choice_text"] != r["answer"]:
        add("CRITICAL", f"Q{r['id']} MC key mismatch: {correct[0]['choice_text'][:40]} vs {r['answer'][:40]}")

# NR answers present
nr_missing = c.execute(
    """
    SELECT q.id FROM questions q
    JOIN topics t ON q.topic_id = t.id
    JOIN courses co ON t.course_id = co.id
    WHERE co.code='BIO30' AND q.is_active=1 AND q.question_type='numerical_response'
    AND (q.answer IS NULL OR trim(q.answer)='')
    """
).fetchall()
for r in nr_missing:
    add("CRITICAL", f"Q{r['id']} NR missing answer")

# Corrected stems
checks = [
    ("Order light pathway", "2413"),
    ("auditory pathway", "2143"),
    ("Order implantation events", "2413"),
    ("insulin response to high blood glucose", "3124"),
    ("Pp × Pp show the dominant phenotype", "0.75"),
    ("Aa × Aa show the dominant phenotype", "0.75"),
]
for stem, expected in checks:
    row = c.execute(
        """
        SELECT q.id, q.answer FROM questions q
        JOIN topics t ON q.topic_id=t.id JOIN courses co ON t.course_id=co.id
        WHERE co.code='BIO30' AND q.question_text LIKE ?
        """,
        (f"%{stem}%",),
    ).fetchone()
    if not row:
        add("HIGH", f"Missing stem: {stem}")
    elif str(row["answer"]) != expected:
        add("CRITICAL", f"Q{row['id']} expected {expected}, got {row['answer']} ({stem[:30]})")

# Q120 explanation
q120 = c.execute("SELECT id, explanation FROM questions WHERE id=120").fetchone()
if q120 and len((q120["explanation"] or "").strip()) < 15:
    add("MEDIUM", f"Q120 short explanation: {q120['explanation']!r}")

# API integration with production IDs
email = f"prod.{random.randint(1,999999)}@e.com"
token = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + "/auth/register",
            data=json.dumps({"name": "p", "email": email, "password": "testpass123"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    ).read()
)["access_token"]
h = {"Authorization": f"Bearer {token}"}
bio = next(
    x
    for x in json.loads(
        urllib.request.urlopen(urllib.request.Request(BASE + "/courses", headers=h)).read()
    )["courses"]
    if x["code"] == "BIO30"
)
quiz = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + f"/quiz/questions?course_id={bio['id']}&count=10",
            headers=h,
        )
    ).read()
)
aid = quiz["quiz_attempt_id"]
for q in quiz["questions"]:
    body = {"quiz_attempt_id": aid, "question_id": q["id"]}
    row = c.execute("SELECT question_type, answer FROM questions WHERE id=?", (q["id"],)).fetchone()
    if not row:
        add("CRITICAL", f"API returned missing question id {q['id']}")
        continue
    if row["question_type"] == "multiple_choice":
        ch = c.execute(
            "SELECT id FROM answer_choices WHERE question_id=? AND is_correct=1",
            (q["id"],),
        ).fetchone()
        body["answer_choice_id"] = ch["id"] if ch else None
    elif row["question_type"] == "numerical_response":
        body["response_text"] = str(row["answer"])
    else:
        body["response_text"] = "Student response."
    try:
        res = json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    BASE + "/quiz/answer",
                    data=json.dumps(body).encode(),
                    headers={**h, "Content-Type": "application/json"},
                    method="POST",
                )
            ).read()
        )
    except urllib.error.HTTPError as e:
        add("CRITICAL", f"Answer failed Q{q['id']}: {e.read()}")
        continue
    if row["question_type"] in ("multiple_choice", "numerical_response") and not res.get("is_correct"):
        add("CRITICAL", f"Correct answer marked wrong Q{q['id']}")
    if row["question_type"] == "written_response" and not res.get("requires_review"):
        add("HIGH", f"WR Q{q['id']} missing requires_review")

results = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(BASE + f"/quiz/attempt/{aid}/results", headers=h)
    ).read()
)
if results["completed"] is not True or results["total_questions"] != 10:
    add("HIGH", f"Results incomplete: {results}")
if not results.get("topics"):
    add("HIGH", "Results missing topic breakdown")

wm = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(BASE + f"/weakness-map?course_id={bio['id']}", headers=h)
    ).read()
)
if not wm.get("has_attempted_topics"):
    add("HIGH", "Weakness map not updated")

dp = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(BASE + f"/daily-practice?course_id={bio['id']}", headers=h)
    ).read()
)
if dp.get("total_questions", 0) <= 0:
    add("HIGH", "Daily practice empty after quiz")

print("\nSUMMARY", len(issues), "issues")
crit = [i for i in issues if i[0] == "CRITICAL"]
print("Critical:", len(crit))
