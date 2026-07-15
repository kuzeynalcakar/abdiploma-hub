"""Tighten the 16 student-trust short-answer items identified by audit.

Only touches listed IDs. Does not change grading tolerance.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.database.init_db import init_db  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models import Question  # noqa: E402
from app.services.answer_grading import grade_numerical_response  # noqa: E402
from app.services.short_answers import (  # noqa: E402
    coalesce_accepted_answers,
    dump_accepted_answers,
)

# id -> fix payload
FIXES: dict[int, dict] = {
    10: {
        "question_text": (
            "Solve $2\\cos^2(x) - \\sin(x) - 1 = 0$ over $0 \\le x < 2\\pi$. "
            "One family of solutions satisfies $\\sin(x) = -1$. "
            "Record that exact solution in this interval using ``pi`` "
            "(for example, ``3pi/2``)."
        ),
        "answer": "3pi/2",
        "accepted_answers": [
            "3pi/2",
            "3π/2",
            "(3pi)/2",
            "(3π)/2",
            "3*pi/2",
        ],
        "reason": (
            "Counting solutions was too shallow for algebraic trig solving; "
            "now requires finding the exact root where sin(x)=-1. "
            "Tight exact-form accepted list only."
        ),
    },
    50: {
        "question_text": (
            "Let $f(x)=\\sqrt{16-x^2}$ and $g(x)=x^2-3x-4$. "
            "For the quotient $(f/g)(x)$, two values in $[-4,4]$ must be "
            "excluded because $g(x)=0$. Record the smaller excluded value."
        ),
        "answer": "-1",
        "accepted_answers": ["-1", "-1.0"],
        "reason": (
            "Counting excluded values did not require identifying the "
            "denominator zeros; now students must find both and report "
            "the smaller one. Accepted list is numeric only."
        ),
    },
    68: {
        "question_text": (
            "Let $f(x)=\\dfrac{x+2}{x-1}$ with $x \\ne 1$. "
            "Evaluate $f(f(5))$. Record the exact value."
        ),
        "answer": "5",
        "accepted_answers": ["5", "5.0"],
        "reason": (
            "Yes/no with y/true was too broad and weak for composition/"
            "inverse skill; evaluating f(f(5))=5 demonstrates that f is "
            "an involution at a concrete input."
        ),
    },
    125: {
        "question_text": (
            "An investment grows by continuous compounding $A = P e^{rt}$. "
            "First isolate $t$, then determine how many years are required "
            "for the investment to triple when $r = 0.05$. "
            "Round to the nearest tenth of a year."
        ),
        "answer": "22.0",
        "accepted_answers": ["22.0", "22"],
        "reason": (
            "Stem now explicitly requires isolating t via ln before "
            "computing; dropped unrounded intermediates (21.97) so only "
            "the correctly rounded diploma-style answer is accepted."
        ),
    },
    144: {
        "question_text": (
            "Factor $P(x)=x^4-5x^2+4$ completely over the reals. "
            "The linear factors may be written as $(x-a)(x+a)(x-b)(x+b)$ "
            "with $0 < a < b$. Record the value of $b$."
        ),
        "answer": "2",
        "accepted_answers": ["2", "2.0"],
        "reason": (
            "Counting intercepts did not require complete factorization; "
            "students must factor the quartic and identify the larger "
            "positive root parameter b=2."
        ),
    },
    204: {
        "question_text": (
            "Consider $\\dfrac{\\sin(2x)}{1+\\cos(2x)}=\\tan(x)$ on "
            "$0 \\le x < 2\\pi$. Record the smallest non-permissible "
            "value of $x$ in this interval, using ``pi`` "
            "(for example, ``pi/2``)."
        ),
        "answer": "pi/2",
        "accepted_answers": [
            "pi/2",
            "π/2",
            "(pi)/2",
            "(π)/2",
            "1pi/2",
        ],
        "reason": (
            "Counting restrictions skipped identifying the actual "
            "non-permissible values; now requires the smallest excluded "
            "exact value π/2."
        ),
    },
    224: {
        "question_text": (
            "Twelve volunteers are partitioned into three distinct teams "
            "of sizes 5, 4, and 3. Because order within a team does not "
            "matter, use combinations: compute "
            "$_{12}C_5 \\cdot _7C_4 \\cdot _3C_3$. "
            "Record the integer result."
        ),
        "answer": "27720",
        "accepted_answers": ["27720"],
        "reason": (
            "Stem now forces the combinations counting structure aligned "
            "with PC3; removed comma formatting variant so only the "
            "exact integer is accepted."
        ),
    },
    292: {
        "question_text": (
            "For $f(x)=\\dfrac{2x}{x-3}$, record the equation of the "
            "vertical asymptote in the form ``x = k`` (include ``x =``)."
        ),
        "answer": "x = 3",
        "accepted_answers": ["x = 3", "x=3", "x =3", "x= 3"],
        "reason": (
            "Removed bare ``3``, which could be guessed without stating "
            "an asymptote equation; require explicit x = k form."
        ),
    },
    294: {
        "question_text": (
            "A rational function has vertical asymptote $x=-2$, "
            "horizontal asymptote $y=1$, and passes through $(0,0)$. "
            "It can be written as $f(x)=\\dfrac{x}{x+a}$. "
            "Record the positive value of $a$."
        ),
        "answer": "2",
        "accepted_answers": ["2", "2.0"],
        "reason": (
            "Open-ended equation entry accepted only one of many valid "
            "forms and was fragile to grade; asking for parameter a "
            "from the standard construction still tests VA/HA/(0,0) "
            "with one clear numeric key."
        ),
    },
    416: {
        "question_text": (
            "Hormone residues from contraceptives that enter wastewater "
            "and disrupt reproduction in aquatic organisms primarily "
            "represent which STS concern? Enter exactly one of: "
            "ethical, economic, ecological."
        ),
        "answer": "ecological",
        "accepted_answers": ["ecological"],
        "reason": (
            "Removed overly broad synonyms environmental/ecology; "
            "stem forces a single diploma-style STS classification."
        ),
    },
    417: {
        "question_text": (
            "Compare gametogenesis: a primary spermatocyte typically "
            "yields 4 functional sperm, while one primary oocyte that "
            "completes meiosis typically yields how many functional "
            "ova? Record the integer."
        ),
        "answer": "1",
        "accepted_answers": ["1"],
        "reason": (
            "Asking only for spermatocyte product count missed the "
            "comparison; now contrasts sperm vs ovum yield so students "
            "must know unequal cytokinesis outcome (1 ovum)."
        ),
    },
    463: {
        "question_text": (
            "Nondisjunction produces an $n+1$ human gamete that is "
            "fertilized by a normal $n$ gamete. Record the resulting "
            "zygote chromosome number as an integer."
        ),
        "answer": "47",
        "accepted_answers": ["47"],
        "reason": (
            "Removed trisomy/2n+1, which accepted conceptual labels "
            "instead of the specific chromosome count the stem requires."
        ),
    },
    465: {
        "question_text": (
            "Compare mitosis and meiosis: relative to the parent cell, "
            "are the daughter cells produced by meiosis haploid or "
            "diploid? Enter haploid or diploid."
        ),
        "answer": "haploid",
        "accepted_answers": ["haploid"],
        "reason": (
            "Counting meiotic divisions was too shallow; requiring the "
            "ploidy outcome tests the core mitosis/meiosis contrast "
            "with a single non-ambiguous term."
        ),
    },
    538: {
        "question_text": (
            "A couple with normal vision has a colour-blind son. "
            "Colour blindness is X-linked recessive. Record the mother's "
            "most likely genotype using carrier notation with N = normal "
            "allele and c = colour-blind allele (enter exactly XNXc)."
        ),
        "answer": "XNXc",
        "accepted_answers": [
            "XNXc",
            "X^N X^c",
            "X^{N}X^{c}",
            "X^N X^c",
        ],
        "reason": (
            "Removed bare carrier / heterozygous carrier; genotype "
            "notation is now required as specified in the stem."
        ),
    },
    540: {
        "question_text": (
            "A mutation that changes exactly one DNA base pair "
            "(with no insertion or deletion of bases) is called a "
            "_____ mutation. Enter the full two-word name."
        ),
        "answer": "point mutation",
        "accepted_answers": ["point mutation", "Point mutation", "Point Mutation"],
        "reason": (
            "Removed bare point and substitution, which were too broad "
            "or mismatched terminology; only the full term "
            "point mutation is accepted."
        ),
    },
    584: {
        "question_text": (
            "In a small population, allele frequencies change due to "
            "random sampling error rather than differences in fitness. "
            "Name this microevolutionary mechanism (exactly two words)."
        ),
        "answer": "genetic drift",
        "accepted_answers": ["genetic drift", "Genetic drift", "Genetic Drift"],
        "reason": (
            "Removed drift / founder effect / bottleneck effect, which "
            "accepted related-but-distinct mechanisms; only genetic drift "
            "matches the random sampling-error definition."
        ),
    },
}


def main() -> int:
    init_db()
    db = SessionLocal()
    report: list[dict] = []
    try:
        backup_dir = BACKEND / "backups"
        backup_dir.mkdir(exist_ok=True)
        db_path = BACKEND / "albertaprep.db"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup = backup_dir / f"albertaprep.db.bak-sa-trust-16-{stamp}"
        if db_path.is_file():
            shutil.copy2(db_path, backup)

        for qid, fix in FIXES.items():
            q = db.get(Question, qid)
            if q is None or not q.is_active:
                raise SystemExit(f"Missing or inactive question {qid}")
            if q.question_type != "numerical_response":
                raise SystemExit(f"Question {qid} is not short-answer NR")

            old_stem = q.question_text
            old_accepted = coalesce_accepted_answers(q.answer, q.accepted_answers)

            q.question_text = fix["question_text"]
            q.answer = fix["answer"]
            q.accepted_answers = dump_accepted_answers(fix["accepted_answers"])
            # outcome/topic/difficulty/skill/explanation untouched

            report.append(
                {
                    "question_id": qid,
                    "old_stem": old_stem,
                    "new_stem": fix["question_text"],
                    "old_accepted_answers": old_accepted,
                    "new_accepted_answers": coalesce_accepted_answers(
                        fix["answer"], dump_accepted_answers(fix["accepted_answers"])
                    ),
                    "reason": fix["reason"],
                }
            )

        db.commit()

        # Verify only these IDs grade correctly on canonical / reject nonsense.
        for qid, fix in FIXES.items():
            q = db.get(Question, qid)
            ok = grade_numerical_response(q, fix["answer"])
            if not ok.auto_graded or ok.is_correct is not True:
                raise SystemExit(f"Canonical grade failed for {qid}")
            try:
                bad = grade_numerical_response(q, "zzz_wrong_answer_9x")
            except ValueError:
                bad = None  # numeric-only fields reject non-numeric input
            if bad is not None and bad.is_correct:
                raise SystemExit(f"False accept for {qid}")
            # Explicit numeric near-miss rejection when answer is tiny.
            if fix["answer"] in {"1", "2", "5", "-1"}:
                near = grade_numerical_response(q, "99")
                if near.is_correct:
                    raise SystemExit(f"Near-miss false accept for {qid}")

        out = BACKEND / "docs" / "SHORT_ANSWER_TRUST_16_FIX_REPORT.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"updated={len(report)} backup={backup}")
        print(f"report={out}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
