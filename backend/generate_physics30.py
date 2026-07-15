"""Generate, validate, and export the Physics 30 question pool (~450 questions)."""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from phys30_questions.helpers import mc, nr, VALID_OUTCOMES
from phys30_questions.unit_a import questions as unit_a
from phys30_questions.unit_b import questions as unit_b
from phys30_questions.unit_c import questions as unit_c
from phys30_questions.unit_d import questions as unit_d

OUTPUT = Path(__file__).parent.parent / "questions.json" / "physics30_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]

TOPIC_A = "Momentum and Impulse"
TOPIC_B = "Forces and Fields"
TOPIC_C = "Electromagnetic Radiation"
TOPIC_D = "Atomic Physics"

K_COULOMB = 8.99e9
H = 6.63e-34
C_LIGHT = 3.00e8
E_CHARGE = 1.60e-19


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def deduplicate(items: list) -> list:
    seen = set()
    unique = []
    for item in items:
        key = (item["topic"].lower(), normalize_text(item["question_text"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def programmatic_supplements():
    """Parameterized original MC/NR questions to build the pool."""
    extra = []

    # --- Unit A: Momentum p = mv ---
    momentum_data = [
        (2.0, 5.0, 10), (0.15, 20, 3), (1.5, 4.0, 6), (0.80, 12, 9.6), (3.0, 2.5, 7.5),
        (0.25, 40, 10), (5.0, 1.2, 6), (0.50, 18, 9), (2.5, 6.0, 15), (0.12, 50, 6),
        (4.0, 3.5, 14), (0.30, 25, 7.5), (1.0, 9.0, 9), (6.0, 0.80, 4.8), (0.20, 35, 7),
        (2.2, 7.0, 15.4), (0.45, 16, 7.2), (3.5, 2.0, 7), (0.60, 14, 8.4), (1.8, 5.5, 9.9),
    ]
    for mass, vel, p in momentum_data:
        extra.append(nr(
            f"An object of mass ${mass}\\ \\text{{kg}}$ moves at ${vel}\\ \\text{{m/s}}$. "
            f"Calculate its momentum in $\\text{{kg·m/s}}$. Record to one decimal place.",
            f"{p:.1f}" if p != int(p) else str(int(p)),
            f"$p = mv = {mass} \\times {vel} = {p}\\ \\text{{kg·m/s}}$.",
            "Students multiply by 2 or confuse momentum with kinetic energy.",
            topic=TOPIC_A, outcome_code="A1.1k",
            skill_tested=f"Calculating momentum for {mass} kg at {vel} m/s",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Unit A: Impulse F·Δt
    impulse_data = [
        (150, 0.020, 3.0), (80, 0.050, 4.0), (200, 0.010, 2.0), (45, 0.080, 3.6),
        (500, 0.004, 2.0), (120, 0.030, 3.6), (60, 0.100, 6.0), (300, 0.015, 4.5),
        (25, 0.200, 5.0), (400, 0.008, 3.2), (90, 0.040, 3.6), (175, 0.025, 4.4),
    ]
    for force, dt, impulse in impulse_data:
        extra.append(nr(
            f"A constant force of ${force}\\ \\text{{N}}$ acts on an object for ${dt}\\ \\text{{s}}$. "
            f"What is the impulse in $\\text{{N·s}}$? Record to one decimal place.",
            f"{impulse:.1f}",
            f"$J = F\\Delta t = {force} \\times {dt} = {impulse}\\ \\text{{N·s}}$.",
            "Students report force instead of impulse or forget to multiply by time.",
            topic=TOPIC_A, outcome_code="A1.2k",
            skill_tested=f"Computing impulse at {force} N for {dt} s",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    # Unit A: 1D momentum conservation (m1*v1 + m2*v2 = (m1+m2)*vf for inelastic)
    inelastic_data = [
        (2.0, 6.0, 3.0, 0, 2.4), (1.0, 8.0, 2.0, 0, 2.67), (3.0, 4.0, 1.0, 0, 3.0),
        (0.5, 10, 0.5, 0, 5.0), (4.0, 3.0, 2.0, 0, 2.0), (1.5, 6.0, 1.5, 0, 3.0),
        (2.0, 5.0, 1.0, 0, 3.3), (3.0, 2.0, 1.0, 0, 1.5),
    ]
    for m1, v1, m2, v2, vf in inelastic_data:
        extra.append(nr(
            f"Cart A (${m1}\\ \\text{{kg}}$) moves at ${v1}\\ \\text{{m/s}}$ and collides with stationary "
            f"Cart B (${m2}\\ \\text{{kg}}$). They stick together. Find common final speed in $\\text{{m/s}}$. "
            f"Record to one decimal place.",
            f"{vf:.1f}",
            f"$v_f = (m_1 v_1 + m_2 v_2)/(m_1+m_2) = ({m1* v1}+{m2*v2})/{m1+m2} = {vf}\\ \\text{{m/s}}$.",
            "Students divide by one mass only or forget the stationary cart contributes zero momentum.",
            topic=TOPIC_A, outcome_code="A1.4k",
            skill_tested=f"Inelastic collision final speed {m1} kg + {m2} kg",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit A: KE comparison elastic vs inelastic MC
    ke_mc = [
        ("In an elastic collision between two objects, total kinetic energy after impact is",
         "equal to total kinetic energy before impact",
         ["always zero", "always greater than before impact", "always half the original value"],
         "Elastic collisions conserve kinetic energy as well as momentum.",
         "Students confuse elastic with inelastic collisions.",
         "A1.5k", "Stating KE conservation in elastic collisions", "Easy", 55),
        ("Clay balls that deform and move together after striking lose kinetic energy mainly because",
         "some mechanical energy is converted to thermal and deformation energy",
         ["momentum is not conserved in the collision", "mass disappears during contact", "gravity reverses their motion"],
         "Inelastic collisions convert some KE to internal energy while momentum is still conserved.",
         "Students think KE loss means momentum is not conserved.",
         "A1.5k", "Explaining KE loss in inelastic collisions", "Medium", 75),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in ke_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Unit A: more MC variants
    a_mc_extra = [
        ("A graph of force versus time during a bat hitting a ball shows a broad peak. A softer grip that lets the bat recoil would",
         "widen the force-time pulse, reducing peak force for the same impulse",
         ["eliminate all impulse on the ball", "increase peak force while shortening contact time", "change the ball's mass during contact"],
         "Same impulse spread over longer time lowers peak force.",
         "Students think softer contact increases peak force.",
         "A1.1sts", "Analyzing bat grip effect on impulse profile", "Medium", 80),
        ("When reporting impulse in SI units, the correct combination is",
         "newton-seconds (N·s)",
         ["joules per second only", "kilograms per metre", "watts per second"],
         "Impulse has units of force × time = N·s, equivalent to kg·m/s.",
         "Students use joules for impulse.",
         "A1.4s", "Using correct SI units for impulse", "Easy", 55),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in a_mc_extra:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit B: Coulomb's law F = kq1q2/r^2 (microcoulombs, cm) ---
    coulomb_data = [
        (2.0, 3.0, 0.10, 5.4), (1.0, 1.0, 0.05, 3.6), (4.0, 2.0, 0.20, 1.8),
        (3.0, 3.0, 0.15, 3.6), (5.0, 1.0, 0.10, 4.5), (2.0, 2.0, 0.08, 5.6),
        (1.5, 4.0, 0.12, 3.7), (6.0, 2.0, 0.30, 1.2), (3.0, 1.0, 0.06, 7.5),
        (2.0, 5.0, 0.25, 1.4), (4.0, 4.0, 0.20, 3.6), (1.0, 3.0, 0.10, 2.7),
        (8.0, 1.0, 0.40, 0.45), (2.0, 8.0, 0.16, 5.6), (3.0, 2.0, 0.09, 6.6),
    ]
    for q1, q2, r_m, f_n in coulomb_data:
        q1c = q1 * 1e-6
        q2c = q2 * 1e-6
        extra.append(nr(
            f"Two point charges of $+{q1}\\ \\mu\\text{{C}}$ and $-{q2}\\ \\mu\\text{{C}}$ are "
            f"${r_m*100:.0f}\\ \\text{{cm}}$ apart. Calculate the magnitude of the electric force in newtons. "
            f"Use $k = 8.99 \\times 10^9\\ \\text{{N·m}}^2/\\text{{C}}^2$. Record to one decimal place.",
            f"{f_n:.1f}",
            f"$F = k|q_1 q_2|/r^2 = 8.99\\times10^9 \\times {q1c:.2e} \\times {q2c:.2e} / {r_m}^2 "
            f"\\approx {f_n}\\ \\text{{N}}$.",
            "Students forget to square distance or omit the $10^{-6}$ conversion for microcoulombs.",
            topic=TOPIC_B, outcome_code="B1.6k",
            skill_tested=f"Coulomb force for {q1} and {q2} μC at {r_m*100:.0f} cm",
            difficulty="Medium", estimated_time_seconds=110,
        ))

    # Unit B: Electric field E = F/q or E = kQ/r^2
    efield_data = [
        (4.0, 0.10, 3600), (2.0, 0.05, 7200), (1.0, 0.20, 225), (5.0, 0.15, 2000),
        (3.0, 0.08, 4219), (6.0, 0.25, 864), (2.0, 0.12, 1249), (4.0, 0.18, 1109),
    ]
    for q_uc, r_m, e_nc in efield_data:
        extra.append(nr(
            f"A point charge of $+{q_uc}\\ \\mu\\text{{C}}$ creates an electric field. "
            f"Calculate the field strength at ${r_m*100:.0f}\\ \\text{{cm}}$ from the charge in $\\text{{N/C}}$. "
            f"Use $k = 8.99 \\times 10^9\\ \\text{{N·m}}^2/\\text{{C}}^2$. Record to the nearest whole number.",
            str(int(round(e_nc))),
            f"$E = kQ/r^2$ with $Q = {q_uc}\\times10^{{-6}}\\ \\text{{C}}$ and $r = {r_m}\\ \\text{{m}}$ "
            f"gives $E \\approx {int(round(e_nc))}\\ \\text{{N/C}}$.",
            "Students use $r$ instead of $r^2$ or forget charge conversion.",
            topic=TOPIC_B, outcome_code="B2.6k",
            skill_tested=f"Electric field from {q_uc} μC at {r_m*100:.0f} cm",
            difficulty="Medium", estimated_time_seconds=105,
        ))

    # Unit B: Potential difference ΔV = Ed
    potential_data = [
        (500, 0.020, 10), (1200, 0.015, 18), (800, 0.025, 20), (300, 0.040, 12),
        (2000, 0.010, 20), (450, 0.030, 13.5), (600, 0.050, 30), (1500, 0.008, 12),
    ]
    for e_field, dist, dv in potential_data:
        extra.append(nr(
            f"A uniform electric field of ${e_field}\\ \\text{{N/C}}$ exists between two parallel plates "
            f"separated by ${dist*100:.1f}\\ \\text{{cm}}$. Calculate the potential difference in volts. "
            f"Record to one decimal place.",
            f"{dv:.1f}",
            f"$\\Delta V = Ed = {e_field} \\times {dist} = {dv}\\ \\text{{V}}$.",
            "Students forget to convert cm to m or divide instead of multiply.",
            topic=TOPIC_B, outcome_code="B2.5k",
            skill_tested=f"Potential difference at {e_field} N/C over {dist*100:.1f} cm",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    # Unit B: Magnetic force F = Bqv
    magforce_data = [
        (0.40, 3.0e5, 1.5e-6, 0.18), (0.25, 4.0e5, 2.0e-6, 0.20), (0.60, 2.0e5, 1.0e-6, 0.12),
        (0.80, 1.5e5, 1.5e-6, 0.18), (0.30, 6.0e5, 2.0e-6, 0.36), (0.50, 2.5e5, 1.2e-6, 0.15),
    ]
    for b_t, v, q_c, f_n in magforce_data:
        extra.append(nr(
            f"A particle with charge $+{q_c/1e-6:.1f}\\ \\mu\\text{{C}}$ moves at "
            f"${v/1e5:.1f} \\times 10^5\\ \\text{{m/s}}$ perpendicular to a "
            f"${b_t}\\ \\text{{T}}$ magnetic field. Find the magnetic force magnitude in newtons. "
            f"Record to two decimal places.",
            f"{f_n:.2f}",
            f"$F = Bqv = {b_t} \\times {q_c:.2e} \\times {v:.2e} = {f_n:.2f}\\ \\text{{N}}$.",
            "Students omit charge or use sin(90°) incorrectly when motion is already perpendicular.",
            topic=TOPIC_B, outcome_code="B3.5k",
            skill_tested=f"Magnetic force at B={b_t} T, v={v/1e5:.1f}e5 m/s",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit B: Velocity selector v = E/B
    vsel_data = [
        (2000, 0.50, 4000), (4000, 0.80, 5000), (1500, 0.30, 5000), (6000, 1.20, 5000),
        (2500, 0.50, 5000), (3000, 0.75, 4000), (1200, 0.40, 3000), (5000, 1.00, 5000),
    ]
    for e_nc, b_t, v_ms in vsel_data:
        extra.append(nr(
            f"In a velocity selector, electric field strength is ${e_nc}\\ \\text{{N/C}}$ and "
            f"magnetic field strength is ${b_t}\\ \\text{{T}}$, mutually perpendicular. "
            f"At what speed in $\\text{{m/s}}$ would a charged particle pass undeflected? Record as a whole number.",
            str(int(v_ms)),
            f"$v = E/B = {e_nc}/{b_t} = {v_ms}\\ \\text{{m/s}}$.",
            "Students invert the ratio using $B/E$ or forget fields must be perpendicular.",
            topic=TOPIC_B, outcome_code="B3.6k",
            skill_tested=f"Velocity selector speed at E={e_nc} N/C, B={b_t} T",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Unit B: MC supplements
    b_mc_extra = [
        ("Charging a metal sphere by touching it with a negatively charged rod is called",
         "charging by conduction",
         ["charging by induction", "polarization without charge transfer", "charging by friction only"],
         "Conduction requires direct contact and transfers charge between objects.",
         "Students label contact charging as induction.",
         "B1.3k", "Identifying conduction charging method", "Easy", 55),
        ("Excess charge on a solid metal conductor in electrostatic equilibrium resides",
         "on the outer surface",
         ["uniformly throughout the volume", "only at the geometric centre", "only on interior faces"],
         "Free electrons in conductors redistribute until the interior field is zero.",
         "Students think charge spreads uniformly through the metal volume.",
         "B1.4k", "Describing charge distribution on conductors", "Easy", 60),
        ("Compared to gravitational force, Coulomb's law and Newton's law of gravitation both",
         "follow an inverse-square relationship with distance",
         ["increase linearly with distance", "are identical in strength for all objects", "apply only inside conductors"],
         "Both forces decrease with $1/r^2$ from point sources.",
         "Students think only gravity follows inverse-square.",
         "B1.8k", "Comparing inverse-square laws", "Easy", 65),
        ("An electric field line indicates the direction of force on a",
         "positive test charge",
         ["negative test charge always", "neutral test mass", "magnetic monopole"],
         "By convention, field lines show force direction on a positive test charge.",
         "Students reverse field direction for positive charges.",
         "B2.6k", "Defining electric field line direction convention", "Easy", 60),
        ("Millikan's oil-drop experiment provided evidence that electric charge is",
         "quantized in multiples of a fundamental unit",
         ["continuously variable to any value", "always zero on oil drops", "equal to gravitational charge"],
         "Millikan showed charge comes in integer multiples of $e$.",
         "Students think charge can take any real value continuously.",
         "B2.10k", "Stating charge quantization evidence from Millikan", "Medium", 75),
        ("In a region where electric and magnetic fields are perpendicular, a charged particle with speed $v = E/B$ experiences",
         "no net electromagnetic force",
         ["maximum magnetic force only", "maximum electric force only", "a force that doubles its speed instantly"],
         "Equal and opposite electric and magnetic forces cancel at the selector speed.",
         "Students think both forces add in the same direction.",
         "B3.6k", "Explaining undeflected motion in velocity selector", "Medium", 85),
        ("Moving a wire through a magnetic field induces current because charges in the wire experience",
         "a magnetic force that separates positive and negative charges",
         ["gravitational attraction to the magnet", "a change in wire mass", "only electric field from gravity"],
         "Relative motion between conductor and field causes charge separation — generator effect.",
         "Students confuse motor effect (current in field) with generator effect (motion in field).",
         "B3.9k", "Explaining generator effect in moving conductor", "Medium", 80),
        ("Lenz's law is consistent with conservation of energy because induced effects oppose",
         "the change that created them",
         ["all motion in the universe", "only electric fields", "gravitational potential energy only"],
         "Opposing induced effects prevent creating energy from nothing.",
         "Students memorize Lenz's law without connecting to energy conservation.",
         "B3.1sts", "Linking Lenz's law to energy conservation", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in b_mc_extra:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_B, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit C: Photon energy E = hf (use eV for convenience) ---
    # E(eV) = 1240 / lambda(nm) approximately
    photon_data = [
        (650, 1.91), (550, 2.25), (450, 2.76), (700, 1.77), (400, 3.10),
        (500, 2.48), (600, 2.07), (350, 3.54), (750, 1.65), (480, 2.58),
        (520, 2.38), (620, 2.00), (580, 2.14), (420, 2.95), (680, 1.82),
    ]
    for wavelength_nm, energy_ev in photon_data:
        extra.append(nr(
            f"Calculate the energy of a photon with wavelength ${wavelength_nm}\\ \\text{{nm}}$ in electron volts. "
            f"Use $E(\\text{{eV}}) = 1240/\\lambda(\\text{{nm}})$. Record to two decimal places.",
            f"{energy_ev:.2f}",
            f"$E = 1240/{wavelength_nm} = {energy_ev:.2f}\\ \\text{{eV}}$.",
            "Students use wavelength in metres without converting or invert the formula.",
            topic=TOPIC_C, outcome_code="C2.1k",
            skill_tested=f"Photon energy for {wavelength_nm} nm light",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Unit C: Photoelectric Kmax = hf - phi (work function in eV)
    pe_data = [
        (400, 2.20), (450, 2.50), (500, 2.00), (350, 3.00),
        (550, 2.00), (480, 2.20), (600, 1.80), (420, 2.50),
    ]
    for wl, phi in pe_data:
        e_photon = round(1240 / wl, 2)
        kmax = max(0.0, round(e_photon - phi, 2))
        extra.append(nr(
            f"Light of wavelength ${wl}\\ \\text{{nm}}$ strikes a metal with work function "
            f"${phi}\\ \\text{{eV}}$. Calculate maximum kinetic energy of emitted electrons in eV. "
            f"Use $E_\\text{{photon}} = 1240/\\lambda$. Record to two decimal places.",
            f"{kmax:.2f}",
            f"$K_{{max}} = hf - \\phi = {e_photon} - {phi} = {kmax:.2f}\\ \\text{{eV}}$.",
            "Students add work function instead of subtracting or use frequency without converting.",
            topic=TOPIC_C, outcome_code="C2.4k",
            skill_tested=f"Photoelectric Kmax at {wl} nm with phi={phi} eV",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # Unit C: Double slit wavelength lambda = xd/(nl) — solve for lambda in nm
    doubleslit_data = [
        (0.025, 0.15, 2, 1, 600), (0.030, 0.20, 3, 1, 500), (0.020, 0.12, 1, 2, 480),
        (0.040, 0.18, 2, 2, 450), (0.035, 0.25, 4, 1, 571), (0.022, 0.10, 1, 1, 440),
        (0.028, 0.16, 3, 2, 480), (0.032, 0.22, 2, 3, 528),
    ]
    for d_mm, x_m, n, l, wl_nm in doubleslit_data:
        d_m = d_mm / 1000
        extra.append(nr(
            f"In a double-slit experiment, slit separation is ${d_mm}\\ \\text{{mm}}$, "
            f"screen distance is ${x_m}\\ \\text{{m}}$, and the ${n}^{{\\text{{th}}}}$ bright fringe "
            f"of order $l = {l}$ is observed. Calculate wavelength in nm using "
            f"$\\lambda = x d / (n l)$. Record to the nearest whole number.",
            str(wl_nm),
            f"$\\lambda = {x_m} \\times {d_m} / ({n} \\times {l}) = {wl_nm}\\ \\text{{nm}}$.",
            "Students invert the formula or forget unit conversions for mm to m.",
            topic=TOPIC_C, outcome_code="C1.10k",
            skill_tested=f"Double-slit wavelength d={d_mm}mm x={x_m}m n={n} l={l}",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # Unit C: Refraction n = v1/v2
    refract_data = [
        (3.0e8, 2.0e8, 1.50), (3.0e8, 2.25e8, 1.33), (3.0e8, 1.5e8, 2.00),
        (2.0e8, 1.5e8, 1.33), (3.0e8, 1.0e8, 3.00), (2.25e8, 1.5e8, 1.50),
    ]
    for v1, v2, n_index in refract_data:
        extra.append(nr(
            f"Light travels at ${v1/1e8:.2f} \\times 10^8\\ \\text{{m/s}}$ in a vacuum and "
            f"${v2/1e8:.2f} \\times 10^8\\ \\text{{m/s}}$ in a medium. Calculate refractive index "
            f"$n = v_1/v_2$. Record to two decimal places.",
            f"{n_index:.2f}",
            f"$n = {v1:.2e}/{v2:.2e} = {n_index:.2f}$.",
            "Students invert the ratio using $v_2/v_1$.",
            topic=TOPIC_C, outcome_code="C1.11k",
            skill_tested=f"Refractive index from v1={v1/1e8:.2f}e8 and v2={v2/1e8:.2f}e8 m/s",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Unit C: MC supplements
    c_mc_extra = [
        ("EMR consists of oscillating electric and magnetic fields that are",
         "perpendicular to each other and to the direction of propagation",
         ["parallel to each other and to propagation", "stationary in space", "longitudinal like sound in air"],
         "EMR is a transverse wave with mutually perpendicular field components.",
         "Students describe EMR as longitudinal.",
         "C1.3k", "Describing EMR field orientation", "Easy", 60),
        ("Diffraction of light around a narrow slit occurs because",
         "wave energy spreads beyond a geometric shadow boundary",
         ["photons lose all energy at edges", "light travels only in straight lines", "interference destroys all wave energy"],
         "Diffraction is spreading past an obstacle; distinct from superposition interference.",
         "Students use diffraction and interference interchangeably.",
         "C1.8k", "Distinguishing diffraction from interference", "Medium", 75),
        ("A converging thin lens",
         "brings parallel rays closer to a focal point",
         ["always spreads rays apart like a diverging lens", "has no focal length", "reflects light like a mirror"],
         "Lenses are described by their effect on light rays, not surface shape alone.",
         "Students confuse lens terminology with mirror convex/concave labels.",
         "C1.7k", "Defining converging lens behaviour", "Easy", 55),
        ("Increasing only the intensity of light above the threshold frequency in the photoelectric effect",
         "increases the number of photoelectrons emitted per second",
         ["increases the maximum kinetic energy of each photoelectron", "decreases the work function of the metal", "changes the threshold frequency"],
         "Intensity affects photon flux (count), not individual photon energy above threshold.",
         "Students think brighter light means higher-energy photons.",
         "C2.3k", "Relating intensity to photoelectron rate", "Medium", 80),
        ("The Compton effect demonstrates photon momentum because scattered X-rays show",
         "longer wavelength and lower energy than the incident beam",
         ["no change in wavelength", "higher frequency after scattering", "complete absorption without scattering"],
         "Compton scattering transfers momentum and energy to the recoiling electron.",
         "Students think scattered photon gains energy.",
         "C2.6k", "Identifying Compton scattering evidence", "Medium", 85),
        ("Young's double-slit experiment supports the wave model because it produces",
         "an interference pattern of alternating bright and dark fringes",
         ["a single sharp shadow with no variation", "only particle tracks on a detector", "total internal reflection bands"],
         "Interference fringes are characteristic wave behaviour.",
         "Students attribute the pattern to photon collisions only.",
         "C1.9k", "Explaining double-slit wave evidence", "Easy", 65),
        ("Total internal reflection can occur when light travels from",
         "a higher-index medium toward a lower-index medium at an angle above the critical angle",
         ["any medium into any other at any angle", "vacuum into glass only", "lower index to higher index always"],
         "TIR requires $n_1 > n_2$ and angle of incidence exceeding the critical angle.",
         "Students think TIR happens at any boundary.",
         "C1.6k", "Stating conditions for total internal reflection", "Medium", 80),
        ("Planck's hypothesis that energy is quantized resolved the problem of",
         "ultraviolet catastrophe in blackbody radiation predictions",
         ["photoelectric effect only with no other applications", "nuclear decay half-lives", "gravitational lensing"],
         "Quantized oscillators explained blackbody spectrum at short wavelengths.",
         "Students attribute quantization only to photoelectric effect.",
         "C2.1sts", "Linking Planck quantization to blackbody problem", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in c_mc_extra:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_C, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Unit D: Energy level transition ΔE(eV) = hc/λ → use 1240/λ(nm) ---
    transition_data = [
        (486, 2.55), (434, 2.86), (656, 1.89), (410, 3.02), (397, 3.12),
        (589, 2.10), (122, 10.17), (95, 13.05), (365, 3.40), (540, 2.30),
    ]
    for wl_nm, delta_e in transition_data:
        extra.append(nr(
            f"An atom emits a photon of wavelength ${wl_nm}\\ \\text{{nm}}$. "
            f"Calculate the energy difference between the states in eV using $E = 1240/\\lambda$. "
            f"Record to two decimal places.",
            f"{delta_e:.2f}",
            f"$\\Delta E = 1240/{wl_nm} = {delta_e:.2f}\\ \\text{{eV}}$.",
            "Students use wavelength in metres or report frequency without converting to eV.",
            topic=TOPIC_D, outcome_code="D2.5k",
            skill_tested=f"Energy transition for {wl_nm} nm emission line",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Unit D: Half-life — fraction remaining after n half-lives = (1/2)^n
    halflife_data = [
        (1, 0.50), (2, 0.25), (3, 0.125), (4, 0.0625), (5, 0.03125),
        (6, 0.015625), (2, 0.25), (3, 0.125), (4, 0.0625),
    ]
    for n_half, fraction in halflife_data:
        pct = round(fraction * 100, 2)
        extra.append(nr(
            f"A radioactive sample undergoes ${n_half}$ half-lives. What percentage of the original "
            f"activity remains? Record to two decimal places.",
            f"{pct:.2f}",
            f"Fraction remaining $= (1/2)^{{{n_half}}} = {fraction}$; percentage $= {pct:.2f}\\%$.",
            "Students multiply by 2 instead of halving repeatedly.",
            topic=TOPIC_D, outcome_code="D3.3k",
            skill_tested=f"Fraction remaining after {n_half} half-lives",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Unit D: Mass defect energy ΔE = Δm c² — use MeV from mass in u (1 u ≈ 931.5 MeV)
    massdefect_data = [
        (0.002, 1.86), (0.005, 4.66), (0.010, 9.32), (0.003, 2.79), (0.008, 7.45),
        (0.004, 3.73), (0.006, 5.59), (0.012, 11.18), (0.001, 0.93), (0.007, 6.52),
    ]
    for dm_u, energy_mev in massdefect_data:
        extra.append(nr(
            f"A nuclear reaction has mass defect $\\Delta m = {dm_u}\\ \\text{{u}}$. "
            f"Calculate energy released in MeV using $1\\ \\text{{u}} = 931.5\\ \\text{{MeV}}/c^2$. "
            f"Record to two decimal places.",
            f"{energy_mev:.2f}",
            f"$\\Delta E = \\Delta m \\times 931.5 = {dm_u} \\times 931.5 = {energy_mev:.2f}\\ \\text{{MeV}}$.",
            "Students forget to multiply by 931.5 MeV/u or use joules without conversion.",
            topic=TOPIC_D, outcome_code="D3.6k",
            skill_tested=f"Mass defect energy for {dm_u} u",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    # Unit D: MC supplements
    d_mc_extra = [
        ("Rutherford's alpha-particle scattering experiment showed that most of the atom's volume is",
         "empty space with a small, dense, positively charged nucleus",
         ["a uniform sphere of positive charge", "entirely filled with electrons like a plum pudding", "devoid of any concentrated mass"],
         "Large-angle scattering implied a tiny massive nucleus.",
         "Students retain the plum pudding model after Rutherford's results.",
         "D1.4k", "Interpreting Rutherford scattering conclusions", "Easy", 65),
        ("Bohr's model introduced the idea that electrons in atoms occupy",
         "specific stationary states with quantized energy",
         ["any continuous range of energies", "only the nucleus", "orbits with arbitrary radii without restriction"],
         "Quantized orbits explain discrete line spectra.",
         "Students think Bohr model allows continuous energy levels.",
         "D2.4k", "Describing Bohr stationary states", "Medium", 75),
        ("Compared to fusion reactions, typical fission reactions per kilogram of fuel release",
         "less energy per unit mass",
         ["more energy per unit mass always", "exactly the same energy per nucleon", "no energy at all"],
         "Fusion releases more energy per unit mass; fission releases more per reaction event.",
         "Students think fission always outperforms fusion on every comparison.",
         "D3.5k", "Comparing fission and fusion energy per unit mass", "Medium", 85),
        ("Alpha radiation consists of",
         "helium-4 nuclei (two protons and two neutrons)",
         ["high-speed electrons", "electromagnetic photons only", "single protons only"],
         "Alpha particles are $^4_2\\text{He}$ nuclei.",
         "Students confuse alpha with beta or gamma radiation.",
         "D3.1k", "Identifying alpha particle composition", "Easy", 55),
        ("Beta-negative decay involves emission of",
         "an electron and an antineutrino from a neutron-rich nucleus",
         ["a helium nucleus and no neutrino", "only a gamma photon", "a positron and neutrino"],
         "Beta-minus converts a neutron to a proton with $e^-$ and $\\bar{\\nu}$ emission.",
         "Students confuse beta-negative with beta-positive decay.",
         "D3.2k", "Describing beta-negative decay products", "Medium", 80),
        ("In the Standard Model, protons and neutrons are composed of",
         "quarks held together by gluons",
         ["electrons orbiting a nucleus", "pure energy without constituents", "only photons"],
         "Hadrons are quark composites in the Standard Model.",
         "Students think protons are fundamental with no substructure.",
         "D4.3k", "Stating proton and neutron quark composition", "Medium", 75),
        ("Pair production requires photon energy at least equal to",
         "$2m_e c^2$ (about 1.02 MeV)",
         ["zero because photons have no mass", "the rest energy of a proton only", "half the electron rest energy"],
         "Photon must provide rest energy for both electron and positron.",
         "Students use single electron rest energy only.",
         "D3.1sts", "Stating threshold energy for pair production", "Hard", 95),
        ("A line-emission spectrum is produced when electrons in an atom",
         "drop from higher to lower energy levels, emitting photons of specific energies",
         ["absorb random amounts of energy continuously", "leave the atom entirely in all cases", "vibrate without changing energy levels"],
         "Discrete transitions produce discrete spectral lines.",
         "Students confuse emission with absorption spectra.",
         "D2.3k", "Explaining line-emission spectrum origin", "Easy", 65),
        ("The strong nuclear force is significant over a range of approximately",
         "$10^{-15}\\ \\text{m}$",
         ["$10^{-10}\\ \\text{m}$ (atomic diameter)", "$1\\ \\text{m}$", "$10^{-5}\\ \\text{m}$"],
         "Strong force operates at nuclear scale (~1 fm).",
         "Students confuse nuclear and atomic length scales.",
         "D4.2k", "Recalling strong force range", "Medium", 70),
        ("When comparing energy released per nucleon, fusion reactions generally",
         "release more energy per nucleon than fission reactions",
         ["release less energy per nucleon than fission", "release zero energy per nucleon", "are identical to chemical reactions"],
         "Fusion has higher binding energy per nucleon for light nuclei.",
         "Students generalize fission as always more energetic per nucleon.",
         "D3.5k", "Comparing fusion and fission energy per nucleon", "Hard", 90),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in d_mc_extra:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_D, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Additional cross-topic MC for integration contexts
    integration_mc = [
        ("A photon colliding with an electron (Compton scattering) can be analyzed using conservation laws from",
         "both momentum and energy principles",
         ["momentum only with no energy consideration", "energy only because photons have no momentum", "neither momentum nor energy"],
         "Compton analysis uses both conservation of momentum and energy.",
         "Students analyze Compton events with energy only.",
         "C2.6k", "Identifying conservation laws for Compton analysis", "Hard", 95),
        ("A particle accelerator uses magnetic fields to curve charged particle paths so that",
         "momentum and charge-to-mass ratio can be inferred from track radius",
         ["gravitational mass alone is measured without fields", "only neutral particles are detected", "electric fields are unnecessary in any accelerator"],
         "Magnetic deflection relates $r$, $p$, and $q$ for particle identification.",
         "Students think accelerators measure only speed without field analysis.",
         "D4.1k", "Linking magnetic deflection to particle identification", "Hard", 100),
        ("Gamma photon emission from an excited nucleus is analogous to",
         "photon emission when an electron drops between atomic energy levels",
         ["chemical combustion releasing heat only", "gravitational collapse of a star", "elastic collision of macroscopic carts"],
         "Both involve quantized energy state transitions releasing photons.",
         "Students see no parallel between nuclear and atomic transitions.",
         "D2.5k", "Comparing nuclear and atomic photon emission", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in integration_mc:
        topic = TOPIC_C if oc.startswith("C") else TOPIC_D if oc.startswith("D") else TOPIC_A
        extra.append(mc(qt, ans, dist, expl, mis, topic=topic, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # --- Extended pool: elastic 1D collision final velocities ---
    # m1*v1i + m2*v2i = m1*v1f + m2*v2f with v2i=0, elastic equal mass head-on -> exchange
    elastic_data = [
        (1.0, 6.0, 1.0, 0.0, 6.0), (2.0, 4.0, 1.0, 1.33, 5.33), (3.0, 5.0, 1.0, 2.0, 7.5),
        (1.0, 8.0, 1.0, 0.0, 8.0), (2.0, 3.0, 1.0, 1.0, 4.0), (4.0, 2.0, 1.0, 2.4, 3.2),
    ]
    for m1, v1, m2, v1f, v2f in elastic_data:
        extra.append(nr(
            f"In a one-dimensional elastic collision, object 1 (${m1}\\ \\text{{kg}}$) approaches at "
            f"${v1}\\ \\text{{m/s}}$ and hits stationary object 2 (${m2}\\ \\text{{kg}}$). "
            f"Find the speed of object 2 after collision in $\\text{{m/s}}$. Record to two decimal places.",
            f"{v2f:.2f}",
            f"Elastic collision solution gives $v_{{2f}} = {v2f:.2f}\\ \\text{{m/s}}$.",
            "Students use inelastic sticking formula for elastic collisions.",
            topic=TOPIC_A, outcome_code="A1.4k",
            skill_tested=f"Elastic collision v2f for {m1}kg at {v1} m/s into {m2}kg",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # Extended Unit A MC
    a_mc_bulk = [
        ("For a constant net force, doubling the contact time during a collision will",
         "halve the average force required for the same momentum change",
         ["double the momentum change", "eliminate impulse entirely", "quadruple the average force"],
         "$F_{avg} = \\Delta p / \\Delta t$; longer time reduces average force.",
         "Students think longer contact increases force.",
         "A1.2k", "Relating contact time to average collision force", "Medium", 75),
        ("A fireworks rocket gains upward speed as hot gases are expelled downward because",
         "the rocket-gas system conserves total momentum",
         ["gravity is cancelled during launch", "the gases have no mass", "momentum applies only to solids"],
         "Expelled gas momentum downward equals rocket momentum gain upward.",
         "Students think rockets push against ground or air only.",
         "A1.1sts", "Applying momentum conservation to rocket launch", "Medium", 80),
        ("When choosing SI units for reporting impulse, which combination is correct?",
         "kg·m/s or equivalently N·s",
         ["J/s only", "N/m", "kg·m/s²"],
         "Impulse has same units as momentum.",
         "Students report joules for impulse.",
         "A1.4s", "Reporting impulse in SI units", "Easy", 50),
        ("A spark timer recording marks every 0.10 s on tape attached to a cart is used to",
         "determine how the cart's position changes over equal time intervals",
         ["measure electric charge on the cart", "determine nuclear decay rates", "calibrate photoelectric cells"],
         "Spark timers provide position-time data for kinematics and collision analysis.",
         "Students confuse spark timers with radiation detectors.",
         "A1.2s", "Describing spark timer data collection", "Easy", 65),
        ("If a system's total momentum is not constant during an event, the most likely reason is",
         "a significant external impulse acted on the system",
         ["momentum is never conserved in collisions", "kinetic energy was converted to heat", "internal forces were zero"],
         "Non-constant momentum implies external net impulse.",
         "Students blame KE loss for momentum non-conservation.",
         "A1.3k", "Diagnosing non-conserved momentum", "Medium", 70),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in a_mc_bulk:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Extended Unit B: current I = q/t
    current_data = [
        (12, 3.0, 4.0), (8.0, 2.0, 4.0), (15, 5.0, 3.0), (6.0, 1.5, 4.0),
        (20, 4.0, 5.0), (9.0, 3.0, 3.0), (18, 6.0, 3.0), (10, 2.5, 4.0),
    ]
    for charge_c, time_s, current_a in current_data:
        extra.append(nr(
            f"A total charge of ${charge_c}\\ \\text{{C}}$ passes a point in a wire in ${time_s}\\ \\text{{s}}$. "
            f"Calculate the electric current in amperes. Record to one decimal place.",
            f"{current_a:.1f}",
            f"$I = q/t = {charge_c}/{time_s} = {current_a}\\ \\text{{A}}$.",
            "Students invert the ratio or confuse charge with current.",
            topic=TOPIC_B, outcome_code="B2.7k",
            skill_tested=f"Current from {charge_c} C in {time_s} s",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Extended Unit B MC bulk
    b_mc_bulk = [
        ("Two negative charges brought near each other experience a force that is",
         "repulsive",
         ["attractive", "zero always", "perpendicular to the line joining them only"],
         "Like charges repel according to Coulomb's law.",
         "Students think all charges attract.",
         "B1.2k", "Predicting force between like charges", "Easy", 50),
        ("An insulator can hold localized excess charge on its surface because",
         "charges are not free to move throughout the material",
         ["electrons move freely like in metals", "insulators contain no charged particles", "insulators eliminate all electric fields"],
         "Bound charges in insulators cannot redistribute easily.",
         "Students think insulators cannot hold any charge.",
         "B1.4k", "Explaining charge localization on insulators", "Easy", 60),
        ("The torsion balance experiment by Coulomb is historically important because it",
         "allowed measurement of small electric forces between charged spheres",
         ["proved that gravity does not exist", "measured the speed of light", "detected nuclear radiation"],
         "Coulomb quantified electrostatic force law using a sensitive torsion balance.",
         "Students confuse Coulomb's apparatus with Cavendish's gravitational balance purpose.",
         "B1.5k", "Describing Coulomb torsion balance purpose", "Medium", 75),
        ("Electric potential energy increases when a positive charge is moved",
         "against the direction of the electric field",
         ["with the direction of the electric field", "perpendicular to any field line without work", "only when magnetic fields are present"],
         "Moving against the field increases electric potential energy.",
         "Students think moving with the field always increases PE.",
         "B2.3k", "Relating PE change to field direction for positive charge", "Medium", 80),
        ("A uniform electric field between parallel plates is created when the plates",
         "carry equal and opposite charges",
         ["both carry the same sign of charge", "are uncharged but moving", "are made of magnetic material only"],
         "Opposite charges on parallel plates produce nearly uniform field between them.",
         "Students think same-sign plates create uniform fields.",
         "B2.6k", "Describing parallel plate field configuration", "Easy", 65),
        ("When a current-carrying wire is placed perpendicular to a uniform magnetic field, the wire experiences",
         "a magnetic force perpendicular to both the current and the field",
         ["no force because current has no charge", "a force parallel to the current only", "only gravitational attraction"],
         "Motor effect: $F = BIL$ when current is perpendicular to $\\vec{B}$.",
         "Students think force is parallel to current direction.",
         "B3.7k", "Describing motor effect on current-carrying wire", "Medium", 80),
        ("Faraday's law of electromagnetic induction states that a changing magnetic flux through a loop induces",
         "an electromotive force (emf) in the loop",
         ["only a static electric charge with no emf", "a permanent increase in mass", "gravitational acceleration"],
         "Changing flux induces emf — basis of generators and transformers.",
         "Students think constant flux still induces emf.",
         "B3.3k", "Stating Faraday's induction principle", "Medium", 75),
        ("MRI technology relies on strong magnetic fields and radio-frequency pulses to",
         "align and perturb nuclear spins in hydrogen atoms in tissue",
         ["ionize all atoms in the body completely", "measure only gravitational fields", "generate X-rays by electron collisions only"],
         "MRI uses nuclear magnetic resonance in hydrogen.",
         "Students confuse MRI with X-ray or CT mechanisms.",
         "B3.2sts", "Describing MRI technology application", "Medium", 85),
        ("A positively charged particle entering a uniform magnetic field perpendicular to its velocity follows",
         "a circular path",
         ["a straight line with no deflection always", "a parabolic path like in gravity only", "a path that stops immediately"],
         "Magnetic force perpendicular to velocity provides centripetal acceleration.",
         "Students predict straight-line motion for all charged particles in B fields.",
         "B3.5k", "Predicting path shape in uniform magnetic field", "Medium", 85),
        ("Oersted's discovery that a compass needle deflects near a current-carrying wire demonstrated",
         "electric currents produce magnetic fields",
         ["magnetic fields create electric charge", "gravity and electricity are identical", "currents eliminate magnetic fields"],
         "Oersted linked electricity and magnetism experimentally.",
         "Students reverse the cause-effect relationship.",
         "B3.3k", "Stating significance of Oersted's observation", "Easy", 65),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in b_mc_bulk:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_B, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Extended Unit C: frequency from wavelength
    freq_data = [
        (600, 5.00e14), (500, 6.00e14), (400, 7.50e14), (700, 4.29e14),
        (550, 5.45e14), (450, 6.67e14), (650, 4.62e14), (750, 4.00e14),
    ]
    for wl_nm, freq_hz in freq_data:
        extra.append(nr(
            f"Calculate the frequency of EMR with wavelength ${wl_nm}\\ \\text{{nm}}$ in air. "
            f"Use $c = 3.00 \\times 10^8\\ \\text{{m/s}}$. Express answer in $\\times 10^{{14}}\\ \\text{{Hz}}$ "
            f"to two decimal places (record just the coefficient, e.g. 5.00 for $5.00\\times10^{{14}}$).",
            f"{freq_hz/1e14:.2f}",
            f"$f = c/\\lambda = 3.00\\times10^8 / ({wl_nm}\\times10^{{-9}}) = {freq_hz:.2e}\\ \\text{{Hz}}$.",
            "Students forget to convert nm to metres.",
            topic=TOPIC_C, outcome_code="C1.2k",
            skill_tested=f"Frequency from wavelength {wl_nm} nm",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    c_mc_bulk = [
        ("Microwaves in a household oven have wavelengths typically in the range of",
         "centimetres",
         ["nanometres only", "kilometres", "metres only"],
         "Microwave oven radiation has $\\lambda \\approx 12$ cm.",
         "Students confuse microwave with visible or X-ray wavelengths.",
         "C1.2k", "Identifying microwave wavelength scale", "Easy", 55),
        ("Polarizing sunglasses reduce glare from horizontal surfaces primarily by",
         "blocking light with a specific polarization orientation",
         ["increasing the speed of all EMR", "converting photons to electrons", "reflecting all wavelengths equally"],
         "Polarizers absorb one field orientation of transverse EMR.",
         "Students think sunglasses only reduce intensity without polarization.",
         "C1.8k", "Explaining polarization in sunglasses", "Medium", 75),
        ("A concave mirror can produce a real inverted image when the object is placed",
         "beyond the focal point",
         ["always inside the focal point only", "at any distance without exception", "only at infinite distance with no real image"],
         "Real images form when object distance exceeds focal length for concave mirrors.",
         "Students think concave mirrors always produce virtual images.",
         "C1.7k", "Stating conditions for real image from concave mirror", "Medium", 80),
        ("The work function of a metal surface represents the",
         "minimum energy required to remove an electron from the surface",
         ["maximum kinetic energy of all photoelectrons", "total internal energy of the metal lattice", "speed of light in the metal"],
         "Work function $\\phi$ is the threshold binding energy per electron.",
         "Students confuse work function with photon energy or Kmax.",
         "C2.3k", "Defining photoelectric work function", "Easy", 60),
        ("Einstein's photoelectric equation $K_{max} = hf - \\phi$ assumes that",
         "one photon interacts with one electron",
         ["many photons are needed to eject one electron always", "intensity determines photon energy", "work function equals photon energy"],
         "Photon model: single photon transfers energy to single electron.",
         "Students think intensity changes individual photon energy.",
         "C2.4k", "Stating one-photon-one-electron model", "Medium", 75),
        ("Hertz's observation of sparks when illuminated with UV light contributed to discovery of",
         "the photoelectric effect",
         ["nuclear fission", "gravitational waves", "superconductivity"],
         "UV light facilitated electron emission — early photoelectric evidence.",
         "Students attribute the observation to unrelated phenomena.",
         "C2.1sts", "Linking Hertz observation to photoelectric effect", "Medium", 80),
        ("Automatic door sensors using infrared LEDs detect pedestrians because",
         "a photodetector responds when reflected IR intensity changes",
         ["infrared light has no photon energy", "doors use only magnetic fields", "visible light is the only radiation detected"],
         "IR photons from LED reflect off objects and trigger photoelectric detection.",
         "Students think sensors use only pressure switches.",
         "C2.3sts", "Explaining IR sensor door technology", "Easy", 65),
        ("A diffraction grating separates colours more effectively than a prism for high-resolution spectroscopy because",
         "interference maxima from many closely spaced slits produce sharp wavelength resolution",
         ["prisms do not refract light at all", "gratings use nuclear transitions", "prisms only work in vacuum"],
         "Gratings use interference; prisms use dispersion by refraction.",
         "Students think both devices use identical physics.",
         "C1.12k", "Comparing grating and prism spectral resolution", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in c_mc_bulk:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_C, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Extended Unit D MC bulk
    d_mc_bulk = [
        ("J. J. Thomson measured the charge-to-mass ratio of electrons using",
         "deflection of cathode rays in electric and magnetic fields",
         ["alpha particle scattering from gold foil", "photoelectric emission from zinc", "nuclear magnetic resonance"],
         "Thomson used field deflection to find $q/m$ for electrons.",
         "Students attribute Thomson's work to Rutherford's scattering experiment.",
         "D1.3k", "Identifying Thomson's experimental method", "Medium", 75),
        ("The line spectrum of hydrogen is explained in the Bohr model by",
         "transitions between discrete energy levels emitting photons of specific energies",
         ["continuous energy changes in the nucleus", "random thermal vibrations only", "gravitational collapse of the atom"],
         "Discrete $\\Delta E$ between levels produces discrete spectral lines.",
         "Students think continuous energy levels produce line spectra.",
         "D2.4k", "Explaining hydrogen line spectrum with Bohr model", "Medium", 75),
        ("An absorption spectrum shows dark lines because",
         "atoms in a cooler gas absorb specific wavelengths from a continuous source",
         ["atoms emit extra wavelengths into the beam", "the source stops producing all light", "photons gain energy passing through"],
         "Absorption removes specific frequencies matching atomic transitions.",
         "Students confuse absorption and emission spectra.",
         "D2.3k", "Explaining absorption spectrum formation", "Medium", 80),
        ("Carbon-14 dating relies on measuring the ratio of $^{14}\\text{C}$ to $^{12}\\text{C}$ because",
         "living organisms maintain a steady $^{14}\\text{C}$ level while alive, which decreases after death",
         ["$^{14}\\text{C}$ is stable forever with no decay", "all carbon isotopes decay at the same rate", "$^{12}\\text{C}$ does not exist in organic matter"],
         "Decay of $^{14}\\text{C}$ after death gives age information.",
         "Students think C-14 dating measures total carbon mass only.",
         "D3.3k", "Explaining basis of carbon-14 dating", "Medium", 85),
        ("In a nuclear reactor, fission chain reactions are controlled by",
         "absorbing excess neutrons with control rods",
         ["removing all fuel immediately without moderation", "increasing reaction rate without limit", "eliminating all neutron production"],
         "Control rods absorb neutrons to maintain steady power output.",
         "Students think control rods speed up reactions.",
         "D3.2sts", "Describing nuclear reactor control mechanism", "Medium", 80),
        ("The up quark and down quark differ primarily in",
         "electric charge (+2/3 e vs -1/3 e)",
         ["having no role in protons or neutrons", "being the same particle with different names", "having infinite mass"],
         "Up quark: +2/3 e; down quark: -1/3 e.",
         "Students think quarks have no charge.",
         "D4.4k", "Comparing up and down quark charges", "Medium", 75),
        ("Electron capture in a nucleus can be represented as a proton combining with an inner electron to form",
         "a neutron and a neutrino",
         ["an alpha particle and a positron", "two protons", "a gamma ray only with no particle change"],
         "$p + e^- \\rightarrow n + \\nu_e$ in electron capture.",
         "Students confuse electron capture with beta-plus emission.",
         "D4.5k", "Describing electron capture products", "Hard", 95),
        ("Bubble chamber photographs of particle tracks are curved because",
         "charged particles experience magnetic forces perpendicular to their velocity",
         ["all particles have no charge", "gravity alone bends all tracks equally", "tracks are drawn by hand without physics"],
         "Magnetic deflection reveals charge and momentum information.",
         "Students think track curvature is random.",
         "D4.1k", "Explaining curved tracks in bubble chambers", "Medium", 80),
        ("The binding energy per nucleon is highest for nuclei near",
         "iron (Fe), indicating maximum nuclear stability in that region",
         ["hydrogen only with no peak elsewhere", "uranium with the highest stability", "helium with the lowest stability"],
         "Binding energy per nucleon peaks near Fe.",
         "Students think heavier nuclei are always more stable per nucleon.",
         "D3.5k", "Locating peak nuclear binding energy per nucleon", "Hard", 90),
        ("Thomson's plum pudding model was replaced because",
         "Rutherford observed large-angle alpha scattering inconsistent with a diffuse positive sphere",
         ["electrons were proven not to exist", "cathode rays were shown to be protons", "photoelectric effect disproved atoms"],
         "Large-angle scattering required a concentrated nucleus.",
         "Students think photoelectric effect disproved Thomson's model directly.",
         "D1.4k", "Explaining why plum pudding model was abandoned", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in d_mc_bulk:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_D, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Unit D: remaining activity after n half-lives (fraction as decimal NR)
    activity_data = [
        (1, 0.5), (2, 0.25), (3, 0.125), (4, 0.0625), (5, 0.03125),
        (6, 0.015625), (7, 0.0078125), (8, 0.00390625),
    ]
    for n, frac in activity_data:
        extra.append(nr(
            f"A sample has initial activity $A_0$. After ${n}$ half-lives, what fraction of $A_0$ remains? "
            f"Record as a decimal to four decimal places.",
            f"{frac:.4f}",
            f"Fraction $= (1/2)^{{{n}}} = {frac}$.",
            "Students add half-lives instead of multiplying fractions.",
            topic=TOPIC_D, outcome_code="D3.3k",
            skill_tested=f"Activity fraction after {n} half-lives",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    # Final expansion batch to reach ~450 pool size
    # Unit A: kinetic energy for momentum check MC
    a_final_mc = [
        ("A $0.40\\ \\text{kg}$ object moving at $10\\ \\text{m/s}$ has kinetic energy of",
         "$20\\ \\text{J}$",
         ["$4\\ \\text{J}$", "$40\\ \\text{J}$", "$100\\ \\text{J}$"],
         "$KE = \\frac{1}{2}mv^2 = 0.5 \\times 0.40 \\times 100 = 20\\ \\text{J}$.",
         "Students forget the $\\frac{1}{2}$ factor in kinetic energy.",
         "A1.5k", "Computing KE to compare collision types", "Easy", 70),
        ("During an explosion that splits one object into two fragments, momentum is conserved if",
         "the object-explosion products system experiences no external impulse",
         ["kinetic energy must also stay constant", "gravity must be zero everywhere", "fragments must have equal mass"],
         "Explosions conserve momentum in isolated systems but increase total KE.",
         "Students require KE conservation for all momentum problems.",
         "A1.3k", "Applying momentum conservation to explosions", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in a_final_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_A, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Unit B: wire force F=BIL
    wire_data = [
        (0.50, 2.0, 0.30, 0.30), (0.80, 1.5, 0.25, 0.30), (1.2, 3.0, 0.40, 1.44),
        (0.35, 4.0, 0.20, 0.28), (0.60, 2.5, 0.50, 0.75), (1.0, 5.0, 0.15, 0.75),
        (0.45, 1.0, 0.60, 0.27), (0.70, 3.5, 0.35, 0.86),
    ]
    for b_t, i_a, l_m, f_n in wire_data:
        extra.append(nr(
            f"A wire of length ${l_m}\\ \\text{{m}}$ carries current ${i_a}\\ \\text{{A}}$ perpendicular to "
            f"a ${b_t}\\ \\text{{T}}$ magnetic field. Calculate force in newtons. Record to two decimal places.",
            f"{f_n:.2f}",
            f"$F = BIL = {b_t} \\times {i_a} \\times {l_m} = {f_n:.2f}\\ \\text{{N}}$.",
            "Students omit wire length or use $F = Bqv$ instead of $BIL$.",
            topic=TOPIC_B, outcome_code="B3.8k",
            skill_tested=f"Wire force B={b_t} T, I={i_a} A, L={l_m} m",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    b_final_mc = [
        ("A transformer changes voltage levels in AC circuits by",
         "electromagnetic induction between primary and secondary coils",
         ["converting AC to DC using a single diode only", "eliminating magnetic flux entirely", "increasing resistance without any coils"],
         "Changing flux in one coil induces emf in another — transformer principle.",
         "Students think transformers work on DC without flux change.",
         "B3.3sts", "Explaining transformer operation", "Medium", 75),
        ("Auroras near Earth's poles are associated with",
         "charged particles from the solar wind interacting with Earth's magnetic field",
         ["only visible light reflection from the Moon", "static charge on mountain peaks only", "gravitational waves from the Sun"],
         "Solar wind particles spiral along geomagnetic field lines and excite atmospheric atoms.",
         "Students think auroras are unrelated to magnetism.",
         "B3.2sts", "Explaining aurora mechanism", "Easy", 70),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in b_final_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_B, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Unit C: index of refraction from speeds (more)
    n_data = [
        (2.25e8, 1.33), (2.00e8, 1.50), (1.50e8, 2.00), (2.50e8, 1.20), (1.80e8, 1.67),
    ]
    for v_med, n_val in n_data:
        extra.append(nr(
            f"Light speed in a medium is ${v_med/1e8:.2f} \\times 10^8\\ \\text{{m/s}}$. "
            f"Calculate refractive index $n = c/v$ where $c = 3.00 \\times 10^8\\ \\text{{m/s}}$. "
            f"Record to two decimal places.",
            f"{n_val:.2f}",
            f"$n = 3.00\\times10^8 / {v_med:.2e} = {n_val:.2f}$.",
            "Students invert to $v/c$.",
            topic=TOPIC_C, outcome_code="C1.11k",
            skill_tested=f"Index of refraction from v={v_med/1e8:.2f}e8 m/s",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    c_final_mc = [
        ("X-rays occupy a region of the EM spectrum with",
         "higher photon energy and shorter wavelength than visible light",
         ["lower frequency than radio waves only", "the same wavelength as red light", "no wave properties"],
         "X-rays have shorter $\\lambda$ and higher $f$ than visible EMR.",
         "Students think all ionizing radiation is identical to visible light.",
         "C2.2k", "Classifying X-ray region of EM spectrum", "Easy", 55),
        ("LED technology for lighting is efficient because",
         "electrons recombine with holes releasing photons with minimal wasted heat",
         ["incandescent filaments are used inside every LED", "LEDs require no energy input", "LEDs emit only infrared radiation"],
         "LEDs convert electrical energy directly to photons via semiconductor transitions.",
         "Students think LEDs work like hot filament bulbs.",
         "C2.3sts", "Explaining LED efficiency advantage", "Easy", 65),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in c_final_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_C, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Unit D: photon energy from eV transition (emission)
    d_final_mc = [
        ("Isotopes of the same element differ in",
         "the number of neutrons in the nucleus",
         ["the number of protons in the nucleus", "the number of electrons in a neutral atom", "their chemical reactivity due to different protons"],
         "Isotopes share proton number (same element) but differ in neutron count.",
         "Students think isotopes differ in proton number.",
         "D3.4k", "Defining isotope difference", "Easy", 55),
        ("Positron emission tomography (PET) uses",
         "positron-emitting isotopes whose annihilation produces detectable gamma photons",
         ["only stable isotopes with no radiation", "gravitational waves from nuclei", "visible light lasers only"],
         "PET traces annihilation gamma pairs from beta-plus emitters.",
         "Students confuse PET with MRI or X-ray imaging.",
         "D3.2sts", "Describing PET imaging principle", "Medium", 85),
        ("The discovery of the neutron by Chadwick explained why",
         "atomic masses exceeded what could be accounted for by protons alone",
         ["atoms contain no positive charge", "electrons have the same mass as protons", "nuclei are empty space"],
         "Neutrons account for extra nuclear mass without adding positive charge.",
         "Students think neutrons were predicted before any mass discrepancy was known.",
         "D4.1sts", "Explaining significance of neutron discovery", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in d_final_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_D, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # More kinetic energy / momentum NR for unit A
    ke_mom_data = [
        (2.0, 3.0, 9.0), (0.5, 8.0, 16.0), (1.0, 6.0, 18.0), (3.0, 2.0, 6.0),
        (0.25, 12, 18.0), (4.0, 1.5, 4.5), (0.8, 5.0, 10.0), (1.5, 4.0, 12.0),
    ]
    for m, v, ke in ke_mom_data:
        extra.append(nr(
            f"A ${m}\\ \\text{{kg}}$ object moves at ${v}\\ \\text{{m/s}}$. "
            f"Calculate kinetic energy in joules. Record to one decimal place.",
            f"{ke:.1f}",
            f"$KE = \\frac{{1}}{{2}}mv^2 = 0.5 \\times {m} \\times {v}^2 = {ke}\\ \\text{{J}}$.",
            "Students omit the factor of $\\frac{1}{2}$.",
            topic=TOPIC_A, outcome_code="A1.5k",
            skill_tested=f"Kinetic energy for {m} kg at {v} m/s",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    # Closing batch — STS and skills MC
    closing_mc = [
        (TOPIC_A, "Crash-test dummies with instrumented accelerometers help engineers evaluate vehicle safety by measuring",
         "how quickly passenger momentum changes during simulated collisions",
         ["the colour of deployed airbags only", "nuclear decay rates in seat materials", "the index of refraction of windshield glass"],
         "Acceleration data reveals force and impulse experienced during impact.",
         "Students think dummies measure only visual damage.",
         "A1.1sts", "Relating crash testing to momentum change", "Easy", 70),
        (TOPIC_B, "Electrostatic precipitators in industrial smokestacks remove particulates by",
         "charging particles and attracting them to collector plates",
         ["heating smoke to plasma temperatures only", "using only gravitational settling", "eliminating all electric fields inside the stack"],
         "Charged dust particles migrate in engineered electric fields to plates.",
         "Students think precipitators work by filtration only without electrostatics.",
         "B2.1sts", "Describing electrostatic precipitator operation", "Medium", 80),
        (TOPIC_C, "Fibre optic communication uses total internal reflection so that",
         "light signals remain trapped inside the glass core with minimal loss",
         ["light escapes freely into the surrounding air", "only sound waves are transmitted", "signals travel faster than the speed of light in vacuum"],
         "Core-cladding index difference enables TIR guiding of optical signals.",
         "Students think fibre optics use simple straight-line beams through air gaps.",
         "C1.2sts", "Explaining fibre optic signal guiding", "Medium", 75),
        (TOPIC_D, "Medical imaging with radioactive tracers relies on detecting",
         "gamma radiation emitted from biologically targeted isotopes",
         ["only visible light from incandescent sources", "gravitational radiation from tissues", "sound waves reflected from bones exclusively"],
         "Gamma emitters allow external detection of tracer distribution.",
         "Students confuse nuclear medicine tracers with ultrasound imaging.",
         "D3.2sts", "Describing nuclear medicine tracer detection", "Medium", 80),
        (TOPIC_B, "Free-body diagrams for a positive charge in a uniform electric field should show",
         "an electric force arrow in the direction of the electric field",
         ["no forces because the charge is stationary only", "magnetic force always parallel to the field", "gravitational force dominating over any electric force"],
         "Positive test charge experiences force parallel to $\\vec{E}$.",
         "Students draw force opposite to field for positive charges.",
         "B2.3s", "Drawing free-body diagram for charge in E field", "Medium", 75),
        (TOPIC_C, "Measuring the focal length of a converging lens in the laboratory requires",
         "forming a real image on a screen and measuring object and image distances",
         ["only observing a virtual image without a screen", "measuring the mass of the lens", "using only a magnetic field probe"],
         "Real image formation allows direct measurement of $f$ using lens equation.",
         "Students try to measure focal length from virtual images alone.",
         "C1.2s", "Describing focal length measurement procedure", "Medium", 80),
    ]
    for topic, qt, ans, dist, expl, mis, oc, skill, diff, time in closing_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic=topic, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return extra


def validate_outcomes(items: list) -> list:
    warnings = []
    for item in items:
        topic = item["topic"]
        code = item["outcome_code"]
        valid = VALID_OUTCOMES.get(topic, set())
        if code not in valid:
            warnings.append(f"Unknown outcome {code} for topic {topic}")
    return warnings


def main():
    pool = []
    pool.extend(unit_a())
    pool.extend(unit_b())
    pool.extend(unit_c())
    pool.extend(unit_d())
    pool.extend(programmatic_supplements())

    before = len(pool)
    pool = deduplicate(pool)
    if len(pool) < before:
        print(f"Deduplicated: {before} -> {len(pool)}")

    ordered = [order_item(q) for q in pool]

    valid_count = 0
    invalid = []
    for i, q in enumerate(ordered):
        reasons = validate_question(q, i)
        if not reasons:
            valid_count += 1
        else:
            invalid.append((i, q.get("outcome_code"), reasons))

    outcome_warnings = validate_outcomes(ordered)

    mc_pos = assert_mc_position_balanced(ordered, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)

    topics = Counter(q["topic"] for q in ordered)
    types = Counter(q["question_type"] for q in ordered)
    diffs = Counter(q["difficulty"] for q in ordered)

    print(f"Wrote {len(ordered)} questions to {OUTPUT}")
    print(f"Validated: {valid_count}/{len(ordered)}")
    print(f"By topic: {dict(topics)}")
    print(f"By type: {dict(types)}")
    print(f"By difficulty: {dict(diffs)}")

    if invalid:
        print(f"\nInvalid ({len(invalid)}):")
        for idx, oc, reasons in invalid[:10]:
            print(f"  [{idx}] {oc}: {reasons}")
    if outcome_warnings:
        print(f"\nOutcome warnings ({len(outcome_warnings)}):")
        for w in outcome_warnings[:10]:
            print(f"  {w}")


if __name__ == "__main__":
    main()
