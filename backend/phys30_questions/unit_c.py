"""Unit C: Electromagnetic Radiation — original Physics 30 questions."""

from .helpers import mc, nr

TOPIC = "Electromagnetic Radiation"


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
            "In the classical wave model of electromagnetic radiation, the electric and magnetic field components oscillate",
            "perpendicular to each other and to the direction of propagation",
            ["parallel to the direction of propagation only", "in the same direction as each other along the ray path", "only when the radiation passes through a vacuum"],
            "Transverse EM waves have mutually perpendicular $\\vec{E}$ and $\\vec{B}$ fields, both normal to propagation.",
            "Students describe EM fields as longitudinal like sound in air.",
            "C1.1k", "Describing transverse nature of EM fields", "Easy", 55,
        ),
        (
            "All electromagnetic waves in vacuum share the same",
            "speed of $3.00 \\times 10^8\\ \\text{m/s}$ regardless of frequency",
            ["wavelength, which is fixed for every type of radiation", "period, which is identical for radio and gamma rays", "amplitude, which must be constant in vacuum"],
            "In vacuum, $c = f\\lambda$ is constant; changing frequency changes wavelength inversely.",
            "Students think higher-frequency radiation travels faster in vacuum.",
            "C1.2k", "Stating constant speed of EM waves in vacuum", "Easy", 55,
        ),
        (
            "The relationship $c = f\\lambda$ implies that doubling the frequency of an EM wave in vacuum",
            "halves its wavelength while speed remains unchanged",
            ["doubles its wavelength and doubles its speed", "leaves wavelength unchanged", "quadruples its speed"],
            "With $c$ fixed, $f$ and $\\lambda$ are inversely proportional.",
            "Students treat frequency and wavelength as directly proportional.",
            "C1.2k", "Applying inverse proportion of frequency and wavelength", "Easy", 60,
        ),
        (
            "X-rays and gamma rays are grouped at the high-energy end of the spectrum primarily because they have",
            "very high frequencies and very short wavelengths",
            ["lower speed in vacuum than infrared radiation", "longer wavelengths than ultraviolet light", "magnetic fields but no oscillating electric fields"],
            "Photon energy and wave frequency are highest for ionizing short-wavelength radiation.",
            "Students select X-rays based on speed differences in vacuum.",
            "C1.3k", "Identifying high-frequency end of EM spectrum", "Easy", 65,
        ),
        (
            "Polarizing sunglasses reduce glare from horizontal surfaces mainly by",
            "blocking light whose electric field oscillates in a selected plane",
            ["increasing the speed of reflected light in glass", "converting transverse waves into longitudinal waves", "absorbing all wavelengths equally without orientation effect"],
            "Polarizers transmit one polarization plane and absorb the orthogonal component.",
            "Students think polarization changes the frequency of reflected light.",
            "C1.4k", "Explaining polarization as evidence for transverse waves", "Medium", 75,
        ),
        (
            "For an electromagnetic wave, doubling the amplitude of the oscillating electric field typically",
            "quadruples the intensity of the radiation",
            ["doubles the intensity only", "does not affect intensity at all", "halves the wavelength in vacuum"],
            "Intensity is proportional to the square of amplitude for sinusoidal waves.",
            "Students assume intensity scales linearly with amplitude.",
            "C1.4k", "Relating wave amplitude to radiation intensity", "Medium", 80,
        ),
        (
            "A medical imaging team chooses X-rays instead of radio waves to image bone because X-rays",
            "have wavelengths short enough to resolve fine internal structures",
            ["travel slower through tissue so they map density directly", "are longitudinal and penetrate solids more easily", "have lower photon energy and therefore pass through bone"],
            "Short-wavelength radiation improves resolution and interacts strongly with dense matter.",
            "Students think radio waves are chosen for imaging because they are safer due to higher energy.",
            "C1.1sts", "Justifying X-ray selection for medical imaging", "Medium", 85,
        ),
        (
            "When a light ray strikes a smooth plane mirror, the angle of reflection is measured between",
            "the reflected ray and the normal to the surface",
            ["the incident ray and the mirror surface only", "the reflected ray and the mirror surface only", "the incident and reflected rays with no reference to the normal"],
            "Both incidence and reflection angles are defined relative to the normal.",
            "Students measure angles from the mirror surface instead of the normal.",
            "C1.5k", "Applying law of reflection with normal reference", "Easy", 60,
        ),
        (
            "Diffuse reflection from rough paper differs from specular reflection from a mirror because rough surfaces",
            "reflect parallel incident rays in many directions",
            ["do not obey the law of reflection at each micro-facet", "absorb all light and emit none", "reverse the frequency of incoming light"],
            "Each tiny facet obeys reflection locally, but surface irregularities scatter rays.",
            "Students think diffuse reflection violates the law of reflection.",
            "C1.5k", "Distinguishing specular and diffuse reflection", "Medium", 70,
        ),
        (
            "The index of refraction $n$ of a transparent medium is defined as",
            "the ratio of the speed of light in vacuum to the speed in the medium",
            ["the ratio of the angle of incidence to the angle of refraction", "the product of frequency and wavelength in the medium", "the sine of the critical angle only"],
            "$n = c/v$ compares vacuum speed to medium speed.",
            "Students confuse $n$ with Snell's law ratio $\\sin\\theta_i/\\sin\\theta_r$.",
            "C1.6k", "Defining index of refraction", "Easy", 65,
        ),
        (
            "A light ray entering glass from air bends toward the normal because in glass the light",
            "travels slower while its frequency stays essentially unchanged",
            ["speeds up while wavelength decreases", "changes frequency to match the medium", "maintains the same direction as in air"],
            "Reduced speed with fixed frequency means shorter wavelength and refraction toward the normal.",
            "Students think refraction occurs because frequency changes at the boundary.",
            "C1.6k", "Explaining refraction toward normal in denser medium", "Medium", 75,
        ),
        (
            "According to Snell's law, if light passes from medium A ($n = 1.33$) into medium B ($n = 1.50$), the refracted ray in B will",
            "bend toward the normal compared with the incident direction in A",
            ["bend away from the normal because it speeds up", "travel undeflected regardless of angle", "reflect completely for every angle of incidence"],
            "Entering a higher-index medium slows light and bends it toward the normal.",
            "Students predict bending away from the normal whenever a ray enters a new medium.",
            "C1.6k", "Predicting refraction direction using relative index", "Medium", 80,
        ),
        (
            "Total internal reflection can occur only when light attempts to travel from",
            "a higher-index medium into a lower-index medium at angles beyond the critical angle",
            ["any medium into vacuum at very small angles of incidence", "air into glass at all angles of incidence", "a lower-index medium into a higher-index medium"],
            "TIR requires incidence in the optically denser medium with angle exceeding $\\theta_c$.",
            "Students think TIR happens whenever light hits any transparent boundary.",
            "C1.7k", "Stating conditions for total internal reflection", "Medium", 80,
        ),
        (
            "Optical fibre communication relies on repeated total internal reflection so that light pulses",
            "remain guided inside the core with minimal loss through the cladding",
            ["gain speed in the cladding to reach distant receivers", "diffract outward at every bend to broadcast signals", "change frequency each time they reflect internally"],
            "Core-cladding index contrast traps rays by TIR along curved paths.",
            "Students think fibre optics works by simple mirror reflection at the outer glass surface.",
            "C1.1sts", "Explaining optical fibre operation using TIR", "Medium", 85,
        ),
        (
            "A fisherman sees a fish closer to the surface than its actual depth because light from the fish",
            "bends away from the normal when leaving water, making the image appear shallower",
            ["speeds up entering water and focuses to a deeper image", "is completely absorbed before reaching the eye", "undergoes total internal reflection at the water surface always"],
            "Refraction at the water-air interface produces a virtual image above the real object.",
            "Students think the fish looks deeper because light slows in air.",
            "C1.7k", "Explaining apparent depth with refraction", "Medium", 85,
        ),
        (
            "A converging thin lens is also described as",
            "convex",
            ["concave", "diverging", "plane"],
            "Converging lenses are thicker at the centre and have convex surfaces.",
            "Students pair converging with concave because both words contain letter patterns they confuse.",
            "C1.8k", "Matching converging lens to convex terminology", "Easy", 55,
        ),
        (
            "A diverging thin lens is also described as",
            "concave",
            ["convex", "converging", "parabolic mirror"],
            "Diverging lenses are thinner at the centre and have concave surfaces.",
            "Students label diverging lenses as convex.",
            "C1.8k", "Matching diverging lens to concave terminology", "Easy", 55,
        ),
        (
            "A concave mirror used in a shaving mirror acts as a",
            "converging mirror",
            ["diverging mirror only", "plane mirror with infinite focal length always", "lens that refracts rather than reflects"],
            "Concave mirrors converge parallel rays toward a real focal point.",
            "Students confuse concave with diverging because both terms sound similar.",
            "C1.9k", "Identifying concave mirror as converging", "Easy", 60,
        ),
        (
            "A convex rear-view vehicle mirror is a",
            "diverging mirror that produces a smaller, wider field of view",
            ["converging mirror that magnifies distant traffic", "plane mirror with no curvature", "converging lens mounted on the bumper"],
            "Convex mirrors spread reflected rays and form virtual upright reduced images.",
            "Students think convex mirrors magnify like converging lenses.",
            "C1.9k", "Identifying convex mirror as diverging", "Easy", 60,
        ),
        (
            "An object placed beyond $2f$ from a converging lens typically produces",
            "a real, inverted image between $f$ and $2f$ on the opposite side",
            ["a virtual upright image on the same side as the object", "no image because the lens cannot refract parallel rays", "a real upright image exactly at the object location"],
            "Standard ray rules place a real inverted image inside the $f$-$2f$ image region.",
            "Students predict virtual images for all converging-lens setups.",
            "C1.10k", "Predicting real image location for converging lens", "Medium", 85,
        ),
        (
            "When an object is placed inside the focal length of a converging lens, the image formed is",
            "virtual, upright, and larger than the object",
            ["real, inverted, and smaller than the object", "real and located on the same side as the object", "absent because rays never refract"],
            "Inside $f$, diverging emergent rays appear to originate from a virtual image.",
            "Students apply the beyond-$2f$ image rules to all object distances.",
            "C1.10k", "Predicting virtual magnified image inside focal length", "Medium", 90,
        ),
        (
            "A diverging lens always forms images that are",
            "virtual, upright, and smaller than the object",
            ["real, inverted, and magnified", "real and located on the opposite side", "nonexistent for any object distance"],
            "Diverging lenses spread rays so only virtual reduced images are produced.",
            "Students think diverging lenses can project real images onto a screen.",
            "C1.10k", "Describing images formed by diverging lenses", "Medium", 80,
        ),
        (
            "In a ray diagram for a converging lens, a ray parallel to the principal axis after refraction passes through",
            "the focal point on the opposite side of the lens",
            ["the centre of the lens at zero deviation only", "a point twice the focal length on the same side", "the normal to the lens surface at the vertex"],
            "Parallel-ray rule is the primary construction line for thin lenses.",
            "Students draw parallel rays continuing undeviated through the lens.",
            "C1.11k", "Applying parallel-ray rule for converging lens", "Medium", 85,
        ),
        (
            "Diffraction of light is best described as",
            "the spreading of waves when they pass through an opening or around an edge",
            ["the alignment of wave crests from two separate coherent sources", "the complete reflection of light at a boundary above the critical angle", "the conversion of photons into electrons at a metal surface"],
            "Diffraction involves bending and spreading due to aperture or obstacle size.",
            "Students label double-slit bright fringes as diffraction rather than interference.",
            "C1.11k", "Defining diffraction of electromagnetic waves", "Medium", 75,
        ),
        (
            "Interference of light occurs when",
            "two or more coherent waves overlap and combine by superposition",
            ["a single ray reflects once from a smooth mirror", "light slows down entering a denser medium", "photons eject electrons above a threshold frequency"],
            "Interference requires overlapping waves with a stable phase relationship.",
            "Students describe any bright beam as interference without superposition.",
            "C1.11k", "Defining interference by wave superposition", "Medium", 75,
        ),
        (
            "In a double-slit experiment with monochromatic light, equally spaced bright fringes on a screen indicate",
            "constructive interference at path differences equal to whole wavelengths",
            ["diffraction from a single narrow slit only", "polarization rotation in the slits", "photoelectric emission from the screen"],
            "Young's pattern is an interference signature from two coherent sources.",
            "Students attribute double-slit fringes solely to single-slit diffraction.",
            "C1.12k", "Interpreting double-slit pattern as interference", "Medium", 90,
        ),
        (
            "A single-slit diffraction pattern differs from a double-slit interference pattern because the single-slit pattern",
            "has a broad central maximum with weaker side maxima",
            ["shows no central bright region at all", "contains only equally spaced fringes of equal brightness", "requires two coherent sources separated by many metres"],
            "Single-slit diffraction envelopes produce one dominant central peak.",
            "Students expect identical fringe spacing and brightness for both arrangements.",
            "C1.12k", "Distinguishing single-slit diffraction from double-slit interference", "Hard", 100,
        ),
        (
            "Two coherent sources produce constructive interference at a point where the path difference equals",
            "an integer multiple of the wavelength",
            ["half-integer multiples of the wavelength only", "exactly one quarter wavelength always", "zero frequency difference only"],
            "Constructive condition: $\\Delta path = m\\lambda$.",
            "Students use $\\lambda/2$ for constructive instead of destructive interference.",
            "C1.12k", "Stating path-difference condition for constructive interference", "Medium", 85,
        ),
        (
            "Destructive interference between two coherent light waves occurs when the path difference is",
            "an odd integer multiple of half a wavelength",
            ["any integer multiple of one full wavelength", "zero for all points on a screen", "equal to twice the amplitude of either wave"],
            "Destructive condition: $\\Delta path = (m + \\tfrac{1}{2})\\lambda$.",
            "Students apply the constructive condition to destructive cases.",
            "C1.12k", "Stating path-difference condition for destructive interference", "Medium", 85,
        ),
        (
            "Thin-film colours on soap bubbles arise primarily because reflected waves from the top and bottom film surfaces",
            "interfere constructively or destructively depending on film thickness and wavelength",
            ["diffract around the bubble without reflection", "change polarization so no colour is visible", "increase the speed of light in air surrounding the bubble"],
            "Path differences inside thin films produce wavelength-dependent interference colours.",
            "Students attribute soap colours only to dispersion without interference.",
            "C1.12k", "Explaining thin-film interference colours", "Hard", 100,
        ),
        (
            "In a laboratory double-slit setup, increasing the slit separation while holding wavelength constant typically",
            "decreases the fringe spacing on the distant screen",
            ["increases the fringe spacing proportionally", "eliminates all dark fringes immediately", "changes the vacuum speed of the laser light"],
            "Fringe spacing is inversely related to slit separation for fixed screen distance.",
            "Students predict wider slits always mean wider fringes.",
            "C1.2s", "Predicting effect of slit separation on fringe spacing", "Hard", 105,
        ),
        (
            "The photoelectric effect demonstrates that electrons are ejected from a metal surface only when incident light",
            "has frequency above a material-specific threshold",
            ["has arbitrarily low frequency if intensity is very high", "is polarized parallel to the surface always", "travels slower than sound in the metal"],
            "Below threshold frequency, no photoelectrons are emitted regardless of intensity.",
            "Students believe bright low-frequency light will eventually eject electrons.",
            "C2.1k", "Stating threshold frequency in photoelectric effect", "Easy", 65,
        ),
        (
            "In the photoelectric effect, increasing the intensity of light above the threshold frequency while keeping frequency fixed",
            "increases the number of photoelectrons emitted per second",
            ["increases the maximum kinetic energy of each photoelectron", "lowers the work function of the metal", "decreases the stopping potential required"],
            "Higher intensity means more photons per second, not higher photon energy.",
            "Students think brighter light increases each electron's maximum kinetic energy.",
            "C2.1k", "Distinguishing intensity effect on photoelectron count", "Medium", 80,
        ),
        (
            "Increasing the frequency of incident light above the threshold in a photoelectric experiment increases",
            "the maximum kinetic energy of emitted photoelectrons",
            ["only the number of electrons with zero kinetic energy", "the work function of the metal surface", "the wavelength of the metal's lattice spacing"],
            "Higher $f$ means higher photon energy, raising $E_{k,\\max}$ via $hf = W + E_{k,\\max}$.",
            "Students expect intensity, not frequency, to control maximum kinetic energy.",
            "C2.2k", "Relating photon frequency to maximum photoelectron energy", "Medium", 85,
        ),
        (
            "The work function of a metal is defined as",
            "the minimum energy required to remove an electron from the metal surface",
            ["the kinetic energy of the fastest photoelectron always", "the intensity of light needed to begin emission", "the momentum of an incident photon divided by wavelength"],
            "$W$ is the binding energy threshold appearing in Einstein's photoelectric equation.",
            "Students confuse work function with measured stopping potential directly.",
            "C2.2k", "Defining work function in photoelectric context", "Easy", 65,
        ),
        (
            "Einstein's photoelectric equation $E_{k,\\max} = hf - W$ shows that a graph of $E_{k,\\max}$ versus frequency has slope equal to",
            "Planck's constant $h$",
            ["the work function $W$", "the speed of light $c$", "the electron charge $e$"],
            "Linear form $y = hx - W$ identifies $h$ as slope.",
            "Students interpret the intercept as slope or vice versa.",
            "C2.2k", "Interpreting slope of photoelectric graph as Planck constant", "Medium", 90,
        ),
        (
            "A solar cell converts sunlight to electrical energy using the photoelectric effect because photons with sufficient energy",
            "transfer energy to electrons that then move through an external circuit",
            ["increase the metal's work function continuously during the day", "eliminate the need for any electric field in the device", "reduce the frequency of incoming radiation inside the cell"],
            "Photon absorption liberates charge carriers that a built-in field drives through a circuit.",
            "Students think solar cells store photons mechanically without electron transfer.",
            "C2.1sts", "Explaining solar cell operation with photoelectric model", "Medium", 85,
        ),
        (
            "The energy of a single photon is calculated using",
            "$E = hf$",
            ["$E = h/f$", "$E = f/c$", "$E = \\lambda c$ without Planck's constant"],
            "Photon energy is proportional to frequency through Planck's constant.",
            "Students invert the relationship and divide by frequency.",
            "C2.3k", "Stating photon energy formula", "Easy", 55,
        ),
        (
            "A photon of blue light has higher energy than a photon of red light of the same intensity because blue light",
            "has higher frequency and shorter wavelength",
            ["travels faster in vacuum", "has lower frequency and longer wavelength", "consists of larger amplitude waves only with no frequency change"],
            "At fixed intensity, individual blue photons carry more energy due to higher $f$.",
            "Students think colour energy depends only on brightness, not frequency.",
            "C2.3k", "Comparing photon energies for different visible colours", "Easy", 60,
        ),
        (
            "The momentum of a photon is given by",
            "$p = h/\\lambda$",
            ["$p = h\\lambda$", "$p = mc^2$ for a photon with nonzero rest mass", "$p = f/c^2$"],
            "Massless photons carry momentum inversely proportional to wavelength.",
            "Students multiply $h$ and $\\lambda$ instead of dividing.",
            "C2.4k", "Stating photon momentum relation", "Medium", 75,
        ),
        (
            "In Compton scattering, an X-ray photon colliding with a nearly free electron emerges with",
            "longer wavelength and lower energy than before the collision",
            ["shorter wavelength because it gains speed in the electron", "unchanged wavelength because photons cannot interact with matter", "higher frequency after transferring energy to the electron"],
            "The photon transfers energy and momentum to the electron, reducing its own energy.",
            "Students predict the photon gains energy during the collision.",
            "C2.5k", "Describing wavelength change in Compton scattering", "Medium", 90,
        ),
        (
            "Compton's experiments supported the particle model of light because the observed wavelength shift depended on",
            "scattering angle and matched predictions using photon momentum transfer",
            ["only the intensity of the incident beam", "the polarization direction alone with no angle dependence", "classical wave interference alone without electron recoil"],
            "The angle-dependent shift confirmed discrete photon momentum exchange.",
            "Students think Compton shift arises from simple mirror reflection.",
            "C2.5k", "Linking Compton shift to photon momentum model", "Hard", 100,
        ),
        (
            "Evidence that light behaves as a wave includes",
            "interference and diffraction patterns produced without matter exchange",
            ["photoelectron emission proportional to intensity above threshold", "wavelength increase after collision with a free electron", "discrete photon energy proportional to frequency"],
            "Wave behaviour is shown by superposition phenomena such as Young's fringes.",
            "Students list photoelectric or Compton results as wave evidence.",
            "C2.6k", "Identifying wave evidence for electromagnetic radiation", "Medium", 80,
        ),
        (
            "Evidence that light behaves as a particle includes",
            "the photoelectric effect and Compton scattering",
            ["constructive interference in a double-slit experiment", "polarization by a single filter", "refraction at an air-glass boundary"],
            "Particle-like behaviour appears when energy and momentum transfer occur in quanta.",
            "Students cite refraction or interference as proof of particle behaviour.",
            "C2.6k", "Identifying particle evidence for electromagnetic radiation", "Medium", 80,
        ),
        (
            "A student claims that because light shows interference, it cannot show photoelectric behaviour. The best evaluation is that",
            "light exhibits both wave and particle models depending on the experiment",
            ["the wave model alone explains all optical phenomena completely", "the particle model alone replaces Maxwell's equations in every case", "interference disproves the existence of photons entirely"],
            "Wave-particle complementarity means models are selected by experimental context.",
            "Students treat wave and particle descriptions as mutually exclusive always.",
            "C2.1sts", "Evaluating wave-particle complementarity for light", "Medium", 85,
        ),
        (
            "A photoelectric experiment measures stopping potential increasing linearly with frequency above threshold because stopping potential is directly related to",
            "the maximum kinetic energy of the fastest emitted electrons",
            ["the number of photons striking the surface per second only", "the work function, which changes with each frequency", "the wavelength of the metal lattice"],
            "Higher $E_{k,\\max}$ requires greater retarding potential to stop the fastest electrons.",
            "Students think stopping potential measures photocurrent count, not maximum energy.",
            "C2.2s", "Relating stopping potential to maximum photoelectron energy", "Hard", 105,
        ),
        (
            "Safety goggles for certain lasers are rated by wavelength because photon energy",
            "depends on frequency, and frequency is inversely related to wavelength",
            ["is independent of wavelength for all lasers", "decreases when wavelength becomes shorter", "depends only on beam diameter, not colour"],
            "Shorter-wavelength lasers deliver higher-energy photons requiring different shielding.",
            "Students think all visible lasers have identical photon energy.",
            "C2.2sts", "Justifying laser eye protection by photon energy", "Medium", 85,
        ),
        (
            "In analyzing a ray diagram lab report, a controlled variable when comparing image distances for different object distances should be",
            "the focal length of the lens used",
            ["the screen colour chosen in the room", "the student's height at the optics bench", "the number of windows in the laboratory"],
            "Fair comparison of object and image distances requires a fixed lens focal length.",
            "Students list manipulated and responding variables but omit controlled ones.",
            "C1.1s", "Identifying controlled variable in lens image-distance lab", "Medium", 80,
        ),
        (
            "A data table lists angles of incidence and refraction for glass. The best derived quantity to plot for verifying Snell's law is",
            "$\\sin\\theta_i$ versus $\\sin\\theta_r$",
            ["incident angle versus reflected angle only", "wavelength versus amplitude", "time of day versus brightness"],
            "Snell's law is linear when sines of angles are compared.",
            "Students plot raw angles without sine conversion.",
            "C1.3s", "Selecting graph variables to verify Snell's law", "Medium", 85,
        ),
        (
            "To reduce systematic error when measuring the focal length of a converging lens with the thin-lens equation, a student should",
            "repeat trials and average image and object distance measurements",
            ["use only one trial at a single object distance", "measure object distance from the screen instead of the lens", "ignore parallax when reading the metre stick"],
            "Averaging multiple object-image pairs reduces random measurement error.",
            "Students take a single measurement and treat it as exact.",
            "C1.4s", "Reducing systematic error in focal length measurement", "Medium", 90,
        ),
    ])

    q.append(nr(
        "Monochromatic light in vacuum has frequency $5.0 \\times 10^{14}\\ \\text{Hz}$. "
        "What is its wavelength in nanometres? Use $c = 3.00 \\times 10^8\\ \\text{m/s}$. "
        "Record as a whole number.",
        "600",
        "$\\lambda = c/f = (3.00 \\times 10^8)/(5.0 \\times 10^{14}) = 6.00 \\times 10^{-7}\\ \\text{m} = 600\\ \\text{nm}$.",
        "Students divide frequency by speed or forget to convert metres to nanometres.",
        topic=TOPIC, outcome_code="C1.2k",
        skill_tested="Calculating wavelength from frequency using c = fλ",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    q.append(nr(
        "A photon has wavelength $500\\ \\text{nm}$ in vacuum. "
        "What is its energy in units of $10^{-19}\\ \\text{J}$? Use $h = 6.63 \\times 10^{-34}\\ \\text{J·s}$ "
        "and $c = 3.00 \\times 10^8\\ \\text{m/s}$. Record to one decimal place.",
        "4.0",
        "$E = hc/\\lambda = (6.63 \\times 10^{-34})(3.00 \\times 10^8)/(500 \\times 10^{-9}) "
        "= 3.98 \\times 10^{-19}\\ \\text{J} \\approx 4.0 \\times 10^{-19}\\ \\text{J}$.",
        "Students multiply by wavelength instead of dividing or omit the nanometre conversion.",
        topic=TOPIC, outcome_code="C2.3k",
        skill_tested="Computing photon energy from wavelength",
        difficulty="Medium", estimated_time_seconds=100,
    ))

    q.append(nr(
        "Light travels from air into glass with index of refraction $n = 1.50$. "
        "What is the speed of light in the glass in units of $10^8\\ \\text{m/s}$? "
        "Use $c = 3.00 \\times 10^8\\ \\text{m/s}$. Record to one decimal place.",
        "2.0",
        "$v = c/n = (3.00 \\times 10^8)/1.50 = 2.0 \\times 10^8\\ \\text{m/s}$.",
        "Students multiply by $n$ instead of dividing, obtaining $4.5 \\times 10^8\\ \\text{m/s}$.",
        topic=TOPIC, outcome_code="C1.6k",
        skill_tested="Calculating light speed in a medium from index of refraction",
        difficulty="Easy", estimated_time_seconds=70,
    ))

    q.append(nr(
        "In a photoelectric experiment, incident light of frequency $7.0 \\times 10^{14}\\ \\text{Hz}$ "
        "ejects electrons from a metal with work function $2.5 \\times 10^{-19}\\ \\text{J}$. "
        "What is the maximum kinetic energy of the photoelectrons in units of $10^{-19}\\ \\text{J}$? "
        "Use $h = 6.63 \\times 10^{-34}\\ \\text{J·s}$. Record to one decimal place.",
        "2.1",
        "$E_{k,\\max} = hf - W = (6.63 \\times 10^{-34})(7.0 \\times 10^{14}) - 2.5 \\times 10^{-19} "
        "= 4.64 \\times 10^{-19} - 2.5 \\times 10^{-19} = 2.1 \\times 10^{-19}\\ \\text{J}$.",
        "Students add the work function instead of subtracting it from photon energy.",
        topic=TOPIC, outcome_code="C2.2k",
        skill_tested="Applying Einstein photoelectric equation for maximum kinetic energy",
        difficulty="Hard", estimated_time_seconds=110,
    ))

    return q
