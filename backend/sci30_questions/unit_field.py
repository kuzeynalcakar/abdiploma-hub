"""Field Theory and Electrical Energy — Science 30 original questions."""

from .helpers import mc, nr

TOPIC = "Field Theory and Electrical Energy"


def _base_mc():
    return [
        mc(
            "A gravitational field exists in the region around a mass because",
            "another mass placed in the region experiences a gravitational force",
            ["all objects lose mass permanently in the region", "electric charges cannot exist nearby", "magnetic poles reverse every second automatically"],
            "Fields describe how forces act at a distance on test objects placed in space.",
            "Fields do not eliminate mass or prevent other field types from existing.",
            topic=TOPIC, outcome_code="C1.1k",
            skill_tested="Defining field as property of space around source",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Electric field lines around a positive point charge point",
            "radially outward from the charge",
            ["inward toward the charge", "in closed circles only", "parallel to each other everywhere"],
            "Positive source charges have field lines directed away from the charge.",
            "Inward lines indicate negative source charge convention.",
            topic=TOPIC, outcome_code="C1.3k",
            skill_tested="Interpreting electric field line direction for positive charge",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "If the distance from a point charge doubles, the electric field strength becomes",
            "one quarter of the original value",
            ["one half of the original value", "four times the original value", "unchanged regardless of distance"],
            "E ∝ 1/r², so doubling r gives E_new = E/4.",
            "Students often use inverse proportion (1/r) instead of inverse square.",
            topic=TOPIC, outcome_code="C1.4k",
            skill_tested="Applying inverse-square law to electric field strength",
            difficulty="Hard", estimated_time_seconds=100,
        ),
        mc(
            "Electromagnetic induction occurs when",
            "a conductor moves through a magnetic field or the field through a conductor changes",
            ["a resistor is painted a different colour", "gravity is eliminated in the laboratory", "a capacitor stores static charge without any field change"],
            "Changing magnetic flux through a conductor induces an EMF (Faraday's law).",
            "Induction requires changing flux, not appearance or static conditions.",
            topic=TOPIC, outcome_code="C1.5k",
            skill_tested="Identifying conditions for electromagnetic induction",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "In a series circuit with two identical resistors, the total resistance is",
            "the sum of the individual resistances",
            ["half the value of one resistor", "equal to the product divided by the sum", "always zero regardless of resistors"],
            "Series: R_T = R₁ + R₂ + ...",
            "Reciprocal sum rule applies to parallel circuits, not series.",
            topic=TOPIC, outcome_code="C1.6k",
            skill_tested="Calculating total resistance in series circuit",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "In a parallel circuit, the voltage across each branch is",
            "equal to the source voltage",
            ["split equally by resistance values only", "always zero in every branch", "double the source voltage in each branch"],
            "Parallel branches share the same potential difference across them.",
            "Current splits in parallel; voltage is the same across branches.",
            topic=TOPIC, outcome_code="C1.6k",
            skill_tested="Stating voltage relationship in parallel circuits",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "A device that converts mechanical kinetic energy into electrical energy is a",
            "generator",
            ["DC motor (electrical to mechanical)", "voltage transformer (AC step-up/down)", "circuit fuse (overcurrent protection)"],
            "Generators use electromagnetic induction to produce electrical output from rotation.",
            "Motors convert electrical to mechanical energy (reverse function).",
            topic=TOPIC, outcome_code="C1.11k",
            skill_tested="Identifying generator energy conversion direction",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "A DC motor converts",
            "electrical energy into kinetic energy of rotation",
            ["kinetic energy into electrical energy", "thermal energy into gravitational potential only", "magnetic monopoles into electric monopoles"],
            "Motors use current in a magnetic field to produce torque and rotation.",
            "Generators perform the reverse energy conversion.",
            topic=TOPIC, outcome_code="C1.11k",
            skill_tested="Identifying motor energy conversion direction",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Alternating current (AC) is preferred over direct current (DC) for long-distance transmission because",
            "AC voltages can be stepped up and down efficiently using transformers",
            ["AC eliminates all resistance in wires completely", "DC always travels faster than the speed of light", "AC prevents any power loss in all circumstances"],
            "High-voltage AC transmission reduces current and I²R losses; transformers require changing flux.",
            "Some losses always occur; AC advantage is transformer voltage conversion.",
            topic=TOPIC, outcome_code="C1.10k",
            skill_tested="Explaining AC advantage for electrical transmission",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "A circuit breaker protects electrical equipment by",
            "interrupting current flow when current exceeds a safe threshold",
            ["increasing voltage without limit during a short circuit", "converting AC to DC in all household outlets", "storing excess charge permanently in the ground wire"],
            "Breakers trip (open circuit) on overcurrent to prevent overheating and fire.",
            "Protection means stopping current, not increasing voltage.",
            topic=TOPIC, outcome_code="C1.12k",
            skill_tested="Describing circuit breaker safety function",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "The ground wire in a household circuit provides",
            "a low-resistance path for fault current to reduce shock hazard",
            ["a path to increase resistance during normal operation", "a means to step up voltage to 10 kV in outlets", "insulation between the hot and neutral wires"],
            "Grounding diverts leakage current safely to earth if insulation fails.",
            "Ground wire is a safety path, not for voltage step-up.",
            topic=TOPIC, outcome_code="C1.12k",
            skill_tested="Explaining ground wire safety purpose",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "Power dissipated in a resistor is calculated using",
            "P = I²R or P = VI",
            ["P = I/R only", "P = R/I² only", "P = V/I² only"],
            "Joule heating power: P = VI = I²R = V²/R for resistive loads.",
            "Power formulas use products/ratios of V, I, R correctly.",
            topic=TOPIC, outcome_code="C1.6k",
            skill_tested="Recalling power formulas for resistive circuits",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "Magnetic field lines around a bar magnet emerge from the",
            "north pole and enter the south pole externally",
            ["south pole only on both sides externally", "centre of the magnet with no external field", "equator of Earth exclusively"],
            "External field lines run from north to south outside the magnet.",
            "Field lines form closed loops through the magnet interior.",
            topic=TOPIC, outcome_code="C1.3k",
            skill_tested="Describing external magnetic field line direction",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Kilowatt-hours (kWh) measure",
            "electrical energy consumed over time",
            ["instantaneous current only", "magnetic field strength in teslas", "gravitational acceleration on Mars"],
            "Energy E = Pt; kWh = power (kW) × time (hours).",
            "Current is amperes; field strength is tesla; kWh is energy.",
            topic=TOPIC, outcome_code="C1.7k",
            skill_tested="Defining kilowatt-hour as energy unit",
            difficulty="Easy", estimated_time_seconds=55,
        ),
    ]


def _parameterized():
    items = []
    for v, r in [(12, 4), (24, 6), (120, 40)]:
        i = v / r
        items.append(nr(
            f"A resistor with resistance {r} Ω is connected to a {v} V source. "
            f"What is the current in amperes? Express as a decimal.",
            f"{i:.1f}" if i == int(i) else f"{i:.2f}",
            f"I = V/R = {v}/{r} = {i} A.",
            "Students multiply V×R instead of dividing.",
            topic=TOPIC, outcome_code="C1.3s",
            skill_tested="Calculating current using Ohm's law",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for i_val, r in [(2, 5), (4, 8), (1.5, 6)]:
        p = i_val * i_val * r
        items.append(nr(
            f"A circuit carries {i_val} A through a {r} Ω resistor. What is the power dissipated in watts? "
            f"Express as a decimal.",
            f"{p:.1f}" if p == int(p) else f"{p:.2f}",
            f"P = I²R = ({i_val})² × {r} = {p} W.",
            "Students use P = V/I or P = IR instead of P = I²R for power in a resistor.",
            topic=TOPIC, outcome_code="C1.3s",
            skill_tested="Calculating power dissipation in a resistor",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for r1, r2 in [(4, 6), (10, 5), (8, 2)]:
        rt = r1 + r2
        items.append(nr(
            f"Two resistors ({r1} Ω and {r2} Ω) are connected in series. What is the total resistance in ohms?",
            str(rt),
            f"Series: R_T = {r1} + {r2} = {rt} Ω.",
            "Students use parallel formula 1/R = 1/R₁ + 1/R₂ for series circuit.",
            topic=TOPIC, outcome_code="C1.6k",
            skill_tested="Calculating total series resistance",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for r1, r2 in [(6, 3), (12, 4), (10, 5)]:
        rt = round(r1 * r2 / (r1 + r2), 1)
        items.append(nr(
            f"Two resistors ({r1} Ω and {r2} Ω) are connected in parallel. "
            f"What is the total resistance in ohms? Express as a decimal to one decimal place.",
            f"{rt:.1f}",
            f"Parallel: 1/R_T = 1/{r1} + 1/{r2}, so R_T = {rt} Ω.",
            "Students add resistances directly as in series.",
            topic=TOPIC, outcome_code="C1.6k",
            skill_tested="Calculating total parallel resistance",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for vp, vs, np_val in [(120, 12, 100), (240, 24, 50), (600, 120, 200), (110, 11, 100)]:
        ns = round(np_val * vs / vp)
        items.append(nr(
            f"A transformer has {np_val} turns on the primary coil at {vp} V. "
            f"The secondary voltage is {vs} V. How many turns are on the secondary coil? "
            f"Record the answer as an integer.",
            str(ns),
            f"N_s/N_p = V_s/V_p, so N_s = {np_val} × {vs}/{vp} = {ns}.",
            "Students invert the voltage ratio or multiply by V_p/V_s incorrectly.",
            topic=TOPIC, outcome_code="C1.9k",
            skill_tested="Calculating transformer secondary turns from voltage ratio",
            difficulty="Hard", estimated_time_seconds=110,
        ))

    for e1, r1, r2 in [(100, 1, 2), (400, 2, 4), (900, 3, 6)]:
        e2 = round(e1 * (r1 / r2) ** 2)
        items.append(nr(
            f"Electric field strength is {e1} N/C at distance {r1} m from a point charge. "
            f"Assuming inverse-square dependence, what is the field strength in N/C at {r2} m? "
            f"Record as an integer.",
            str(int(e2)),
            f"E₂ = E₁ × (r₁/r₂)² = {e1} × ({r1}/{r2})² = {int(e2)} N/C.",
            "Students use inverse (not inverse-square) relationship, e.g. halving distance but only doubling field.",
            topic=TOPIC, outcome_code="C1.4k",
            skill_tested="Calculating electric field strength at new distance",
            difficulty="Hard", estimated_time_seconds=115,
        ))

    extra_mc = [
        ("In a step-down transformer, the secondary coil has", "fewer turns than the primary coil", ["more turns than the primary always", "exactly zero turns", "the same voltage as the primary without any turns ratio"], "Step-down reduces voltage: N_s < N_p when V_s < V_p.", "Step-down means lower secondary voltage, fewer turns.", "C1.9k", "Identifying step-down transformer turn relationship", "Medium", 80),
        ("Direct current (DC) in a circuit is characterized by", "charge flowing in one consistent direction", ["charge oscillating direction 60 times per second always", "no movement of any charge carriers", "voltage that is always zero"], "DC has unidirectional electron flow (conventional current defined accordingly).", "Oscillating flow describes AC, not DC.", "C1.8k", "Defining direct current electron flow pattern", "Easy", 60),
        ("A fuse differs from a circuit breaker in that a fuse", "must be replaced after it melts from overcurrent", ["can be reset electronically without replacement always", "increases current capacity during a short circuit", "converts electrical energy to nuclear energy"], "Fuses are one-time sacrificial overcurrent protectors.", "Breakers are resettable; fuses melt and must be replaced.", "C1.12k", "Comparing fuse and circuit breaker operation", "Medium", 75),
        ("Lenz's law is consistent with conservation of energy because induced current creates a field that", "opposes the change causing the induction", ["doubles the change causing the induction", "eliminates all magnetic fields permanently", "converts all mass to energy instantly"], "Opposing induced effects require work against the induced field, conserving energy.", "Induced effects oppose change, not amplify it.", "C1.5k", "Applying Lenz's law energy conservation principle", "Hard", 105),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in extra_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
