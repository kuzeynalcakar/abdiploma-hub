"""Unit A: Momentum and Impulse — original Physics 30 questions."""

from .helpers import mc, nr

TOPIC = "Momentum and Impulse"


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
            "Momentum is defined as a vector quantity equal to",
            "the product of an object's mass and its velocity",
            ["mass divided by velocity", "the sum of mass and speed", "force multiplied by time only"],
            "$\\vec{p} = m\\vec{v}$; momentum depends on both mass and velocity direction.",
            "Students define momentum using speed only or confuse it with impulse.",
            "A1.1k", "Defining momentum as mass times velocity", "Easy", 55,
        ),
        (
            "Impulse delivered to an object equals",
            "the change in momentum of the object",
            ["the object's kinetic energy at impact", "mass times gravitational acceleration", "the total force acting before contact"],
            "Impulse $\\vec{J} = \\Delta\\vec{p}$; it quantifies momentum transfer during a force interaction.",
            "Students equate impulse with kinetic energy or with force alone.",
            "A1.2k", "Relating impulse to change in momentum", "Easy", 60,
        ),
        (
            "In an isolated system, the total momentum before an interaction equals",
            "the total momentum after the interaction",
            ["zero always, regardless of collision type", "the total kinetic energy after the interaction", "the sum of individual forces on each object"],
            "Momentum conservation holds when no net external impulse acts on the system.",
            "Students assume momentum is not conserved in inelastic collisions.",
            "A1.3k", "Stating momentum conservation in isolated systems", "Easy", 60,
        ),
        (
            "A collision in which kinetic energy is conserved is classified as",
            "elastic",
            ["inelastic", "perfectly inelastic only", "impossible in real macroscopic systems"],
            "Elastic collisions conserve both momentum and kinetic energy.",
            "Students label any collision with separated objects as elastic.",
            "A1.5k", "Classifying elastic collisions by KE conservation", "Easy", 55,
        ),
        (
            "Two carts stick together after colliding. This interaction is best described as",
            "perfectly inelastic",
            ["elastic", "explosive separation", "momentum-not-conserved"],
            "Objects that move as one after contact share a common final velocity — perfectly inelastic.",
            "Students think sticking together still conserves kinetic energy.",
            "A1.5k", "Identifying perfectly inelastic collisions", "Medium", 70,
        ),
        (
            "Newton's third law explains momentum conservation because internal forces between interacting objects are",
            "equal in magnitude and opposite in direction",
            ["always zero during contact", "proportional to mass only", "independent of contact time"],
            "Action-reaction pairs cancel as external impulses on the isolated pair.",
            "Students think the heavier object exerts a larger force during contact.",
            "A1.3k", "Linking Newton's third law to momentum conservation", "Medium", 75,
        ),
        (
            "The area under a force-time graph for a single object during a collision represents",
            "the impulse experienced by that object",
            ["the object's instantaneous velocity", "the kinetic energy lost only", "the acceleration at one instant"],
            "Impulse equals the integral of force over time, shown as area under an $F$-$t$ graph.",
            "Students read the slope instead of the area, confusing force with impulse.",
            "A1.2k", "Interpreting impulse from force-time graph area", "Medium", 80,
        ),
        (
            "When analyzing a two-cart collision on a low-friction track, treating the two carts as one system is useful because",
            "external friction forces are small compared to internal collision forces",
            ["momentum is never conserved on tracks", "each cart must always be analyzed separately", "kinetic energy is always conserved on tracks"],
            "Low friction allows the pair to approximate an isolated system for momentum analysis.",
            "Students assume tracks automatically guarantee energy conservation.",
            "A1.3k", "Justifying isolated-system approximation for carts", "Medium", 75,
        ),
        (
            "Airbags increase injury protection primarily by",
            "extending the time over which the passenger's momentum changes",
            ["increasing the peak force on the passenger", "eliminating the need for seat belts", "reducing the passenger's mass during impact"],
            "Longer $\\Delta t$ for the same $\\Delta p$ reduces average force via $F_{avg} = \\Delta p / \\Delta t$.",
            "Students think airbags work by absorbing mass rather than extending collision time.",
            "A1.1sts", "Explaining airbag design using impulse concepts", "Medium", 80,
        ),
        (
            "Rocket propulsion in deep space demonstrates conservation of momentum because",
            "expelled exhaust gains momentum opposite to the rocket's forward motion",
            ["gravity provides the forward thrust", "no momentum is transferred without air to push against", "only kinetic energy is conserved"],
            "Rocket + exhaust is an isolated system; total momentum remains constant.",
            "Students think rockets require an atmosphere to push against.",
            "A1.1sts", "Applying momentum conservation to rocket thrust", "Medium", 85,
        ),
        (
            "In a head-on elastic collision between two identical carts with equal speed and opposite direction, the carts",
            "reverse directions with the same speeds as before",
            ["stop completely and remain at rest", "stick together and move at half the original speed", "both move in the same direction afterward"],
            "Equal-mass elastic head-on exchange reverses velocities.",
            "Students predict both carts stop because forces are equal.",
            "A1.4k", "Predicting equal-mass elastic head-on outcome", "Hard", 95,
        ),
        (
            "A variable that must be controlled when comparing impulse on different foam pads is",
            "the initial speed of the object striking the pad",
            ["the colour of the foam pad", "the brand name printed on the pad", "the room temperature only"],
            "Fair comparison requires the same incoming momentum change while varying contact material.",
            "Students identify manipulated and responding variables but miss controlled variables.",
            "A1.1s", "Identifying controlled variables in impulse experiment", "Medium", 85,
        ),
        (
            "When a hockey puck's velocity changes from $+8.0\\ \\text{m/s}$ to $-4.0\\ \\text{m/s}$, the sign change indicates",
            "a reversal in the direction of the momentum vector",
            ["momentum became negative mass", "the puck lost all its mass", "impulse was zero because speed changed"],
            "Momentum is a vector; sign reflects direction along the chosen axis.",
            "Students treat negative velocity as a separate scalar error rather than direction reversal.",
            "A1.1k", "Interpreting signed velocity in momentum calculations", "Medium", 70,
        ),
        (
            "Comparing impulse and kinetic energy for the same collision, impulse relates to",
            "momentum change, while kinetic energy relates to work done on the system",
            ["both measuring exactly the same physical quantity", "impulse being always larger than kinetic energy", "kinetic energy determining the force-time area"],
            "Impulse and kinetic energy answer different questions about the interaction.",
            "Students use kinetic energy formulas when impulse is required.",
            "A1.2k", "Distinguishing impulse from kinetic energy", "Medium", 75,
        ),
        (
            "If external friction on a sliding block is significant, the block-track system should be classified as",
            "non-isolated",
            ["isolated because only two objects exist", "isolated if the block is heavy", "isolated if the track is level"],
            "External friction impulses prevent strict momentum conservation for the block alone.",
            "Students assume two-object systems are always isolated.",
            "A1.3k", "Classifying systems with external friction", "Medium", 70,
        ),
        (
            "In a two-dimensional collision analysis, a scaled vector diagram can be used instead of sine and cosine laws when",
            "the diagram is drawn carefully to scale and answers need only approximate graphical results",
            ["no vectors are involved in 2D collisions", "momentum is not a vector quantity", "2D collisions never conserve momentum"],
            "Alberta POS allows graphical vector addition for 2D momentum problems.",
            "Students think 2D momentum problems always require component equations.",
            "A1.3s", "Selecting graphical method for 2D momentum", "Hard", 100,
        ),
        (
            "Sporting helmets reduce concussion risk by",
            "increasing the collision time so the brain experiences lower average force for the same momentum change",
            ["decreasing the player's mass during impact", "eliminating all momentum transfer to the head", "converting momentum into gravitational potential energy"],
            "Same $\\Delta p$ over longer time reduces peak acceleration experienced by the brain.",
            "Students think helmets prevent all momentum transfer rather than extend contact time.",
            "A1.1sts", "Relating helmet design to impulse and force reduction", "Easy", 70,
        ),
        (
            "The slope of a line on a graph of post-collision speed versus pre-collision speed for inelastic cart collisions is typically",
            "less than 1 and positive",
            ["exactly 2 for all collisions", "negative for all inelastic cases", "undefined because momentum is not conserved"],
            "In inelastic collisions, final speed magnitude is less than incoming speed for the striking cart.",
            "Students expect slope 1 because momentum is conserved.",
            "A1.3s", "Interpreting inelastic collision speed graph slope", "Hard", 105,
        ),
    ])

    q.append(nr(
        "A $0.50\\ \\text{kg}$ ball moving at $12\\ \\text{m/s}$ strikes a wall and rebounds at $8.0\\ \\text{m/s}$ "
        "in the opposite direction. What is the magnitude of the momentum change in $\\text{kg·m/s}$? "
        "Record as a whole number.",
        "10",
        "$|\\Delta p| = m|v_f - v_i| = 0.50 \\times |{-8} - 12| = 0.50 \\times 20 = 10\\ \\text{kg·m/s}$.",
        "Students subtract speeds without accounting for direction reversal (getting 2 instead of 10).",
        topic=TOPIC, outcome_code="A1.2k",
        skill_tested="Calculating momentum change for rebounding ball",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    q.append(nr(
        "A hockey puck of mass $0.17\\ \\text{kg}$ has momentum $1.02\\ \\text{kg·m/s}$. "
        "What is its speed in $\\text{m/s}$? Record to one decimal place.",
        "6.0",
        "$v = p/m = 1.02/0.17 = 6.0\\ \\text{m/s}$.",
        "Students multiply mass and momentum instead of dividing.",
        topic=TOPIC, outcome_code="A1.1k",
        skill_tested="Computing speed from momentum and mass",
        difficulty="Easy", estimated_time_seconds=65,
    ))

    return q
