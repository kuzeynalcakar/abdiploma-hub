"""Final student-audit confirmed fixes for SCI10 production bank.

Applies every confirmed issue from multi-pass student review.
Writes science10_questions_final.json and course_questions_final.json.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

QDIR = Path(__file__).resolve().parents[2] / "questions.json"
BANK = QDIR / "science10_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"


def set_mc(
    q: dict,
    *,
    stem: str | None = None,
    answer: str,
    wrongs: list[str],
    explanation: str,
    common_mistake: str,
    skill: str | None = None,
    outcome: str | None = None,
) -> None:
    if stem is not None:
        q["question_text"] = stem
    q["answer"] = answer
    q["choices"] = [{"text": answer, "is_correct": True}] + [
        {"text": w, "is_correct": False} for w in wrongs
    ]
    q["explanation"] = explanation
    q["common_mistake"] = common_mistake
    if skill:
        q["skill_tested"] = skill
    if outcome:
        q["outcome_code"] = outcome


def apply_all(bank: list[dict]) -> list[str]:
    log: list[str] = []

    # 243 — incoming energy mislabelled as absorbed
    bank[243]["question_text"] = (
        "A lake receives 1.5 × 10⁶ J of incoming solar energy. If 4.5 × 10⁵ J is reflected, "
        "what percentage of the incoming energy was absorbed? Record as an integer."
    )
    bank[243]["explanation"] = (
        "Absorbed energy = incoming − reflected = 1.5×10⁶ − 4.5×10⁵ = 1.05×10⁶ J. "
        "Percent absorbed = (1.05×10⁶ / 1.5×10⁶) × 100 = 70%."
    )
    bank[243]["common_mistake"] = (
        "Students report the reflected percentage (30%) instead of the absorbed percentage."
    )
    log.append("243: fixed incoming/absorbed wording (key 70 unchanged)")

    # 176 — protein hormones do not diffuse across membranes
    set_mc(
        bank[176],
        stem="Most protein hormones affect target cells primarily by _______?",
        answer="binding receptors on the cell surface and triggering internal signalling pathways",
        wrongs=[
            "diffusing freely through the phospholipid bilayer like steroid hormones",
            "being converted directly into ATP inside the nucleus",
            "passing unchanged through the cell wall into the vacuole",
        ],
        explanation=(
            "Protein hormones are typically water-soluble and cannot cross the phospholipid bilayer; "
            "they bind surface receptors that activate signalling pathways. Lipid-soluble steroid "
            "hormones can diffuse across membranes."
        ),
        common_mistake="Students confuse protein hormones with steroid hormones that diffuse into cells.",
        skill="Distinguishing membrane action of protein vs lipid-soluble hormones",
    )
    log.append("176: corrected protein-hormone membrane mechanism")

    # 173 — CLSM off-curriculum; replace with compound microscope
    set_mc(
        bank[173],
        stem="A compound light microscope is useful for studying cells because it?",
        answer=(
            "combines ocular and objective lenses to magnify thin specimens so cells "
            "and some organelles are visible"
        ),
        wrongs=[
            "resolves individual atoms inside the nucleus without any staining",
            "destroys all cellular membranes on contact with the slide",
            "replaces the need for any understanding of cell theory",
        ],
        explanation=(
            "Compound light microscopes multiply eyepiece and objective magnifications, allowing "
            "observation of cells, walls, nuclei, and chloroplasts in prepared slides."
        ),
        common_mistake="Students overestimate resolution (atoms) or think microscopes replace cell theory.",
        skill="Explaining the purpose of compound light microscopy",
        outcome="C1.2k",
    )
    log.append("173: replaced off-curriculum CLSM with compound microscope")

    # 109
    set_mc(
        bank[109],
        stem="Gravitational potential energy near Earth's surface depends on _______?",
        answer="mass, gravitational field strength, and vertical height",
        wrongs=[
            "horizontal distance travelled on level ground only",
            "the object's colour and surface texture only",
            "elapsed time since the object was manufactured",
        ],
        explanation="$E_p = mgh$ depends on mass, gravitational field strength $g$, and vertical height.",
        common_mistake="Students think horizontal path length on flat ground changes $E_p$.",
    )
    log.append("109: replaced non-diploma Ep distractors")

    # 201
    set_mc(
        bank[201],
        stem="Louis Pasteur's swan-neck flask experiments supported cell theory by demonstrating that?",
        answer="sterile broth stays free of microbes unless contaminated by airborne microorganisms",
        wrongs=[
            "all living organisms require continuous sunlight to survive",
            "every cell in every organism contains a membrane-bound nucleus",
            "heritable information is stored only as DNA double helices",
        ],
        explanation=(
            "Pasteur showed broth stayed sterile when microbes were trapped in the swan neck, "
            "refuting spontaneous generation and supporting that cells arise from existing cells."
        ),
        common_mistake="Students associate Pasteur with photosynthesis, eukaryotic nuclei, or DNA structure.",
    )
    log.append("201: rewrote Pasteur options")

    # 211
    set_mc(
        bank[211],
        stem="As a cell grows larger, its surface area to volume ratio generally?",
        answer="decreases, which can limit efficient exchange of materials across the membrane",
        wrongs=[
            "increases without limit, so exchange improves indefinitely",
            "stays exactly constant no matter how large the cell becomes",
            "increases only when the nucleus doubles its chromosome count",
        ],
        explanation="Volume increases faster than surface area, lowering SA:V and constraining membrane transport.",
        common_mistake="Students reverse the SA:V trend or incorrectly link it to chromosome number.",
    )
    log.append("211: removed off-topic chromosome distractor")

    # 214
    set_mc(
        bank[214],
        stem="Exocytosis is used by cells to _______?",
        answer="release materials such as proteins when vesicles fuse with the plasma membrane",
        wrongs=[
            "take up large volumes of water when placed in a hypertonic solution",
            "break down starch molecules inside the chloroplast stroma",
            "copy DNA molecules during the synthesis (S) phase of interphase",
        ],
        explanation="Secretory vesicles fuse with the plasma membrane and release contents outside the cell.",
        common_mistake="Students confuse exocytosis with endocytosis, osmosis, digestion, or DNA replication.",
    )
    log.append("214: improved exocytosis distractors")

    # 218
    set_mc(
        bank[218],
        stem="The endoplasmic reticulum (ER) is involved in _______?",
        answer="synthesizing lipids and proteins and transporting them within the cell",
        wrongs=[
            "separating duplicated chromosomes during mitosis",
            "capturing light energy to produce carbohydrates",
            "generating root-hair turgor by storing starch only",
        ],
        explanation="Rough ER synthesizes proteins; smooth ER synthesizes lipids and helps detoxify molecules.",
        common_mistake="Students assign mitosis, photosynthesis, or turgor roles to the ER.",
    )
    log.append("218: improved ER distractors")

    # 223
    set_mc(
        bank[223],
        stem="A plant cell in a hypertonic solution may undergo plasmolysis, which means _______?",
        answer="the cell membrane pulls away from the cell wall as water leaves by osmosis",
        wrongs=[
            "the rigid cell wall dissolves completely into the surrounding solution",
            "chloroplasts multiply rapidly to restore water balance",
            "the nucleus is forced out through pores in the cell wall",
        ],
        explanation="Water leaves by osmosis and the protoplast shrinks away from the intact wall.",
        common_mistake="Students think the wall dissolves or that organelles exit the cell.",
    )
    log.append("223: balanced plasmolysis distractors")

    # 281
    set_mc(
        bank[281],
        stem="When analyzing a technology from an economic STS perspective, efficiency mainly affects?",
        answer="operating costs, because less efficient devices use more energy for the same useful output",
        wrongs=[
            "only the brand colour printed on the device casing",
            "whether workers can recite chromosome numbers from memory",
            "unchanging physical constants such as the speed of light",
        ],
        explanation=(
            "Lower efficiency means more energy must be purchased for the same service, "
            "raising operating cost."
        ),
        common_mistake="Students separate efficiency from economic STS analysis of technology.",
        skill="Linking energy efficiency to economic STS analysis",
    )
    log.append("281: replaced absurd STS distractors")

    climate_fixes = {
        255: [
            "Earth's total water mass is increasing from nuclear reactions in seawater",
            "all rivers worldwide have permanently stopped reaching the ocean",
            "evaporation has permanently removed the entire ocean reservoir",
        ],
        256: [
            "the equator is millions of kilometres closer to the Sun every day",
            "polar ice eliminates all incoming solar radiation completely",
            "Earth's core heats only the equatorial atmosphere",
        ],
        258: [
            "clockwise and outward away from the centre only",
            "straight northward with no curvature at any latitude",
            "vertically downward into Earth's mantle as a lava flow",
        ],
        261: [
            "next week's daily weather forecasts with hour-by-hour detail",
            "current prices of stocks traded on global markets",
            "today's classroom attendance totals for every school",
        ],
        286: [
            "fixed forever after a single early experiment",
            "based only on untested opinions without measurement",
            "unrelated to technology or international cooperation",
        ],
    }
    for idx, wrongs in climate_fixes.items():
        q = bank[idx]
        correct = next(c["text"] for c in q["choices"] if c["is_correct"])
        q["choices"] = [{"text": correct, "is_correct": True}] + [
            {"text": w, "is_correct": False} for w in wrongs
        ]
        q["answer"] = correct
        log.append(f"{idx}: replaced silly climate/STS distractors")

    meta_cm = {
        9: "Students substitute incorrect values into the molar-mass or mole calculation.",
        28: "Students substitute incorrect values into the molar-mass or mole calculation.",
        90: "Students substitute incorrect values into the energy or efficiency calculation.",
    }
    for idx, text in meta_cm.items():
        bank[idx]["common_mistake"] = text
        log.append(f"{idx}: removed outcome-code meta from common_mistake")

    bank[108]["explanation"] = (
        "Energy is recognized when it is transferred or transformed; we observe effects of that "
        "transfer, not energy as a static object by itself."
    )
    log.append("108: removed curriculum-meta explanation phrasing")

    bank[98]["skill_tested"] = "Calculating device efficiency from energy input and useful output"
    bank[112]["skill_tested"] = "Calculating average acceleration from a change in velocity"
    log.append("98/112: removed item-number artifacts from skill_tested")

    return log


def main() -> int:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    assert len(bank) == 300
    before = deepcopy(bank)
    log = apply_all(bank)

    assert len(bank) == 300
    for i, q in enumerate(bank):
        if q["question_type"] != "Multiple Choice":
            continue
        corr = [c for c in q["choices"] if c.get("is_correct")]
        assert len(corr) == 1, i
        assert corr[0]["text"] == q["answer"], (i, corr[0]["text"], q["answer"])
        assert len(q["choices"]) == 4, i

    text = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    BANK.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")

    changed = sum(1 for a, b in zip(before, bank) if a != b)
    print(f"Questions modified: {changed}")
    for line in log:
        print(" -", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
