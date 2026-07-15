"""Unit A: Thermochemical Changes — original Chemistry 30 questions."""

from .helpers import mc, nr

TOPIC = "Thermochemical Changes"


def _batch_mc(items):
    return [
        mc(q, a, d, e, m, topic=TOPIC, outcome_code=oc, skill_tested=s,
           difficulty=diff, estimated_time_seconds=t)
        for q, a, d, e, m, oc, s, diff, t in items
    ]


def questions():
    q = []

    q += _batch_mc([
        (
            "The equation $Q = mc\\Delta T$ is used to calculate heat transfer when",
            "temperature change of a substance is measured and specific heat capacity is known",
            ["only chemical bonds are broken without any temperature change", "mass is always measured in moles of gas only", "the reaction must be at equilibrium"],
            "$Q = mc\\Delta T$ relates heat energy to mass, specific heat capacity, and temperature change.",
            "Students confuse $Q$ with enthalpy change $\\Delta H$ from a chemical reaction.",
            "A1.1k", "Recalling Q = mcΔT application", "Easy", 60,
        ),
        (
            "Energy stored in the chemical bonds of fossil fuels ultimately originated from",
            "solar energy captured during photosynthesis in ancient plants",
            ["nuclear fusion in the Earth's core only", "gravitational collapse of the Moon", "static electricity in the atmosphere exclusively"],
            "Hydrocarbons store chemical potential energy from carbon fixed via photosynthesis millions of years ago.",
            "Students think fuel energy is created during combustion rather than released from stored bonds.",
            "A1.2k", "Explaining origin of hydrocarbon bond energy", "Easy", 65,
        ),
        (
            "Molar enthalpy ($\\Delta H$) for a chemical reaction specifically refers to",
            "enthalpy change when one mole of a specified substance is produced or consumed",
            ["total heat absorbed by the calorimeter vessel only", "activation energy required to start any reaction", "the rate at which products form per second"],
            "Molar enthalpy is expressed in kJ/mol and refers to a stoichiometric quantity of one mole.",
            "Students confuse molar enthalpy with total heat $Q$ for an arbitrary mass.",
            "A1.3k", "Defining molar enthalpy", "Easy", 70,
        ),
        (
            "In a thermochemical equation, a positive $\\Delta H$ value indicates the reaction is",
            "endothermic",
            ["exothermic", "at equilibrium with no net energy change", "catalyzed by an enzyme only"],
            "Positive $\\Delta H$ means energy is absorbed from surroundings — endothermic.",
            "Students reverse the sign convention for endothermic vs exothermic.",
            "A1.5k", "Interpreting positive ΔH notation", "Easy", 60,
        ),
        (
            "When liquid water is a product of hydrocarbon combustion in an open campfire, the water exists primarily as",
            "water vapour (g)",
            ["liquid water at 25°C always", "solid ice regardless of temperature", "separate hydrogen and oxygen gases"],
            "Open-system combustion releases enough energy to vaporize water produced.",
            "Students use liquid water for all combustion, ignoring open vs closed system distinction.",
            "A1.9k", "Identifying combustion products in open systems", "Medium", 85,
        ),
        (
            "Photosynthesis is classified as an endothermic process because",
            "energy from sunlight is absorbed to build glucose from CO$_2$ and H$_2$O",
            ["heat is released when glucose is broken down", "no chemical bonds are formed", "it occurs only at temperatures above 500°C"],
            "Photosynthesis stores solar energy in chemical bonds — net energy input from surroundings.",
            "Students confuse photosynthesis (endergonic) with cellular respiration (exothermic).",
            "A1.10k", "Classifying photosynthesis as endothermic", "Easy", 70,
        ),
        (
            "Cellular respiration is best classified as",
            "exothermic",
            ["endothermic", "neither exothermic nor endothermic", "a physical change only"],
            "Respiration releases stored chemical energy as heat — exothermic overall.",
            "Students think all biological processes are endothermic because they need activation energy.",
            "A1.10k", "Classifying cellular respiration energy change", "Easy", 65,
        ),
        (
            "Activation energy ($E_a$) on an enthalpy diagram represents",
            "the energy barrier that must be overcome for reactants to form products",
            ["the total enthalpy of products minus reactants", "heat lost to the calorimeter walls", "the equilibrium constant of the reaction"],
            "Activation energy is the peak above reactant energy on an enthalpy diagram.",
            "Students confuse activation energy with enthalpy change $\\Delta H$.",
            "A2.1k", "Defining activation energy on energy diagrams", "Easy", 70,
        ),
        (
            "During an exothermic reaction, the enthalpy of products is",
            "lower than the enthalpy of reactants",
            ["higher than the enthalpy of reactants", "equal to activation energy", "always zero"],
            "Exothermic reactions release energy, so products sit lower on an enthalpy diagram.",
            "Students think exothermic means products have higher energy.",
            "A2.2k", "Relating product enthalpy to exothermic reactions", "Easy", 65,
        ),
        (
            "A catalyst increases reaction rate by",
            "providing an alternate pathway with lower activation energy",
            ["increasing the enthalpy change of the reaction", "shifting equilibrium toward products always", "consuming one of the reactants permanently"],
            "Catalysts lower $E_a$ without changing $\\Delta H$ or equilibrium position.",
            "Students think catalysts change $\\Delta H$ or favour products at equilibrium.",
            "A2.4k", "Explaining catalyst effect on activation energy", "Medium", 80,
        ),
        (
            "Catalytic converters in automobiles reduce air pollution by",
            "catalyzing conversion of CO and unburned hydrocarbons to CO$_2$ and H$_2$O",
            ["increasing fuel combustion temperature above 2000°C", "removing all nitrogen from exhaust", "converting gasoline directly into electricity"],
            "Catalysts in converters speed up oxidation of pollutants without being consumed.",
            "Students think converters eliminate all emissions or generate electricity.",
            "A2.1sts", "Describing catalytic converter environmental application", "Medium", 85,
        ),
        (
            "A polystyrene coffee-cup calorimeter is often used in school labs because polystyrene",
            "is a good insulator, minimizing heat loss to the surroundings",
            ["reacts with all acids to produce hydrogen gas", "has infinite specific heat capacity", "measures temperature without a thermometer"],
            "Polystyrene's low thermal conductivity reduces heat exchange with environment.",
            "Students think the cup material significantly absorbs most of the reaction heat.",
            "A1.8k", "Explaining polystyrene calorimeter design", "Easy", 75,
        ),
        (
            "When a small mass of solute dissolves in a large volume of solvent, using the solvent mass for $m$ in $Q = mc\\Delta T$ is acceptable because",
            "the solute mass is less than 10% of the solvent mass",
            ["the solute always has zero specific heat capacity", "temperature change depends only on the solute", "the calorimeter must be made of copper"],
            "Alberta POS allows solvent mass when solute is a minor fraction of total solution mass.",
            "Students use solute mass only or confuse when approximation is valid.",
            "A1.8k", "Applying calorimetry mass approximation rules", "Medium", 90,
        ),
        (
            "Hess's law states that the enthalpy change for an overall reaction equals",
            "the sum of enthalpy changes for a series of steps that add to the same net reaction",
            ["the product of all individual rate constants", "the average activation energy of all steps", "zero for any multi-step mechanism"],
            "Hess's law allows calculation of $\\Delta H$ from known step enthalpies.",
            "Students try to multiply rather than add step enthalpies.",
            "A1.7k", "Stating Hess's law principle", "Medium", 80,
        ),
        (
            "Standard molar enthalpy of formation ($\\Delta_f H°$) for an element in its standard state equals",
            "0 kJ/mol",
            ["1 kJ/mol by definition", "the enthalpy of combustion of that element", "always negative for all elements"],
            "By convention, elements in standard states have $\\Delta_f H° = 0$ kJ/mol.",
            "Students assign non-zero formation enthalpies to elements like O$_2$(g).",
            "A1.6k", "Recalling standard formation enthalpy of elements", "Easy", 65,
        ),
        (
            "In a bomb calorimeter experiment, water produced from combustion exists as",
            "liquid water",
            ["water vapour only", "solid ice at 0°C", "hydrogen and oxygen gases"],
            "Closed bomb calorimeter keeps water as liquid; open combustion produces vapour.",
            "Students apply open-system product state to closed calorimeter contexts.",
            "A1.9k", "Distinguishing bomb calorimeter product states", "Medium", 90,
        ),
        (
            "A source of error that would cause a calculated enthalpy change to appear larger (more exothermic) than the true value in a coffee-cup calorimeter is",
            "heat loss to the surroundings not fully accounted for",
            ["using a thermometer with 10% precision", "adding excess catalyst", "using distilled water as solvent"],
            "Unmeasured heat loss makes temperature rise appear smaller, but some errors inflate $\\Delta H$ — using too small a mass in calculations overestimates $\\Delta H$.",
            "Students cannot predict whether an error raises or lowers calculated enthalpy.",
            "A2.3s", "Predicting calorimetry source-of-error effects", "Hard", 120,
        ),
        (
            "The efficiency of a heating device is calculated as",
            "useful energy output divided by total energy input, expressed as a percentage",
            ["activation energy divided by enthalpy change", "mass of fuel divided by volume of oxygen", "temperature change times equilibrium constant"],
            "Efficiency = (useful output / energy input) × 100%.",
            "Students confuse efficiency with enthalpy change or reaction rate.",
            "A2.3s", "Defining thermal energy conversion efficiency", "Medium", 85,
        ),
        (
            "Selecting propane over coal for rural home heating in Alberta may be influenced by",
            "cleaner combustion with fewer particulate emissions and easier transport",
            ["propane having zero carbon atoms in its formula", "coal releasing no CO$_2$ when burned", "propane not requiring any oxygen for combustion"],
            "Propane (C$_3$H$_8$) burns more cleanly and is easier to deliver to remote areas than bulk coal.",
            "Students think propane combustion produces no greenhouse gases.",
            "A1.1sts", "Evaluating fuel selection for rural communities", "Medium", 90,
        ),
        (
            "Unintended consequences of relying solely on fossil fuels include",
            "increased atmospheric CO$_2$ and contribution to climate change",
            ["complete elimination of all energy needs worldwide", "permanent increase in atmospheric oxygen only", "zero impact on local air quality"],
            "Fossil fuel combustion releases CO$_2$ and other pollutants with environmental consequences.",
            "Students list only intended benefits without environmental costs.",
            "A1.2sts", "Identifying unintended fossil fuel consequences", "Easy", 75,
        ),
        (
            "Bond breaking during a chemical reaction is",
            "endothermic (requires energy input)",
            ["exothermic (releases energy)", "always energy-neutral", "impossible in exothermic reactions"],
            "Breaking bonds requires energy; forming bonds releases energy. Net $\\Delta H$ depends on balance.",
            "Students think bond breaking releases energy because overall reaction may be exothermic.",
            "A2.2k", "Explaining energy change during bond breaking", "Medium", 85,
        ),
        (
            "On an enthalpy diagram, the difference in height between reactants and products represents",
            "enthalpy change ($\\Delta H$) of the reaction",
            ["activation energy only", "the equilibrium constant", "the rate of reaction"],
            "Vertical distance between reactant and product levels equals $\\Delta H$.",
            "Students label activation energy (peak to reactants) as $\\Delta H$.",
            "A2.3k", "Interpreting enthalpy diagram ΔH", "Medium", 80,
        ),
        (
            "A reaction coordinate diagram shows reactants higher in energy than products. This indicates",
            "an exothermic reaction with negative $\\Delta H$",
            ["an endothermic reaction with positive $\\Delta H$", "the reaction cannot occur without a catalyst", "equilibrium strongly favours reactants"],
            "Products lower than reactants means energy is released — exothermic, $\\Delta H < 0$.",
            "Students invert the exothermic/endothermic interpretation on diagrams.",
            "A2.3k", "Reading exothermic profile from enthalpy diagram", "Easy", 70,
        ),
        (
            "Ethanol is sometimes blended with gasoline because ethanol",
            "is a renewable oxygenated additive that can reduce certain emissions",
            ["contains no carbon and produces only water when burned", "increases the octane rating by removing all oxygen from exhaust", "eliminates the need for catalytic converters"],
            "Ethanol combustion still produces CO$_2$ but offers renewable sourcing and oxygenation benefits.",
            "Students think ethanol is carbon-neutral in all contexts or produces no CO$_2$.",
            "A1.1sts", "Explaining ethanol fuel blending rationale", "Medium", 85,
        ),
        (
            "WHMIS labelling on chemical containers in a calorimetry experiment helps students",
            "identify hazards and follow safe handling procedures for reactants",
            ["calculate enthalpy change without a thermometer", "eliminate all sources of experimental error", "determine the activation energy from the label alone"],
            "WHMIS provides safety information; it does not replace experimental measurement.",
            "Students confuse safety labelling with thermodynamic data.",
            "A1.1s", "Applying WHMIS safety in calorimetry labs", "Easy", 60,
        ),
    ])

    q += [
        nr(
            "A $25.0\\ \\text{g}$ sample of water in a polystyrene calorimeter absorbs $2090\\ \\text{J}$ of heat. "
            "If the specific heat capacity of water is $4.19\\ \\text{J/(g·°C)}$, what is the temperature change in °C? "
            "Express your answer to one decimal place.",
            "20.0",
            "$\\Delta T = Q/(mc) = 2090/(25.0 \\times 4.19) = 20.0\\ °\\text{C}$.",
            "Students forget to divide by both mass and specific heat capacity.",
            topic=TOPIC, outcome_code="A1.1k",
            skill_tested="Calculating temperature change from Q = mcΔT",
            difficulty="Medium", estimated_time_seconds=120,
        ),
        nr(
            "When $2.00\\ \\text{mol}$ of a fuel is burned, $802\\ \\text{kJ}$ of energy is released. "
            "What is the molar enthalpy of combustion in kJ/mol? Express as a positive integer.",
            "401",
            "Molar enthalpy = $802/2.00 = 401\\ \\text{kJ/mol}$.",
            "Students report total energy (802) instead of per-mole value.",
            topic=TOPIC, outcome_code="A1.5k",
            skill_tested="Calculating molar enthalpy from total energy and moles",
            difficulty="Easy", estimated_time_seconds=75,
        ),
        nr(
            "Given $\\Delta H°_f[\\text{CO}_2(g)] = -393.5\\ \\text{kJ/mol}$ and "
            "$\\Delta H°_f[\\text{H}_2\\text{O}(l)] = -285.8\\ \\text{kJ/mol}$, "
            "calculate $\\Delta H°$ for $\\text{C}(s) + \\text{O}_2(g) \\rightarrow \\text{CO}_2(g) + \\text{H}_2\\text{O}(l)$ "
            "if 1 mol CO$_2$ and 0 mol H$_2$O are formed. Express in kJ to one decimal (magnitude only as positive integer for CO$_2$ formation only).",
            "394",
            "For $\\text{C} + \\text{O}_2 \\rightarrow \\text{CO}_2$: $\\Delta H° = -393.5 \\approx -394\\ \\text{kJ/mol}$.",
            "Students add unrelated formation enthalpies without a balanced target equation.",
            topic=TOPIC, outcome_code="A1.6k",
            skill_tested="Using formation enthalpy for CO₂ combustion",
            difficulty="Medium", estimated_time_seconds=130,
        ),
        nr(
            "A reaction has $\\Delta H_1 = -50\\ \\text{kJ}$ for step 1 and $\\Delta H_2 = +30\\ \\text{kJ}$ for step 2. "
            "What is the net $\\Delta H$ for the overall reaction in kJ? Record as a signed integer.",
            "-20",
            "Hess's law: $\\Delta H_{net} = -50 + 30 = -20\\ \\text{kJ}$.",
            "Students subtract in wrong order or ignore sign of endothermic step.",
            topic=TOPIC, outcome_code="A1.7k",
            skill_tested="Applying Hess's law to sum step enthalpies",
            difficulty="Easy", estimated_time_seconds=80,
        ),
        nr(
            "In a calorimetry trial, $150\\ \\text{g}$ of water increases in temperature by $3.50\\ \\text{°C}$. "
            "Using $c = 4.19\\ \\text{J/(g·°C)}$, calculate heat absorbed $Q$ in kJ to one decimal place.",
            "2.2",
            "$Q = 150 \\times 4.19 \\times 3.50 = 2200\\ \\text{J} = 2.2\\ \\text{kJ}$.",
            "Students report joules without converting to kJ, or omit mass.",
            topic=TOPIC, outcome_code="A1.8k",
            skill_tested="Calculating heat absorbed in calorimetry",
            difficulty="Medium", estimated_time_seconds=120,
        ),
        nr(
            "A heating device delivers $3.40 \\times 10^3\\ \\text{kJ}$ of useful heat from $4.00 \\times 10^3\\ \\text{kJ}$ of fuel energy. "
            "What is the efficiency as a percentage rounded to the nearest whole number?",
            "85",
            "Efficiency = $(3400/4000) \\times 100 = 85\\%$.",
            "Students invert the input/output ratio.",
            topic=TOPIC, outcome_code="A2.3s",
            skill_tested="Calculating thermal device efficiency percentage",
            difficulty="Medium", estimated_time_seconds=90,
        ),
    ]

    return q
