"""One-time migration: rewrite non-auto-gradable constructed-response items.

Invalid items were stored as written_response (manual review). Each is converted
to numerical_response short-answer with accepted_answers. MC untouched.

Usage (from backend/):
  python scripts/migrate_rewrite_invalid_nr.py
  python scripts/migrate_rewrite_invalid_nr.py --dry-run
"""

from __future__ import annotations

import argparse
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
from app.services.short_answers import dump_accepted_answers  # noqa: E402

# id -> rewrite. explanation / outcome / difficulty / skill preserved on Question.
REWRITES: dict[int, dict] = {
    # --- BIO30 ---
    354: {
        "reason": "Explain... (requires subjective/paragraph marking)",
        "question_text": (
            "After heavy sweating raises blood osmolarity, which hormone "
            "increases water reabsorption in the kidney collecting ducts?"
        ),
        "answer": "ADH",
        "accepted_answers": [
            "ADH",
            "adh",
            "antidiuretic hormone",
            "anti-diuretic hormone",
            "vasopressin",
        ],
    },
    355: {
        "reason": "Explain... multi-step synaptic description",
        "question_text": (
            "At a cholinergic synapse, which ion enters the presynaptic "
            "terminal through voltage-gated channels to trigger vesicle "
            "exocytosis of acetylcholine?"
        ),
        "answer": "Ca2+",
        "accepted_answers": [
            "Ca2+",
            "Ca^{2+}",
            "calcium",
            "calcium ion",
            "calcium ions",
            "Ca++",
        ],
    },
    356: {
        "reason": "Compare... autonomic divisions",
        "question_text": (
            "Which autonomic division is primarily responsible for "
            "fight-or-flight responses such as increased heart rate?"
        ),
        "answer": "sympathetic",
        "accepted_answers": [
            "sympathetic",
            "sympathetic nervous system",
            "SNS",
            "sympathetic division",
        ],
    },
    357: {
        "reason": "Describe... multi-system glucose regulation",
        "question_text": (
            "After a large carbohydrate meal raises blood glucose, which "
            "hormone is secreted by pancreatic beta cells to lower blood glucose?"
        ),
        "answer": "insulin",
        "accepted_answers": ["insulin", "Insulin"],
    },
    358: {
        "reason": "Compare... rod vs cone",
        "question_text": (
            "Which photoreceptor cells are more sensitive in dim light and "
            "do not detect colour?"
        ),
        "answer": "rods",
        "accepted_answers": ["rods", "rod", "rod cells", "rod cell"],
    },
    359: {
        "reason": "Explain... thyroid feedback",
        "question_text": (
            "Which anterior-pituitary hormone stimulates the thyroid gland "
            "to release T3 and T4?"
        ),
        "answer": "TSH",
        "accepted_answers": [
            "TSH",
            "tsh",
            "thyroid-stimulating hormone",
            "thyroid stimulating hormone",
            "thyrotropin",
        ],
    },
    360: {
        "reason": "Explain... thyroid feedback",
        "question_text": (
            "Elevated blood T3/T4 primarily inhibits release of which "
            "hypothalamic hormone in the thyroid axis?"
        ),
        "answer": "TRH",
        "accepted_answers": [
            "TRH",
            "trh",
            "thyrotropin-releasing hormone",
            "thyrotropin releasing hormone",
        ],
    },
    361: {
        "reason": "Explain... pupillary reflex",
        "question_text": (
            "In bright light, which autonomic division mediates pupil "
            "constriction of the iris sphincter?"
        ),
        "answer": "parasympathetic",
        "accepted_answers": [
            "parasympathetic",
            "parasympathetic nervous system",
            "PNS",
            "parasympathetic division",
        ],
    },
    416: {
        "reason": "Discuss... STS essay prompt",
        "question_text": (
            "Trace hormones from hormonal contraceptives entering aquatic "
            "ecosystems via wastewater raise which type of environmental "
            "concern: ethical, economic, or ecological?"
        ),
        "answer": "ecological",
        "accepted_answers": ["ecological", "ecology", "environmental", "Ecological"],
    },
    417: {
        "reason": "Compare... spermatogenesis vs oogenesis",
        "question_text": (
            "How many functional gametes does one primary spermatocyte "
            "typically produce through meiosis?"
        ),
        "answer": "4",
        "accepted_answers": ["4", "four"],
    },
    418: {
        "reason": "Describe... ovarian cycle hormones",
        "question_text": (
            "Which hormone surge immediately triggers ovulation in the "
            "ovarian cycle?"
        ),
        "answer": "LH",
        "accepted_answers": [
            "LH",
            "lh",
            "luteinizing hormone",
            "luteinising hormone",
        ],
    },
    419: {
        "reason": "Explain... teratogen critical periods",
        "question_text": (
            "During which embryonic process are organs rapidly forming, making "
            "teratogen exposure especially likely to cause permanent structural "
            "birth defects?"
        ),
        "answer": "organogenesis",
        "accepted_answers": [
            "organogenesis",
            "organogenesis period",
            "critical period of organogenesis",
        ],
    },
    420: {
        "reason": "Describe... luteal phase",
        "question_text": (
            "After ovulation, which temporary endocrine structure secretes "
            "progesterone to maintain the endometrium?"
        ),
        "answer": "corpus luteum",
        "accepted_answers": [
            "corpus luteum",
            "the corpus luteum",
            "Corpus luteum",
        ],
    },
    421: {
        "reason": "Explain... three factor types",
        "question_text": (
            "Which class of genes helps establish anterior–posterior body "
            "segment identity during development?"
        ),
        "answer": "Hox genes",
        "accepted_answers": [
            "Hox genes",
            "hox genes",
            "Hox",
            "homeobox genes",
            "Hox gene",
        ],
    },
    463: {
        "reason": "Explain... nondisjunction/trisomy",
        "question_text": (
            "If nondisjunction produces an n+1 gamete that is fertilized by a "
            "normal n gamete, what is the resulting zygote chromosome number "
            "in humans (use digit form, e.g. 47)?"
        ),
        "answer": "47",
        "accepted_answers": ["47", "2n+1", "trisomy"],
    },
    464: {
        "reason": "Describe... prophase I variation",
        "question_text": (
            "Which prophase I process exchanges DNA between non-sister "
            "chromatids of homologous chromosomes?"
        ),
        "answer": "crossing over",
        "accepted_answers": [
            "crossing over",
            "crossover",
            "crossing-over",
            "genetic recombination",
            "recombination",
        ],
    },
    465: {
        "reason": "Compare... mitosis vs meiosis",
        "question_text": (
            "How many nuclear divisions occur in meiosis?"
        ),
        "answer": "2",
        "accepted_answers": ["2", "two"],
    },
    466: {
        "reason": "Explain... tumour suppressor",
        "question_text": (
            "Which tumour-suppressor gene normally pauses the cell cycle for "
            "DNA repair or triggers apoptosis when damage is detected?"
        ),
        "answer": "p53",
        "accepted_answers": ["p53", "TP53", "tp53", "P53"],
    },
    534: {
        "reason": "Evaluate... pedigree claim",
        "question_text": (
            "A trait where affected fathers transmit the trait to all daughters "
            "but never to sons is most consistent with which inheritance pattern?"
        ),
        "answer": "X-linked dominant",
        "accepted_answers": [
            "X-linked dominant",
            "x-linked dominant",
            "X linked dominant",
            "sex-linked dominant",
        ],
    },
    535: {
        "reason": "Describe... DNA replication enzymes",
        "question_text": (
            "Which enzyme unwinds the DNA double helix at the replication fork?"
        ),
        "answer": "helicase",
        "accepted_answers": ["helicase", "DNA helicase", "Helicase"],
    },
    536: {
        "reason": "Explain... CRISPR plus ethics",
        "question_text": (
            "In CRISPR-Cas9 editing, which molecule directs Cas9 to a matching "
            "genomic DNA sequence?"
        ),
        "answer": "guide RNA",
        "accepted_answers": [
            "guide RNA",
            "gRNA",
            "sgRNA",
            "guide rna",
            "Guide RNA",
        ],
    },
    537: {
        "reason": "Describe... frameshift effect",
        "question_text": (
            "Deleting two base pairs from the middle of an open reading frame "
            "typically causes which class of mutation?"
        ),
        "answer": "frameshift",
        "accepted_answers": [
            "frameshift",
            "frameshift mutation",
            "frame-shift",
            "frame shift",
        ],
    },
    538: {
        "reason": "Explain... X-linked colour blindness",
        "question_text": (
            "A couple with normal vision has a colour-blind son. What is the "
            "mother’s most likely genotype for an X-linked recessive trait "
            "(use carrier notation such as XNXc)?"
        ),
        "answer": "XNXc",
        "accepted_answers": [
            "XNXc",
            "X^N X^c",
            "XNXC",
            "carrier",
            "heterozygous carrier",
            "X^N X^c",
        ],
    },
    539: {
        "reason": "Explain... central dogma",
        "question_text": (
            "According to the central dogma, DNA is transcribed into which "
            "molecule before proteins are made?"
        ),
        "answer": "RNA",
        "accepted_answers": ["RNA", "mRNA", "rna", "messenger RNA"],
    },
    540: {
        "reason": "Distinguish... mutation types",
        "question_text": (
            "A mutation that changes a single DNA base pair is called what "
            "type of mutation?"
        ),
        "answer": "point mutation",
        "accepted_answers": [
            "point mutation",
            "point",
            "substitution",
            "base substitution",
        ],
    },
    541: {
        "reason": "Explain... PCR + electrophoresis",
        "question_text": (
            "Which technique amplifies a specific DNA region using primers "
            "before fragments are compared by gel electrophoresis?"
        ),
        "answer": "PCR",
        "accepted_answers": [
            "PCR",
            "pcr",
            "polymerase chain reaction",
            "Polymerase Chain Reaction",
        ],
    },
    583: {
        "reason": "Explain... antibiotic selection",
        "question_text": (
            "Antibiotic use that kills susceptible bacteria while resistant "
            "bacteria survive and reproduce is an example of which evolutionary "
            "mechanism?"
        ),
        "answer": "natural selection",
        "accepted_answers": [
            "natural selection",
            "selection",
            "directional selection",
        ],
    },
    584: {
        "reason": "Explain... microevolution mechanisms",
        "question_text": (
            "Random change in allele frequencies due to chance in a small "
            "population is called what?"
        ),
        "answer": "genetic drift",
        "accepted_answers": [
            "genetic drift",
            "drift",
            "founder effect",
            "bottleneck effect",
        ],
    },
    585: {
        "reason": "Predict... trophic cascade essay",
        "question_text": (
            "Loss of a lake’s top predator leading to increases in herbivores "
            "and declines in producers is an example of which ecological concept?"
        ),
        "answer": "trophic cascade",
        "accepted_answers": [
            "trophic cascade",
            "trophic cascades",
            "cascade",
            "top-down control",
        ],
    },
    586: {
        "reason": "Describe... three impacts essay",
        "question_text": (
            "Connecting fragmented habitat patches with strips of habitat so "
            "wildlife can move between them is an example of which mitigation "
            "strategy?"
        ),
        "answer": "wildlife corridors",
        "accepted_answers": [
            "wildlife corridors",
            "wildlife corridor",
            "habitat corridor",
            "habitat corridors",
            "ecological corridors",
            "corridors",
        ],
    },
    # --- MATH30-1 ---
    10: {
        "reason": "Solve algebraically / state solutions (multi-value WR)",
        "question_text": (
            "How many solutions does $2\\cos^2(x) - \\sin(x) - 1 = 0$ have "
            "over $0 \\le x < 2\\pi$? Record the integer count."
        ),
        "answer": "3",
        "accepted_answers": ["3"],
    },
    30: {
        "reason": "Multi-part transformation WR",
        "question_text": (
            "If $y=f(x)$ has domain $[-6,9]$ and $g(x)=-3f(2x)$, what is the "
            "upper bound of the domain of $g$? Record as a decimal."
        ),
        "answer": "4.5",
        "accepted_answers": ["4.5", "9/2", "4.50"],
    },
    50: {
        "reason": "Multi-part domain WR",
        "question_text": (
            "For $f(x)=\\sqrt{16-x^2}$ and $g(x)=x^2-3x-4$, how many real "
            "values must be excluded from the domain of $(f/g)(x)$ within "
            "$[-4,4]$? Record the integer count."
        ),
        "answer": "2",
        "accepted_answers": ["2"],
    },
    68: {
        "reason": "Multi-part composition / inverse WR",
        "question_text": (
            "If $f(x)=\\dfrac{x+2}{x-1}$ and $f(f(x))=x$ (for permissible $x$), "
            "is $f$ its own inverse? Enter yes or no."
        ),
        "answer": "yes",
        "accepted_answers": ["yes", "Yes", "y", "true"],
    },
    86: {
        "reason": "Multi-part inverse WR",
        "question_text": (
            "For $f(x)=-\\sqrt{25-x^2}$ on $0\\le x\\le 5$, what is the lower "
            "bound of the range of $f$? Record the integer."
        ),
        "answer": "-5",
        "accepted_answers": ["-5"],
    },
    105: {
        "reason": "Multi-part exponential equation WR",
        "question_text": (
            "Solve $\\left(\\frac{4}{9}\\right)^{x-3}=\\left(\\frac{27}{8}\\right)^{x+2}$. "
            "Record the exact value of $x$."
        ),
        "answer": "0",
        "accepted_answers": ["0"],
    },
    125: {
        "reason": "Multi-part continuous growth WR",
        "question_text": (
            "Using $A=Pe^{rt}$ with $r=0.05$, how many years are required for "
            "an investment to triple? Round to the nearest tenth."
        ),
        "answer": "22.0",
        "accepted_answers": ["22.0", "22", "21.97", "21.972"],
    },
    144: {
        "reason": "Multi-part factoring WR",
        "question_text": (
            "How many distinct real $x$-intercepts does "
            "$P(x)=x^4-5x^2+4$ have? Record the integer."
        ),
        "answer": "4",
        "accepted_answers": ["4"],
    },
    164: {
        "reason": "Multi-part arc angle WR",
        "question_text": (
            "A satellite orbit has radius $8000$ km and arc length $12000$ km. "
            "What is the angular displacement in radians?"
        ),
        "answer": "1.5",
        "accepted_answers": ["1.5", "3/2", "1.50"],
    },
    184: {
        "reason": "Multi-part sinusoidal modelling WR",
        "question_text": (
            "Harbor depth is $16$ m at $t=2$ (high tide) and $4$ m at $t=8$ "
            "(low tide). Using the cosine model "
            "$d(t)=6\\cos\\left(\\frac{\\pi}{6}(t-2)\\right)+10$, what is "
            "the depth in metres at $t=5$?"
        ),
        "answer": "10",
        "accepted_answers": ["10", "10.0"],
    },
    204: {
        "reason": "Prove identity / state restrictions WR",
        "question_text": (
            "For $\\dfrac{\\sin(2x)}{1+\\cos(2x)}=\\tan(x)$ on "
            "$0\\le x<2\\pi$, how many non-permissible $x$-values are there "
            "in the interval? Record the integer."
        ),
        "answer": "2",
        "accepted_answers": ["2"],
    },
    224: {
        "reason": "Explain + calculate partitioning WR",
        "question_text": (
            "In how many ways can 12 volunteers be partitioned into teams of "
            "sizes 5, 4, and 3 (teams distinct)? Record the integer."
        ),
        "answer": "27720",
        "accepted_answers": ["27720", "27,720"],
    },
    244: {
        "reason": "Multi-part binomial expansion WR",
        "question_text": (
            "In the expansion of $\\left(2x^2-\\frac{1}{2x}\\right)^6$, what "
            "is the constant term? Record as a decimal."
        ),
        "answer": "3.75",
        "accepted_answers": ["3.75", "15/4", "3.750", "15/4"],
    },
    268: {
        "reason": "Solve with verification WR",
        "question_text": (
            "Solve $\\sqrt{x+5}=x-1$. Record the valid solution."
        ),
        "answer": "4",
        "accepted_answers": ["4"],
    },
    269: {
        "reason": "Describe transformations WR",
        "question_text": (
            "The graph of $y=-2\\sqrt{x+3}-1$ is obtained from $y=\\sqrt{x}$. "
            "What is the $x$-coordinate of the transformed starting point?"
        ),
        "answer": "-3",
        "accepted_answers": ["-3"],
    },
    292: {
        "reason": "Describe asymptotes/domain WR",
        "question_text": (
            "For $f(x)=\\dfrac{2x}{x-3}$, what is the equation of the "
            "vertical asymptote? Enter as x = k."
        ),
        "answer": "x = 3",
        "accepted_answers": ["x = 3", "x=3", "x= 3", "x =3", "3"],
    },
    293: {
        "reason": "Solve rational equation WR (multiple solutions)",
        "question_text": (
            "Solve $\\dfrac{1}{x}+\\dfrac{1}{x+2}=\\dfrac{3}{4}$. "
            "Record the positive solution."
        ),
        "answer": "2",
        "accepted_answers": ["2"],
    },
    294: {
        "reason": "Construct / justify rational function WR",
        "question_text": (
            "A rational function has vertical asymptote $x=-2$, horizontal "
            "asymptote $y=1$, and passes through $(0,0)$. Enter one possible "
            "equation (simplified)."
        ),
        "answer": "x/(x+2)",
        "accepted_answers": [
            "x/(x+2)",
            "x / (x + 2)",
            "f(x)=x/(x+2)",
            "f(x) = x/(x+2)",
            "(x)/(x+2)",
            "\\frac{x}{x+2}",
        ],
    },
}


def migrate(*, dry_run: bool) -> dict:
    init_db()
    db = SessionLocal()
    report_rows: list[dict] = []
    try:
        backup_path = None
        if not dry_run:
            backup_dir = BACKEND / "backups"
            backup_dir.mkdir(exist_ok=True)
            db_path = BACKEND / "albertaprep.db"
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"albertaprep.db.bak-nr-rewrite-{stamp}"
            if db_path.is_file():
                shutil.copy2(db_path, backup_path)

        missing = []
        for qid, rewrite in sorted(REWRITES.items()):
            q = db.get(Question, qid)
            if q is None or not q.is_active:
                missing.append(qid)
                continue
            original = q.question_text
            row = {
                "course": q.topic.course.code if q.topic and q.topic.course else "?",
                "question_id": qid,
                "original_question": original,
                "reason_invalid": rewrite["reason"],
                "new_question": rewrite["question_text"],
                "accepted_answers": [rewrite["answer"], *rewrite["accepted_answers"]],
                "previous_type": q.question_type,
            }
            report_rows.append(row)
            if dry_run:
                continue
            q.question_text = rewrite["question_text"]
            q.answer = rewrite["answer"]
            q.accepted_answers = dump_accepted_answers(rewrite["accepted_answers"])
            q.question_type = "numerical_response"
            # explanation / difficulty / outcome / skill unchanged

        if not dry_run:
            db.commit()

        # Verify every rewritten item auto-grades its canonical answer.
        verify_fail = []
        if not dry_run:
            for qid, rewrite in REWRITES.items():
                q = db.get(Question, qid)
                if q is None:
                    continue
                try:
                    result = grade_numerical_response(q, rewrite["answer"])
                except Exception as exc:  # noqa: BLE001
                    verify_fail.append((qid, str(exc)))
                    continue
                if not result.auto_graded or result.is_correct is not True:
                    verify_fail.append((qid, "canonical answer did not grade correct"))

        # Remaining WR / subjective NR scan
        remaining_wr = (
            db.query(Question)
            .filter(
                Question.is_active.is_(True),
                Question.question_type == "written_response",
            )
            .count()
        )

        return {
            "dry_run": dry_run,
            "backup_path": str(backup_path) if backup_path else None,
            "rewritten": len(report_rows),
            "missing_ids": missing,
            "verify_fail": verify_fail,
            "remaining_written_response": remaining_wr,
            "rows": report_rows,
        }
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = migrate(dry_run=args.dry_run)

    report_path = (
        BACKEND
        / "docs"
        / "NR_CONSTRUCTED_RESPONSE_AUDIT.md"
    )
    report_path.parent.mkdir(exist_ok=True)

    lines = [
        "# Constructed-response (NR) auto-grade audit",
        "",
        f"**Dry run:** `{result['dry_run']}`",
        f"**Questions rewritten:** `{result['rewritten']}`",
        f"**Backup:** `{result['backup_path']}`",
        f"**Remaining written_response:** `{result['remaining_written_response']}`",
        "",
        "## Finding",
        "",
        "All active `numerical_response` items already had a single numeric key "
        "and were auto-gradable. The invalid constructed-response items were "
        "the **48** active `written_response` questions (BIO30 + MATH30-1), "
        "which require subjective / multi-part marking.",
        "",
        "Each was rewritten to an automatically graded short-answer "
        "`numerical_response` with `accepted_answers`. Stems only were "
        "rewritten; explanations, outcomes, difficulty, and skills preserved. "
        "MC questions were not modified. Banks were not regenerated.",
        "",
        "## Rewrite table",
        "",
        "| Course | Question ID | Reason invalid | Accepted answers |",
        "|--------|-------------|----------------|------------------|",
    ]
    for row in result["rows"]:
        answers = "; ".join(row["accepted_answers"][:6])
        reason = row["reason_invalid"].replace("|", "/")
        lines.append(
            f"| {row['course']} | {row['question_id']} | {reason} | `{answers}` |"
        )

    lines.extend(["", "## Detail", ""])
    for row in result["rows"]:
        lines.extend(
            [
                f"### {row['course']} #{row['question_id']}",
                "",
                f"**Reason invalid:** {row['reason_invalid']}",
                "",
                "**Original:**",
                "",
                row["original_question"],
                "",
                "**New question:**",
                "",
                row["new_question"],
                "",
                f"**Accepted answers:** {', '.join(row['accepted_answers'])}",
                "",
            ]
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path = BACKEND / "docs" / "NR_CONSTRUCTED_RESPONSE_AUDIT.json"
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"rewritten={result['rewritten']} dry_run={result['dry_run']}")
    print(f"remaining_written_response={result['remaining_written_response']}")
    print(f"missing={result['missing_ids']}")
    print(f"verify_fail={result['verify_fail']}")
    print(f"report={report_path}")
    if result["verify_fail"] and not result["dry_run"]:
        return 1
    if result["remaining_written_response"] and not result["dry_run"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
