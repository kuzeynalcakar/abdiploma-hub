"""Resolve remaining BIO30 text mismatches and fix boilerplate explanations.

Maps production question IDs to JSON entries by semantic fragment.
Preserves question IDs, text, and answers where DB format differs from JSON.
Updates explanations, common_mistake, and curriculum metadata.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "biology30_questions_final.json"
PROD_DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
BACKUP_DIR = Path(__file__).resolve().parents[1] / "backups"

# DB question_id -> JSON lookup fragment (unique within BIO30 JSON)
JSON_LOOKUP = {
    333: "increase in heart rate (beats/min)",
    338: "resting membrane potential of $-72$ mV",
    339: "Which sensory receptor type detects light",
    371: "science-technology-society (STS) concern raised by somatic cell nuclear transfer",
    475: "Cystic fibrosis is autosomal recessive. Two carrier parents",
    486: "dihybrid testcross AaBb",
}

# Custom content for DB-specific question formats (not in JSON verbatim)
CUSTOM_CONTENT = {
    332: {
        "explanation": (
            "Resting membrane potential is −70 mV; record the magnitude as two digits: 70. "
            "During depolarization the membrane peaks at +40 mV; record as two digits: 40. "
            "Concatenate resting then peak in order: 7040."
        ),
        "common_mistake": (
            "Students reverse digit order, subtract incorrectly, or record only one value "
            "instead of both resting and peak magnitudes."
        ),
        "outcome_code": "A1.1k",
        "skill_tested": "Recording membrane potential values as two-digit codes",
    },
    411: {
        "explanation": (
            "Nervous tissue—including the brain, spinal cord, and peripheral nerves—"
            "develops from ectoderm (layer 2). Mesoderm (1) forms muscle and bone; "
            "endoderm (3) forms the lining of the digestive tract."
        ),
        "common_mistake": (
            "Students confuse ectoderm (nervous system and epidermis) with mesoderm "
            "(muscle, bone, circulatory system) or endoderm (gut lining)."
        ),
        "outcome_code": "B2.1k",
        "skill_tested": "Identifying embryonic germ layer derivatives",
    },
    339: {
        "explanation": (
            "Photoreceptors (1) in the retina detect light energy and transduce it into "
            "neural signals. Mechanoreceptors in the cochlea (2) detect sound; "
            "chemoreceptors (3) detect taste; nociceptors (4) detect pain."
        ),
        "common_mistake": (
            "Students confuse photoreceptors with mechanoreceptors (sound) or "
            "chemoreceptors (taste/smell)."
        ),
        "outcome_code": "A1.6k",
        "skill_tested": "Matching receptors to stimuli",
    },
}


def load_json_items() -> list[dict]:
    return [i for i in json.loads(JSON_PATH.read_text(encoding="utf-8")) if i.get("course_code") == "BIO30"]


def find_json(items: list[dict], fragment: str) -> dict | None:
    for item in items:
        if fragment.lower() in item["question_text"].lower():
            return item
    return None


def backup() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_bio30_polish_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    return dest


def main() -> int:
    items = load_json_items()
    backup_path = backup()
    conn = sqlite3.connect(PROD_DB)
    conn.row_factory = sqlite3.Row
    updated = []
    unchanged = []

    def update_row(qid: int, fields: dict) -> None:
        row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if not row:
            print(f"SKIP missing Q{qid}")
            return
        changes = {}
        for field, value in fields.items():
            if field not in ("explanation", "common_mistake", "unit", "outcome_code", "skill_tested"):
                continue
            current = row[field] if field in row.keys() else None
            if (current or "").strip() != (value or "").strip():
                changes[field] = value
        if changes:
            sets = ", ".join(f"{k} = ?" for k in changes)
            conn.execute(
                f"UPDATE questions SET {sets} WHERE id = ?",
                (*changes.values(), qid),
            )
            updated.append((qid, list(changes.keys())))
        else:
            unchanged.append(qid)

    # Custom fixes
    for qid, fields in CUSTOM_CONTENT.items():
        update_row(qid, fields)

    # JSON-paired metadata and explanations
    for qid, fragment in JSON_LOOKUP.items():
        json_item = find_json(items, fragment)
        if not json_item:
            print(f"WARN no JSON for Q{qid} fragment {fragment!r}")
            continue
        fields = {
            "unit": json_item.get("unit"),
            "outcome_code": json_item.get("outcome_code"),
            "skill_tested": json_item.get("skill_tested"),
        }
        row = conn.execute("SELECT explanation FROM questions WHERE id = ?", (qid,)).fetchone()
        expl = (row["explanation"] or "") if row else ""
        if expl.startswith("The correct answer is"):
            fields["explanation"] = json_item.get("explanation")
            fields["common_mistake"] = json_item.get("common_mistake")
        elif qid in (475, 486):
            # Align MC explanations with JSON reasoning while keeping MC answer format
            if json_item.get("explanation"):
                fields["explanation"] = json_item["explanation"]
            if json_item.get("common_mistake"):
                fields["common_mistake"] = json_item["common_mistake"]
        elif qid == 371:
            fields["explanation"] = (
                "Cloning debates involve identity, consent, personhood, and societal "
                "implications beyond pure biology. Valid STS concerns include impacts on "
                "genetic diversity, commercialization of human tissues, and uncertainty "
                "about long-term health outcomes."
            )
            fields["common_mistake"] = (
                "Students list technical steps without explaining why society should care."
            )
        update_row(qid, fields)

    conn.commit()

    boiler = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'BIO30' AND q.explanation LIKE 'The correct answer is%'
        """
    ).fetchone()[0]

    print(f"Backup: {backup_path}")
    print(f"Updated: {len(updated)} questions")
    for qid, fields in updated:
        print(f"  Q{qid}: {', '.join(fields)}")
    print(f"Unchanged in this pass: {len(unchanged)}")
    print(f"Remaining boilerplate explanations: {boiler}")
    conn.close()
    return 0 if boiler == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
