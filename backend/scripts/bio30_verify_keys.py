from app.database.session import SessionLocal
from app.models import Question, Course, Topic
from app.services.answer_grading import grade_answer

db = SessionLocal()
checks = [
    ("dominant phenotype", "0.75"),
    ("light pathway", "2413"),
    ("auditory pathway", "2143"),
    ("ovarian cycle", "2143"),
    ("implantation", "2413"),
    ("insulin", "3124"),
]
bio = db.query(Course).filter(Course.code == "BIO30").first()
for kw, expected in checks:
    q = (
        db.query(Question)
        .join(Topic)
        .filter(Topic.course_id == bio.id, Question.question_text.ilike(f"%{kw}%"))
        .first()
    )
    if not q:
        print(f"MISSING stem with {kw}")
        continue
    ans = q.answer
    ok = ans == expected
    print(f"Q{q.id} [{kw}]: answer={ans} expected={expected} {'OK' if ok else 'WRONG'}")
    if q.question_type == "numerical_response":
        r = grade_answer(q, response_text=expected)
        print(f"  grader accepts correct: {r.is_correct}")

q120 = db.query(Question).filter(Question.id == 120).first()
print(f"Q120 explanation len={len(q120.explanation or '')}: {(q120.explanation or '')[:120]}")
db.close()
