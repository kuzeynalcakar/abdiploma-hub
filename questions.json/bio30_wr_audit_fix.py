"""Second WR audit: revert auto-gradable WR items to MC/NR; fix vague stems."""
from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent
BANK_PATH = HERE / "biology30_questions_final.json"
REPORT_PATH = HERE / "bio30_wr_audit_report.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

# WR items that are objectively sequenced — restore NR from pool content
SEQUENCE_RESTORE = {
    41: "During a knee-jerk reflex, place the following events in the correct chronological order:",
    42: "Order sound processing:",
    46: "Order light pathway:",
    49: "Place the following auditory pathway structures in the order sound travels",
    50: "Order insulin response to high blood glucose:",
    51: "During the pupillary light reflex, order these events:",
    54: "Order HPA axis:",
    58: "Order reflex arc signal:",
    106: "Order menstrual cycle phases:",
    108: "Order ovarian cycle:",
    109: "Order fertilization events:",
    110: "Order implantation events:",
    113: "Order sperm pathway structures after production:",
    118: "Order spermatogenesis:",
    158: "Order meiosis II stages:",
    162: "Order meiosis I stages:",
    229: "Order protein synthesis steps:",
    235: "Place DNA replication events in order:",
    237: "Order mRNA processing:",
}

# Stem-recall WR → single-value NR
CALC_NR = {
    37: {
        "question_text": (
            "A resting neuron has membrane potential $-70$ mV and peaks at $+40$ mV "
            "during depolarization. What is the magnitude of the depolarization change, in mV?"
        ),
        "answer": "110",
        "explanation": (
            "Change = peak minus resting = $+40 - (-70) = 110$ mV magnitude of depolarization."
        ),
        "common_mistake": "Students subtract in the wrong order or omit the sign change across zero.",
    },
    38: {
        "question_text": (
            "A patient has a resting heart rate of $68$ beats/min before exercise and "
            "$142$ beats/min immediately after sprinting. What is the increase in heart rate "
            "(beats/min)?"
        ),
        "answer": "74",
        "explanation": "Increase = $142 - 68 = 74$ beats/min.",
        "common_mistake": "Students report the post-exercise rate instead of the increase.",
    },
    43: {
        "question_text": (
            "A neuron has a resting membrane potential of $-72$ mV and reaches a peak "
            "depolarization of $+35$ mV during an action potential. What is the magnitude of "
            "the depolarization change, in mV?"
        ),
        "answer": "107",
        "explanation": "Change = $+35 - (-72) = 107$ mV.",
        "common_mistake": "Students add absolute values incorrectly or report only the peak value.",
    },
}

MC_RESTORE = {
    44: {
        "question_text": "Which sensory receptor type detects light?",
        "answer": "photoreceptor",
        "choices": [
            {"text": "photoreceptor", "is_correct": True},
            {"text": "mechanoreceptor in cochlea", "is_correct": False},
            {"text": "chemoreceptor for taste", "is_correct": False},
            {"text": "nociceptor", "is_correct": False},
        ],
        "explanation": "Photoreceptors in the retina transduce light energy into neural signals.",
        "common_mistake": "Cochlear hair cells are mechanoreceptors, not photoreceptors.",
    },
    116: {
        "question_text": "Which embryonic germ layer gives rise to nervous tissue?",
        "answer": "ectoderm",
        "choices": [
            {"text": "ectoderm", "is_correct": True},
            {"text": "mesoderm", "is_correct": False},
            {"text": "endoderm", "is_correct": False},
            {"text": "mesoderm and endoderm equally", "is_correct": False},
        ],
        "explanation": "Ectoderm differentiates into the nervous system and epidermis.",
        "common_mistake": "Students confuse mesoderm (muscle/bone) with ectoderm.",
    },
}


def _find_pool_item(pool: list[dict], fragment: str) -> dict | None:
    frag = fragment.lower()
    for item in pool:
        if frag in item["question_text"].lower():
            return item
    return None


def _to_nr(q: dict, pool_item: dict) -> dict:
    out = deepcopy(q)
    out["question_type"] = "Numerical Response"
    out["question_text"] = pool_item["question_text"]
    out["answer"] = str(pool_item["answer"])
    out["choices"] = []
    out["explanation"] = pool_item.get("explanation", q.get("explanation", ""))
    out["common_mistake"] = pool_item.get("common_mistake", q.get("common_mistake", ""))
    return out


def _apply_calc_nr(q: dict, spec: dict) -> dict:
    out = deepcopy(q)
    out["question_type"] = "Numerical Response"
    out["question_text"] = spec["question_text"]
    out["answer"] = spec["answer"]
    out["choices"] = []
    out["explanation"] = spec["explanation"]
    out["common_mistake"] = spec["common_mistake"]
    return out


def _apply_mc(q: dict, spec: dict) -> dict:
    out = deepcopy(q)
    out["question_type"] = "Multiple Choice"
    out["question_text"] = spec["question_text"]
    out["answer"] = spec["answer"]
    out["choices"] = deepcopy(spec["choices"])
    out["explanation"] = spec["explanation"]
    out["common_mistake"] = spec["common_mistake"]
    return out


def main() -> None:
    items = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    pool = json.loads((HERE / "biology30_questions_pool.json").read_text(encoding="utf-8"))

    wr_before = [i for i, q in enumerate(items) if q["question_type"] == "Written Response"]
    changes: list[dict] = []

    for index in wr_before:
        q = items[index]
        old_type = q["question_type"]

        if index in SEQUENCE_RESTORE:
            pool_item = _find_pool_item(pool, SEQUENCE_RESTORE[index])
            if not pool_item:
                raise RuntimeError(f"No pool match for index {index}")
            new_q = _to_nr(q, pool_item)
            reason = (
                "sequencing has one objectively correct order — auto-gradable as numerical response"
            )
        elif index in CALC_NR:
            new_q = _apply_calc_nr(q, CALC_NR[index])
            reason = (
                "single numeric answer derived from stem values — no written explanation required"
            )
        elif index in MC_RESTORE:
            new_q = _apply_mc(q, MC_RESTORE[index])
            reason = "single discrete term answer — multiple choice is appropriate"
        else:
            continue

        items[index] = new_q
        changes.append(
            {
                "index": index,
                "outcome_code": q["outcome_code"],
                "from": old_type,
                "to": new_q["question_type"],
                "reason": reason,
                "question_text": new_q["question_text"][:120],
            }
        )

    invalid = [(i, validate_question(q, i)) for i, q in enumerate(items) if validate_question(q, i)]
    if invalid:
        for i, reasons in invalid[:10]:
            print(f"INVALID [{i}]: {reasons}")
        raise SystemExit(1)

    from collections import Counter

    counts = Counter(q["question_type"] for q in items)
    report = {
        "wr_reviewed": len(wr_before),
        "wr_changed": len(changes),
        "wr_kept": len(wr_before) - len(changes),
        "counts_after": dict(counts),
        "changes": changes,
    }

    BANK_PATH.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"WR reviewed: {report['wr_reviewed']}")
    print(f"WR changed: {report['wr_changed']}")
    print(f"WR kept: {report['wr_kept']}")
    print("Final distribution:", dict(counts))


if __name__ == "__main__":
    main()
