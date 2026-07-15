"""Unit C: Chemical Changes of Organic Compounds — original Chemistry 30 questions."""

from .helpers import mc, nr

TOPIC = "Chemical Changes of Organic Compounds"


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
            "An organic compound is defined as one that contains carbon, with exceptions including",
            "carbonates, cyanides, carbides, and oxides of carbon",
            ["all compounds containing any element bonded to carbon", "only hydrocarbons with no other elements ever", "sodium chloride and water"],
            "Organic chemistry focuses on carbon compounds; carbonates and CO$_2$ are inorganic exceptions.",
            "Students think every carbon-containing compound is organic.",
            "C1.1k", "Defining organic compounds with inorganic exceptions", "Easy", 65,
        ),
        (
            "Methane (CH$_4$) is used primarily as",
            "a natural gas fuel for heating and electricity generation",
            ["an acid in acid-base titrations", "a polymer building block for nylon only", "an electrolyte in voltaic cells"],
            "Methane is the main component of natural gas, burned for energy.",
            "Students confuse methane with methanol or other derivatives.",
            "C1.2k", "Identifying methane application in daily life", "Easy", 60,
        ),
        (
            "The IUPAC name for $\\text{CH}_3\\text{CH}_2\\text{CH}_2\\text{OH}$ is",
            "propan-1-ol",
            ["propane", "methoxyethane", "propanal"],
            "Three-carbon chain with OH on carbon 1: propan-1-ol.",
            "Students name it propane (alkane) or misplace the hydroxyl position.",
            "C1.3k", "Applying IUPAC naming to primary alcohol", "Medium", 90,
        ),
        (
            "The IUPAC name for $\\text{CH}_3\\text{CH}_2\\text{COOH}$ is",
            "propanoic acid",
            ["ethyl methanoate", "propanal", "propan-1-ol"],
            "Three-carbon carboxylic acid: propanoic acid.",
            "Students confuse carboxylic acids with esters or aldehydes.",
            "C1.3k", "Applying IUPAC naming to carboxylic acid", "Medium", 90,
        ),
        (
            "A compound with the hydroxyl (-OH) functional group attached to a saturated aliphatic carbon chain is classified as",
            "an alcohol",
            ["an ester", "a carboxylic acid", "an alkene"],
            "Hydroxyl on aliphatic carbon defines alcohol (not phenol unless on benzene ring).",
            "Students confuse alcohols with carboxylic acids (which have -COOH).",
            "C1.4k", "Identifying alcohol functional group", "Easy", 65,
        ),
        (
            "Propanoic acid and methyl ethanoate both have molecular formula C$_3$H$_6$O$_2$. They are best described as",
            "structural isomers with different functional groups",
            ["identical compounds with the same name", "ionization isomers of sodium chloride", "allotropes of carbon only"],
            "Both C$_3$H$_6$O$_2$ with different connectivity — classic structural isomerism.",
            "Students think isomers must have different molecular formulas.",
            "C1.5k", "Identifying structural isomer pair", "Hard", 110,
        ),
        (
            "Within a homologous series of straight-chain alkanes, boiling point generally",
            "increases as molar mass increases due to stronger London dispersion forces",
            ["decreases as molar mass increases", "is identical for all chain lengths", "depends only on hydrogen bonding"],
            "Larger molecules have stronger temporary dipole interactions, raising boiling point.",
            "Students think all alkanes have the same boiling point.",
            "C1.6k", "Relating alkane boiling point to molar mass", "Medium", 85,
        ),
        (
            "1-propanol is more soluble in water than 1-chloropropane because",
            "propanol can form hydrogen bonds with water molecules",
            ["chloropropane is non-polar with no dipole", "propanol has a larger molar mass only", "chlorine always makes compounds water-soluble"],
            "Alcohols hydrogen-bond with water; halogenated alkanes cannot form strong H-bonds with water.",
            "Students cite polarity alone without considering hydrogen bonding requirement.",
            "C1.6k", "Explaining alcohol vs halogenated hydrocarbon solubility", "Medium", 90,
        ),
        (
            "Fractional distillation separates crude oil components primarily by differences in",
            "boiling point",
            ["molecular polarity only", "oxidation number of carbon", "electrical conductivity"],
            "Tower fractions collect hydrocarbons with different boiling ranges.",
            "Students confuse fractional distillation with solvent extraction.",
            "C1.7k", "Explaining fractional distillation separation principle", "Easy", 70,
        ),
        (
            "Solvent extraction separates organic compounds based on",
            "differential solubility between two immiscible solvents",
            ["differences in oxidation potential only", "catalytic cracking of long chains", "electrolysis at the anode"],
            "Compounds partition between solvents according to relative solubility.",
            "Students think extraction uses boiling point differences like distillation.",
            "C1.7k", "Explaining solvent extraction separation principle", "Medium", 80,
        ),
        (
            "Propane is classified as a saturated hydrocarbon because",
            "all carbon-carbon bonds are single bonds",
            ["it contains a carbon-oxygen double bond", "it has a benzene ring", "it dissolves in water readily"],
            "Saturated = only C-C single bonds; C=O in acids does not make them unsaturated.",
            "Students count C=O double bonds as unsaturation.",
            "C1.3k", "Classifying propane as saturated hydrocarbon", "Easy", 65,
        ),
        (
            "Cyclohexene reacts with aqueous bromine rapidly because",
            "the carbon-carbon double bond undergoes addition, decolourizing bromine",
            ["cyclohexene is aromatic and stable", "bromine substitutes all hydrogens instantly without a double bond", "cyclohexene has no reaction with halogens ever"],
            "Alkene + Br$_2$ addition reaction is fast and visible (colour loss).",
            "Students expect saturated compounds to decolourize bromine instantly.",
            "C1.3s", "Interpreting bromine test for unsaturated aliphatics", "Medium", 85,
        ),
        (
            "Ethanoic acid gives a negative bromine test (no rapid decolourization) because",
            "its unsaturation is C=O, not C=C; it is classified as saturated",
            ["it has no oxygen atoms", "it is an aromatic compound", "bromine only reacts with metals"],
            "Alberta POS: only C=C or C≡C makes aliphatic compounds unsaturated.",
            "Students think any double bond means positive bromine test.",
            "C1.3k", "Explaining negative bromine test for carboxylic acid", "Medium", 90,
        ),
        (
            "An addition reaction in organic chemistry is characterized by",
            "atoms adding across a multiple bond without losing other atoms from the original molecule",
            ["two molecules joining with loss of water", "removal of adjacent atoms to form a double bond", "complete combustion to CO$_2$ and H$_2$O"],
            "Addition: atoms add across C=C (e.g., H$_2$ + alkene → alkane).",
            "Students confuse addition with elimination or condensation.",
            "C2.1k", "Defining addition reaction in organic chemistry", "Easy", 70,
        ),
        (
            "An elimination reaction produces",
            "a product with a carbon-carbon double bond by removing atoms from adjacent carbons",
            ["a salt and water from acid-base reaction", "only CO$_2$ and H$_2$O", "a polymer chain from monomers"],
            "Elimination removes H and X (or similar) from adjacent carbons, forming C=C.",
            "Students confuse elimination with substitution.",
            "C2.1k", "Defining elimination reaction in organic chemistry", "Medium", 80,
        ),
        (
            "Cracking a long-chain alkane to produce shorter alkanes and alkenes is classified as",
            "elimination",
            ["addition only", "esterification", "neutralization"],
            "Cracking produces alkenes with C=C bonds — elimination-type process.",
            "Students classify cracking as combustion.",
            "C2.1k", "Classifying cracking as elimination reaction", "Medium", 85,
        ),
        (
            "The reaction $\\text{CH}_4 + \\text{Cl}_2 \\rightarrow \\text{CH}_3\\text{Cl} + \\text{HCl}$ (with UV light) is",
            "substitution",
            ["addition", "elimination", "esterification"],
            "H on methane replaced by Cl — free radical substitution.",
            "Students label all halogen reactions as addition.",
            "C2.2k", "Identifying halogenation as substitution", "Medium", 85,
        ),
        (
            "Esterification between ethanol and ethanoic acid produces",
            "ethyl ethanoate and water",
            ["ethene and hydrogen gas", "sodium ethanoate and HCl", "polyethylene and CO$_2$"],
            "Acid + alcohol → ester + water (condensation/esterification).",
            "Students predict wrong products or confuse with combustion.",
            "C2.2k", "Predicting esterification products", "Medium", 90,
        ),
        (
            "Polyethylene is formed from ethylene monomers by",
            "addition polymerization",
            ["condensation polymerization with loss of HCl each step", "complete combustion", "fractional distillation only"],
            "Ethylene (C=C) opens to form long -CH$_2$-CH$_2$- chains — addition polymer.",
            "Students confuse addition and condensation polymerization.",
            "C2.3k", "Identifying polyethylene as addition polymer", "Medium", 85,
        ),
        (
            "Nylon is an example of",
            "condensation polymerization",
            ["addition polymerization of ethylene only", "a monatomic noble gas", "an inorganic carbonate"],
            "Nylon forms by condensation with elimination of small molecules (e.g., H$_2$O).",
            "Students classify all polymers as addition polymers.",
            "C2.3k", "Identifying nylon as condensation polymer", "Medium", 85,
        ),
        (
            "Complete combustion of an organic compound in excess oxygen produces",
            "CO$_2$ and H$_2$O (and possibly other products if halogens present)",
            ["only carbon (soot) with no oxygen-containing products", "NH$_3$ and N$_2$ always", "pure ethanol"],
            "Complete combustion oxidizes C to CO$_2$ and H to H$_2$O.",
            "Students think incomplete combustion products apply to complete combustion.",
            "C2.1k", "Describing complete combustion products", "Easy", 65,
        ),
        (
            "Bitumen upgrading in Alberta involves",
            "converting heavy bitumen into lighter synthetic crude oil fractions",
            ["removing all carbon to produce hydrogen gas only", "electrolysis of bitumen in water", "fermentation to ethanol"],
            "Upgrading breaks heavy hydrocarbons into more valuable lighter products.",
            "Students confuse bitumen upgrading with simple mining without chemical change.",
            "C2.1sts", "Describing bitumen upgrading process", "Medium", 85,
        ),
        (
            "Blending ethanol into gasoline can",
            "increase octane rating and provide a renewable oxygenate component",
            ["eliminate all carbon emissions from vehicles", "convert gasoline into a strong acid", "prevent all combustion reactions"],
            "Ethanol blending improves fuel properties; it does not eliminate CO$_2$ emissions.",
            "Students think ethanol-blended fuels are emission-free.",
            "C2.2sts", "Explaining ethanol fuel blending benefits", "Medium", 80,
        ),
        (
            "Chlorofluorocarbons (CFCs) contributed to ozone depletion because",
            "UV radiation breaks C-Cl bonds releasing chlorine radicals that catalyze ozone destruction",
            ["CFCs absorb all UV light harmlessly", "CFCs increase stratospheric oxygen concentration only", "CFCs are too heavy to reach the stratosphere"],
            "Cl radicals from CFC photolysis catalytically destroy O$_3$ in the stratosphere.",
            "Students confuse greenhouse effect with ozone depletion mechanism.",
            "C2.3sts", "Explaining CFC impact on ozone layer", "Medium", 90,
        ),
        (
            "The term hydrocarbon should be used only for compounds containing",
            "carbon and hydrogen atoms only",
            ["carbon, hydrogen, and oxygen", "carbon and any halogen", "any organic compound with a functional group"],
            "Hydrocarbon = C and H only; chloromethane is a hydrocarbon derivative.",
            "Students call chlorinated organics hydrocarbons.",
            "C1.3k", "Applying strict hydrocarbon definition", "Easy", 65,
        ),
        (
            "Benzene is classified as",
            "aromatic",
            ["a saturated aliphatic hydrocarbon", "an inorganic carbonate", "a strong Brønsted-Lowry acid"],
            "Benzene has a stable aromatic ring — neither saturated nor unsaturated aliphatic.",
            "Students try to classify benzene as saturated or unsaturated aliphatic.",
            "C1.3k", "Classifying benzene as aromatic compound", "Easy", 70,
        ),
        (
            "A primary alcohol has the hydroxyl group attached to a carbon that is bonded to",
            "only one other carbon atom (or none for methanol)",
            ["three other carbon atoms", "a benzene ring directly", "an oxygen of a carboxyl group"],
            "Primary: -OH on C with 0-1 other carbons; secondary = 2; tertiary = 3.",
            "Students confuse primary alcohols with phenols or carboxylic acids.",
            "C1.4k", "Defining primary alcohol structure", "Medium", 80,
        ),
        (
            "Margarine production from vegetable oils may involve",
            "hydrogenation of unsaturated fats using a nickel catalyst",
            ["complete combustion of oils to CO$_2$", "electrolysis of fatty acids", "distillation of proteins"],
            "Hydrogenation adds H across C=C bonds, solidifying liquid oils.",
            "Students confuse hydrogenation with hydrolysis or combustion.",
            "C1.1sts", "Describing hydrogenation in food processing", "Medium", 85,
        ),
    ])

    q += [
        nr(
            "How many carbon atoms are in the parent chain of 2-methylbutane? Record as a single digit.",
            "4",
            "Longest continuous chain has 4 carbons (butane); methyl branch on carbon 2.",
            "Students count the methyl branch carbon as part of the parent chain (5).",
            topic=TOPIC, outcome_code="C1.3k",
            skill_tested="Determining parent chain length in IUPAC name",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        nr(
            "A hydrocarbon has molecular formula C$_5$H$_{12}$. How many hydrogen atoms does it contain? Record as a two-digit integer.",
            "12",
            "The formula explicitly states 12 hydrogen atoms.",
            "Students confuse molecular formula subscripts with parent chain length.",
            topic=TOPIC, outcome_code="C1.5k",
            skill_tested="Reading molecular formula hydrogen count",
            difficulty="Easy", estimated_time_seconds=45,
        ),
        nr(
            "How many carbon atoms are in one molecule of glucose (C$_6$H$_{12}$O$_6$)? Record as a single digit.",
            "6",
            "Glucose molecular formula contains 6 carbon atoms.",
            "Students add all atoms (6+12+6=24) instead of counting carbons only.",
            topic=TOPIC, outcome_code="C1.2k",
            skill_tested="Identifying carbon count in biologically significant organic compound",
            difficulty="Easy", estimated_time_seconds=50,
        ),
    ]

    return q
