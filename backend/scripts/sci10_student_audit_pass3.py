"""Pass 3: remaining silly distractors + curriculum stretch fixes."""
from __future__ import annotations

import json
from pathlib import Path

QDIR = Path(__file__).resolve().parents[2] / "questions.json"
BANK = QDIR / "science10_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"


def set_mc(q, *, stem, answer, wrongs, explanation, common_mistake, skill=None):
    q["question_text"] = stem
    q["answer"] = answer
    q["choices"] = [{"text": answer, "is_correct": True}] + [
        {"text": w, "is_correct": False} for w in wrongs
    ]
    q["explanation"] = explanation
    q["common_mistake"] = common_mistake
    if skill:
        q["skill_tested"] = skill


def main() -> int:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    log = []

    # 177 — replace HIV/liposome (Bio30 flavour) with Sci10 membrane application
    set_mc(
        bank[177],
        stem="Soap bubbles and liposomes are useful models of cell membranes because they?",
        answer="form phospholipid (or similar amphipathic) bilayers that can enclose aqueous compartments",
        wrongs=[
            "convert cell walls into chloroplasts on contact",
            "permanently prevent any diffusion across membranes",
            "generate spontaneous generation of entirely new cells",
        ],
        explanation=(
            "Amphipathic molecules arrange into bilayers that enclose watery interiors, modelling "
            "how plasma membranes separate cell contents from surroundings."
        ),
        common_mistake="Students treat membrane models as literal biological organelles rather than structural analogies.",
        skill="Applying membrane bilayer models to everyday amphipathic systems",
    )
    log.append("177: replaced HIV-liposome stretch with soap/liposome membrane model")

    # Soften remaining silly climate distractors into genuine misconceptions
    set_mc(
        bank[255],
        stem=bank[255]["question_text"],
        answer="thermal expansion of warming ocean water and melting land ice add water to oceans",
        wrongs=[
            "sea-floor volcanoes create new water molecules that permanently raise sea level",
            "all rivers worldwide have permanently stopped discharging into the ocean",
            "increased evaporation has permanently removed the entire ocean reservoir",
        ],
        explanation=bank[255]["explanation"],
        common_mistake=bank[255]["common_mistake"],
    )
    log.append("255: replaced absurd sea-level distractors")

    set_mc(
        bank[256],
        stem=bank[256]["question_text"],
        answer="sunlight strikes equatorial surfaces at a more direct angle year-round",
        wrongs=[
            "the equator is always millions of kilometres closer to the Sun than the poles",
            "polar ice reflects and eliminates all incoming solar radiation at high latitudes",
            "Earth's core heats only the air above the equator",
        ],
        explanation=bank[256]["explanation"],
        common_mistake=bank[256]["common_mistake"],
    )
    log.append("256: replaced absurd insolation distractors")

    set_mc(
        bank[281],
        stem=bank[281]["question_text"],
        answer="operating costs, because less efficient devices use more energy for the same useful output",
        wrongs=[
            "only the brand colour printed on the device casing",
            "the atomic number of metals used in the device casing",
            "whether the device was invented before or after the telephone",
        ],
        explanation=bank[281]["explanation"],
        common_mistake=bank[281]["common_mistake"],
        skill=bank[281].get("skill_tested"),
    )
    log.append("281: replaced speed-of-light STS distractor")

    # Cross-course distinctness: ensure pH stem differs from SCI30 wording
    # (already rewritten earlier to 'best classified as')
    assert "pH of 3" in bank[52]["question_text"]

    text = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    BANK.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")
    for line in log:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
