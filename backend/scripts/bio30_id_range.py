import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.session import SessionLocal
from app.models import Course, Question, Topic

db = SessionLocal()
bio = db.query(Course).filter(Course.code == "BIO30").first()
qs = (
    db.query(Question.id, Question.question_text[:50])
    .join(Topic)
    .filter(Topic.course_id == bio.id, Question.is_active.is_(True))
    .order_by(Question.id)
    .all()
)
print("BIO30 count", len(qs))
print("min", qs[0][0], qs[0][1])
print("max", qs[-1][0], qs[-1][1])
# gaps
ids = [q[0] for q in qs]
print("id range span", ids[-1] - ids[0] + 1, "actual", len(ids))
low = [i for i in ids if i <= 100]
high = [i for i in ids if i > 294]
print("ids <=100", len(low), low[:10])
print("ids >294", len(high), high[:10], "...", high[-5:])
db.close()
