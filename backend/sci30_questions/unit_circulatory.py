"""Circulatory and Immune Systems — Science 30 original questions."""

from .helpers import mc, nr

TOPIC = "Circulatory and Immune Systems"


def _base_mc():
    items = [
        mc(
            "Oxygenated blood returning from the lungs enters the heart through the",
            "pulmonary veins into the left atrium",
            ["pulmonary arteries into the right atrium", "aorta into the left ventricle", "vena cava into the right ventricle"],
            "Pulmonary veins carry oxygen-rich blood from lungs to the left atrium for systemic distribution.",
            "Students confuse pulmonary arteries (deoxygenated to lungs) with pulmonary veins.",
            topic=TOPIC, outcome_code="A1.2k",
            skill_tested="Tracing pulmonary circulation pathway",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "The chamber that pumps oxygenated blood to the entire body is the",
            "left ventricle",
            ["right atrium", "right ventricle", "left atrium"],
            "The left ventricle has the thickest muscular wall because it generates pressure for systemic circulation.",
            "Right ventricle pumps only to lungs; left atrium receives blood but does not pump to body.",
            topic=TOPIC, outcome_code="A1.1k",
            skill_tested="Identifying heart chamber responsible for systemic output",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Blood pressure is typically lowest in the",
            "capillaries",
            ["the aorta (high-pressure artery)", "arterioles (resistance vessels)", "veins immediately before the heart"],
            "Resistance is greatest in capillary beds, so pressure drops to its minimum there before venous return.",
            "Students assume pressure keeps decreasing only in veins or increases after capillaries.",
            topic=TOPIC, outcome_code="A1.3k",
            skill_tested="Relating vessel type to blood pressure gradient",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Which blood component is primarily responsible for transporting dissolved oxygen?",
            "hemoglobin within red blood cells",
            ["platelets", "plasma proteins only", "white blood cells"],
            "Hemoglobin in erythrocytes binds O₂ in the lungs and releases it in tissues.",
            "Plasma carries dissolved gases in small amounts but hemoglobin carries the bulk of O₂.",
            topic=TOPIC, outcome_code="A1.4k",
            skill_tested="Identifying oxygen transport mechanism in blood",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "A patient with a low platelet count would most likely have difficulty with",
            "blood clot formation at injury sites",
            ["oxygen delivery to tissues", "antibody production against pathogens", "regulating blood pH through buffers"],
            "Platelets aggregate at wounds to initiate the clotting cascade.",
            "Oxygen transport involves RBCs; antibodies involve B lymphocytes.",
            topic=TOPIC, outcome_code="A1.4k",
            skill_tested="Associating platelet function with hemostasis",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "The first line of defence against pathogens entering through the skin includes",
            "physical barrier and antimicrobial secretions on the epidermis",
            ["production of memory B cells in bone marrow", "antibody-mediated neutralization in blood", "complement cascade activation only"],
            "Intact skin and chemical secretions (sweat, sebum) block or inhibit pathogens before they enter tissues.",
            "Adaptive immunity (memory cells, antibodies) is a later, specific response.",
            topic=TOPIC, outcome_code="A2.2k",
            skill_tested="Describing non-specific external body defences",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Helper T cells are essential in adaptive immunity because they",
            "activate B cells and coordinate other immune cells through cytokine release",
            ["produce antibodies that bind free viruses in plasma", "engulf pathogens by phagocytosis directly", "form the physical barrier of the skin"],
            "Helper T cells release signals that enable clonal expansion of B cells and activation of cytotoxic T cells.",
            "Antibody production is by B cells; phagocytosis is primarily by macrophages.",
            topic=TOPIC, outcome_code="A2.3k",
            skill_tested="Explaining helper T cell role in immune coordination",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Memory cells formed after a successful immune response allow the body to",
            "mount a faster and stronger response upon re-exposure to the same antigen",
            ["prevent all future infections from any pathogen type", "eliminate the need for any innate immune defences", "produce antibiotics against bacteria"],
            "Memory B and T cells persist and respond rapidly when the same antigen appears again.",
            "Memory is antigen-specific; innate defences and antibiotics are separate mechanisms.",
            topic=TOPIC, outcome_code="A2.3k",
            skill_tested="Describing immunological memory function",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "An autoimmune disorder such as rheumatoid arthritis occurs when",
            "the immune system attacks the body's own tissues",
            ["pathogens replicate faster than white blood cells can divide", "vaccines introduce live pathogens that cause disease", "the spleen removes all red blood cells from circulation"],
            "Autoimmunity involves loss of self-tolerance; immune cells target normal body antigens.",
            "Vaccines use weakened/inactivated material; they do not cause autoimmune disease directly.",
            topic=TOPIC, outcome_code="A2.4k",
            skill_tested="Defining autoimmune disease mechanism",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "A vaccine provides protection primarily by stimulating",
            "production of memory lymphocytes without causing severe disease",
            ["immediate destruction of all bacteria in the body", "permanent closure of all capillary beds", "elimination of the need for helper T cells"],
            "Vaccines expose the immune system to antigens safely, generating memory for future encounters.",
            "Vaccines do not instantly clear all pathogens or replace normal immune cell types.",
            topic=TOPIC, outcome_code="A2.5k",
            skill_tested="Explaining vaccine mechanism of protection",
            difficulty="Easy", estimated_time_seconds=70,
        ),
        mc(
            "Arteries differ from veins in that arteries typically have",
            "thicker muscular walls to withstand higher pressure",
            ["valves preventing backflow in all arteries", "no elastic tissue in their walls", "lower pressure than adjacent capillaries"],
            "Arteries carry blood under high pressure from ventricular contraction and need strong walls.",
            "Valves are prominent in veins; arteries rely on pressure from heart beats.",
            topic=TOPIC, outcome_code="A1.3k",
            skill_tested="Comparing structural features of arteries and veins",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "Which vessel type allows exchange of nutrients and gases between blood and tissues?",
            "capillaries",
            ["the aorta (systemic artery)", "large veins (low-pressure return)", "pulmonary arteries only (to lungs)"],
            "Thin capillary walls and large surface area enable diffusion between blood and interstitial fluid.",
            "Large vessels transport blood; exchange occurs at capillary level.",
            topic=TOPIC, outcome_code="A1.3k",
            skill_tested="Identifying site of blood-tissue exchange",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Antibodies produced by plasma cells function by",
            "binding to specific antigens and marking pathogens for destruction",
            ["directly pumping blood through the heart", "replicating viral DNA inside host cells", "dissolving red blood cell membranes in healthy tissue"],
            "Antibodies neutralize or tag pathogens for phagocytes and complement proteins.",
            "Antibodies are proteins, not mechanical pumps or DNA replicators.",
            topic=TOPIC, outcome_code="A2.3k",
            skill_tested="Describing antibody function in humoral immunity",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Stomach acid contributes to innate immunity by",
            "destroying many ingested microorganisms in the gastric lumen",
            ["producing antibodies against intestinal bacteria", "transporting oxygen to the small intestine", "generating memory T cells in the stomach lining"],
            "Low pH in the stomach denatures proteins in many pathogens, reducing infection risk.",
            "Antibody production and memory cell formation are adaptive immune functions elsewhere.",
            topic=TOPIC, outcome_code="A2.2k",
            skill_tested="Explaining chemical barrier role of stomach acid",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Regular aerobic exercise can improve cardiovascular health primarily by",
            "strengthening cardiac muscle efficiency and improving circulation",
            ["eliminating all cholesterol from arterial walls instantly", "removing the need for the immune system", "preventing all genetic mutations"],
            "Exercise improves heart stroke efficiency, vessel elasticity, and metabolic health over time.",
            "Exercise benefits cardiovascular function but cannot instantly reverse all plaque or mutations.",
            topic=TOPIC, outcome_code="A1.1sts",
            skill_tested="Relating lifestyle factors to cardiovascular wellness",
            difficulty="Easy", estimated_time_seconds=70,
        ),
        mc(
            "Atherosclerosis in coronary arteries reduces blood flow to heart muscle, which can lead to",
            "angina or myocardial infarction during exertion",
            ["increased oxygen delivery to cardiac cells", "expansion of capillary diameter in the brain only", "complete immunity to bacterial infection"],
            "Plaque narrows arteries, limiting oxygen supply to cardiac tissue during demand.",
            "Reduced flow decreases oxygen delivery; it does not improve it.",
            topic=TOPIC, outcome_code="A1.1sts",
            skill_tested="Connecting arterial disease to cardiac oxygen supply",
            difficulty="Medium", estimated_time_seconds=90,
        ),
        mc(
            "Killer T cells eliminate infected body cells by",
            "recognizing antigen-presenting infected cells and inducing apoptosis",
            ["secreting hydrochloric acid into the bloodstream", "binding oxygen in the alveoli", "producing red blood cells in the spleen"],
            "Cytotoxic T lymphocytes destroy virus-infected or abnormal cells displaying foreign antigens.",
            "Killer T cells do not perform digestive, respiratory, or erythropoietic functions.",
            topic=TOPIC, outcome_code="A2.3k",
            skill_tested="Describing cytotoxic T cell effector mechanism",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Plasma in blood tissue serves to",
            "transport nutrients, hormones, wastes, and blood cells",
            ["contract rhythmically to pump blood", "carry genetic information as chromosomes", "produce electrical impulses like neurons"],
            "Plasma is the liquid matrix suspending formed elements and dissolved solutes.",
            "Pumping is done by the heart; chromosomes are in nuclei, not plasma.",
            topic=TOPIC, outcome_code="A1.4k",
            skill_tested="Describing plasma transport functions",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "The systemic circuit begins when blood leaves the",
            "left ventricle through the aorta",
            ["right atrium through pulmonary veins", "right ventricle through the vena cava", "left atrium through coronary veins only"],
            "Oxygenated blood exits the left ventricle into the aorta for distribution to body tissues.",
            "Pulmonary circuit starts at right ventricle; vena cava returns blood to heart.",
            topic=TOPIC, outcome_code="A1.2k",
            skill_tested="Identifying origin of systemic circulation",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "A person who receives a flu vaccine containing inactivated viral particles is protected through",
            "active artificial immunity",
            ["passive natural immunity from maternal antibodies", "innate immunity only with no memory response", "passive artificial immunity from donated serum"],
            "The person's own immune system responds to vaccine antigens, generating active immunity and memory.",
            "Passive immunity uses pre-made antibodies from another source; vaccines stimulate self-production.",
            topic=TOPIC, outcome_code="A2.5k",
            skill_tested="Classifying vaccine-induced immunity type",
            difficulty="Medium", estimated_time_seconds=90,
        ),
    ]
    return items


def _parameterized():
    items = []
    for hr in [70, 85]:
        beats_year = hr * 60 * 24 * 365
        items.append(nr(
            f"A resting heart rate of {hr} beats per minute is maintained for one year. "
            f"Assuming no change in rate, how many total heartbeats occur in that year? "
            f"Express your answer in scientific notation with one digit before the decimal "
            f"(e.g., 3.2e7).",
            f"{beats_year:.1e}",
            f"Beats/year = {hr} × 60 × 24 × 365 = {beats_year:.1e}.",
            "Students multiply by 365 only, omitting minutes per hour and hours per day.",
            topic=TOPIC, outcome_code="A1.3s",
            skill_tested="Extrapolating annual heartbeat count from resting rate",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    for rbc_millions in [4.8, 5.2]:
        total = int(rbc_millions * 5)
        items.append(nr(
            f"A blood sample contains {rbc_millions} million red blood cells per microlitre. "
            f"If a total of 5 microlitres are combined, how many million red blood cells are present? "
            f"Express the answer as a decimal.",
            f"{total:.1f}",
            f"Total = {rbc_millions} × 5 = {total:.1f} million RBCs.",
            "Students add 5 instead of multiplying by volume.",
            topic=TOPIC, outcome_code="A1.4k",
            skill_tested="Calculating total blood cell count from concentration",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for wbc, pathogen in [(8000, 2000), (7500, 1800)]:
        ratio = round(wbc / pathogen, 1)
        items.append(nr(
            f"In a controlled sample, {wbc} white blood cells respond to {pathogen} invading cells. "
            f"What is the ratio of white blood cells to invading cells? Express as a decimal rounded to one decimal place.",
            str(ratio),
            f"Ratio = {wbc}/{pathogen} = {ratio}.",
            "Students invert the ratio (pathogen/WBC instead of WBC/pathogen).",
            topic=TOPIC, outcome_code="A2.3s",
            skill_tested="Computing immune cell-to-pathogen ratio",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    for sbp, dbp in [(120, 80), (130, 85), (115, 75)]:
        pulse = sbp - dbp
        items.append(nr(
            f"A blood pressure reading shows systolic pressure of {sbp} mmHg and diastolic pressure of {dbp} mmHg. "
            f"What is the pulse pressure (systolic minus diastolic) in mmHg?",
            str(pulse),
            f"Pulse pressure = {sbp} − {dbp} = {pulse} mmHg.",
            "Students add the values or report diastolic pressure alone.",
            topic=TOPIC, outcome_code="A1.3k",
            skill_tested="Calculating pulse pressure from systolic and diastolic values",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    vaccine_mc = [
        ("Herd immunity develops in a population when a sufficiently high proportion of individuals are", "immunized so pathogen spread is limited", ["allergic to vaccine components", "unable to produce any white blood cells", "exposed only to bacterial toxins without antigens"], "High vaccination rates reduce susceptible hosts, protecting even unvaccinated members.", "Herd immunity requires immunization, not immunodeficiency.", "A2.5k", "Explaining herd immunity concept", "Medium", 85),
        ("Passive immunity transferred from mother to infant through breast milk involves", "antibodies present in colostrum without the infant producing its own antibodies first", ["memory T cells permanently replacing infant bone marrow", "live viruses that cause mild infection in all infants", "genetic modification of infant DNA"], "IgA and other antibodies in milk provide temporary protection while infant immunity matures.", "Passive immunity does not alter infant DNA or replace marrow.", "A2.3k", "Describing passive immunity via breast milk", "Medium", 80),
        ("Inflammation at a wound site is characterized by", "redness, heat, swelling, and increased blood flow to the area", ["complete absence of white blood cells", "permanent loss of all capillaries in the region", "instant antibody production against all pathogens globally"], "Inflammatory response increases vessel permeability and recruits immune cells to injury.", "Inflammation involves immune cell activity, not their absence.", "A2.2k", "Identifying signs of inflammatory response", "Easy", 65),
        ("The role of macrophages in the immune response includes", "engulfing pathogens and presenting antigens to T cells", ["producing hemoglobin for oxygen transport", "generating action potentials along axons", "pumping blood from atria to ventricles"], "Macrophages are phagocytes that process and display antigens to activate adaptive immunity.", "Hemoglobin is in RBCs; neurons conduct impulses; heart pumps blood.", "A2.3k", "Describing macrophage antigen presentation role", "Medium", 80),
        ("Fever during infection can help the immune response by", "increasing metabolic rate of immune cells and inhibiting some pathogen growth", ["destroying all antibodies in the bloodstream", "permanently stopping heart contraction", "converting all T cells into red blood cells"], "Elevated temperature supports immune activity and may reduce pathogen replication.", "Fever does not destroy antibodies or change cell lineages.", "A2.2k", "Explaining adaptive value of fever response", "Medium", 75),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in vaccine_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
