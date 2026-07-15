"""Pass-2 student polish: diploma stem style + residual weak distractors."""
from __future__ import annotations

import json
import re
from pathlib import Path

QDIR = Path(__file__).resolve().parents[2] / "questions.json"
BANK = QDIR / "science10_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"


def fix_blank_question_mark(stem: str) -> str:
    """Convert awkward '_______?' completions into incomplete diploma stems."""
    # trailing blank + ?
    stem = re.sub(r"\s*_{3,}\s*\?\s*$", "", stem)
    # blank then ? mid-stem unlikely; also blank at end with no ?
    stem = re.sub(r"\s*_{3,}\s*$", "", stem)
    return stem.strip()


def main() -> int:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    log = []

    # 1) Diploma-style incomplete stems
    n = 0
    for q in bank:
        old = q["question_text"]
        new = fix_blank_question_mark(old)
        if new != old:
            q["question_text"] = new
            n += 1
    log.append(f"reformatted {n} blank+? stems to incomplete diploma style")

    # 2) Residual chromosome-flavoured distractors that still read as jokes
    patches = {
        211: [
            "increases without limit, so exchange improves indefinitely",
            "stays exactly constant no matter how large the cell becomes",
            "depends only on whether the cell is animal or plant, not on size",
        ],
        218: [
            "forming the spindle that pulls sister chromatids apart in mitosis",
            "capturing light energy to produce carbohydrates",
            "generating root-hair turgor by storing starch only",
        ],
        281: [
            "only the brand colour printed on the device casing",
            "the atomic number of metals used in the casing",
            "unchanging physical constants such as the speed of light",
        ],
    }
    for idx, wrongs in patches.items():
        q = bank[idx]
        correct = next(c["text"] for c in q["choices"] if c["is_correct"])
        q["choices"] = [{"text": correct, "is_correct": True}] + [
            {"text": w, "is_correct": False} for w in wrongs
        ]
        q["answer"] = correct
        log.append(f"{idx}: polished residual distractors")

    # 3) Soften remaining stock-market / attendance style if any leftover
    silly = re.compile(
        r"(stock market|classroom attendance|recite chromosome|speed of light in vacuum exclusively)",
        re.I,
    )
    leftovers = []
    for i, q in enumerate(bank):
        for c in q.get("choices", []):
            if not c.get("is_correct") and silly.search(c["text"]):
                leftovers.append((i, c["text"]))
    if leftovers:
        log.append(f"WARNING leftover silly: {leftovers}")

    text = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    BANK.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")
    for line in log:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
