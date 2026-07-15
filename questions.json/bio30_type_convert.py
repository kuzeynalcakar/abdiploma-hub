"""Convert Biology 30 question types per Alberta diploma best practices.

Does not generate new questions — reclassifies existing items and rewrites
stems only where needed for the new format. Preserves outcome codes, topics,
difficulty, and curriculum coverage.
"""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "biology30_questions_final.json"
OUTPUT = HERE / "biology30_questions_final.json"
REPORT = HERE / "bio30_type_conversion_report.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

ORDER_PATTERN = re.compile(
    r"\b(order|place the following|place .+ in order|arrange)\b", re.I
)
NUMBERED_ITEM = re.compile(r"\((\d+)\)\s*([^(),]+?)(?=\s*\(\d+\)|\s*\.|\s*Record|\s*Write|$)")

# Explicit index sets (verified by audit)
SEQUENCE_NR_INDICES = {
    41, 42, 46, 49, 50, 51, 54, 58, 106, 108, 109, 110, 113, 118,
    158, 162, 229, 235, 237,
}
FAKE_CONCAT_NR_INDICES = {37, 38, 43}
FAKE_LABEL_NR_INDICES = {44, 116}
MC_TO_NR_INDICES = {173, 180, 191}
MC_TO_WR_INDICES = {76}


def _parse_numbered_items(text: str) -> dict[int, str]:
    items: dict[int, str] = {}
    for match in NUMBERED_ITEM.finditer(text):
        num = int(match.group(1))
        label = match.group(2).strip().rstrip(".,;")
        items[num] = label
    return items


def _decode_sequence(answer: str, items: dict[int, str]) -> list[str]:
    order = []
    for ch in str(answer).strip():
        if ch.isdigit():
            idx = int(ch)
            if idx in items:
                order.append(items[idx])
    return order


def _marking_guide_sequence(correct: list[str]) -> str:
    parts = [f"({i + 1}) {step}" for i, step in enumerate(correct)]
    return (
        "Marking guide: Award 1 mark per correctly placed step (4 marks total). "
        "Accept equivalent wording. Correct order: "
        + " → ".join(parts)
        + "."
    )


def _to_written(
    q: dict,
    *,
    question_text: str,
    model_answer: str,
    marking_guide: str,
    common_mistake: str | None = None,
    estimated_time_seconds: int | None = None,
) -> dict:
    out = deepcopy(q)
    out["question_type"] = "Written Response"
    out["question_text"] = question_text
    out["answer"] = model_answer.strip()
    out["choices"] = []
    out["explanation"] = marking_guide.strip()
    if common_mistake:
        out["common_mistake"] = common_mistake.strip()
    if estimated_time_seconds:
        out["estimated_time_seconds"] = estimated_time_seconds
    return out


def _to_numerical(q: dict, *, answer: str, question_text: str | None = None) -> dict:
    out = deepcopy(q)
    out["question_type"] = "Numerical Response"
    out["answer"] = str(answer).strip().strip("%")
    out["choices"] = []
    if question_text:
        out["question_text"] = question_text
    return out


def convert_sequence_nr(index: int, q: dict) -> tuple[dict, str]:
    items = _parse_numbered_items(q["question_text"])
    ordered = _decode_sequence(str(q["answer"]), items)
    if not ordered:
        ordered = [str(q["answer"])]

    # Rewrite stem for constructed response
    item_list = "; ".join(f"({k}) {v}" for k, v in sorted(items.items()))
    new_text = (
        q["question_text"]
        .split("Record")[0]
        .split("Write")[0]
        .strip()
        .rstrip(".")
    )
    if not ORDER_PATTERN.search(new_text):
        new_text = f"Place the following events in the correct order: {item_list}"
    else:
        new_text = (
            new_text.replace("Record all four digits of your answer.", "")
            .replace("Record all four digits.", "")
            .strip()
        )
        new_text += ". Write the correct sequence using the event names."

    model = " → ".join(ordered)
    guide = _marking_guide_sequence(ordered)
    mistake = (
        q.get("common_mistake")
        or "Students memorize labels but cannot state the biological sequence in words."
    )
    return (
        _to_written(
            q,
            question_text=new_text,
            model_answer=model,
            marking_guide=guide,
            common_mistake=mistake,
            estimated_time_seconds=max(q.get("estimated_time_seconds", 120), 180),
        ),
        "sequencing cannot be assessed as a numeric code — requires written sequence",
    )


def convert_fake_concat_nr(index: int, q: dict) -> tuple[dict, str]:
    text = q["question_text"]
    if "membrane potential" in text.lower():
        nums = re.findall(r"\$?(-?\d+)\$?", text)
        new_text = (
            f"A neuron has resting membrane potential ${nums[0]}$ mV and peak "
            f"depolarization ${nums[1]}$ mV during an action potential. "
            "State both values with units."
            if len(nums) >= 2
            else (
                "State the resting membrane potential and peak depolarization "
                "with units for the neuron described in the stem."
            )
        )
        if len(nums) >= 2:
            model = (
                f"Resting membrane potential: {nums[0]} mV; "
                f"peak depolarization: {nums[1]} mV"
            )
        else:
            model = q.get("explanation", "").split(".")[0]
    elif "heart rate" in text.lower():
        new_text = (
            "For the patient described, state the resting heart rate (beats/min) "
            "and the heart rate immediately after exercise (beats/min)."
        )
        nums = re.findall(r"\$(\d+)\$?", text)
        model = (
            f"Resting heart rate: {nums[0]} beats/min; post-exercise heart rate: {nums[1]} beats/min"
            if len(nums) >= 2
            else str(q["answer"])
        )
    else:
        new_text = text.split("Record")[0].strip() + " State all required values with units."
        model = q.get("explanation", "See marking guide.").split(".")[0]

    guide = (
        "Marking guide: 2 marks for each correctly stated value with correct unit "
        "(4 marks total). Accept values as stated in the stem if numerically correct."
    )
    return (
        _to_written(
            q,
            question_text=new_text,
            model_answer=model,
            marking_guide=guide,
            common_mistake=q.get(
                "common_mistake",
                "Students concatenate digits instead of reporting separate measurements with units.",
            ),
            estimated_time_seconds=max(q.get("estimated_time_seconds", 90), 150),
        ),
        "concatenated digit encoding is not a valid numerical response",
    )


def convert_fake_label_nr(index: int, q: dict) -> tuple[dict, str]:
    if "receptor" in q["question_text"].lower():
        items = _parse_numbered_items(q["question_text"])
        correct_idx = int(str(q["answer"]).strip())
        name = items.get(correct_idx, "photoreceptor")
        new_text = (
            "Identify which sensory receptor type detects light. "
            f"Options provided: {', '.join(items.values())}."
        )
        model = name
        guide = (
            "Marking guide: 2 marks for correct receptor name. "
            "1 mark partial credit for correct category (photoreceptor) with imprecise wording."
        )
        reason = "single-label digit code is not an objective NR value"
    else:
        items = _parse_numbered_items(q["question_text"])
        correct_idx = int(str(q["answer"]).strip())
        name = items.get(correct_idx, "ectoderm")
        new_text = (
            "Which embryonic germ layer forms nervous tissue? "
            "Name the layer and one example tissue formed by a different germ layer."
        )
        model = (
            f"Nervous tissue forms from the {name.split('—')[0].strip() if '—' in name else name}. "
            "For example, gut lining forms from endoderm and muscle from mesoderm."
        )
        guide = (
            "Marking guide: (1) Correct germ layer for nervous tissue — 2 marks. "
            "(2) Valid example tissue from another layer — 2 marks."
        )
        reason = "germ-layer identification requires constructed response, not a label digit"

    return (
        _to_written(
            q,
            question_text=new_text,
            model_answer=model,
            marking_guide=guide,
            common_mistake=q.get(
                "common_mistake",
                "Students report option numbers instead of biological structure names.",
            ),
            estimated_time_seconds=max(q.get("estimated_time_seconds", 80), 150),
        ),
        reason,
    )


def convert_mc_to_nr(index: int, q: dict) -> tuple[dict, str]:
    ans = str(q["answer"]).strip().strip("%")
    if ans.endswith("%"):
        ans = ans[:-1]
    try:
        float(ans)
    except ValueError:
        ans = ans.replace("%", "")
    new_text = q["question_text"]
    if "Record" not in new_text and "?" not in new_text:
        new_text = new_text.rstrip(".") + "."
    return (
        _to_numerical(q, answer=ans, question_text=new_text),
        "objective probability/percentage has a single numeric answer — NR format appropriate",
    )


def convert_mc_to_wr_sts(index: int, q: dict) -> tuple[dict, str]:
    correct = q["answer"]
    distractors = [c["text"] for c in q.get("choices", []) if not c.get("is_correct")]
    new_text = (
        "Discuss one significant science-technology-society (STS) concern raised by "
        "somatic cell nuclear transfer (reproductive cloning)."
    )
    model = correct
    if not model.endswith("."):
        model += (
            " Additional valid concerns include impacts on genetic diversity, "
            "commercialization of human tissues, and uncertainty about long-term health outcomes."
        )
    guide = (
        "Marking guide: (1) Identifies a valid STS concern — 2 marks. "
        "(2) Explains why it matters to society/ethics — 3 marks. "
        "Award partial credit for relevant concerns not listed in the model answer."
    )
    mistake = (
        q.get("common_mistake")
        or f"Students confuse cloning concerns with unrelated issues such as: {distractors[0] if distractors else 'gene therapy'}."
    )
    return (
        _to_written(
            q,
            question_text=new_text,
            model_answer=model,
            marking_guide=guide,
            common_mistake=mistake,
            estimated_time_seconds=max(q.get("estimated_time_seconds", 110), 240),
        ),
        "STS concern requires discussion/evaluation — not multiple choice selection",
    )


def convert_question(index: int, q: dict) -> tuple[dict, str | None, str | None]:
    old = q["question_type"]
    if index in SEQUENCE_NR_INDICES and q["question_type"] == "Numerical Response":
        new, reason = convert_sequence_nr(index, q)
        return new, old, reason
    if index in FAKE_CONCAT_NR_INDICES and q["question_type"] == "Numerical Response":
        new, reason = convert_fake_concat_nr(index, q)
        return new, old, reason
    if index in FAKE_LABEL_NR_INDICES and q["question_type"] == "Numerical Response":
        new, reason = convert_fake_label_nr(index, q)
        return new, old, reason
    if index in MC_TO_NR_INDICES and q["question_type"] == "Multiple Choice":
        new, reason = convert_mc_to_nr(index, q)
        return new, old, reason
    if index in MC_TO_WR_INDICES and q["question_type"] == "Multiple Choice":
        new, reason = convert_mc_to_wr_sts(index, q)
        return new, old, reason
    return q, None, None


def main() -> None:
    items = json.loads(INPUT.read_text(encoding="utf-8"))
    changes: list[dict] = []
    converted: list[dict] = []

    for index, q in enumerate(items):
        new_q, old_type, reason = convert_question(index, q)
        converted.append(new_q)
        if old_type:
            changes.append(
                {
                    "index": index,
                    "topic": q["topic"],
                    "outcome_code": q["outcome_code"],
                    "from": old_type,
                    "to": new_q["question_type"],
                    "reason": reason,
                    "question_text": q["question_text"][:120],
                }
            )

    # Validate all
    invalid = []
    for index, item in enumerate(converted):
        reasons = validate_question(item, index)
        if reasons:
            invalid.append((index, reasons))

    if invalid:
        print("VALIDATION FAILED:")
        for index, reasons in invalid[:20]:
            print(f"  [{index}] {reasons}")
        raise SystemExit(1)

    from collections import Counter

    counts = Counter(q["question_type"] for q in converted)
    report = {
        "total": len(converted),
        "counts_after": dict(counts),
        "changes": changes,
    }

    INPUT.write_text(
        json.dumps(converted, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Conversion complete.")
    print("Counts:", dict(counts))
    print(f"Changed: {len(changes)}")
    for c in changes:
        print(f"  [{c['index']}] {c['from']} -> {c['to']}: {c['reason']}")


if __name__ == "__main__":
    main()
