"""Energy and the Environment — Science 30 original questions."""

from .helpers import mc, nr

TOPIC = "Energy and the Environment"


def _base_mc():
    return [
        mc(
            "Sustainable development aims to meet current energy needs while",
            "preserving environmental quality for future generations",
            ["maximizing fossil fuel use without any limits", "eliminating all technology from society", "ignoring economic and social factors entirely"],
            "Sustainability balances environmental, economic, and social considerations over time.",
            "Sustainability does not mean halting all development or ignoring society.",
            topic=TOPIC, outcome_code="D1.3k",
            skill_tested="Defining sustainable development in energy context",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Canada's per-capita energy consumption is generally higher than many developing nations primarily because of",
            "climate, industrial activity, and lifestyle factors",
            ["complete absence of any natural resources in Canada", "lower technology use in Canadian households", "lack of any heating requirements in winter"],
            "Cold climate, large geography, and industrial economy increase per-capita energy demand.",
            "Canada has abundant resources and significant winter heating needs.",
            topic=TOPIC, outcome_code="D1.2k",
            skill_tested="Explaining factors affecting per-capita energy consumption",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Coal-fired power generation contributes to environmental concerns including",
            "CO₂ emissions and potential acid deposition precursors",
            ["complete elimination of all atmospheric gases", "production of pure oxygen as the only exhaust", "permanent cooling of the entire biosphere"],
            "Coal combustion releases CO₂, SOₓ, NOₓ, and particulates affecting air and climate.",
            "Coal plants emit multiple pollutants, not only oxygen.",
            topic=TOPIC, outcome_code="D1.5k",
            skill_tested="Identifying environmental impacts of coal power",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Solar photovoltaic cells convert sunlight directly into",
            "electrical energy through semiconductor materials",
            ["gravitational potential energy in water towers only", "nuclear fusion in the cell material", "permanent magnetic monopoles"],
            "Photovoltaic effect generates electron flow when photons excite electrons in semiconductors.",
            "PV cells produce electricity, not gravitational PE or fusion.",
            topic=TOPIC, outcome_code="D2.4k",
            skill_tested="Describing photovoltaic energy conversion",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "Wind turbines generate electricity by",
            "converting kinetic energy of moving air to rotational mechanical energy then electrical energy",
            ["absorbing all carbon dioxide from the atmosphere directly", "using nuclear fission in the turbine blades", "converting tidal gravitational forces in the tower base"],
            "Wind turns blades connected to generators producing electrical output.",
            "Wind turbines harness air kinetic energy, not nuclear or tidal directly.",
            topic=TOPIC, outcome_code="D2.4k",
            skill_tested="Tracing wind turbine energy conversion chain",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Geothermal energy ultimately derives from",
            "heat within Earth's interior from radioactive decay and residual formation heat",
            ["direct absorption of visible sunlight at the surface only", "gravitational collapse of the Moon exclusively", "chemical energy stored in atmospheric nitrogen only"],
            "Earth's internal heat drives geothermal; it is not primarily solar surface heating.",
            "Students often confuse geothermal with direct solar radiation.",
            topic=TOPIC, outcome_code="D2.4k",
            skill_tested="Identifying source of geothermal energy",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Nuclear fission in a CANDU reactor releases energy when",
            "heavy uranium nuclei split into smaller nuclei with mass defect converted to energy",
            ["hydrogen nuclei fuse into helium at room temperature", "electrons are permanently removed from all atoms", "coal is burned inside the reactor core directly"],
            "Fission splits U-235 (or similar) nuclei; mass difference becomes energy (E = mc²).",
            "Fusion is different process; CANDU uses fission of heavy nuclei.",
            topic=TOPIC, outcome_code="D2.5k",
            skill_tested="Describing nuclear fission energy release mechanism",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Nuclear fusion as an energy source requires",
            "extremely high temperature and pressure to overcome electrostatic repulsion",
            ["only room temperature and standard atmospheric pressure", "complete absence of any hydrogen isotopes", "direct combustion of uranium metal in air"],
            "Fusion needs extreme conditions so nuclei can overcome Coulomb barrier.",
            "Fusion is not achievable at everyday conditions commercially yet.",
            topic=TOPIC, outcome_code="D2.5k",
            skill_tested="Identifying conditions required for nuclear fusion",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "A hydroelectric dam converts energy through the chain",
            "gravitational PE of stored water → kinetic energy → electrical energy via turbine/generator",
            ["chemical energy of coal → light → sound only", "nuclear fusion in reservoir water → microwaves", "static friction in concrete → permanent magnetism only"],
            "Water falling (or flowing) through turbines spins generators producing electricity.",
            "Hydro uses water PE/KE, not coal chemistry or fusion.",
            topic=TOPIC, outcome_code="D2.10k",
            skill_tested="Tracing hydroelectric energy conversion sequence",
            difficulty="Easy", estimated_time_seconds=70,
        ),
        mc(
            "Tidal power stations such as La Rance, France harness energy from",
            "the gravitational interaction of the Moon and Earth on ocean water",
            ["solar wind particles ionizing the atmosphere only", "radioactive decay in turbine lubricant exclusively", "combustion of methane in underwater burners"],
            "Tidal differences from lunar/solar gravity drive water through turbines.",
            "Tides are gravitational, not primarily solar wind or combustion.",
            topic=TOPIC, outcome_code="D2.12k",
            skill_tested="Explaining tidal energy gravitational source",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Biomass energy from wood combustion is considered renewable when",
            "harvesting rates allow regrowth to replace consumed material over reasonable time",
            ["all forests are cleared permanently without replanting", "wood is converted to uranium in the burner", "combustion produces no carbon dioxide at all"],
            "Renewability depends on replenishment; sustainable forestry enables biomass renewal.",
            "Biomass still releases CO₂; renewability depends on regrowth rate.",
            topic=TOPIC, outcome_code="D2.4k",
            skill_tested="Evaluating biomass renewability conditions",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Hydrogen fuel cells produce electricity by",
            "combining hydrogen and oxygen to form water, releasing energy as electricity",
            ["splitting water without any chemical reaction", "fusing hydrogen into iron at room temperature", "burning coal inside the fuel cell membrane"],
            "Electrochemical reaction in fuel cell: 2H₂ + O₂ → 2H₂O + electrical energy.",
            "Fuel cells use H₂/O₂ reaction, not coal or fusion.",
            topic=TOPIC, outcome_code="D2.4k",
            skill_tested="Describing hydrogen fuel cell electrochemical reaction",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Cogeneration improves energy efficiency by",
            "capturing waste heat from electricity generation for heating or industrial use",
            ["releasing all waste heat to the atmosphere deliberately", "reducing output voltage to zero during peak demand", "eliminating the need for any fuel source"],
            "CHP (combined heat and power) uses thermal energy that would otherwise be wasted.",
            "Cogeneration uses waste heat productively, not discards it.",
            topic=TOPIC, outcome_code="D1.3k",
            skill_tested="Explaining cogeneration efficiency improvement",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "From an environmental perspective, political considerations in energy policy include",
            "regulations, subsidies, and international agreements on emissions",
            ["only the colour of solar panels on rooftops", "the speed of light in fibre optic cables", "the genetic code for hemoglobin synthesis"],
            "Political perspective covers laws, treaties, and government incentives for energy choices.",
            "Political STS is policy-based, not physical appearance or genetics.",
            topic=TOPIC, outcome_code="D2.1sts",
            skill_tested="Identifying political perspective in energy STS analysis",
            difficulty="Easy", estimated_time_seconds=65,
        ),
    ]


def _parameterized():
    items = []
    for ein, eout in [(1000, 350), (500, 200), (800, 400), (2000, 700), (1200, 480), (600, 240)]:
        eff = round(100 * eout / ein, 1)
        items.append(nr(
            f"An energy device receives {ein} J of energy input and delivers {eout} J of useful output. "
            f"What is the efficiency as a percentage? Express as a decimal to one decimal place.",
            f"{eff:.1f}",
            f"Efficiency = (useful output/input) × 100% = ({eout}/{ein}) × 100% = {eff}%.",
            "Students divide input by output instead of output by input.",
            topic=TOPIC, outcome_code="D2.3s",
            skill_tested="Calculating device energy efficiency percentage",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for mass_kg, c in [(0.001, 3e8), (0.002, 3e8), (0.0005, 3e8)]:
        e = mass_kg * c * c
        items.append(nr(
            f"A nuclear reaction converts {mass_kg} kg of mass entirely to energy. "
            f"Using c = 3.0e8 m/s, what is the energy released in joules? "
            f"Express in scientific notation with one digit before the decimal.",
            f"{e:.1e}",
            f"E = mc² = {mass_kg} × (3.0×10⁸)² = {e:.1e} J.",
            "Students forget to square c or use wrong mass units.",
            topic=TOPIC, outcome_code="D2.7k",
            skill_tested="Calculating energy from mass defect using E=mc²",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    for hf_products, hf_reactants, result in [
        ((-394, -286), (-75,), -605),
        ((-393, -286), (-74,), -605),
        ((-890, 0), (-218,), -672),
    ]:
        items.append(nr(
            f"In a Hess's law calculation, ΣΔH°f(products) = {hf_products[0]} + ({hf_products[1]}) kJ/mol "
            f"and ΣΔH°f(reactants) = {hf_reactants[0]} kJ/mol for a combustion reaction. "
            f"Using ΔH° = ΣΔH°f(products) − ΣΔH°f(reactants), what is ΔH° in kJ/mol? Record as an integer.",
            str(result),
            f"ΔH° = ({hf_products[0]} + {hf_products[1]}) − ({hf_reactants[0]}) = {result} kJ/mol.",
            "Students add reactants and products instead of subtracting reactants from products.",
            topic=TOPIC, outcome_code="D2.1k",
            skill_tested="Calculating enthalpy change using Hess's law",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    for pct_renewable in [25, 40, 60, 75, 35, 50]:
        non = 100 - pct_renewable
        items.append(nr(
            f"An energy portfolio report states {pct_renewable}% of electricity comes from renewable sources. "
            f"What percentage comes from non-renewable sources?",
            str(non),
            f"Non-renewable = 100% − {pct_renewable}% = {non}%.",
            "Students report the renewable percentage instead of the complement.",
            topic=TOPIC, outcome_code="D1.4k",
            skill_tested="Calculating non-renewable energy portfolio percentage",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    energy_mc = [
        ("Oil sands extraction raises environmental concerns primarily due to", "high water use, habitat disruption, and greenhouse gas emissions", ["complete elimination of all carbon in the ore", "production of pure oxygen as the only byproduct", "permanent increase in stratospheric ozone globally"], "Oil sands processing is energy- and water-intensive with significant land and emissions impacts.", "Oil sands still involve carbon and multiple environmental impacts.", "D1.5k", "Evaluating oil sands environmental impacts", "Medium", 85),
        ("Passive solar home design reduces heating costs by", "maximizing winter solar gain through window placement and thermal mass", ["eliminating all windows to block sunlight year-round", "using only nuclear fuel rods in the foundation", "converting all walls to copper electrical conductors"], "Strategic orientation and materials store solar heat passively.", "Passive solar uses sunlight; it does not eliminate windows.", "D2.4k", "Describing passive solar heating design principle", "Medium", 75),
        ("The energy return on investment (EROI) for an energy source compares", "energy output to energy invested in extraction and processing", ["only the monetary cost of the fuel to consumers", "the speed of electromagnetic radiation in vacuum", "the number of chromosomes in a diploid cell"], "EROI is an energy-out vs energy-in ratio for assessing net energy gain.", "EROI is energy-based, not purely financial or biological.", "D1.1sts", "Defining energy return on investment concept", "Medium", 80),
        ("Nuclear waste from fission reactors requires long-term management because", "some isotopes remain radioactive for thousands of years", ["all waste becomes harmless within one hour", "waste converts to renewable biomass immediately", "waste increases atmospheric oxygen concentration"], "Long half-life isotopes need secure geological or engineered storage.", "Nuclear waste persists; it does not rapidly become harmless.", "D2.8k", "Explaining long-term nuclear waste storage need", "Medium", 80),
        ("Active solar heating systems differ from passive designs because they", "use pumps or fans to circulate heated fluid or air", ["require no energy input for circulation ever", "use only nuclear fusion in rooftop panels", "block all sunlight from entering the building"], "Active systems consume energy to move heat-transfer medium.", "Active systems use mechanical circulation.", "D2.4k", "Distinguishing active from passive solar heating", "Easy", 65),
        ("Energy load scheduling shifts electricity use to off-peak hours in order to", "reduce strain on the grid and potentially lower costs", ["increase peak demand deliberately for all consumers", "eliminate all renewable energy from the grid", "prevent all transformers from operating"], "Load shifting balances demand, improving efficiency and reducing peak plant needs.", "Scheduling manages demand; it does not eliminate renewables.", "D1.3k", "Explaining purpose of electrical load scheduling", "Medium", 75),
        (
            "Alpha decay of a nucleus results in",
            "emission of a helium-4 nucleus (2 protons, 2 neutrons)",
            ["emission of a high-speed electron from the nucleus", "emission of only visible light with no particles", "complete fusion of the nucleus with hydrogen in air"],
            "Alpha particles are He-4 nuclei ejected from unstable heavy nuclei.",
            "Beta decay emits electrons; alpha emits He-4 nuclei.",
            "D2.6k", "Identifying alpha decay particle product", "Medium", 80,
        ),
    ]

    for qt, ans, dist, expl, mis, oc, skill, diff, time in energy_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
