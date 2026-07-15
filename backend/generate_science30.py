"""Generate, validate, and export the Science 30 question pool (~450 questions)."""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from sci30_questions.helpers import mc, nr
from sci30_questions.expansion_pool import expansion
from sci30_questions.pool_qa import qa_fix_pool
from sci30_questions.unit_circulatory import questions as circulatory
from sci30_questions.unit_genetics import questions as genetics
from sci30_questions.unit_env_chem import questions as env_chem
from sci30_questions.unit_field import questions as field_theory
from sci30_questions.unit_emr import questions as emr
from sci30_questions.unit_energy import questions as energy

OUTPUT = Path(__file__).parent.parent / "questions.json" / "science30_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def programmatic_supplements() -> list[dict]:
    """Parameterized original questions to expand pool toward ~450."""
    extra = []

    # --- Circulatory & Immune supplements ---
    circ_mc = [
        ("The coronary arteries supply blood directly to the", "heart muscle (myocardium)", ["lungs for gas exchange", "brain exclusively", "skin surface only"], "Coronary circulation nourishes cardiac tissue itself.", "Pulmonary arteries serve lungs; coronary serves heart muscle.", "A1.1k", "Identifying coronary artery target tissue", "Easy", 60),
        ("Lymphocytes mature and differentiate primarily in", "bone marrow and lymphoid tissues such as the thymus", ["the left ventricle during systole", "red blood cell cytoplasm exclusively", "the alveoli of the lungs"], "B and T lymphocytes develop in bone marrow/thymus and secondary lymphoid organs.", "Cardiac chambers pump blood; they do not mature lymphocytes.", "A2.3k", "Identifying lymphocyte maturation sites", "Medium", 80),
        ("An elevated white blood cell count during infection suggests", "active immune response to pathogens", ["complete absence of any immune activity", "permanent loss of all red blood cells", "increased hemoglobin oxygen capacity only"], "Leukocytosis often indicates immune system activation against infection.", "High WBC indicates immune response, not its absence.", "A2.3k", "Interpreting elevated leukocyte count during infection", "Medium", 75),
        ("The vena cavae return blood to the", "right atrium of the heart", ["left ventricle directly", "pulmonary artery", "aorta before systemic circulation"], "Deoxygenated systemic blood enters right atrium via superior and inferior vena cavae.", "Oxygenated blood from lungs enters left atrium via pulmonary veins.", "A1.2k", "Tracing venous return pathway to heart", "Easy", 55),
        ("Histamine release during an allergic reaction contributes to", "increased capillary permeability and inflammation", ["permanent destruction of all red blood cells", "conversion of all T cells to platelets", "elimination of all antibodies from plasma"], "Histamine dilates vessels and increases permeability, causing swelling and redness.", "Allergic inflammation involves vessels, not cell lineage conversion.", "A2.3k", "Explaining histamine role in allergic inflammation", "Medium", 80),
        ("A double-blind drug trial design prevents", "bias from both participants and researchers knowing who receives treatment", ["all immune responses in every participant", "the heart from contracting during the study", "DNA replication in all body cells"], "Blinding reduces placebo and observer bias in clinical testing.", "Double-blind controls bias, not basic physiology.", "A2.1s", "Explaining double-blind experimental design purpose", "Medium", 85),
        ("Cholesterol deposits in arterial walls contribute to", "reduced blood flow and increased risk of cardiovascular events", ["increased oxygen-carrying capacity of blood", "faster nerve impulse conduction in axons", "complete immunity to all viral infections"], "Atherosclerotic plaque narrows arteries, restricting blood supply.", "Plaque reduces flow; it does not improve oxygen transport.", "A1.1sts", "Connecting arterial plaque to cardiovascular risk", "Medium", 80),
        ("Suppressor (regulatory) T cells function to", "reduce excessive immune responses and maintain self-tolerance", ["produce all hemoglobin in red blood cells", "pump blood through the pulmonary circuit", "generate all stomach acid in the gastric lumen"], "Regulatory T cells dampen immune activity to prevent overreaction and autoimmunity.", "Hemoglobin synthesis and digestion are unrelated to Treg function.", "A2.3k", "Describing regulatory T cell immune modulation role", "Hard", 95),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in circ_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Circulatory and Immune Systems",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    for hr_rest, hr_exercise in [(70, 140), (65, 130), (75, 150), (68, 136), (72, 144)]:
        increase = hr_exercise - hr_rest
        extra.append(nr(
            f"Resting heart rate is {hr_rest} bpm and increases to {hr_exercise} bpm during moderate exercise. "
            f"By how many beats per minute did heart rate increase?",
            str(increase),
            f"Increase = {hr_exercise} − {hr_rest} = {increase} bpm.",
            "Students report the exercise rate instead of the difference.",
            topic="Circulatory and Immune Systems", outcome_code="A1.2s",
            skill_tested="Calculating heart rate change during exercise",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # --- Genetics supplements ---
    for dominant_pct in [75, 50, 25]:
        extra.append(nr(
            f"In a large monohybrid cross with complete dominance, {dominant_pct}% of offspring "
            f"show the dominant phenotype. What percentage show the recessive phenotype?",
            str(100 - dominant_pct),
            f"Recessive phenotype = 100% − {dominant_pct}% = {100 - dominant_pct}%.",
            "Students add percentages instead of finding complement.",
            topic="Genetics and Molecular Biology", outcome_code="A3.2k",
            skill_tested="Calculating recessive phenotype percentage complement",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    gen_mc = [
        ("Transcription produces", "mRNA complementary to a DNA template strand", ["DNA from an mRNA template", "protein directly from ribosomal DNA", "lipid bilayers from amino acids"], "RNA polymerase builds mRNA using DNA template during transcription.", "Translation (not transcription) produces protein from mRNA.", "A3.6k", "Defining transcription product", "Easy", 60),
        ("A nonsense mutation introduces a", "stop codon that terminates translation early", ["permanent increase in chromosome number to 92", "change in blood type without any DNA change", "fusion of two different species' nuclei in the ribosome"], "Nonsense mutations create premature stop codons, truncating the polypeptide.", "Nonsense affects translation termination, not chromosome number.", "A3.8k", "Identifying nonsense mutation effect on translation", "Medium", 85),
        ("Polymerase chain reaction (PCR) technology amplifies", "specific DNA sequences using thermal cycling and primers", ["red blood cells in circulating blood", "AC voltage in household transformers", "acid deposition in rainfall samples directly"], "PCR exponentially copies target DNA regions in vitro.", "PCR is a DNA amplification technique, not cell or voltage amplification.", "A3.9k", "Describing PCR DNA amplification application", "Medium", 80),
        ("Colour blindness linked to X chromosome inheritance affects", "males more frequently than females in the population", ["females more frequently due to Y-linked inheritance", "all individuals equally regardless of sex chromosomes", "only individuals with trisomy 21 exclusively"], "X-linked recessive traits express more in males (XY) with one X allele.", "X-linked recessive is not Y-linked; males lack second X allele.", "A3.3k", "Applying X-linked inheritance frequency pattern", "Medium", 85),
        ("Telomeres at chromosome ends function to", "protect coding DNA from degradation during replication", ["code for hemoglobin protein directly", "produce hydrochloric acid in the stomach", "generate electrical current in neurons"], "Telomeres are protective repetitive sequences shortened with each division.", "Hemoglobin and acid production are unrelated to telomere function.", "A3.5k", "Describing telomere protective function during replication", "Hard", 95),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in gen_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Genetics and Molecular Biology",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Environmental Chemistry supplements ---
    for m_acid, vol_ml, m_base in [(0.10, 20.0, 0.10), (0.05, 40.0, 0.05), (0.20, 15.0, 0.20), (0.15, 25.0, 0.15)]:
        vol_l = vol_ml / 1000
        moles = m_acid * vol_l
        extra.append(nr(
            f"A {vol_ml:.0f} mL sample of {m_acid:.2f} mol/L monoprotic acid is titrated. "
            f"How many moles of acid are present? Express as a decimal to three decimal places.",
            f"{moles:.3f}",
            f"n = M × V = {m_acid:.2f} × {vol_l:.3f} = {moles:.3f} mol.",
            "Students forget to convert mL to L before multiplying.",
            topic="Environmental Chemistry", outcome_code="B1.3s",
            skill_tested="Calculating moles of acid from molarity and volume",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    chem_mc = [
        ("Nitric acid (HNO₃) contributes to acid deposition primarily as", "a strong acid formed when NOₓ reacts with atmospheric moisture", ["a weak base that neutralizes all soil acidity", "an organic pollutant that biomagnifies in fish only", "a CFC that destroys ozone without forming acids"], "NOₓ from combustion forms HNO₃ in atmosphere, lowering rain pH.", "HNO₃ is acidic; it does not neutralize soil or function as CFC.", "B1.8k", "Linking nitrogen oxides to nitric acid in acid deposition", "Medium", 80),
        ("Halogenated hydrocarbons such as CFCs are chemically stable because", "carbon-halogen bonds are strong and resist environmental breakdown", ["they ionize completely in water like HCl", "they contain no carbon atoms at all", "they react instantly with all ozone in one second globally"], "Strong C-Cl/C-F bonds cause persistence in environment.", "CFCs contain carbon; persistence means slow breakdown.", "B2.4k", "Explaining chemical stability of halogenated hydrocarbons", "Medium", 80),
        ("Activated charcoal filters remove some water pollutants by", "adsorbing organic molecules onto its high surface area", ["adding sulfur dioxide to increase acidity", "converting all dissolved salts to ozone gas", "increasing pH above 14 in all samples instantly"], "Adsorption traps contaminants on porous carbon surfaces.", "Charcoal filters adsorb; they do not add SO₂ or create ozone.", "B3.2k", "Describing activated carbon water filtration mechanism", "Medium", 75),
        ("Limestone (calcium carbonate) can neutralize acid deposition in lakes because it", "reacts with acid to form less acidic products", ["increases the concentration of sulfur dioxide dissolved", "prevents all carbon dioxide from dissolving in water", "converts all water to pure hydrochloric acid"], "CaCO₃ + acid → neutralization products raising pH.", "Limestone neutralizes acid; it does not produce HCl.", "B1.9k", "Explaining limestone neutralization of acidic water", "Medium", 80),
        ("The conjugate base of H₂SO₄ after one proton donation is", "HSO₄⁻", ["SO₄²⁻ (fully deprotonated sulfate ion)", "H₃SO₄⁺ (protonated sulfuric acid species)", "H₂ gas exclusively (not a conjugate base)"], "First proton loss from H₂SO₄ gives bisulfate ion HSO₄⁻.", "SO₄²⁻ is conjugate base after two proton losses.", "B1.1k", "Identifying conjugate base after single proton transfer", "Hard", 95),
        ("POPs (persistent organic pollutants) are regulated internationally because they", "remain in the environment and accumulate in organisms over time", ["dissolve instantly in water and disappear within minutes", "are essential nutrients required for all plant growth", "increase atmospheric oxygen to toxic levels for all humans"], "Persistence and bioaccumulation justify international restriction (e.g., Stockholm Convention).", "POPs persist; they are not nutrients or oxygen sources.", "B2.3k", "Explaining rationale for POP international regulation", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in chem_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Environmental Chemistry",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Field Theory supplements ---
    for p_kw, hours in [(1.5, 4), (2.0, 6), (0.8, 10), (3.0, 2), (1.2, 8)]:
        kwh = p_kw * hours
        extra.append(nr(
            f"An electric heater rated at {p_kw} kW operates for {hours} hours. "
            f"How many kilowatt-hours (kWh) of energy are consumed?",
            f"{kwh:.1f}" if kwh != int(kwh) else str(int(kwh)),
            f"E = P × t = {p_kw} kW × {hours} h = {kwh} kWh.",
            "Students divide power by time instead of multiplying.",
            topic="Field Theory and Electrical Energy", outcome_code="C1.7k",
            skill_tested="Calculating electrical energy consumption in kWh",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for vp, ip, turns_p in [(120, 2, 100), (240, 1, 200), (600, 5, 50)]:
        vs = round(vp * 0.1)  # step-down example
        is_val = round(ip * vp / vs, 1)
        extra.append(nr(
            f"A transformer has primary voltage {vp} V and current {ip} A. Secondary voltage is {vs} V. "
            f"Assuming ideal transformer (P_in = P_out), what is secondary current in amperes? "
            f"Express as a decimal to one decimal place.",
            f"{is_val:.1f}",
            f"P = V_p I_p = V_s I_s, so I_s = V_p I_p / V_s = {vp}×{ip}/{vs} = {is_val} A.",
            "Students use turns ratio instead of power conservation for current.",
            topic="Field Theory and Electrical Energy", outcome_code="C1.9k",
            skill_tested="Calculating transformer secondary current from power conservation",
            difficulty="Hard", estimated_time_seconds=115,
        ))

    field_mc = [
        ("Coulomb's law describes the force between two point charges as", "inversely proportional to the square of the distance between them", ["directly proportional to distance squared", "independent of charge magnitude", "equal to the gravitational force in all cases"], "F ∝ q₁q₂/r² for electrostatic force between point charges.", "Electrostatic force depends on charges and inverse square of distance.", "C1.2k", "Stating inverse-square relationship in Coulomb's law", "Medium", 85),
        ("A voltmeter is connected in parallel with a resistor because it", "measures potential difference without drawing significant current through the resistor branch", ["measures current through the resistor in series only", "increases resistance to infinity in the circuit", "converts AC to DC in all measurements"], "Voltmeters have high resistance and are placed in parallel across components.", "Ammeters are in series; voltmeters are in parallel.", "C1.2s", "Explaining voltmeter parallel connection principle", "Medium", 80),
        ("Electric potential energy stored in a capacitor depends on", "capacitance and the square of the voltage across it", ["only the colour of the dielectric material", "the speed of sound in the connecting wires", "the number of chromosomes in nearby cells"], "E = ½CV² for capacitor energy storage.", "Capacitor energy is electrical, not biological or acoustic.", "C1.6k", "Relating capacitor stored energy to voltage and capacitance", "Hard", 100),
        ("A step-up transformer increases voltage and", "decreases current proportionally (in ideal case) to conserve power", ["increases current by the same factor as voltage", "eliminates all electrical resistance in the circuit", "converts all electrical energy to gravitational energy"], "Ideal transformer: V_s/V_p = N_s/N_p and I_s/I_p = N_p/N_s.", "Step-up increases V but decreases I for power conservation.", "C1.9k", "Describing current change in step-up transformer", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in field_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Field Theory and Electrical Energy",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- EMR supplements ---
    for wavelength_nm in [450, 650]:
        f = 3e8 / (wavelength_nm * 1e-9)
        extra.append(mc(
            f"Visible light with wavelength {wavelength_nm} nm in vacuum has frequency closest to",
            f"{f:.1e} Hz",
            [f"{f*10:.1e} Hz (ten times too high)", f"{f/10:.1e} Hz (ten times too low)", f"{f*100:.1e} Hz (one hundred times too high)"],
            f"f = c/λ = 3.0×10⁸/({wavelength_nm}×10⁻⁹) ≈ {f:.1e} Hz.",
            "Students multiply c×λ instead of dividing c by λ.",
            topic="Electromagnetic Spectrum", outcome_code="C2.6k",
            skill_tested="Estimating visible light frequency from wavelength",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    emr_mc = [
        ("Ultraviolet radiation is more likely than visible light to cause skin damage because it", "carries higher energy per photon capable of damaging DNA", ["has longer wavelength and lower frequency always", "travels slower than visible light in vacuum", "cannot be absorbed by any biological molecule"], "Higher-frequency UV photons have enough energy to cause molecular damage.", "UV has shorter λ and higher f than visible light.", "C2.2k", "Explaining UV biological damage via photon energy", "Medium", 80),
        ("Total internal reflection in optical fibres requires light to hit the boundary at an angle", "greater than the critical angle from the denser medium", ["less than the critical angle from the less dense medium always", "exactly equal to 0° in all circumstances", "of exactly 90° from the normal in air only"], "TIR occurs when angle in denser medium exceeds critical angle.", "TIR requires angle > critical angle in optically denser medium.", "C2.4k", "Stating condition for total internal reflection", "Hard", 100),
        ("A neutron star forms when a massive star collapses after a supernova, leaving a remnant that is", "extremely dense with roughly solar mass in city-sized volume", ["identical in size to the original main-sequence star", "composed entirely of liquid water at room temperature", "unable to produce any gravitational field"], "Neutron stars are compact remnants with extraordinary density.", "Neutron stars are tiny and dense, not Sun-sized water bodies.", "C2.11k", "Describing neutron star formation and density", "Hard", 105),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in emr_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Electromagnetic Spectrum",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Energy supplements ---
    for coal_mw, hours in [(500, 24), (800, 12), (300, 48), (600, 8)]:
        mwh = coal_mw * hours / 1000 if coal_mw * hours >= 1000 else coal_mw * hours
        # Actually MWh = MW * hours directly
        mwh = coal_mw * hours
        extra.append(nr(
            f"A coal power plant produces {coal_mw} MW of electrical power continuously for {hours} hours. "
            f"How many megawatt-hours (MWh) of energy are generated?",
            str(mwh),
            f"Energy = Power × time = {coal_mw} MW × {hours} h = {mwh} MWh.",
            "Students divide MW by hours instead of multiplying.",
            topic="Energy and the Environment", outcome_code="D2.10k",
            skill_tested="Calculating electrical energy output in MWh",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for protons, neutrons in [(92, 146), (94, 150), (90, 144)]:
        mass_num = protons + neutrons
        extra.append(nr(
            f"A uranium isotope has {protons} protons and {neutrons} neutrons in each nucleus. "
            f"What is the mass number A?",
            str(mass_num),
            f"A = protons + neutrons = {protons} + {neutrons} = {mass_num}.",
            "Students report only proton number (atomic number Z) instead of mass number.",
            topic="Energy and the Environment", outcome_code="D2.5k",
            skill_tested="Calculating nuclear mass number from nucleon count",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    energy_mc = [
        ("Carbon capture and storage (CCS) technology aims to", "trap CO₂ emissions before release and store them underground", ["increase sulfur dioxide emissions from coal plants", "convert all CO₂ to stratospheric ozone instantly", "eliminate the need for any energy input in society"], "CCS reduces atmospheric CO₂ from fossil fuel combustion sources.", "CCS addresses CO₂, not SO₂ increase or zero energy needs.", "D1.5k", "Describing carbon capture and storage purpose", "Medium", 80),
        ("Net metering for residential solar panels allows homeowners to", "receive credit for excess electricity fed back to the grid", ["eliminate all nighttime electricity use without any storage", "produce nuclear fusion in rooftop panels", "block all AC current from reaching the neighbourhood transformer"], "Net metering compensates prosumers for surplus generation.", "Solar panels do not produce fusion or block grid AC.", "D2.4k", "Explaining net metering for residential solar systems", "Medium", 75),
        ("Peak oil theory suggests that global petroleum production will eventually", "reach a maximum and then decline as reserves deplete", ["increase exponentially forever without limit", "be replaced instantly by cold fusion in all vehicles", "have no connection to energy policy or economics"], "Finite fossil reserves imply production peak then decline.", "Petroleum is finite; production cannot grow forever.", "D1.1k", "Describing peak oil production concept", "Medium", 80),
        ("Waste-energy recovery in industrial plants captures", "thermal energy from exhaust or processes for additional useful work", ["all radioactive waste from nuclear reactors for household use", "visible light from the Sun for nighttime illumination only", "genetic information from bacterial plasmids for fuel"], "Industrial waste heat can generate electricity or process heat.", "Waste-energy recovery is thermal, not genetic or purely solar.", "D1.3k", "Defining industrial waste-energy recovery", "Medium", 75),
        ("Life-cycle analysis of an energy technology evaluates", "environmental impacts from resource extraction through disposal", ["only the colour of the equipment housing", "the speed of nerve impulses in the human brain", "acid-base conjugate pairs in a single titration only"], "LCA considers full cradle-to-grave environmental footprint.", "LCA is comprehensive environmental accounting, not single parameters.", "D2.1sts", "Defining life-cycle environmental analysis for energy tech", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in energy_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Energy and the Environment",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Large batch: cross-topic MC for breadth ---
    breadth = [
        ("Circulatory and Immune Systems", "A1.4k", "Easy",
         "Which plasma protein is primarily responsible for blood clotting cascade activation?",
         "fibrinogen (converted to fibrin)", ["hemoglobin for oxygen transport", "albumin for osmotic pressure only", "antibodies for all clotting reactions"],
         "Fibrinogen is cleaved to fibrin, forming the structural mesh of a blood clot.",
         "Students confuse clotting proteins with oxygen-carrying hemoglobin or antibodies."),
        ("Circulatory and Immune Systems", "A2.1k", "Medium",
         "A pathogen entering through a break in the skin bypasses which first-line defence?",
         "intact epidermal barrier", ["adaptive antibody memory response", "complement cascade in blood only", "red blood cell hemoglobin binding"],
         "Broken skin removes the physical epidermal barrier, a primary non-specific defence.",
         "Students name adaptive immunity mechanisms that act after barrier breach."),
        ("Genetics and Molecular Biology", "A3.4k", "Easy",
         "The sugar in DNA nucleotides is",
         "deoxyribose", ["ribose as in RNA nucleotides", "glucose from cellular respiration", "fructose from fruit metabolism"],
         "DNA contains deoxyribose (lacking 2'-OH); RNA contains ribose.",
         "Students confuse deoxyribose (DNA) with ribose (RNA)."),
        ("Genetics and Molecular Biology", "A3.10k", "Hard",
         "Transformation in bacteria allows",
         "uptake of foreign DNA from the environment into bacterial cells",
         ["conversion of all glucose to ATP without DNA involvement", "permanent change in blood type without any genetic material", "elimination of all plasmids from every bacterial species globally"],
         "Competent bacteria can absorb naked DNA from surroundings, incorporating new genes.",
         "Students confuse bacterial transformation with metabolism or human blood typing."),
        ("Environmental Chemistry", "B1.7k", "Medium",
         "Soil with high buffering capacity can",
         "resist large changes in pH when acid or base is added",
         ["never interact with any acid or base ever", "instantly convert all rain to pH 14", "prevent all plant growth regardless of nutrients"],
         "Buffered soil contains compounds that neutralize added acid or base, stabilizing pH.",
         "Students think buffering means no chemical interaction or forced extreme pH."),
        ("Environmental Chemistry", "B2.5k", "Medium",
         "The Antarctic ozone hole forms seasonally because",
         "unique atmospheric conditions allow chlorine catalytic cycles to destroy O₃",
         ["CFCs are produced only in the Southern Ocean", "sulfur dioxide is absent from all polar air", "visible light cannot reach the stratosphere in winter"],
         "Polar stratospheric clouds enable chlorine catalysis that destroys ozone each spring.",
         "Students attribute the ozone hole to ocean CFC production or tropospheric SO₂."),
        ("Field Theory and Electrical Energy", "C1.8k", "Easy",
         "In a DC circuit, conventional current direction is defined as",
         "flow from positive terminal to negative terminal through external circuit",
         ["flow of electrons from positive to negative by definition", "random oscillation with no defined direction", "flow only through the battery's internal electrolyte externally"],
         "Conventional current flows from + to − externally; electrons actually flow opposite.",
         "Students equate conventional current with electron flow direction."),
        ("Field Theory and Electrical Energy", "C1.11k", "Medium",
         "In a simple DC motor, the commutator functions to",
         "reverse current direction in the coil every half rotation",
         ["step up voltage using a turns ratio", "measure resistance without any current flow", "store electrical energy as gravitational potential"],
         "The commutator swaps coil connections each half turn to maintain continuous torque.",
         "Students confuse commutator function with transformer or energy storage."),
        ("Electromagnetic Spectrum", "C2.5k", "Medium",
         "When visible light enters glass from air, its speed",
         "decreases while frequency remains constant",
         ["increases above the speed of light in vacuum", "becomes zero at all wavelengths simultaneously", "changes frequency to match the speed of sound"],
         "Light slows in denser medium (glass) but frequency stays the same; wavelength shortens.",
         "Students think speed increases in glass or that frequency must change with speed."),
        ("Electromagnetic Spectrum", "C2.10k", "Hard",
         "Blue-shifted light from an approaching star indicates the star is",
         "moving toward the observer",
         ["moving away at high speed", "stationary with no relative motion", "emitting only radio waves with no visible spectrum"],
         "Approach compresses wavelengths (blue shift); recession stretches them (red shift).",
         "Students reverse Doppler shift direction or confuse with emission type."),
        ("Energy and the Environment", "D2.3k", "Medium",
         "Most energy in a typical coal-fired plant's fuel is lost as",
         "waste heat to the environment during electricity generation",
         ["visible light emitted to power all nearby homes without loss", "gravitational potential energy stored in the smokestack permanently", "genetic information transferred to bacterial plasmids"],
         "Thermodynamic limits mean much fuel energy becomes low-grade waste heat, not electricity.",
         "Students think all fuel energy becomes usable electricity without thermal loss."),
        ("Energy and the Environment", "D1.6k", "Medium",
         "Indigenous perspectives on environmental interconnectedness emphasize",
         "balancing resource use with long-term ecosystem health",
         ["unlimited extraction without any consequences", "complete separation of human activity from all natural systems", "exclusive reliance on non-renewable fossil fuels indefinitely"],
         "Interconnectedness requires sustainable resource use respecting ecological relationships.",
         "Students think Indigenous perspectives advocate unlimited extraction or fossil reliance."),
    ]
    for topic, oc, diff, qtext, ans, dist, expl, mis in breadth:
        extra.append(mc(
            qtext, ans, dist, expl, mis,
            topic=topic, outcome_code=oc,
            skill_tested=f"Applying {oc} concept in {topic}",
            difficulty=diff, estimated_time_seconds=75,
        ))

    # --- Additional parameterized NR batches ---
    for v1, v2, v3 in [(6, 6, 6), (10, 20, 30)]:
        rt = v1 + v2 + v3
        extra.append(nr(
            f"Three resistors ({v1} Ω, {v2} Ω, and {v3} Ω) are wired in series across a battery. "
            f"What is the total resistance in ohms?",
            str(rt),
            f"Series total = {v1} + {v2} + {v3} = {rt} Ω.",
            "Students use parallel formula for a series circuit.",
            topic="Field Theory and Electrical Energy", outcome_code="C1.6k",
            skill_tested="Calculating total resistance for three-resistor series circuit",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for p_percent in [25, 50, 75]:
        p_val = p_percent / 100
        q_val = round(1 - p_val, 2)
        q_prob = round(p_val ** 2, 2)
        extra.append(nr(
            f"In a Hardy-Weinberg population, {p_percent}% of alleles for a trait are dominant (A). "
            f"Assuming p = {p_val:.2f} and q = {q_val:.2f}, what is the expected "
            f"frequency of genotype AA? Express as a decimal to two decimal places.",
            f"{q_prob:.2f}",
            f"p = {p_val:.2f}, q = {q_val:.2f}. AA frequency = p² = {q_prob:.2f}.",
            "Students calculate 2pq (heterozygote) instead of p².",
            topic="Genetics and Molecular Biology", outcome_code="A3.2k",
            skill_tested="Calculating homozygous dominant frequency from allele percentage",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    return extra


def programmatic_supplements_batch2() -> list[dict]:
    """Second expansion batch to reach ~450 pool questions."""
    extra = []

    # --- Genetics: more Punnett and molecular MC ---
    gen_crosses = [
        ("BB", "bb", "100%", "all offspring heterozygous (Bb)",
         ["0% (no heterozygous offspring)", "25% (one-in-four heterozygous ratio)", "50% (half heterozygous ratio)"],
         "BB × bb produces all Bb offspring; 100% are heterozygous.",
         "Students think recessive bb parent produces homozygous dominant offspring."),
        ("Bb", "bb", "50%", "heterozygous (Bb)",
         ["0% (no heterozygous offspring)", "100% (all offspring heterozygous)", "25% (one-in-four heterozygous ratio)"],
         "Bb × bb gives 50% Bb and 50% bb; half are heterozygous.",
         "Students report 100% heterozygous instead of 50% for this test cross."),
        ("Aa", "AA", "50%", "homozygous dominant (AA)",
         ["0% (no homozygous dominant offspring)", "100% (all offspring homozygous dominant)", "25% (one-in-four homozygous dominant ratio)"],
         "Aa × AA produces 50% AA and 50% Aa; half are homozygous dominant.",
         "Students confuse heterozygous (Aa) fraction with homozygous dominant (AA) fraction."),
    ]
    for p1, p2, ans, desc, dist, expl, mis in gen_crosses:
        extra.append(mc(
            f"In a monohybrid cross {p1} × {p2} with complete dominance, what percentage of offspring are {desc}?",
            ans, dist, expl, mis,
            topic="Genetics and Molecular Biology", outcome_code="A3.2k",
            skill_tested=f"Calculating offspring percentage for {p1} x {p2} cross",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    gen_mc2 = [
        ("Ribosomes are the site of", "translation of mRNA into polypeptide chains",
         ["DNA replication in the nucleus", "photosynthesis in chloroplasts", "blood clotting in plasma"],
         "Ribosomes read mRNA codons and assemble amino acids into polypeptide chains during translation.",
         "Students confuse translation (protein synthesis) with transcription (mRNA synthesis) or DNA replication.",
         "A3.6k", "Identifying ribosome function in protein synthesis", "Medium", 80),
        ("A deletion mutation removes", "one or more nucleotides from the DNA sequence",
         ["only the cell membrane from the cell", "all chromosomes simultaneously", "the entire circulatory system from the body"],
         "Deletion mutations lose nucleotides, potentially shifting the reading frame downstream.",
         "Students confuse deletion (lost bases) with substitution (one base replaced).",
         "A3.8k", "Defining deletion mutation", "Medium", 80),
        ("Sex-linked recessive traits appear more often in males because", "males have only one X chromosome and express any recessive allele on it",
         ["males have two X chromosomes always", "the Y chromosome carries all recessive alleles for every trait", "females cannot inherit X-linked alleles from fathers"],
         "Males (XY) lack a second X allele to mask recessive traits present on their single X chromosome.",
         "Students incorrectly assume females cannot inherit or express X-linked alleles.",
         "A3.3k", "Explaining male prevalence of X-linked recessive traits", "Medium", 85),
        ("Recombinant DNA technology involves", "combining DNA from different sources into the same molecule",
         ["only selective breeding without DNA manipulation", "converting all proteins to DNA without enzymes", "eliminating all genes from an organism"],
         "Recombinant DNA joins genetic material from different organisms using restriction enzymes and ligases.",
         "Students confuse genetic engineering (DNA manipulation) with traditional selective breeding alone.",
         "A3.9k", "Defining recombinant DNA technology", "Medium", 80),
        ("The Human Genome Project aimed to", "map and sequence the entire human genetic code",
         ["eliminate all mutations from every human cell", "replace all blood cells with synthetic platelets", "measure only the pH of human blood plasma"],
         "The international project determined the nucleotide sequence of the human genome for research and medicine.",
         "Students confuse genome sequencing with eliminating mutations or unrelated physiology.",
         "A3.1sts", "Describing Human Genome Project goal", "Medium", 80),
        ("Antibiotic overuse in agriculture can accelerate", "selection for resistant bacterial populations",
         ["complete elimination of all bacteria globally", "permanent immunity in all humans to all diseases", "conversion of viruses to multicellular plants"],
         "Constant antibiotic exposure selects bacteria with resistance alleles, increasing resistant population frequency.",
         "Students think antibiotics eliminate all bacteria rather than selecting resistant survivors.",
         "A3.10k", "Linking antibiotic overuse to natural selection in bacteria", "Medium", 85),
        ("Mitosis produces daughter cells that are", "genetically identical to the parent cell",
         ["haploid with half the chromosome number always", "always four cells each with quarter the DNA", "completely unrelated genetically to the parent"],
         "Mitosis duplicates and distributes identical chromosome sets to two diploid daughter cells.",
         "Students confuse mitosis (identical diploid cells) with meiosis (haploid genetically varied gametes).",
         "A3.1k", "Describing mitosis daughter cell genetic identity", "Easy", 70),
        ("Meiosis in germ cells produces", "haploid gametes with genetic variation",
         ["diploid somatic cells identical to parent", "only red blood cells for circulation", "platelets for blood clotting exclusively"],
         "Meiosis halves chromosome number and recombines alleles to form genetically unique haploid gametes.",
         "Students confuse meiosis in germ cells with mitosis in somatic cells.",
         "A3.1k", "Describing meiosis gamete products", "Medium", 80),
        ("A carrier of a recessive genetic disorder is typically", "heterozygous and does not show the disorder phenotype",
         ["homozygous dominant with severe symptoms always", "missing all chromosomes in every cell", "unable to pass any alleles to offspring"],
         "Carriers (Aa) possess one recessive allele but express the dominant phenotype with complete dominance.",
         "Students think carriers must show disease symptoms or cannot transmit the allele.",
         "A3.2k", "Defining genetic carrier status", "Medium", 80),
        ("Epigenetic changes can alter gene expression without changing", "the DNA nucleotide sequence",
         ["the number of protons in atomic nuclei", "the speed of light in a vacuum", "the gravitational field around Earth"],
         "Epigenetic mechanisms (e.g., methylation) regulate gene activity while the base sequence stays unchanged.",
         "Students confuse epigenetic regulation with mutations that alter DNA nucleotide sequences.",
         "A3.8k", "Distinguishing epigenetic from sequence change", "Hard", 90),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in gen_mc2:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Genetics and Molecular Biology",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Environmental Chemistry expansion ---
    for ph_val in [1, 3, 5]:
        h = 10 ** (-ph_val)
        extra.append(nr(
            f"A laboratory acid sample has pH {ph_val}. What is [H₃O⁺] in mol/L? "
            f"Express in scientific notation with one digit before the decimal.",
            f"{h:.1e}",
            f"[H₃O⁺] = 10^(−{ph_val}) = {h:.1e} mol/L.",
            "Students report pH value as concentration.",
            topic="Environmental Chemistry", outcome_code="B1.3s",
            skill_tested="Converting pH to hydronium ion concentration",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    chem_mc2 = [
        ("Acid deposition can accelerate corrosion of metal structures because", "lowered pH increases chemical attack on metals",
         ["it raises pH above 14 on all metals", "it eliminates all oxygen from the atmosphere", "it converts iron to pure gold instantly"],
         "Acidic rainwater and dry deposition chemically attack metal surfaces, speeding oxidation and corrosion.",
         "Students think acid deposition raises pH or has no effect on metals.",
         "B1.9k", "Explaining acid deposition effect on metal corrosion", "Medium", 80),
        ("A conjugate acid-base pair differs by", "one proton (H⁺)",
         ["one neutron in the nucleus", "one entire chromosome", "one glucose molecule in solution"],
         "Conjugate pairs are related by transfer of a single H⁺ (e.g., H₂CO₃/HCO₃⁻).",
         "Students confuse proton transfer with nuclear or unrelated molecular changes.",
         "B1.1k", "Defining conjugate acid-base pair relationship", "Medium", 75),
        ("Weak bases such as ammonia (NH₃) accept protons to form", "NH₄⁺ (ammonium ion)",
         ["HCl gas exclusively", "pure water with no ions", "sulfur dioxide gas only"],
         "NH₃ + H⁺ → NH₄⁺; ammonia acts as a proton acceptor (base) in this reaction.",
         "Students cannot identify the protonated product of a weak base.",
         "B1.1k", "Identifying ammonium ion as protonated ammonia", "Medium", 75),
        ("Halogenated organic compounds persist in the environment because", "carbon-halogen bonds resist degradation",
         ["they dissolve instantly in all water bodies", "they are required vitamins for all mammals", "they increase atmospheric ozone uniformly"],
         "Strong C-X bonds make halogenated organics resistant to bacterial and chemical breakdown.",
         "Students think all organic compounds biodegrade rapidly in the environment.",
         "B2.4k", "Explaining persistence of halogenated organics", "Medium", 80),
        ("Eutrophication of lakes is accelerated when", "excess nutrients cause algal blooms depleting oxygen",
         ["all dissolved salts are removed from water", "pH is raised above 14 permanently", "all fish migrate to the stratosphere"],
         "Nutrient runoff fuels algal overgrowth; decomposition depletes dissolved oxygen, harming aquatic life.",
         "Students confuse eutrophication with acidification or salinity changes.",
         "B3.3s", "Explaining eutrophication mechanism in lakes", "Medium", 85),
        ("The greenhouse effect differs from ozone depletion because", "greenhouse effect traps infrared radiation while ozone depletion increases UV at surface",
         ["they are identical processes with the same cause", "greenhouse effect only occurs in laboratory glassware", "ozone depletion only affects ocean salinity"],
         "Greenhouse gases trap IR heat; ozone loss allows more harmful UV to reach Earth's surface.",
         "Students conflate climate change (greenhouse) with ozone hole (CFC) mechanisms.",
         "B1.2sts", "Distinguishing greenhouse effect from ozone depletion", "Medium", 85),
        ("Industrial scrubbers use alkaline solutions primarily to", "neutralize acidic gases in exhaust streams",
         ["increase SO₂ emissions deliberately", "convert all CO₂ to solid diamond instantly", "eliminate all nitrogen from the atmosphere"],
         "Scrubbers spray base solution to remove acidic gases like SO₂ from industrial exhaust.",
         "Students think scrubbers increase emissions rather than reduce acidic pollutants.",
         "B3.2k", "Describing industrial scrubber neutralization function", "Medium", 75),
        ("Biodiesel produced from plant oils is classified as", "a renewable biofuel when sourced sustainably",
         ["a non-renewable fossil fuel identical to coal", "a CFC that destroys ozone rapidly", "a strong acid with pH below zero"],
         "Plant-based biodiesel can be renewable if feedstock is regrown sustainably.",
         "Students classify all liquid fuels as non-renewable fossil fuels.",
         "B2.2k", "Classifying biodiesel as renewable biofuel", "Medium", 75),
        ("Water hardness from dissolved Ca²⁺ and Mg²⁺ can be reduced by", "ion exchange or adding washing soda (sodium carbonate)",
         ["adding concentrated sulfuric acid to all water", "removing all dissolved oxygen from the sample", "converting all water to solid ice permanently"],
         "Ion exchange replaces Ca²⁺/Mg²⁺ ions; sodium carbonate precipitates hardness ions.",
         "Students propose acid addition which does not remove hardness ions effectively.",
         "B3.3s", "Identifying water softening methods", "Medium", 80),
        ("Risk-benefit analysis of pesticide application weighs", "crop protection benefits against ecological and health risks",
         ["only the colour of the spray equipment", "the speed of nerve impulses in earthworms only", "motor design in electric generators exclusively"],
         "STS analysis balances agricultural gains against environmental persistence and health effects.",
         "Students treat risk-benefit as a single-factor or unrelated physical measurement.",
         "B3.1sts", "Applying risk-benefit analysis to pesticide use", "Medium", 90),
        ("Sulfuric acid in acid deposition forms when", "SO₂ oxidizes and dissolves in atmospheric moisture",
         ["all nitrogen is removed from the air first", "ozone reacts with iron in the troposphere only", "methane combusts without any oxygen present"],
         "SO₂ → SO₃ → H₂SO₄ in atmospheric moisture contributes to acid deposition.",
         "Students confuse sulfuric acid formation with unrelated atmospheric processes.",
         "B1.8k", "Describing sulfuric acid formation in atmosphere", "Medium", 80),
        ("An alkaline solution has pH", "greater than 7",
         ["exactly 7 always", "less than 0 in all cases", "equal to the hydronium concentration numerically"],
         "Alkaline (basic) solutions have pH > 7 on the logarithmic pH scale.",
         "Students think alkaline means pH below 7 or confuse pH with concentration numerically.",
         "B1.3k", "Defining alkaline solution pH range", "Easy", 60),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in chem_mc2:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Environmental Chemistry",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Energy expansion ---
    for input_kj, output_kj in [(5000, 1750), (8000, 2800), (3000, 1050)]:
        eff = round(100 * output_kj / input_kj, 1)
        extra.append(nr(
            f"A power plant consumes {input_kj} kJ of fuel energy and delivers {output_kj} kJ as electrical output. "
            f"What is the plant efficiency in percent? Express to one decimal place.",
            f"{eff:.1f}",
            f"Efficiency = ({output_kj}/{input_kj}) × 100% = {eff}%.",
            "Students invert the efficiency ratio.",
            topic="Energy and the Environment", outcome_code="D2.3s",
            skill_tested="Calculating power plant energy conversion efficiency",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for mass_g, energy_mj in [(1, 90), (2, 180)]:
        extra.append(nr(
            f"Complete fission of {mass_g} g of nuclear fuel releases {energy_mj} MJ of energy. "
            f"How many MJ are released per gram? Express as a decimal.",
            str(int(energy_mj / mass_g)),
            f"Energy per gram = {energy_mj}/{mass_g} = {int(energy_mj/mass_g)} MJ/g.",
            "Students multiply mass by energy instead of dividing.",
            topic="Energy and the Environment", outcome_code="D2.11k",
            skill_tested="Calculating specific energy release per unit mass",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    energy_mc2 = [
        ("Fracking (hydraulic fracturing) for natural gas raises concerns about", "groundwater contamination and induced seismicity",
         ["complete elimination of all natural gas reserves in one day", "permanent cooling of Earth's core", "conversion of all wind to nuclear energy instantly"],
         "Fracturing fluid and methane migration can contaminate aquifers; injection can trigger small earthquakes.",
         "Students dismiss fracking risks or confuse them with unrelated energy conversions.",
         "D1.5k", "Evaluating fracking environmental risks", "Medium", 85),
        ("A hybrid electric vehicle improves fuel efficiency by", "using electric motor assist to reduce gasoline consumption",
         ["eliminating the need for any energy storage", "converting all motion to nuclear fusion in the cabin", "blocking all electromagnetic radiation from the engine"],
         "Regenerative braking and electric assist reduce gasoline use in hybrid drivetrains.",
         "Students think hybrids need no battery or involve nuclear processes.",
         "D1.3k", "Explaining hybrid vehicle efficiency improvement", "Medium", 80),
        ("Tidal energy is most viable in locations with", "large tidal range and suitable coastal geography",
         ["no water access and desert climate only", "permanent ice cover preventing any liquid water", "constant wind speeds above 200 m/s"],
         "Large tidal ranges (e.g., Bay of Fundy) provide sufficient head for tidal turbine installations.",
         "Students think tidal power works without water or extreme unrelated conditions.",
         "D2.12k", "Identifying geographic requirements for tidal energy", "Medium", 80),
        ("Solar thermal power plants use mirrors or lenses to", "concentrate sunlight to heat a fluid driving a turbine",
         ["absorb all carbon dioxide from the atmosphere directly", "produce nuclear fission in the reflector panels", "eliminate all infrared radiation from the Sun"],
         "Concentrated solar thermal (CSP) systems heat transfer fluid to generate steam for electricity.",
         "Students confuse solar thermal with photovoltaic or nuclear energy.",
         "D2.4k", "Describing concentrated solar thermal electricity generation", "Medium", 80),
        ("Energy density of fossil fuels is generally", "higher than most batteries per unit mass",
         ["lower than a fully charged AA battery always", "equal to zero for all hydrocarbons", "identical to gravitational potential energy of water only"],
         "Hydrocarbons store large chemical energy per kilogram compared to current battery technology.",
         "Students overstate battery energy density relative to fossil fuels.",
         "D2.11k", "Comparing fossil fuel and battery energy density", "Medium", 85),
        ("The Paris Agreement international framework addresses", "reducing greenhouse gas emissions through national commitments",
         ["eliminating all science education globally", "mandating only coal power in all nations", "preventing all use of renewable energy sources"],
         "Countries pledged nationally determined contributions to limit global temperature rise.",
         "Students think the agreement bans renewables or mandates coal exclusively.",
         "D1.1sts", "Describing Paris Agreement emissions framework", "Medium", 80),
        ("Smog in urban areas often results from", "reactions between NOₓ, VOCs, and sunlight",
         ["complete absence of any combustion processes", "only natural volcanic ash with no human activity", "excessive dissolved oxygen in rainwater only"],
         "Photochemical smog forms when sunlight drives reactions between vehicle/industrial pollutants.",
         "Students attribute smog only to natural sources or unrelated water chemistry.",
         "D1.5k", "Explaining photochemical smog formation", "Medium", 80),
        ("Energy conservation in buildings can be improved by", "improving insulation and using efficient appliances",
         ["removing all windows and ventilation permanently", "burning all waste indoors for heat without ventilation", "using only incandescent bulbs at maximum wattage always"],
         "Better insulation and efficient devices reduce heating, cooling, and electrical demand.",
         "Students propose unsafe or counterproductive conservation measures.",
         "D1.3k", "Identifying building energy conservation strategies", "Easy", 70),
        ("Uranium-235 fission in reactors is initiated by", "absorption of a slow (thermal) neutron by the U-235 nucleus",
         ["direct exposure to visible light only", "combustion with oxygen in open air like coal", "mixing with hydrochloric acid in the reactor pool"],
         "Thermal neutrons trigger U-235 fission chain reactions in moderated reactor cores.",
         "Students confuse nuclear fission with chemical combustion or photochemical processes.",
         "D2.8k", "Describing neutron-induced U-235 fission initiation", "Medium", 85),
        ("Wind power variability can be addressed by", "grid integration, storage, and geographic distribution of turbines",
         ["eliminating all weather forecasting technology", "using only a single turbine for an entire country", "converting all wind to acid deposition"],
         "Diversified sites, forecasting, and storage smooth variable wind output on the grid.",
         "Students think a single turbine or unrelated chemistry solves variability.",
         "D2.4k", "Evaluating solutions to wind power intermittency", "Medium", 80),
        ("Geothermal power plants in Iceland benefit from", "accessible geothermal reservoirs near tectonic activity",
         ["permanent sunlight 24 hours per day year-round", "absence of any water or steam sources underground", "direct solar panels installed inside the magma chamber"],
         "Volcanic tectonic activity provides accessible hot water/steam reservoirs for geothermal plants.",
         "Students confuse geothermal (Earth's internal heat) with direct solar radiation.",
         "D2.4k", "Explaining Iceland geothermal resource advantage", "Medium", 85),
        ("Ethanol blended with gasoline (gasohol) aims to", "reduce fossil fuel consumption and support agricultural sectors",
         ["eliminate all carbon emissions from vehicles completely", "increase lead additives to fuel for better octane", "replace all engine lubricants with pure water"],
         "Ethanol from biomass partially displaces gasoline but still produces CO₂ when burned.",
         "Students think bioethanol is carbon-free or replaces engine lubricants.",
         "D2.3k", "Evaluating gasohol fuel blend purpose", "Medium", 80),
        ("Small modular nuclear reactors (SMRs) are proposed to", "provide scalable lower-capital nuclear power options",
         ["replace all personal vehicles with nuclear engines", "eliminate all radioactive isotopes from nature", "generate electricity only from visible light reflection"],
         "SMRs offer factory-built modular designs with potentially lower upfront costs than large reactors.",
         "Students confuse SMRs with vehicle engines or non-nuclear energy sources.",
         "D2.8k", "Describing small modular reactor proposal", "Medium", 80),
        ("An energy audit of a home identifies", "areas of energy waste and opportunities for efficiency improvements",
         ["only the genetic code of the residents", "the speed of blood flow through capillaries", "acid-base conjugate pairs in rainwater exclusively"],
         "Audits assess insulation, appliances, and usage patterns to recommend efficiency upgrades.",
         "Students confuse energy audits with unrelated biological or chemistry measurements.",
         "D1.3k", "Defining residential energy audit purpose", "Easy", 65),
        ("Carbon-neutral biomass energy claims depend on", "sustainable regrowth absorbing CO₂ equivalent to emissions",
         ["complete absence of any CO₂ release during combustion", "conversion of all biomass to uranium fuel rods", "permanent storage of all ash in the stratosphere"],
         "Carbon neutrality requires regrowth to reabsorb CO₂ released during biomass combustion.",
         "Students think biomass combustion releases no CO₂ or involves nuclear fuel.",
         "D2.4k", "Evaluating carbon-neutral biomass claim requirements", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in energy_mc2:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Energy and the Environment",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # --- Circulatory, Field, EMR top-up ---
    for platelet_pct in [0.5, 1.0, 1.5, 2.0]:
        total_cells = int(100000 * platelet_pct / 100)
        extra.append(nr(
            f"A blood sample contains 100,000 cells per microlitre and platelets make up {platelet_pct}% of them. "
            f"How many platelets per microlitre? Record as an integer.",
            str(total_cells),
            f"Platelets = {platelet_pct}% of 100,000 = {total_cells}.",
            "Students divide by 100 twice or use wrong percentage base.",
            topic="Circulatory and Immune Systems", outcome_code="A1.4k",
            skill_tested="Calculating platelet count from percentage of total cells",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    for v, i_val in [(120, 5), (240, 2), (12, 10), (48, 2.5)]:
        p = v * i_val
        extra.append(nr(
            f"A circuit operates at {v} V with current {i_val} A. What is the power in watts?",
            f"{p:.1f}" if p != int(p) else str(int(p)),
            f"P = VI = {v} × {i_val} = {p} W.",
            "Students use P = V/I instead of P = VI.",
            topic="Field Theory and Electrical Energy", outcome_code="C1.3s",
            skill_tested="Calculating electrical power from voltage and current",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for freq_ghz in [2.4, 5]:
        lam = 3e8 / (freq_ghz * 1e9)
        extra.append(mc(
            f"Radio/microwave communication at {freq_ghz} GHz has wavelength closest to",
            f"{lam:.2f} m",
            [f"{lam*10:.2f} m (ten times too long)", f"{lam/10:.2f} m (ten times too short)", f"{lam*100:.2f} m (one hundred times too long)"],
            f"λ = c/f = 3.0×10⁸/({freq_ghz}×10⁹) ≈ {lam:.2f} m.",
            "Students multiply c×f instead of dividing.",
            topic="Electromagnetic Spectrum", outcome_code="C2.6k",
            skill_tested="Estimating wavelength from GHz frequency",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    return extra


def programmatic_supplements_batch3() -> list[dict]:
    """Final top-up to reach ~450 questions."""
    extra = []

    circ_batch = [
        ("The pulmonary circuit carries blood between the heart and", "the lungs for gas exchange",
         ["the brain only without returning to heart", "the digestive tract exclusively", "the skin without any gas exchange"],
         "Pulmonary circulation moves blood between the right side of the heart and the lungs for oxygenation.",
         "Students confuse pulmonary circulation with systemic routes to the brain or digestive organs.",
         "A1.2k", "Tracing pulmonary circuit pathway", "Easy", 65),
        ("Antibodies are produced by differentiated", "B lymphocytes (plasma cells)",
         ["red blood cells during oxygen transport", "platelets during clot formation only", "cardiac muscle cells during systole"],
         "Activated B cells differentiate into plasma cells that secrete antigen-specific antibodies.",
         "Students attribute antibody production to red blood cells or platelets.",
         "A2.3k", "Identifying plasma cell antibody production", "Medium", 80),
        ("The spleen functions in the immune system to", "filter blood and store lymphocytes",
         ["pump blood to the lungs directly", "produce all digestive enzymes for the stomach", "generate electrical impulses for motor neurons"],
         "The spleen removes old blood cells and mounts immune responses to blood-borne pathogens.",
         "Students think the spleen pumps blood or produces digestive enzymes.",
         "A2.3k", "Describing spleen immune and filtration role", "Medium", 75),
        ("Anaphylaxis is a severe", "allergic reaction involving widespread immune activation",
         ["bacterial infection cured by antibiotics only", "genetic mutation in all chromosomes simultaneously", "normal resting heart rate variation"],
         "Anaphylaxis is a rapid systemic allergic response that can cause airway constriction and shock.",
         "Students confuse anaphylaxis with infection or normal cardiovascular variation.",
         "A2.4k", "Defining anaphylactic allergic response", "Medium", 80),
        ("The tricuspid valve prevents backflow of blood from the", "right ventricle to the right atrium during ventricular contraction",
         ["left ventricle to the aorta during systole", "pulmonary vein to the left atrium", "aorta to the left ventricle during diastole"],
         "The tricuspid valve closes when the right ventricle contracts, preventing backflow into the right atrium.",
         "Students confuse right-side valves with left-side aortic or mitral valve function.",
         "A1.2k", "Identifying tricuspid valve function", "Medium", 75),
        ("Natural killer (NK) cells provide", "innate immune surveillance against infected and abnormal cells",
         ["oxygen transport to all body tissues", "mechanical pumping of blood through arteries", "digestion of all dietary fats in the small intestine"],
         "NK cells recognize and destroy virus-infected or tumour cells without prior sensitization.",
         "Students assign respiratory, circulatory, or digestive functions to NK cells.",
         "A2.3k", "Describing natural killer cell innate immunity role", "Medium", 80),
        ("Complement proteins in blood enhance immune defence by", "marking pathogens for destruction and forming membrane attack complexes",
         ["binding oxygen for transport to tissues", "generating electrical current in neurons", "producing hydrochloric acid in the stomach"],
         "Complement cascade opsonizes pathogens and can lyse bacterial membranes directly.",
         "Students confuse complement proteins with hemoglobin, neurotransmitters, or gastric acid.",
         "A2.3k", "Explaining complement protein immune function", "Medium", 80),
        ("A tourniquet temporarily stops blood flow by", "compressing blood vessels to reduce bleeding from a limb",
         ["increasing heart rate to maximum permanently", "converting all plasma to red blood cells", "eliminating all white blood cells from circulation"],
         "Mechanical compression of vessels slows hemorrhage until definitive treatment is available.",
         "Students think tourniquets alter heart rate or change blood cell composition.",
         "A1.4s", "Explaining tourniquet hemostatic function", "Easy", 65),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in circ_batch:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Circulatory and Immune Systems",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    field_batch = [
        ("Electric field lines never cross because", "that would indicate two directions of field at one point",
         ["fields only exist inside conductors", "gravity prevents all electric forces", "magnetic monopoles block all field lines"],
         "At any point, the electric field has a single unique direction; crossing lines would violate this.",
         "Students invent unrelated reasons for the non-crossing field line rule.",
         "C1.3k", "Explaining why electric field lines do not cross", "Medium", 85),
        ("A permanent magnet creates a magnetic field because of", "aligned magnetic domains in ferromagnetic material",
         ["free electric charges moving at light speed in vacuum only", "nuclear fusion in the magnet core at room temperature", "complete absence of any electrons in the material"],
         "Ferromagnetic materials have domains whose alignment produces a net external magnetic field.",
         "Students attribute magnetism to fusion, absence of electrons, or free vacuum charges.",
         "C1.3k", "Explaining aligned domains in permanent magnets", "Medium", 80),
        ("An ammeter must have", "very low resistance and be connected in series",
         ["very high resistance and be connected in parallel", "infinite resistance in all measurements", "no connection to the circuit at all"],
         "Low resistance in series ensures the ammeter measures circuit current without significantly altering it.",
         "Students confuse ammeter (series, low R) with voltmeter (parallel, high R) connection.",
         "C1.2s", "Explaining ammeter connection and resistance requirements", "Medium", 80),
        ("The unit tesla (T) measures", "magnetic field strength",
         ["electrical resistance", "power consumption", "hydronium ion concentration"],
         "Tesla (T) is the SI unit for magnetic flux density / field strength.",
         "Students confuse tesla with ohms, watts, or chemistry concentration units.",
         "C1.3k", "Identifying tesla as magnetic field unit", "Easy", 55),
        ("Electrostatic force between like charges is", "repulsive",
         ["attractive always", "zero regardless of distance", "identical to gravitational attraction always"],
         "Like charges repel; opposite charges attract per Coulomb's law.",
         "Students think all charges attract or that sign does not affect force direction.",
         "C1.2k", "Stating electrostatic force between like charges", "Easy", 60),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in field_batch:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Field Theory and Electrical Energy",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    emr_batch = [
        ("Gamma rays have the", "highest frequency in the electromagnetic spectrum",
         ["lowest energy of all EMR types", "same frequency as AM radio waves always", "wavelength longer than all radio waves"],
         "Gamma rays occupy the highest-frequency, shortest-wavelength end of the EM spectrum.",
         "Students place gamma rays at the low-frequency radio end of the spectrum.",
         "C2.1k", "Identifying gamma ray position on EM spectrum", "Easy", 60),
        ("A prism separates white light into colours because", "each wavelength refracts at a slightly different angle in glass",
         ["all wavelengths travel at different speeds in vacuum", "the prism absorbs all colours equally", "white light contains only one wavelength"],
         "Dispersion occurs because the refractive index of glass varies slightly with wavelength.",
         "Students think dispersion requires different speeds in vacuum or single-wavelength white light.",
         "C2.4k", "Explaining prism dispersion of white light", "Medium", 80),
        ("LASER light is characterized by", "coherent, monochromatic, and collimated photons",
         ["random phases and all wavelengths equally", "slower speed than sunlight in vacuum", "only infrared with no visible component ever"],
         "Laser emission is coherent (in-phase), one wavelength, and directionally focused.",
         "Students think laser light is broadband incoherent radiation or slower than c.",
         "C2.1sts", "Describing laser light properties", "Medium", 80),
        ("The aurora borealis is caused by", "charged particles from the Sun interacting with Earth's magnetic field and atmosphere",
         ["reflection of city lights from ice crystals only", "nuclear fission in the troposphere", "complete absence of any magnetic field near poles"],
         "Solar wind particles excite atmospheric gases, producing light near the magnetic poles.",
         "Students attribute auroras to city lights or terrestrial nuclear reactions.",
         "C2.1k", "Explaining aurora formation mechanism", "Medium", 85),
        ("Microwave ovens use a frequency near", "2.45 GHz to excite water molecules",
         ["2.45 Hz to match heart rate", "2.45 MHz used exclusively for AM radio", "visible light at 500 THz in the cavity"],
         "Microwave ovens use ~2.45 GHz radiation to rotate polar molecules (especially water), generating heat.",
         "Students confuse GHz microwave oven frequency with Hz heart rate or visible light THz.",
         "C2.1sts", "Identifying microwave oven operating frequency band", "Medium", 75),
        ("Radio waves diffract around hills more easily than visible light because", "they have longer wavelengths",
         ["they travel faster than light in vacuum", "they have higher photon energy per quantum", "they are absorbed completely by all obstacles"],
         "Diffraction is more pronounced when wavelength is comparable to obstacle size; radio λ >> visible λ.",
         "Students think diffraction depends on speed or photon energy rather than wavelength.",
         "C2.4k", "Explaining radio wave diffraction around obstacles", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in emr_batch:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Electromagnetic Spectrum",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    env_nr = [(0.001, 3.0), (0.0001, 4.0)]
    for h, expected_ph in env_nr:
        extra.append(nr(
            f"Hydronium ion concentration is {h:.0e} mol/L. What is the pH (one decimal place)?",
            f"{expected_ph:.1f}",
            f"pH = −log({h:.0e}) = {expected_ph:.1f}.",
            "Students forget negative sign in pH calculation.",
            topic="Environmental Chemistry", outcome_code="B1.3k",
            skill_tested="Computing pH from given hydronium concentration",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    energy_batch = [
        ("Lignite coal has", "lower energy density than anthracite coal",
         ["higher energy density than all nuclear fuels", "identical energy content to solar photons", "no carbon content whatsoever"],
         "Anthracite is more compressed and carbon-rich, yielding more energy per unit mass than lignite.",
         "Students think all coal grades have identical energy density or no carbon.",
         "D1.5k", "Comparing lignite and anthracite energy density", "Medium", 80),
        ("A heat pump can heat a building by", "transferring thermal energy from cooler outside air or ground to the interior",
         ["creating thermal energy from nothing violating conservation", "only burning coal inside the living room", "eliminating all need for any electrical input always"],
         "Heat pumps move existing thermal energy using refrigeration cycle; they do not create energy.",
         "Students think heat pumps violate energy conservation or need no electricity.",
         "D2.4k", "Explaining heat pump energy transfer principle", "Medium", 80),
        ("The feed-in tariff policy encourages renewable energy by", "paying producers a set rate for electricity fed into the grid",
         ["banning all solar panels from residential roofs", "requiring only coal power for all new installations", "eliminating all energy storage technology research"],
         "Feed-in tariffs guarantee a purchase price for renewable electricity exported to the grid.",
         "Students think tariffs ban solar or mandate fossil fuel installations.",
         "D1.1sts", "Describing feed-in tariff renewable incentive", "Medium", 80),
        ("Offshore wind farms can capture", "stronger and more consistent winds than many onshore sites",
         ["no wind because ocean air is stationary always", "only geothermal energy from the ocean floor", "visible light for photovoltaic panels underwater without turbines"],
         "Open ocean and coastal sites often have higher average wind speeds than inland locations.",
         "Students think offshore sites lack wind or generate geothermal electricity.",
         "D2.4k", "Evaluating offshore wind resource advantage", "Medium", 80),
        ("Energy poverty describes households that", "spend a disproportionate share of income on energy costs",
         ["produce more energy than they consume always", "have no access to any form of technology ever", "generate fusion power in domestic basements"],
         "Energy poverty occurs when energy bills consume an excessive fraction of household income.",
         "Students confuse energy poverty with energy surplus or fusion technology.",
         "D1.2k", "Defining energy poverty concept", "Medium", 75),
        ("The concept of embedded energy in a product includes", "all energy used in extraction, manufacturing, transport, and disposal",
         ["only the electrical energy used when the product is switched on", "only the kinetic energy of the packaging box", "genetic energy stored in DNA of the product"],
         "Embodied/embedded energy accounts for the full life-cycle energy investment in a product.",
         "Students count only operating energy, ignoring production and disposal costs.",
         "D2.1sts", "Defining embedded energy in product life cycle", "Medium", 85),
        ("A net-zero energy building produces", "as much energy as it consumes over a year",
         ["no energy and uses no resources at all", "unlimited energy exceeding global supply", "only nuclear waste with no electricity output"],
         "Net-zero buildings balance annual energy generation with consumption through efficiency and renewables.",
         "Students think net-zero means zero consumption or unlimited free energy.",
         "D1.3k", "Defining net-zero energy building standard", "Medium", 80),
        ("Transmission line power loss is minimized by", "stepping up voltage to reduce current for the same power",
         ["stepping down voltage to maximum current always", "using only DC without any transformers ever", "eliminating all resistance from copper wire completely"],
         "P_loss = I²R; higher transmission voltage reduces current and resistive losses for fixed power.",
         "Students think lower voltage or zero resistance wires are practical solutions.",
         "D2.10k", "Explaining high-voltage transmission loss reduction", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in energy_batch:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Energy and the Environment",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    for growth in [2, 5, 10]:
        new_pop = 1000 * growth
        extra.append(nr(
            f"Global energy demand in a model region grows from 1000 units to {new_pop} units over a decade. "
            f"What is the multiplication factor of increase?",
            str(growth),
            f"Factor = {new_pop}/1000 = {growth}.",
            "Students subtract 1000 instead of computing the ratio.",
            topic="Energy and the Environment", outcome_code="D1.1k",
            skill_tested="Calculating energy demand growth factor",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    return extra


def collect_all() -> list[dict]:
    items = []
    items.extend(circulatory())
    items.extend(genetics())
    items.extend(env_chem())
    items.extend(field_theory())
    items.extend(emr())
    items.extend(energy())
    items.extend(programmatic_supplements())
    items.extend(programmatic_supplements_batch2())
    items.extend(programmatic_supplements_batch3())
    items.extend(expansion())
    return items


def deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        key = (item["topic"].lower(), normalize_text(item["question_text"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def validate_all(items: list[dict]):
    errors = []
    for i, item in enumerate(items):
        reasons = validate_question(item, i)
        if reasons:
            errors.append((i, reasons))
    return errors


def print_stats(items: list[dict]):
    print(f"\nTotal questions: {len(items)}")
    print("\nBy topic:")
    for topic, count in sorted(Counter(i["topic"] for i in items).items()):
        print(f"  {topic}: {count}")
    print("\nBy difficulty:")
    for diff, count in sorted(Counter(i["difficulty"] for i in items).items()):
        print(f"  {diff}: {count}")
    print("\nBy question type:")
    for qt, count in sorted(Counter(i["question_type"] for i in items).items()):
        print(f"  {qt}: {count}")
    print("\nBy unit:")
    for unit, count in sorted(Counter(i["unit"] for i in items).items()):
        print(f"  {unit}: {count}")
    outcomes = Counter(i["outcome_code"] for i in items)
    print(f"\nUnique outcome codes: {len(outcomes)}")


def main():
    items = collect_all()
    items = deduplicate(items)
    items = qa_fix_pool(items, max_per_template=2)
    errors = validate_all(items)
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} invalid items")
        for idx, reasons in errors[:20]:
            print(f"  item {idx}: {reasons}")
        raise SystemExit(1)

    ordered = [order_item(i) for i in items]
    mc_pos = assert_mc_position_balanced(ordered, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print_stats(ordered)
    print(f"\nWrote {len(ordered)} questions to {OUTPUT}")
    print("VALIDATION: PASSED — pool ready for sci30_clean_bank.py")


if __name__ == "__main__":
    main()
