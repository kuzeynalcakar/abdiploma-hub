"""Unit D: Atomic Physics — original Physics 30 questions."""

from .helpers import mc, nr

TOPIC = "Atomic Physics"


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
            "Thomson's plum-pudding model pictured the atom as",
            "a sphere of positive charge with embedded electrons",
            ["a tiny dense nucleus orbited by electrons", "a solid indivisible sphere with no internal structure", "a nucleus containing only neutrons"],
            "Thomson proposed uniform positive matter with electrons scattered throughout.",
            "Students confuse Thomson's model with Rutherford's planetary nuclear model.",
            "D1.1k", "Describing Thomson's plum-pudding atomic model", "Easy", 55,
        ),
        (
            "Rutherford's alpha-particle scattering experiment showed that most of the atom's volume is",
            "empty space",
            ["filled uniformly with positive charge", "occupied entirely by electrons only", "composed of equal numbers of protons and neutrons throughout"],
            "Most alphas passed undeflected; rare large-angle scattering implied a small, dense nucleus.",
            "Students think most alphas bounced back rather than passing through.",
            "D1.1k", "Interpreting Rutherford scattering evidence for empty space", "Easy", 60,
        ),
        (
            "The observation that a few alpha particles rebounded at large angles in Rutherford's experiment led to the conclusion that the nucleus is",
            "small, massive, and positively charged",
            ["large and spread evenly through the atom", "negatively charged and located at the edge", "identical in size to the whole atom"],
            "Large-angle deflection requires a concentrated positive core exerting strong repulsion.",
            "Students assume large deflections mean the nucleus is large rather than small and dense.",
            "D1.1k", "Inferring nuclear properties from large-angle alpha scattering", "Medium", 75,
        ),
        (
            "In the Bohr model, electrons occupy",
            "specific allowed orbits with fixed energy values",
            ["any orbit whose radius fits the nuclear size", "only the region inside the nucleus", "orbits that continuously radiate while remaining stable"],
            "Bohr quantized electron energies to explain discrete spectral lines.",
            "Students believe Bohr allowed continuous energy orbits like classical planets.",
            "D1.2k", "Stating Bohr's quantized electron energy levels", "Easy", 60,
        ),
        (
            "An electron transition from a higher energy level to a lower one in an atom results in",
            "emission of a photon with energy equal to the level difference",
            ["absorption of a photon with random energy", "no change in electromagnetic radiation", "emission of an alpha particle from the nucleus"],
            "The lost atomic energy appears as a photon: $\\Delta E = hf$.",
            "Students confuse emission (downward transition) with absorption (upward transition).",
            "D1.2k", "Relating downward electron transitions to photon emission", "Medium", 75,
        ),
        (
            "Ionization of a hydrogen atom in the ground state requires energy at least equal to",
            "13.6 eV",
            ["1.51 eV", "3.40 eV", "0.85 eV"],
            "Binding energy of the ground-state electron is 13.6 eV.",
            "Students use the energy of a visible Balmer transition instead of the ionization energy.",
            "D1.2k", "Recalling hydrogen ground-state ionization energy", "Medium", 80,
        ),
        (
            "A bright-line emission spectrum is produced when",
            "excited atoms emit photons at specific wavelengths as electrons drop to lower levels",
            ["white light passes through cool gas without interaction", "electrons are removed from nuclei in a particle accelerator", "all wavelengths of light are absorbed equally"],
            "Downward transitions produce discrete bright lines characteristic of each element.",
            "Students confuse emission spectra with continuous blackbody spectra.",
            "D1.3k", "Explaining origin of emission line spectra", "Medium", 75,
        ),
        (
            "Dark absorption lines in a stellar spectrum indicate that",
            "specific wavelengths were removed as light passed through cooler gas",
            ["the star emits only ultraviolet radiation", "electrons in the star's core undergo nuclear fusion", "the star contains no hydrogen whatsoever"],
            "Cooler outer gas absorbs photons matching its transition energies.",
            "Students think absorption lines mean those wavelengths were added by the gas.",
            "D1.3k", "Interpreting absorption lines in stellar spectra", "Medium", 80,
        ),
        (
            "The Balmer series of hydrogen appears in the visible region because those transitions end at",
            "the $n = 2$ energy level",
            ["the ground state $n = 1$ only", "the $n = 3$ level exclusively", "levels above the ionization limit only"],
            "Balmer lines involve upper levels dropping to $n = 2$.",
            "Students associate all hydrogen visible lines with transitions to the ground state.",
            "D1.3k", "Identifying the lower level of the Balmer series", "Medium", 85,
        ),
        (
            "Protons and neutrons are classified as hadrons because they",
            "experience the strong nuclear force and are composed of quarks",
            ["carry no mass and travel at the speed of light", "are fundamental leptons with no internal structure", "interact only through gravity and electromagnetism"],
            "Hadrons are quark composites bound by the strong force.",
            "Students label protons as leptons or as fundamental point particles with no quark structure.",
            "D1.4k", "Classifying protons and neutrons as hadrons", "Medium", 80,
        ),
        (
            "A proton is composed of",
            "two up quarks and one down quark",
            ["one up quark and two down quarks", "three down quarks only", "an electron and two neutrons"],
            "Proton quark content is $uud$.",
            "Students swap the up/down counts or confuse proton and neutron quark compositions.",
            "D1.4k", "Stating quark composition of a proton", "Easy", 60,
        ),
        (
            "A neutron is composed of",
            "one up quark and two down quarks",
            ["two up quarks and one down quark", "three up quarks only", "two protons and one electron"],
            "Neutron quark content is $udd$.",
            "Students reverse the proton and neutron quark combinations.",
            "D1.4k", "Stating quark composition of a neutron", "Easy", 60,
        ),
        (
            "Quarks carry fractional electric charges. The charge of an up quark is",
            "$+\\frac{2}{3}\\,e$",
            ["$-\\frac{1}{3}\\,e$", "$+1\\,e$", "$-\\frac{2}{3}\\,e$"],
            "Up quarks carry $+2e/3$; down quarks carry $-e/3$.",
            "Students assign integer charge units to individual quarks.",
            "D1.4k", "Recalling up-quark electric charge", "Medium", 70,
        ),
        (
            "Rutherford's experiment provided evidence against Thomson's model primarily because",
            "large-angle alpha scattering could not occur with a diffuse positive sphere",
            ["Thomson predicted no deflection at any angle", "alpha particles have no charge", "electrons in Thomson's model repel alpha particles strongly"],
            "A uniform positive charge cannot produce the observed concentrated repulsive force.",
            "Students think Thomson's model predicted the same scattering pattern as Rutherford observed.",
            "D1.1sts", "Evaluating how scattering data refuted plum-pudding model", "Medium", 85,
        ),
        (
            "Spectroscopy is used in astronomy to determine a star's chemical composition because",
            "each element's line pattern acts as a fingerprint in the star's spectrum",
            ["stars emit only one wavelength of light", "composition can be read directly from the star's brightness", "all elements absorb identical wavelengths of light"],
            "Matching observed lines to known transition patterns identifies elements present.",
            "Students think a star's colour alone reveals its complete elemental makeup.",
            "D1.1sts", "Applying spectroscopy to identify stellar composition", "Medium", 80,
        ),
        (
            "When drawing a simple energy-level diagram for hydrogen, the spacing between higher levels should",
            "decrease, showing levels converging toward the ionization limit",
            ["increase equally between every pair of levels", "remain identical to the ground-state spacing throughout", "be random with no relation to quantum theory"],
            "Bohr energies scale as $1/n^2$, so higher levels crowd closer together.",
            "Students draw equally spaced levels for all $n$ values.",
            "D1.2s", "Sketching accurate relative spacing of hydrogen levels", "Hard", 95,
        ),
        (
            "Alpha radiation consists of",
            "helium nuclei ($^4_2\\text{He}$)",
            ["high-speed electrons", "electromagnetic photons with no rest mass", "hydrogen nuclei ($^1_1\\text{H}$)"],
            "Alpha particles are two protons and two neutrons — helium-4 nuclei.",
            "Students confuse alpha particles with beta electrons or gamma photons.",
            "D2.1k", "Identifying the composition of alpha radiation", "Easy", 55,
        ),
        (
            "Beta-minus ($\\beta^-$) decay involves the nucleus emitting",
            "an electron and an antineutrino as a neutron converts to a proton",
            ["a helium nucleus and gamma radiation only", "a positron with no neutrino", "only a high-energy photon"],
            "In $\\beta^-$ decay: $n \\rightarrow p + e^- + \\bar{\\nu}_e$.",
            "Students think beta decay ejects a proton or an alpha particle from the nucleus.",
            "D2.1k", "Describing beta-minus decay products", "Medium", 75,
        ),
        (
            "Gamma ($\\gamma$) radiation differs from alpha and beta radiation because it",
            "is electromagnetic radiation with no change in atomic or mass number",
            ["carries a charge of $+2\\,e$", "always increases the mass number by four", "consists of particles with measurable rest mass"],
            "Gamma emission releases energy without changing $Z$ or $A$.",
            "Students think gamma rays change the element's identity like alpha decay does.",
            "D2.1k", "Distinguishing gamma radiation from particulate decay", "Easy", 60,
        ),
        (
            "Which type of nuclear radiation is most easily stopped by a sheet of paper?",
            "alpha",
            ["beta", "gamma", "neutron"],
            "Alpha particles have low penetration due to large mass and $+2$ charge.",
            "Students select gamma because it seems the least dangerous in daily language.",
            "D2.1k", "Comparing penetration of alpha, beta, and gamma radiation", "Easy", 55,
        ),
        (
            "In the balanced nuclear equation $^{238}_{92}\\text{U} \\rightarrow \\,^{234}_{90}\\text{Th} + \\,^{4}_{2}\\text{He}$, the decay mode is",
            "alpha decay",
            ["beta-minus decay", "gamma emission only", "positron emission"],
            "Mass number drops by 4 and atomic number by 2 — characteristic of alpha emission.",
            "Students focus on the thorium product and ignore the helium nucleus released.",
            "D2.2k", "Identifying alpha decay from a balanced nuclear equation", "Easy", 65,
        ),
        (
            "During beta-minus decay of $^{14}_{6}\\text{C}$, the daughter nucleus is",
            "$^{14}_{7}\\text{N}$",
            ["$^{14}_{5}\\text{B}$", "$^{10}_{6}\\text{C}$", "$^{18}_{6}\\text{C}$"],
            "Atomic number increases by 1 while mass number stays constant: $^{14}_{6}\\text{C} \\rightarrow \\,^{14}_{7}\\text{N} + e^- + \\bar{\\nu}$.",
            "Students decrease $Z$ instead of increasing it in beta-minus decay.",
            "D2.2k", "Determining daughter nucleus in beta-minus decay", "Medium", 80,
        ),
        (
            "When balancing a nuclear decay equation, the sum of mass numbers and the sum of atomic numbers must",
            "each remain the same on both sides of the equation",
            ["increase by one on the product side only", "be ignored for gamma emission processes", "equal zero on both sides"],
            "Conservation of nucleon number and charge governs all nuclear equations.",
            "Students balance charge but forget to conserve mass number.",
            "D2.2k", "Applying conservation laws to nuclear decay equations", "Medium", 75,
        ),
        (
            "A sample has a half-life of 6.0 hours. After 12 hours, the fraction of the original radioactive nuclei remaining is",
            "$\\frac{1}{4}$",
            ["$\\frac{1}{2}$", "$\\frac{1}{3}$", "$\\frac{1}{8}$"],
            "Two half-lives elapsed: $(1/2)^2 = 1/4$ remains.",
            "Students use one half-life of decay ($1/2$) instead of two.",
            "D2.3k", "Calculating remaining fraction after multiple half-lives", "Medium", 85,
        ),
        (
            "Carbon-14 dating is useful for estimating ages of organic materials up to roughly",
            "50 000 years",
            ["4.5 billion years", "500 years only", "10 million years"],
            "After about ten half-lives ($5730\\ \\text{y}$ each), $^{14}\\text{C}$ activity becomes too low to measure reliably.",
            "Students confuse carbon-14 dating range with uranium-lead geological dating.",
            "D2.3k", "Stating practical limits of carbon-14 dating", "Medium", 80,
        ),
        (
            "Nuclear fission is characterized by",
            "a heavy nucleus splitting into lighter nuclei with neutron release",
            ["light nuclei combining to form a heavier nucleus", "emission of only gamma radiation with no particle change", "complete conversion of mass to neutrinos only"],
            "Fission splits $A > 200$ nuclei, often triggered by neutron absorption.",
            "Students confuse fission (splitting) with fusion (combining).",
            "D2.4k", "Defining nuclear fission", "Easy", 55,
        ),
        (
            "Compared with fission, energy release per nucleon in fusion of light elements is generally",
            "greater for fusion of very light nuclei such as hydrogen isotopes",
            ["zero for all fusion reactions", "always less than chemical bond energy only", "identical for fission and fusion of all nuclei"],
            "Fusion of light elements up to iron releases more energy per nucleon than fission of heavy nuclei.",
            "Students think fission always releases more energy per nucleon than any fusion reaction.",
            "D2.6k", "Comparing energy per nucleon for fission and fusion", "Hard", 100,
        ),
        (
            "A chain reaction in a nuclear reactor is controlled primarily by",
            "absorbing excess neutrons with control rods",
            ["removing all fuel rods simultaneously", "increasing the number of emitted gamma rays", "cooling the reactor until fusion begins"],
            "Control rods regulate neutron population to maintain steady fission rate.",
            "Students think water cooling alone stops the chain reaction without neutron absorption.",
            "D2.7k", "Explaining control-rod function in fission reactors", "Medium", 80,
        ),
        (
            "Medical tracers use radioactive isotopes with short half-lives primarily so that",
            "patient exposure to radiation is minimized after the diagnostic procedure",
            ["the isotope remains in the body permanently for monitoring", "half-life has no effect on radiation dose received", "longer half-life always produces clearer images"],
            "Short half-life limits total decays and dose while still allowing detection.",
            "Students think longer half-life is always better for medical imaging.",
            "D2.1sts", "Justifying short half-life for medical radioisotopes", "Medium", 85,
        ),
        (
            "Mass defect of a nucleus refers to",
            "the difference between the sum of separate nucleon masses and the measured nuclear mass",
            ["the loss of electrons during ionization", "the increase in mass when a nucleus absorbs a photon", "the mass of neutrinos emitted in every decay"],
            "Binding energy accounts for the missing mass: $m_{\\text{defect}} = \\sum m_{\\text{parts}} - m_{\\text{nucleus}}$.",
            "Students think mass defect means the nucleus weighs more than its separated parts.",
            "D3.2k", "Defining nuclear mass defect", "Medium", 75,
        ),
        (
            "The binding energy per nucleon reaches a broad maximum near",
            "iron ($^{56}\\text{Fe}$)",
            ["hydrogen ($^{1}\\text{H}$)", "uranium ($^{238}\\text{U}$)", "helium ($^{4}\\text{He}$) exclusively"],
            "Iron-56 has among the highest binding energy per nucleon, marking peak nuclear stability.",
            "Students select uranium because it is used in reactors, not because it has maximum binding per nucleon.",
            "D3.3k", "Identifying nuclei with maximum binding energy per nucleon", "Medium", 85,
        ),
        (
            "If the mass defect of a nucleus is $\\Delta m$, the binding energy is calculated using",
            "$E_b = \\Delta m \\, c^2$",
            ["$E_b = \\Delta m \\, c$", "$E_b = \\frac{1}{2}\\Delta m \\, v^2$", "$E_b = \\Delta m / c^2$"],
            "Binding energy equals mass defect times the square of the speed of light.",
            "Students omit the $c^2$ factor or use classical kinetic energy formulas.",
            "D3.4k", "Calculating binding energy from mass defect", "Medium", 80,
        ),
        (
            "Energy is released in nuclear fission of heavy nuclei because",
            "the total binding energy of the products exceeds that of the original nucleus",
            ["mass is created from nothing during the reaction", "the number of protons increases without energy change", "binding energy per nucleon decreases for all product nuclei"],
            "Products closer to the iron peak are more tightly bound per nucleon.",
            "Students think energy release violates conservation of mass-energy rather than converting mass.",
            "D3.5k", "Explaining fission energy release via binding energy", "Hard", 95,
        ),
        (
            "Nuclear fusion in the Sun primarily converts",
            "hydrogen into helium",
            ["uranium into lead", "iron into heavier transuranic elements", "electrons into protons directly"],
            "Stellar fusion builds helium from hydrogen isotopes in the proton-proton chain.",
            "Students think stars fuse heavy elements like uranium throughout their main-sequence life.",
            "D3.6k", "Identifying primary fusion product in main-sequence stars", "Easy", 60,
        ),
        (
            "A photon emitted when an electron drops between hydrogen levels has energy determined by",
            "the difference in energy between the initial and final levels",
            ["the average of all level energies only", "the speed of the electron in the lower orbit only", "twice the ground-state binding energy always"],
            "Transition energy $\\Delta E = E_i - E_f = hf$.",
            "Students use the final level energy alone instead of the level difference.",
            "D3.1s", "Relating spectral photon energy to level difference", "Medium", 85,
        ),
        (
            "In a cloud chamber, a particle track that is thick, straight, and short most likely belongs to",
            "an alpha particle",
            ["a gamma ray", "a neutrino", "a high-energy photon with no ionization"],
            "Alpha particles ionize strongly, producing dense, straight, limited-range tracks.",
            "Students select beta because it is faster, ignoring the track density clue.",
            "D4.2k", "Identifying alpha particles from cloud chamber track appearance", "Medium", 85,
        ),
        (
            "A thin, wavy cloud chamber track that extends across much of the chamber is characteristic of",
            "a beta particle",
            ["an alpha particle", "uncharged gamma radiation", "a stationary neutron"],
            "Beta electrons have smaller mass and charge, ionize weakly, and scatter easily.",
            "Students expect all nuclear radiation to produce identical tracks.",
            "D4.2k", "Identifying beta particles from cloud chamber track appearance", "Medium", 85,
        ),
        (
            "Quark confinement means that",
            "individual quarks cannot be isolated; they are observed only within hadrons",
            ["quarks are visible as free particles in cloud chambers", "quarks have no role in nuclear binding", "only electrons are confined inside the nucleus"],
            "The strong force increases with separation, preventing free quark observation.",
            "Students think quarks can be knocked out and detected alone like electrons.",
            "D4.3k", "Explaining quark confinement in hadrons", "Hard", 100,
        ),
        (
            "Particle accelerators such as cyclotrons are used to",
            "accelerate charged particles to high energy for research and medical treatments",
            ["produce chemical reactions by heating samples in a furnace", "generate only visible light with no particle beams", "eliminate all radioactivity from isotope samples"],
            "Magnetic and electric fields in cyclotrons boost ion energy for collision studies and proton therapy.",
            "Students think accelerators only produce electromagnetic waves like radio transmitters.",
            "D4.1k", "Describing purpose of particle accelerators", "Easy", 60,
        ),
        (
            "The Large Hadron Collider primarily investigates",
            "fundamental particles and forces at very high collision energies",
            ["daily weather patterns in the upper atmosphere", "chemical rates of organic combustion only", "planetary orbital mechanics in the solar system"],
            "High-energy proton collisions probe the Standard Model and new physics.",
            "Students confuse high-energy particle physics with astronomical observation.",
            "D4.1sts", "Stating scientific purpose of the Large Hadron Collider", "Medium", 75,
        ),
        (
            "Pair production in a detector requires",
            "sufficient photon energy near matter to create a particle-antiparticle pair",
            ["only visible light with no minimum energy threshold", "alpha decay inside the detector gas exclusively", "chemical ionization of water molecules alone"],
            "A photon with $E \\geq 2m_ec^2$ near a nucleus can create $e^-e^+$ pair.",
            "Students think any photon regardless of energy can create matter-antimatter pairs.",
            "D4.4k", "Describing energy requirement for electron-positron pair production", "Hard", 105,
        ),
        (
            "Antimatter particles such as positrons",
            "annihilate with corresponding matter particles, converting mass to photon energy",
            ["combine with protons to form stable new elements in all cases", "have the same charge as their matter counterparts", "cannot be detected in any laboratory setting"],
            "Electron-positron annihilation produces gamma photons totaling $2m_ec^2$.",
            "Students think positrons are identical to electrons in charge and behavior.",
            "D4.5k", "Describing matter-antimatter annihilation", "Medium", 80,
        ),
        (
            "When analyzing a nuclear decay series diagram, a step that decreases mass number by 4 and atomic number by 2 represents",
            "alpha emission",
            ["beta-minus emission", "gamma emission only", "electron capture with no mass change"],
            "Alpha decay reduces $A$ by 4 and $Z$ by 2 on each step.",
            "Students misread the diagram and assign beta decay to alpha steps.",
            "D2.2s", "Interpreting alpha steps on a decay series diagram", "Medium", 90,
        ),
        (
            "A Geiger counter clicks more frequently near a alpha source at 2 cm than at 20 cm primarily because",
            "alpha particles ionize strongly but have very limited range in air",
            ["alpha intensity increases with distance from the source", "gamma radiation dominates at short distance", "alpha particles speed up as they travel farther from the source"],
            "Inverse-square law reduces count rate, and alphas cannot reach 20 cm in air.",
            "Students think alpha penetration increases with distance from the source.",
            "D2.1s", "Interpreting distance dependence of alpha count rate", "Medium", 85,
        ),
        (
            "The Standard Model organizes fundamental particles into",
            "quarks, leptons, and force-carrying bosons",
            ["only protons, neutrons, and electrons with no substructure", "planets, stars, and galaxies by mass", "alpha, beta, and gamma radiation exclusively"],
            "The Standard Model classifies matter fermions and interaction bosons.",
            "Students list only the three historical radiations instead of fundamental particle classes.",
            "D4.3sts", "Summarizing Standard Model particle categories", "Medium", 80,
        ),
    ])

    q.append(nr(
        "A radioactive isotope has a half-life of 8.0 days. A lab sample initially contains "
        "$640\\ \\text{mg}$ of the isotope. What mass in milligrams remains after 24 days? "
        "Record as a whole number.",
        "80",
        "Three half-lives elapsed: $640 \\times (1/2)^3 = 640/8 = 80\\ \\text{mg}$.",
        "Students divide by 3 instead of applying exponential half-life decay.",
        topic=TOPIC, outcome_code="D2.3k",
        skill_tested="Calculating remaining mass after multiple half-lives",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    q.append(nr(
        "A hydrogen atom emits a photon when an electron drops from the $n=3$ level to the $n=2$ level. "
        "Using $E_n = -13.6/n^2\\ \\text{eV}$, what is the photon energy in electron volts? "
        "Record to one decimal place.",
        "1.9",
        "$\\Delta E = 13.6/4 - 13.6/9 = 3.40 - 1.51 = 1.89 \\approx 1.9\\ \\text{eV}$.",
        "Students subtract level numbers instead of calculating $1/n^2$ energies.",
        topic=TOPIC, outcome_code="D1.2k",
        skill_tested="Computing photon energy from hydrogen level transition",
        difficulty="Hard", estimated_time_seconds=110,
    ))

    q.append(nr(
        "A nucleus has a mass defect of $0.025\\ \\text{u}$. Using $1\\ \\text{u} = 931\\ \\text{MeV}$, "
        "what is the binding energy in MeV? Record to the nearest whole number.",
        "23",
        "$E_b = 0.025 \\times 931 = 23.275 \\approx 23\\ \\text{MeV}$.",
        "Students divide by 931 instead of multiplying, or omit unit conversion.",
        topic=TOPIC, outcome_code="D3.4k",
        skill_tested="Converting mass defect to binding energy in MeV",
        difficulty="Medium", estimated_time_seconds=95,
    ))

    q.append(nr(
        "An sample shows $12.5\\%$ of its original radioactivity after some time. "
        "How many half-lives have elapsed? Record as a whole number.",
        "3",
        "$12.5\\% = 1/8 = (1/2)^3$, so three half-lives have passed.",
        "Students calculate $100/12.5 = 8$ and report 8 instead of finding the exponent.",
        topic=TOPIC, outcome_code="D2.3k",
        skill_tested="Determining number of half-lives from remaining activity fraction",
        difficulty="Medium", estimated_time_seconds=85,
    ))

    q.append(nr(
        "The rest mass of a proton is $1.0073\\ \\text{u}$ and of a neutron is $1.0087\\ \\text{u}$. "
        "The measured mass of a $^4_2\\text{He}$ nucleus is $4.0015\\ \\text{u}$. "
        "What is the mass defect in unified atomic mass units? Record to four decimal places.",
        "0.0305",
        "$\\Delta m = 2(1.0073) + 2(1.0087) - 4.0015 = 4.0320 - 4.0015 = 0.0305\\ \\text{u}$.",
        "Students forget to multiply by two for each nucleon or subtract in the wrong order.",
        topic=TOPIC, outcome_code="D3.2k",
        skill_tested="Calculating mass defect from separate nucleon masses",
        difficulty="Hard", estimated_time_seconds=105,
    ))

    return q
