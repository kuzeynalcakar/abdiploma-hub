"""Pydantic schemas for the admin dashboard APIs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StatCard(BaseModel):
    key: str
    label: str
    value: int | float | str | None
    note: str | None = None


class RecentUser(BaseModel):
    id: int
    name: str
    # Masked for operator privacy (e.g. a***@example.com) — never full address in UI payloads.
    email_masked: str
    created_at: datetime | None


class RecentAttempt(BaseModel):
    id: int
    user_id: int
    course_name: str | None
    mode: str
    questions_total: int
    questions_correct: int | None
    started_at: datetime | None
    completed_at: datetime | None


class RecentFeedback(BaseModel):
    id: int
    rating: str
    message: str | None
    course_name: str | None
    created_at: datetime | None
    is_anonymous: bool
    is_unread: bool = True


class RecentReport(BaseModel):
    id: int
    question_id: int
    reason: str
    status: str
    created_at: datetime | None


class AdminOverview(BaseModel):
    registered_users: int
    guest_quiz_sessions: int | None
    guest_quiz_sessions_note: str | None
    quiz_attempts: int
    questions_answered: int
    daily_practice_sessions: int
    average_accuracy: float | None
    practice_streak_average: float | None
    courses_available: int
    total_questions: int
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    recent_registrations: list[RecentUser]
    recent_quiz_attempts: list[RecentAttempt]
    recent_feedback: list[RecentFeedback]
    recent_reports: list[RecentReport]


class AdminReportItem(BaseModel):
    id: int
    course_code: str | None
    course_name: str | None
    question_id: int
    question_preview: str
    reason: str
    comment: str | None
    reported_at: datetime | None
    status: str
    status_changed_at: datetime | None = None
    admin_note: str | None = None
    report_count_for_question: int
    # Integer user id only — no email/name (ops triage without excess PII).
    has_reporter: bool = False


class AdminReportList(BaseModel):
    items: list[AdminReportItem]
    total: int


class ReportStatusUpdate(BaseModel):
    status: Literal["pending", "resolved", "ignored"]
    admin_note: str | None = Field(None, max_length=2000)


class AdminQuestionDetail(BaseModel):
    id: int
    question_text: str
    explanation: str | None
    question_type: str
    difficulty: str | None
    answer: str | None
    course_code: str | None
    course_name: str | None
    topic_name: str | None
    choices: list[dict]
    report_count: int
    reports: list[AdminReportItem]


class FeedbackWordCount(BaseModel):
    word: str
    count: int


class AdminFeedbackItem(BaseModel):
    id: int
    rating: str
    message: str | None
    created_at: datetime | None
    course_code: str | None
    course_name: str | None
    is_anonymous: bool
    is_unread: bool = True
    admin_reviewed_at: datetime | None = None


class AdminFeedbackSummary(BaseModel):
    total: int
    unread_count: int
    positive_count: int
    negative_count: int
    positive_percent: float | None
    negative_percent: float | None
    most_common_words: list[FeedbackWordCount]
    newest: list[AdminFeedbackItem]
    items: list[AdminFeedbackItem]
    by_sentiment: dict[str, int] | None = None


class TopicStat(BaseModel):
    topic_id: int
    topic_name: str
    course_code: str | None
    attempts: int | None = None
    accuracy: float | None = None
    questions_attempted: int | None = None


class CourseAttemptStat(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    attempts: int


class AdminAnalytics(BaseModel):
    most_attempted_courses: list[CourseAttemptStat]
    most_difficult_topics: list[TopicStat]
    highest_accuracy_topics: list[TopicStat]
    lowest_accuracy_topics: list[TopicStat]
    average_quiz_score: float | None
    average_quiz_duration_seconds: float | None
    average_questions_per_session: float | None
    daily_practice_completion_percent: float | None
    weakness_map_users: int
    weakness_map_note: str | None
    guest_vs_registered: dict
    top_searched_topics: list | None
    top_searched_topics_note: str | None


class QuestionsByCourse(BaseModel):
    course_code: str
    course_name: str
    question_count: int


class AdminDbHealth(BaseModel):
    total_users: int
    total_attempts: int
    total_answers: int
    total_questions: int
    questions_by_course: list[QuestionsByCourse]
    reports_waiting: int
    database_size_bytes: int | None
    database_size_label: str | None
    last_backup: str | None
    last_backup_note: str | None
    health_status: str
    database_status: str


class AdminImpact(BaseModel):
    registered_users: int
    quiz_attempts: int
    questions_answered: int
    courses_practiced: int
    feedback_submitted: int
    reports_submitted: int
    students_helped: int
    practice_sessions_completed: int
    daily_practices_completed: int
    average_improvement: float | None
    average_improvement_note: str | None
    strong_topics_mastered: int
    weaknesses_identified: int
    questions_reported: int
    questions_fixed: int
    feedback_received: int
    users_last_7_days: int
    quizzes_last_7_days: int


class MostReportedQuestion(BaseModel):
    question_id: int
    report_count: int
    pending_count: int
    course_code: str | None
    question_preview: str


class AdminQuestionQuality(BaseModel):
    unanswered_reports_count: int
    questions_with_multiple_reports: int
    most_reported_questions: list[MostReportedQuestion]


class RecentErrorItem(BaseModel):
    ts: float
    endpoint: str
    status_code: int
    error_type: str
    message: str


class AdminReliability(BaseModel):
    total_users: int
    total_quizzes: int
    feedback_count: int
    reported_questions: int
    pending_reports: int
    sentry_configured: bool
    environment: str
    version: str
    uptime_seconds: int
    recent_errors: list[RecentErrorItem]


class IntegrityCheckItem(BaseModel):
    key: str
    label: str
    count: int
    ok: bool
    detail: str | None = None


class AdminIntegrity(BaseModel):
    ok: bool
    issue_count: int
    checks: list[IntegrityCheckItem]

