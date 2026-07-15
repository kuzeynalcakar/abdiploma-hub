"""Genetics and Molecular Biology — Science 30 original questions."""

from .helpers import mc, nr

TOPIC = "Genetics and Molecular Biology"


def _base_mc():
    return [
        mc(
            "During meiosis, homologous chromosomes pair and exchange segments in a process called",
            "crossing over",
            ["DNA replication in the S phase", "translation at the ribosome", "binary fission in bacteria"],
            "Crossing over during prophase I increases genetic variation in gametes.",
            "Replication occurs before meiosis; translation is protein synthesis, not chromosome exchange.",
            topic=TOPIC, outcome_code="A3.1k",
            skill_tested="Identifying meiotic recombination process",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "A heterozygous individual (Aa) for a trait with complete dominance will express",
            "the dominant phenotype",
            ["the recessive phenotype only", "both phenotypes simultaneously in all cells", "no phenotype because alleles cancel"],
            "Complete dominance means one dominant allele masks recessive in heterozygotes.",
            "Recessive phenotype requires homozygous recessive genotype.",
            topic=TOPIC, outcome_code="A3.2k",
            skill_tested="Applying dominance rules to heterozygous genotype",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Hemophilia is inherited in a pattern where affected males pass the allele to",
            "all daughters who become carriers but not to sons",
            ["all sons who become carriers", "no children of either sex", "only daughters who are always affected"],
            "X-linked recessive: affected father passes X to daughters (carriers); sons receive Y from father.",
            "Sons inherit father's Y chromosome, not his X-linked allele.",
            topic=TOPIC, outcome_code="A3.3k",
            skill_tested="Predicting X-linked inheritance from affected father",
            difficulty="Hard", estimated_time_seconds=110,
        ),
        mc(
            "In the DNA double helix, adenine pairs with",
            "thymine through two hydrogen bonds",
            ["cytosine through three hydrogen bonds", "guanine through two hydrogen bonds", "uracil in the permanent DNA strand"],
            "Complementary base pairing: A-T (2 bonds), G-C (3 bonds) in DNA.",
            "A pairs with T, not C or G; uracil replaces thymine only in RNA.",
            topic=TOPIC, outcome_code="A3.4k",
            skill_tested="Recalling DNA complementary base pairing rules",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "The enzyme DNA polymerase functions during replication to",
            "add nucleotides to the growing strand using the template strand",
            ["break hydrogen bonds between bases permanently", "translate mRNA into protein at the ribosome", "package DNA into gametes during fertilization"],
            "DNA polymerase synthesizes new DNA by adding complementary nucleotides.",
            "Helicase separates strands; polymerase builds new strands.",
            topic=TOPIC, outcome_code="A3.5k",
            skill_tested="Describing DNA polymerase role in replication",
            difficulty="Medium", estimated_time_seconds=75,
        ),
        mc(
            "A point mutation that substitutes one nucleotide may result in",
            "a different amino acid in the protein sequence",
            ["complete destruction of the cell membrane", "elimination of all chromosomes", "conversion of DNA to RNA permanently"],
            "Missense mutations change codons, potentially altering the polypeptide sequence.",
            "Point mutations affect specific nucleotides, not entire chromosomes or membranes.",
            topic=TOPIC, outcome_code="A3.8k",
            skill_tested="Relating point mutation to protein alteration",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Sickle-cell anemia results from a mutation affecting",
            "the beta-globin chain of hemoglobin",
            ["the structure of the ribosome only", "the number of chromosomes in each cell", "the function of motor neurons exclusively"],
            "A single nucleotide change in the HBB gene alters hemoglobin shape and RBC morphology.",
            "Sickle cell is a specific hemoglobin gene mutation, not a chromosome number disorder.",
            topic=TOPIC, outcome_code="A3.8k",
            skill_tested="Connecting sickle-cell disease to hemoglobin mutation",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Gene therapy aims to",
            "introduce functional copies of genes to treat genetic disorders",
            ["eliminate all bacteria using vaccines", "increase heart rate through exercise", "produce acid rain in laboratory settings"],
            "Gene therapy replaces or supplements defective genes to restore normal protein function.",
            "Vaccines and exercise are unrelated to direct gene replacement therapy.",
            topic=TOPIC, outcome_code="A3.9k",
            skill_tested="Defining purpose of gene therapy",
            difficulty="Easy", estimated_time_seconds=65,
        ),
        mc(
            "Genetic engineering of crop plants to resist herbicides involves",
            "inserting recombinant DNA to alter the plant genome",
            ["selective breeding without any DNA modification", "changing soil pH to eliminate all genes", "removing all chromosomes from root cells"],
            "Recombinant DNA technology introduces specific genes conferring desired traits.",
            "Genetic engineering modifies DNA directly, beyond traditional breeding alone.",
            topic=TOPIC, outcome_code="A3.9k",
            skill_tested="Distinguishing genetic engineering from traditional breeding",
            difficulty="Medium", estimated_time_seconds=80,
        ),
        mc(
            "Bacterial resistance to antibiotics can spread rapidly through",
            "plasmid transfer between bacteria via conjugation",
            ["osmosis of water across the cell wall only", "photosynthesis in the bacterial chloroplast", "binary fission of red blood cells"],
            "Resistance genes on plasmids can transfer horizontally between bacterial cells.",
            "Bacteria lack chloroplasts; RBCs are eukaryotic and do not conjugate.",
            topic=TOPIC, outcome_code="A3.10k",
            skill_tested="Explaining horizontal gene transfer of resistance",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "The central dogma of molecular genetics describes the flow",
            "from DNA to RNA to protein",
            ["from protein to DNA to lipid", "from RNA to DNA only with no protein step", "from glucose to ATP without genetic involvement"],
            "Information flows DNA → (transcription) → RNA → (translation) → protein.",
            "Proteins do not normally reverse-transcribe to DNA in standard cell processes.",
            topic=TOPIC, outcome_code="A3.6k",
            skill_tested="Stating central dogma information flow",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        mc(
            "Enzymes are proteins that function primarily as",
            "biological catalysts lowering activation energy",
            ["structural fibres in hair and nails only", "long-term energy storage molecules", "genetic information carriers in the nucleus"],
            "Enzymes speed biochemical reactions without being consumed.",
            "Keratin provides structure; fats store energy; DNA carries genetic info.",
            topic=TOPIC, outcome_code="A3.7k",
            skill_tested="Identifying catalytic role of enzyme proteins",
            difficulty="Easy", estimated_time_seconds=55,
        ),
        mc(
            "Stem-cell research raises ethical debate primarily because",
            "the source and use of certain stem cells involves moral considerations about potential life",
            ["stem cells cannot differentiate into any cell type", "all stem cells are identical to mature neurons", "stem cells eliminate the need for all medical research"],
            "Ethical concerns focus on embryo-derived cells and consent, balanced against therapeutic potential.",
            "Stem cells can differentiate; they are not identical to all mature cells.",
            topic=TOPIC, outcome_code="A3.2sts",
            skill_tested="Evaluating ethical dimensions of stem-cell research",
            difficulty="Medium", estimated_time_seconds=90,
        ),
        mc(
            "A test cross (Aa × aa) is used to determine whether a dominant phenotype individual is",
            "heterozygous or homozygous dominant",
            ["haploid or diploid", "male or female regardless of genotype", "infected with a virus or not"],
            "Crossing with homozygous recessive reveals hidden recessive alleles in offspring ratios.",
            "Test crosses determine genotype, not sex or infection status.",
            topic=TOPIC, outcome_code="A3.2k",
            skill_tested="Explaining purpose of test cross in genetics",
            difficulty="Medium", estimated_time_seconds=85,
        ),
        mc(
            "Messenger RNA differs from DNA in that mRNA typically contains",
            "uracil instead of thymine and is single-stranded",
            ["deoxyribose sugar and a double helix", "thymine instead of uracil in a permanent double helix", "no nucleotides at all"],
            "RNA uses ribose, uracil, and is usually single-stranded during transcription products.",
            "DNA has deoxyribose and thymine; mRNA is transcribed from DNA template.",
            topic=TOPIC, outcome_code="A3.4k",
            skill_tested="Comparing mRNA structure to DNA",
            difficulty="Medium", estimated_time_seconds=75,
        ),
    ]


def _parameterized():
    items = []
    crosses = [
        ("Aa", "Aa", 0.25, "homozygous dominant (AA)"),
        ("Aa", "aa", 0.50, "heterozygous (Aa)"),
        ("Bb", "Bb", 0.25, "homozygous recessive (bb)"),
        ("Dd", "dd", 0.50, "heterozygous (Dd)"),
        ("Ee", "Ee", 0.75, "dominant phenotype"),
        ("Ff", "ff", 0.50, "heterozygous (Ff)"),
    ]
    for p1, p2, prob, desc in crosses:
        items.append(nr(
            f"A monohybrid cross between parents with genotypes {p1} and {p2} (complete dominance) "
            f"produces many offspring. What is the expected probability of {desc}? "
            f"Express as a decimal.",
            f"{prob:.2f}",
            f"Punnett square for {p1} × {p2} gives probability {prob} for {desc}.",
            f"Students misread the {p1} × {p2} Punnett square or report a phenotype ratio instead of decimal probability for {desc}.",
            topic=TOPIC, outcome_code="A3.2k",
            skill_tested=f"Calculating {desc} probability in {p1} × {p2} monohybrid cross",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for codons in ["AUG"]:
        items.append(mc(
            f"The mRNA codon {codons} typically functions as",
            "a start codon initiating translation with methionine",
            ["a stop codon ending all protein synthesis", "a codon coding for three amino acids at once", "an intron removed before mRNA leaves the nucleus"],
            f"{codons} is the start codon; translation begins at this triplet in the genetic code table.",
            "Students confuse start codons (AUG) with stop codons (UAA, UAG, UGA).",
            topic=TOPIC, outcome_code="A3.6k",
            skill_tested="Identifying start codon function in translation",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for percent in [25, 50]:
        items.append(nr(
            f"In a population survey, {percent}% of individuals carry a recessive allele for a genetic trait. "
            f"What percentage do NOT carry the recessive allele?",
            str(100 - percent),
            f"100% − {percent}% = {100 - percent}%.",
            "Students report the given percentage instead of the complement.",
            topic=TOPIC, outcome_code="A3.3s",
            skill_tested="Calculating allele frequency complement",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    mutation_mc = [
        ("A frameshift mutation caused by inserting one nucleotide typically alters", "every amino acid downstream of the insertion site", ["only the first amino acid with no downstream effect", "the number of chromosomes to zero", "blood type without affecting DNA"], "Insertion shifts the reading frame, changing all subsequent codons.", "Frameshift affects downstream sequence, not just one codon.", "A3.8k", "Predicting frameshift mutation consequence", "Hard", 100),
        ("Down syndrome (trisomy 21) is an example of", "chromosomal number abnormality", ["a single point mutation in one base only", "a bacterial plasmid transfer event", "acid-base neutralization in blood"], "Trisomy involves an extra copy of chromosome 21.", "Down syndrome is chromosomal, not a point mutation or bacterial event.", "A3.8k", "Classifying chromosomal disorder type", "Medium", 80),
        ("CRISPR-Cas9 technology allows scientists to", "edit specific DNA sequences in living cells", ["measure blood pressure non-invasively", "convert AC electricity to DC in transformers", "rank acids by pH without any genetic tools"], "CRISPR targets and modifies precise genomic sequences.", "CRISPR is a gene-editing tool, not a medical device or chemistry method.", "A3.9k", "Describing CRISPR gene editing application", "Medium", 85),
        ("Natural selection contributes to antibiotic resistance when", "bacteria with resistance alleles survive and reproduce after antibiotic exposure", ["all bacteria die regardless of genotype", "antibiotics speed up DNA replication in all cells equally", "vaccines introduce plasmids to human cells"], "Selection favours resistant survivors; resistant populations increase over generations.", "Antibiotics select survivors; they do not kill all bacteria equally.", "A3.10k", "Explaining natural selection in antibiotic resistance", "Medium", 85),
        ("Huntington disease is inherited as an autosomal dominant disorder, meaning", "one copy of the mutant allele can cause the disease", ["two copies of the recessive allele are required", "only females can inherit the disorder", "the disease is caused by a bacterial plasmid"], "Dominant disorders manifest with at least one disease allele on an autosome.", "Recessive requires two copies; Huntington is autosomal dominant.", "A3.8k", "Applying autosomal dominant inheritance pattern", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, time in mutation_mc:
        items.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                        skill_tested=skill, difficulty=diff, estimated_time_seconds=time))

    return items


def questions():
    return _base_mc() + _parameterized()
