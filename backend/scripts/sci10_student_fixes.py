"""Confirmed student-audit fixes for the SCI10 production bank."""

from __future__ import annotations

import re
from typing import Any

BOILERPLATE_DISTRACTOR_MARKERS = (
    "misconception from another",
    "related misconception from another",
    "reversed cause-and-effect",
    "true statement that does not answer",
    "does not answer this specific",
    "does not answer this stem",
    "terminology from a different",
    "unrelated process outside",
    "partial truth that omits",
    "concept confused with the correct answer",
)


# index -> full replacement for choices (and optional stem/answer/explanation patches)
HAND_FIXED_MC: dict[int, dict[str, Any]] = {
    33: {
        "choices": [
            {"text": "Cl$^{-}$", "is_correct": True},
            {"text": "Cl$^{+}$", "is_correct": False},
            {"text": "Cl$_2$", "is_correct": False},
            {"text": "Cl$^{2-}$", "is_correct": False},
        ],
        "answer": "Cl$^{-}$",
        "explanation": "Chlorine gains one electron to complete its valence shell, forming the chloride ion Cl$^{-}$.",
        "common_mistake": "Students reverse the charge and choose Cl$^{+}$ as if chlorine loses an electron.",
    },
    34: {
        "choices": [
            {"text": "7", "is_correct": True},
            {"text": "0", "is_correct": False},
            {"text": "14", "is_correct": False},
            {"text": "1", "is_correct": False},
        ],
        "answer": "7",
        "explanation": "At 25°C, pure water has equal [H$^{+}$] and [OH$^{-}$], so pH ≈ 7.",
        "common_mistake": "Students confuse pH 0 (strongly acidic) or pH 14 (strongly basic) with neutrality.",
    },
    35: {
        "choices": [
            {"text": "CH$_4$", "is_correct": True},
            {"text": "NaCl", "is_correct": False},
            {"text": "MgO", "is_correct": False},
            {"text": "CaF$_2$", "is_correct": False},
        ],
        "answer": "CH$_4$",
        "explanation": "Methane is a covalent molecular compound of non-metals; the others are ionic lattices.",
        "common_mistake": "Students classify any compound containing carbon as ionic.",
    },
    36: {
        "choices": [
            {"text": "pink", "is_correct": True},
            {"text": "colourless", "is_correct": False},
            {"text": "bright blue only in all bases", "is_correct": False},
            {"text": "metallic grey", "is_correct": False},
        ],
        "answer": "pink",
        "explanation": "Phenolphthalein is colourless in acid and turns pink in basic solution.",
        "common_mistake": "Students remember the acid colour (colourless) and apply it to bases.",
    },
    38: {
        "choices": [
            {"text": "SO$_4^{2-}$", "is_correct": True},
            {"text": "SO$_3^{2-}$", "is_correct": False},
            {"text": "S$^{2-}$", "is_correct": False},
            {"text": "HSO$_4^{-}$", "is_correct": False},
        ],
        "answer": "SO$_4^{2-}$",
        "explanation": "Sulfate is SO$_4^{2-}$; sulfite is SO$_3^{2-}$ and sulfide is S$^{2-}$.",
        "common_mistake": "Students confuse sulfate with sulfite or hydrogen sulfate.",
    },
    47: {
        "choices": [
            {"text": "endothermic", "is_correct": True},
            {"text": "exothermic", "is_correct": False},
            {"text": "combustion only", "is_correct": False},
            {"text": "always a physical change", "is_correct": False},
        ],
        "answer": "endothermic",
        "explanation": "A reaction that absorbs heat from the surroundings feels cold and is endothermic.",
        "common_mistake": "Students swap endothermic and exothermic definitions.",
    },
    49: {
        "choices": [
            {"text": "12", "is_correct": True},
            {"text": "24", "is_correct": False},
            {"text": "36", "is_correct": False},
            {"text": "0", "is_correct": False},
        ],
        "answer": "12",
        "explanation": "Neutrons = mass number − protons = 24 − 12 = 12.",
        "common_mistake": "Students report the mass number (24) instead of subtracting protons.",
    },
    50: {
        "choices": [
            {"text": "CaO", "is_correct": True},
            {"text": "Ca$_2$O", "is_correct": False},
            {"text": "CaO$_2$", "is_correct": False},
            {"text": "Ca$_2$O$_2$", "is_correct": False},
        ],
        "answer": "CaO",
        "explanation": "Ca$^{2+}$ and O$^{2-}$ combine 1:1, so the formula is CaO.",
        "common_mistake": "Students write Ca$_2$O by reversing ion charges incorrectly.",
    },
    52: {
        "question_text": "A solution has a pH of 3. How should this solution be classified?",
        "choices": [
            {"text": "Acidic", "is_correct": True},
            {"text": "Neutral", "is_correct": False},
            {"text": "Basic", "is_correct": False},
            {"text": "Amphoteric", "is_correct": False},
        ],
        "answer": "Acidic",
        "explanation": "pH below 7 indicates an acidic solution; pH 3 is strongly acidic relative to neutral water.",
        "common_mistake": "Students reverse the pH scale and call pH 3 basic.",
    },
    55: {
        "choices": [
            {"text": "electron", "is_correct": True},
            {"text": "proton", "is_correct": False},
            {"text": "neutron", "is_correct": False},
            {"text": "alpha particle", "is_correct": False},
        ],
        "answer": "electron",
        "explanation": "Positive ions (cations) form when atoms lose one or more electrons.",
        "common_mistake": "Students think the nucleus loses a proton when a cation forms.",
    },
    56: {
        "choices": [
            {"text": "CO$_2$", "is_correct": True},
            {"text": "NaCl", "is_correct": False},
            {"text": "KBr", "is_correct": False},
            {"text": "MgO", "is_correct": False},
        ],
        "answer": "CO$_2$",
        "explanation": "CO$_2$ is a covalent molecular compound; NaCl, KBr, and MgO are ionic.",
        "common_mistake": "Students pick a familiar ionic salt when asked for a molecular example.",
    },
    58: {
        "choices": [
            {"text": "CO$_3^{2-}$", "is_correct": True},
            {"text": "CO$_2$", "is_correct": False},
            {"text": "HCO$_3^{2-}$", "is_correct": False},
            {"text": "CO$_4^{2-}$", "is_correct": False},
        ],
        "answer": "CO$_3^{2-}$",
        "explanation": "Carbonate is CO$_3^{2-}$; bicarbonate is HCO$_3^{-}$ (not 2−).",
        "common_mistake": "Students confuse carbonate with carbon dioxide or mischarge bicarbonate.",
    },
    69: {
        "choices": [
            {"text": "−1", "is_correct": True},
            {"text": "+1", "is_correct": False},
            {"text": "−2", "is_correct": False},
            {"text": "+7", "is_correct": False},
        ],
        "answer": "−1",
        "explanation": "Group 17 halogens need one electron to fill their valence shell, forming 1− ions.",
        "common_mistake": "Students assign +1 by confusing gain/loss of electrons.",
    },
    71: {
        "choices": [
            {"text": "PCl$_3$", "is_correct": True},
            {"text": "Na$_2$O", "is_correct": False},
            {"text": "CaCl$_2$", "is_correct": False},
            {"text": "LiF", "is_correct": False},
        ],
        "answer": "PCl$_3$",
        "explanation": "PCl$_3$ is covalent (non-metal + non-metal); the others are ionic metal–non-metal compounds.",
        "common_mistake": "Students classify all compounds containing chlorine as molecular.",
    },
    105: {
        "choices": [
            {"text": "5000 J", "is_correct": True},
            {"text": "500 J", "is_correct": False},
            {"text": "50 J", "is_correct": False},
            {"text": "510 J", "is_correct": False},
        ],
        "answer": "5000 J",
        "explanation": "Energy = power × time = 500 W × 10 s = 5000 J.",
        "common_mistake": "Students forget to multiply by time and report the power value in joules.",
    },
    112: {
        "choices": [
            {"text": "2.0 m/s²", "is_correct": True},
            {"text": "0.5 m/s²", "is_correct": False},
            {"text": "32 m/s²", "is_correct": False},
            {"text": "4.0 m/s²", "is_correct": False},
        ],
        "answer": "2.0 m/s²",
        "explanation": "a = Δv/Δt = (8.0 − 0)/4.0 = 2.0 m/s².",
        "common_mistake": "Students divide time by velocity (0.5) or multiply 8×4 (32).",
    },
    113: {
        "choices": [
            {"text": "joule (J)", "is_correct": True},
            {"text": "watt (W)", "is_correct": False},
            {"text": "newton (N)", "is_correct": False},
            {"text": "metre per second (m/s)", "is_correct": False},
        ],
        "answer": "joule (J)",
        "explanation": "Kinetic energy is measured in joules; watts are for power and newtons for force.",
        "common_mistake": "Students confuse the unit of energy with the unit of power.",
    },
    131: {
        "choices": [
            {"text": "twice as large", "is_correct": True},
            {"text": "four times as large", "is_correct": False},
            {"text": "one half as large", "is_correct": False},
            {"text": "the same", "is_correct": False},
        ],
        "answer": "twice as large",
        "explanation": "E_k = ½mv²; at the same speed, doubling mass doubles kinetic energy.",
        "common_mistake": "Students apply the v² factor and say four times when only mass changed.",
    },
    146: {
        "choices": [
            {"text": "four", "is_correct": True},
            {"text": "two", "is_correct": False},
            {"text": "eight", "is_correct": False},
            {"text": "one half", "is_correct": False},
        ],
        "answer": "four",
        "explanation": "E_k ∝ v², so doubling speed multiplies kinetic energy by 2² = 4.",
        "common_mistake": "Students think energy doubles with speed instead of quadrupling.",
    },
    154: {
        "choices": [
            {"text": "10 MJ", "is_correct": True},
            {"text": "6.4 MJ", "is_correct": False},
            {"text": "8.0 MJ", "is_correct": False},
            {"text": "80 MJ", "is_correct": False},
        ],
        "answer": "10 MJ",
        "explanation": "Useful = efficiency × input ⇒ input = 8.0 / 0.80 = 10 MJ.",
        "common_mistake": "Students multiply 8.0 × 0.80 and report 6.4 MJ as the input.",
    },
    294: {
        "choices": [
            {"text": "18 g", "is_correct": True},
            {"text": "16 g", "is_correct": False},
            {"text": "32 g", "is_correct": False},
            {"text": "2 g", "is_correct": False},
        ],
        "answer": "18 g",
        "explanation": "16 g O₂ is 0.50 mol. The reaction O₂ + 2H₂ → 2H₂O makes 1.0 mol H₂O = 18 g.",
        "common_mistake": "Students assume product mass equals reactant oxygen mass (16 g).",
    },
    295: {
        "choices": [
            {"text": "Al$_2$(SO$_4$)$_3$", "is_correct": True},
            {"text": "AlSO$_4$", "is_correct": False},
            {"text": "Al$_2$SO$_4$", "is_correct": False},
            {"text": "Al(SO$_4$)$_2$", "is_correct": False},
        ],
        "answer": "Al$_2$(SO$_4$)$_3$",
        "explanation": "Al$^{3+}$ and SO$_4^{2-}$ require a 2:3 ratio for charge balance.",
        "common_mistake": "Students write a 1:1 formula without balancing charges.",
    },
    299: {
        "choices": [
            {"text": "4, 3, 2 respectively", "is_correct": True},
            {"text": "2, 1, 1 respectively", "is_correct": False},
            {"text": "2, 3, 2 respectively", "is_correct": False},
            {"text": "4, 2, 3 respectively", "is_correct": False},
        ],
        "answer": "4, 3, 2 respectively",
        "explanation": "4Fe + 3O₂ → 2Fe₂O₃ balances Fe and O atoms on both sides.",
        "common_mistake": "Students use 2, 3, 2 which leaves iron unbalanced.",
    },
}


def is_boilerplate_distractor(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in BOILERPLATE_DISTRACTOR_MARKERS)


def apply_hand_fixes(items: list[dict]) -> list[dict]:
    applied = []
    for idx, patch in HAND_FIXED_MC.items():
        if idx >= len(items):
            continue
        q = items[idx]
        for key, value in patch.items():
            q[key] = value
        applied.append({"index": idx, "fix": "replaced boilerplate/weak MC content with real distractors"})
    return applied


def fix_nr_precision(items: list[dict]) -> list[dict]:
    applied = []
    for i, q in enumerate(items):
        if q["question_type"] != "Numerical Response":
            continue
        text = q["question_text"].lower()
        ans = str(q["answer"]).strip()
        if "one decimal" in text or "1 decimal" in text or "to one decimal" in text:
            try:
                formatted = f"{float(ans):.1f}"
                if formatted != ans:
                    q["answer"] = formatted
                    applied.append({"index": i, "fix": f"NR precision -> {formatted}"})
            except ValueError:
                pass
        if "two decimal" in text:
            try:
                formatted = f"{float(ans):.2f}"
                if formatted != ans:
                    q["answer"] = formatted
                    applied.append({"index": i, "fix": f"NR precision -> {formatted}"})
            except ValueError:
                pass
        # Strip meta prefixes that feel AI/test-harness
        for prefix in ("Checkpoint: ", "Review: "):
            if q["question_text"].startswith(prefix):
                q["question_text"] = q["question_text"][len(prefix) :]
                applied.append({"index": i, "fix": f"removed '{prefix.strip()}' meta prefix"})
    return applied


def scrub_ai_explanations(items: list[dict]) -> list[dict]:
    applied = []
    for i, q in enumerate(items):
        expl = q.get("explanation") or ""
        if "is correct because it matches" in expl.lower() or "the other options reflect common misconceptions within" in expl.lower():
            # rebuild a tighter explanation from answer
            ans = q.get("answer", "")
            q["explanation"] = f"{ans} follows directly from the relationships stated in the question stem."
            applied.append({"index": i, "fix": "rewrote AI-template explanation"})
        mistake = q.get("common_mistake") or ""
        if "students select a distractor that confuses related concepts within" in mistake.lower():
            q["common_mistake"] = "Students confuse related quantities or reverse a key relationship in the stem."
            applied.append({"index": i, "fix": "rewrote generic common_mistake"})
    return applied


def assert_no_boilerplate(items: list[dict]) -> list[dict]:
    remaining = []
    for i, q in enumerate(items):
        if q["question_type"] != "Multiple Choice":
            continue
        for c in q.get("choices") or []:
            if is_boilerplate_distractor(c["text"]):
                remaining.append({"index": i, "text": c["text"]})
    return remaining
