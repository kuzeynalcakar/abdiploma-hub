"""Deep student simulation: correct answers, feedback fields, topic coverage."""
from __future__ import annotations

import json
import random
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.session import SessionLocal
from app.models import AnswerChoice, Course, Question, Topic

BASE = "http://127.0.0.1:8000/api/v1"
issues: list[str] = []


def api(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def add(msg):
    issues.append(msg)
    print("ISSUE:", msg)


token = api("POST", "/auth/register", body={
    "name": "Bio Deep Sim",
    "email": f"bio.deep.{random.randint(100000,999999)}@example.com",
    "password": "testpass123",
})["token"]

courses = api("GET", "/courses", token=token)
bio = next(c for c in courses["courses"] if c["code"] == "BIO30")
cid = bio["id"]

db = SessionLocal()
topics = db.query(Topic).filter(Topic.course_id == db.query(Course).filter(Course.code == "BIO30").first().id).all()
topic_names = {t.id: t.name for t in topics}

# Per-topic quiz with CORRECT answers
for topic in topics:
    quiz = api("GET", f"/quiz/questions?course_id={cid}&topic_id={topic.id}&count=8", token=token)
    aid = quiz["quiz_attempt_id"]
    for q in quiz["questions"]:
        body = {"quiz_attempt_id": aid, "question_id": q["id"]}
        if q["question_type"] == "multiple_choice":
            correct = (
                db.query(AnswerChoice)
                .filter(AnswerChoice.question_id == q["id"], AnswerChoice.is_correct.is_(True))
                .first()
            )
            if not correct:
                add(f"CRITICAL MC Q{q['id']} ({topic.name}): no correct choice in DB")
                continue
            body["answer_choice_id"] = correct.id
        elif q["question_type"] == "numerical_response":
            db_q = db.query(Question).filter(Question.id == q["id"]).first()
            if not db_q or not db_q.answer:
                add(f"CRITICAL NR Q{q['id']}: missing answer in DB")
                continue
            body["response_text"] = str(db_q.answer)
        else:
            body["response_text"] = "Model student written response."
        result = api("POST", "/quiz/answer", token=token, body=body)
        if q["question_type"] in ("multiple_choice", "numerical_response"):
            if not result.get("is_correct"):
                add(f"CRITICAL Q{q['id']} ({topic.name}): correct answer marked wrong")
            if not result.get("explanation"):
                add(f"MEDIUM Q{q['id']} ({topic.name}): no explanation on correct submit")
        if q["question_type"] == "written_response":
            if not result.get("requires_review"):
                add(f"HIGH Q{q['id']} ({topic.name}): WR missing requires_review")
            if not result.get("expected_answer"):
                add(f"MEDIUM Q{q['id']} ({topic.name}): WR missing model solution")
        if q["question_type"] == "multiple_choice" and not result.get("common_mistake"):
            add(f"LOW Q{q['id']} ({topic.name}): MC missing common_mistake on submit")

    results = api("GET", f"/quiz/attempt/{aid}/results", token=token)
    if results["answered"] != results["total_questions"]:
        add(f"HIGH Results ({topic.name}): answered mismatch")
    if results["score_percent"] < 50 and results["review_required"] == 0:
        add(f"MEDIUM Results ({topic.name}): low score despite correct-key simulation")

# Wrong NR should show expected answer
quiz = api("GET", f"/quiz/questions?course_id={cid}&count=5&difficulty=medium", token=token)
aid = quiz["quiz_attempt_id"]
for q in quiz["questions"]:
    if q["question_type"] != "numerical_response":
        continue
    result = api("POST", "/quiz/answer", token=token, body={
        "quiz_attempt_id": aid,
        "question_id": q["id"],
        "response_text": "99999",
    })
    if result.get("is_correct") is not False:
        add(f"HIGH NR Q{q['id']}: wrong answer not marked incorrect")
    if not result.get("expected_answer"):
        add(f"MEDIUM NR Q{q['id']}: wrong submit missing expected_answer")
    if not result.get("common_mistake"):
        add(f"LOW NR Q{q['id']}: wrong submit missing common_mistake")
    break

wm = api("GET", f"/weakness-map?course_id={cid}", token=token)
if not wm.get("topics"):
    add("HIGH Weakness map: empty topics after quizzes")
elif not wm.get("has_attempted_topics"):
    add("HIGH Weakness map: has_attempted_topics false after quizzes")

dp = api("GET", f"/daily-practice?course_id={cid}", token=token)
if dp.get("total_questions", 0) <= 0:
    add("HIGH Daily practice: no questions recommended after weakness data")
if not dp.get("target_areas"):
    add("MEDIUM Daily practice: no target_areas")
if not dp.get("focus_message"):
    add("LOW Daily practice: missing focus_message")

start = api("POST", f"/daily-practice/start?course_id={cid}", token=token)
if not start.get("questions"):
    add("CRITICAL Daily practice start: no questions returned")

db.close()
print("\n=== DEEP SIM SUMMARY ===")
print(f"Issues found: {len(issues)}")
for i in issues:
    print(" -", i)
if not issues:
    print("All deep checks passed.")
