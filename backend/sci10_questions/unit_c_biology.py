"""Cycling of Matter in Living Systems — Science 10 original questions."""

from .helpers import mc, nr

TOPIC = "Cycling of Matter in Living Systems"


def questions():
    q = []

    # --- Cell theory and microscopy (C1) ---
    q.append(mc(
        "Which statement is part of the modern cell theory?",
        "all cells arise from pre-existing cells",
        ["all organisms can arise from non-living matter", "only plants are composed of cells", "viruses are the smallest functional units of life"],
        "Cell theory states that all cells come from pre-existing cells, replacing spontaneous generation.",
        "Spontaneous generation was disproven; viruses are not considered complete cells.",
        topic=TOPIC, outcome_code="C1.1k",
        skill_tested="Stating a principle of cell theory",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Robert Hooke's observations of cork contributed to cell theory because he",
        "described small compartments he called cells in plant tissue",
        ["proved that bacteria cause disease", "invented the electron microscope", "showed that animal cells lack walls"],
        "Hooke viewed dead cork under a compound microscope and named the box-like structures cells.",
        "Hooke did not work with bacteria or electron microscopes.",
        topic=TOPIC, outcome_code="C1.1k",
        skill_tested="Linking Hooke's work to cell theory development",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "Louis Pasteur's swan-neck flask experiments supported cell theory by demonstrating that",
        "microorganisms do not spontaneously appear in sterile broth when contamination is prevented",
        ["all life requires sunlight for energy", "cells contain a nucleus in every organism", "DNA carries genetic information"],
        "Pasteur showed broth remained sterile unless exposed to airborne microbes, refuting spontaneous generation.",
        "Pasteur's work addressed origin of microbes, not photosynthesis or DNA structure.",
        topic=TOPIC, outcome_code="C1.1k",
        skill_tested="Explaining Pasteur's role in disproving spontaneous generation",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Schleiden and Schwann contributed to cell theory by proposing that",
        "plants and animals are composed of cells",
        ["only single-celled organisms are alive", "cells generate spontaneously in soil", "organelles are larger than cells"],
        "Schleiden (plants) and Schwann (animals) generalized that all living organisms are cellular.",
        "They extended cell theory to multicellular organisms, not just single-celled ones.",
        topic=TOPIC, outcome_code="C1.1k",
        skill_tested="Identifying Schleiden and Schwann contributions",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "Viruses are considered sub-cellular particles rather than cells because they",
        "require a host cell to reproduce and lack independent metabolism",
        ["always contain chloroplasts for photosynthesis", "are larger than most eukaryotic cells", "have cell walls made of cellulose"],
        "Viruses lack cellular machinery and cannot carry out life processes outside a host.",
        "Viruses are much smaller than cells and lack plant cell structures.",
        topic=TOPIC, outcome_code="C1.1k",
        skill_tested="Distinguishing viruses from cells",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "The invention of the electron microscope most significantly improved cell study by",
        "revealing ultrastructural details of organelles not visible with light microscopy",
        ["eliminating the need for staining techniques", "allowing observation of living cells at low magnification only", "proving that prokaryotes have nuclei"],
        "Electron microscopes use electron beams to resolve structures such as ribosomes and ER at nanometre scale.",
        "Staining is still used; EM often requires fixed specimens; prokaryotes lack nuclei.",
        topic=TOPIC, outcome_code="C1.2k",
        skill_tested="Describing impact of electron microscopy on cell biology",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Confocal laser scanning microscopy (CLSM) is useful for studying cells because it",
        "creates sharp optical sections and can construct three-dimensional images of fluorescently labelled structures",
        ["uses only visible light at magnifications below 10×", "destroys all cellular membranes instantly", "replaces the need for any knowledge of cell theory"],
        "CLSM reduces out-of-focus blur and enables detailed 3D reconstruction of labelled organelles.",
        "CLSM uses lasers and fluorescence; it complements rather than replaces cell theory.",
        topic=TOPIC, outcome_code="C1.2k",
        skill_tested="Explaining advantages of confocal microscopy",
        difficulty="Hard", estimated_time_seconds=90,
    ))
    q.append(mc(
        "Staining techniques such as iodine or methylene blue are used in light microscopy to",
        "increase contrast so cellular structures are easier to distinguish",
        ["kill all cells by osmotic lysis only", "permanently change DNA into RNA", "magnify specimens beyond the lens limit"],
        "Stains bind specific components, improving visibility of nuclei, starch granules, or cytoplasm.",
        "Staining improves contrast; magnification is determined by lenses, not stains.",
        topic=TOPIC, outcome_code="C1.2k",
        skill_tested="Describing purpose of biological staining",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Research on transport across cell membranes at the molecular level may investigate",
        "how carrier proteins move ions against a concentration gradient",
        ["how the Sun produces nuclear fusion in its core", "how tectonic plates move continents", "how atmospheric pressure creates weather fronts"],
        "Membrane transport research focuses on channels, pumps, and gradients at the cellular level.",
        "Solar fusion, plate tectonics, and weather are not cell membrane topics.",
        topic=TOPIC, outcome_code="C1.3k",
        skill_tested="Identifying molecular-level cell research areas",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "DNA and gene mapping research relates to cell biology because it",
        "helps explain how genetic instructions in the nucleus control cell functions",
        ["proves that cells can form from non-living chemicals in air", "shows that plant cells lack mitochondria", "demonstrates that diffusion requires ATP in all cases"],
        "Gene mapping links nuclear DNA to proteins and processes carried out by organelles.",
        "Gene mapping does not address spontaneous generation or universal ATP use in diffusion.",
        topic=TOPIC, outcome_code="C1.3k",
        skill_tested="Connecting gene mapping to cellular function",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Improved microscopy has benefited medical diagnosis by enabling clinicians to",
        "identify abnormal cell morphology in tissue biopsies",
        ["predict earthquakes from cell vibrations", "measure the mass of entire ecosystems directly", "eliminate all bacterial infections with light alone"],
        "Microscopic examination of cells helps detect cancerous and diseased tissue changes.",
        "Microscopy does not predict earthquakes or measure ecosystem mass.",
        topic=TOPIC, outcome_code="C1.1sts",
        skill_tested="Relating microscopy advances to medical applications",
        difficulty="Easy", estimated_time_seconds=65,
    ))

    # --- Organelles and cell as open system (C2) ---
    q.append(mc(
        "The nucleus of a eukaryotic cell primarily functions to",
        "store DNA and control activities such as protein synthesis",
        ["carry out aerobic respiration for ATP production", "digest worn-out organelles with enzymes", "perform photosynthesis using chlorophyll"],
        "The nucleus contains genetic material and regulates gene expression for the cell.",
        "Respiration occurs in mitochondria; digestion in lysosomes; photosynthesis in chloroplasts.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying nucleus function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Mitochondria are described as the powerhouse of the cell because they",
        "release energy from nutrients through aerobic cellular respiration",
        ["synthesize lipids for the cell membrane only", "package proteins for export from the cell", "store water and maintain turgor pressure"],
        "Mitochondria produce ATP by breaking down glucose in the presence of oxygen.",
        "Lipid synthesis occurs in ER; packaging in Golgi; water storage in vacuoles.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying mitochondrion function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Chloroplasts in plant cells function to",
        "convert light energy into chemical energy during photosynthesis",
        ["break down fatty acids in the absence of oxygen", "transport sugars through the phloem", "regulate opening and closing of stomata directly"],
        "Chloroplasts contain chlorophyll and enzymes for the light-dependent and Calvin cycles.",
        "Fatty acid breakdown is not photosynthesis; phloem transport is separate from chloroplasts.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying chloroplast function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Ribosomes function in cells by",
        "assembling amino acids into proteins according to mRNA instructions",
        ["replicating DNA before cell division", "modifying and sorting proteins for secretion", "maintaining cell shape with microtubules only"],
        "Ribosomes translate genetic code into polypeptide chains on mRNA templates.",
        "DNA replication occurs in the nucleus; sorting in Golgi; shape from cytoskeleton.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying ribosome function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "The endoplasmic reticulum (ER) is involved in",
        "synthesizing lipids and proteins and transporting them within the cell",
        ["dividing chromosomes during mitosis", "capturing light for carbohydrate production", "creating turgor pressure in root hairs"],
        "Rough ER has ribosomes for protein synthesis; smooth ER synthesizes lipids and detoxifies.",
        "Mitosis uses spindle fibres; light capture is in chloroplasts; turgor involves vacuoles and water.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying endoplasmic reticulum function",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "The Golgi apparatus modifies and packages substances primarily for",
        "secretion from the cell or delivery to other organelles",
        ["ATP synthesis through the electron transport chain", "splitting water during the light reactions", "replicating circular prokaryotic DNA"],
        "Golgi receives vesicles from ER, processes contents, and ships them in new vesicles.",
        "ATP synthesis is mitochondrial; water splitting is photosynthetic; prokaryotes lack Golgi.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying Golgi apparatus function",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "Lysosomes contain hydrolytic enzymes that",
        "break down damaged organelles and engulfed materials",
        ["build cellulose cell walls in plant cells", "carry oxygen bound to heme groups", "synthesize messenger RNA from DNA templates"],
        "Lysosomes digest macromolecules and recycle cellular components.",
        "Cell walls are built outside the cell; hemoglobin is in red blood cells; mRNA synthesis is nuclear.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying lysosome function",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "A large central vacuole in plant cells helps maintain",
        "turgor pressure against the cell wall",
        ["genetic stability by storing chromosomes", "oxygen transport to mitochondria", "active transport using carrier proteins only"],
        "Water-filled vacuoles press the cytoplasm against the rigid wall, keeping cells firm.",
        "Chromosomes are in the nucleus; oxygen diffuses; vacuoles store water, not exclusively active transport.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Identifying vacuole function in plant cells",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "Plant cells differ from typical animal cells because plant cells have",
        "a rigid cell wall and chloroplasts in green tissues",
        ["centrioles in every cell type for photosynthesis", "no membrane-bound nucleus", "mitochondria replaced entirely by chloroplasts"],
        "Plant cells have cellulose walls and often chloroplasts; animal cells lack walls and chloroplasts.",
        "Plant cells still have nuclei and mitochondria; centrioles are not used for photosynthesis.",
        topic=TOPIC, outcome_code="C2.5k",
        skill_tested="Comparing plant and animal cell structures",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "The complementary relationship between plant and animal cells is illustrated by",
        "plants producing O₂ and carbohydrates while animals consume O₂ and organic nutrients",
        ["both cell types performing identical functions in all tissues", "animal cells carrying out photosynthesis in leaves", "plant cells lacking any need for mitochondria"],
        "Plant photosynthesis produces food and oxygen used by animal respiration; cycles are complementary.",
        "Animal cells do not photosynthesize; plant cells still respire using mitochondria.",
        topic=TOPIC, outcome_code="C2.5k",
        skill_tested="Describing complementary roles of plant and animal cells",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "A cell is considered an open system because it",
        "continuously exchanges matter and energy with its surroundings",
        ["is completely isolated from environmental changes", "never releases waste products", "stores all nutrients permanently without turnover"],
        "Open systems take in nutrients, release wastes, and transfer energy through metabolic pathways.",
        "Isolated cells would not survive; waste excretion and nutrient uptake are essential.",
        topic=TOPIC, outcome_code="C2.3k",
        skill_tested="Describing the cell as an open system",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "The fluid-mosaic model describes the cell membrane as",
        "a phospholipid bilayer with embedded proteins that can move laterally",
        ["a rigid cellulose wall surrounding all cells", "a single layer of starch molecules", "an impermeable barrier with no protein channels"],
        "Membrane proteins and lipids form a dynamic bilayer allowing selective transport.",
        "Cellulose walls are in plants; membranes are lipid-based, not starch; channels exist.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Describing fluid-mosaic membrane structure",
        difficulty="Medium", estimated_time_seconds=75,
    ))

    # --- Diffusion, osmosis, and transport (C2) ---
    q.append(mc(
        "Diffusion across a cell membrane occurs when",
        "particles move from an area of higher concentration to an area of lower concentration",
        ["ATP is always required for each particle crossing", "particles move against their concentration gradient", "only large proteins can pass through lipid bilayers unaided"],
        "Diffusion is passive movement down a concentration gradient until equilibrium.",
        "Diffusion is passive and does not require ATP; it moves down, not against, gradients.",
        topic=TOPIC, outcome_code="C2.1k",
        skill_tested="Defining diffusion in cellular context",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Osmosis is best defined as",
        "the diffusion of water across a selectively permeable membrane",
        ["active transport of glucose using carrier proteins", "movement of ions against a gradient using ATP", "bulk transport of solids by phagocytosis only"],
        "Osmosis specifically describes water movement in response to water potential differences.",
        "Glucose carrier transport and phagocytosis are distinct from osmosis.",
        topic=TOPIC, outcome_code="C2.1k",
        skill_tested="Defining osmosis",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Active transport differs from passive diffusion because active transport",
        "moves substances against a concentration gradient using energy from ATP",
        ["always moves substances down a gradient without energy", "only occurs in dead cells with ruptured membranes", "requires no protein carriers in the membrane"],
        "Carrier proteins powered by ATP pump ions or molecules to higher concentration regions.",
        "Passive transport moves down gradients; living cells use active transport with proteins.",
        topic=TOPIC, outcome_code="C2.1k",
        skill_tested="Comparing active and passive transport",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "A red blood cell placed in distilled water will swell and may lyse because",
        "water enters the cell by osmosis toward the higher solute concentration inside",
        ["salt leaves the cell by active transport only", "the membrane becomes completely impermeable to water", "distilled water has a lower water concentration than the cytoplasm"],
        "Distilled water is hypotonic; water enters until the membrane ruptures.",
        "Distilled water has higher water concentration outside; water enters, salt does not leave primarily.",
        topic=TOPIC, outcome_code="C2.2k",
        skill_tested="Predicting osmotic effects on animal cells",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "A plant cell in a hypertonic solution may undergo plasmolysis, which means",
        "the cell membrane pulls away from the cell wall as water leaves by osmosis",
        ["the cell wall dissolves completely", "chloroplasts multiply rapidly", "the nucleus exits through the cell wall"],
        "Water loss shrinks the protoplast away from the rigid wall while the wall remains.",
        "The cell wall stays intact; plasmolysis affects membrane position, not organelle exit.",
        topic=TOPIC, outcome_code="C2.2k",
        skill_tested="Explaining plasmolysis in plant cells",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Facilitated diffusion uses carrier proteins to",
        "move specific molecules down their concentration gradient without ATP",
        ["pump sodium ions out of the cell against a gradient", "digest proteins inside lysosomes", "synthesize ATP in the cytoplasm"],
        "Facilitated diffusion is passive transport through channel or carrier proteins.",
        "Pumping against gradients is active transport; lysosomes digest; ATP synthesis is in mitochondria.",
        topic=TOPIC, outcome_code="C2.1k",
        skill_tested="Distinguishing facilitated diffusion from active transport",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Endocytosis allows a cell to",
        "take in large particles or liquids by engulfing them with the membrane",
        ["release wastes by passive diffusion only", "replicate DNA without using the nucleus", "photosynthesize using external chloroplasts"],
        "Endocytosis forms vesicles that bring materials into the cytoplasm.",
        "Endocytosis is import, not passive waste release or external photosynthesis.",
        topic=TOPIC, outcome_code="C2.2k",
        skill_tested="Describing endocytosis as bulk transport",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "Exocytosis is used by cells to",
        "secrete materials such as proteins by fusing vesicles with the plasma membrane",
        ["take in water when placed in hypertonic solution", "break down starch in the chloroplast stroma", "duplicate chromosomes during interphase"],
        "Vesicles from Golgi fuse with the membrane, releasing contents outside the cell.",
        "Water uptake in hypertonic solutions decreases; starch breakdown and DNA replication differ.",
        topic=TOPIC, outcome_code="C2.2k",
        skill_tested="Describing exocytosis function",
        difficulty="Medium", estimated_time_seconds=70,
    ))
    q.append(mc(
        "Equilibrium in diffusion across a membrane is reached when",
        "net movement of particles in all directions is balanced",
        ["all particles stop moving completely", "active transport pumps reverse direction permanently", "the membrane becomes thicker"],
        "At equilibrium, random motion continues but there is no net change in concentration.",
        "Particles still move at equilibrium; membrane thickness is unrelated.",
        topic=TOPIC, outcome_code="C2.6k",
        skill_tested="Explaining equilibrium during diffusion",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Dialysis machines for kidney patients apply membrane transport principles by",
        "using a semi-permeable membrane to remove waste from blood while retaining cells and proteins",
        ["forcing all blood cells through pores into dialysate", "adding glucose to blood by spontaneous generation", "preventing any water movement across membranes"],
        "Dialysis relies on diffusion of small wastes across a membrane while large blood components stay.",
        "Blood cells are retained; glucose is controlled, not generated; water can move.",
        topic=TOPIC, outcome_code="C2.7k",
        skill_tested="Applying dialysis as a membrane transport application",
        difficulty="Medium", estimated_time_seconds=85,
    ))
    q.append(mc(
        "Desalination by reverse osmosis uses pressure to",
        "force water through a membrane while leaving dissolved salts behind",
        ["increase salt concentration in drinking water", "destroy all membranes in seawater", "convert salt ions directly into glucose"],
        "Applied pressure overcomes osmotic pressure, allowing pure water to pass the filter.",
        "Desalination removes salt; it does not create glucose or destroy all membranes.",
        topic=TOPIC, outcome_code="C2.7k",
        skill_tested="Applying reverse osmosis in desalination",
        difficulty="Medium", estimated_time_seconds=85,
    ))
    q.append(mc(
        "Honey has been used traditionally as an antibacterial agent partly because its",
        "high solute concentration creates osmotic conditions that dehydrate microbes",
        ["low sugar content promotes bacterial growth", "colour reflects high chlorophyll content", "fluid-mosaic structure blocks all diffusion"],
        "Hypertonic honey draws water from bacteria by osmosis, inhibiting their growth.",
        "Honey is high in sugar; it lacks chlorophyll; osmosis, not membrane model, explains effect.",
        topic=TOPIC, outcome_code="C2.7k",
        skill_tested="Connecting osmosis to traditional antibacterial use of honey",
        difficulty="Medium", estimated_time_seconds=80,
    ))

    # --- Cell size and surface area to volume (C2.8k) ---
    q.append(mc(
        "As a cell grows larger, its surface area to volume ratio generally",
        "decreases, limiting efficient exchange of materials",
        ["increases without limit, improving exchange indefinitely", "remains constant regardless of cell size", "determines the number of chromosomes in the nucleus"],
        "Volume increases faster than surface area, reducing relative membrane area for transport.",
        "SA:V decreases as size increases; chromosome number is genetically determined.",
        topic=TOPIC, outcome_code="C2.8k",
        skill_tested="Relating cell size to surface area-to-volume ratio",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Root hair cells are long and narrow extensions that increase",
        "surface area for absorption of water and minerals",
        ["volume without any increase in membrane area", "the rate of photosynthesis in the root cortex", "genetic material per cell for faster division"],
        "Elongated shape maximizes contact with soil water for uptake by osmosis and active transport.",
        "Root hairs absorb water; photosynthesis occurs mainly in leaves; shape does not change DNA amount.",
        topic=TOPIC, outcome_code="C2.8k",
        skill_tested="Explaining root hair shape and function",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Flat, thin red blood cells are adapted for",
        "maximizing surface area for gas exchange relative to cell volume",
        ["storing large quantities of chlorophyll", "anchoring plants in rocky soil", "producing cellulose for cell walls"],
        "Biconcave disc shape increases SA:V for efficient O₂ and CO₂ diffusion.",
        "RBCs lack chlorophyll, anchoring functions, and cellulose walls.",
        topic=TOPIC, outcome_code="C2.8k",
        skill_tested="Relating red blood cell shape to gas exchange",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Multicellular organisms overcome the size limits of single cells partly by",
        "specializing different cells for exchange, transport, and support",
        ["eliminating all need for membranes", "making every cell identical in shape and function", "preventing diffusion in all tissues"],
        "Specialized tissues maintain SA:V advantages at the organism level through structures like leaves and roots.",
        "Membranes remain essential; specialization requires different cell types; diffusion still occurs.",
        topic=TOPIC, outcome_code="C3.1k",
        skill_tested="Explaining multicellular organization and cell size limits",
        difficulty="Medium", estimated_time_seconds=85,
    ))

    # --- Plant structure, transport, gas exchange (C3) ---
    q.append(mc(
        "Palisade mesophyll cells in leaves are located",
        "just beneath the upper epidermis where they receive abundant light for photosynthesis",
        ["deep in the root cortex near xylem vessels only", "inside the phloem sieve tubes", "exclusively in the stem pith with no chloroplasts"],
        "Palisade tissue is packed with chloroplasts in the upper leaf layer for maximum light capture.",
        "Roots absorb water; phloem transports sugar; palisade cells contain chloroplasts.",
        topic=TOPIC, outcome_code="C3.2k",
        skill_tested="Identifying palisade mesophyll location and function",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "Spongy mesophyll cells in leaves contribute to gas exchange because they",
        "have air spaces that allow CO₂ and O₂ to diffuse to photosynthetic cells",
        ["form a waxy cuticle on the leaf surface", "produce lignin for structural support of stems", "actively pump water from soil into xylem"],
        "Intercellular air spaces in spongy tissue connect to stomata for gas diffusion.",
        "Cuticle is epidermal; lignin is in xylem walls; soil water uptake is in roots.",
        topic=TOPIC, outcome_code="C3.2k",
        skill_tested="Describing spongy mesophyll role in gas exchange",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Guard cells control gas exchange by",
        "changing shape to open or close stomatal pores between them",
        ["producing lignin in vessel walls", "transporting sugars through sieve tubes", "replacing xylem during secondary growth"],
        "Turgor changes in guard cells regulate stomatal aperture for CO₂ entry and water loss.",
        "Lignin and sieve tubes are separate structures; guard cells regulate stomata.",
        topic=TOPIC, outcome_code="C3.4k",
        skill_tested="Explaining guard cell control of stomata",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Xylem tissue primarily transports",
        "water and dissolved minerals upward from roots to shoots",
        ["sucrose produced in leaves to roots", "oxygen produced only during night respiration", "genetic information between cells"],
        "Xylem vessels move water via transpiration pull and cohesion-tension.",
        "Phloem transports sugars; DNA is not transported in xylem sap.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Identifying xylem transport function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Phloem tissue transports",
        "photosynthetic products such as sucrose from sources to sinks",
        ["water driven only by root pressure with no osmosis", "mineral ions exclusively from soil to leaves", "chlorophyll molecules to root hair cells"],
        "Phloem translocation moves organic nutrients through sieve tube elements.",
        "Water and minerals move mainly in xylem; chlorophyll stays in chloroplasts.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Identifying phloem transport function",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Cohesion of water molecules helps xylem transport because it",
        "allows a continuous water column to be pulled upward during transpiration",
        ["prevents water from evaporating at stomata", "converts glucose into starch in roots", "blocks all osmosis across root membranes"],
        "Hydrogen bonding between water molecules transmits pulling force from leaves to roots.",
        "Cohesion aids column continuity; evaporation still occurs; osmosis continues in roots.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Explaining cohesion in xylem water transport",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Adhesion of water to xylem walls assists transport because it",
        "helps maintain the water column against gravity in narrow vessels",
        ["repels water from the cell wall entirely", "eliminates the need for transpiration", "prevents minerals from dissolving in sap"],
        "Water adheres to hydrophilic xylem surfaces, reducing column breakage during pull.",
        "Adhesion attracts water; transpiration drives flow; minerals remain dissolved.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Explaining adhesion in xylem water transport",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Transpiration refers to",
        "loss of water vapour from plant surfaces, mainly through stomata",
        ["active uptake of CO₂ by root hairs only", "movement of sucrose in phloem at night exclusively", "production of lignin in secondary xylem"],
        "Evaporation from leaf surfaces creates tension that pulls xylem sap upward.",
        "CO₂ enters leaves; phloem operates various times; lignin formation is separate.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Defining transpiration",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Root hair cells absorb minerals from soil often by",
        "active transport against concentration gradients using carrier proteins",
        ["simple diffusion when soil minerals are always lower inside the cell", "osmosis moving minerals as if they were water molecules", "gravitropism bending roots toward light"],
        "Mineral ions may be more concentrated inside root cells, requiring energy-driven uptake.",
        "Minerals are not water; diffusion alone is insufficient when gradients oppose; gravitropism is growth response.",
        topic=TOPIC, outcome_code="C3.3k",
        skill_tested="Explaining mineral uptake in root hairs",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Lenticels in woody stems allow",
        "gas exchange between internal tissues and the atmosphere",
        ["photosynthesis using chlorophyll in bark", "transport of sucrose from leaves to roots only at night", "active replication of xylem vessel elements"],
        "Lenticels are porous regions in bark permitting O₂ and CO₂ diffusion to living cells.",
        "Bark lacks chloroplasts for photosynthesis; phloem not limited to night; replication differs.",
        topic=TOPIC, outcome_code="C3.4k",
        skill_tested="Identifying lenticel function in gas exchange",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "The upper epidermis of a leaf often has a waxy cuticle that",
        "reduces water loss while allowing light to reach mesophyll cells",
        ["blocks all gas exchange through stomata permanently", "stores DNA for the entire plant", "pumps water into xylem by active transport"],
        "Cuticle waterproofs the surface; gas exchange occurs through stomata, not the cuticle.",
        "Stomata remain functional; DNA is in nuclei; cuticle does not pump water.",
        topic=TOPIC, outcome_code="C3.2k",
        skill_tested="Describing epidermis and cuticle function",
        difficulty="Easy", estimated_time_seconds=60,
    ))

    # --- Tropisms (C3) ---
    q.append(mc(
        "Phototropism is defined as",
        "growth of a plant toward or away from a light source",
        ["movement of water through xylem due to cohesion", "digestion of starch in chloroplasts at night", "division of guard cells during mitosis only"],
        "Phototropism is a directional growth response to light, such as shoots bending toward light.",
        "Xylem flow and starch use are not tropisms; guard cell division is not phototropism.",
        topic=TOPIC, outcome_code="C3.5k",
        skill_tested="Defining phototropism",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Gravitropism causes plant roots to grow",
        "downward in response to gravity",
        ["toward the brightest light source only", "in random directions with no stimulus response", "upward exclusively in all conditions"],
        "Root positive gravitropism directs growth into soil for anchorage and water access.",
        "Roots show positive gravitropism; shoots often show negative gravitropism.",
        topic=TOPIC, outcome_code="C3.5k",
        skill_tested="Describing gravitropism in roots",
        difficulty="Easy", estimated_time_seconds=55,
    ))
    q.append(mc(
        "Darwin's experiments on coleoptiles suggested that",
        "a signal produced at the tip causes bending toward light",
        ["light destroys auxin at the base of the stem", "roots synthesize chlorophyll in response to gravity", "stomata close permanently when plants are tipped horizontally"],
        "Covering the tip prevented phototropic bending, indicating a mobile growth signal.",
        "Darwin studied shoot tips, not root chlorophyll or permanent stomatal closure.",
        topic=TOPIC, outcome_code="C3.6k",
        skill_tested="Tracing Darwin's contribution to phototropism research",
        difficulty="Medium", estimated_time_seconds=85,
    ))
    q.append(mc(
        "Boysen-Jensen demonstrated that phototropic signals",
        "could pass through agar but not through mica barriers",
        ["travel only as light waves through the stem", "require stomata to open before bending occurs", "are identical to xylem sap under all conditions"],
        "Permeable agar allowed signal diffusion; impermeable mica blocked it, supporting chemical messenger.",
        "The signal is chemical (later identified as auxin), not light through stem or xylem sap.",
        topic=TOPIC, outcome_code="C3.6k",
        skill_tested="Tracing Boysen-Jensen phototropism experiments",
        difficulty="Hard", estimated_time_seconds=95,
    ))
    q.append(mc(
        "Went's work with agar blocks containing growth substances showed that",
        "a chemical auxin from the tip causes uneven growth and bending",
        ["gravity has no effect on root orientation", "phloem transports auxin exclusively as starch granules", "phototropism requires photosynthesis in roots"],
        "Went collected auxin that promoted growth, explaining phototropic curvature.",
        "Gravity affects roots; auxin is a hormone, not starch; shoots respond to light.",
        topic=TOPIC, outcome_code="C3.6k",
        skill_tested="Tracing Went's auxin experiments on phototropism",
        difficulty="Hard", estimated_time_seconds=95,
    ))
    q.append(mc(
        "Uneven distribution of auxin on the shaded side of a shoot causes",
        "greater cell elongation on the shaded side, bending the shoot toward light",
        ["immediate closure of all stomata on the illuminated side", "conversion of xylem into phloem tissue", "plasmolysis of all palisade cells"],
        "Auxin promotes elongation; higher concentration on shaded side creates asymmetric growth.",
        "Stomatal closure and tissue conversion are unrelated to phototropic bending mechanism.",
        topic=TOPIC, outcome_code="C3.5k",
        skill_tested="Explaining auxin role in phototropic bending",
        difficulty="Medium", estimated_time_seconds=85,
    ))
    q.append(mc(
        "A plant growing on a horizontal surface shows differential auxin distribution in roots such that",
        "auxin accumulates on the lower side, inhibiting elongation and directing root growth downward",
        ["auxin is destroyed by gravity in all root cells equally", "roots bend upward because lower side elongates faster", "stomata on roots regulate gravitropism directly"],
        "In roots, higher auxin on the lower side suppresses growth, curving root down.",
        "Root gravitropism involves auxin inhibition on lower side, not upward bending or root stomata.",
        topic=TOPIC, outcome_code="C3.5k",
        skill_tested="Explaining gravitropism mechanism in roots",
        difficulty="Hard", estimated_time_seconds=95,
    ))
    q.append(mc(
        "Selective breeding of crop plants often relies on understanding plant cell specialization because",
        "desired traits such as drought tolerance involve specialized root and leaf tissues",
        ["all plant cells perform identical roles in every tissue", "tropisms prevent any human modification of plants", "microscopy cannot observe plant cells"],
        "Breeding targets tissue-level traits like stomatal density, root hairs, and vascular efficiency.",
        "Specialization enables trait selection; tropisms and microscopy support plant science.",
        topic=TOPIC, outcome_code="C3.1sts",
        skill_tested="Relating plant specialization to agricultural applications",
        difficulty="Medium", estimated_time_seconds=80,
    ))

    # --- Additional organelle and transport questions ---
    q.append(mc(
        "Which organelle would be most abundant in a muscle cell that requires large amounts of ATP?",
        "mitochondria",
        ["chloroplasts", "large central vacuoles with cell sap", "thick cellulose cell walls"],
        "Muscle cells have high metabolic demand and contain many mitochondria for respiration.",
        "Muscle cells are animal cells lacking chloroplasts, large vacuoles, and cellulose walls.",
        topic=TOPIC, outcome_code="C2.4k",
        skill_tested="Relating organelle abundance to cell function",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "A selectively permeable membrane allows",
        "some substances to pass while restricting others based on size and polarity",
        ["all particles to cross at identical rates without restriction", "only water to move under any condition", "transport exclusively by active means"],
        "Selective permeability enables controlled exchange through lipid bilayer and proteins.",
        "Membranes are selective; ions and other molecules also cross; passive transport occurs.",
        topic=TOPIC, outcome_code="C2.6k",
        skill_tested="Describing selective permeability of membranes",
        difficulty="Easy", estimated_time_seconds=60,
    ))
    q.append(mc(
        "Isotonic saline solution is used medically to replace body fluids because it",
        "has the same solute concentration as body cells, preventing osmotic water shifts",
        ["causes rapid plasmolysis in all blood cells", "is hypertonic and draws water out of tissues", "contains no water and therefore cannot enter cells"],
        "Isotonic fluids maintain cell volume by matching extracellular osmolarity.",
        "Isotonic does not cause plasmolysis or water loss; saline is aqueous.",
        topic=TOPIC, outcome_code="C2.7k",
        skill_tested="Applying isotonic solutions in medicine",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "Cheese making uses osmosis when",
        "salt draws moisture out of curds, inhibiting bacterial spoilage",
        ["lactose spontaneously converts into cellulose cell walls", "mitochondria in milk perform photosynthesis", "active transport pumps air into solid cheese"],
        "Salting creates hypertonic conditions that remove water from curds and microbes.",
        "Cheese making does not involve cellulose formation or photosynthesis in milk.",
        topic=TOPIC, outcome_code="C2.7k",
        skill_tested="Applying osmosis in cheese production",
        difficulty="Medium", estimated_time_seconds=75,
    ))
    q.append(mc(
        "A single-celled organism that grows too large will struggle to survive primarily because",
        "its volume increases faster than its surface area available for nutrient exchange",
        ["its nucleus divides into multiple nuclei automatically", "diffusion becomes faster as cell diameter increases", "active transport no longer requires membrane proteins"],
        "Limited SA:V reduces efficiency of intake and waste removal in oversized cells.",
        "Extra nuclei do not solve exchange limits; diffusion slows relative to needs at large size.",
        topic=TOPIC, outcome_code="C3.1k",
        skill_tested="Explaining size limits in single-celled organisms",
        difficulty="Medium", estimated_time_seconds=80,
    ))
    q.append(mc(
        "Liposomes used to deliver HIV drugs to cells rely on membrane principles because they",
        "fuse with or merge into cell membranes to release medication inside target cells",
        ["convert all cell walls into chloroplasts on contact", "prevent any diffusion across membranes permanently", "require spontaneous generation of new cells"],
        "Liposome bilayers mimic cell membranes, enabling targeted drug delivery via fusion or endocytosis.",
        "Liposomes do not create chloroplasts or block all transport; they exploit membrane compatibility.",
        topic=TOPIC, outcome_code="C2.9k",
        skill_tested="Applying liposome drug delivery to membrane models",
        difficulty="Hard", estimated_time_seconds=90,
    ))
    q.append(mc(
        "Some protein hormones enter target cells primarily by",
        "diffusion through the membrane or receptor-mediated uptake when small enough or bound to carriers",
        ["active photosynthesis in the hormone molecule itself", "replacing the nucleus with a cell wall", "osmosis moving hormones as water molecules only"],
        "Small, lipid-soluble hormones can diffuse across membranes; others bind surface receptors triggering internal signals.",
        "Hormones are not water; they do not photosynthesize or replace nuclei.",
        topic=TOPIC, outcome_code="C2.9k",
        skill_tested="Explaining hormone entry as a membrane transport application",
        difficulty="Hard", estimated_time_seconds=90,
    ))

    # --- Numerical response: magnification (C1.1s) ---
    for eyepiece, objective in [(10, 4), (10, 10), (15, 40)]:
        total_mag = eyepiece * objective
        q.append(nr(
            f"A compound light microscope has an eyepiece lens of {eyepiece}× and an objective lens of {objective}×. "
            f"What is the total magnification? Record a whole number.",
            str(total_mag),
            f"Total magnification = eyepiece × objective = {eyepiece} × {objective} = {total_mag}.",
            "Students add lens powers instead of multiplying them.",
            topic=TOPIC, outcome_code="C1.1s",
            skill_tested="Calculating total microscope magnification",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for image_um, actual_um in [(120, 30), (200, 40), (90, 15)]:
        mag = image_um // actual_um
        q.append(nr(
            f"A specimen measures {actual_um} μm across. Under the microscope the image appears "
            f"{image_um} μm wide. What is the magnification? Record a whole number.",
            str(mag),
            f"Magnification = image size ÷ actual size = {image_um}/{actual_um} = {mag}.",
            "Students divide actual by image size, inverting the ratio.",
            topic=TOPIC, outcome_code="C1.1s",
            skill_tested="Calculating magnification from image and actual size",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    # --- Numerical response: surface area to volume ratio (C1.3s) ---
    for length in [2, 3, 4, 5]:
        sa = 6 * length * length
        vol = length * length * length
        ratio = round(sa / vol, 2)
        q.append(nr(
            f"A cube-shaped cell has edges of {length} μm. Surface area = 6 × edge² and volume = edge³. "
            f"What is the surface-area-to-volume ratio? Express as a decimal rounded to two decimal places.",
            f"{ratio:.2f}",
            f"SA = 6 × {length}² = {sa} μm²; V = {length}³ = {vol} μm³; SA:V = {sa}/{vol} = {ratio:.2f}.",
            "Students invert the ratio (volume ÷ surface area) or forget to square/cube the edge.",
            topic=TOPIC, outcome_code="C1.3s",
            skill_tested="Calculating surface-area-to-volume ratio for a cubic cell",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # --- Numerical response: percent (C1.4s) ---
    for plasmolyzed, total in [(12, 50), (8, 40), (15, 60)]:
        pct = round(100 * plasmolyzed / total, 1)
        q.append(nr(
            f"In a microscope field of view, {plasmolyzed} of {total} plant cells show plasmolysis after "
            f"placing the tissue in a hypertonic salt solution. What percent of cells are plasmolyzed? "
            f"Express as a decimal rounded to one decimal place.",
            f"{pct:.1f}",
            f"Percent = ({plasmolyzed}/{total}) × 100 = {pct:.1f}%.",
            "Students divide total by plasmolyzed or forget to multiply by 100.",
            topic=TOPIC, outcome_code="C1.4s",
            skill_tested="Calculating percent of plasmolyzed cells",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for stomata, area in [(180, 1), (240, 2), (150, 1)]:
        density = stomata / area if area else stomata
        q.append(nr(
            f"A leaf sample of {area} mm² contains {stomata} open stomata visible under the microscope. "
            f"What is the stomatal density in stomata per mm²? Record a whole number.",
            str(int(density)),
            f"Density = {stomata} stomata ÷ {area} mm² = {int(density)} per mm².",
            "Students multiply area by stomata count instead of dividing.",
            topic=TOPIC, outcome_code="C1.2s",
            skill_tested="Calculating stomatal density from count and area",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    return q
