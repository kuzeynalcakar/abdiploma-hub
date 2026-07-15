"""Generate, validate, and export the Science 10 question pool (~450 questions)."""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from sci10_questions.helpers import mc, nr, VALID_OUTCOMES
from sci10_questions.unit_a_chem import questions as unit_a
from sci10_questions.unit_b_physics import questions as unit_b
from sci10_questions.unit_c_biology import questions as unit_c
from sci10_questions.unit_d_climate import questions as unit_d
from sci10_questions.expansion_pool import expansion
from sci10_questions.pool_qa import qa_fix_pool

OUTPUT = Path(__file__).parent.parent / "questions.json" / "science10_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]

TOPIC_A = "Energy and Matter in Chemical Change"
TOPIC_B = "Energy Flow in Technological Systems"
TOPIC_C = "Cycling of Matter in Living Systems"
TOPIC_D = "Energy Flow in Global Systems"


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def programmatic_supplements() -> list[dict]:
    """Parameterized original questions to reach ~450 pool size."""
    extra = []

    # --- Unit A: molar mass and mole NR ---
    compounds = [
        ("water", "H2O", {"H": 1, "O": 16}, 18, "A3.8k"),
        ("carbon dioxide", "CO2", {"C": 12, "O": 16}, 44, "A3.8k"),
        ("sodium chloride", "NaCl", {"Na": 23, "Cl": 35.5}, 58.5, "A3.8k"),
        ("glucose", "C6H12O6", {"C": 12, "H": 1, "O": 16}, 180, "A3.8k"),
        ("ammonia", "NH3", {"N": 14, "H": 1}, 17, "A3.8k"),
        ("methane", "CH4", {"C": 12, "H": 1}, 16, "A3.8k"),
        ("calcium carbonate", "CaCO3", {"Ca": 40, "C": 12, "O": 16}, 100, "A3.8k"),
        ("sulfuric acid", "H2SO4", {"H": 1, "S": 32, "O": 16}, 98, "A3.8k"),
    ]
    for name, formula, _, molar_mass, oc in compounds:
        extra.append(nr(
            f"What is the molar mass of {name} ({formula}) in g/mol? "
            f"Use: H = 1, C = 12, N = 14, O = 16, Na = 23, S = 32, Cl = 35.5, Ca = 40.",
            str(int(molar_mass) if molar_mass == int(molar_mass) else molar_mass),
            f"Molar mass of {formula} = {molar_mass} g/mol.",
            "Students add subscripts incorrectly or use wrong atomic masses.",
            topic=TOPIC_A, outcome_code=oc,
            skill_tested=f"Calculating molar mass of {name}",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for mass, mm, moles, name in [
        (36, 18, 2, "water"), (88, 44, 2, "carbon dioxide"),
        (58.5, 58.5, 1, "sodium chloride"), (32, 16, 2, "methane"),
        (90, 180, 0.5, "glucose"), (34, 17, 2, "ammonia"),
    ]:
        extra.append(nr(
            f"What is the amount of {name} in moles when the sample has a mass of {mass} g "
            f"and molar mass {mm} g/mol?",
            str(moles) if moles != 0.5 else "0.5",
            f"Moles = mass / molar mass = {mass} / {mm} = {moles} mol.",
            "Students multiply mass and molar mass instead of dividing.",
            topic=TOPIC_A, outcome_code="A3.9k",
            skill_tested=f"Converting mass to moles for {name}",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # --- Unit B: Ek, Ep, efficiency NR ---
    for m, v, ek in [(2, 4, 16), (3, 6, 54), (0.5, 10, 25)]:
        extra.append(nr(
            f"A {m} kg object moves at {v} m/s. What is its kinetic energy in joules? "
            f"Use $E_k = \\frac{{1}}{{2}}mv^2$.",
            str(ek),
            f"$E_k = 0.5 \\times {m} \\times {v}^2 = {ek}$ J.",
            "Students forget the factor of one-half in the kinetic energy formula.",
            topic=TOPIC_B, outcome_code="B2.10k",
            skill_tested="Calculating kinetic energy from mass and velocity",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for m, h, ep in [(2, 5, 98), (4, 10, 392), (0.5, 20, 98)]:
        ans = int(ep) if ep == int(ep) else ep
        extra.append(nr(
            f"A {m} kg object is raised {h} m vertically near Earth's surface. "
            f"What is the gravitational potential energy in joules? Use $g = 9.8$ m/s$^2$ and $E_p = mgh$.",
            str(ans),
            f"$E_p = {m} \\times 9.8 \\times {h} = {ep}$ J.",
            "Students omit gravitational acceleration or use wrong height.",
            topic=TOPIC_B, outcome_code="B2.12k",
            skill_tested="Calculating gravitational potential energy",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for useful, total, eff in [(400, 500, 80), (150, 300, 50), (720, 900, 80)]:
        extra.append(nr(
            f"A device delivers {useful} J of useful energy from {total} J of total energy input. "
            f"What is the efficiency as a percentage?",
            str(eff),
            f"Efficiency = ({useful}/{total}) × 100 = {eff}%.",
            "Students invert the ratio or forget to multiply by 100.",
            topic=TOPIC_B, outcome_code="B3.5k",
            skill_tested="Calculating device efficiency percentage",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for v0, v1, t, a in [(0, 20, 4, 5), (10, 30, 8, 2.5)]:
        ans = str(int(a)) if a == int(a) else str(a)
        extra.append(nr(
            f"A cart's velocity changes from {v0} m/s to {v1} m/s in {t} s. "
            f"What is the average acceleration in m/s$^2$? Use $a = \\Delta v / \\Delta t$.",
            ans,
            f"$a = ({v1} - {v0}) / {t} = {a}$ m/s$^2$.",
            "Students divide by final velocity instead of time interval.",
            topic=TOPIC_B, outcome_code="B2.8k",
            skill_tested="Calculating average acceleration from velocity change",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # --- Unit C: magnification and SA:V NR ---
    for obj, img, mag in [(0.05, 2.0, 40), (0.02, 1.0, 50)]:
        extra.append(nr(
            f"A microscope specimen is {obj} mm wide and its image measures {img} mm wide. "
            f"What is the magnification (image size ÷ actual size)?",
            str(int(mag)),
            f"Magnification = {img} / {obj} = {mag}×.",
            "Students divide actual size by image size, inverting the ratio.",
            topic=TOPIC_C, outcome_code="C1.2s",
            skill_tested="Calculating microscope magnification",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for length, width, height, ratio in [(2, 2, 2, 3), (4, 4, 4, 1.5)]:
        extra.append(nr(
            f"A rectangular cell measures {length} μm × {width} μm × {height} μm. "
            f"Surface area = $2(lw + lh + wh)$, volume = $lwh$. "
            f"What is the surface-area-to-volume ratio rounded to one decimal?",
            str(ratio),
            f"SA:V ratio ≈ {ratio} (dimensionless).",
            "Students calculate volume only or invert the SA:V ratio.",
            topic=TOPIC_C, outcome_code="C2.9k",
            skill_tested="Calculating cell surface-area-to-volume ratio",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # --- Unit D: Q=mcΔT NR ---
    for m, c, dt, q in [(0.5, 4200, 10, 21000), (1.0, 4200, 5, 21000)]:
        extra.append(nr(
            f"How much thermal energy in joules is required to raise the temperature of "
            f"{m} kg of water by {dt}°C? Use $c = {c}$ J/(kg·°C) and $Q = mc\\Delta T$.",
            str(q),
            f"$Q = {m} \\times {c} \\times {dt} = {q}$ J.",
            "Students forget to multiply by specific heat capacity.",
            topic=TOPIC_D, outcome_code="D2.6k",
            skill_tested="Calculating thermal energy with Q=mcΔT",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    # --- Additional MC supplements ---
    chem_mc = [
        ("Which particle is gained or lost when an atom becomes a positive ion?",
         "electron", ["proton", "neutron", "nucleus"],
         "Cations form when atoms lose one or more electrons.", "Students think protons are lost to form cations.",
         "A2.3k", "Explaining ion formation by electron transfer", "Easy", 55),
        ("A double replacement reaction is best identified when",
         "two compounds exchange ions to form two new compounds",
         ["one element replaces another in a compound", "a single compound breaks into simpler substances", "a hydrocarbon reacts with oxygen only"],
         "Double replacement involves partner swapping of ions between two reactants.", "Students confuse with single replacement or decomposition.",
         "A3.5k", "Identifying double replacement reactions", "Medium", 75),
        ("The pH of a neutral solution at room temperature is approximately",
         "7", ["0", "14", "1"],
         "Pure water at 25°C has pH 7, indicating equal H⁺ and OH⁻ concentrations.", "Students confuse acidic (low pH) with basic (high pH) values.",
         "A2.5k", "Identifying neutral pH value", "Easy", 50),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in chem_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    phys_mc = [
        ("At constant velocity on a level frictionless surface, the net force on an object is",
         "zero", ["equal to the object's weight always", "equal to mass times velocity", "increasing continuously"],
         "Newton's first law: no net force means no acceleration at constant velocity.", "Students think motion requires continuous net force.",
         "B2.7k", "Applying Newton's first law to constant velocity", "Medium", 75),
        ("Useful energy output is always less than total energy input in real devices because",
         "some energy is dissipated as waste heat due to the second law of thermodynamics",
         ["energy is destroyed permanently in all conversions", "useful energy can exceed input in all real systems", "the first law prohibits any energy transfer"],
         "Real conversions lose energy to surroundings, limiting efficiency below 100%.", "Students think energy is destroyed rather than transformed to less useful forms.",
         "B3.3k", "Explaining why real device efficiency is below 100%", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in phys_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_B, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    bio_mc = [
        ("Turgor pressure in plant cells results primarily from",
         "water entering the vacuole by osmosis in a hypotonic environment",
         ["active transport of starch into the nucleus", "diffusion of oxygen through the cell wall only", "photosynthesis occurring in mitochondria"],
         "Water influx into the central vacuole creates internal pressure against the cell wall.", "Students confuse turgor with gas exchange or respiration.",
         "C3.3k", "Explaining turgor pressure in plant cells", "Medium", 80),
        ("The cohesion of water molecules contributes to",
         "upward movement of water in xylem through transpiration pull",
         ["active pumping of water by mitochondria in roots", "diffusion of carbon dioxide through stomata only", "synthesis of proteins on ribosomes"],
         "Hydrogen bonding between water molecules helps maintain continuous columns in xylem.", "Students attribute xylem transport to unrelated cellular processes.",
         "C3.3k", "Relating water cohesion to xylem transport", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in bio_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_C, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    climate_mc = [
        ("Net radiation surplus at low latitudes compared to high latitudes drives",
         "global circulation of atmosphere and oceans redistributing thermal energy",
         ["complete cessation of all wind patterns globally", "equal temperature at every latitude always", "elimination of seasonal variation everywhere"],
         "Unequal heating creates pressure and density differences that drive circulation systems.", "Students think surplus energy stays local without redistribution.",
         "D2.1k", "Explaining energy redistribution by global circulation", "Medium", 80),
        ("Paleoclimate evidence from ice cores provides data on",
         "past atmospheric composition and temperature trends over thousands of years",
         ["future weather forecasts for the next week only", "current stock market prices", "daily classroom attendance records"],
         "Trapped gas bubbles and isotope ratios in ice layers record historical climate conditions.", "Students confuse paleoclimate archives with short-term weather forecasting.",
         "D4.2k", "Identifying ice core paleoclimate evidence", "Medium", 75),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in climate_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_D, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return extra


def validate_pool(pool: list[dict]) -> None:
    invalid = []
    for i, item in enumerate(pool):
        reasons = validate_question(item, i)
        if reasons:
            invalid.append((i, reasons))
        oc = item.get("outcome_code", "")
        topic = item.get("topic", "")
        if topic in VALID_OUTCOMES and oc not in VALID_OUTCOMES[topic]:
            invalid.append((i, [f"invalid outcome_code {oc} for topic {topic}"]))
    if invalid:
        for idx, reasons in invalid[:20]:
            print(f"INVALID item {idx}: {reasons}")
        raise SystemExit(f"{len(invalid)} invalid questions in pool")


def main() -> None:
    pool = []
    pool.extend(unit_a())
    pool.extend(unit_b())
    pool.extend(unit_c())
    pool.extend(unit_d())
    pool.extend(expansion())
    pool.extend(programmatic_supplements())
    pool = qa_fix_pool(pool, max_per_template=2)

    validate_pool(pool)

    ordered = [order_item(q) for q in pool]
    mc_pos = assert_mc_position_balanced(ordered, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(ordered)} questions to {OUTPUT}")
    print("Topics:", dict(Counter(q["topic"] for q in ordered)))
    print("Types:", dict(Counter(q["question_type"] for q in ordered)))
    print("Difficulty:", dict(Counter(q["difficulty"] for q in ordered)))
    cog = Counter()
    for q in ordered:
        c = q["outcome_code"]
        if c.endswith("sts"):
            cog["sts"] += 1
        elif c.endswith("s"):
            cog["skills"] += 1
        else:
            cog["knowledge"] += 1
    print("Cognitive:", dict(cog))


if __name__ == "__main__":
    main()
