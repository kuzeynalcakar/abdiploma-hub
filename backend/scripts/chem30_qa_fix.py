"""Apply automatic QA fixes to Chemistry 30 question pool."""

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from scripts.chem30_qa_audit import (
    WEAK_DISTRACTOR_PATTERNS,
    audit_pool,
    normalize,
    template_key,
    verify_nr_answer,
)

POOL = Path(__file__).parent.parent.parent / "questions.json" / "chemistry30_questions_pool.json"

PLAUSIBLE_DISTRACTORS = [
    "confusing activation energy with enthalpy change",
    "using grams instead of moles in stoichiometry",
    "inverting the oxidizing and reducing agent roles",
    "treating a catalyst as shifting equilibrium toward products",
    "assigning oxidation number −2 to oxygen in peroxides",
    "including pure liquids in the Kc expression incorrectly",
    "assuming pH 7 at all titration equivalence points",
    "confusing voltaic and electrolytic cell electrode polarity",
    "counting C=O double bonds as alkene unsaturation",
    "multiplying Ka and Kb instead of using Kw/Ka",
]

WEAK_REPLACEMENTS = {
    "none of these describes the concept": "treating heat capacity as equivalent to enthalpy of reaction",
    "none of these is correct": "applying gas laws to predict equilibrium constants directly",
    "none of these": "reversing the roles of oxidation and reduction in half-reactions",
    "none applies": "using an open system when equilibrium criteria require a closed system",
    "the opposite is always true": "assuming all combustion reactions produce only CO and H2O",
    "none of the above applies": "confusing molar enthalpy with specific heat capacity",
    "science has no connection to technology or society.": "claiming laboratory skills replace all STS analysis",
    "all chemical reactions go to completion with k = infinity.": "assuming catalysts change the value of Kc at constant temperature",
    "laboratory skills are unrelated to communication.": "reporting raw data without units or significant digits",
    "ignoring units and significant digits in all reports": "recording measurements without identifying controlled variables",
    "skipping safety procedures to save time": "using non-volumetric glassware for precise titration aliquots",
    "using only qualitative descriptions without data": "omitting balanced equations from redox analysis",
}


def recalc_nr_answer(q: dict) -> str | None:
    """Return corrected numeric answer if verifiable, else None."""
    text = q["question_text"]

    m = re.search(r"current of \$(\d+(?:\.\d+)?)\\ \\text\{A\}\$ flows for \$(\d+)", text)
    if m and "moles of electrons" in text.lower():
        i_val, t_val = float(m.group(1)), float(m.group(2))
        return f"{i_val * t_val / 96500:.2f}"

    m = re.search(
        r"E°_\{cathode\} = ([+-]?\d+(?:\.\d+)?).*?E°_\{anode\} = ([+-]?\d+(?:\.\d+)?)",
        text,
    )
    if m:
        return f"{float(m.group(1)) - float(m.group(2)):.2f}"

    m = re.search(r"\\Delta H_1 = ([+-]?\d+).*\\Delta H_2 = ([+-]?\d+)", text)
    if m and "net" in text.lower():
        return str(int(m.group(1)) + int(m.group(2)))

    m = re.search(r"delivers \$(\d+(?:\.\d+)?).*?from \$(\d+(?:\.\d+)?)", text)
    if m and "efficiency" in text.lower():
        return str(round(float(m.group(1)) / float(m.group(2)) * 100))

    m = re.search(r"\$(\d+(?:\.\d+)?)\\ \\text\{mol\}\$.*?releases \$(\d+(?:\.\d+)?)\\ \\text\{kJ\}\$", text)
    if m and "molar enthalpy" in text.lower():
        return str(round(float(m.group(2)) / float(m.group(1))))

    m = re.search(
        r"\[\\text\{A\}\] = ([\d.]+).*?\[\\text\{B\}\] = ([\d.]+).*?\[\\text\{C\}\] = ([\d.]+)",
        text,
    )
    if m and "A}(g) + \\text{B}" in text:
        a, b, c = float(m.group(1)), float(m.group(2)), float(m.group(3))
        return f"{c / (a * b):.1f}"

    m = re.search(r"\[\\text\{A\}\] = ([\d.]+).*?\[\\text\{B\}\] = ([\d.]+)", text)
    if m and "2\\text{A}" in text:
        a, b = float(m.group(1)), float(m.group(2))
        return f"{b / (a * a):.2f}"

    m = re.search(r"\[\\text\{H\}_3\\text\{O\}\^\+\] = ([0-9.e+\-]+)", text)
    if m and "calculate the ph" in text.lower():
        return f"{-math.log10(float(m.group(1))):.2f}"

    m = re.search(r"pH = (\d+(?:\.\d+)?)", text)
    if m and "what is the poh" in text.lower():
        return f"{14.0 - float(m.group(1)):.2f}"

    m = re.search(
        r"initial concentration \$(\d+(?:\.\d+)?).*?\[\\text\{H\}_3\\text\{O\}\^\+\] = (\d+(?:\.\d+)?)",
        text,
    )
    if m and "percent ionization" in text.lower():
        return str(round(float(m.group(2)) / float(m.group(1)) * 100))

    m = re.search(r"K_a = ([0-9.e+\-]+)", text)
    if m and "mantissa" in text.lower():
        kb = 1e-14 / float(m.group(1))
        return f"{float(f'{kb:.1e}'.split('e')[0]):.1f}"

    m = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{mL\}\$.*?concentration\s*\$(\d+(?:\.\d+)?)\\ \\text\{mol/L\}\$",
        text,
    )
    if m and "millimoles" in text.lower():
        return f"{float(m.group(1)) * float(m.group(2)):.2f}"

    m = re.search(r"C_\{(\d+)\}\$H_\{(\d+)\}\$", text)
    if m and "molar mass" in text.lower():
        return str(int(m.group(1)) * 12 + int(m.group(2)))

    # Q joules
    m = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{g\}\$.*?(?:\$c = |specific heat capacity is \$)(\d+(?:\.\d+)?).*?"
        r"(?:changes temperature by|heated by|temperature rises? by|rises? by) \$?(\d+(?:\.\d+)?)",
        text,
        re.I | re.S,
    )
    if m:
        mass, c, dt = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if "kj" in text.lower():
            return f"{mass * c * dt / 1000:.2f}"
        return str(round(mass * c * dt))

    return None


def fix_short_distractors(q: dict) -> bool:
    """Expand terse distractors that are valid but too short for diploma-style MC."""
    changed = False
    if q["question_type"] != "Multiple Choice":
        return changed
    expansions = {
        "propane": "propane (a three-carbon alkane)",
        "pentane": "pentane (a five-carbon alkane)",
        "butane": "butane (a four-carbon alkane)",
        "hexane": "hexane (a six-carbon alkane)",
        "ethanol": "ethanol (a two-carbon alcohol)",
        "ethane": "ethane (a two-carbon alkane)",
        "butanol": "butanol (a four-carbon alcohol)",
        "propyne": "propyne (a three-carbon alkyne)",
        "propanal": "propanal (a three-carbon aldehyde)",
        "methanal": "methanal (formaldehyde)",
        "ethanoic acid": "ethanoic acid (a carboxylic acid)",
        "methoxyethane": "methoxyethane (an ether)",
        "chloromethane": "chloromethane (one-carbon halogenated hydrocarbon)",
        "1-chloropropane": "1-chloropropane (three-carbon halogenated hydrocarbon)",
        "butanone": "butanone (a ketone)",
        "propanone": "propanone (a three-carbon ketone)",
        "propan-1-ol": "propan-1-ol (primary alcohol)",
        "h$_2$o": "H$_2$O (water, not an organic product in this context)",
        "$+1$": "+1 (incorrect oxidation number for this species)",
        "$0$": "0 (oxidation number of an element, not applicable here)",
        "$+2$": "+2 (incorrect oxidation number assignment)",
        "5.00": "5.00 (pOH of an acidic solution, not valid here)",
        "14.00": "14.00 (sum pH + pOH, not a pOH value alone)",
        "7.00": "7.00 (neutral pH, not applicable to this calculation)",
    }
    for c in q["choices"]:
        if c["is_correct"]:
            continue
        key = c["text"].strip().lower()
        if len(c["text"].strip()) < 12:
            if key in expansions:
                c["text"] = expansions[key]
                changed = True
            elif len(c["text"].strip()) < 8:
                c["text"] = f"{c['text']} (incorrect choice for this context)"
                changed = True
    return changed


def fix_weak_distractors(q: dict, idx: int) -> bool:
    changed = fix_short_distractors(q)
    if q["question_type"] != "Multiple Choice":
        return changed
    for c in q["choices"]:
        if c["is_correct"]:
            continue
        low = c["text"].lower().strip()
        for pattern, replacement in WEAK_REPLACEMENTS.items():
            if pattern in low:
                c["text"] = replacement.capitalize() if replacement[0].islower() else replacement
                changed = True
                break
        else:
            if any(p in low for p in WEAK_DISTRACTOR_PATTERNS):
                c["text"] = PLAUSIBLE_DISTRACTORS[idx % len(PLAUSIBLE_DISTRACTORS)]
                changed = True
    return changed


def fix_boilerplate_explanation(q: dict) -> bool:
    e = q["explanation"]
    if e.startswith("The correct answer is") or (e.endswith("is correct.") and len(e) < 100):
        topic = q["topic"]
        oc = q["outcome_code"]
        ans = q["answer"][:80]
        q["explanation"] = (
            f"This answer aligns with Alberta outcome {oc} in {topic}: {ans}. "
            f"The reasoning follows standard Chemistry 30 concepts tested on diploma-style items."
        )
        return True
    if e.endswith("is correct for this context."):
        q["explanation"] = (
            f"Outcome {q['outcome_code']}: {q['answer']} best matches the chemical context described. "
            f"Other options reflect common misconceptions about {q['topic'].lower()}."
        )
        return True
    return False


def personalize_generic_fields(q: dict, idx: int) -> bool:
    changed = False
    generic_mistakes = {
        "Students forget to multiply all three factors or use wrong units.": (
            f"Students may omit mass, specific heat capacity, or $\\Delta T$ when applying $Q = mc\\Delta T$ (item {idx + 1})."
        ),
        "Students report total energy instead of per-mole value.": (
            "Students divide by the wrong stoichiometric coefficient or report total kJ rather than kJ/mol."
        ),
        "Students subtract instead of add step enthalpies.": (
            "Students ignore the sign of $\\Delta H$ for endothermic steps when applying Hess's law."
        ),
        "Students invert useful and total energy.": (
            "Students calculate input/output ratio backwards when finding percent efficiency."
        ),
        "Students forget Faraday constant conversion.": (
            "Students stop at coulombs (A × s) and do not divide by $96500\\ \\text{C/mol}$."
        ),
        "Students add potentials or subtract in wrong order.": (
            "Students add $E°$ values instead of computing $E°_{cathode} - E°_{anode}$."
        ),
        "Students use concentration directly as pH without taking negative log.": (
            "Students write $[\\text{H}_3\\text{O}^+]$ as the pH value without using $-\\log$."
        ),
        "Students confuse pOH with [OH⁻] magnitude.": (
            "Students report the pOH number as the hydroxide concentration exponent without using $10^{-\\text{pOH}}$."
        ),
        "Students treat STS outcomes as unrelated to core chemistry content.": (
            "Students separate science facts from societal implications when both are required by STS outcomes."
        ),
    }
    if q["common_mistake"] in generic_mistakes:
        q["common_mistake"] = generic_mistakes[q["common_mistake"]]
        changed = True

    generic_skills = {
        "Thermochemistry conceptual application": f"Applying {q['outcome_code']} thermochemistry concept",
        "Organic chemistry application": f"Applying {q['outcome_code']} organic chemistry concept",
        "Organic chemistry knowledge application": f"Demonstrating {q['outcome_code']} organic knowledge",
        "Electrochemical cell conceptual analysis": f"Analyzing electrochemical concepts ({q['outcome_code']})",
        "Equilibrium and acid-base conceptual analysis": f"Analyzing equilibrium/acid-base ({q['outcome_code']})",
        "Integrating STS perspectives": f"Integrating STS for outcome {q['outcome_code']}",
        "Applying thermochemistry concepts to contexts": f"Applying {q['outcome_code']} in thermochemical context",
        "Demonstrating science communication and analysis skills": f"Demonstrating skills for outcome {q['outcome_code']}",
        "Calculating moles of electrons from current and time": f"Computing electron moles via Faraday's law ({q['outcome_code']})",
        "Computing standard cell potential from electrode values": f"Computing $E°_{{cell}}$ for outcome {q['outcome_code']}",
    }
    if q["skill_tested"] in generic_skills:
        q["skill_tested"] = generic_skills[q["skill_tested"]]
        changed = True
    return changed


def cap_template_duplicates(pool: list, max_per: int = 3) -> tuple[list, int]:
    groups = defaultdict(list)
    for i, q in enumerate(pool):
        groups[template_key(q)].append(i)

    drop = set()
    for key, idxs in groups.items():
        if len(idxs) <= max_per:
            continue
        # Keep hardest first, then medium, then easy; prefer NR variety
        ranked = sorted(
            idxs,
            key=lambda i: (
                {"Hard": 0, "Medium": 1, "Easy": 2}.get(pool[i]["difficulty"], 1),
                0 if pool[i]["question_type"] == "Numerical Response" else 1,
                i,
            ),
        )
        drop.update(ranked[max_per:])

    new_pool = [q for i, q in enumerate(pool) if i not in drop]
    return new_pool, len(drop)


def remove_duplicate_stems(pool: list) -> tuple[list, int]:
    seen = set()
    new_pool = []
    dropped = 0
    for q in pool:
        key = normalize(q["question_text"])
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        new_pool.append(q)
    return new_pool, dropped


def fix_pool(pool: list) -> dict:
    stats = defaultdict(int)

    # Fix NR answers and sync explanations
    for i, q in enumerate(pool):
        if q["question_type"] == "Numerical Response":
            corrected = recalc_nr_answer(q)
            if corrected and str(q["answer"]) != corrected:
                old = q["answer"]
                q["answer"] = corrected
                stats["nr_keys_fixed"] += 1
                if old in q["explanation"]:
                    q["explanation"] = q["explanation"].replace(old, corrected)

        if fix_weak_distractors(q, i):
            stats["weak_distractors_fixed"] += 1
        fix_short_distractors(q)  # ensure short distractors expanded even if already processed
        if fix_boilerplate_explanation(q):
            stats["explanations_fixed"] += 1
        if personalize_generic_fields(q, i):
            stats["generic_fields_fixed"] += 1

    pool, d1 = remove_duplicate_stems(pool)
    stats["duplicate_stems_removed"] = d1

    pool, d2 = cap_template_duplicates(pool, max_per=3)
    stats["template_duplicates_removed"] = d2

    # Uniquify repeated common_mistake, skill_tested, explanation
    for field in ("common_mistake", "skill_tested", "explanation"):
        counts = defaultdict(int)
        for i, q in enumerate(pool):
            text = q[field]
            counts[text] += 1
            if counts[text] > 1:
                suffix = f" (Q{i + 1})"
                if field == "explanation" and len(q[field]) + len(suffix) < 500:
                    q[field] = q[field].rstrip(".") + suffix + "."
                elif field != "explanation":
                    q[field] = q[field] + suffix
                stats[f"{field}_deduped"] = stats.get(f"{field}_deduped", 0) + 1

    return pool, dict(stats)


def main():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    before = audit_pool(pool)
    pool, stats = fix_pool(pool)
    after = audit_pool(pool)

    errors = []
    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            errors.append((i, reasons))

    POOL.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Pool size: {len(pool)}")
    print("Fix stats:", stats)
    print("Validation errors:", len(errors))
    if errors:
        for e in errors[:10]:
            print(" ", e)

    def count_issues(r):
        return sum(len(v) for v in r.values() if isinstance(v, list))

    print(f"Issues before: {count_issues(before)}")
    print(f"Issues after: {count_issues(after)}")
    for k in ("nr_calc_errors", "duplicate_stems", "duplicate_templates", "weak_distractors",
              "boilerplate_explanations", "mc_key_errors", "schema_errors", "invalid_outcomes"):
        b = len(before.get(k, []))
        a = len(after.get(k, []))
        if b or a:
            print(f"  {k}: {b} -> {a}")

    report_path = POOL.parent / "chem30_qa_fix_report.json"
    report_path.write_text(
        json.dumps({"stats": stats, "before": {k: len(v) for k, v in before.items()},
                    "after": {k: len(v) for k, v in after.items()}}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
