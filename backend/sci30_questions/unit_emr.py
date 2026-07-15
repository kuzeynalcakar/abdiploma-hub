"""Electromagnetic Spectrum — Science 30 original questions."""

from .helpers import mc, nr

TOPIC = "Electromagnetic Spectrum"


def _base_mc():
    return [
        mc(
            "Electromagnetic radiation consists of oscillating electric and magnetic fields that",
            "propagate through space at the speed of light in a vacuum",
            ["require a medium like air to travel at all", "travel slower than sound in all materials", "consist only of stationary electric charges"],
            "EMR is self-propagating transverse waves travelling at c ≈ 3.00 × 10⁸ m/s in vacuum.",
            "EMR does not need a medium; it is not static charge.",
            topic=TOPIC, outcome_code="C2.1k",
            skill_tested="Describing EMR propagation characteristics",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Compared to visible light, gamma rays have",
            "higher frequency and higher energy per photon",
            ["lower frequency and lower energy", "the same wavelength in all media", "no ability to ionize matter"],
            "Higher frequency EMR (gamma) carries more energy per photon than visible light.",
            "Frequency and energy increase toward gamma end of spectrum.",
            topic=TOPIC, outcome_code="C2.2k",
            skill_tested="Comparing frequency and energy across EMR regions",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "The ozone layer in the stratosphere absorbs much of the Sun's",
            "ultraviolet radiation",
            ["radio waves only", "visible green light exclusively", "all infrared radiation without exception"],
            "O₃ absorbs harmful UV-B and UV-C, protecting surface life.",
            "Ozone selectively absorbs UV, not all visible or IR.",
            topic=TOPIC, outcome_code="C2.3k",
            skill_tested="Identifying UV absorption by atmospheric ozone",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "When light passes from air into glass at an angle, the phenomenon of bending at the boundary is",
            "refraction",
            ["reflection only with no transmission", "diffraction around the entire glass block", "polarization requiring a polarizing filter only"],
            "Refraction occurs due to change in speed at the interface between media.",
            "Bending at boundary is refraction; reflection bounces without entering.",
            topic=TOPIC, outcome_code="C2.4k",
            skill_tested="Identifying refraction at media boundary",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Diffraction of light is best observed when light passes through",
            "an opening comparable in size to the wavelength",
            ["a slit millions of times wider than the wavelength", "a perfect vacuum with no obstacles ever", "a copper wire carrying DC current"],
            "Diffraction is significant when aperture size is similar to λ.",
            "Very large openings show negligible diffraction effects.",
            topic=TOPIC, outcome_code="C2.4k",
            skill_tested="Identifying conditions for observable light diffraction",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Polarized sunglasses reduce glare from horizontal surfaces because they",
            "block light waves oscillating in a specific plane",
            ["amplify all reflected light equally", "convert all EMR to radio waves", "increase the speed of light in air"],
            "Polarizing filters transmit one plane of oscillation, reducing polarized glare.",
            "Polarizers filter orientation; they do not amplify or change c.",
            topic=TOPIC, outcome_code="C2.4k",
            skill_tested="Explaining glare reduction by polarizing filters",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "In a vacuum, all electromagnetic waves travel at the same",
            "speed regardless of frequency",
            ["wavelength only with different speeds per type", "energy with lower frequencies always faster", "amplitude with higher frequencies always slower"],
            "In vacuum, c = fλ is constant; changing f changes λ inversely.",
            "Speed in vacuum is c for all EMR; frequency does not change speed.",
            topic=TOPIC, outcome_code="C2.5k",
            skill_tested="Stating constant speed of all EMR in vacuum",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "A reflecting telescope uses a curved mirror to",
            "collect and focus incoming light to a focal point",
            ["produce radio signals from the ionosphere", "generate nuclear fusion in the tube", "convert all visible light to X-rays"],
            "Mirrors gather EMR and bring it to focus for observation or detection.",
            "Telescopes collect/focus light; they do not cause fusion or frequency conversion.",
            topic=TOPIC, outcome_code="C2.7k",
            skill_tested="Describing reflecting telescope mirror function",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Nuclear fusion in the Sun produces energy and releases",
            "a broad spectrum of electromagnetic radiation",
            ["only visible green light with no other wavelengths", "sound waves that travel through the vacuum of space", "static electric charges with no radiation"],
            "Fusion releases enormous energy radiated across the EM spectrum.",
            "The Sun emits full spectrum EMR, not only green light.",
            topic=TOPIC, outcome_code="C2.8k",
            skill_tested="Relating solar fusion to EMR emission",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "An emission spectrum from excited gas atoms shows",
            "bright lines at specific wavelengths characteristic of the element",
            ["a continuous rainbow with no gaps for all elements", "only infrared with no visible lines ever", "identical lines for every element in the periodic table"],
            "Excited atoms emit photons at discrete wavelengths unique to each element.",
            "Each element has a unique line spectrum fingerprint.",
            topic=TOPIC, outcome_code="C2.9k",
            skill_tested="Interpreting atomic emission spectrum pattern",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "The Doppler effect applied to light from distant galaxies provides evidence that",
            "the universe is expanding",
            ["all stars are stationary relative to Earth", "light speed depends on source velocity in vacuum", "gamma rays cannot be detected from space"],
            "Redshift of spectral lines indicates galaxies moving away from us.",
            "Redshift supports expansion; c in vacuum remains constant.",
            topic=TOPIC, outcome_code="C2.10k",
            skill_tested="Applying Doppler redshift evidence for cosmic expansion",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "A main-sequence star like the Sun will eventually, after exhausting core hydrogen,",
            "expand into a red giant phase",
            ["immediately collapse to a black hole with no intermediate stage", "stop all nuclear reactions and become invisible instantly", "transform into a planet with no fusion"],
            "Stellar evolution for Sun-like stars includes red giant stage before white dwarf.",
            "Sun-mass stars do not go directly to black hole.",
            topic=TOPIC, outcome_code="C2.11k",
            skill_tested="Describing main-sequence star evolutionary stage",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Microwave radiation in a kitchen microwave oven primarily transfers energy to food by",
            "causing polar molecules (like water) to rotate and generate heat",
            ["ionizing all atoms to form plasma at room temperature", "emitting visible light that replaces all nutrients", "blocking all infrared from the heating element only"],
            "Microwaves excite molecular rotation (dielectric heating), especially in water.",
            "Microwave ovens use non-ionizing microwave EMR, not ionizing radiation.",
            topic=TOPIC, outcome_code="C2.1sts",
            skill_tested="Explaining microwave oven heating mechanism",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "X-rays are used in medical imaging because they",
            "penetrate soft tissue but are partially absorbed by denser bone",
            ["are completely absorbed by all human tissue equally", "have wavelengths longer than radio waves", "travel only through solid copper wire"],
            "Differential absorption creates contrast between bone and soft tissue on film.",
            "X-rays are short wavelength, high penetration—not equally absorbed.",
            topic=TOPIC, outcome_code="C2.1sts",
            skill_tested="Explaining X-ray medical imaging principle",
            difficulty="Easy", estimated_time_seconds=70,
        ),
    ]


def _parameterized():
    items = []
    waves = [
        (3e8, 600e-9, 5e14),
        (3e8, 500e-9, 6e14),
        (3e8, 2e-2, 1.5e10),
        (3e8, 1e-3, 3e11),
        (3e8, 400e-9, 7.5e14),
        (3e8, 700e-9, 4.29e14),
        (3e8, 0.1, 3e9),
        (3e8, 3e-2, 1e10),
    ]
    for v, lam, f in waves:
        items.append(nr(
            f"Electromagnetic radiation travels at {v:.0e} m/s in a vacuum with wavelength {lam:.0e} m. "
            f"What is the frequency in hertz? Express in scientific notation with one digit before the decimal.",
            f"{f:.1e}",
            f"f = v/λ = {v:.0e}/{lam:.0e} = {f:.1e} Hz.",
            "Students multiply v×λ instead of dividing, or confuse wavelength units.",
            topic=TOPIC, outcome_code="C2.6k",
            skill_tested="Calculating EMR frequency using universal wave equation",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for f, lam in [(5e14, 6e-7), (1e15, 3e-7), (1e10, 0.03), (2e14, 1.5e-6)]:
        items.append(nr(
            f"Radiation with frequency {f:.0e} Hz travels at 3.0e8 m/s in vacuum. "
            f"What is the wavelength in metres? Express in scientific notation.",
            f"{lam:.1e}",
            f"λ = v/f = 3.0×10⁸/{f:.0e} = {lam:.1e} m.",
            "Students invert the formula using λ/f instead of v/f.",
            topic=TOPIC, outcome_code="C2.6k",
            skill_tested="Calculating EMR wavelength from frequency",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    emr_mc = [
        ("Infrared radiation is used in remote controls primarily because", "IR LEDs can emit pulses detected by a receiver without visible light", ["IR has higher energy than gamma rays", "IR cannot travel through air", "IR only exists inside nuclear reactors"], "IR remotes use non-visible wavelengths detected by photodiodes.", "IR is lower energy than gamma; it travels through air.", "C2.1sts", "Describing infrared remote control application", "Easy", 65),
        ("Absorption spectra from cool gases in front of a bright source show", "dark lines where specific wavelengths are absorbed", ["bright lines at all wavelengths uniformly", "no interaction between light and gas", "only gamma radiation with no visible features"], "Cool gas absorbs specific wavelengths, creating dark Fraunhofer-type lines.", "Absorption removes specific wavelengths, creating dark lines.", "C2.9k", "Interpreting absorption spectrum features", "Medium", 85),
        ("Radio telescopes detect", "long-wavelength EMR from astronomical sources", ["only sound waves from stellar explosions", "visible light exclusively with no other wavelengths", "direct current from household batteries"], "Radio telescopes collect radio-frequency EMR, not sound or DC.", "Astronomical radio telescopes detect radio EMR.", "C2.7k", "Identifying radio telescope detection range", "Easy", 60),
        ("A white dwarf is a stellar remnant that", "is dense and hot but no longer fuses hydrogen in its core", ["is larger than a red supergiant in radius", "fuses hydrogen more vigorously than a main-sequence star", "emits no electromagnetic radiation"], "White dwarfs are compact stellar cores without active fusion.", "White dwarfs are small and dense, not larger than supergiants.", "C2.11k", "Describing white dwarf stellar remnant properties", "Medium", 80),
        ("Fiber optic cables transmit internet data using", "total internal reflection of infrared or visible light in glass fibres", ["sound waves through copper cores only", "static magnetic fields with no EMR", "alpha particle beams through plastic tubes"], "Light signals bounce inside fibre cores via total internal reflection.", "Fiber optics use light (EMR), not sound or particle beams.", "C2.1sts", "Explaining fiber optic light transmission principle", "Medium", 75),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in emr_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
