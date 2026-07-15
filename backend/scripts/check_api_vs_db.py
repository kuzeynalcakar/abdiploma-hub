import json
import random
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.session import SessionLocal
from app.models import Question

BASE = "http://127.0.0.1:8000/api/v1"
email = f"chk.{random.randint(1, 999999)}@e.com"
token = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + "/auth/register",
            data=json.dumps({"name": "c", "email": email, "password": "testpass123"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    ).read()
)["access_token"]
h = {"Authorization": f"Bearer {token}"}
bio = next(
    c
    for c in json.loads(
        urllib.request.urlopen(urllib.request.Request(BASE + "/courses", headers=h)).read()
    )["courses"]
    if c["code"] == "BIO30"
)
quiz = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            BASE + f"/quiz/questions?course_id={bio['id']}&topic_id=42&count=3",
            headers=h,
        )
    ).read()
)
db = SessionLocal()
for q in quiz["questions"]:
    api_id = q["id"]
    db_q = db.get(Question, api_id)
    print("API id", api_id, "exists in DB", bool(db_q))
    print("  API text:", q["question_text"][:60])
    if db_q:
        print("  DB text:", db_q.question_text[:60])
    else:
        # search by stem
        match = (
            db.query(Question)
            .filter(Question.question_text == q["question_text"])
            .first()
        )
        print("  DB match by text:", match.id if match else "NONE")
    print("  choices:", [(c["id"], c["label"][:30]) for c in q.get("choices", [])])
db.close()
