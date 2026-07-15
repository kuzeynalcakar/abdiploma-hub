"""Deep student-perspective review: dump suspicious patterns and verify keys."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BANK = Path(__file__).resolve().parents[2] / "questions.json" / "science10_questions_final.json"


def main() -> None:
    d = json.loads(BANK.read_text(encoding="utf-8"))
    findings: dict[str, list] = defaultdict(list)

    # --- Confirmed calc / wording bugs ---
    for i, q in enumerate(d):
        t = q["question_text"]
        low = t.lower()

        # Stem says lake "absorbs" but treats value as incoming
        if "lake absorbs" in low and "reflected" in low:
            findings["misleading_wording_incoming_called_absorbs"].append(
                (i, t, q["answer"])
            )

        # Photosynthesis stoichiometry spot checks if present
        if "photosynthesis" in low and "glucose" in low and q["question_type"] == "Numerical Response":
            findings["review_photosynthesis_nr"].append((i, t, q["answer"]))

    # --- MC: correct choice identical meaning to another choice ---
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        texts = [c["text"].strip().lower() for c in q["choices"]]
        if len(texts) != len(set(texts)):
            findings["duplicate_choice_text"].append((i, texts))

    # --- Silly / off-topic distractors (not diploma-caliber) ---
    SILLY = (
        "only the colour",
        "speed of light in vacuum",
        "number of chromosomes",
        "metallic grey",
        "all life requires sunlight",
        "dna carries genetic information",
        "operates exclusively on magnetic monopoles",
        "requires infinite energy",
        "none of the above",
        "all of the above",
        "cannot be determined from any information",
    )
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        for c in q["choices"]:
            if c.get("is_correct"):
                continue
            low = c["text"].lower()
            if any(s in low for s in SILLY):
                findings["silly_distractor"].append((i, c["text"], q["question_text"][:70]))
            # distractors that are Wikipedia factoids unrelated to stem topic cues
            if "chromosome" in low and "chromosom" not in q["question_text"].lower():
                findings["offtopic_chromosome_distractor"].append((i, c["text"]))

    # --- Meta / AI leakage remaining ---
    for i, q in enumerate(d):
        for field in ("explanation", "common_mistake", "skill_tested", "question_text"):
            val = q.get(field) or ""
            low = val.lower()
            if re.search(r"\boutcome\s+[A-D]", val):
                findings["meta_outcome_ref"].append((i, field, val))
            if "alberta science 10" in low:
                findings["meta_alberta_prefix"].append((i, field, val))
            if re.search(r"item\s+\d+", low):
                findings["meta_item_number"].append((i, field, val))
            if low.startswith(("checkpoint:", "review:")):
                findings["meta_prefix"].append((i, field, val))

    # --- Answer length tell ---
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        corr = [c for c in q["choices"] if c.get("is_correct")]
        bad = [c for c in q["choices"] if not c.get("is_correct")]
        if not corr or not bad:
            continue
        clen = len(corr[0]["text"])
        maxlen_bad = max(len(x["text"]) for x in bad)
        if clen >= 70 and clen > 1.8 * maxlen_bad:
            findings["answer_length_tell"].append(
                (i, clen, maxlen_bad, q["question_text"][:60], corr[0]["text"][:80])
            )

    # --- Near-template skeletons (3+) ---
    skel = defaultdict(list)
    for i, q in enumerate(d):
        s = q["question_text"].lower()
        s = re.sub(r"\$[^$]*\$", " ", s)
        s = re.sub(r"\d+(?:\.\d+)?", "#", s)
        s = re.sub(r"[^a-z# ]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        skel[s].append(i)
    for s, idxs in skel.items():
        if len(idxs) >= 3:
            findings["template_family_3plus"].append((len(idxs), idxs, s[:90]))

    # --- Efficiency wording: percent instructed, answer looks like fraction ---
    for i, q in enumerate(d):
        if q["question_type"] != "Numerical Response":
            continue
        low = q["question_text"].lower()
        try:
            ans = float(q["answer"])
        except (TypeError, ValueError):
            continue
        if "efficiency" in low and ("percent" in low or "percentage" in low):
            if 0 < ans <= 1:
                findings["efficiency_key_as_fraction"].append((i, ans, q["question_text"][:90]))

    # --- Blank+? awkward stems (flag for reword, not auto-fail) ---
    awkward = 0
    for i, q in enumerate(d):
        t = q["question_text"]
        if "_______?" in t.replace(" ", ""):
            awkward += 1
    findings["blank_question_mark_count"] = [("count", awkward)]

    # --- Spot-check known Science 10 misconceptions / factual traps ---
    for i, q in enumerate(d):
        low = q["question_text"].lower()
        # photosynthesis product wrong key?
        if "photosynthesis" in low and q["question_type"] == "Multiple Choice":
            corr = next((c["text"] for c in q["choices"] if c.get("is_correct")), "")
            findings["photosynthesis_mc"].append((i, q["question_text"][:90], corr))
        # phenolphthalein colour
        if "phenolphthalein" in low:
            corr = next((c["text"] for c in q["choices"] if c.get("is_correct")), "")
            findings["phenolphthalein"].append((i, corr, q["question_text"]))
        # neutral pH
        if "neutral" in low and "ph" in low and q["question_type"] == "Multiple Choice":
            corr = next((c["text"] for c in q["choices"] if c.get("is_correct")), "")
            findings["neutral_ph"].append((i, corr))

    # --- Cross-stem near identical after number strip (dupe calc templates) ---
    for s, idxs in skel.items():
        if len(idxs) == 2:
            a, b = d[idxs[0]], d[idxs[1]]
            if a["answer"] == b["answer"] and a["question_type"] == b["question_type"]:
                # same skeleton + same answer = true dupe calc
                if a["question_type"] == "Numerical Response":
                    findings["near_dupe_nr_same_answer"].append(
                        (idxs, a["answer"], s[:80])
                    )

    print("=== FINDINGS SUMMARY ===")
    for k, v in sorted(findings.items(), key=lambda x: -len(x[1])):
        print(f"\n[{k}] x{len(v)}")
        for item in v[:40]:
            print(" ", item)


if __name__ == "__main__":
    main()
