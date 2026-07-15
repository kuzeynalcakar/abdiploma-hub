"""Generate, validate, and export the Chemistry 30 question pool (~450 questions)."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from chem30_questions.helpers import mc, nr
from chem30_questions.unit_a import questions as unit_a
from chem30_questions.unit_b import questions as unit_b
from chem30_questions.unit_c import questions as unit_c
from chem30_questions.unit_d import questions as unit_d

OUTPUT = Path(__file__).parent.parent / "questions.json" / "chemistry30_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]

TOPIC_A = "Thermochemical Changes"
TOPIC_B = "Electrochemical Changes"
TOPIC_C = "Chemical Changes of Organic Compounds"
TOPIC_D = "Chemical Equilibrium Focusing on Acid-Base Systems"


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def deduplicate(items: list) -> list:
    seen = set()
    unique = []
    for item in items:
        key = (item["topic"].lower(), normalize_text(item["question_text"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def programmatic_supplements():
    """Parameterized original MC/NR questions to build the pool."""
    extra = []

    # --- Unit A: Calorimetry Q = mcΔT ---
    cal_data = [
        (50.0, 4.19, 2.00, 419),
        (75.0, 4.19, 4.00, 1257),
        (100.0, 4.19, 1.50, 629),
        (200.0, 4.19, 0.50, 419),
        (30.0, 4.19, 5.00, 629),
        (120.0, 4.19, 3.00, 1508),
        (80.0, 4.19, 2.50, 838),
        (60.0, 4.19, 6.00, 1508),
        (150.0, 4.19, 1.00, 629),
        (40.0, 4.19, 8.00, 1338),
        (90.0, 4.19, 3.50, 1320),
        (110.0, 4.19, 2.20, 1014),
        (25.0, 4.19, 10.0, 1048),
        (180.0, 4.19, 0.80, 603),
        (70.0, 4.19, 4.50, 1320),
    ]
    for mass, c, dt, q_j in cal_data:
        extra.append(nr(
            f"A calorimetry trial uses ${mass:.1f}\\ \\text{{g}}$ of water. "
            f"Specific heat capacity is ${c}\\ \\text{{J/(g·°C)}}$ and temperature rises by ${dt:.2f}\\ \\text{{°C}}$. "
            f"Calculate heat absorbed $Q$ in joules. Record as a whole number.",
            str(int(q_j)),
            f"$Q = mc\\Delta T = {mass} \\times {c} \\times {dt} = {q_j}\\ \\text{{J}}$.",
            f"Students may forget one factor in $Q=mc\\Delta T$ for the {mass} g sample.",
            topic=TOPIC_A, outcome_code="A1.1k",
            skill_tested=f"Calculating Q in joules for {mass} g water",
            difficulty="Medium", estimated_time_seconds=110,
        ))

    # Unit A: Molar enthalpy from total energy
    enthalpy_data = [
        (1.50, 285, 190),
        (0.500, 142, 284),
        (3.00, 540, 180),
        (2.50, 550, 220),
        (4.00, 720, 180),
        (0.250, 55.0, 220),
        (5.00, 1100, 220),
        (1.00, 73.5, 74),
        (2.00, 320, 160),
        (0.800, 144, 180),
    ]
    for mol, energy, molar_h in enthalpy_data:
        extra.append(nr(
            f"When ${mol}\\ \\text{{mol}}$ of a fuel is burned, ${energy}\\ \\text{{kJ}}$ of energy is released. "
            f"What is the molar enthalpy of combustion in kJ/mol? Record as a whole number.",
            str(molar_h),
            f"Molar enthalpy = ${energy}/{mol} = {molar_h}\\ \\text{{kJ/mol}}$.",
            f"Students may report {energy} kJ total instead of dividing by {mol} mol.",
            topic=TOPIC_A, outcome_code="A1.5k",
            skill_tested=f"Calculating molar enthalpy from {energy} kJ and {mol} mol",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    # Unit A: Hess's law sums
    hess_data = [
        (-100, 40, -60),
        (-250, 80, -170),
        (50, -30, 20),
        (-75, -25, -100),
        (120, -90, 30),
        (-200, 150, -50),
        (80, 20, 100),
        (-150, 60, -90),
        (30, 30, 60),
        (-400, 100, -300),
    ]
    for h1, h2, net in hess_data:
        extra.append(nr(
            f"Reaction step 1 has $\\Delta H_1 = {h1}\\ \\text{{kJ}}$ and step 2 has $\\Delta H_2 = {h2}\\ \\text{{kJ}}$. "
            f"What is the net $\\Delta H$ for the overall reaction? Record as a signed integer.",
            str(net),
            f"$\\Delta H_{{net}} = {h1} + ({h2}) = {net}\\ \\text{{kJ}}$.",
            "Students subtract instead of add step enthalpies.",
            topic=TOPIC_A, outcome_code="A1.7k",
            skill_tested="Summing step enthalpies using Hess's law",
            difficulty="Easy", estimated_time_seconds=80,
        ))

    # Unit A: Efficiency
    for useful, total in [(850, 1000), (680, 800), (425, 500), (1020, 1200), (340, 400),
                          (765, 900), (510, 600), (920, 1100), (275, 350), (1440, 1600)]:
        eff = round(useful / total * 100)
        extra.append(nr(
            f"A furnace delivers ${useful}\\ \\text{{kJ}}$ of useful heat from ${total}\\ \\text{{kJ}}$ of fuel energy. "
            f"What is the efficiency as a percentage? Record as a whole number.",
            str(eff),
            f"Efficiency = $({useful}/{total}) \\times 100 = {eff}\\%$.",
            "Students invert useful and total energy.",
            topic=TOPIC_A, outcome_code="A2.3s",
            skill_tested="Calculating furnace thermal efficiency",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Unit A: MC batch
    a_mc = [
        ("Enthalpy change $\\Delta H$ for a reaction is negative when the reaction is", "exothermic",
         ["endothermic", "at equilibrium with $\\Delta H = 0$ always", "impossible to measure"],
         "Negative $\\Delta H$ means energy released to surroundings.", "Students reverse sign convention.",
         "A1.5k", "Interpreting negative ΔH", "Easy", 60),
        ("Bond formation during a chemical reaction is", "exothermic",
         ["endothermic", "always zero energy change", "only endothermic in catalyzed reactions"],
         "Forming bonds releases energy; breaking bonds requires energy.", "Students confuse bond breaking with bond forming.",
         "A2.2k", "Classifying bond formation energy change", "Easy", 65),
        ("A reaction with activation energy of 50 kJ/mol and $\\Delta H$ of $-100$ kJ/mol is", "exothermic with an energy barrier of 50 kJ/mol",
         ["endothermic overall", "without any activation barrier", "at equilibrium with $\\Delta H = 0$"],
         "Negative $\\Delta H$ = exothermic; $E_a$ is separate barrier on diagram.", "Students think exothermic means no activation energy.",
         "A2.3k", "Distinguishing ΔH from activation energy", "Medium", 85),
        ("Enzymes in living systems function as", "biological catalysts lowering activation energy",
         ["oxidizing agents in all reactions", "sources of activation energy input", "products of cellular respiration only"],
         "Enzymes provide alternate pathways with lower $E_a$ without changing $\\Delta H$.", "Students think enzymes are consumed or change $\\Delta H$.",
         "A2.4k", "Describing enzyme catalytic role", "Medium", 80),
        ("Comparing coal and natural gas for home heating, natural gas generally produces", "fewer particulate emissions per unit energy",
         ["more soot per joule than coal always", "no carbon dioxide when burned", "only endothermic combustion"],
         "Natural gas burns more cleanly with less particulate matter than coal.", "Students think natural gas produces no CO$_2$.",
         "A1.1sts", "Comparing coal and natural gas emissions", "Medium", 85),
        ("Assessing fossil fuel reliance, a risk of continued dependence is", "depletion of non-renewable reserves and climate impacts",
         ["unlimited supply of all fossil fuels forever", "complete elimination of all energy costs", "increase in atmospheric nitrogen only"],
         "Fossil fuels are finite and combustion releases greenhouse gases.", "Students ignore resource limits and climate effects.",
         "A2.2sts", "Assessing fossil fuel sustainability risks", "Easy", 75),
        ("In an endothermic reaction plotted on an enthalpy diagram, products appear", "higher in energy than reactants",
         ["lower in energy than reactants", "at the same energy as activation energy", "below the x-axis always"],
         "Endothermic: energy absorbed, so products higher than reactants.", "Students invert endothermic diagram interpretation.",
         "A2.3k", "Reading endothermic profile on enthalpy diagram", "Easy", 70),
        ("The specific heat capacity of water ($4.19\\ \\text{J/(g·°C)}$) explains why water", "requires substantial heat to change temperature",
         ["changes temperature instantly with minimal heat", "cannot be used in calorimetry experiments", "has zero heat capacity"],
         "High $c$ means water absorbs much heat per degree of temperature change.", "Students think water heats up quickly with little energy.",
         "A1.1k", "Explaining significance of water's specific heat capacity", "Easy", 65),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in a_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit B: Oxidation numbers (NR) ---
    ox_data = [
        ("\\text{MnO}_4^-", 7),
        ("\\text{Cr}_2\\text{O}_7^{2-}", 6),
        ("\\text{NO}_3^-", 5),
        ("\\text{H}_2\\text{SO}_4 \\text{ (sulfur)}", 6),
        ("\\text{NH}_3 \\text{ (nitrogen)}", -3),
        ("\\text{ClO}_3^-", 5),
        ("\\text{Fe}_2\\text{O}_3 \\text{ (iron)}", 3),
        ("\\text{Na}_2\\text{S} \\text{ (sulfur)}", -2),
        ("\\text{K}_2\\text{CrO}_4 \\text{ (chromium)}", 6),
        ("\\text{PO}_4^{3-} \\text{ (phosphorus)}", 5),
        ("\\text{IO}_3^- \\text{ (iodine)}", 5),
        ("\\text{N}_2\\text{H}_4 \\text{ (nitrogen)}", -2),
        ("\\text{HClO} \\text{ (chlorine)}", 1),
        ("\\text{SnCl}_2 \\text{ (tin)}", 2),
        ("\\text{PbO}_2 \\text{ (lead)}", 4),
    ]
    for formula, ox in ox_data:
        extra.append(nr(
            f"What is the oxidation number of the highlighted element in {formula}? Record as a signed integer.",
            str(ox),
            f"Applying oxidation number rules gives {ox}.",
            "Students forget overall ion charge or assign standard values without calculation.",
            topic=TOPIC_B, outcome_code="B1.7k",
            skill_tested=f"Calculating oxidation number in {formula}",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit B: E°cell calculations
    cell_data = [
        (0.80, -0.25, 1.05),
        (1.36, 0.00, 1.36),
        (0.34, -0.44, 0.78),
        (0.77, -0.13, 0.90),
        (1.07, 0.34, 0.73),
        (0.52, -0.76, 1.28),
        (0.93, -0.28, 1.21),
        (1.23, 0.00, 1.23),
        (0.40, -0.93, 1.33),
        (0.15, -0.40, 0.55),
    ]
    for cathode, anode, ecell in cell_data:
        extra.append(nr(
            f"A voltaic cell has $E°_{{cathode}} = {cathode:+.2f}\\ \\text{{V}}$ and "
            f"$E°_{{anode}} = {anode:+.2f}\\ \\text{{V}}$. Calculate $E°_{{cell}}$ in V to two decimal places.",
            f"{ecell:.2f}",
            f"$E°_{{cell}} = {cathode} - ({anode}) = {ecell:.2f}\\ \\text{{V}}$.",
            "Students add potentials or subtract cathode from anode incorrectly.",
            topic=TOPIC_B, outcome_code="B2.6k",
            skill_tested="Computing standard cell potential from electrode values",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit B: Faraday charge/moles — compute answer from I×t/F
    faraday_data = [
        (1.00, 965), (2.00, 1930), (0.50, 4825), (3.00, 2895), (4.00, 3860),
        (0.25, 2413), (5.00, 9650), (1.50, 1448), (2.50, 4825), (0.10, 965),
    ]
    for current, time_s in faraday_data:
        mol_e = round(current * time_s / 96500, 2)
        extra.append(nr(
            f"During electrolysis, a current of ${current}\\ \\text{{A}}$ flows for ${time_s}\\ \\text{{s}}$. "
            f"How many moles of electrons pass through? Use $F = 96500\\ \\text{{C/mol}}$. Express to two decimal places.",
            f"{mol_e:.2f}",
            f"$Q = It = {current} \\times {time_s} = {current*time_s}\\ \\text{{C}}$. "
            f"Moles = ${current*time_s}/96500 = {mol_e:.2f}$.",
            f"Students may report {current*time_s} C as moles without dividing by Faraday's constant.",
            topic=TOPIC_B, outcome_code="B2.8k",
            skill_tested=f"Computing electron moles at {current} A for {time_s} s",
            difficulty="Hard", estimated_time_seconds=140,
        ))

    # Unit B: MC supplements
    b_mc = [
        ("When $\\text{Fe}^{2+}$ is oxidized to $\\text{Fe}^{3+}$, iron", "loses one electron",
         ["gains one electron", "loses three electrons always", "changes oxidation number to $-3$"],
         "Fe$^{2+}$ → Fe$^{3+}$ is loss of one electron (oxidation).", "Students confuse oxidation number change with electron count.",
         "B1.1k", "Identifying electron transfer in Fe²⁺ oxidation", "Easy", 65),
        ("A species that causes another to be oxidized while being reduced itself is the", "oxidizing agent",
         ["reducing agent", "spectator ion", "catalyst"],
         "Oxidizing agent is reduced; reducing agent is oxidized.", "Classic oxidizing/reducing agent confusion.",
         "B1.2k", "Defining oxidizing agent role", "Easy", 60),
        ("Photosynthesis and cellular respiration are redox partners because", "photosynthesis reduces CO$_2$ while respiration oxidizes glucose",
         ["neither involves electron transfer", "both only produce water without redox", "only respiration involves redox"],
         "Both processes involve electron transfer — opposite overall directions.", "Students think only respiration is redox.",
         "B1.4k", "Comparing redox in photosynthesis and respiration", "Medium", 85),
        ("Galvanizing iron with zinc protects against rust because zinc", "oxidizes preferentially as a sacrificial anode",
         ["prevents all oxygen from contacting iron", "is a stronger oxidizing agent than iron", "converts iron to stainless steel"],
         "Zinc corrodes first, protecting iron cathode.", "Students think zinc coats without electrochemical action.",
         "B1.1sts", "Explaining galvanizing corrosion protection", "Medium", 80),
        ("In electrolytic refining of copper, impure copper is the", "anode that dissolves as Cu oxidizes to Cu$^{2+}$",
         ["cathode where Cu$^{2+}$ deposits", "salt bridge", "inert spectator electrode only"],
         "Impure Cu anode dissolves; pure Cu deposits on cathode.", "Students reverse anode and cathode in refining.",
         "B2.1sts", "Identifying electrodes in copper refining", "Medium", 90),
        ("A battery producing 1.5 V from Zn and Cu electrodes is an example of", "a voltaic cell converting chemical energy to electrical energy",
         ["an electrolytic cell requiring external power", "a fuel cell using continuous H$_2$ supply only", "a nuclear reactor"],
         "Voltaic cells spontaneously produce voltage from redox.", "Students confuse voltaic and electrolytic cells.",
         "B2.2k", "Classifying common battery as voltaic cell", "Easy", 65),
        ("Overvoltage during electrolysis explains why", "actual electrode reactions may differ from E° predictions",
         ["E° values are always exactly equal to measured cell potentials", "equilibrium constants change with overvoltage", "catalysts are never needed in electrolysis"],
         "Extra voltage needed at electrode interface can change reaction order.", "Students assume E° perfectly predicts electrolysis products.",
         "B2.4k", "Explaining overvoltage significance", "Hard", 110),
        ("Redox titration of $\\text{Fe}^{2+}$ with $\\text{MnO}_4^-$ in acidic solution requires", "acidic conditions to drive the permanganate half-reaction",
         ["basic conditions exclusively", "no acid or base ever", "only inert gas atmosphere"],
         "MnO$_4^-$ reduction in acid produces Mn$^{2+}$; basic conditions give different products.", "Students titrate permanganate in basic medium.",
         "B1.8k", "Identifying acidic conditions for permanganate titration", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in b_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_B, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit C: Naming MC ---
    naming_data = [
        ("\\text{CH}_3\\text{CH}_2\\text{CH}_2\\text{CH}_3", "butane", ["propane", "pentane", "2-methylpropane"]),
        ("\\text{CH}_3\\text{CH}=\\text{CH}_2", "propene", ["propane", "propyne", "cyclopropane"]),
        ("\\text{CH}_3\\text{COOCH}_3", "methyl ethanoate", ["ethanol", "ethanoic acid", "methoxyethane"]),
        ("\\text{CH}_3\\text{CH}_2\\text{Cl}", "chloroethane", ["chloromethane", "1-chloropropane", "ethane"]),
        ("\\text{CH}_3\\text{CH}_2\\text{CH}_2\\text{CHO}", "butanal", ["butanol", "butanoic acid", "butanone"]),
        ("\\text{CH}_3\\text{OCH}_3", "methoxymethane", ["ethanol", "methanal", "ethanoic acid"]),
        ("\\text{CH}_3\\text{CH(OH)CH}_3", "propan-2-ol", ["propan-1-ol", "propanone", "propanoic acid"]),
        ("\\text{CH}_3\\text{CH}_2\\text{CH}_2\\text{OH}", "propan-1-ol", ["propane", "propanal", "propanoic acid"]),
    ]
    for struct, name, distractors in naming_data:
        extra.append(mc(
            f"What is the correct IUPAC name for {struct}?",
            name,
            distractors,
            f"The structure {struct} is named {name} by IUPAC rules.",
            "Students misidentify functional group priority or parent chain length.",
            topic=TOPIC_C, outcome_code="C1.3k",
            skill_tested=f"IUPAC naming of structure {struct}",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # More naming with unique structures
    more_names = [
        ("2-methylbutane", ["pentane", "3-methylpentane", "2,2-dimethylpropane"],
         "Longest chain is 4 (butane) with methyl on C-2."),
        ("pent-2-ene", ["pent-1-ene", "pentane", "cyclopentane"],
         "Five-carbon chain with double bond at position 2."),
        ("3-methylpentane", ["2-methylpentane", "hexane", "2,2-dimethylbutane"],
         "Parent chain is 5 carbons with methyl at position 3."),
        ("cyclohexane", ["hexane", "cyclohexene", "benzene"],
         "Six-carbon saturated ring."),
        ("methyl propanoate", ["propyl methanoate", "butanoic acid", "propan-1-ol"],
         "Ester: methyl group from methanol + propanoate from propanoic acid."),
        ("2-chlorobutane", ["1-chlorobutane", "butane", "2-bromobutane"],
         "Four-carbon chain with Cl on carbon 2."),
        ("butan-2-one", ["butanal", "butanoic acid", "butan-1-ol"],
         "Ketone with carbonyl on carbon 2 of four-carbon chain."),
        ("ethoxyethane", ["ethanol", "diethyl ether common name", "ethanoic acid"],
         "Two ethyl groups linked by oxygen: ethoxyethane."),
    ]
    for correct, wrong, reason in more_names:
        extra.append(mc(
            f"Which IUPAC name is correct for the described structure: {reason}",
            correct,
            wrong,
            f"By IUPAC rules, the correct name is {correct} because {reason}",
            "Students select names with wrong parent chain or functional group suffix.",
            topic=TOPIC_C, outcome_code="C1.3k",
            skill_tested=f"Selecting correct IUPAC name: {correct}",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Unit C: Carbon count and formula NR
    for carbons, h, formula_desc in [(3, 8, "propane"), (4, 10, "butane"), (5, 12, "pentane"),
                                      (6, 14, "hexane"), (7, 16, "heptane"), (8, 18, "octane")]:
        extra.append(nr(
            f"An alkane {formula_desc} has how many hydrogen atoms in its molecular formula? Record as a two-digit integer.",
            str(h),
            f"Alkane C$_n$H$_{{2n+2}}$: for $n={carbons}$, H = ${h}$.",
            "Students use $2n$ instead of $2n+2$ for alkanes.",
            topic=TOPIC_C, outcome_code="C1.5k",
            skill_tested=f"Determining hydrogen count in {formula_desc}",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # Unit C: MC reaction types and properties
    c_mc = [
        ("Ethene reacts with H$_2$ in the presence of a nickel catalyst to produce", "ethane",
         ["ethanol", "ethyne", "polyethylene directly"],
         "H$_2$ addition across C=C: ethene → ethane (hydrogenation).", "Students confuse addition with substitution.",
         "C2.2k", "Predicting hydrogenation product of ethene", "Easy", 70),
        ("Heating ethanol with concentrated H$_2$SO$_4$ at high temperature can produce", "ethene and water",
         ["sodium ethoxide and H$_2$", "ethanoic acid only with no elimination", "polyethylene immediately"],
         "Acid-catalyzed dehydration of alcohol is elimination: ethene + H$_2$O.", "Students predict substitution or polymerization.",
         "C2.1k", "Identifying elimination in alcohol dehydration", "Medium", 85),
        ("The polymer formed from propene monomers is", "polypropene",
         ["polyethylene", "polystyrene", "nylon"],
         "Propene (CH$_3$CH=CH$_2$) polymerizes to polypropene.", "Students name wrong polymer for given monomer.",
         "C2.3k", "Naming polymer from propene monomer", "Easy", 65),
        ("Fractional distillation of crude oil separates components at different heights because", "compounds have different boiling points",
         ["all hydrocarbons have identical boiling points", "density alone determines tower position without temperature", "catalysts at each tray change molecular formulas"],
         "Lower boiling fractions rise higher; higher boiling collect lower in tower.", "Students cite density alone without boiling point.",
         "C1.7k", "Explaining fractional distillation tower separation", "Easy", 70),
        ("1-butanol has a higher boiling point than butane primarily because", "butanol forms hydrogen bonds between molecules",
         ["butane has larger molar mass", "butane is ionic", "butanol is non-polar"],
         "H-bonding in alcohols requires more energy to vaporize than London forces in alkanes.", "Students cite molar mass without considering H-bonding.",
         "C1.6k", "Explaining boiling point difference: alcohol vs alkane", "Medium", 90),
        ("Isomers with the same molecular formula but different structures are called", "structural isomers",
         ["geometric isomers only", "allotropes of carbon", "ionic compounds"],
         "Structural isomerism: same formula, different connectivity.", "Students confuse structural with stereoisomers.",
         "C1.5k", "Defining structural isomerism", "Easy", 60),
        ("Complete combustion of propane produces", "CO$_2$ and H$_2$O",
         ["CO only with no water", "C and H$_2$O without oxygen", "CH$_4$ and O$_2$"],
         "C$_3$H$_8$ + 5O$_2$ → 3CO$_2$ + 4H$_2$O (complete combustion).", "Students predict incomplete combustion products.",
         "C2.2k", "Predicting propane combustion products", "Easy", 65),
        ("Esterification is best described as", "a condensation reaction between an alcohol and carboxylic acid producing ester and water",
         ["addition of water across a double bond", "complete combustion of an ester", "substitution of all hydrogens with chlorine"],
         "Acid + alcohol → ester + H$_2$O.", "Students confuse esterification with hydrolysis or combustion.",
         "C2.1k", "Defining esterification reaction type", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in c_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_C, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit D: pH calculations ---
    ph_data = [
        (1e-2, 2.00), (1e-5, 5.00), (1e-7, 7.00), (1e-9, 9.00), (1e-11, 11.00),
        (1e-3, 3.00), (1e-6, 6.00), (1e-8, 8.00), (1e-10, 10.00), (1e-12, 12.00),
        (5.0e-4, 3.30), (2.0e-5, 4.70), (3.0e-3, 2.52), (8.0e-6, 5.10), (4.0e-9, 8.40),
    ]
    for conc, ph in ph_data:
        exp = f"{conc:.1e}" if conc < 0.01 else str(conc)
        extra.append(nr(
            f"Calculate the pH of a solution with $[\\text{{H}}_3\\text{{O}}^+] = {exp}\\ \\text{{mol/L}}$. "
            f"Express to two decimal places.",
            f"{ph:.2f}",
            f"pH = $-\\log({exp}) = {ph:.2f}$.",
            "Students use concentration directly as pH without taking negative log.",
            topic=TOPIC_D, outcome_code="D2.1k",
            skill_tested="Calculating pH from hydronium ion concentration",
            difficulty="Easy" if ph in (2, 3, 5, 6, 7, 9, 10, 11, 12) else "Medium",
            estimated_time_seconds=75,
        ))

    # Unit D: pOH from pH
    for ph in [2.0, 3.5, 5.0, 7.0, 8.5, 10.0, 11.5, 12.0, 4.0, 6.0, 9.0, 13.0]:
        poh = round(14.0 - ph, 2)
        extra.append(nr(
            f"At 25°C, a solution has pH = {ph:.1f}. What is the pOH? Express to two decimal places.",
            f"{poh:.2f}",
            f"pOH = 14.00 - {ph:.1f} = {poh:.2f}$.",
            "Students add pH + pOH incorrectly or forget to subtract from 14.",
            topic=TOPIC_D, outcome_code="D2.1k",
            skill_tested="Calculating pOH from pH at 25°C",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Unit D: Ka/Kb from Kw
    ka_kb_data = [
        (1.8e-5, 5.6e-10),
        (6.8e-4, 1.5e-11),
        (1.0e-3, 1.0e-11),
        (7.4e-4, 1.4e-11),
        (4.5e-5, 2.2e-10),
        (2.0e-6, 5.0e-9),
        (3.5e-4, 2.9e-11),
        (9.0e-5, 1.1e-10),
        (5.0e-10, 2.0e-5),
        (1.0e-8, 1.0e-6),
    ]
    for ka, kb in ka_kb_data:
        coeff = float(f"{kb:.1e}".split("e")[0])
        extra.append(nr(
            f"A weak acid has $K_a = {ka:.1e}$ at 25°C. What is $K_b$ for its conjugate base? "
            f"Record the mantissa (coefficient) of $K_b$ in scientific notation to one decimal place.",
            f"{coeff:.1f}",
            f"$K_b = 1.0 \\times 10^{{-14}} / ({ka:.1e}) = {kb:.1e}$. Mantissa = {coeff:.1f}.",
            "Students multiply Ka × Kb or invert the division.",
            topic=TOPIC_D, outcome_code="D2.2k",
            skill_tested="Determining Kb mantissa from Ka",
            difficulty="Medium", estimated_time_seconds=115,
        ))

    # Unit D: Kc calculations
    kc_data = [
        (0.10, 0.10, 0.20, 2.0),   # A+B<->C: 0.2/(0.1*0.1)=200 - let me use simpler
        (0.50, 0.50, 0.25, 1.0),   # 2A<->B: K = 0.25/0.25 = 1.0
        (0.20, 0.30, 0.10, 1.67),  # A+B<->C: 0.1/(0.2*0.3)=1.67
        (1.0, 1.0, 2.0, 2.0),      # A+B<->2C: 4/(1*1)=4 - need fix
        (0.40, 0.40, 0.16, 1.0),   # 2A<->B: 0.16/0.16=1
        (0.60, 0.20, 0.15, 1.25),  # A+2B<->C: 0.15/(0.6*0.04)=6.25
        (0.80, 0.10, 0.05, 0.63),  # A+B<->C: 0.05/0.08=0.625
        (0.30, 0.30, 0.09, 1.0),   # 2A<->B: 0.09/0.09=1
        (0.25, 0.40, 0.20, 2.0),   # A+B<->C: 0.2/0.1=2
        (0.10, 0.20, 0.04, 2.0),   # 2A<->B: 0.04/0.01=4
    ]
    # Use simple A + B <=> C for clarity
    simple_kc = [
        ((0.20, 0.30, 0.06), 1.0),
        ((0.50, 0.40, 0.20), 1.0),
        ((0.10, 0.10, 0.05), 5.0),
        ((0.80, 0.50, 0.60), 1.5),
        ((0.25, 0.25, 0.10), 1.6),
        ((0.60, 0.20, 0.24), 2.0),
        ((0.40, 0.10, 0.08), 2.0),
        ((0.15, 0.35, 0.0525), 1.0),
        ((0.70, 0.30, 0.42), 2.0),
        ((0.05, 0.05, 0.01), 4.0),
    ]
    for (a, b, c), kc in simple_kc:
        extra.append(nr(
            f"For $\\text{{A}}(g) + \\text{{B}}(g) \\rightleftharpoons \\text{{C}}(g)$, equilibrium concentrations are "
            f"$[\\text{{A}}] = {a}\\ \\text{{mol/L}}$, $[\\text{{B}}] = {b}\\ \\text{{mol/L}}$, "
            f"$[\\text{{C}}] = {c}\\ \\text{{mol/L}}$. Calculate $K_c$ to one decimal place.",
            f"{kc:.1f}",
            f"$K_c = [{c}]/([{a}][{b}]) = {c}/({a*b}) = {kc:.1f}$.",
            "Students invert the expression or forget product/reactant placement.",
            topic=TOPIC_D, outcome_code="D2.3k",
            skill_tested="Calculating Kc for A + B ⇌ C equilibrium",
            difficulty="Medium", estimated_time_seconds=120,
        ))

    # Unit D: MC supplements
    d_mc = [
        ("Adding a catalyst to $\\text{N}_2(g) + 3\\text{H}_2(g) \\rightleftharpoons 2\\text{NH}_3(g)$ at equilibrium will",
         "increase the rate of approach to equilibrium without changing $K_c$",
         ["shift equilibrium toward more NH$_3$", "decrease $K_c$ at higher temperature", "prevent any reaction from occurring"],
         "Catalysts affect kinetics, not thermodynamic position.", "Students think catalysts shift equilibrium toward products.",
         "D1.3k", "Predicting catalyst effect on ammonia equilibrium", "Easy", 65),
        ("For an endothermic equilibrium, decreasing temperature will", "decrease $K_c$ and favour reactants",
         ["increase $K_c$", "have no effect on equilibrium position", "always produce more product"],
         "Endothermic + decrease T favours reactants; K decreases.", "Students think all temperature decreases favour products.",
         "D1.3k", "Predicting temperature effect on endothermic Kc", "Medium", 90),
        ("The conjugate acid of $\\text{H}_2\\text{O}$ is", "$\\text{H}_3\\text{O}^+$",
         ["$\\text{OH}^-$", "$\\text{O}^{2-}$", "$\\text{H}_2\\text{O}$ itself cannot have a conjugate acid"],
         "Water accepts H$^+$ to form H$_3$O$^+$ (conjugate acid).", "Students select hydroxide as conjugate acid.",
         "D1.7k", "Identifying conjugate acid of water", "Easy", 60),
        ("A solution with pH = 11 is", "basic",
         ["acidic", "neutral", "amphiprotic always"],
         "pH > 7 indicates basic solution at 25°C.", "Students think high pH means acidic.",
         "D2.1k", "Classifying solution acidity from pH", "Easy", 55),
        ("In $\\text{HF}(aq) + \\text{H}_2\\text{O}(l) \\rightleftharpoons \\text{F}^-(aq) + \\text{H}_3\\text{O}^+(aq)$, HF acts as",
         "a Brønsted-Lowry acid",
         ["a Brønsted-Lowry base only", "a spectator ion", "an amphiprotic base in this reaction only"],
         "HF donates H$^+$ to water — acid.", "Students think all fluorine compounds are bases.",
         "D1.5k", "Identifying HF as Brønsted-Lowry acid", "Easy", 60),
        ("The Solvay process produces sodium carbonate using equilibrium principles by",
         "manipulating CO$_2$, NH$_3$, and NaCl concentrations to precipitate NaHCO$_3$",
         ["electrolysis of molten NaCl only without equilibria", "combustion of sodium metal in air", "fractional distillation of brine"],
         "Solvay process uses coupled equilibria and precipitation.", "Students confuse Solvay with chlor-alkali electrolysis.",
         "D1.3sts", "Describing Solvay process equilibrium application", "Medium", 85),
        ("A strong acid-strong base titration curve shows a buffer region", "nowhere — neither reactant is a weak acid or base",
         ["throughout the entire curve from start to finish", "only after equivalence point exclusively", "at the equivalence point only"],
         "Buffers require weak acid/base pairs; SA/SB titration has no buffer region.", "Students see flat regions and call all buffers.",
         "D1.8k", "Recognizing absence of buffer in SA/SB titration", "Medium", 85),
        ("When $\\text{Ag}^+(aq)$ is added to remove $\\text{Cl}^-(aq)$ from equilibrium, this stress is best described as",
         "removal of a product (or reactant depending on equation) by precipitation",
         ["addition of an inert gas at constant volume", "increase in temperature only", "addition of a catalyst"],
         "Ag$^+$ + Cl$^-$ → AgCl(s) removes Cl$^-$ from solution, shifting equilibria involving Cl$^-$.", "Students do not recognize precipitation as concentration removal.",
         "D1.3k", "Identifying precipitation as Le Châtelier stress", "Hard", 105),
        ("For a diprotic acid H$_2$A, the second ionization constant $K_{a2}$ is typically much smaller than $K_{a1}$ because",
         "removing a proton from a negatively charged species is more difficult",
         ["the first proton is always stronger", "diprotic acids do not ionize twice", "K values are always equal for both steps"],
         "Electrostatic repulsion makes second proton removal harder.", "Students think both protons ionize equally.",
         "D1.6k", "Explaining why Ka2 is smaller than Ka1", "Hard", 110),
        ("Industrial methanol production from CO and H$_2$ is an equilibrium process where high pressure",
         "favours product formation (fewer gas moles on product side in some conditions)",
         ["always decreases yield regardless of stoichiometry", "has no effect on gaseous equilibria", "eliminates the need for a catalyst"],
         "Pressure effects depend on mole counts of gaseous species on each side.", "Students apply pressure rules without checking gas mole balance.",
         "D1.3sts", "Applying pressure principle to methanol synthesis", "Medium", 90),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in d_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_D, outcome_code=oc,
                          skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Additional bulk MC to reach target — varied contexts per unit
    bulk_a = [
        ("Standard enthalpy of formation data in the Data Booklet is used to calculate", "$\\Delta H$ for a reaction via $\\sum n\\Delta H_f°(products) - \\sum n\\Delta H_f°(reactants)$",
         ["equilibrium constants directly", "oxidation numbers of all species", "pH of combustion products"]),
        ("Liquid water as a combustion product in a bomb calorimeter means the measured energy includes", "energy to condense water vapour if formed, or liquid water heat content",
         ["only gas phase water energy always", "no water-related energy terms", "activation energy of the reaction"]),
        ("Renewable alternatives to fossil fuels include", "bioethanol and biodiesel from biomass",
         ["only coal and bitumen", "nuclear fusion in car engines", "infinite petroleum regeneration"]),
        ("A student measures temperature rise of 5.0°C for 100 g water absorbing 2090 J. The calculated $c$ in J/(g·°C) is approximately", "4.19",
         ["0.42", "20.9", "418"]),
    ]
    for i, (qt, ans, distractors) in enumerate(bulk_a):
        extra.append(mc(qt, ans, distractors, f"The correct answer is {ans}.",
                        "Students select distractors from incomplete analysis.",
                        topic=TOPIC_A, outcome_code="A1.6k" if i == 0 else "A1.8k" if i == 1 else "A1.1sts" if i == 2 else "A1.1k",
                        skill_tested="Thermochemistry conceptual application",
                        difficulty="Medium", estimated_time_seconds=80))

    # Expand with more parameterized unique questions across units
    # Unit B: Redox titration variations
    for vol, conc, mmol in [(20.0, 0.0150, 0.30), (30.0, 0.0200, 0.60), (15.0, 0.0400, 0.60),
                            (25.0, 0.0300, 0.75), (10.0, 0.0500, 0.50), (35.0, 0.0100, 0.35),
                            (40.0, 0.0250, 1.00), (22.5, 0.0200, 0.45), (18.0, 0.0350, 0.63),
                            (12.5, 0.0400, 0.50)]:
        extra.append(nr(
            f"A ${vol:.1f}\\ \\text{{mL}}$ aliquot of $\\text{{Fe}}^{{2+}}$ solution with concentration "
            f"${conc:.4f}\\ \\text{{mol/L}}$ is titrated with $\\text{{MnO}}_4^-$ (1:1 ratio). "
            f"How many millimoles of $\\text{{MnO}}_4^-$ are required? Express to two decimal places.",
            f"{mmol:.2f}",
            f"mmol = ${vol} \\times {conc} = {mmol:.2f}$ (mL × mol/L = mmol).",
            "Students forget mL numerically equals mmol when concentration is mol/L.",
            topic=TOPIC_B, outcome_code="B1.8k",
            skill_tested="Calculating permanganate titrant millimoles",
            difficulty="Medium", estimated_time_seconds=110,
        ))

    # Unit B: Mass from Faraday (1:1 mole ratio, M=63.5 Cu)
    for current, time_s, mass in [(2.0, 965, 0.635), (1.0, 1930, 1.27), (3.0, 965, 0.953),
                                   (0.5, 3860, 1.27), (4.0, 482.5, 0.635), (1.5, 1287, 0.635)]:
        extra.append(nr(
            f"Electrolysis of $\\text{{Cu}}^{{2+}}$ deposits copper (molar mass $63.5\\ \\text{{g/mol}}$) "
            f"with current ${current}\\ \\text{{A}}$ for ${time_s}\\ \\text{{s}}$. "
            f"How many grams of Cu are deposited? Use $F = 96500\\ \\text{{C/mol}}$ and 2 electrons per Cu. "
            f"Express to two decimal places.",
            f"{mass:.2f}",
            f"Moles e$^-$ = ${current*time_s}/96500$. Moles Cu = moles e$^-$/2. Mass = moles × 63.5.",
            "Students use 1 electron per Cu or forget molar mass.",
            topic=TOPIC_B, outcome_code="B2.8k",
            skill_tested="Calculating copper mass deposited by electrolysis",
            difficulty="Hard", estimated_time_seconds=160,
        ))

    # Unit C: More organic MC
    org_bulk = [
        ("Polyvinyl chloride (PVC) is produced from", "chloroethene (vinyl chloride) monomers",
         ["ethylene only without chlorine", "benzene rings exclusively", "methane gas directly"]),
        ("Hydrocracking in a refinery converts", "heavy hydrocarbons to lighter, more valuable products",
         ["metals to hydrocarbons", "water to organic acids", "CO$_2$ to glucose directly"]),
        ("An ester functional group contains the linkage", "$-\\text{COO}-$",
         ["$-OH$ only", "$-COOH$ without oxygen bridge", "$-NH-$"]),
        ("Aldehydes differ from ketones because aldehydes", "have a carbonyl at the end of the carbon chain",
         ["never contain oxygen", "always form polymers", "cannot undergo any oxidation"]),
        ("Glucose (C$_6$H$_{12}$O$_6$) is an example of", "a biologically important organic compound",
         ["an inorganic carbonate", "a noble gas", "a strong mineral acid"]),
        ("Saturated fats contain", "only carbon-carbon single bonds in their fatty acid chains",
         ["many carbon-carbon double bonds", "no carbon atoms", "ionic bonds between chains"]),
        ("Trans fats are associated with health concerns because they", "may increase cardiovascular disease risk",
         ["contain no carbon atoms", "are essential nutrients required in large amounts", "prevent all chemical reactions in the body"]),
        ("Nanotechnology in the petrochemical industry may", "develop catalysts with higher surface area for more efficient reactions",
         ["eliminate all carbon emissions instantly", "replace all organic chemistry with physics", "prevent all polymer formation"]),
    ]
    oc_map = ["C2.3k", "C2.1sts", "C1.4k", "C1.4k", "C1.2k", "C1.3k", "C2.3sts", "C2.1sts"]
    for (qt, ans, distractors), oc in zip(org_bulk, oc_map):
        extra.append(mc(qt, ans, distractors,
                        f"Outcome {oc}: {ans} is best supported by Alberta organic chemistry expectations.",
                        f"Students may confuse related concepts tested under outcome {oc}.",
                        topic=TOPIC_C, outcome_code=oc, skill_tested=f"Applying {oc} organic chemistry concept",
                        difficulty="Medium", estimated_time_seconds=80))

    # Fix pOH exponent answers — remove broken intermediate block
    extra = [q for q in extra if not (
        q.get("topic") == TOPIC_D and "exponent only" in q.get("question_text", "")
    )]
    for poh in [3.0, 5.0, 7.0, 9.0, 11.0, 4.0, 6.0, 8.0, 10.0, 12.0]:
        extra.append(nr(
            f"A solution at 25°C has pOH = {poh:.1f}. Calculate $[\\text{{OH}}^-]$ in mol/L. "
            f"Express in scientific notation with coefficient 1.0 (record the power of 10 as a signed integer).",
            str(int(-poh)),
            f"$[\\text{{OH}}^-] = 10^{{-{poh:.1f}}}\\ \\text{{mol/L}}$; exponent = $-{int(poh)}$.",
            "Students confuse pOH with [OH⁻] magnitude.",
            topic=TOPIC_D, outcome_code="D2.1k",
            skill_tested="Relating pOH to hydroxide ion concentration",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    extra.extend(_pool_expansion())
    return extra


def _pool_expansion():
    """Additional original questions to reach ~450 pool size."""
    more = []

    # Unit A: heat from temperature change (unique values)
    for mass, dt, q_kj in [(45, 8.0, 1.51), (55, 6.5, 1.50), (65, 5.0, 1.36),
                           (85, 4.0, 1.42), (95, 3.5, 1.39), (105, 3.0, 1.32),
                           (115, 2.5, 1.20), (125, 2.0, 1.05), (135, 1.8, 1.02),
                           (145, 1.5, 0.91)]:
        more.append(nr(
            f"${mass}\\ \\text{{g}}$ of water ($c = 4.19\\ \\text{{J/(g·°C)}}$) is heated by ${dt}\\ \\text{{°C}}$. "
            f"Calculate heat absorbed in kJ to two decimal places.",
            f"{q_kj:.2f}",
            f"$Q = {mass} \\times 4.19 \\times {dt}/1000 = {q_kj:.2f}\\ \\text{{kJ}}$.",
            "Students forget to convert joules to kilojoules.",
            topic=TOPIC_A, outcome_code="A1.8k",
            skill_tested="Calculating calorimetry heat in kJ",
            difficulty="Medium", estimated_time_seconds=115,
        ))

    # Unit A: MC expansion
    a_more = [
        ("Molar enthalpy of vaporization differs from molar enthalpy of combustion because vaporization involves",
         "overcoming intermolecular forces without breaking covalent bonds within molecules",
         ["breaking all C-C covalent bonds in the fuel", "forming new ionic compounds", "nuclear fusion of hydrogen"]),
        ("The Data Booklet standard enthalpies of formation are defined at",
         "25°C and 1 atm for standard states",
         ["0 K only", "any temperature students choose", "100°C exclusively"]),
        ("A student plots temperature vs time during a phase change at constant pressure. The flat region indicates",
         "energy is used to break intermolecular forces without temperature change",
         ["no energy transfer occurs", "covalent bonds within molecules are breaking", "the reaction has reached equilibrium with K > 1"]),
        ("Biomass fuels are considered renewable because",
         "they can be replenished on human timescales through photosynthesis",
         ["they contain no carbon atoms", "they never produce CO₂ when burned", "they are elements in standard states"]),
        ("In an energy diagram, the peak between reactants and products represents",
         "the activated complex at maximum potential energy",
         ["the final equilibrium constant", "the pH of the reaction mixture", "the concentration of products at completion"]),
        ("Neutralization of a strong acid and strong base in a calorimeter measures",
         "enthalpy of neutralization (exothermic)",
         ["standard reduction potential", "equilibrium constant Kc", "activation energy of combustion"]),
        ("When comparing fuels, molar enthalpy of combustion allows fair comparison of",
         "energy released per mole of fuel burned",
         ["energy per gram only without mole conversion", "activation energy of each fuel", "oxidation number of carbon only"]),
        ("A reaction with small positive $\\Delta H$ and large $E_a$ at room temperature will",
         "proceed very slowly despite being only slightly endothermic",
         ["proceed instantly to completion", "have $\\Delta H$ equal to $E_a$", "not require any collision energy"]),
        ("Thermal power plant efficiency is limited partly because",
         "some energy is lost as waste heat to the environment",
         ["all fuel energy converts to electricity with no losses", "enthalpy of formation is zero for all fuels", "catalysts are not used in combustion"]),
        ("Linking Chemistry 30 to daily life, the energy content on food labels relates to",
         "enthalpy of combustion of macronutrients",
         ["equilibrium constants of proteins", "oxidation numbers of vitamins only", "Faraday's law in digestion"]),
    ]
    for qt, ans, distractors in a_more:
        more.append(mc(qt, ans, distractors, f"{ans} correctly describes this thermochemistry concept.",
                        "Students confuse related but distinct energy concepts.",
                        topic=TOPIC_A, outcome_code="A1.3k",
                        skill_tested="Applying thermochemistry concepts to contexts",
                        difficulty="Medium", estimated_time_seconds=85))

    # Unit B: oxidation MC expansion
    b_more = [
        ("In the reaction $\\text{Zn}(s) + \\text{Cu}^{2+}(aq) \\rightarrow \\text{Zn}^{2+}(aq) + \\text{Cu}(s)$, the reducing agent is",
         "Zn(s)", ["Cu$^{2+}$(aq)", "Cu(s)", "Zn$^{2+}$(aq)"]),
        ("Electrons flow in the external circuit of a voltaic cell from",
         "anode to cathode through the wire", ["cathode to anode through the salt bridge", "salt bridge to anode only", "electrolyte directly without electrodes"]),
        ("During discharge of a lead-acid battery, the anode reaction involves",
         "oxidation of Pb to PbSO$_4$", ["reduction of Pb$^{2+}$ to Pb metal", "oxidation of H$_2$O to O$_2$ only", "precipitation of NaCl"]),
        ("Standard electrode potentials in the Data Booklet assume",
         "1.0 mol/L aqueous ions and 25°C", ["0 mol/L all species", "100°C always", "gas pressures of 10 atm"]),
        ("A non-spontaneous electrolytic reaction requires",
         "external voltage exceeding the cell's decomposition potential", ["only a salt bridge without power", "spontaneous electron flow from anode", "zero current at all times"]),
        ("Corrosion of iron in moist air is accelerated because water and oxygen",
         "act as oxidizing agents forming rust", ["prevent all electron transfer", "convert iron to a noble metal", "lower activation energy to zero"]),
        ("In a Daniell cell, $\\text{Cu}^{2+}$ is reduced at the cathode. The cathode electrode is",
         "copper metal", ["zinc metal", "platinum only always", "the salt bridge"]),
        ("Reducing agents are located on the ___ side of a standard reduction potential table (higher tendency to lose electrons).",
         "upper (more negative E° half-reactions)", ["lower (most positive E° only)", "middle exclusively", "table has no pattern"]),
        ("Electrolysis of molten NaCl produces sodium at the cathode because",
         "Na$^+$ ions are reduced to Na(l)", ["Cl$^-$ is reduced to Cl$_2$ at cathode", "water is always reduced first", "no redox occurs"]),
        ("A 1.10 V voltaic cell under standard conditions indicates",
         "a spontaneous reaction with positive E°cell", ["a non-spontaneous reaction", "equilibrium with no net reaction", "zero electron flow always"]),
    ]
    for qt, ans, distractors in b_more:
        more.append(mc(qt, ans, distractors, f"{ans} is correct.",
                        "Students confuse electrode identities or electron flow direction.",
                        topic=TOPIC_B, outcome_code="B2.1k",
                        skill_tested="Electrochemical cell conceptual analysis",
                        difficulty="Medium", estimated_time_seconds=90))

    # Unit B: more E°cell NR
    for c, a, e in [(0.22, -0.76, 0.98), (0.34, -0.25, 0.59), (1.07, 0.34, 0.73),
                    (0.77, -0.44, 1.21), (0.52, 0.00, 0.52), (0.93, 0.34, 0.59),
                    (1.36, 0.77, 0.59), (0.15, -0.93, 1.08), (0.40, -0.25, 0.65),
                    (0.80, -0.13, 0.93)]:
        more.append(nr(
            f"Calculate $E°_{{cell}}$ in V to two decimal places if $E°_{{cathode}} = {c:+.2f}\\ \\text{{V}}$ "
            f"and $E°_{{anode}} = {a:+.2f}\\ \\text{{V}}$.",
            f"{e:.2f}",
            f"$E°_{{cell}} = {c} - ({a}) = {e:.2f}\\ \\text{{V}}$.",
            "Students add electrode potentials instead of subtracting.",
            topic=TOPIC_B, outcome_code="B2.6k",
            skill_tested="Computing E°cell from electrode potentials",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    # Unit C: naming and reactions MC
    c_more = [
        ("The condensed structural formula CH$_3$CH$_2$CH$_2$CH$_2$CH$_3$ represents", "pentane",
         ["butane", "hexane", "2-methylpentane"]),
        ("An alkene functional group is characterized by", "a carbon-carbon double bond",
         ["a carbon-oxygen single bond only", "an ionic lattice", "a benzene ring exclusively"]),
        ("Dehydration of an alcohol with concentrated acid is an example of", "elimination",
         ["addition", "complete combustion", "esterification"]),
        ("PVC plastic recycling challenges include", "difficulty separating additives and contamination",
         ["PVC being an element on the periodic table", "PVC having no carbon atoms", "PVC being fully biodegradable in days"]),
        ("Octane rating of gasoline measures", "resistance to knocking during combustion",
         ["boiling point in Kelvin only", "pH of the fuel", "oxidation number of carbon exclusively"]),
        ("A carboxylic acid can be produced from oxidation of a", "primary alcohol or aldehyde",
         ["saturated alkane with no functional group directly in one step always", "noble gas", "ionic sodium chloride"]),
        ("Isomers of C$_4$H$_{10}$ include butane and", "2-methylpropane",
         ["pentane", "cyclobutane only without branching", "methane"]),
        ("The process of cracking increases the yield of", "smaller, more useful hydrocarbon fractions",
         ["only solid carbon soot", "ionic compounds from crude oil", "water from petroleum"]),
        ("A positive test with aqueous potassium permanganate for an unsaturated compound shows",
         "decolouration of the purple solution",
         ["precipitation of a blue solid always", "no visible change ever", "release of chlorine gas"]),
        ("Polymers in living systems include", "proteins and carbohydrates",
         ["only synthetic polyethylene", "ionic table salt crystals", "noble gases"]),
    ]
    for qt, ans, d1, d2 in [(q, a, d[0], d[1]) for q, a, d in c_more]:
        more.append(mc(qt, ans, [d1, d2, "none of these"], f"{ans} is the best answer.",
                        "Students confuse organic reaction types or nomenclature.",
                        topic=TOPIC_C, outcome_code="C1.3k",
                        skill_tested="Organic chemistry knowledge application",
                        difficulty="Medium", estimated_time_seconds=80))

    # Unit C: molecular mass NR (simple auto-grade)
    for name, carbons, h, mw in [("ethane", 2, 6, 30), ("propane", 3, 8, 44), ("butane", 4, 10, 58),
                                  ("pentane", 5, 12, 72), ("hexane", 6, 14, 86)]:
        more.append(nr(
            f"An alkane {name} has formula C$_{{{carbons}}}$H$_{{{h}}}$. "
            f"What is its approximate molar mass in g/mol? Use C = 12 and H = 1. Record as a whole number.",
            str(mw),
            f"Molar mass = ${carbons} \\times 12 + {h} \\times 1 = {mw}\\ \\text{{g/mol}}$.",
            "Students use wrong atomic masses or count only carbons.",
            topic=TOPIC_C, outcome_code="C1.5k",
            skill_tested=f"Calculating molar mass of {name}",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Unit D: percent ionization NR
    for c0, h_conc, pct in [(0.100, 0.0010, 1), (0.050, 0.00050, 1), (0.200, 0.0020, 1),
                            (0.010, 0.0010, 10), (0.020, 0.0020, 10), (0.0050, 0.00050, 10),
                            (0.100, 0.010, 10), (0.050, 0.0050, 10)]:
        more.append(nr(
            f"A weak acid with initial concentration ${c0}\\ \\text{{mol/L}}$ has "
            f"$[\\text{{H}}_3\\text{{O}}^+] = {h_conc}\\ \\text{{mol/L}}$ at equilibrium. "
            f"What is the percent ionization? Record as a whole number.",
            str(pct),
            f"% ionization = $({h_conc}/{c0}) \\times 100 = {pct}\\%$.",
            "Students confuse [H₃O⁺] with percent directly.",
            topic=TOPIC_D, outcome_code="D2.2k",
            skill_tested="Calculating weak acid percent ionization",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit D: equilibrium MC expansion
    d_more = [
        ("For $\\text{H}_2(g) + \\text{I}_2(g) \\rightleftharpoons 2\\text{HI}(g)$, decreasing volume at constant temperature",
         "does not change Kc but may change equilibrium position",
         ["changes Kc to a larger value always", "stops all molecular motion", "removes all HI instantly"]),
        ("A buffer containing CH$_3$COOH and CH$_3$COO$^-$ resists pH change because added OH$^-$ reacts with",
         "CH$_3$COOH", ["CH$_3$COO$^-$ only without consuming acid", "Na$^+$ spectator ions", "water breaking into H$_2$ and O$_2$"]),
        ("The equivalence point of a weak base–strong acid titration has pH",
         "less than 7", ["equal to 7 always", "greater than 7", "exactly 0"]),
        ("Amphiprotic H$_2$PO$_4^-$ can act as an acid donating H$^+$ to form",
         "HPO$_4^{2-}$", ["PO$_4^{3-}$ in one step always", "H$_3$PO$_4$ by gaining two protons", "P$^{5+}$ ion"]),
        ("Adding solid NaCl to $\\text{Ag}^+(aq) + \\text{Cl}^-(aq) \\rightleftharpoons \\text{AgCl}(s)$ shifts equilibrium",
         "toward AgCl(s) precipitation (more product)", ["toward Ag$^+$ ions only", "without any change because solids do not matter", "only if temperature increases"]),
        ("Kw at 25°C equals $1.0 \\times 10^{-14}$ means in pure water",
         "[H$_3$O$^+$][OH$^-$] = $1.0 \\times 10^{-14}$ mol$^2$/L$^2$",
         ["pH + pOH = 1", "[H$_3$O$^+$] equals 1 mol/L", "water cannot ionize"]),
        ("A large Kc value for a gaseous reaction with equal moles of gas on both sides indicates",
         "products are favoured at equilibrium (extent of reaction)", ["reactants always favoured regardless of Kc", "Kc is unrelated to position", "the reaction is not at equilibrium"]),
        ("Strong acids in the Brønsted-Lowry sense have",
         "very stable conjugate bases (weak bases)", ["very strong conjugate bases", "no conjugate pairs", "conjugate acids that are stronger than HClO$_4$ always"]),
        ("At the half-equivalence point of a weak acid–strong base titration",
         "pH equals pKa of the weak acid", ["pH equals 7 always", "pH equals 14", "[acid] equals zero"]),
        ("Industrial ammonia synthesis shifts equilibrium toward products by using",
         "high pressure and removing NH$_3$ as formed", ["low pressure exclusively", "adding inert gas at constant volume to shift right", "decreasing temperature without limit always"]),
    ]
    for qt, ans, d1, d2 in [(q, a, d[0], d[1]) for q, a, d in d_more]:
        more.append(mc(qt, ans, [d1, d2, "none applies"], f"{ans} is correct.",
                        "Students apply incorrect equilibrium or acid-base rules.",
                        topic=TOPIC_D, outcome_code="D1.3k",
                        skill_tested="Equilibrium and acid-base conceptual analysis",
                        difficulty="Medium", estimated_time_seconds=90))

    # Unit D: 2A ⇌ B style Kc
    for a_conc, b_conc, kc in [(0.40, 0.04, 0.25), (0.60, 0.09, 0.25), (0.80, 0.16, 0.25),
                                (0.20, 0.02, 0.50), (0.50, 0.05, 0.20), (0.30, 0.03, 0.33),
                                (0.70, 0.14, 0.29), (0.10, 0.01, 1.0), (0.90, 0.09, 0.11),
                                (0.35, 0.07, 0.57)]:
        more.append(nr(
            f"For $2\\text{{A}}(g) \\rightleftharpoons \\text{{B}}(g)$, $[\\text{{A}}] = {a_conc}$ and $[\\text{{B}}] = {b_conc}$ at equilibrium. "
            f"Calculate $K_c$ to two decimal places.",
            f"{kc:.2f}",
            f"$K_c = [{b_conc}]/([{a_conc}]^2) = {kc:.2f}$.",
            "Students forget to square [A] in the denominator.",
            topic=TOPIC_D, outcome_code="D2.3k",
            skill_tested="Calculating Kc for 2A ⇌ B equilibrium",
            difficulty="Hard", estimated_time_seconds=130,
        ))

    # Cross-unit STS MC
    sts = [
        (TOPIC_A, "A1.2sts", "Lifecycle analysis of fuels considers extraction, transport, combustion, and emissions together."),
        (TOPIC_B, "B2.3sts", "Hydrogen fuel cells in transportation reduce tailpipe emissions but require energy to produce hydrogen."),
        (TOPIC_C, "C2.3sts", "Plastic recycling reduces landfill waste but may degrade polymer quality in downcycling."),
        (TOPIC_D, "D1.2sts", "Equilibrium concepts explain why sealed carbonated beverages remain fizzy until opened."),
    ]
    for topic, oc, stmt in sts:
        unit_label = {
            TOPIC_A: "Unit A thermochemical",
            TOPIC_B: "Unit B electrochemical",
            TOPIC_C: "Unit C organic",
            TOPIC_D: "Unit D equilibrium and acid-base",
        }[topic]
        more.append(mc(
            f"Which statement best reflects Alberta STS expectations for {unit_label} chemistry?",
            stmt,
            ["Technology develops independently of scientific evidence.", "All reversible reactions reach completion with $K = \\infty$.", "Communication skills are optional in chemistry lab work."],
            f"Outcome {oc}: {stmt}",
            f"Students may treat STS outcome {oc} as separate from {unit_label.lower()} content.",
            topic=topic, outcome_code=oc, skill_tested=f"Integrating STS outcome {oc}",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Final top-up to ~450
    for i, (m, c, dt) in enumerate([(32, 4.19, 12.5), (48, 4.19, 7.0), (72, 4.19, 4.5),
                                      (88, 4.19, 3.8), (52, 4.19, 9.2), (68, 4.19, 5.5)]):
        q_j = round(m * c * dt)
        more.append(nr(
            f"Calculate $Q$ in joules when ${m}\\ \\text{{g}}$ of water ($c = 4.19\\ \\text{{J/(g·°C)}}$) "
            f"changes temperature by ${dt}\\ \\text{{°C}}$. Record as a whole number.",
            str(q_j),
            f"$Q = {m} \\times 4.19 \\times {dt} = {q_j}\\ \\text{{J}}$.",
            "Students omit mass or specific heat from the calculation.",
            topic=TOPIC_A, outcome_code="A1.1k",
            skill_tested="Computing heat transfer in joules",
            difficulty="Easy", estimated_time_seconds=90,
        ))

    extra_mc_topup = [
        (TOPIC_A, "A2.2sts", "Assessing fossil fuel reliance requires weighing economic benefits against environmental and climate risks."),
        (TOPIC_A, "A1.4s", "Communicating calorimetry results requires SI units, significant digits, and clear energy diagrams."),
        (TOPIC_B, "B1.3s", "Interpreting redox titration data includes identifying limitations of endpoint detection versus equivalence."),
        (TOPIC_B, "B2.4s", "Collaborative analysis of electrochemical cell data uses appropriate units for potential and charge."),
        (TOPIC_C, "C1.1sts", "Organic compounds in Alberta petrochemical industries support economy but require environmental stewardship."),
        (TOPIC_C, "C2.4s", "Reporting on organic chemistry societal issues requires citing evidence from multiple sources."),
        (TOPIC_D, "D1.4s", "Group reports on equilibrium systems should include graphs with proper axis labels and units."),
        (TOPIC_D, "D2.4s", "Equilibrium application reports link industrial processes to Alberta chemistry industries."),
        (TOPIC_D, "D2.3s", "Calculating K from experimental data requires consistent concentration units throughout."),
        (TOPIC_B, "B1.4s", "Redox titration communication includes balanced equations and clear concentration units."),
        (TOPIC_A, "A2.4s", "Enthalpy communication uses kJ/mol and correct sign for exothermic/endothermic processes."),
        (TOPIC_C, "C1.4s", "IUPAC naming in lab reports follows Alberta classroom conventions for structural diagrams."),
        (TOPIC_D, "D1.1s", "Planning equilibrium shift experiments requires identifying measurable and controlled variables."),
        (TOPIC_B, "B2.2s", "Constructing electrochemical cells includes labelled diagrams with ion flow direction."),
        (TOPIC_A, "A1.3s", "Analyzing calorimetry data compares experimental $\\Delta H$ to accepted values with percent error."),
    ]
    for topic, oc, stmt in extra_mc_topup:
        more.append(mc(
            f"Which practice aligns with Alberta Chemistry 30 skills outcome {oc} in {topic}?",
            stmt,
            ["Reporting data without units, significant digits, or safety context", "Using non-standard glassware for precision volumetric work", "Describing observations without linking to outcome criteria"],
            f"Outcome {oc} requires: {stmt}",
            f"Students overlook skills outcome {oc} when communicating chemistry results.",
            topic=topic, outcome_code=oc, skill_tested=f"Demonstrating skills outcome {oc}",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    return more


def main():
    pool = []
    pool.extend(unit_a())
    pool.extend(unit_b())
    pool.extend(unit_c())
    pool.extend(unit_d())
    pool.extend(programmatic_supplements())

    pool = deduplicate(pool)
    ordered = [order_item(q) for q in pool]

    # Post-generation QA fixes
    from scripts.chem30_qa_fix import fix_pool
    ordered, _fix_stats = fix_pool(ordered)
    if _fix_stats:
        print("QA fix stats:", _fix_stats)

    errors = []
    for i, q in enumerate(ordered):
        reasons = validate_question(q, i)
        if reasons:
            errors.append((i, "; ".join(reasons), q.get("question_text", "")[:80]))

    if errors:
        print(f"Validation errors: {len(errors)}")
        for i, err, text in errors[:20]:
            print(f"  [{i}] {err} — {text}")
        sys.exit(1)

    mc_pos = assert_mc_position_balanced(ordered, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)

    topics = Counter(q["topic"] for q in ordered)
    types = Counter(q["question_type"] for q in ordered)
    diffs = Counter(q["difficulty"] for q in ordered)
    outcomes = Counter(q["outcome_code"] for q in ordered)

    print(f"Wrote {len(ordered)} questions to {OUTPUT}")
    print(f"Topics: {dict(topics)}")
    print(f"Types: {dict(types)}")
    print(f"Difficulties: {dict(diffs)}")
    print(f"Unique outcomes: {len(outcomes)}")


if __name__ == "__main__":
    main()
