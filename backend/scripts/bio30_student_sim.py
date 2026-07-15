"""Grade 12 student simulation for Biology 30 — report only, no modifications."""
from __future__ import annotations

import json
import random
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.session import SessionLocal
from app.models import AnswerChoice, Course, Question, Topic
from app.services.answer_grading import grade_answer

BASE = "http://127.0.0.1:8000/api/v1"
ISSUES: list[dict] = []


def issue(severity: str, category: str, detail: str, qid: int | None = None, topic: str = ""):
    ISSUES.append(
        {"severity": severity, "category": category, "detail": detail, "question_id": qid, "topic": topic}
    )


def api(method: str, path: str, token: str | None = None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {"detail": str(e)}


def register() -> str:
    email = f"bio.sim.{random.randint(100000, 999999)}@example.com"
    _, data = api("POST", "/auth/register", body={"name": "Bio Sim Student", "email": email, "password": "testpass123"})
    return data["access_token"]


def verify_mc_keys(db):
    """Check every MC has exactly one correct choice matching answer field."""
    bio = db.query(Course).filter(Course.code == "BIO30").first()
    questions = (
        db.query(Question)
        .join(Topic)
        .filter(Topic.course_id == bio.id, Question.is_active.is_(True), Question.question_type == "multiple_choice")
        .all()
    )
    for q in questions:
        correct = [c for c in q.choices if c.is_correct]
        if len(correct) != 1:
            issue("critical", "MC key", f"Question has {len(correct)} correct choices", q.id, q.topic.name)
            continue
        if q.answer and correct[0].choice_text != q.answer:
            issue(
                "critical",
                "MC key",
                f"answer field '{q.answer[:50]}' != correct choice '{correct[0].choice_text[:50]}'",
                q.id,
                q.topic.name,
            )


def verify_nr_grading(db):
    bio = db.query(Course).filter(Course.code == "BIO30").first()
    questions = (
        db.query(Question)
        .join(Topic)
        .filter(Topic.course_id == bio.id, Question.is_active.is_(True), Question.question_type == "numerical_response")
        .all()
    )
    for q in questions:
        if not q.answer:
            issue("critical", "NR grading", "Missing stored answer", q.id, q.topic.name)
            continue
        result = grade_answer(q, response_text=str(q.answer))
        if not result.is_correct:
            issue(
                "critical",
                "NR grading",
                f"Correct key '{q.answer}' not accepted by grader",
                q.id,
                q.topic.name,
            )
        # sequence codes: 4-digit should parse as float
        if len(str(q.answer)) == 4 and str(q.answer).isdigit():
            wrong = grade_answer(q, response_text="9999")
            if wrong.is_correct:
                issue("high", "NR grading", "Wrong sequence 9999 marked correct", q.id, q.topic.name)


def simulate_quizzes(token: str, course_id: int, topics: list[dict]):
    """Quiz each topic + 2 random mixed quizzes."""
    plans = [(t["id"], t["name"]) for t in topics] + [(None, "All topics")] * 2
    for topic_id, topic_name in plans:
        params = f"course_id={course_id}&count=10"
        if topic_id:
            params += f"&topic_id={topic_id}"
        status, quiz = api("GET", f"/quiz/questions?{params}", token=token)
        if status != 200:
            issue("critical", "Quiz API", f"Failed quiz for {topic_name}: {status} {quiz}", topic=topic_name)
            continue
        if not quiz.get("questions"):
            issue("high", "Quiz API", f"No questions returned for {topic_name}", topic=topic_name)
            continue
        attempt_id = quiz["quiz_attempt_id"]
        type_counts = defaultdict(int)
        for q in quiz["questions"]:
            type_counts[q["question_type"]] += 1
            body = {"quiz_attempt_id": attempt_id, "question_id": q["id"]}
            if q["question_type"] == "multiple_choice":
                if not q.get("choices"):
                    issue("critical", "MC display", "MC question has no choices in API", q["id"], topic_name)
                    continue
                body["answer_choice_id"] = q["choices"][0]["id"]
            elif q["question_type"] == "numerical_response":
                body["response_text"] = "0"
            else:
                body["response_text"] = "Student test response for written item."
            status, result = api("POST", "/quiz/answer", token=token, body=body)
            if status != 200:
                issue(
                    "critical",
                    "Grading API",
                    f"Answer submit failed ({q['question_type']}): {result}",
                    q["id"],
                    topic_name,
                )
                continue
            if q["question_type"] == "written_response":
                if result.get("auto_graded") is not False and result.get("requires_review") is not True:
                    issue(
                        "high",
                        "WR grading",
                        f"WR should require review; got auto_graded={result.get('auto_graded')}",
                        q["id"],
                        topic_name,
                    )
                if not result.get("explanation"):
                    issue("medium", "WR display", "No explanation returned after WR submit", q["id"], topic_name)
            if q["question_type"] == "multiple_choice" and "explanation" not in result:
                issue("medium", "MC feedback", "No explanation in answer response", q["id"], topic_name)
            if q["question_type"] == "numerical_response":
                if result.get("expected_answer") is None and result.get("is_correct") is False:
                    issue("medium", "NR feedback", "Wrong NR answer but no expected_answer shown", q["id"], topic_name)

        # results
        status, results = api("GET", f"/quiz/attempt/{attempt_id}/results", token=token)
        if status != 200:
            issue("critical", "Results", f"Results page API failed for {topic_name}", topic=topic_name)
        elif not results.get("questions"):
            issue("high", "Results", f"Empty results for {topic_name}", topic=topic_name)

    # weakness map
    status, wm = api("GET", f"/weakness-map?course_id={course_id}", token=token)
    if status != 200:
        issue("critical", "Weakness map", f"API failed: {wm}")
    elif "needs_practice" not in wm:
        issue("high", "Weakness map", "Missing needs_practice field")

    # daily practice
    status, dp = api("GET", f"/daily-practice?course_id={course_id}", token=token)
    if status != 200:
        issue("critical", "Daily practice", f"Status API failed: {dp}")
    else:
        if not dp.get("target_areas") and dp.get("total_questions", 0) > 0:
            issue("medium", "Daily practice", "Has questions but no target_areas after quizzes")
    status, start = api("POST", f"/daily-practice/start?course_id={course_id}", token=token)
    if status != 200:
        issue("critical", "Daily practice", f"Start failed: {start}")


def check_content_quality(db):
    """Student-facing content checks on explanations."""
    bio = db.query(Course).filter(Course.code == "BIO30").first()
    questions = (
        db.query(Question)
        .join(Topic)
        .filter(Topic.course_id == bio.id, Question.is_active.is_(True))
        .all()
    )
    absurd = ("always", "never", "200 years", "without exception")
    for q in questions:
        if not q.explanation or len(q.explanation.strip()) < 10:
            issue("medium", "Explanation", "Missing or very short explanation", q.id, q.topic.name)
        if q.explanation and q.explanation.startswith("The correct answer is"):
            issue("medium", "Explanation", "Boilerplate explanation remains", q.id, q.topic.name)
        if q.question_type == "multiple_choice":
            for c in q.choices:
                if not c.is_correct and any(a in c.choice_text.lower() for a in absurd):
                    issue("low", "Distractor", f"Implausible distractor: {c.choice_text[:60]}", q.id, q.topic.name)


def main():
    db = SessionLocal()
    try:
        verify_mc_keys(db)
        verify_nr_grading(db)
        check_content_quality(db)

        _, courses = api("GET", "/courses")
        bio = next(c for c in courses["courses"] if c["code"] == "BIO30")
        if bio["question_count"] != 300:
            issue("critical", "Course", f"BIO30 shows {bio['question_count']} questions, expected 300")

        token = register()
        # get topics from DB for simulation
        course = db.query(Course).filter(Course.code == "BIO30").first()
        topics = db.query(Topic).filter(Topic.course_id == course.id).all()
        topic_list = [{"id": t.id, "name": t.name} for t in topics]
        simulate_quizzes(token, bio["id"], topic_list)
    finally:
        db.close()

    critical = [i for i in ISSUES if i["severity"] == "critical"]
    high = [i for i in ISSUES if i["severity"] == "high"]
    medium = [i for i in ISSUES if i["severity"] == "medium"]
    low = [i for i in ISSUES if i["severity"] == "low"]

    print("=== BIO30 STUDENT SIMULATION REPORT ===")
    print(f"Total issues: {len(ISSUES)}")
    print(f"Critical: {len(critical)} | High: {len(high)} | Medium: {len(medium)} | Low: {len(low)}")
    for sev, items in [("CRITICAL", critical), ("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if not items:
            continue
        print(f"\n--- {sev} ---")
        for i in items[:25]:
            print(f"  [{i['category']}] Q{i['question_id'] or '?'} {i['topic']}: {i['detail'][:120]}")
        if len(items) > 25:
            print(f"  ... +{len(items)-25} more")

    out = Path(__file__).resolve().parents[2] / "questions.json" / "bio30_student_sim_report.json"
    out.write_text(json.dumps(ISSUES, indent=2), encoding="utf-8")
    print(f"\nFull report: {out}")
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
