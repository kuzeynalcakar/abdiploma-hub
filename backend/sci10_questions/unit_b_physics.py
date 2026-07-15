"""Unit B: Energy Flow in Technological Systems — Science 10 original questions."""

from .helpers import mc, nr

TOPIC = "Energy Flow in Technological Systems"


def _batch_mc(items):
    return [
        mc(q, a, d, e, m, topic=TOPIC, outcome_code=oc, skill_tested=s,
           difficulty=diff, estimated_time_seconds=t)
        for q, a, d, e, m, oc, s, diff, t in items
    ]


def questions():
    q = []

    # --- Energy forms and evidence (B2.1k–B2.2k) ---
    q += _batch_mc([
        (
            "Which observation provides direct evidence that energy is present in a system?",
            "a measurable increase in temperature after friction between surfaces",
            ["a change in the number of protons in an atom's nucleus", "the permanent disappearance of mass from the universe", "complete absence of any particle motion at all times"],
            "Energy transfers often appear as temperature changes, motion, or deformation.",
            "Students confuse nuclear identity changes with everyday energy evidence.",
            "B2.1k", "Identifying observable evidence of energy transfer", "Easy", 55,
        ),
        (
            "Kinetic energy is defined as energy associated with",
            "motion of an object",
            ["chemical bonds stored in fuel molecules only", "position of an object relative to Earth's centre only", "static electric charge at rest on an insulator"],
            "$E_k = \\frac{1}{2}mv^2$ depends on mass and speed of moving objects.",
            "Students confuse kinetic energy with gravitational potential energy.",
            "B2.2k", "Defining kinetic energy as energy due to motion", "Easy", 55,
        ),
        (
            "Gravitational potential energy depends on",
            "mass, gravitational field strength, and vertical height",
            ["only the colour of the object", "the horizontal distance travelled along a flat road", "the age of the object in years"],
            "$E_p = mgh$ links mass, $g$, and height above a reference level.",
            "Students think potential energy depends on horizontal path length only.",
            "B2.2k", "Identifying variables in gravitational potential energy", "Easy", 60,
        ),
        (
            "Thermal energy in a substance is most closely associated with",
            "random motion and vibration of particles",
            ["only the gravitational height of the bulk material", "the net velocity of the entire object in one direction only", "permanent loss of all internal particle motion"],
            "Temperature reflects average kinetic energy of particles in random motion.",
            "Students treat thermal energy as identical to bulk translational kinetic energy only.",
            "B2.1k", "Relating thermal energy to particle motion", "Medium", 70,
        ),
        (
            "When a stretched spring is released and launches a cart, energy is converted from",
            "elastic potential energy to kinetic energy",
            ["kinetic energy to nuclear binding energy exclusively", "thermal energy to chemical energy with no mechanical change", "gravitational potential energy to light with no motion"],
            "Stored spring energy becomes motion energy of the cart.",
            "Students overlook elastic potential energy in mechanical systems.",
            "B2.2k", "Tracing elastic-to-kinetic energy conversion", "Medium", 75,
        ),
        (
            "Sound energy in a technological device such as a speaker is produced when",
            "electrical energy causes a diaphragm to vibrate, transferring energy to air",
            ["gravitational collapse of the speaker housing occurs", "all electrons in the wire stop moving permanently", "magnetic monopoles are created in the cone material"],
            "Speaker coils convert electrical input to mechanical vibration of air.",
            "Students think sound appears without a mechanical vibration source.",
            "B2.1k", "Describing electrical-to-sound energy conversion in speakers", "Medium", 75,
        ),
        (
            "Chemical energy stored in gasoline is released during combustion primarily as",
            "thermal energy and light, which can be converted to mechanical work in an engine",
            ["only gravitational potential energy with no heat produced", "pure kinetic energy of the liquid fuel before ignition", "permanent removal of energy from the universe"],
            "Fuel chemical bonds store energy released as heat and light during reaction.",
            "Students think chemical energy converts directly to motion with no thermal step.",
            "B2.1k", "Describing chemical energy release in combustion", "Medium", 80,
        ),
        (
            "Energy is said to be observed only when it is",
            "being transferred or transformed",
            ["stored indefinitely with no measurable effects ever", "created from nothing inside an isolated box", "identical to the mass of an object at rest always"],
            "Alberta Science 10 emphasizes that energy manifests during transfer between forms.",
            "Students think energy can be seen at rest without any interaction.",
            "B2.1k", "Explaining that energy is observed during transfer", "Easy", 60,
        ),
    ])

    # --- Motion, displacement, and vectors (B2.3k–B2.7k) ---
    q += _batch_mc([
        (
            "Distance and displacement differ because displacement is",
            "a vector quantity measuring straight-line change from start to finish",
            ["always greater than or equal to the path length travelled", "a scalar measuring total path length only", "measured only in units of seconds"],
            "Displacement includes direction; distance is total path length regardless of direction.",
            "Students use distance and displacement interchangeably.",
            "B2.3k", "Distinguishing displacement from distance", "Easy", 60,
        ),
        (
            "A student walks $40\\ \\text{m}$ east, then $30\\ \\text{m}$ north from the same starting point. "
            "The magnitude of the displacement is closest to",
            "$50\\ \\text{m}$",
            ["$70\\ \\text{m}$", "$10\\ \\text{m}$", "$1200\\ \\text{m}$"],
            "Displacement magnitude: $\\sqrt{40^2 + 30^2} = 50\\ \\text{m}$ by Pythagorean theorem.",
            "Students add path segments ($70\\ \\text{m}$) instead of finding resultant displacement.",
            "B2.4k", "Calculating displacement magnitude from perpendicular legs", "Medium", 85,
        ),
        (
            "Speed is calculated as",
            "distance travelled divided by time interval",
            ["displacement divided by time, always including direction in the quotient", "mass multiplied by acceleration", "force divided by area"],
            "Average speed = $\\Delta d / \\Delta t$ using path length.",
            "Students confuse speed with velocity or use force formulas.",
            "B2.5k", "Defining average speed operationally", "Easy", 55,
        ),
        (
            "Velocity differs from speed because velocity",
            "includes direction as well as magnitude",
            ["is always a larger numerical value than speed", "is measured only when an object is at rest", "does not depend on displacement or time"],
            "Velocity is a vector; speed is the magnitude of velocity.",
            "Students think velocity and speed are identical scalars.",
            "B2.5k", "Distinguishing velocity from speed", "Easy", 60,
        ),
        (
            "On a position-time graph, a straight line with positive slope indicates the object is moving with",
            "constant velocity in the positive direction",
            ["increasing acceleration throughout the interval", "zero velocity at every instant", "decreasing speed back toward the origin"],
            "Constant slope on a $d$-$t$ graph means constant rate of change of position.",
            "Students interpret any curved graph as constant velocity.",
            "B2.6k", "Interpreting constant slope on position-time graph", "Medium", 75,
        ),
        (
            "A velocity-time graph showing a horizontal line above zero means the object has",
            "constant non-zero velocity",
            ["zero velocity throughout", "constant acceleration equal to the line's height", "decreasing speed approaching rest"],
            "Horizontal $v$-$t$ line indicates velocity is not changing with time.",
            "Students confuse constant velocity with constant acceleration.",
            "B2.6k", "Interpreting horizontal line on velocity-time graph", "Medium", 70,
        ),
        (
            "Two displacement vectors of equal magnitude at $90^\\circ$ to each other combine to give a resultant with magnitude",
            "$\\sqrt{2}$ times the magnitude of either vector",
            ["exactly equal to the magnitude of one vector always", "zero because vectors always cancel", "twice the magnitude in all cases regardless of angle"],
            "Perpendicular vectors: $R = \\sqrt{A^2 + B^2} = \\sqrt{2}\\,A$ when $A = B$.",
            "Students add magnitudes directly without considering angle.",
            "B2.7k", "Finding resultant magnitude of perpendicular vectors", "Medium", 85,
        ),
        (
            "A boat heads straight across a river with velocity $3.0\\ \\text{m/s}$ north relative to the water. "
            "The river flows east at $4.0\\ \\text{m/s}$. The magnitude of the boat's velocity relative to the shore is",
            "$5.0\\ \\text{m/s}$",
            ["$7.0\\ \\text{m/s}$", "$1.0\\ \\text{m/s}$", "$12\\ \\text{m/s}$"],
            "Resultant speed: $\\sqrt{3^2 + 4^2} = 5.0\\ \\text{m/s}$.",
            "Students add ($7.0$) or subtract ($1.0$) components instead of using Pythagorean theorem.",
            "B2.7k", "Combining perpendicular velocity components", "Medium", 90,
        ),
        (
            "Negative velocity on a one-dimensional number line indicates",
            "motion in the direction opposite the chosen positive axis",
            ["the object has negative mass", "the object cannot have kinetic energy", "speed must also be negative numerically"],
            "Sign shows direction; speed is the magnitude and is non-negative.",
            "Students think negative velocity means negative speed or impossible motion.",
            "B2.5k", "Interpreting sign of velocity on a number line", "Easy", 65,
        ),
        (
            "The area under a velocity-time graph between two times represents",
            "displacement during that interval",
            ["acceleration at a single instant only", "total force applied to the object", "mass of the object in kilograms"],
            "Integrating velocity over time gives displacement: $\\Delta d = v \\Delta t$ for constant $v$.",
            "Students think the area gives speed or acceleration directly.",
            "B2.6k", "Interpreting area under velocity-time graph as displacement", "Medium", 80,
        ),
    ])

    # --- Acceleration (B2.8k, B1.2s) ---
    q += _batch_mc([
        (
            "Acceleration is defined as",
            "the rate of change of velocity",
            ["distance divided by time without regard to direction", "mass times gravitational field strength only", "total energy divided by work done"],
            "$a = \\Delta v / \\Delta t$ for constant acceleration in one dimension.",
            "Students define acceleration as speed divided by time, ignoring direction changes.",
            "B2.8k", "Defining acceleration as rate of change of velocity", "Easy", 55,
        ),
        (
            "An object slowing down while moving in the positive direction has acceleration that is",
            "negative (opposite the velocity direction)",
            ["always positive regardless of motion", "zero because speed is decreasing", "equal to velocity at every instant"],
            "Deceleration means acceleration opposes velocity vector.",
            "Students think slowing down means zero acceleration.",
            "B2.8k", "Relating acceleration sign to slowing in positive direction", "Medium", 75,
        ),
        (
            "On a velocity-time graph, constant positive acceleration appears as",
            "a straight line with positive slope",
            ["a horizontal line", "a curve approaching zero slope", "a vertical line at every time value"],
            "Slope of $v$-$t$ graph equals acceleration.",
            "Students confuse constant velocity (horizontal) with constant acceleration (sloped).",
            "B2.8k", "Identifying constant acceleration on velocity-time graph", "Medium", 75,
        ),
        (
            "Uniform acceleration means",
            "velocity changes by equal amounts in equal time intervals",
            ["speed is constant while direction changes randomly each second", "the object must remain at rest", "only gravitational field can produce the motion"],
            "Uniform (constant) acceleration implies linear change in velocity with time.",
            "Students confuse uniform acceleration with uniform velocity.",
            "B2.8k", "Defining uniform acceleration", "Easy", 60,
        ),
        (
            "When a car's velocity increases from $10\\ \\text{m/s}$ to $30\\ \\text{m/s}$ in $5.0\\ \\text{s}$, "
            "the average acceleration is",
            "$4.0\\ \\text{m/s}^2$",
            ["$2.0\\ \\text{m/s}^2$", "$6.0\\ \\text{m/s}^2$", "$20\\ \\text{m/s}^2$"],
            "$a = (30 - 10)/5.0 = 4.0\\ \\text{m/s}^2$.",
            "Students divide final velocity by time without subtracting initial velocity.",
            "B2.8k", "Calculating average acceleration from velocity change", "Medium", 80,
        ),
    ])

    q.append(nr(
        "A cyclist accelerates uniformly from rest to 20 m/s in 4.0 s. "
        "What is the average acceleration in m/s²? Record as a decimal.",
        "5.0",
        "$a = (20 - 0)/4.0 = 5.0\\ \\text{m/s}^2$.",
        "Students divide final velocity by time without subtracting initial velocity.",
        topic=TOPIC, outcome_code="B1.2s",
        skill_tested="Calculating cyclist acceleration from rest",
        difficulty="Medium", estimated_time_seconds=85,
    ))
    q.append(nr(
        "A hockey puck slows uniformly from 12 m/s to 0 m/s in 6.0 s on ice. "
        "What is the average acceleration in m/s²? Record as a decimal (include sign).",
        "-2.0",
        "$a = (0 - 12)/6.0 = -2.0\\ \\text{m/s}^2$ (negative indicates deceleration).",
        "Students report +2.0 by ignoring the direction of velocity change.",
        topic=TOPIC, outcome_code="B1.2s",
        skill_tested="Calculating deceleration of a slowing puck",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    # --- Kinetic energy (B2.9k, B2.10k, B1.1s) ---
    q += _batch_mc([
        (
            "Doubling the speed of an object while mass stays constant multiplies its kinetic energy by",
            "four",
            ["two", "eight", "one half"],
            "$E_k \\propto v^2$; $(2v)^2 = 4v^2$ gives four times the energy.",
            "Students think energy doubles linearly with speed.",
            "B2.9k", "Predicting kinetic energy change when speed doubles", "Medium", 80,
        ),
        (
            "Two objects have the same speed. Object X has twice the mass of object Y. "
            "The kinetic energy of X compared to Y is",
            "twice as large",
            ["the same", "four times as large", "one half as large"],
            "$E_k = \\frac{1}{2}mv^2$; at equal $v$, energy is proportional to mass.",
            "Students apply the $v^2$ dependence to mass incorrectly.",
            "B2.9k", "Comparing kinetic energy at equal speeds different masses", "Medium", 75,
        ),
        (
            "The SI unit for kinetic energy is the",
            "joule (J)",
            ["newton (N)", "watt (W)", "metre per second (m/s)"],
            "Energy is measured in joules; $1\\ \\text{J} = 1\\ \\text{N}\\cdot\\text{m}$.",
            "Students confuse energy units with force or power units.",
            "B2.10k", "Identifying SI unit for kinetic energy", "Easy", 50,
        ),
        (
            "Work done on an object increases its kinetic energy when",
            "the force has a component in the direction of displacement",
            ["the force is always perpendicular to displacement", "no displacement occurs", "the object remains at constant velocity with no net force"],
            "Work-energy principle: net work changes kinetic energy.",
            "Students think any force, even perpendicular, always increases $E_k$.",
            "B2.10k", "Applying work-energy relationship qualitatively", "Medium", 80,
        ),
        (
            "A $2.0\\ \\text{kg}$ ball moving at $3.0\\ \\text{m/s}$ has kinetic energy closest to",
            "$9\\ \\text{J}$",
            ["$6\\ \\text{J}$", "$3\\ \\text{J}$", "$18\\ \\text{J}$"],
            "$E_k = \\frac{1}{2}(2.0)(3.0)^2 = 9\\ \\text{J}$.",
            "Students forget the $\\frac{1}{2}$ factor or fail to square velocity.",
            "B2.9k", "Estimating kinetic energy from mass and speed", "Medium", 80,
        ),
    ])

    for mass, speed, energy in [
        (4.0, 3.0, 18.0),
        (2.0, 6.0, 36.0),
        (5.0, 4.0, 40.0),
        (0.5, 10.0, 25.0),
        (8.0, 2.5, 25.0),
        (3.0, 8.0, 96.0),
    ]:
        q.append(nr(
            f"A {mass} kg object moves at {speed} m/s. "
            f"Calculate its kinetic energy in joules using $E_k = \\frac{{1}}{{2}}mv^2$. "
            f"Record as an integer.",
            str(int(energy)),
            f"$E_k = \\frac{{1}}{{2}}({mass})({speed})^2 = {int(energy)}\\ \\text{{J}}$.",
            "Students forget to square velocity or omit the one-half factor.",
            topic=TOPIC, outcome_code="B1.1s",
            skill_tested="Calculating kinetic energy using Ek = 1/2 mv²",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # --- Gravitational potential energy (B2.11k, B2.12k, B1.2s) ---
    q += _batch_mc([
        (
            "Gravitational potential energy is zero when",
            "a reference level is chosen where height is defined as zero",
            ["an object is always at Earth's core regardless of reference", "mass equals zero in all cases", "velocity is exactly zero only"],
            "Potential energy depends on relative height; reference level is arbitrary but must be consistent.",
            "Students think absolute zero PE exists at only one universal location.",
            "B2.11k", "Explaining reference level for gravitational potential energy", "Medium", 70,
        ),
        (
            "Raising a $5.0\\ \\text{kg}$ mass vertically by $2.0\\ \\text{m}$ near Earth's surface "
            "(use $g = 9.8\\ \\text{m/s}^2$) increases its gravitational potential energy by approximately",
            "$98\\ \\text{J}$",
            ["$10\\ \\text{J}$", "$49\\ \\text{J}$", "$196\\ \\text{J}$"],
            "$\\Delta E_p = mgh = (5.0)(9.8)(2.0) \\approx 98\\ \\text{J}$.",
            "Students forget to multiply by $g$ or use height only once incorrectly.",
            "B2.11k", "Estimating gravitational potential energy change", "Medium", 85,
        ),
        (
            "When a roller coaster car descends a hill without friction, gravitational potential energy is converted primarily to",
            "kinetic energy",
            ["nuclear energy in the track rails", "permanent destruction of total mechanical energy", "chemical energy stored in the wheels only"],
            "Mechanical energy converts between $E_p$ and $E_k$ in ideal frictionless cases.",
            "Students think energy disappears rather than transforming.",
            "B2.12k", "Tracing gravitational-to-kinetic conversion on roller coaster", "Easy", 65,
        ),
        (
            "Doubling the height of an object above a reference level while mass is constant",
            "doubles the gravitational potential energy",
            ["quadruples the gravitational potential energy", "has no effect on potential energy", "halves the gravitational potential energy"],
            "$E_p = mgh$ is directly proportional to height.",
            "Students confuse height dependence ($h$) with speed dependence ($v^2$) in kinetic energy.",
            "B2.11k", "Predicting potential energy change when height doubles", "Easy", 65,
        ),
        (
            "Mechanical energy of an object in a frictionless system refers to",
            "the sum of kinetic and potential energy",
            ["thermal energy of surroundings only", "chemical energy in fuel tanks only", "energy lost irreversibly to heat always"],
            "Mechanical energy = $E_k + E_p$ in ideal mechanical analyses.",
            "Students include unrelated forms like chemical energy in mechanical sum.",
            "B2.12k", "Defining mechanical energy as Ek + Ep", "Easy", 60,
        ),
    ])

    for mass, height, energy in [
        (2.0, 5.0, 98.0),
        (4.0, 3.0, 117.6),
        (10.0, 2.0, 196.0),
        (1.5, 4.0, 58.8),
        (6.0, 1.5, 88.2),
    ]:
        q.append(nr(
            f"A {mass} kg object is lifted {height} m vertically above a reference level. "
            f"Using $g = 9.8\\ \\text{{m/s}}^2$, calculate gravitational potential energy in joules. "
            f"Record to one decimal place.",
            f"{energy:.1f}",
            f"$E_p = mgh = ({mass})(9.8)({height}) = {energy:.1f}\\ \\text{{J}}$.",
            "Students use wrong $g$ value or forget to multiply all three factors.",
            topic=TOPIC, outcome_code="B1.2s",
            skill_tested="Calculating gravitational potential energy using Ep = mgh",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # --- Energy conservation and transformations (B3.1k–B3.4k) ---
    q += _batch_mc([
        (
            "The law of conservation of energy states that in an isolated system",
            "total energy remains constant although it may change form",
            ["useful energy always increases with each conversion", "energy can be created from nothing during conversion", "thermal energy cannot be produced in any process"],
            "Energy is neither created nor destroyed; it transforms among forms.",
            "Students think conservation means useful energy is preserved unchanged.",
            "B3.1k", "Stating law of conservation of energy", "Easy", 60,
        ),
        (
            "When a falling book hits the floor and stops, its mechanical energy is primarily converted to",
            "thermal energy and sound in the book, floor, and air",
            ["gravitational potential energy stored permanently in the floor", "nuclear binding energy in the paper fibres", "energy that leaves the universe entirely"],
            "Inelastic interactions dissipate mechanical energy as heat and sound.",
            "Students think energy vanishes when motion stops.",
            "B3.2k", "Explaining energy transformation when object hits floor", "Medium", 75,
        ),
        (
            "The first law of thermodynamics is essentially a statement of",
            "conservation of energy including heat and work",
            ["the direction in which heat flows spontaneously only", "the impossibility of any temperature change", "creation of energy in steam engines"],
            "First law: $\\Delta U = Q - W$ (sign conventions vary); energy is conserved.",
            "Students confuse first law (conservation) with second law (entropy/degradation).",
            "B3.3k", "Relating first law of thermodynamics to energy conservation", "Medium", 80,
        ),
        (
            "The second law of thermodynamics implies that in real energy conversions",
            "some energy becomes less useful, often as dispersed thermal energy",
            ["all input energy can become fully useful work with no losses", "energy is destroyed and removed from Earth", "efficiency can exceed 100% in well-designed devices"],
            "Second law: entropy increases; not all energy stays in useful forms.",
            "Students think conservation means no degradation of usefulness.",
            "B3.4k", "Explaining second law implication for useful energy", "Medium", 85,
        ),
        (
            "In a pendulum swinging with air resistance, the amplitude decreases because",
            "mechanical energy is gradually converted to thermal energy in the air and pivot",
            ["gravitational field strength decreases each swing", "mass of the bob increases with each oscillation", "conservation of energy does not apply to pendulums"],
            "Friction and air drag remove mechanical energy as heat each cycle.",
            "Students think amplitude loss violates conservation of energy.",
            "B3.2k", "Explaining energy loss in damped pendulum motion", "Medium", 80,
        ),
        (
            "A hydroelectric turbine converts energy in the sequence",
            "gravitational potential energy of water → kinetic energy → electrical energy",
            ["chemical energy of coal → light → sound only", "nuclear fusion in reservoir → microwaves", "static friction in concrete → permanent magnetism only"],
            "Stored water PE drives turbines connected to generators.",
            "Students confuse hydroelectric chain with fossil fuel combustion.",
            "B3.2k", "Tracing hydroelectric energy conversion sequence", "Easy", 65,
        ),
        (
            "Regenerative braking in an electric vehicle partially recovers energy by converting",
            "kinetic energy back to stored electrical energy in the battery",
            ["thermal energy in brake pads to nuclear energy", "gravitational energy to chemical energy in tires", "all kinetic energy with 100% efficiency and no losses"],
            "Motor/generator reversal stores some kinetic energy electrically; losses still occur.",
            "Students think regeneration captures all energy with no thermal loss.",
            "B3.2k", "Describing regenerative braking energy recovery", "Medium", 80,
        ),
        (
            "In an ideal frictionless roller coaster loop, total mechanical energy at the top of a hill compared to the bottom (same track level reference) is",
            "the same if no external work is done, with $E_k$ and $E_p$ exchanging",
            ["always greater at the bottom because energy is created downhill", "zero everywhere on the track", "always greater at the top because height adds energy from nothing"],
            "Conservation: $E_k + E_p$ constant neglecting friction.",
            "Students think height alone creates new energy without transfer from $E_k$.",
            "B3.1k", "Applying mechanical energy conservation on roller coaster", "Medium", 85,
        ),
    ])

    # --- Efficiency and thermal devices (B3.5k–B3.8k, B1.3s, B1.4s) ---
    q += _batch_mc([
        (
            "Efficiency of an energy conversion device is defined as",
            "useful energy output divided by total energy input, expressed as a percentage",
            ["total input divided by useful output", "energy lost to heat only, ignoring all other forms", "always equal to 100% in real machines"],
            "Efficiency = (useful output / energy input) × 100%.",
            "Students invert the ratio or think real devices are 100% efficient.",
            "B3.5k", "Defining efficiency operationally", "Easy", 60,
        ),
        (
            "A device cannot exceed 100% efficiency because",
            "output useful energy cannot exceed total energy supplied without violating conservation",
            ["the second law requires exactly 200% efficiency in motors", "all machines convert mass directly to light only", "friction always adds energy to the system from nothing"],
            "Conservation limits useful output to at most the energy input.",
            "Students think clever design can produce more energy than supplied.",
            "B3.6k", "Explaining why efficiency cannot exceed 100%", "Easy", 65,
        ),
        (
            "In an internal combustion engine, much of the fuel's energy becomes",
            "waste thermal energy expelled in exhaust and coolant",
            ["only useful mechanical work with no heat loss", "gravitational potential energy stored in pistons permanently", "new chemical elements created in the cylinder"],
            "Real engines lose significant energy as unavoidable heat.",
            "Students underestimate thermal losses in heat engines.",
            "B3.7k", "Identifying waste energy in internal combustion engine", "Medium", 80,
        ),
        (
            "Improving insulation in a house reduces heating costs primarily by",
            "decreasing unwanted thermal energy transfer to the environment",
            ["creating energy inside walls from nothing", "eliminating the need for any temperature difference", "converting all lost heat back to electricity at 100% efficiency"],
            "Better insulation lowers rate of heat loss; less fuel/electricity needed to maintain temperature.",
            "Students think insulation generates heat rather than reducing loss.",
            "B3.8k", "Explaining how insulation improves thermal device efficiency", "Medium", 75,
        ),
        (
            "Cogeneration at a power plant improves overall efficiency by",
            "using waste heat from electricity generation for building or industrial heating",
            ["releasing all waste heat directly to the atmosphere deliberately", "burning more fuel without capturing any thermal output", "eliminating the generator entirely"],
            "Combined heat and power captures energy that would otherwise be wasted.",
            "Students think cogeneration means discarding heat faster.",
            "B3.8k", "Describing cogeneration efficiency benefit", "Medium", 80,
        ),
        (
            "LED lighting is more efficient than incandescent bulbs because LEDs convert",
            "a greater fraction of electrical input to visible light with less waste heat",
            ["electrical energy to nuclear radiation primarily", "all input energy to infrared only", "no energy at all while appearing bright"],
            "Incandescent bulbs lose most energy as infrared/heat; LEDs emit more useful light per joule.",
            "Students think brightness alone means equal efficiency.",
            "B3.8k", "Comparing LED and incandescent conversion efficiency", "Medium", 75,
        ),
    ])

    for ein, eout, label in [
        (1000, 350, "industrial conveyor motor"),
        (600, 450, "high-efficiency furnace"),
        (400, 340, "compact fluorescent lamp"),
    ]:
        eff = round(100 * eout / ein, 1)
        q.append(nr(
            f"A {label} receives {ein} J of energy input and delivers {eout} J of useful output. "
            f"What is the efficiency as a percentage? Record to one decimal place.",
            f"{eff:.1f}",
            f"Efficiency = ({eout}/{ein}) × 100% = {eff}%.",
            "Students divide input by output instead of useful output by total input.",
            topic=TOPIC, outcome_code="B1.3s",
            skill_tested=f"Calculating efficiency of a {label}",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    q.append(nr(
        "An electric motor uses 2400 J of electrical energy and produces 1800 J of useful mechanical work. "
        "How much energy is lost to non-useful forms? Record as an integer in joules.",
        "600",
        "Energy lost = input − useful output = 2400 − 1800 = 600 J.",
        "Students report useful output or efficiency instead of the energy loss.",
        topic=TOPIC, outcome_code="B1.4s",
        skill_tested="Calculating energy loss from input and useful output",
        difficulty="Medium", estimated_time_seconds=80,
    ))

    q.append(nr(
        "A light bulb converts 900 J of electrical energy into 180 J of useful light energy. "
        "What is the efficiency as a percentage? Record as an integer.",
        "20",
        "Efficiency = (180/900) × 100% = 20%.",
        "Students invert the fraction or subtract energies instead of dividing.",
        topic=TOPIC, outcome_code="B1.3s",
        skill_tested="Calculating device efficiency from energy values",
        difficulty="Easy", estimated_time_seconds=75,
    ))

    # --- Historical technologies and STS (B1.1k–B1.4k, B1.1sts, B3.1sts) ---
    q += _batch_mc([
        (
            "Early steam engines were developed and improved before scientists fully formulated the laws of thermodynamics, which shows that",
            "practical technology can advance through trial and improvement before complete theoretical models exist",
            ["thermodynamics laws are irrelevant to any real engine design", "steam engines violate conservation of energy", "no energy conversions occur in historical machines"],
            "Unit B emphasizes that engineering practice often precedes formal theory.",
            "Students think laws must be known before any useful device can exist.",
            "B1.1k", "Relating pre-thermodynamics engineering to later theory", "Medium", 80,
        ),
        (
            "James Watt's improvements to the steam engine increased efficiency partly by",
            "adding a separate condenser so the main cylinder stayed hotter",
            ["eliminating all use of steam pressure", "converting the engine to run on nuclear fission", "removing all moving parts from the design"],
            "Separate condensing reduced heat loss in the cylinder, improving performance.",
            "Students think Watt invented steam power from scratch rather than improving efficiency.",
            "B1.2k", "Describing Watt steam engine efficiency improvement", "Medium", 85,
        ),
        (
            "The development of the automobile depended on efficient conversion of",
            "chemical energy in fuel to mechanical energy for wheels",
            ["gravitational energy in tires to nuclear energy in axles", "only static electric charge in the frame", "thermal energy in air to permanent magnetism in glass"],
            "Internal combustion converts fuel chemical energy to mechanical motion.",
            "Students overlook the fuel-to-motion conversion chain in vehicles.",
            "B1.3k", "Identifying primary energy conversion in automobiles", "Easy", 65,
        ),
        (
            "Windmills used historically for grinding grain converted",
            "kinetic energy of moving air to mechanical rotation of millstones",
            ["nuclear energy in blades to chemical energy in flour only", "gravitational energy of clouds to electrical energy directly", "thermal energy of stones to wind with no moving parts"],
            "Wind turns blades; mechanical linkage drives grinding stones.",
            "Students confuse historical windmills with modern electrical wind turbines only.",
            "B1.4k", "Describing energy conversion in historical windmill", "Easy", 65,
        ),
        (
            "From an environmental STS perspective, inefficient energy conversions matter because they",
            "increase fuel consumption and greenhouse gas emissions for the same useful output",
            ["eliminate all waste heat from ecosystems permanently", "have no connection to natural resource use", "guarantee 100% useful work in all devices"],
            "Lower efficiency means more fuel burned and more environmental impact per task.",
            "Students think efficiency is purely a physics lab concept unrelated to environment.",
            "B3.1sts", "Linking conversion efficiency to environmental impact", "Medium", 80,
        ),
        (
            "When analyzing a technology from an economic STS perspective, efficiency affects",
            "operating costs because less efficient devices consume more energy per unit of useful output",
            ["only the colour of the device casing", "the number of chromosomes in the operator", "the speed of light in vacuum exclusively"],
            "Higher efficiency reduces energy bills and long-term operating expense.",
            "Students separate economic analysis from energy efficiency entirely.",
            "B1.1sts", "Applying economic perspective to energy efficiency", "Medium", 75,
        ),
        (
            "An Aboriginal perspective on energy use in technological systems may emphasize",
            "using natural resources responsibly and avoiding waste out of stewardship for the land",
            ["maximizing resource extraction without any limits always", "rejecting all technology regardless of context", "ignoring environmental consequences of energy choices"],
            "Alberta curriculum includes stewardship and judicious resource use in STS outcomes.",
            "Students think STS perspectives exclude Indigenous stewardship viewpoints.",
            "B1.1sts", "Identifying stewardship perspective in energy STS", "Medium", 75,
        ),
        (
            "Comparing incandescent, fluorescent, and LED lighting involves evaluating",
            "efficiency, cost, lifespan, and environmental impact of each technology",
            ["only the wattage printed on packaging with no other factors", "the genetic sequence of the glass filament", "whether bulbs float in water exclusively"],
            "STS analysis weighs multiple criteria when choosing lighting technology.",
            "Students reduce comparison to a single numeric label.",
            "B3.1sts", "Evaluating lighting technologies using multiple STS criteria", "Medium", 85,
        ),
        (
            "Before thermodynamics was formalized, engineers measured machine performance using concepts such as",
            "duty, horsepower, and fuel consumption per unit of work",
            ["quarks and leptons in piston assemblies", "DNA base pairing in boiler tubes", "magnetic monopoles in flywheels"],
            "Operational measures preceded abstract laws; performance was tracked practically.",
            "Students think no quantitative performance measures existed before thermodynamics.",
            "B1.2k", "Identifying pre-thermodynamics performance measures", "Medium", 80,
        ),
        (
            "A food chain in an ecosystem differs from an electrical circuit as an energy system because in the food chain",
            "energy is transferred between organisms and much is lost as heat at each trophic level",
            ["energy is conserved with 100% efficiency at every transfer", "no energy transformations occur between levels", "organisms create energy from nothing during photosynthesis and respiration"],
            "Biological energy transfers are inefficient compared to designed electrical systems.",
            "Students apply 100% efficiency incorrectly to ecological energy transfer.",
            "B3.4k", "Comparing ecological and technological energy transfer efficiency", "Medium", 85,
        ),
    ])

    # --- Additional motion/energy integration (remaining B2/B3 coverage) ---
    q += _batch_mc([
        (
            "A $60\\ \\text{kg}$ skier descends $10\\ \\text{m}$ vertically. "
            "Neglecting friction, the speed at the bottom is closest to "
            "(use $g = 9.8\\ \\text{m/s}^2$, energy conservation $mgh = \\frac{1}{2}mv^2$)",
            "$14\\ \\text{m/s}$",
            ["$5\\ \\text{m/s}$", "$98\\ \\text{m/s}$", "$1.4\\ \\text{m/s}$"],
            "$v = \\sqrt{2gh} = \\sqrt{2(9.8)(10)} \\approx 14\\ \\text{m/s}$; mass cancels.",
            "Students include mass incorrectly or forget the square root step.",
            "B2.12k", "Applying energy conservation to find speed from height", "Hard", 110,
        ),
        (
            "Power is defined as",
            "the rate at which energy is transferred or transformed",
            ["the total energy stored in an object at rest", "mass times velocity only", "displacement divided by force"],
            "Power = energy transfer / time; unit is the watt (J/s).",
            "Students confuse power with total energy or force.",
            "B2.10k", "Defining power as rate of energy transfer", "Easy", 60,
        ),
        (
            "A machine rated at $500\\ \\text{W}$ operates for $20\\ \\text{s}$. "
            "The energy transferred is",
            "$10\\ 000\\ \\text{J}$",
            ["$25\\ \\text{J}$", "$520\\ \\text{J}$", "$1000\\ \\text{J}$"],
            "$E = Pt = (500)(20) = 10\\ 000\\ \\text{J}$.",
            "Students divide power by time or add quantities incorrectly.",
            "B2.10k", "Calculating energy from power and time", "Medium", 85,
        ),
        (
            "Negative work done by friction on a sliding box means friction",
            "removes mechanical energy from the box, often as thermal energy",
            ["adds kinetic energy indefinitely without limit", "has no effect on the box's energy", "creates energy inside the box from nothing"],
            "Friction opposes motion and dissipates mechanical energy as heat.",
            "Students think negative work means no energy change occurs.",
            "B3.2k", "Interpreting negative work by friction on moving object", "Medium", 80,
        ),
        (
            "In a closed system with no external work, if potential energy decreases by $50\\ \\text{J}$, kinetic energy typically",
            "increases by $50\\ \\text{J}$ if no friction converts energy to heat",
            ["decreases by $50\\ \\text{J}$ always", "remains unchanged in all circumstances", "increases by $100\\ \\text{J}$ automatically"],
            "Conservation: $\\Delta E_p + \\Delta E_k = 0$ in ideal mechanical systems.",
            "Students think both forms decrease together.",
            "B3.1k", "Applying energy conservation between potential and kinetic forms", "Medium", 80,
        ),
        (
            "Heat engines such as car engines are limited in efficiency partly because",
            "some energy must be expelled to a cooler reservoir as required by the second law",
            ["conservation of energy does not apply to engines", "all fuel energy can become work with perfect pistons alone", "cold reservoirs absorb zero energy in all cycles"],
            "Second law limits conversion of heat to work in cyclic engines.",
            "Students blame only friction, ignoring fundamental thermodynamic limits.",
            "B3.7k", "Explaining second-law limit on heat engine efficiency", "Hard", 95,
        ),
        (
            "Choosing bicycle transportation over a car for short trips can reduce environmental impact because",
            "human-powered travel converts food chemical energy with lower fossil fuel consumption per trip",
            ["bicycles violate conservation of energy and create power from nothing", "cars use no energy when idling at intersections", "bicycles emit more CO₂ per kilometre than diesel trucks always"],
            "Active transport avoids direct fossil fuel burn for many short journeys.",
            "Students think bicycles involve no energy considerations at all.",
            "B3.1sts", "Analyzing transportation energy choices environmentally", "Medium", 75,
        ),
    ])

    return q
