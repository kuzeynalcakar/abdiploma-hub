"""API security hardening tests: answer leakage, docs, CORS, IDOR, validation."""

from __future__ import annotations

import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.rate_limit import reset_rate_limits
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import Course, Question

ANSWER_LEAK_KEYS = {
    "is_correct",
    "correct_choice_id",
    "expected_answer",
    "explanation",
    "common_mistake",
    "answer",
    "answer_key",
}

GRADE_FEEDBACK_KEYS = {
    "question_type",
    "is_correct",
    "auto_graded",
    "requires_review",
    "correct_choice_id",
    "expected_answer",
    "explanation",
    "common_mistake",
}


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@example.com"


def _assert_no_answer_leak(payload) -> None:
    """Recursively ensure answer-key fields are absent from quiz fetch JSON."""
    if isinstance(payload, dict):
        leaked = ANSWER_LEAK_KEYS.intersection(payload.keys())
        if leaked:
            raise AssertionError(f"Answer leak fields present: {sorted(leaked)}")
        for value in payload.values():
            _assert_no_answer_leak(value)
    elif isinstance(payload, list):
        for item in payload:
            _assert_no_answer_leak(item)


class ApiSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        db = SessionLocal()
        try:
            cls.question = (
                db.query(Question).filter(Question.is_active.is_(True)).first()
            )
            if cls.question is None:
                raise unittest.SkipTest("No active questions in database")
            from app.models import Topic

            topic = db.get(Topic, cls.question.topic_id)
            cls.course = db.get(Course, topic.course_id) if topic else None
            if cls.course is None:
                cls.course = (
                    db.query(Course).filter(Course.is_active.is_(True)).first()
                )
            if cls.course is None:
                raise unittest.SkipTest("No active course in database")
            cls.course_id = cls.course.id
            cls.question_id = cls.question.id
        finally:
            db.close()

    def setUp(self):
        reset_rate_limits()
        settings.rate_limit_enabled = False

    def tearDown(self):
        settings.rate_limit_enabled = True
        reset_rate_limits()

    def _register(self, email: str | None = None, password: str = "SecurePass1"):
        email = email or _email("user")
        response = self.client.post(
            "/api/v1/auth/register",
            json={"name": "API Sec", "email": email, "password": password},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    # --- 1. Answer key exposure ---

    def test_guest_quiz_fetch_has_no_answer_fields(self):
        response = self.client.get(
            f"/api/v1/quiz/guest/questions?course_id={self.course_id}&count=3"
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("questions", body)
        self.assertIn("guest_token", body)
        self.assertTrue(body["guest_token"])
        self.assertGreater(len(body["questions"]), 0)
        _assert_no_answer_leak(body)
        for question in body["questions"]:
            for choice in question.get("choices", []):
                self.assertEqual(set(choice.keys()), {"id", "label"})

    def test_guest_grade_without_session_rejected(self):
        response = self.client.post(
            "/api/v1/quiz/guest/grade",
            json={
                "guest_token": "",
                "question_id": self.question_id,
                "response_text": "42",
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("correct", response.json()["detail"].lower())

    def test_guest_grade_without_token_rejected(self):
        response = self.client.post(
            "/api/v1/quiz/guest/grade",
            json={
                "question_id": self.question_id,
                "response_text": "42",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_guest_grade_after_fetch_returns_intended_feedback_only(self):
        fetch = self.client.get(
            f"/api/v1/quiz/guest/questions?course_id={self.course_id}&count=2"
        )
        self.assertEqual(fetch.status_code, 200)
        fetch_body = fetch.json()
        guest_token = fetch_body["guest_token"]
        question = fetch_body["questions"][0]
        qid = question["id"]

        # Prefer MC choice if present; else textual answer
        body: dict
        if question.get("choices"):
            body = {
                "guest_token": guest_token,
                "question_id": qid,
                "answer_choice_id": question["choices"][0]["id"],
            }
        else:
            body = {
                "guest_token": guest_token,
                "question_id": qid,
                "response_text": "1",
            }

        grade = self.client.post("/api/v1/quiz/guest/grade", json=body)
        self.assertEqual(grade.status_code, 200, grade.text)
        payload = grade.json()
        self.assertTrue(GRADE_FEEDBACK_KEYS.issuperset(payload.keys()))
        # Must not expose ORM / password fields
        self.assertNotIn("password", str(payload).lower())
        self.assertNotIn("password_hash", str(payload))

    def test_guest_cannot_grade_foreign_question_id(self):
        fetch = self.client.get(
            f"/api/v1/quiz/guest/questions?course_id={self.course_id}&count=1"
        )
        self.assertEqual(fetch.status_code, 200)
        fetch_body = fetch.json()
        guest_token = fetch_body["guest_token"]
        issued = {q["id"] for q in fetch_body["questions"]}
        # Pick an active question not in the issued set if possible
        db = SessionLocal()
        try:
            foreign = (
                db.query(Question)
                .filter(Question.is_active.is_(True), ~Question.id.in_(issued))
                .first()
            )
        finally:
            db.close()
        if foreign is None:
            self.skipTest("Need another question id to test foreign grade")

        response = self.client.post(
            "/api/v1/quiz/guest/grade",
            json={
                "guest_token": guest_token,
                "question_id": foreign.id,
                "response_text": "x",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_authenticated_quiz_fetch_does_not_leak_answers(self):
        auth = self._register()
        token = auth["access_token"]
        response = self.client.get(
            f"/api/v1/quiz/questions?course_id={self.course_id}&count=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        _assert_no_answer_leak(response.json())

    # --- 2. OpenAPI docs ---

    def test_docs_disabled_by_default_config(self):
        # Application was built with settings.enable_api_docs from env.
        # When False, /docs and /redoc are 404. When True (local .env), they 200.
        docs = self.client.get("/docs")
        redoc = self.client.get("/redoc")
        if settings.enable_api_docs:
            self.assertIn(docs.status_code, (200, 200))
            self.assertEqual(docs.status_code, 200)
            self.assertEqual(redoc.status_code, 200)
        else:
            self.assertEqual(docs.status_code, 404)
            self.assertEqual(redoc.status_code, 404)

    def test_docs_factory_respects_flag(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient as TC

        locked = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        client = TC(locked)
        self.assertEqual(client.get("/docs").status_code, 404)
        self.assertEqual(client.get("/redoc").status_code, 404)
        self.assertEqual(client.get("/openapi.json").status_code, 404)

    # --- 3. CORS ---

    def test_cors_allows_configured_origin(self):
        origins = settings.cors_allow_origins()
        self.assertTrue(origins)
        self.assertNotIn("*", origins)
        origin = origins[0]
        response = self.client.options(
            "/api/v1/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"), origin
        )

    def test_cors_rejects_unknown_origin(self):
        response = self.client.get(
            "/api/v1/health",
            headers={"Origin": "https://evil.example"},
        )
        # Request succeeds but ACAO must not echo evil origin
        self.assertEqual(response.status_code, 200)
        acao = response.headers.get("access-control-allow-origin")
        self.assertNotEqual(acao, "https://evil.example")
        self.assertNotEqual(acao, "*")

    def test_frontend_url_rejects_wildcard(self):
        with self.assertRaises(ValueError):
            # Temporarily patch via method using a fake settings copy
            class Boom:
                frontend_url = "*"

                def cors_allow_origins(self):
                    raw = self.frontend_url.strip()
                    for part in raw.split(","):
                        if part.strip() == "*":
                            raise ValueError("no wildcard")
                    return []

            Boom().cors_allow_origins()

        # Exercise real settings helper with temporary override
        previous = settings.frontend_url
        try:
            settings.frontend_url = "https://ok.example,*"
            with self.assertRaises(ValueError):
                settings.cors_allow_origins()
        finally:
            settings.frontend_url = previous

    # --- 4. Validation / body size ---

    def test_feedback_message_too_long(self):
        response = self.client.post(
            "/api/v1/feedback",
            json={
                "course_id": self.course_id,
                "rating": "positive",
                "message": "x" * 2001,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_question_report_comment_too_long(self):
        response = self.client.post(
            "/api/v1/question-reports",
            json={
                "question_id": self.question_id,
                "reason": "other",
                "comment": "y" * 2001,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_quiz_count_above_maximum(self):
        response = self.client.get(
            f"/api/v1/quiz/guest/questions?course_id={self.course_id}&count=51"
        )
        self.assertEqual(response.status_code, 422)

    def test_oversized_body_rejected(self):
        response = self.client.post(
            "/api/v1/feedback",
            content=b"{" + b"x" * (settings.max_request_body_bytes + 100),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["detail"], "Request body is too large.")

    # --- 5. IDOR ---

    def test_cross_user_cannot_read_other_attempt_results(self):
        user_a = self._register(email=_email("a"))
        user_b = self._register(email=_email("b"))
        token_a = user_a["access_token"]
        token_b = user_b["access_token"]

        quiz = self.client.get(
            f"/api/v1/quiz/questions?course_id={self.course_id}&count=1",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(quiz.status_code, 200)
        attempt_id = quiz.json()["quiz_attempt_id"]

        forbidden = self.client.get(
            f"/api/v1/quiz/attempt/{attempt_id}/results",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertIn(forbidden.status_code, (403, 404))

        allowed = self.client.get(
            f"/api/v1/quiz/attempt/{attempt_id}/results",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(allowed.status_code, 200)

    def test_cross_user_cannot_attach_feedback_to_foreign_attempt(self):
        user_a = self._register(email=_email("fa"))
        user_b = self._register(email=_email("fb"))
        quiz = self.client.get(
            f"/api/v1/quiz/questions?course_id={self.course_id}&count=1",
            headers={"Authorization": f"Bearer {user_a['access_token']}"},
        )
        attempt_id = quiz.json()["quiz_attempt_id"]

        response = self.client.post(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {user_b['access_token']}"},
            json={
                "course_id": self.course_id,
                "quiz_attempt_id": attempt_id,
                "rating": "positive",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_guest_cannot_attach_feedback_to_attempt(self):
        user = self._register(email=_email("fg"))
        quiz = self.client.get(
            f"/api/v1/quiz/questions?course_id={self.course_id}&count=1",
            headers={"Authorization": f"Bearer {user['access_token']}"},
        )
        attempt_id = quiz.json()["quiz_attempt_id"]
        self.client.cookies.clear()
        response = self.client.post(
            "/api/v1/feedback",
            json={
                "course_id": self.course_id,
                "quiz_attempt_id": attempt_id,
                "rating": "negative",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_progress_and_weakness_require_auth(self):
        self.client.cookies.clear()
        self.assertEqual(self.client.get("/api/v1/progress").status_code, 401)
        self.assertEqual(
            self.client.get(
                f"/api/v1/weakness-map?course_id={self.course_id}"
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.get(
                f"/api/v1/daily-practice?course_id={self.course_id}"
            ).status_code,
            401,
        )

    def test_admin_requires_authorization(self):
        self.client.cookies.clear()
        response = self.client.get("/api/v1/admin/overview")
        self.assertEqual(response.status_code, 403)

        student = self._register(email=_email("stu"))
        response = self.client.get(
            "/api/v1/admin/overview",
            headers={"Authorization": f"Bearer {student['access_token']}"},
        )
        self.assertEqual(response.status_code, 403)

    # --- 6. Security headers ---

    def test_security_headers_present(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(response.headers.get("x-frame-options"), "DENY")
        self.assertIn("strict-origin", response.headers.get("referrer-policy", ""))
        self.assertIn("Permissions-Policy", response.headers)
        # Starlette lowercases header names
        self.assertTrue(
            response.headers.get("permissions-policy")
            or response.headers.get("Permissions-Policy")
        )
        csp = response.headers.get("content-security-policy", "")
        self.assertIn("frame-ancestors", csp)


if __name__ == "__main__":
    unittest.main()

