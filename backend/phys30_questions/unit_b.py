"""Unit B: Forces and Fields — original Physics 30 questions."""

from .helpers import mc, nr

TOPIC = "Forces and Fields"


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
            "According to Coulomb's law, the magnitude of the electric force between two point charges varies",
            "inversely with the square of the distance between them",
            ["directly with distance", "inversely with distance only", "with the cube of the distance"],
            "$F = k|q_1 q_2|/r^2$; doubling separation reduces force to one quarter.",
            "Students forget the inverse-square dependence and treat force as $1/r$.",
            "B1.1k", "Stating Coulomb's law dependence on distance", "Easy", 55,
        ),
        (
            "Two identical positive charges are fixed at a separation of $0.20\\ \\text{m}$. "
            "If the separation is increased to $0.40\\ \\text{m}$ while charges remain unchanged, "
            "the electric force between them becomes",
            "one quarter of the original force",
            ["one half of the original force", "double the original force", "four times the original force"],
            "Force scales as $1/r^2$; doubling $r$ gives $(1/2)^2 = 1/4$.",
            "Students halve the force instead of squaring the distance ratio.",
            "B1.2k", "Predicting force change when charge separation doubles", "Medium", 75,
        ),
        (
            "Rubbing a glass rod with silk leaves the rod positively charged because",
            "electrons transfer from the rod to the silk",
            ["protons move from the silk onto the rod", "neutrons are removed from the rod surface", "the rod gains positive charge from the air"],
            "Charging by friction involves electron transfer; the rod loses electrons and becomes positive.",
            "Students think positive charge means protons move in everyday charging.",
            "B1.3k", "Explaining charging by friction via electron transfer", "Easy", 60,
        ),
        (
            "A neutral metal sphere is touched by a negatively charged rod. After contact, the sphere becomes",
            "negatively charged by conduction",
            ["positively charged by induction", "polarized but still neutral overall", "uncharged because metals cannot hold charge"],
            "Conduction shares excess charge; electrons spread onto the neutral conductor.",
            "Students confuse conduction with induction and predict opposite charge.",
            "B1.3k", "Identifying charging by conduction", "Easy", 60,
        ),
        (
            "In charging by induction, a charged object is brought near but does not touch a conductor that is",
            "grounded and then disconnected from ground before the charged object is removed",
            ["grounded throughout the entire process with no disconnection", "left ungrounded with no contact ever made", "touched directly by the charged object"],
            "Grounding allows charge redistribution; removing ground before removing the inducing charge traps the induced charge.",
            "Students remove the inducing charge before disconnecting ground, neutralizing the conductor.",
            "B1.4k", "Describing correct steps for charging by induction", "Medium", 85,
        ),
        (
            "The electric field at a point in space is defined as the",
            "electric force per unit positive test charge at that point",
            ["total charge divided by distance", "magnetic force on a moving electron", "work done per unit current"],
            "$\\vec{E} = \\vec{F}/q$ for a small positive test charge.",
            "Students define field using total force without dividing by test charge.",
            "B2.6k", "Defining electric field as force per unit charge", "Easy", 55,
        ),
        (
            "Electric field lines around an isolated positive point charge point",
            "radially outward from the charge",
            ["radially inward toward the charge", "in closed circular loops", "only horizontally to the right"],
            "Positive source charges have field lines directed away from the charge.",
            "Students reverse field line direction for positive charges.",
            "B2.6k", "Drawing electric field direction for positive charge", "Easy", 55,
        ),
        (
            "At a location where electric field lines are drawn closer together, the electric field strength is",
            "greater than where the lines are farther apart",
            ["weaker because lines crowd near weak fields", "zero because lines never cross", "independent of line spacing"],
            "Line density indicates field magnitude; crowding means stronger field.",
            "Students think crowded lines indicate weaker fields or confuse spacing with direction.",
            "B1.6k", "Interpreting electric field line density", "Medium", 70,
        ),
        (
            "Millikan's oil-drop experiment provided evidence that electric charge is",
            "quantized in multiples of a fundamental unit",
            ["continuously variable at any value", "always equal to the charge on a proton only", "produced solely by friction"],
            "Measured droplet charges were integer multiples of $e \\approx 1.6 \\times 10^{-19}\\ \\text{C}$.",
            "Students think charge can take any real value because macroscopic charge seems continuous.",
            "B1.7k", "Stating charge quantization from Millikan's experiment", "Medium", 75,
        ),
        (
            "In Millikan's apparatus, balancing a charged oil droplet in a uniform electric field requires adjusting the field until",
            "the upward electric force equals the downward gravitational force",
            ["the droplet accelerates upward indefinitely", "magnetic force cancels gravity", "the droplet becomes neutral"],
            "At balance, $qE = mg$ and the droplet remains suspended.",
            "Students think balance means net force is maximized rather than zero.",
            "B1.7k", "Explaining force balance in Millikan oil-drop setup", "Medium", 80,
        ),
        (
            "Two parallel conducting plates separated by $0.010\\ \\text{m}$ maintain a uniform electric field of "
            "$4.0 \\times 10^4\\ \\text{N/C}$ pointing from Plate P ($+$) to Plate N ($-$). "
            "The electric force on a proton located between the plates points",
            "from Plate P toward Plate N",
            ["from Plate N toward Plate P", "perpendicular to both plates", "with no force because the proton is neutral"],
            "A positive charge experiences force parallel to $\\vec{E}$, from higher to lower potential.",
            "Students apply force opposite to field for positive charges.",
            "B1.6k", "Determining force direction on proton in uniform field", "Medium", 75,
        ),
        (
            "The electric potential energy of two like charges held at fixed separation increases when",
            "the charges are moved farther apart against the repulsive electric force",
            ["the charges are moved closer together", "the charges are replaced by neutral spheres", "the distance is held constant"],
            "Work done against the field increases stored electric potential energy.",
            "Students think repelling charges lose potential energy when separated.",
            "B1.8k", "Relating electric potential energy to charge separation", "Medium", 80,
        ),
        (
            "A student maps the electric field around two equal positive charges using a positive test charge. "
            "The field at the midpoint between the charges is",
            "zero because the two field contributions cancel",
            ["maximum because both fields add", "directed toward one charge only", "undefined because fields cannot overlap"],
            "Equal-magnitude opposite-direction contributions cancel at the midpoint.",
            "Students add magnitudes without considering vector directions.",
            "B1.6k", "Analyzing field superposition between like charges", "Hard", 95,
        ),
        (
            "Polarization of a neutral insulator near a charged object occurs because",
            "charges within atoms shift slightly, creating separated positive and negative regions",
            ["protons permanently leave the material", "electrons are destroyed", "the material gains net charge without any external influence"],
            "Induced dipoles align with the external field without net charge transfer.",
            "Students think polarization requires net charge on the neutral object.",
            "B1.4k", "Explaining polarization in neutral insulators", "Medium", 75,
        ),
        (
            "In a lab charging a neutral electroscope by induction with a negative rod, the leaves diverge because",
            "like charges repel and accumulate on the leaves after grounding steps are completed",
            ["protons accumulate on the leaves", "gravity pulls the leaves apart", "the rod removes all electrons from the electroscope"],
            "Induction redistributes electrons so the leaves share the same sign and repel.",
            "Students think leaves separate due to attraction to the rod rather than leaf-leaf repulsion.",
            "B1.4s", "Interpreting electroscope leaf divergence after induction", "Medium", 85,
        ),
        (
            "A uniform electric field between parallel plates is best represented by field lines that are",
            "parallel, equally spaced, and perpendicular to the plates",
            ["radiating outward from the centre of the gap", "forming closed loops between plates", "curving to meet at the plate edges only"],
            "Large parallel plates produce nearly uniform $\\vec{E}$ except near edges.",
            "Students draw radial patterns for all electric field situations.",
            "B2.6k", "Representing uniform field between parallel plates", "Easy", 60,
        ),
        (
            "A magnetic field around a long straight current-carrying wire forms",
            "concentric circular field lines in planes perpendicular to the wire",
            ["radial lines pointing away from the wire like electric fields", "parallel lines along the wire only", "no field unless the wire is coiled"],
            "Ampère's law for a straight wire gives circular $\\vec{B}$ centred on the conductor.",
            "Students draw radial magnetic fields analogous to point charge electric fields.",
            "B2.1k", "Describing magnetic field geometry around straight wire", "Easy", 60,
        ),
        (
            "The right-hand rule for a straight conductor: thumb points along conventional current and curled fingers indicate",
            "the direction of the magnetic field around the wire",
            ["the direction of electric field inside the wire", "the force on a stationary proton nearby", "the direction electrons flow inside the wire"],
            "Thumb = current; fingers curl in the $\\vec{B}$ direction for straight wires.",
            "Students point thumb along electron flow without converting to conventional current.",
            "B2.2k", "Applying right-hand rule for straight current-carrying wire", "Easy", 65,
        ),
        (
            "A proton moves east through a uniform magnetic field directed downward. "
            "Using the right-hand rule for positive charges, the magnetic force on the proton points",
            "south",
            ["north", "upward", "east"],
            "Fingers = $\\vec{v}$ (east), curl toward $\\vec{B}$ (down); thumb points south.",
            "Students reverse the cross-product order or use left hand for positive charges.",
            "B2.3k", "Determining magnetic force direction on moving positive charge", "Medium", 85,
        ),
        (
            "The magnitude of magnetic force on a charge $q$ moving at speed $v$ perpendicular to uniform "
            "magnetic field $B$ is given by",
            "$F = qvB$",
            ["$F = qv/B$", "$F = qB/v$", "$F = qvB^2$"],
            "Maximum force occurs at $90^\\circ$ between $\\vec{v}$ and $\\vec{B}$: $F = qvB\\sin\\theta$ with $\\sin 90^\\circ = 1$.",
            "Students invert the relationship or add an extra factor of $B$.",
            "B2.4k", "Stating magnetic force magnitude for perpendicular motion", "Easy", 60,
        ),
        (
            "A charged particle enters a uniform magnetic field parallel to the field lines. "
            "The magnetic force on the particle is",
            "zero because $\\sin 0^\\circ = 0$",
            ["maximum because speed is highest", "directed opposite to the velocity", "equal to $qvB$ regardless of angle"],
            "$F = qvB\\sin\\theta$; parallel motion gives $\\theta = 0$ and zero force.",
            "Students assume any charged particle in any magnetic field experiences $qvB$.",
            "B2.4k", "Recognizing zero magnetic force for parallel motion", "Medium", 70,
        ),
        (
            "In a velocity selector, particles pass through crossed electric and magnetic fields adjusted so that",
            "electric and magnetic forces on selected-speed particles cancel",
            ["only gravitational force balances magnetic force", "magnetic force always exceeds electric force", "electric field is parallel to magnetic field"],
            "Selected particles have $qE = qvB$, allowing undeflected passage.",
            "Students think the selector accelerates all particles equally rather than filtering by speed.",
            "B3.6k", "Explaining velocity selector force balance condition", "Medium", 85,
        ),
        (
            "For a positive ion to pass straight through a velocity selector with $\\vec{E}$ upward and "
            "$\\vec{B}$ into the page, the required velocity must be directed",
            "to the right",
            ["to the left", "upward", "into the page"],
            "$\\vec{F}_E$ is down; $\\vec{F}_B$ must be up, requiring $\\vec{v}$ right by right-hand rule.",
            "Students choose velocity parallel to $\\vec{E}$ or $\\vec{B}$ instead of perpendicular to both.",
            "B3.6k", "Determining velocity direction in velocity selector", "Hard", 100,
        ),
        (
            "A current-carrying wire in a uniform external magnetic field experiences maximum force when the wire is",
            "perpendicular to the field direction",
            ["parallel to the field direction", "shielded by insulation only", "stationary with no current"],
            "$F = BIL\\sin\\theta$; maximum at $\\theta = 90^\\circ$.",
            "Students think force is greatest when wire is parallel to $\\vec{B}$.",
            "B3.8k", "Identifying orientation for maximum force on current-carrying wire", "Medium", 75,
        ),
        (
            "The force on a straight wire of length $L$ carrying current $I$ perpendicular to magnetic field $B$ is",
            "$F = BIL$",
            ["$F = BI/L$", "$F = BIL^2$", "$F = IL/B$"],
            "Wire force law parallels charge force: $F = BIL\\sin\\theta$ with $\\sin 90^\\circ = 1$.",
            "Students confuse wire force with point-charge $qvB$ without including length.",
            "B3.8k", "Applying force law for current-carrying conductor", "Easy", 65,
        ),
        (
            "A galvanometer can detect current because a magnetic field exerts torque on",
            "a coil carrying current placed in the field",
            ["stationary neutral atoms in the coil", "the insulation on the connecting wires only", "the battery's chemical energy directly"],
            "Current in a coil experiences $\\vec{B}$-induced torque proportional to $I$.",
            "Students think magnetic fields push electrons without involving coil orientation.",
            "B3.7k", "Explaining galvanometer operation using motor principle", "Medium", 80,
        ),
        (
            "Two parallel wires carrying currents in the same direction",
            "attract each other",
            ["repel each other", "experience no force", "exchange electric charge"],
            "Each wire's field exerts force on the other's current; same-direction currents attract.",
            "Students apply like-current repulsion rule incorrectly.",
            "B3.7k", "Predicting force between parallel current-carrying wires", "Medium", 80,
        ),
        (
            "The Earth's magnetic field near the surface is useful for navigation because a",
            "compass needle aligns with the local magnetic field direction",
            ["compass measures electric field from the ionosphere", "compass detects gravitational field variations", "compass works only at the magnetic equator"],
            "A freely pivoted magnet aligns parallel to $\\vec{B}_{Earth}$.",
            "Students think compasses find geographic north without magnetic field alignment.",
            "B2.1sts", "Relating compass behaviour to Earth's magnetic field", "Easy", 65,
        ),
        (
            "A charged particle moving in a plane perpendicular to a uniform magnetic field follows",
            "a circular path at constant speed",
            ["a straight line accelerating forward", "a parabolic path like projectile motion", "a spiral that immediately stops"],
            "Magnetic force is always perpendicular to $\\vec{v}$, providing centripetal acceleration only.",
            "Students confuse magnetic deflection with gravitational projectile paths.",
            "B3.5k", "Predicting trajectory of charge in perpendicular magnetic field", "Medium", 85,
        ),
        (
            "Increasing the current in a solenoid while keeping the same number of turns and core material generally",
            "strengthens the magnetic field inside the solenoid",
            ["eliminates the magnetic field", "reverses only the electric field outside", "has no effect on magnetic field strength"],
            "Solenoid field is proportional to current: $B \\propto I$ for fixed geometry.",
            "Students think field depends only on number of turns, ignoring current.",
            "B3.4k", "Relating solenoid field strength to current", "Easy", 60,
        ),
        (
            "A laboratory magnet labeled with N and S poles creates field lines that outside the magnet run",
            "from north pole to south pole through the surrounding space",
            ["from south to north externally only", "only inside the magnet with no external field", "perpendicular to all iron filings everywhere"],
            "External field lines leave north and enter south, forming continuous loops through the magnet.",
            "Students think lines start at south externally or exist only inside the material.",
            "B2.1k", "Drawing external magnetic field lines for bar magnet", "Easy", 60,
        ),
        (
            "When a conductor moves through a magnetic field and experiences an induced current, energy is transferred by",
            "the mechanical work done moving the conductor against magnetic forces",
            ["creating charge from nothing inside the conductor", "increasing the conductor's mass", "eliminating the magnetic field permanently"],
            "Generator effect converts mechanical input to electrical energy via changing flux.",
            "Students think induced current appears without energy input.",
            "B3.1k", "Linking induced current to mechanical energy input", "Medium", 80,
        ),
        (
            "Faraday's law states that the magnitude of induced emf is proportional to",
            "the rate of change of magnetic flux through the loop",
            ["the total flux regardless of time", "the square of the magnetic field only", "the wire's resistance alone"],
            "$\\mathcal{E} = -N\\,\\Delta\\Phi/\\Delta t$; changing flux induces emf.",
            "Students think constant nonzero flux always induces emf.",
            "B3.3k", "Stating Faraday's law dependence on flux change rate", "Easy", 65,
        ),
        (
            "Lenz's law determines the direction of induced current such that the induced magnetic field",
            "opposes the change in external flux that caused it",
            ["always aligns with the external field", "always doubles the external flux change", "is unrelated to flux change"],
            "Induced effects oppose the change producing them, consistent with energy conservation.",
            "Students think induced field always aids the original flux change.",
            "B3.3k", "Applying Lenz's law to oppose flux change", "Medium", 80,
        ),
        (
            "A bar magnet is pushed toward a conducting coil. By Lenz's law, the coil's induced magnetic field near the "
            "approaching pole will",
            "repel the approaching magnet",
            ["attract the magnet more strongly", "have no interaction with the magnet", "cancel Earth's magnetic field completely"],
            "Coil creates field opposing increasing flux — repulsion slows the approach.",
            "Students predict attraction, thinking induced poles always match approaching poles.",
            "B3.3k", "Predicting repulsion when magnet approaches coil", "Medium", 85,
        ),
        (
            "In a simple electric motor, a current-carrying coil in a magnetic field experiences",
            "a torque that can produce continuous rotation when commutated",
            ["no force because the coil is symmetric", "only gravitational torque", "uniform acceleration along the field lines"],
            "Motor effect: $\\vec{B}$ exerts force on current segments, producing torque about the axis.",
            "Students confuse motor torque with generator induction.",
            "B3.7k", "Explaining motor operation via torque on current coil", "Easy", 65,
        ),
        (
            "A split-ring commutator in a DC motor reverses current in the coil every half rotation so that",
            "torque continues to drive rotation in the same direction",
            ["the coil stops after one half turn", "magnetic field direction reverses instead", "electric field inside the coil disappears"],
            "Commutation flips current direction as torque would otherwise reverse.",
            "Students think commutators measure induced emf rather than reverse supply current.",
            "B3.5k", "Describing commutator role in DC motor", "Medium", 80,
        ),
        (
            "An electric generator converts mechanical energy to electrical energy by",
            "rotating a coil in a magnetic field to change magnetic flux through the coil",
            ["passing constant flux through a stationary coil", "heating the coil until electrons evaporate", "storing charge on the commutator permanently"],
            "Changing flux induces emf; rotation provides continuous flux change.",
            "Students think generators create energy without mechanical input.",
            "B3.6k", "Describing generator energy conversion via flux change", "Easy", 65,
        ),
        (
            "The output of an AC generator varies sinusoidally because the induced emf depends on",
            "the changing angle between the coil plane and the magnetic field during rotation",
            ["a constant flux always producing constant emf", "only the coil's resistance changing", "gravitational potential energy of the coil"],
            "$\\mathcal{E} \\propto \\sin(\\omega t)$ as flux linkage varies with rotation.",
            "Students expect DC output from any rotating coil without commutator.",
            "B3.7k", "Explaining sinusoidal AC output from rotating coil", "Medium", 85,
        ),
        (
            "Eddy currents induced in a metal plate moving through a magnetic field can",
            "oppose the motion by magnetic interaction, acting as electromagnetic braking",
            ["accelerate the plate without energy loss", "eliminate all magnetic field in the region", "flow only in non-metallic materials"],
            "Lenz's law: eddy currents create fields opposing motion, dissipating kinetic energy.",
            "Students think induced currents always speed up the moving conductor.",
            "B3.8k", "Explaining electromagnetic braking via eddy currents", "Medium", 85,
        ),
        (
            "A transformer steps voltage up on the secondary coil compared to the primary when the secondary has",
            "more turns than the primary",
            ["fewer turns than the primary", "the same turns with no core", "no magnetic flux linking the coils"],
            "$V_s/V_p = N_s/N_p$ for ideal transformers; more secondary turns gives higher secondary voltage.",
            "Students invert the turns ratio or think transformers create power.",
            "B3.9k", "Applying transformer turns ratio to voltage", "Medium", 80,
        ),
        (
            "In a motor versus generator comparison using the same coil and field, the motor requires",
            "an external current supply to produce rotation",
            ["only mechanical rotation with no electrical input", "a permanent absence of magnetic flux", "static charges on the commutator only"],
            "Motors convert electrical to mechanical; generators do the reverse.",
            "Students cannot distinguish which device needs external electrical input.",
            "B3.7k", "Distinguishing motor input from generator output", "Easy", 60,
        ),
        (
            "A student moves a magnet into a solenoid connected to a galvanometer and observes deflection. "
            "Reversing the direction of motion without changing speed",
            "reverses the galvanometer deflection direction",
            ["produces identical deflection", "produces zero deflection", "triples the resistance of the solenoid"],
            "Opposite $\\Delta\\Phi/\\Delta t$ sign reverses induced emf polarity per Lenz's law.",
            "Students think speed alone sets direction, ignoring motion direction relative to coil.",
            "B3.2s", "Predicting galvanometer reversal when motion reverses", "Medium", 85,
        ),
        (
            "A particle with speed $2.0 \\times 10^6\\ \\text{m/s}$ enters a velocity selector where "
            "$E = 4.0 \\times 10^4\\ \\text{N/C}$ and $B = 0.020\\ \\text{T}$. "
            "For the particle to pass undeflected, the required speed satisfies",
            "$v = E/B$",
            ["$v = EB$", "$v = B/E$", "$v = E^2/B$"],
            "Balance gives $v = E/B = (4.0 \\times 10^4)/(0.020) = 2.0 \\times 10^6\\ \\text{m/s}$.",
            "Students multiply $E$ and $B$ or invert the ratio.",
            "B3.6k", "Applying velocity selector equation $v = E/B$", "Hard", 95,
        ),
        (
            "When analyzing force on a current loop in a uniform magnetic field, the maximum torque occurs when the "
            "plane of the loop is",
            "parallel to the magnetic field",
            ["perpendicular to the field", "aligned so no current flows", "removed from the field entirely"],
            "Torque is maximum when magnetic moment is perpendicular to $\\vec{B}$ (loop plane parallel to field).",
            "Students confuse loop plane orientation with magnetic moment orientation.",
            "B3.7k", "Identifying orientation for maximum torque on current loop", "Hard", 100,
        ),
        (
            "A negatively charged oil droplet in Millikan's experiment is held stationary between horizontal plates "
            "with the upper plate positive. The electric force on the droplet acts",
            "upward toward the positive plate",
            ["downward toward the negative plate", "horizontally between the plates", "with zero magnitude at balance"],
            "Field points from the positive plate downward; a negative charge experiences force opposite to $\\vec{E}$, so upward.",
            "Students apply force direction for positive charges to negative droplets.",
            "B1.7k", "Determining electric force direction on negative droplet", "Medium", 80,
        ),
        (
            "A conducting rod slides on rails perpendicular to a uniform magnetic field. "
            "An induced current circulates if the rod moves because",
            "the area enclosed by the loop changes, changing magnetic flux",
            ["the rod's mass changes", "the magnetic field reverses spontaneously", "static charge appears without flux change"],
            "Motional emf arises from changing flux through the expanding or contracting loop.",
            "Students think any motion in a field induces current without flux change.",
            "B3.9k", "Explaining motional emf from changing loop area", "Medium", 85,
        ),
        (
            "A proton and an electron at the same distance from a large positive plate in a parallel-plate capacitor "
            "experience electric forces that are",
            "equal in magnitude but opposite in direction",
            ["equal in magnitude and the same direction", "zero for the electron only", "independent of plate charge"],
            "Same $|q|$ and same $E$ give equal $F$ magnitudes; opposite signs give opposite directions.",
            "Students think the lighter electron must experience smaller electric force.",
            "B1.6k", "Comparing forces on proton and electron in uniform field", "Medium", 75,
        ),
    ])

    q.append(nr(
        "Two point charges of $+3.0 \\times 10^{-6}\\ \\text{C}$ and $-3.0 \\times 10^{-6}\\ \\text{C}$ "
        "are separated by $0.30\\ \\text{m}$. Using $k = 9.0 \\times 10^9\\ \\text{N·m}^2/\\text{C}^2$, "
        "what is the magnitude of the electric force in newtons? Record to two significant figures.",
        "0.90",
        "$F = k|q_1 q_2|/r^2 = (9.0 \\times 10^9)(3.0 \\times 10^{-6})^2/(0.30)^2 "
        "= (9.0 \\times 10^9)(9.0 \\times 10^{-12})/0.090 = 0.90\\ \\text{N}$.",
        "Students forget to square the distance or mishandle scientific notation exponents.",
        topic=TOPIC, outcome_code="B1.2k",
        skill_tested="Calculating Coulomb force between two point charges",
        difficulty="Medium", estimated_time_seconds=120,
    ))

    q.append(nr(
        "A uniform electric field of $2.5 \\times 10^3\\ \\text{N/C}$ acts on a proton. "
        "What is the magnitude of the electric force in newtons? "
        "Use $e = 1.6 \\times 10^{-19}\\ \\text{C}$. Record in scientific notation as $a \\times 10^b$ with one digit before the decimal.",
        "4.0e-16",
        "$F = qE = (1.6 \\times 10^{-19})(2.5 \\times 10^3) = 4.0 \\times 10^{-16}\\ \\text{N}$.",
        "Students multiply exponents incorrectly or use electron mass instead of charge.",
        topic=TOPIC, outcome_code="B1.6k",
        skill_tested="Computing electric force on proton in uniform field",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    q.append(nr(
        "An electron travels at $3.0 \\times 10^6\\ \\text{m/s}$ perpendicular to a uniform magnetic field of "
        "$0.15\\ \\text{T}$. What is the magnitude of the magnetic force in newtons? "
        "Use $e = 1.6 \\times 10^{-19}\\ \\text{C}$. Record in scientific notation as $a \\times 10^b$.",
        "7.2e-14",
        "$F = qvB = (1.6 \\times 10^{-19})(3.0 \\times 10^6)(0.15) = 7.2 \\times 10^{-14}\\ \\text{N}$.",
        "Students omit the charge, divide by $B$, or fail to use perpendicular condition.",
        topic=TOPIC, outcome_code="B2.4k",
        skill_tested="Calculating magnetic force on moving electron",
        difficulty="Medium", estimated_time_seconds=100,
    ))

    q.append(nr(
        "A straight wire $0.25\\ \\text{m}$ long carries $4.0\\ \\text{A}$ perpendicular to a "
        "$0.80\\ \\text{T}$ magnetic field. What is the magnetic force on the wire in newtons? "
        "Record to two significant figures.",
        "0.80",
        "$F = BIL = (0.80)(4.0)(0.25) = 0.80\\ \\text{N}$.",
        "Students use $qvB$ instead of $BIL$ or forget to include wire length.",
        topic=TOPIC, outcome_code="B2.6k",
        skill_tested="Calculating force on current-carrying wire in magnetic field",
        difficulty="Easy", estimated_time_seconds=75,
    ))

    return q
