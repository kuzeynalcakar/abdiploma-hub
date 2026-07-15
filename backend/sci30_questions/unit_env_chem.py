"""Environmental Chemistry — Science 30 original questions."""

import math
from .helpers import mc, nr

TOPIC = "Environmental Chemistry"


def _base_mc():
    return [
        mc(
            "According to the proton donor-acceptor model, an acid is a substance that",
            "donates a proton (H⁺) to another species",
            ["accepts electrons to form a negative ion only", "always has a pH above 7", "cannot react with any metal"],
            "Acids donate protons; bases accept protons in Brønsted-style definitions used in Science 30.",
            "Bases accept protons; acids have pH below 7 in aqueous solution.",
            topic=TOPIC, outcome_code="B1.1k",
            skill_tested="Defining acid as proton donor",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "A solution with pH 3 is",
            "more acidic than a solution with pH 6",
            ["more basic than a solution with pH 6", "neutral compared to pH 6", "exactly 3 times less concentrated in all ions"],
            "Lower pH means higher [H₃O⁺]; pH 3 has 1000× more hydronium than pH 6.",
            "Students may think higher pH number means more acidic.",
            topic=TOPIC, outcome_code="B1.3k",
            skill_tested="Comparing acidity using pH scale",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "A buffer solution resists pH change when",
            "small amounts of acid or base are added",
            ["large volumes of pure water remove all ions", "the solution is heated above 500°C", "all dissolved gases are removed instantly"],
            "Buffers contain weak acid/base conjugate pairs that neutralize added H⁺ or OH⁻.",
            "Buffers work through chemical equilibrium, not temperature or degassing alone.",
            topic=TOPIC, outcome_code="B1.4k",
            skill_tested="Explaining buffer action against pH change",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "The hydrogen carbonate ion (HCO₃⁻) in blood helps maintain pH by",
            "acting as part of a buffer system that absorbs excess H⁺ or OH⁻",
            ["binding oxygen to hemoglobin directly", "producing sulfur dioxide in the lungs", "eliminating all carbon dioxide from the body"],
            "HCO₃⁻/H₂CO₃ buffer regulates blood pH alongside respiratory CO₂ control.",
            "Oxygen binding is hemoglobin's role; HCO₃⁻ buffers pH.",
            topic=TOPIC, outcome_code="B1.5k",
            skill_tested="Relating bicarbonate buffer to blood pH regulation",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Sulfur dioxide and nitrogen oxides released into the atmosphere can lead to",
            "acid deposition when they react with water in the air",
            ["increased stratospheric ozone concentration globally", "complete neutralization of all ocean water", "formation of pure oxygen gas only"],
            "SO₂ and NOₓ form acids (H₂SO₄, HNO₃) in atmospheric moisture, lowering rain pH.",
            "These pollutants cause acid rain, not ozone increase or ocean neutralization.",
            topic=TOPIC, outcome_code="B1.8k",
            skill_tested="Connecting combustion pollutants to acid deposition",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Acid deposition can leach aluminum ions from soil, which may harm aquatic ecosystems by",
            "damaging gill function in fish and disrupting food webs",
            ["increasing dissolved oxygen to toxic levels for all life", "preventing all nitrogen fixation in the atmosphere", "converting all water to pure H₂ gas"],
            "Mobilized Al³⁺ is toxic to fish; lowered pH also affects aquatic organisms directly.",
            "Acid deposition harms ecosystems; it does not increase O₂ to toxic levels.",
            topic=TOPIC, outcome_code="B1.9k",
            skill_tested="Analyzing acid deposition impact on aquatic life",
            difficulty="Medium", estimated_time_seconds=90,
        ),
        mc(
            "Chlorofluorocarbons (CFCs) are environmental concerns because they",
            "release chlorine radicals that catalyze ozone destruction in the stratosphere",
            ["directly cause acid rain by lowering rain pH below 2 always", "are essential nutrients for all aquatic plants", "increase blood pH through buffer action"],
            "CFCs persist and break down to release Cl atoms that destroy O₃ in the ozone layer.",
            "Acid rain involves SOₓ/NOₓ; CFCs primarily affect stratospheric ozone.",
            topic=TOPIC, outcome_code="B2.4k",
            skill_tested="Explaining CFC role in ozone depletion",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Biomagnification of DDT in a food chain means",
            "DDT concentration increases at higher trophic levels",
            ["DDT is diluted at each trophic level", "DDT converts to oxygen at the top predator", "DDT only affects producers at the bottom"],
            "Persistent lipophilic toxins accumulate in fatty tissue and concentrate up the chain.",
            "Biomagnification increases concentration upward, not dilution.",
            topic=TOPIC, outcome_code="B2.6k",
            skill_tested="Defining biomagnification in food chains",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Methane (CH₄) is considered a greenhouse gas because it",
            "absorbs infrared radiation emitted from Earth's surface",
            ["reflects all ultraviolet radiation before reaching Earth", "increases stratospheric ozone concentration directly", "neutralizes acid deposition in the atmosphere"],
            "Greenhouse gases trap outgoing IR radiation, warming the lower atmosphere.",
            "Methane does not reflect UV or neutralize acid rain.",
            topic=TOPIC, outcome_code="B2.3k",
            skill_tested="Explaining methane greenhouse effect mechanism",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "IUPAC name for CH₃CH₂CH₃ is",
            "propane",
            ["propene (alkene with double bond)", "propyne (alkyne with triple bond)", "propanol (alcohol functional group)"],
            "Three-carbon alkane with single bonds: propane.",
            "Propene has a double bond; propyne has a triple bond.",
            topic=TOPIC, outcome_code="B2.1k",
            skill_tested="Naming three-carbon alkane using IUPAC",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Catalytic converters in vehicles reduce harmful emissions by",
            "converting some exhaust gases to less harmful products before release",
            ["increasing sulfur dioxide output deliberately", "removing all nitrogen from the atmosphere", "producing concentrated hydrochloric acid exhaust"],
            "Catalysts convert CO and unburned hydrocarbons to CO₂ and H₂O, and reduce NOₓ.",
            "Converters reduce pollutants; they do not increase SO₂ or produce HCl exhaust.",
            topic=TOPIC, outcome_code="B3.2k",
            skill_tested="Describing catalytic converter pollution reduction",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Bioremediation as an alternative to some chemical technologies uses",
            "microorganisms to break down or absorb environmental contaminants",
            ["permanent storage of all waste in the stratosphere", "increasing CFC production for cooling", "eliminating all buffers from soil"],
            "Certain bacteria and fungi metabolize pollutants into less harmful substances.",
            "Bioremediation uses biological agents, not atmospheric storage or CFCs.",
            topic=TOPIC, outcome_code="B3.3k",
            skill_tested="Defining bioremediation approach to pollution",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "A strong acid such as HCl(aq) in dilute solution",
            "ionizes completely to produce H₃O⁺ and Cl⁻ ions",
            ["ionizes only partially like acetic acid", "does not produce any ions in water", "always has pH exactly 14"],
            "Strong acids fully dissociate in aqueous solution.",
            "Weak acids partially ionize; strong acids ionize completely.",
            topic=TOPIC, outcome_code="B1.2k",
            skill_tested="Distinguishing strong acid complete ionization",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "PCBs (polychlorinated biphenyls) persist in the environment because they",
            "are chemically stable and lipophilic, resisting breakdown",
            ["rapidly dissolve in water and disappear within hours", "convert immediately to harmless nitrogen gas", "are required nutrients for all fish species"],
            "PCBs resist metabolic and environmental degradation and accumulate in organisms.",
            "Persistence means slow breakdown, not rapid disappearance.",
            topic=TOPIC, outcome_code="B2.3k",
            skill_tested="Explaining environmental persistence of PCBs",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Scrubbers in industrial smokestacks reduce air pollution by",
            "neutralizing acidic gases before they exit the stack",
            ["increasing particulate emissions deliberately", "converting all CO₂ to ozone in the troposphere", "removing all oxygen from exhaust gas"],
            "Scrubbers spray alkaline solutions to remove SO₂ and other acidic pollutants.",
            "Scrubbers reduce emissions; they do not increase pollution.",
            topic=TOPIC, outcome_code="B3.2k",
            skill_tested="Describing scrubber technology for emission control",
            difficulty="Medium", estimated_time_seconds=75,
        ),
    ]


def _parameterized():
    items = []
    for h_conc in [1e-3, 1e-4, 1e-2]:
        ph = -math.log10(h_conc)
        items.append(nr(
            f"The hydronium ion concentration of a solution is {h_conc:.0e} mol/L. "
            f"What is the pH? Express as a number rounded to one decimal place.",
            f"{ph:.1f}",
            f"pH = −log[H₃O⁺] = −log({h_conc:.0e}) = {ph:.1f}.",
            "Students use log base without negation or confuse pH with [H₃O⁺] directly.",
            topic=TOPIC, outcome_code="B1.3k",
            skill_tested="Calculating pH from hydronium ion concentration",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for ph in [2, 4, 6]:
        h = 10 ** (-ph)
        items.append(nr(
            f"A laboratory solution has pH {ph}. What is the hydronium ion concentration in mol/L? "
            f"Express in scientific notation with one digit before the decimal (e.g., 1.0e-3).",
            f"{h:.1e}",
            f"[H₃O⁺] = 10^(−{ph}) = {h:.1e} mol/L.",
            "Students report the pH value instead of calculating concentration.",
            topic=TOPIC, outcome_code="B1.3s",
            skill_tested="Calculating hydronium concentration from pH",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for ma, mb, va in [(0.10, 0.10, 25.0), (0.20, 0.10, 20.0), (0.15, 0.05, 30.0)]:
        moles_acid = ma * va / 1000
        vb = moles_acid / mb * 1000
        items.append(nr(
            f"A {va:.0f} mL sample of {ma:.2f} mol/L monoprotic acid is titrated with "
            f"{mb:.2f} mol/L monoprotic base. What volume of base in mL is required to reach equivalence? "
            f"Express as a decimal to one decimal place.",
            f"{vb:.1f}",
            f"n_acid = M_a × V_a = {ma:.2f} × {va/1000:.3f} = {moles_acid:.4f} mol. "
            f"V_b = n/M_b = {moles_acid:.4f}/{mb:.2f} = {vb/1000:.4f} L = {vb:.1f} mL.",
            "Students multiply acid and base molarities without using mole equality at equivalence.",
            topic=TOPIC, outcome_code="B1.3s",
            skill_tested="Calculating base volume required for acid-base titration equivalence",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    alkane_distractors = {
        1: ["ethane (two-carbon alkane)", "propane (three-carbon alkane)", "butane (four-carbon alkane)"],
        2: ["methane (one-carbon alkane)", "propane (three-carbon alkane)", "butane (four-carbon alkane)"],
        3: ["methane (one-carbon alkane)", "ethane (two-carbon alkane)", "butane (four-carbon alkane)"],
    }
    for carbons in [1, 2, 3]:
        names = {1: "methane", 2: "ethane", 3: "propane"}
        formulas = {1: "CH₄", 2: "CH₃CH₃", 3: "CH₃CH₂CH₃"}
        items.append(mc(
            f"The IUPAC name for the saturated hydrocarbon {formulas[carbons]} is",
            names[carbons],
            alkane_distractors[carbons],
            f"{formulas[carbons]} is a {carbons}-carbon alkane named {names[carbons]}.",
            "Students confuse alkane, alkene, and alkyne suffixes.",
            topic=TOPIC, outcome_code="B2.1k",
            skill_tested=f"Naming {carbons}-carbon saturated hydrocarbon",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    extra_mc = [
        ("Weak acids such as acetic acid in solution", "ionize only partially, establishing an equilibrium", ["ionize 100% like hydrochloric acid", "do not produce any hydronium ions", "always have pH of exactly 0"], "Weak acids partially dissociate; equilibrium lies left of full ionization.", "Complete ionization defines strong acids, not weak acids.", "B1.2k", "Distinguishing weak acid partial ionization", "Medium", 75),
        ("Photochemical smog formation is promoted by", "sunlight acting on pollutants such as NOₓ and volatile organics", ["complete absence of all solar radiation", "only sulfur dioxide with no other gases", "buffers in automotive exhaust systems"], "UV-driven reactions produce oxidants like ozone and PAN in smog.", "Smog requires sunlight and multiple pollutants.", "B1.8k", "Explaining photochemical smog formation conditions", "Medium", 80),
        ("Dissolved oxygen levels in a lake decrease most directly when", "organic pollution increases biological oxygen demand", ["pH becomes slightly alkaline from natural buffers", "the lake freezes in winter temporarily", "visible light reflects off the water surface"], "Decomposers consume O₂ breaking down organic waste, lowering dissolved oxygen.", "Freezing and light reflection do not directly deplete dissolved O₂ like BOD.", "B3.3s", "Relating organic pollution to dissolved oxygen decline", "Medium", 85),
        ("Risk-benefit analysis of pesticide use considers", "crop yield benefits against environmental and health risks", ["only the colour of the pesticide liquid", "the speed of light in a vacuum exclusively", "motor versus generator design in power plants"], "STS analysis weighs economic/agricultural gains vs ecological and human health costs.", "Risk-benefit is broader than physical appearance or physics topics.", "B3.1sts", "Applying risk-benefit framework to pesticide use", "Medium", 90),
        ("Ethanol (CH₃CH₂OH) as a fuel additive is related to environmental chemistry because it", "can reduce some fossil fuel dependence but still produces CO₂ when combusted", ["eliminates all greenhouse gas emissions when burned", "is identical to stratospheric ozone", "prevents all acid deposition globally"], "Ethanol combustion still releases CO₂ but may reduce net fossil carbon use.", "Ethanol is not emission-free and is not ozone.", "B2.2k", "Evaluating ethanol fuel environmental trade-offs", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in extra_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
