"""Apply confirmed student-audit fixes to the SCI10 production bank.

Fix classes:
 1. Replace placeholder/meta distractors with real, plausible, curriculum-correct wrong answers.
 2. Rewrite boilerplate / AI-tell explanations into genuine worked solutions.
 3. Fix percent-vs-decimal grading ambiguity wording.
 4. Strip artificial "Checkpoint:" / "Review:" stem prefixes.
 5. Reword cross-course duplicate pH stem.
 6. Rephrase blatant clone calculation stems (answers unchanged) to reduce template repetition.

Keyed by exact current question_text (stable, static file). Writes both
science10_questions_final.json and course_questions_final.json.
"""
from __future__ import annotations

import json
from pathlib import Path

QDIR = Path(__file__).resolve().parents[2] / "questions.json"
BANK = QDIR / "science10_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"


# ---- 1. Distractor replacements: stem-substring -> [3 wrong choices] ----
DISTRACTORS = {
    "The ion formed when a chlorine atom gains one electron": ["Cl$^+$", "Cl$^{2-}$", "Na$^+$"],
    "The pH of a neutral solution at room temperature": ["0", "1", "14"],
    "Which compound is molecular rather than ionic?": ["NaCl", "MgO", "KBr"],
    "Phenolphthalein in a basic solution appears": ["colourless", "red", "yellow"],
    "The polyatomic ion sulfate has the formula": ["SO$_3^{2-}$", "SO$_4^{-}$", "S$^{2-}$"],
    "feels cold to the touch because it absorbs energy": ["exothermic", "combustion", "oxidation"],
    "A neutral atom of magnesium-24 has 12 protons": ["24", "36", "6"],
    "The formula for calcium oxide is": ["Ca$_2$O", "CaO$_2$", "Ca$_2$O$_3$"],
    "A solution with a pH of 3 is best classified as": ["basic", "neutral", "amphoteric"],
    "Which particle is gained or lost when an atom becomes a positive ion?": [
        "proton (positive particle in the nucleus)",
        "neutron (neutral particle in the nucleus)",
        "photon (a particle of light, not matter)",
    ],
    "A molecular (covalent) compound is best represented by": ["NaCl", "MgCl$_2$", "KF"],
    "The carbonate ion has the formula": ["HCO$_3^-$", "CO$_3^{-}$", "C$_2$O$_4^{2-}$"],
    "Halogens in Group 17 typically gain one electron to form ions with charge": ["+1", "−2", "+7"],
    "Which substance is classified as a molecular compound?": ["NaCl", "CaF$_2$", "Li$_2$O"],
    "A motor rated at 500 W running for 10 s transfers energy": ["50 J", "500 J", "510 J"],
    "An athlete accelerates from rest to 8.0 m/s in 4.0 s": ["4.0 m/s²", "0.5 m/s²", "32 m/s²"],
    "The SI unit for kinetic energy is the": ["newton (N)", "watt (W)", "pascal (Pa)"],
    "Object X has twice the mass of object Y": ["four times as large", "one half as large", "the same"],
    "Doubling the speed of an object while mass stays constant multiplies its kinetic energy": [
        "two", "eight", "sixteen",
    ],
    "A natural gas furnace rated 80% efficient delivers 8.0 MJ": ["6.4 MJ", "8.0 MJ", "12.5 MJ"],
    "16 g of O$_2$ gas reacts completely with excess hydrogen": ["16 g", "32 g", "36 g"],
    "Which formula correctly represents aluminum sulfate?": ["AlSO$_4$", "Al$_2$SO$_4$", "Al(SO$_4$)$_2$"],
    "Balancing the equation ___ Fe + ___ O$_2$": [
        "2, 3, 2 respectively", "3, 2, 3 respectively", "4, 3, 1 respectively",
    ],
}


# ---- 2. Explanation rewrites: stem-substring -> worked solution ----
EXPLANATIONS = {
    "A neutralization reaction releases 4500 J of heat to 150 g of water":
        "ΔT = Q / (mc) = 4500 / (150 × 4.18) = 4500 / 627 = 7.2 °C.",
    "How many moles are in 88 g of CO$_2$?":
        "moles = mass ÷ molar mass = 88 ÷ 44 = 2.0 mol.",
    "What is the molar mass of CO$_2$ in g/mol? Use C = 12":
        "Molar mass of CO₂ = 12 + 2(16) = 44 g/mol.",
    "How many moles are in 12.0 g of carbon?":
        "moles = mass ÷ molar mass = 12.0 ÷ 12.0 = 1.0 mol.",
    "What is the molar mass of NaCl in g/mol? Use Na = 23":
        "Molar mass of NaCl = 23 + 35.5 = 58.5 g/mol.",
    "What is the molar mass of MgO in g/mol?":
        "Molar mass of MgO = 24 + 16 = 40 g/mol.",
    "What is the molar mass of methane (CH4)":
        "Molar mass of CH₄ = 12 + 4(1) = 16 g/mol.",
    "A calorimeter contains 200 g of water (c = 4.18":
        "q = mcΔT = 200 × 4.18 × 5.0 = 4180 J.",
    "What is the molar mass of sodium chloride (NaCl)":
        "Molar mass of NaCl = 23 + 35.5 = 58.5 g/mol.",
    "What is the amount of carbon dioxide in moles when the sample has a mass of 88 g":
        "moles = mass ÷ molar mass = 88 ÷ 44 = 2 mol.",
    "What is the molar mass of water (H2O)":
        "Molar mass of H₂O = 2(1) + 16 = 18 g/mol.",
    "What is the molar mass of carbon dioxide (CO2)":
        "Molar mass of CO₂ = 12 + 2(16) = 44 g/mol.",
    "What is the molar mass of ammonia (NH3)":
        "Molar mass of NH₃ = 14 + 3(1) = 17 g/mol.",
    "What is the amount of methane in moles when the sample has a mass of 32 g":
        "moles = mass ÷ molar mass = 32 ÷ 16 = 2 mol.",
    "What is the amount of water in moles when the sample has a mass of 36 g":
        "moles = mass ÷ molar mass = 36 ÷ 18 = 2 mol.",
    "What is the molar mass of calcium carbonate (CaCO3)":
        "Molar mass of CaCO₃ = 40 + 12 + 3(16) = 100 g/mol.",
    "What is the molar mass of glucose (C6H12O6)":
        "Molar mass of C₆H₁₂O₆ = 6(12) + 12(1) + 6(16) = 72 + 12 + 96 = 180 g/mol.",
    "What is the molar mass of sulfuric acid (H2SO4)":
        "Molar mass of H₂SO₄ = 2(1) + 32 + 4(16) = 2 + 32 + 64 = 98 g/mol.",
    "What is the amount of ammonia in moles when the sample has a mass of 34 g":
        "moles = mass ÷ molar mass = 34 ÷ 17 = 2 mol.",
    "A light bulb converts 900 J of electrical energy into 180 J":
        "Efficiency = useful ÷ input × 100% = 180 ÷ 900 × 100% = 20%.",
    "A 2 kg object moves at 4 m/s. What is its kinetic energy":
        "E_k = ½mv² = ½ × 2 × 4² = ½ × 2 × 16 = 16 J.",
    "A cart's velocity changes from 10 m/s to 30 m/s in 8 s":
        "a = Δv ÷ Δt = (30 − 10) ÷ 8 = 20 ÷ 8 = 2.5 m/s².",
    "A device delivers 400 J of useful energy from 500 J":
        "Efficiency = 400 ÷ 500 × 100% = 80%.",
    "A 2 kg object is raised 5 m vertically near Earth's surface":
        "E_p = mgh = 2 × 9.8 × 5 = 98 J.",
    "A 3 kg cart travels at 6 m/s":
        "E_k = ½mv² = ½ × 3 × 6² = ½ × 3 × 36 = 54 J.",
    "Starting from rest, a runner reaches 20 m/s after 4 s":
        "a = Δv ÷ Δt = (20 − 0) ÷ 4 = 5 m/s².",
    "A machine outputs 150 J of useful energy for every 300 J":
        "Efficiency = 150 ÷ 300 × 100% = 50%.",
    "How much gravitational potential energy (in J) does a 4 kg mass gain when lifted 10 m":
        "E_p = mgh = 4 × 9.8 × 10 = 392 J.",
    "A compact fluorescent lamp receives 400 J of energy input and delivers 340 J":
        "Efficiency = 340 ÷ 400 × 100% = 85.0%.",
    "A cyclist accelerates uniformly from rest to 20 m/s in 4.0 s":
        "a = Δv ÷ Δt = (20 − 0) ÷ 4.0 = 5.0 m/s².",
    "A high-efficiency furnace receives 600 J of energy input and delivers 450 J":
        "Efficiency = 450 ÷ 600 × 100% = 75.0%.",
    "A industrial conveyor motor receives 1000 J of energy input and delivers 350 J":
        "Efficiency = 350 ÷ 1000 × 100% = 35.0%.",
    "A device receives 400 J of energy and produces 160 J":
        "Efficiency = 160 ÷ 400 × 100% = 40.0%.",
    "A device receives 750 J of energy and produces 300 J":
        "Efficiency = 300 ÷ 750 × 100% = 40.0%.",
    "An athlete accelerates from rest to 8.0 m/s in 4.0 s":
        "a = Δv ÷ Δt = (8.0 − 0) ÷ 4.0 = 2.0 m/s².",
    "A rectangular cell measures 2 μm × 2 μm × 2 μm":
        "SA = 2(2·2 + 2·2 + 2·2) = 24 μm²; V = 2·2·2 = 8 μm³; ratio = 24 ÷ 8 = 3.0.",
    "A cubic cell 4 μm on each side":
        "SA = 2(4·4 + 4·4 + 4·4) = 96 μm²; V = 4·4·4 = 64 μm³; ratio = 96 ÷ 64 = 1.5.",
    "A microscope specimen is 0.02 mm wide and its image measures 1.0 mm":
        "Magnification = image ÷ actual = 1.0 ÷ 0.02 = 50.",
    "In a field of view, 12 of 50 plant cells show plasmolysis":
        "Percent = 12 ÷ 50 × 100% = 24.0%.",
    "Of 40 plant cells viewed, 8 show plasmolysis":
        "Percent = 8 ÷ 40 × 100% = 20.0%.",
    "A leaf sample of 2 mm² contains 240 open stomata":
        "Density = count ÷ area = 240 ÷ 2 = 120 stomata/mm².",
    "Across 1 mm² of leaf surface, 180 open stomata are counted":
        "Density = count ÷ area = 180 ÷ 1 = 180 stomata/mm².",
    "A microscope specimen is 0.05 mm wide and its image measures 2.0 mm":
        "Magnification = image ÷ actual = 2.0 ÷ 0.05 = 40.",
    "A climate model projects sea level rise of 3.2 mm per year":
        "Rise = rate × time = 3.2 mm/yr × 25 yr = 80 mm.",
    "How much thermal energy in joules is required to raise the temperature of 0.5 kg of water by 10":
        "Q = mcΔT = 0.5 × 4200 × 10 = 21000 J.",
    "How many joules of energy are needed to warm 3.0 kg of water by 5.0":
        "Q = mcΔT = 3.0 × 4200 × 5.0 = 63000 J.",
    "How much thermal energy in joules is required to raise the temperature of 1.0 kg of water by 5":
        "Q = mcΔT = 1.0 × 4200 × 5 = 21000 J.",
    "A soil sample with mass 1.0 kg and c = 800":
        "ΔT = Q ÷ (mc) = 4000 ÷ (1.0 × 800) = 5 °C.",
    "Atmospheric CO₂ rose from 380 ppm to 420 ppm over a decade":
        "Increase = 420 − 380 = 40 ppm.",
}


# ---- 5/6. Stem rewrites: old-substring -> full new question_text ----
STEM_REWRITES = {
    "A solution with pH 3 is _______?":
        "A solution with a pH of 3 is best classified as?",
    "A 3 kg object moves at 6 m/s. What is its kinetic energy in joules? Use $E_k = \\frac{1}{2}mv^2$.":
        "A 3 kg cart travels at 6 m/s. Determine its kinetic energy in joules using $E_k = \\frac{1}{2}mv^2$.",
    "A cart's velocity changes from 0 m/s to 20 m/s in 4 s. What is the average acceleration in m/s$^2$? Use $a = \\Delta v / \\Delta t$.":
        "Starting from rest, a runner reaches 20 m/s after 4 s. Find the average acceleration in m/s$^2$ using $a = \\Delta v / \\Delta t$.",
    "A device delivers 150 J of useful energy from 300 J of total energy input. What is the efficiency as a percentage?":
        "A machine outputs 150 J of useful energy for every 300 J of energy supplied. Calculate its efficiency as a percentage.",
    "A 4 kg object is raised 10 m vertically near Earth's surface. What is the gravitational potential energy in joules? Use $g = 9.8$ m/s$^2$ and $E_p = mgh$.":
        "How much gravitational potential energy (in J) does a 4 kg mass gain when lifted 10 m? Use $g = 9.8$ m/s$^2$ and $E_p = mgh$.",
    "A 4.0 kg object moves at 3.0 m/s. Calculate its kinetic energy in joules using $E_k = \\frac{1}{2}mv^2$. Record to one decimal place.":
        "Determine the kinetic energy (in J) of a 4.0 kg object travelling at 3.0 m/s using $E_k = \\frac{1}{2}mv^2$. Record to one decimal place.",
    "A rectangular cell measures 4 μm × 4 μm × 4 μm. Surface area = $2(lw + lh + wh)$, volume = $lwh$. What is the surface-area-to-volume ratio rounded to one decimal?":
        "A cubic cell 4 μm on each side has surface area $2(lw + lh + wh)$ and volume $lwh$. What is its surface-area-to-volume ratio, rounded to one decimal?",
    "A compound light microscope has an eyepiece lens of 10× and an objective lens of 10×. What is the total magnification? Record a whole number.":
        "Using a compound light microscope, a student combines a 10× eyepiece with a 10× objective lens. What total magnification results? Record a whole number.",
    "In a microscope field of view, 8 of 40 plant cells show plasmolysis after placing the tissue in a hypertonic salt solution. What percent of cells are plasmolyzed? Express as a decimal rounded to one decimal place.":
        "Of 40 plant cells viewed, 8 show plasmolysis after the tissue is placed in a hypertonic salt solution. What percentage of the cells are plasmolyzed? Round to one decimal place.",
    "A leaf sample of 1 mm² contains 180 open stomata visible under the microscope. What is the stomatal density in stomata per mm²? Record a whole number.":
        "Across 1 mm² of leaf surface, 180 open stomata are counted under the microscope. What is the stomatal density in stomata per mm²? Record a whole number.",
    "A cube-shaped cell has edges of 2 μm. Surface area = 6 × edge² and volume = edge³. What is the surface-area-to-volume ratio? Express as a decimal rounded to two decimal places.":
        "A cube-shaped cell has 2 μm edges. Using surface area = 6 × edge² and volume = edge³, calculate its surface-area-to-volume ratio to two decimal places.",
    "A specimen measures 30 μm across. Under the microscope the image appears 120 μm wide. What is the magnification? Record a whole number.":
        "Under the microscope a 30 μm specimen produces an image 120 μm wide. Determine the magnification and record a whole number.",
    # grading ambiguity wording (idx 160)
    "In a microscope field of view, 12 of 50 plant cells show plasmolysis after placing the tissue in a hypertonic salt solution. What percent of cells are plasmolyzed? Express as a decimal rounded to one decimal place.":
        "In a field of view, 12 of 50 plant cells show plasmolysis in a hypertonic salt solution. What percentage of the cells are plasmolyzed? Round to one decimal place.",
    # strip artificial prefixes
    "Checkpoint: A device receives 750 J of energy and produces 300 J of useful output. What is the efficiency as a percentage? Record to one decimal place.":
        "A device receives 750 J of energy and produces 300 J of useful output. What is the efficiency as a percentage? Record to one decimal place.",
    "Review: How much thermal energy in joules is required to raise the temperature of 1.0 kg of water by 5°C? Use $c = 4200$ J/(kg·°C) and $Q = mc\\Delta T$.":
        "How much thermal energy in joules is required to raise the temperature of 1.0 kg of water by 5°C? Use $c = 4200$ J/(kg·°C) and $Q = mc\\Delta T$.",
}


def apply_fixes(bank: list[dict]) -> dict:
    counts = {"stems": 0, "distractors": 0, "explanations": 0}

    # Stems first (so later matches use new text where needed)
    for q in bank:
        for old, new in STEM_REWRITES.items():
            if q["question_text"] == old:
                q["question_text"] = new
                counts["stems"] += 1
                break

    for q in bank:
        stem = q["question_text"]
        # distractors
        for key, wrongs in DISTRACTORS.items():
            if key in stem:
                correct = [c for c in q["choices"] if c.get("is_correct")]
                if not correct:
                    break
                new_choices = [{"text": correct[0]["text"], "is_correct": True}]
                new_choices += [{"text": w, "is_correct": False} for w in wrongs]
                q["choices"] = new_choices
                counts["distractors"] += 1
                break
        # explanations
        for key, expl in EXPLANATIONS.items():
            if key in stem:
                q["explanation"] = expl
                counts["explanations"] += 1
                break
    return counts


def main() -> int:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    counts = apply_fixes(bank)
    BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")
    ALIAS.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Applied: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
