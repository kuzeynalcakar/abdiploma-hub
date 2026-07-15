"""Seed Alberta high school courses and their curriculum topics.

Courses and topics only — no questions, no users. Idempotent: existing
courses and topics (matched by course code and topic name) are skipped,
so the script can be re-run safely at any time.

Usage, from the backend directory:

    python -m app.database.curriculum_seed
"""

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models import Course, Topic

# Topic names follow Alberta Program of Studies units for each course.
CURRICULUM = {
    "MATH10C": {
        "name": "Mathematics 10C",
        "topics": [
            "Measurement",
            "Trigonometry",
            "Exponents and Radicals",
            "Polynomials",
            "Relations and Functions",
            "Linear Functions",
            "Systems of Linear Equations",
        ],
    },
    "MATH20-1": {
        "name": "Mathematics 20-1",
        "topics": [
            "Sequences and Series",
            "Trigonometry",
            "Quadratic Functions",
            "Quadratic Equations",
            "Radical Expressions and Equations",
            "Rational Expressions and Equations",
            "Absolute Value and Reciprocal Functions",
            "Systems of Equations",
            "Linear and Quadratic Inequalities",
        ],
    },
    "MATH20-2": {
        "name": "Mathematics 20-2",
        "topics": [
            "Inductive and Deductive Reasoning",
            "Properties of Angles and Triangles",
            "Acute Triangle Trigonometry",
            "Radicals",
            "Statistical Reasoning",
            "Quadratic Functions and Equations",
            "Proportional Reasoning",
        ],
    },
    "MATH30-1": {
        "name": "Mathematics 30-1",
        "topics": [
            "Transformations of Functions",
            "Radical Functions",
            "Polynomial Functions",
            "Trigonometry and the Unit Circle",
            "Trigonometric Functions and Graphs",
            "Trigonometric Identities",
            "Exponential Functions",
            "Logarithmic Functions",
            "Rational Functions",
            "Function Operations and Composition",
            "Permutations, Combinations and the Binomial Theorem",
        ],
    },
    "MATH30-2": {
        "name": "Mathematics 30-2",
        "topics": [
            "Set Theory and Logic",
            "Counting Methods",
            "Probability",
            "Rational Expressions and Equations",
            "Polynomial Functions",
            "Exponential and Logarithmic Functions",
            "Sinusoidal Functions",
        ],
    },
    "BIO30": {
        "name": "Biology 30",
        "topics": [
            "Nervous and Endocrine Systems",
            "Reproduction and Development",
            "Cell Division",
            "Genetics and Molecular Biology",
            "Population and Community Dynamics",
        ],
    },
    "CHEM30": {
        "name": "Chemistry 30",
        "topics": [
            "Thermochemical Changes",
            "Electrochemical Changes",
            "Chemical Changes of Organic Compounds",
            "Chemical Equilibrium Focusing on Acid-Base Systems",
        ],
    },
    "PHYS30": {
        "name": "Physics 30",
        "topics": [
            "Momentum and Impulse",
            "Forces and Fields",
            "Electromagnetic Radiation",
            "Atomic Physics",
        ],
    },
    "SCI30": {
        "name": "Science 30",
        "topics": [
            "Circulatory and Immune Systems",
            "Genetics and Molecular Biology",
            "Environmental Chemistry",
            "Field Theory and Electrical Energy",
            "Electromagnetic Spectrum",
            "Energy and the Environment",
        ],
    },
    "SCI10": {
        "name": "Science 10",
        "topics": [
            "Energy and Matter in Chemical Change",
            "Energy Flow in Technological Systems",
            "Cycling of Matter in Living Systems",
            "Energy Flow in Global Systems",
        ],
    },
    "ELA30-1": {
        "name": "English Language Arts 30-1",
        "topics": [
            "Reading Comprehension",
            "Literary Analysis",
            "Poetry",
            "Shakespearean Drama",
            "Personal Response to Texts",
            "Critical and Analytical Response",
        ],
    },
    "ELA30-2": {
        "name": "English Language Arts 30-2",
        "topics": [
            "Reading Comprehension",
            "Visual and Multimodal Texts",
            "Literary Devices",
            "Personal Response to Texts",
            "Critical Response Writing",
            "Grammar and Mechanics",
        ],
    },
    "SOC30-1": {
        "name": "Social Studies 30-1",
        "topics": [
            "Ideology and Identity",
            "Origins of Liberalism",
            "Resistance to Liberalism",
            "The Viability of Contemporary Liberalism",
            "Citizenship and Ideology",
        ],
    },
    "SOC30-2": {
        "name": "Social Studies 30-2",
        "topics": [
            "Ideologies and Identity",
            "Liberalism in Practice",
            "Challenges to Liberalism",
            "Citizenship and Ideology",
        ],
    },
}

# Curriculum shells with no imported question bank yet.
# They remain in the catalog for future enablement but must not be
# active practice courses (integrity: active_courses_without_questions).
COMING_SOON_WITHOUT_BANK = frozenset(
    {
        "MATH10C",
        "MATH20-2",
        "ELA30-1",
        "ELA30-2",
        "SOC30-2",
    }
)


def seed_curriculum(db: Session) -> None:
    courses_created = 0
    topics_created = 0

    for code, data in CURRICULUM.items():
        course = db.query(Course).filter(Course.code == code).first()
        if course is None:
            course = Course(
                code=code,
                name=data["name"],
                is_active=code not in COMING_SOON_WITHOUT_BANK,
            )
            db.add(course)
            db.flush()
            courses_created += 1

        existing_names = {
            name
            for (name,) in db.query(Topic.name).filter(
                Topic.course_id == course.id
            )
        }
        for sort_order, topic_name in enumerate(data["topics"]):
            if topic_name in existing_names:
                continue
            db.add(
                Topic(
                    course_id=course.id,
                    name=topic_name,
                    sort_order=sort_order,
                )
            )
            topics_created += 1

    db.commit()
    print(f"Courses created: {courses_created}")
    print(f"Topics created: {topics_created}")


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed_curriculum(session)
    finally:
        session.close()
