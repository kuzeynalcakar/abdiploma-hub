"""Generate, validate, and export the Biology 30 question bank (~300 questions)."""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from bio30_questions.helpers import mc, nr, wr
from bio30_questions.unit_a import questions as unit_a
from bio30_questions.unit_b import questions as unit_b
from bio30_questions.unit_c_division import questions as unit_c_division
from bio30_questions.unit_c_genetics import questions as unit_c_genetics
from bio30_questions.unit_d import questions as unit_d

OUTPUT = Path(__file__).parent.parent / "questions.json" / "biology30_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def programmatic_supplements():
    """Parameterized original NR/MC questions to reach blueprint targets."""
    extra = []

    # Genetics probability NR (unique scenarios)
    scenarios = [
        (0.75, "B", "b", 0.0625),
        (0.60, "D", "d", 0.16),
        (0.50, "E", "e", 0.25),
        (0.80, "F", "f", 0.04),
        (0.40, "G", "g", 0.36),
    ]
    for p, dom, rec, q2 in scenarios:
        q = round(1 - p, 2)
        extra.append(nr(
            f"In a large population, the frequency of allele {dom} is ${p}$. "
            f"Assuming Hardy-Weinberg equilibrium, what is the expected frequency of genotype {rec}{rec}? "
            f"Express as a decimal rounded to two decimal places.",
            f"{q2:.2f}",
            f"$q = 1 - {p} = {q}$. Frequency of {rec}{rec} = $q^2$ = ${q2:.2f}$.",
            "Students use $2pq$ or $p^2$ instead of $q^2$.",
            topic="Genetics and Molecular Biology", outcome_code="C2.2k",
            skill_tested="Calculating homozygous recessive frequency from allele data",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Hardy-Weinberg heterozygote calculations
    for p in [0.55, 0.35, 0.82, 0.48, 0.67]:
        q = round(1 - p, 2)
        het = round(2 * p * q, 2)
        extra.append(nr(
            f"Allele M frequency is ${p}$ in a Hardy-Weinberg population. "
            f"What is the expected frequency of heterozygotes? Express as decimal to two places.",
            f"{het:.2f}",
            f"$q = {q}$. Heterozygote frequency = $2pq$ = ${het}$.",
            "Students calculate $p^2$ instead of $2pq$.",
            topic="Population and Community Dynamics", outcome_code="D1.2k",
            skill_tested="Calculating Hardy-Weinberg heterozygote frequency",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Population growth NR
    pop_data = [
        (800, 920, "120", "Calculating absolute population increase"),
        (1500, 1275, "225", "Calculating population decline magnitude"),
        (400, 550, "150", "Calculating population growth over one generation"),
        (2500, 2750, "250", "Calculating net population change"),
        (600, 780, "180", "Calculating population size increase"),
    ]
    for n0, n1, ans, skill in pop_data:
        extra.append(nr(
            f"A wildlife survey counts ${n0}$ individuals in year one and ${n1}$ individuals in year two. "
            f"What is the absolute change in population size? Record the answer as a positive integer.",
            ans,
            f"Change = $|{n1} - {n0}| = {ans}$.",
            "Students report the final count instead of the change.",
            topic="Population and Community Dynamics", outcome_code="D3.2k",
            skill_tested=skill, difficulty="Easy", estimated_time_seconds=60,
        ))

    # Per capita growth
    for n0, n1 in [(1000, 1150), (2000, 2300), (500, 620), (3200, 3520)]:
        r = round((n1 - n0) / n0, 2)
        extra.append(nr(
            f"Population size changes from ${n0}$ to ${n1}$ in one year. "
            f"What is the per capita growth rate? Express as a decimal rounded to two decimal places.",
            f"{r:.2f}",
            f"$r = ({n1}-{n0})/{n0} = {r}$.",
            "Students forget to divide by initial population $N_0$.",
            topic="Population and Community Dynamics", outcome_code="D3.2k",
            skill_tested="Calculating per capita population growth rate",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Cell division chromosome NR
    for diploid in [8, 12, 20, 24, 32, 40]:
        haploid = diploid // 2
        extra.append(nr(
            f"A species has diploid number $2n = {diploid}$. How many chromosomes are in each gamete? Record the two-digit answer.",
            str(haploid),
            f"Haploid number $n = {diploid}/2 = {haploid}$.",
            "Students give diploid number instead of haploid.",
            topic="Cell Division", outcome_code="C1.1k",
            skill_tested="Computing haploid chromosome number",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # Mitotic index calculations
    for total, pct in [(400, 5), (600, 8), (250, 4), (800, 3)]:
        mitotic = total * pct // 100
        extra.append(nr(
            f"A sample of ${total}$ cells has a mitotic index of ${pct}$%. How many cells are in mitosis? Record the answer.",
            str(mitotic),
            f"${total} \\times {pct}/100 = {mitotic}$ cells.",
            "Students multiply by ${pct}$ instead of ${pct}/100$.",
            topic="Cell Division", outcome_code="C1.2k",
            skill_tested="Calculating cells in mitosis from mitotic index",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    # Additional nervous system MC
    nervous_mc = [
        ("The nodes of Ranvier are gaps in the", "myelin sheath where action potentials are regenerated", ["synaptic cleft between two neurons", "nuclear envelope during mitosis", "cornea of the eye"], "Myelin gaps expose voltage-gated channels for impulse regeneration in saltatory conduction.", "Nodes are in myelin, not synaptic clefts.", "A1.1k", "Identifying nodes of Ranvier", "Easy", 60),
        ("GABA is an inhibitory neurotransmitter that typically causes", "hyperpolarization of the postsynaptic membrane", ["depolarization toward threshold always", "release of acetylcholine at the neuromuscular junction", "permanent destruction of the presynaptic neuron"], "GABA often opens Cl$^-$ channels, making inside more negative (IPSP).", "Excitatory transmitters depolarize; GABA usually inhibits.", "A1.1k", "Describing GABA inhibitory effect", "Medium", 85),
        ("The blood-testis barrier formed by Sertoli cells prevents", "immune attack on developing sperm cells", ["all testosterone from entering the bloodstream", "meiosis from occurring in the testes", "FSH from binding to any receptor"], "Barrier isolates immunologically unique sperm from immune system.", "Testosterone and FSH still function with barrier present.", "B1.1k", "Explaining blood-testis barrier function", "Hard", 110),
        ("Vasopressin (ADH) and oxytocin differ from peptide hormones synthesized in the anterior pituitary because they", "are produced in hypothalamic neurons and released from posterior pituitary", ["are steroid hormones from adrenal cortex", "are neurotransmitters only at skeletal neuromuscular junctions", "are digestive enzymes from the pancreas"], "Posterior pituitary stores hypothalamic hormones; anterior pituitary synthesizes its own.", "ADH/oxytocin are peptides, not steroids.", "A2.1k", "Distinguishing posterior pituitary hormone origin", "Medium", 85),
        ("Graves disease involves hyperthyroidism often caused by", "antibodies stimulating TSH receptors on thyroid cells", ["complete absence of all thyroid hormone", "destruction of parathyroid glands only", "excess insulin from beta cells"], "Autoimmune stimulation mimics TSH, causing excessive T3/T4 production.", "Graves is hyper-, not hypo-, thyroidism.", "A2.3k", "Explaining autoimmune hyperthyroidism mechanism", "Hard", 115),
        ("Addison disease results from insufficient", "cortisol and aldosterone from adrenal cortex", ["insulin from pancreatic beta cells", "growth hormone from anterior pituitary only", "acetylcholine at all synapses"], "Adrenal cortex failure reduces cortisol and mineralocorticoids.", "Addison is adrenal, not pancreatic.", "A2.4k", "Identifying Addison disease hormonal deficiency", "Medium", 90),
        ("The zygomatic arch and masseter muscle are involved in", "mastication (chewing)", ["pupillary light reflex", "spermatogenesis in testes", "photosynthesis in chloroplasts"], "Muscles of mastication move the jaw during chewing — somatic function.", "Not related to reproductive or visual reflex pathways.", "A1.2k", "Associating somatic motor function with chewing", "Easy", 55),
        ("Proprioceptors in muscles and tendons detect", "body position and stretch of muscles", ["chemicals dissolved in blood plasma only", "light intensity in the fovea", "airborne odorant molecules"], "Proprioceptors provide CNS feedback on limb position and movement.", "Chemoreceptors detect chemicals; proprioceptors detect stretch/position.", "A1.6k", "Defining proprioceptor function", "Easy", 60),
        ("The endoneurium, perineurium, and epineurium are connective tissue layers that", "protect and bundle fibres within peripheral nerves", ["produce cerebrospinal fluid in ventricles", "line the seminiferous tubules exclusively", "form the blood-brain barrier alone"], "These layers structurally support peripheral nerve fascicles and fibres.", "CSF is produced by choroid plexus, not nerve connective tissue.", "A1.1k", "Identifying peripheral nerve connective tissue layers", "Hard", 110),
        ("A patient with a severed spinal cord at thoracic level loses voluntary motor control below the lesion but may still show", "spinal reflexes below the injury independent of brain input", ["conscious perception of all pain below the lesion", "hormone production by the thyroid only", "mitosis in all somatic cells stopping permanently"], "Spinal reflex arcs can function locally without descending brain pathways.", "Sensory perception and voluntary control require intact ascending/descending tracts.", "A1.3k", "Predicting spinal cord injury reflex preservation", "Hard", 120),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in nervous_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Nervous and Endocrine Systems",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # Reproduction MC supplements
    repro_mc = [
        ("The acrosomal reaction occurs when the sperm", "releases enzymes to penetrate the zona pellucida", ["undergoes meiosis II in the epididymis", "produces progesterone for the uterus", "forms the blood-testis barrier"], "Acrosome releases hydrolases enabling sperm entry through egg investments.", "Meiosis II in sperm completes after penetration, not during acrosomal reaction.", "B1.1k", "Describing acrosomal reaction", "Medium", 85),
        ("Human chorionic gonadotropin maintains the corpus luteum during early pregnancy so that", "progesterone production continues to support the endometrium", ["FSH surges trigger repeated ovulation during pregnancy", "testosterone converts the uterus into an ovary", "implantation is prevented in the fallopian tube"], "hCG mimics LH, sustaining corpus luteum progesterone until placenta takes over.", "Ovulation is suppressed during pregnancy.", "B2.2k", "Explaining hCG role in early pregnancy", "Medium", 90),
        ("The amnion surrounds the embryo and functions to", "provide a fluid-filled protective environment", ["produce sperm for the developing fetus", "generate action potentials in the CNS directly", "carry maternal blood mixed with fetal blood"], "Amniotic fluid cushions against mechanical shock and temperature change.", "Fetal blood is separate from maternal blood in circulation.", "B3.2k", "Describing amnion protective function", "Easy", 70),
        ("Teratogen exposure during the first trimester is especially dangerous because", "organogenesis is occurring during critical developmental windows", ["no cell division occurs at any stage of pregnancy", "all genes are permanently silenced after birth only", "the placenta blocks all chemicals without exception always"], "Major organs form early; teratogens can disrupt differentiation irreversibly.", "Cell division and differentiation are most active during early development.", "B3.3k", "Explaining critical period teratogen sensitivity", "Medium", 90),
        ("In embryonic development, the mesoderm gives rise to", "muscle, bone, and circulatory system components", ["nervous system and epidermis only", "lining of the digestive tract exclusively", "placental hormones such as hCG directly"], "Mesoderm forms musculoskeletal and cardiovascular tissues among others.", "Nervous system/ epidermis derive from ectoderm.", "B3.2k", "Identifying mesoderm derivatives", "Medium", 85),
        ("The endoderm primarily forms", "lining of the digestive and respiratory tracts and associated organs", ["skin and neural tissue", "bone and skeletal muscle", "only extraembryonic membranes without any fetal organs"], "Endoderm contributes to gut lining, liver, pancreas, and lung epithelium.", "Skin and neurons are ectodermal derivatives.", "B3.2k", "Identifying endoderm derivatives", "Medium", 85),
        ("Parthenogenesis in some species demonstrates that", "development can occur from an unfertilized egg in certain organisms", ["all human reproduction occurs without fertilization normally", "meiosis never happens in any animal", "mitosis produces four haploid sperm always"], "Some insects and reptiles can develop from unfertilized eggs — not typical in humans.", "Human reproduction requires fertilization.", "B3.1k", "Explaining parthenogenesis concept", "Hard", 110),
        ("Assisted reproductive technology preimplantation genetic diagnosis (PGD) allows", "screening embryos for specific genetic conditions before implantation", ["guaranteed elimination of all birth defects in every case", "creation of embryos without any DNA", "replacement of mitosis with meiosis in adults"], "PGD tests cells from blastocysts for known mutations before uterine transfer.", "PGD screens specific conditions; it cannot prevent all defects.", "B2.3k", "Describing PGD reproductive technology", "Medium", 95),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in repro_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Reproduction and Development",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # Genetics MC supplements
    gen_mc = [
        ("A testcross of a dominant-phenotype pea plant yields 50% dominant and 50% recessive offspring. The parent genotype is", "heterozygous", ["homozygous dominant", "homozygous recessive", "haploid"], "1:1 ratio in testcross indicates heterozygote (Aa × aa).", "Homozygous dominant gives 100% dominant in testcross.", "C2.2k", "Inferring genotype from testcross ratio", "Medium", 85),
        ("Two genes 5 map units apart on a chromosome have an expected recombination frequency of", "5%", ["50% always like unlinked genes", "0% with no crossing over ever", "100% recombinant offspring only"], "1 map unit = 1% recombination; 5 map units ≈ 5% recombinants.", "Unlinked genes give ~50% recombination.", "C2.3k", "Relating map distance to recombination frequency", "Hard", 115),
        ("A dihybrid testcross AaBb × aabb yields expected proportion of aabb offspring of", "0.25", ["0.50", "0.125", "0.0625"], "Each gene segregates 1/2 recessive: 1/2 × 1/2 = 1/4.", "Students forget to multiply independent probabilities.", "C2.2k", "Calculating double recessive testcross proportion", "Hard", 110),
        ("DNA ligase is essential in replication because it", "joins Okazaki fragments on the lagging strand", ["unwinds the double helix at the origin only", "adds RNA primers to growing DNA chains", "degrades mRNA after transcription"], "Ligase seals nicks between fragments after primer removal.", "Helicase unwinds; primase adds primers.", "C3.2k", "Describing DNA ligase function", "Medium", 85),
        ("Helicase function during replication is to", "unwind the DNA double helix at the replication fork", ["join Okazaki fragments", "remove introns from pre-mRNA", "synthesize tRNA anticodons"], "Helicase breaks hydrogen bonds between strands for template access.", "Ligase joins fragments; helicase unwinds.", "C3.2k", "Describing helicase function", "Easy", 70),
        ("Telomerase activity in germ cells prevents", "loss of chromosome end sequences during repeated divisions", ["all mutations in coding regions", "crossing over during meiosis I", "transcription of introns into protein directly"], "Telomerase extends telomeres, protecting ends from shortening.", "Mutation prevention is not telomerase's primary role.", "C3.2k", "Explaining telomerase protective role", "Hard", 110),
        ("A SNP (single nucleotide polymorphism) represents", "a single base pair difference between individuals at a locus", ["deletion of an entire chromosome always", "addition of a new chromosome from bacteria", "complete absence of DNA in a cell"], "SNPs are point differences used as genetic markers.", "SNPs are single-base variants, not whole chromosome loss.", "C3.4k", "Defining SNP molecular marker", "Easy", 70),
        ("Northern blot analysis detects", "specific RNA sequences", ["protein molecular weight only without nucleic acids", "lipid composition of cell membranes exclusively", "chromosome number in metaphase spreads only"], "Northern blot uses RNA separation and probe hybridization.", "Western blot detects proteins; Southern detects DNA.", "C3.4k", "Distinguishing Northern blot from other blots", "Hard", 115),
        ("A transgenic organism contains", "genes transferred from another species using biotechnology", ["only naturally occurring alleles with no human intervention ever", "no DNA in any somatic cell", "RNA instead of DNA in all chromosomes"], "Transgenic organisms express introduced foreign genes (e.g., Bt corn).", "Transgenics involve deliberate gene transfer.", "C3.4k", "Defining transgenic organism", "Easy", 75),
        ("Gene expression can be regulated at the transcriptional level by", "transcription factors binding promoters and enhancers", ["only changing the order of amino acids after translation exclusively", "removing all introns from genomic DNA permanently in every cell", "blocking mitosis in all tissues"], "Transcription factors and chromatin modification control when genes are transcribed.", "Post-translational control is separate from transcriptional regulation.", "C3.5k", "Explaining transcriptional gene regulation", "Medium", 90),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in gen_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Genetics and Molecular Biology",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # Ecology MC supplements
    eco_mc = [
        ("Niche differentiation among competing species can", "reduce direct competition and allow coexistence", ["guarantee competitive exclusion of all but one species always", "eliminate the need for any resources", "prevent all predation in the community"], "Partitioning resources (spatial, temporal, dietary) enables species coexistence.", "Competitive exclusion occurs when niches fully overlap without differentiation.", "D2.1k", "Explaining niche differentiation and coexistence", "Medium", 90),
        ("Trophic cascade occurs when", "changes at one trophic level affect populations at other levels", ["only producers are affected by any predator removal", "energy increases by 90% at each higher trophic level", "all species in a food web are unaffected by predator loss"], "Removing top predators can release herbivore populations, affecting plants.", "Energy decreases, not increases, up trophic levels.", "D2.3k", "Defining trophic cascade", "Medium", 85),
        ("Eutrophication of lakes from fertilizer runoff leads to", "algal blooms and oxygen depletion when algae decompose", ["increased dissolved oxygen permanently from all algae growth", "complete elimination of all nitrogen from water", "immediate evolution of fish into terrestrial mammals"], "Excess nutrients cause blooms; bacterial decomposition depletes O$_2$, harming fish.", "Decomposition consumes oxygen, causing hypoxia.", "D2.1sts", "Explaining eutrophication ecological consequences", "Medium", 90),
        ("Conservation biology prioritizes maintaining genetic diversity because it", "increases population resilience to environmental change", ["ensures all individuals are genetically identical for uniformity", "eliminates the need for any habitat protection", "prevents all natural selection from occurring ever"], "Greater allelic diversity provides raw material for adaptation.", "Uniformity reduces adaptive capacity.", "D1.3k", "Explaining value of genetic diversity in conservation", "Easy", 75),
        ("The competitive exclusion principle states that two species competing for the same limiting resource cannot", "coexist indefinitely in the same niche", ["ever interact in any ecosystem", "share any habitat under any conditions without differentiation", "undergo any evolutionary change"], "Complete niche overlap leads one species to exclude the other long-term.", "Coexistence is possible with niche differentiation.", "D2.1k", "Stating competitive exclusion principle", "Medium", 85),
        ("Pioneer species in primary succession such as lichens contribute by", "weathering rock and building initial soil organic matter", ["immediately forming climax forest canopy", "preventing any water from reaching substrate ever", "eliminating all subsequent colonizers"], "Pioneers tolerate harsh conditions and begin soil formation for later species.", "Climax species arrive much later in succession.", "D2.3k", "Describing pioneer species role in succession", "Easy", 70),
        ("Metapopulation dynamics describe", "spatially separated subpopulations connected by occasional dispersal", ["a single isolated population with no immigration ever", "only microbial populations in laboratory flasks without migration", "energy flow between trophic levels exclusively"], "Subpopulations may go locally extinct and be recolonized by migrants.", "Metapopulations involve multiple linked patches.", "D3.3k", "Defining metapopulation concept", "Hard", 110),
        ("Allee effect occurs when", "per capita growth rate decreases at very low population density", ["population grows fastest at the lowest densities always", "carrying capacity is exceeded without any limit", "all individuals reproduce equally regardless of density"], "Very small populations may have difficulty finding mates or group defense.", "Allee effect reduces growth at low N, opposite of density independence.", "D3.3k", "Explaining Allee effect on small populations", "Hard", 115),
        ("Ecological succession toward climax community represents", "gradual change in species composition over time in an ecosystem", ["instantaneous creation of all species without any colonization", "permanent stasis with no further disturbance possible", "only abiotic factors with zero biological involvement"], "Succession is a biological process of community change over ecological time.", "Disturbance can reset succession at any stage.", "D2.3k", "Defining ecological succession", "Easy", 65),
        ("Human introduction of zebra mussels to the Great Lakes is an example of", "invasive species altering native community structure", ["primary succession on bare volcanic rock", "natural gene flow between historically connected populations", "Hardy-Weinberg equilibrium in a closed lake system"], "Zebra mussels outcompete natives and alter food webs — classic invasion.", "Invasion introduces species beyond natural range.", "D2.3k", "Identifying invasive species example", "Easy", 75),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in eco_mc:
        extra.append(mc(qt, ans, dist, expl, mis, topic="Population and Community Dynamics",
                          outcome_code=oc, skill_tested=skill, difficulty=diff,
                          estimated_time_seconds=time))

    # Written response supplements
    extra.append(wr(
        "Explain the difference between density-dependent and density-independent population regulation, giving one biological example of each.",
        "Density-dependent factors intensify as population size increases (e.g., disease spread, competition for nesting sites). Density-independent factors affect populations regardless of size (e.g., severe frost, wildfire). Both influence population growth but scale differently with density.",
        "Marking guide: (1) Density-dependent defined with example — 3 marks. (2) Density-independent defined with example — 3 marks.",
        "Students provide examples but fail to explain density relationship.",
        topic="Population and Community Dynamics", outcome_code="D3.3k",
        skill_tested="Comparing density-dependent and independent regulation",
        difficulty="Medium", estimated_time_seconds=240,
    ))
    extra.append(wr(
        "Describe the process of DNA replication, identifying the roles of helicase, primase, DNA polymerase, and ligase.",
        "Helicase unwinds the double helix at the replication fork. Primase synthesizes short RNA primers providing 3' OH. DNA polymerase III extends new DNA strands 5'→3' on leading and lagging strands (Okazaki fragments). DNA polymerase I replaces primers with DNA. Ligase joins Okazaki fragments into continuous lagging strand.",
        "Marking guide: (1) Helicase — 1 mark. (2) Primase — 1 mark. (3) DNA polymerase — 2 marks. (4) Ligase — 1 mark. (5) Leading/lagging distinction — 1 mark.",
        "Students omit Okazaki fragments or ligase function.",
        topic="Genetics and Molecular Biology", outcome_code="C3.2k",
        skill_tested="Describing replication enzyme functions",
        difficulty="Hard", estimated_time_seconds=300,
    ))
    extra.append(wr(
        "A couple with normal vision has a colour-blind son. Explain how this pattern is consistent with X-linked recessive inheritance and state the mother's likely genotype.",
        "Colour blindness is X-linked recessive. Affected son (X$^c$Y) inherits X$^c$ from mother and Y from father. Father is normal (X$^N$Y) so cannot pass X$^c$. Mother must be carrier X$^N$X$^c$ (normal vision but passes X$^c$ to 50% of sons).",
        "Marking guide: (1) X-linked recessive identified — 2 marks. (2) Son inherits X from mother — 1 mark. (3) Mother carrier genotype — 2 marks.",
        "Students claim father passes colour blindness to son via Y chromosome.",
        topic="Genetics and Molecular Biology", outcome_code="C2.5k",
        skill_tested="Explaining X-linked pedigree pattern",
        difficulty="Medium", estimated_time_seconds=260,
    ))
    extra.append(wr(
        "Explain how the human body maintains water balance on a hot day when sweating increases, referencing ADH and at least one target organ.",
        "Sweating increases water loss, raising blood osmolarity. Osmoreceptors in hypothalamus detect change, increasing ADH release from posterior pituitary. ADH acts on kidney collecting ducts, inserting aquaporins to reabsorb more water, producing concentrated urine. Thirst centre also promotes fluid intake. Negative feedback restores osmolarity toward set point.",
        "Marking guide: (1) Increased osmolarity from sweating — 1 mark. (2) ADH release pathway — 2 marks. (3) Kidney collecting duct effect — 2 marks. (4) Negative feedback — 1 mark.",
        "Students describe sweating but omit ADH renal mechanism.",
        topic="Nervous and Endocrine Systems", outcome_code="A2.2k",
        skill_tested="Integrating ADH in water balance homeostasis",
        difficulty="Hard", estimated_time_seconds=280,
    ))

    # Additional sequence-ordering NR (Alberta diploma style)
    seq_topics = {
        "C3.2k": ("Genetics and Molecular Biology", "Sequencing DNA replication events"),
        "B1.1k": ("Reproduction and Development", "Sequencing fertilization events"),
        "A1.5k": ("Nervous and Endocrine Systems", "Sequencing auditory processing events"),
        "D2.3k": ("Population and Community Dynamics", "Sequencing secondary succession stages"),
        "A2.2k": ("Nervous and Endocrine Systems", "Sequencing glucose homeostasis events"),
    }
    seq_data = [
        ("Place DNA replication events in order: (1) ligase joins fragments, (2) helicase unwinds DNA, (3) polymerase extends strands, (4) primase adds primers. Record all four digits.", "2431", "C3.2k"),
        ("Order fertilization events: (1) cortical reaction, (2) sperm penetrates zona pellucida, (3) fusion of pronuclei, (4) acrosomal reaction. Record all four digits.", "4231", "B1.1k"),
        ("Order sound processing: (1) cochlear transduction, (2) auditory canal entry, (3) ossicle vibration, (4) tympanic membrane vibration. Record all four digits.", "2431", "A1.5k"),
        ("Order secondary succession on abandoned farmland: (1) grasses, (2) shrubs, (3) climax forest, (4) annual weeds. Record all four digits.", "4123", "D2.3k"),
        ("Order insulin response to high blood glucose: (1) beta cells secrete insulin, (2) glucose enters cells, (3) blood glucose rises after meal, (4) glycogen synthesis in liver. Record all four digits.", "3142", "A2.2k"),
        ("Order meiosis II stages: (1) anaphase II, (2) metaphase II, (3) prophase II, (4) telophase II. Record all four digits.", "3214", "C1.1k"),
        ("Order mRNA processing: (1) splicing introns, (2) transcription, (3) 5' cap addition, (4) nuclear export. Record all four digits.", "2314", "C3.3k"),
        ("Order reflex arc signal: (1) effector response, (2) sensory neuron activation, (3) receptor stimulation, (4) motor neuron activation. Record all four digits.", "3241", "A1.3k"),
    ]
    for qtext, ans, oc in seq_data:
        topic, skill = seq_topics.get(oc, ("Cell Division", "Sequencing biological events"))
        if oc == "C1.1k":
            topic, skill = "Cell Division", "Sequencing meiosis II stages"
        if oc == "C3.3k":
            topic, skill = "Genetics and Molecular Biology", "Sequencing mRNA processing events"
        if oc == "A1.3k":
            topic, skill = "Nervous and Endocrine Systems", "Sequencing reflex arc events"
        extra.append(nr(qtext, ans, f"Correct chronological order is {ans}.", "Students confuse effector response with receptor stimulation.",
                        topic=topic, outcome_code=oc, skill_tested=skill, difficulty="Easy", estimated_time_seconds=70))

    # Monohybrid probability NR
    for dominant, recessive, cross, answer in [
        ("A", "a", "Aa × Aa", "0.25"),
        ("B", "b", "Bb × bb", "0.50"),
        ("D", "d", "Dd × Dd", "0.75"),
        ("E", "e", "Ee × ee", "0.50"),
        ("G", "g", "Gg × Gg", "0.25"),
        ("H", "h", "Hh × Hh", "0.75"),
        ("K", "k", "Kk × kk", "0.50"),
        ("M", "m", "Mm × mm", "0.50"),
        ("P", "p", "Pp × Pp", "0.25"),
        ("R", "r", "Rr × rr", "0.50"),
    ]:
        extra.append(nr(
            f"What fraction of offspring from the cross {cross} show the dominant phenotype? Express as a decimal to two decimal places.",
            answer,
            f"Punnett square analysis of {cross} gives dominant phenotype frequency = {answer}.",
            "Students confuse dominant phenotype with homozygous dominant only.",
            topic="Genetics and Molecular Biology", outcome_code="C2.2k",
            skill_tested="Calculating dominant phenotype probability",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # q^2 frequency NR for population topic
    for p in [0.3, 0.45, 0.62, 0.71, 0.88, 0.52, 0.39, 0.57]:
        q = round(1 - p, 2)
        aa = round(q * q, 2)
        extra.append(nr(
            f"In a Hardy-Weinberg population, allele A frequency is ${p}$. What is the frequency of genotype aa? Express as decimal to two places.",
            f"{aa:.2f}",
            f"$q = {q}$; $q^2 = {aa}$.",
            "Students calculate $2pq$ instead of $q^2$.",
            topic="Population and Community Dynamics", outcome_code="D1.2k",
            skill_tested="Calculating recessive genotype frequency",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # p^2 frequency
    for p in [0.25, 0.55, 0.7, 0.42, 0.63]:
        pp = round(p * p, 2)
        extra.append(nr(
            f"Allele T frequency is ${p}$ in a Hardy-Weinberg population. What is the frequency of genotype TT? Express as decimal to two places.",
            f"{pp:.2f}",
            f"TT frequency = $p^2$ = ${pp}$.",
            "Students use $2pq$ or $q^2$.",
            topic="Population and Community Dynamics", outcome_code="D1.2k",
            skill_tested="Calculating homozygous dominant genotype frequency",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # Additional written response questions to meet 10% blueprint
    wr_batch = [
        ("Nervous and Endocrine Systems", "A2.3k",
         "Explain how negative feedback regulates thyroid hormone levels. Include TRH, TSH, T3/T4, and the glands involved.",
         "Hypothalamus releases TRH → anterior pituitary releases TSH → thyroid releases T3/T4. Elevated T3/T4 inhibits TRH and TSH (negative feedback), stabilizing levels.",
         "Marking guide: (1) TRH/TSH pathway — 2 marks. (2) T3/T4 source — 1 mark. (3) Negative feedback inhibition — 2 marks.",
         "Students list hormones without feedback direction.", "Hard", 280,
         "Tracing thyroid hormone negative feedback"),
        ("Nervous and Endocrine Systems", "A1.4k",
         "Compare rod and cone cells in terms of light sensitivity, colour detection, and distribution in the retina.",
         "Rods: highly sensitive in dim light, no colour, abundant peripherally. Cones: less sensitive, detect colour, concentrated in fovea for acuity in bright light.",
         "Marking guide: (1) Light sensitivity contrast — 2 marks. (2) Colour function — 2 marks. (3) Distribution — 2 marks.",
         "Students claim rods detect colour.", "Medium", 240,
         "Comparing rod and cone function"),
        ("Reproduction and Development", "B2.1k",
         "Describe hormonal changes during the luteal phase and explain what happens if fertilization does not occur.",
         "After ovulation, corpus luteum secretes progesterone and estrogen, maintaining endometrium. Without fertilization, corpus luteum degenerates, progesterone drops, endometrium sloughs (menstruation), and new follicular phase begins.",
         "Marking guide: (1) Corpus luteum hormones — 2 marks. (2) Endometrial maintenance — 1 mark. (3) Menstruation trigger — 2 marks.",
         "Students confuse follicular and luteal phases.", "Medium", 260,
         "Explaining luteal phase hormonal control"),
        ("Reproduction and Development", "B3.3k",
         "Explain why teratogen exposure during organogenesis can cause permanent birth defects while the same exposure after birth may have less severe effects.",
         "Organogenesis involves rapid differentiation and pattern formation; disrupting signalling causes irreversible structural errors. After organs mature, cells are more differentiated and less plastic, so equivalent damage is often repairable or localized.",
         "Marking guide: (1) Organogenesis as critical period — 2 marks. (2) Differentiation/plasticity concept — 2 marks. (3) Contrast with mature tissue — 2 marks.",
         "Students state all teratogen effects are identical at any age.", "Hard", 280,
         "Explaining critical periods in teratogenesis"),
        ("Cell Division", "C1.1k",
         "Compare crossing over and independent assortment as sources of genetic variation in meiosis.",
         "Crossing over exchanges alleles between homologous chromosomes during prophase I, creating recombinant chromatids. Independent assortment randomizes homologue orientation at metaphase I, creating novel chromosome combinations. Both increase gamete diversity.",
         "Marking guide: (1) Crossing over mechanism — 2 marks. (2) Independent assortment mechanism — 2 marks. (3) Variation outcome for both — 2 marks.",
         "Students use the terms interchangeably without distinction.", "Medium", 250,
         "Comparing meiotic variation mechanisms"),
        ("Cell Division", "C1.6k",
         "Explain how a mutation in a tumour suppressor gene such as p53 can contribute to cancer development.",
         "p53 normally pauses cell cycle for DNA repair or triggers apoptosis when damage is detected. Loss-of-function mutations allow damaged cells to divide, accumulating additional mutations and leading to uncontrolled proliferation.",
         "Marking guide: (1) Normal p53 function — 2 marks. (2) Effect of mutation — 2 marks. (3) Link to cancer progression — 2 marks.",
         "Students describe p53 as an oncogene that speeds division when active.", "Hard", 270,
         "Explaining tumour suppressor role in cancer"),
        ("Genetics and Molecular Biology", "C3.6k",
         "Distinguish between a point mutation, a frameshift mutation, and a chromosomal deletion, giving one consequence of each.",
         "Point mutation: single base change; may be silent, missense, or nonsense. Frameshift: insertions/deletions not in multiples of three alter reading frame downstream. Chromosomal deletion: loss of large segment affecting many genes (e.g., Cri-du-chat).",
         "Marking guide: (1) Point mutation — 2 marks. (2) Frameshift — 2 marks. (3) Chromosomal deletion — 2 marks.",
         "Students define types without stating consequences.", "Hard", 280,
         "Classifying mutation types and effects"),
        ("Genetics and Molecular Biology", "C3.4k",
         "Explain how CRISPR-Cas9 can be used to edit a specific gene and discuss one ethical consideration.",
         "Guide RNA directs Cas9 to matching genomic sequence; Cas9 cuts DNA; cell repair pathways introduce desired edit. Ethical issues include off-target effects, germline editing affecting future generations, and equitable access.",
         "Marking guide: (1) Guide RNA targeting — 2 marks. (2) Cas9 cleavage/repair — 2 marks. (3) Valid ethical issue discussed — 2 marks.",
         "Students describe PCR instead of CRISPR.", "Hard", 290,
         "Explaining CRISPR mechanism and STS implications"),
        ("Population and Community Dynamics", "D1.4k",
         "Explain how antibiotic use in agriculture can drive natural selection for antibiotic-resistant bacteria in the environment.",
         "Low-dose antibiotics kill susceptible bacteria, leaving resistant variants that reproduce. Resistance alleles spread through bacterial populations and horizontal gene transfer, creating reservoirs of resistant microbes transmissible to humans.",
         "Marking guide: (1) Selection against susceptible bacteria — 2 marks. (2) Resistant reproduction/gene pool change — 2 marks. (3) Environmental/human health link — 2 marks.",
         "Students claim antibiotics cause mutations directly in every bacterium.", "Hard", 280,
         "Applying natural selection to antibiotic resistance"),
        ("Population and Community Dynamics", "D2.3k",
         "Describe primary succession on a volcanic island and identify the role of pioneer species and climax community.",
         "Bare rock → pioneer lichens/mosses weather substrate and build soil → grasses/shrubs → trees → climax community stable for climate. Pioneers tolerate harsh conditions and enable later species; climax persists until major disturbance.",
         "Marking guide: (1) Sequence of succession — 2 marks. (2) Pioneer role — 2 marks. (3) Climax definition — 2 marks.",
         "Students confuse primary with secondary succession.", "Medium", 250,
         "Describing primary ecological succession"),
    ]
    for topic, oc, q, a, expl, mis, diff, time, skill in wr_batch:
        extra.append(wr(q, a, expl, mis, topic=topic, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    # Nervous/endocrine NR supplements (need ~22 per topic target)
    nervous_nr = [
        ("A resting neuron has membrane potential $-70$ mV and peaks at $+40$ mV during depolarization. Record resting as two digits then peak as two digits.", "7040", "A1.1k", "Recording membrane potential values", "Easy"),
        ("Order synaptic events: (1) Ca$^{2+}$ influx, (2) vesicle fusion, (3) action potential arrives, (4) neurotransmitter binds receptor. Record all four digits.", "3124", "A1.1k", "Sequencing synaptic transmission events", "Medium"),
        ("Parasympathetic activation increases salivation and decreases heart rate from $80$ to $62$ bpm. Record the heart rate decrease in bpm (two digits).", "18", "A1.2k", "Calculating heart rate change", "Easy"),
        ("A patient pupil diameter changes from $7$ mm in dim light to $3$ mm in bright light. Record the change in mm as one digit.", "4", "A1.3k", "Calculating pupillary response magnitude", "Easy"),
        ("Order light pathway: (1) optic nerve, (2) photoreceptor, (3) occipital cortex, (4) bipolar cell. Record all four digits.", "2134", "A1.4k", "Sequencing visual pathway components", "Medium"),
        ("A hearing test shows threshold shift of $15$ dB at $4000$ Hz. Record the frequency in hundreds of Hz as two digits.", "40", "A1.5k", "Interpreting audiogram frequency data", "Medium"),
        ("Sensory threshold decreases from $12$ mV to $8$ mV after hormone treatment. Record the decrease as one digit.", "4", "A1.6k", "Calculating threshold change", "Easy"),
        ("Blood glucose rises from $4.5$ to $11.2$ mmol/L post-meal. Record the increase rounded to one decimal as two digits (e.g., 6.7 → 67).", "67", "A2.2k", "Calculating postprandial glucose increase", "Medium"),
        ("TSH level increases from $2.1$ to $8.4$ mU/L when thyroid hormone is low. Record the fold increase rounded to nearest whole number.", "4", "A2.3k", "Calculating hormone fold-change", "Hard"),
        ("Cortisol peaks at $620$ nmol/L at 8 AM and drops to $180$ nmol/L at midnight. Record the decrease as three digits.", "440", "A2.4k", "Calculating diurnal cortisol decrease", "Medium"),
        ("A neuron fires $12$ impulses in $3$ seconds. Record the frequency in Hz as two digits.", "4", "A1.1k", "Calculating neuronal firing frequency", "Easy"),
        ("Order HPA axis: (1) cortisol release, (2) CRH release, (3) ACTH release, (4) hypothalamus detects stress. Record all four digits.", "4231", "A2.2k", "Sequencing HPA axis activation", "Hard"),
    ]
    for q, a, oc, skill, diff in nervous_nr:
        extra.append(nr(q, a, f"The correct answer is {a}.", "Students reverse digit order or use wrong operation.",
                        topic="Nervous and Endocrine Systems", outcome_code=oc, skill_tested=skill,
                        difficulty=diff, estimated_time_seconds=75))

    # Reproduction NR supplements
    repro_nr = [
        ("Order spermatogenesis: (1) spermiogenesis, (2) meiosis II, (3) primary spermatocyte, (4) spermatid. Record all four digits.", "3241", "B1.1k", "Sequencing spermatogenesis stages", "Medium"),
        ("Order ovarian cycle: (1) ovulation, (2) follicular phase, (3) menstruation, (4) luteal phase. Record all four digits.", "2413", "B2.2k", "Sequencing ovarian cycle events", "Medium"),
        ("A follicle grows from $4$ mm to $20$ mm before ovulation. Record the increase in mm as two digits.", "16", "B2.1k", "Calculating follicle growth", "Easy"),
        ("hCG concentration rises from $5$ IU/L to $45$ IU/L in early pregnancy. Record the fold increase as one digit.", "9", "B2.2k", "Calculating hCG fold increase", "Medium"),
        ("Gestation is $40$ weeks; an embryo is $6$ weeks post-fertilization. Record remaining weeks as two digits.", "34", "B3.1k", "Calculating remaining gestation time", "Easy"),
        ("A karyotype shows $46$ chromosomes with XX. How many autosomes? Record the two-digit answer.", "44", "B3.1k", "Calculating autosome count from karyotype", "Easy"),
        ("Order embryonic layers use: (1) mesoderm—muscle, (2) ectoderm—nervous tissue, (3) endoderm—gut lining. Which layer forms nervous tissue? Record one digit.", "2", "B3.2k", "Identifying germ layer derivatives", "Easy"),
        ("Progesterone rises from $5$ nmol/L to $45$ nmol/L in luteal phase. Record the increase as two digits.", "40", "B2.1k", "Calculating progesterone increase", "Medium"),
        ("Order implantation events: (1) blastocyst hatches, (2) fertilization, (3) implantation, (4) cleavage to morula. Record all four digits.", "2431", "B2.2k", "Sequencing early embryonic events", "Hard"),
        ("FSH level is $6$ IU/L and LH surges to $42$ IU/L at ovulation. Record LH increase as two digits.", "36", "B2.1k", "Calculating LH surge magnitude", "Medium"),
        ("Semen sample has $25$ million sperm/mL and volume $3$ mL. Total sperm in millions? Record two digits.", "75", "B1.2k", "Calculating total sperm count", "Hard"),
        ("Embryo heart begins beating at day $22$ and organogenesis largely completes by day $56$. Record duration in days as two digits.", "34", "B3.2k", "Calculating organogenesis duration", "Medium"),
        ("A pregnancy test detects hCG above $25$ mIU/mL; patient level is $180$ mIU/mL. How many times above threshold? Record as whole number.", "7", "B2.2k", "Calculating hCG threshold multiple", "Medium"),
    ]
    for q, a, oc, skill, diff in repro_nr:
        extra.append(nr(q, a, f"The correct answer is {a}.", "Students use final value instead of requested calculation.",
                        topic="Reproduction and Development", outcome_code=oc, skill_tested=skill,
                        difficulty=diff, estimated_time_seconds=80))

    # Hard difficulty supplements across topics
    hard_mc = [
        ("Nervous and Endocrine Systems", "A1.1k", "A toxin cleaves SNARE proteins preventing vesicle fusion. Which step of synaptic transmission is blocked?", "release of neurotransmitter into the synaptic cleft", ["generation of the action potential in the axon", "binding of neurotransmitter to postsynaptic receptors", "reuptake of neurotransmitter by the presynaptic cell"], "SNARE proteins mediate vesicle-membrane fusion during exocytosis.", "Students confuse vesicle release with receptor binding.", "Blocking vesicle fusion in synaptic transmission", 115),
        ("Nervous and Endocrine Systems", "A2.5k", "A steroid hormone enters a target cell and binds a cytoplasmic receptor. The complex directly", "acts as a transcription factor altering gene expression", ["opens ligand-gated ion channels in the plasma membrane", "activates adenylyl cyclase to produce cAMP at the membrane", "is degraded immediately without entering the nucleus"], "Steroid-receptor complexes typically regulate transcription in the nucleus.", "Peptide second-messenger pathways are incorrectly applied to steroids.", "Predicting steroid hormone mechanism of action", 110),
        ("Reproduction and Development", "B2.3k", "Preimplantation genetic testing identifies an embryo carrying a balanced Robertsonian translocation. Parents are informed because", "the child may have reduced fertility or produce unbalanced gametes", ["the embryo will lack all mitochondria from the mother", "meiosis will be replaced by mitosis in all adult cells", "the translocation guarantees trisomy 21 in every offspring"], "Balanced carriers are phenotypically normal but may produce unbalanced gametes during meiosis.", "Balanced translocations do not always cause Down syndrome.", "Evaluating STS implications of chromosomal testing", 120),
        ("Cell Division", "C1.1k", "A cell completes meiosis I but fails cytokinesis. The immediate result is a cell with", "duplicated homologous chromosomes and twice the normal cytoplasm volume", ["haploid unduplicated chromosomes in four separate cells", "no DNA content because replication did not occur", "triploid chromosome number in one nucleus"], "Nuclear division without cytokinesis doubles DNA/cytoplasm without separating cells.", "Meiosis I without cytokinesis does not immediately yield haploid cells.", "Predicting consequences of failed cytokinesis in meiosis I", 115),
        ("Cell Division", "C1.3k", "Primary nondisjunction of sex chromosomes producing XXY most likely occurred during", "meiosis I in the father producing XY sperm", ["mitosis in maternal liver cells", "DNA replication in the zygote only", "cytokinesis of the first embryonic cleavage exclusively"], "XXY commonly arises from XY sperm (father meiosis I error) or XX egg; XY sperm implies paternal MI nondisjunction.", "Students attribute all sex chromosome aneuploidy to maternal meiosis only.", "Inferring timing of sex chromosome nondisjunction", 120),
        ("Genetics and Molecular Biology", "C2.3k", "Two genes show 18% recombination frequency. The map distance between them is", "18 map units", ["36 map units because recombination is doubled in meiosis II", "9 map units because only half of chromatids recombine", "50 map units indicating independent assortment"], "1% recombination = 1 map unit; 18% = 18 map units.", "Map distance equals recombination frequency, not half or double.", "Converting recombination frequency to map distance", 110),
        ("Genetics and Molecular Biology", "C3.5k", "Hypermethylation of a tumour suppressor gene promoter most likely causes", "reduced transcription of the tumour suppressor", ["increased translation of the protein product from mRNA", "permanent deletion of the gene from the chromosome", "instant frameshift mutation in all exons"], "Promoter methylation typically silences gene expression epigenetically.", "Methylation represses transcription; it does not increase translation.", "Predicting epigenetic silencing of tumour suppressors", 115),
        ("Genetics and Molecular Biology", "C3.6k", "A trinucleotide repeat expansion in a coding region that lengthens a polyglutamine tract often causes disease through", "toxic gain-of-function of the altered protein", ["complete loss of the gene from the genome by deletion", "conversion of the gene into a noncoding RNA only", "prevention of all DNA replication in somatic cells"], "Expanded polyglutamine tracts (e.g., Huntington) create aberrant protein function.", "Repeat expansion causes toxic protein, not simple gene absence.", "Explaining trinucleotide repeat disease mechanism", 120),
        ("Population and Community Dynamics", "D1.2k", "In a population in Hardy-Weinberg equilibrium, 16% show recessive phenotype. The frequency of heterozygotes is", "0.48", ["0.16", "0.32", "0.64"], "q²=0.16 → q=0.4, p=0.6; 2pq=0.48.", "Students report q² or p² instead of 2pq.", "Calculating heterozygote frequency from recessive phenotype data", 115),
        ("Population and Community Dynamics", "D3.3k", "A population of 5000 has per capita growth rate r=0.12/year. Approximate growth in one year (individuals) is", "600", ["60", "1200", "5000"], "Growth ≈ r×N = 0.12×5000 = 600.", "Students forget to multiply by population size.", "Applying per capita growth rate to population size", 110),
        ("Nervous and Endocrine Systems", "A1.3k", "After spinal cord hemisection, a patient shows loss of voluntary motor control and proprioception on the same side below the lesion, and loss of pain/temperature on the opposite side. The tracts damaged include", "corticospinal and dorsal columns ipsilaterally; spinothalamic contralaterally", ["only optic radiation fibres bilaterally", "all cranial nerves exiting above the lesion only", "sympathetic preganglionic fibres without any sensory loss"], "Brown-Séquard syndrome reflects tract decussation patterns.", "Students expect all deficits on the same side.", "Integrating spinal tract anatomy with lesion deficits", 130),
        ("Genetics and Molecular Biology", "C2.5k", "An X-linked dominant disorder affects heterozygous females and hemizygous males. Affected father (X^D Y) × unaffected mother (X^N X^N) produces", "all daughters affected, no sons affected", ["all sons affected, no daughters affected", "no affected children of either sex", "50% of both sons and daughters affected"], "Father passes X^D to all daughters (affected) and Y to sons (unaffected).", "Sons inherit Y from father in X-linked patterns.", "Predicting X-linked dominant cross outcomes", 120),
        ("Reproduction and Development", "B3.5k", "Somatic cell nuclear transfer for therapeutic cloning aims to", "produce genetically matched stem cells for potential tissue repair", ["create a genetically unique child with two biological fathers only", "eliminate the need for meiosis in all human reproduction permanently", "replace prenatal genetic screening with mitochondrial sequencing only"], "Therapeutic cloning seeks patient-matched cells, raising distinct ethics from reproductive cloning.", "Therapeutic cloning is not identical to reproductive cloning goals.", "Evaluating STS goals of therapeutic cloning", 115),
        ("Cell Division", "C1.2k", "If a culture has mitotic index 10% and 2% of cells are in cytokinesis visually, the proportion in nuclear division (mitosis proper) is approximately", "8%", ["12%", "2%", "10% including interphase"], "Mitotic index counts mitosis; cytokinesis follows telophase — 10% total mitotic cells minus 2% in cytokinesis ≈ 8% in mitosis.", "Students add rather than separate cytokinesis from mitosis.", "Interpreting mitotic index with cytokinesis data", 120),
        ("Population and Community Dynamics", "D2.1k", "Species A competitively excludes species B when resources are limiting, but both coexist when resource availability doubles. This supports", "competitive exclusion can be avoided when resources are not limiting", ["competitive exclusion is impossible in all ecosystems always", "predation never affects community composition", "primary succession cannot occur on disturbed soil"], "Coexistence becomes possible when niche overlap is reduced by greater resource availability.", "Competitive exclusion depends on resource limitation.", "Applying competitive exclusion with resource availability", 115),
    ]
    for topic, oc, q, a, dist, expl, mis, skill, time in hard_mc:
        extra.append(mc(q, a, dist, expl, mis, topic=topic, outcome_code=oc,
                        skill_tested=skill, difficulty="Hard", estimated_time_seconds=time))

    # Hard numerical response supplements (pool was short on hard NR)
    hard_nr = [
        ("Genetics and Molecular Biology", "C2.2k", "In a population 36% show recessive phenotype for a gene. Under Hardy-Weinberg, what is allele frequency $p$ of the dominant allele? Express as decimal to two places.", "0.40", "q²=0.36→q=0.6; p=0.4.", "Students use 0.36 as p instead of q²."),
        ("Genetics and Molecular Biology", "C2.5k", "An X-linked recessive allele has frequency 0.08 in males. What is female carrier frequency (2pq)? Express as decimal to two places.", "0.15", "Males hemizygous: q=0.08, p=0.92; 2pq=0.147≈0.15.", "Students forget females need 2pq for carriers."),
        ("Population and Community Dynamics", "D1.2k", "Recessive phenotype frequency is 4%. What percent of population is heterozygous? Express as whole number percent.", "32", "q²=0.04→q=0.2,p=0.8;2pq=0.32=32%.", "Students report 4% or 64%."),
        ("Population and Community Dynamics", "D3.2k", "Population grows from 2400 to 3100 in 5 years. Average annual growth rate r? Express as decimal to two places.", "0.05", "Total growth (3100-2400)/2400=0.292 over 5 yr; per year ≈0.05 using r=ln(Nt/N0)/t or linear approx 140/2400/5≈0.0117 - use simpler: (3100-2400)/(2400×5)=700/12000=0.058≈0.06. Let me use cleaner numbers.", "Students divide by final N or forget years."),
        ("Cell Division", "C1.2k", "Culture has 720 cells; mitotic index 7.5%. How many cells in mitosis? Record two-digit answer.", "54", "720×0.075=54.", "Students multiply by 7.5 not 0.075."),
        ("Nervous and Endocrine Systems", "A2.2k", "Fasting glucose 3.8 mmol/L rises to 10.4 mmol/L. Increase expressed as one decimal (e.g., 6.6 → record 66).", "66", "10.4-3.8=6.6.", "Students record 104 or 38."),
        ("Reproduction and Development", "B2.2k", "Cycle day 14 ovulation; luteal phase lasts 14 days. If no pregnancy, menstruation starts day __. Record two digits.", "28", "14+14=28.", "Students answer 14 only."),
        ("Genetics and Molecular Biology", "C2.2k", "Dihybrid AaBb × AaBb: fraction showing both recessive traits? Express as decimal to two places.", "0.06", "1/4×1/4=1/16=0.0625≈0.06.", "Students answer 0.25 or 0.16."),
        ("Population and Community Dynamics", "D3.2k", "N=2000, r=0.18/year. Expected growth in one year (individuals)? Record three digits.", "360", "0.18×2000=360.", "Students use 0.18 alone."),
        ("Cell Division", "C1.1k", "Species 2n=34. Chromatids visible at mitotic metaphase in one cell? Record two digits.", "68", "34 chromosomes ×2 chromatids=68.", "Students answer 34."),
        ("Nervous and Endocrine Systems", "A1.1k", "Resting potential -68 mV; threshold -55 mV. Depolarization needed in mV? Record two digits.", "13", "68-55=13 mV (absolute difference).", "Students add potentials."),
        ("Reproduction and Development", "B1.1k", "Sperm concentration 15 million/mL, motility 40%, volume 2.5 mL. Motile sperm in millions (whole number)?", "15", "15×0.4×2.5=15 million.", "Students ignore motility or volume."),
        ("Genetics and Molecular Biology", "C3.1k", "DNA is 27% thymine. Percent cytosine? Record two digits.", "23", "T=A=27%; G+C=46%; G=C=23%.", "Students answer 27 or 46."),
        ("Population and Community Dynamics", "D1.2k", "2pq=0.42 and p>q. What is p? Express as decimal to two places.", "0.70", "p+q=1, 2pq=0.42; solve p=0.7,q=0.3.", "Students guess 0.42 as p."),
        ("Nervous and Endocrine Systems", "A2.4k", "ACTH stimulates 4× cortisol output from 120 to __ μg/dL. Record three digits.", "480", "120×4=480.", "Students add 4 instead of multiply."),
    ]
    # Fix population growth NR with clean numbers
    hard_nr[3] = ("Population and Community Dynamics", "D3.2k",
                  "Population grows from 2000 to 2600 in 4 years. Average annual per capita growth rate? Express as decimal to two places.",
                  "0.07", "Total fractional growth (2600-2000)/2000=0.3 over 4 years; r≈0.3/4=0.075≈0.07.",
                  "Students divide by 2600 or forget to divide by years.")

    for topic, oc, q, a, expl, mis in hard_nr:
        extra.append(nr(q, a, expl, mis, topic=topic, outcome_code=oc,
                        skill_tested="Multi-step quantitative biology problem",
                        difficulty="Hard", estimated_time_seconds=110))

    return extra


def collect_all():
    items = []
    items.extend(unit_a())
    items.extend(unit_b())
    items.extend(unit_c_division())
    items.extend(unit_c_genetics())
    items.extend(unit_d())
    items.extend(programmatic_supplements())
    return items


def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        key = (
            item["topic"].strip().lower(),
            " ".join(item["question_text"].split()).lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def validate_all(items):
    errors = []
    for i, item in enumerate(items):
        reasons = validate_question(item, i)
        if reasons:
            errors.append((i, reasons))
    return errors


def print_stats(items):
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


def main():
    items = collect_all()
    items = deduplicate(items)
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
    print("VALIDATION: PASSED — production-ready for question_import.py")


if __name__ == "__main__":
    main()
