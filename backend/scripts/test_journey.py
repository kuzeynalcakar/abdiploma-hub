"""End-to-end journey test for core learning loop."""

import json
import random
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"


def req(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        BASE + path, data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
            return json.loads(content) if content else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        print("FAIL", method, path, exc.code, detail)
        raise


def answer_body(attempt_id, question):
    body = {
        "quiz_attempt_id": attempt_id,
        "question_id": question["id"],
    }
    if question.get("question_type") == "multiple_choice" and question.get("choices"):
        body["answer_choice_id"] = question["choices"][0]["id"]
    elif question.get("question_type") == "numerical_response":
        body["response_text"] = "0"
    else:
        body["response_text"] = "wrong answer"
    return body


def main() -> int:
    req("GET", "/courses")

    email = f"journey.{random.randint(10000, 99999)}@example.com"
    password = "testpass123"
    reg = req(
        "POST",
        "/auth/register",
        body={"name": "Journey Test", "email": email, "password": password},
    )
    token = reg["token"]
    print("1. Registered:", email)

    courses = req("GET", "/courses")["courses"]
    course = next(c for c in courses if c["code"] == "MATH30-1")
    course_id = course["id"]
    print("2. Course:", course["name"], course["question_count"], "questions")

    quiz = req(
        "GET",
        f"/quiz/questions?course_id={course_id}&count=10",
        token=token,
    )
    attempt_id = quiz["quiz_attempt_id"]
    print("3. Quiz started:", len(quiz["questions"]), "questions")

    wrong = 0
    for question in quiz["questions"]:
        result = req(
            "POST",
            "/quiz/answer",
            token=token,
            body=answer_body(attempt_id, question),
        )
        if not result.get("is_correct"):
            wrong += 1
    print("4. Quiz completed, wrong:", wrong)

    weakness_map = req("GET", f"/weakness-map?course_id={course_id}", token=token)
    print("5. Weakness map:", len(weakness_map["needs_practice"]), "need practice")
    if weakness_map["needs_practice"]:
        weakest = weakness_map["needs_practice"][0]
        print("   Weakest:", weakest["topic_name"], weakest["accuracy"], "%")
        print("   Why:", weakest["why"][:100])

    daily_status = req("GET", f"/daily-practice?course_id={course_id}", token=token)
    print(
        "6. Daily practice:",
        daily_status["total_questions"],
        "questions, targets:",
        [area["topic_name"] for area in daily_status.get("target_areas", [])],
    )

    start = req(
        "POST",
        f"/daily-practice/start?course_id={course_id}",
        token=token,
    )
    print("7. Daily practice started:", start["total_questions"], "questions")

    for question in start["questions"]:
        req(
            "POST",
            "/quiz/answer",
            token=token,
            body=answer_body(start["quiz_attempt_id"], question),
        )

    results = req(
        "GET",
        f"/quiz/attempt/{start['quiz_attempt_id']}/results",
        token=token,
    )
    print(
        "8. Daily practice results:",
        results["correct"],
        "correct of",
        results["total_questions"],
    )

    progress = req("GET", "/progress", token=token)
    print(
        "9. Streak:",
        progress.get("practice_streak"),
        "last:",
        progress.get("last_practice_date"),
    )

    print("JOURNEY OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("JOURNEY FAILED:", exc)
        raise SystemExit(1)
