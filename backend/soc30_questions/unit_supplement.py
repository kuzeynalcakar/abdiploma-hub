"""Additional original SOC30-1 items to deepen the unbalanced pool toward ~450."""

from __future__ import annotations

from .helpers import mc, nr

T_ID = "Ideology and Identity"
T_ORIG = "Origins of Liberalism"
T_RES = "Resistance to Liberalism"
T_VIA = "The Viability of Contemporary Liberalism"
T_CIT = "Citizenship and Ideology"
DIFFS = ("Easy", "Medium", "Hard")


def _d(i: int) -> str:
    return DIFFS[i % 3]


def build_questions() -> list:
    q: list = []

    # --- RI1 supplements ---
    for i, (stem, ans, d1, d2, d3, oc, skill, expl, mist) in enumerate([
        ("A city celebrates multiple newcomer languages at a civic ceremony while still enforcing equal legal rights. The identity analysis should emphasize",
         "cultural pluralism interacting with liberal civic equality",
         "that language festivals abolish rule of law",
         "that only fascism holds festivals",
         "that ideology forbids celebrations",
         "1.3k", "Linking cultural language factors to civic identity",
         "Culture and language shape identity (1.3k) without automatically cancelling liberal legal equality.",
         "Students treat multicultural celebration as anti-liberal by definition."),
        ("Someone argues ‘humans are selfish, so markets alone should allocate everything.’ Which ideology characteristic is foremost?",
         "a belief about human nature used to justify a preferred social order",
         "a GIS skill",
         "a nuclear yield calculation",
         "a transit fare schedule",
         "1.5k", "Identifying human-nature claims in ideology",
         "Beliefs about human nature are a named ideology characteristic in 1.5k.",
         "Students debate the policy without naming the characteristic."),
        ("Comparing a private art collection with a municipally owned gallery highlights tension between",
         "private property and public property principles",
         "détente and brinkmanship",
         "nonalignment and suffrage alone",
         "pin factories and charcoal sketches only",
         "1.7k", "Contrasting private and public property principles",
         "Private property is liberal-individualist; public property is collectivist (1.7k/1.8k).",
         "Students ignore property-type contrast."),
        ("A influencer claims ‘your shopping cart is your real political identity.’ A critical 30-1 response is that",
         "consumption may express values but ideology and identity are broader than market choice alone",
         "shopping carts are illegal under liberalism",
         "only monarchs may shop",
         "GDP outlaws identity",
         "1.10k", "Evaluating reductive identity claims",
         "1.10k evaluates how far ideology should shape identity—not slogans reducing identity to purchases.",
         "Students accept marketing slogans as analysis."),
        ("Collective interest differs most clearly from economic equality when a policy",
         "protects a shared fishery stock without necessarily equalizing household incomes",
         "sets identical after-tax income for every person by force",
         "abolishes all shared resources",
         "bans fishing metaphors in exams",
         "1.8k", "Distinguishing collective interest from economic equality",
         "Collective interest concerns shared benefit; economic equality concerns material gap narrowing.",
         "Students treat every collectivist principle as interchangeable."),
        ("Self-interest as a liberal principle is illustrated when",
         "a freelancer prices services to raise personal income within legal rules",
         "a politburo sets shoe quotas",
         "a dictator bans all markets as racial policy",
         "elders allocate harvest solely by sacred custom with no choice",
         "1.7k", "Recognizing self-interest in liberal individualism",
         "Self-interest is a listed liberal principle tied to individualism.",
         "Students moralize self-interest as greed outside any principle list."),
        ("Common good arguments are strongest in 30-1 when they",
         "show how collective aims interact with—not automatically erase—individual rights",
         "deny that individuals exist",
         "require fascism",
         "ban all taxation discussion",
         "1.9k", "Framing common-good arguments with rights",
         "1.9k analyzes the dynamic between individualism and common good.",
         "Students treat common good as automatically illiberal."),
        ("Themes of nation and class collide when a party says",
         "workers of one ethnicity deserve the state while others do not",
         "airline points determine ideology",
         "map scale bars outlaw politics",
         "pin length equals justice",
         "1.6k", "Recognizing intersecting ideology themes",
         "Nation and class can intertwine in exclusionary ideologies.",
         "Students examine only one theme."),
    ]):
        q.append(mc(stem, ans, [d1, d2, d3], expl, mist,
                     topic=T_ID, outcome_code=oc, skill_tested=skill,
                     difficulty=_d(i), estimated_time_seconds=90 + 10 * (i % 3)))

    # Principle application grid
    for i, (principle, eg) in enumerate([
        ("competition", "two streaming services undercut each other’s subscription prices"),
        ("rule of law", "a wealthy donor receives the same ticket for illegal parking as a student"),
        ("economic freedom", "artisans may sell crafts online without a state product list"),
        ("individual rights and freedoms", "a blogger criticizes city hall without being jailed for the criticism alone"),
        ("cooperation", "rival towns co-fund a shared water treatment plant"),
        ("adherence to collective norms", "a communal farm fines members who skip assigned harvest days"),
        ("collective responsibility", "union members accept dues that fund strike pay for others"),
        ("economic equality", "a basic income floor narrows post-transfer poverty gaps"),
    ]):
        topic = T_ID
        oc = "1.7k" if principle in {
            "competition", "rule of law", "economic freedom", "individual rights and freedoms"
        } else "1.8k"
        q.append(mc(
            f"Classroom example: {eg}. The principle best matched is",
            principle,
            [
                "brinkmanship",
                "nonalignment",
                "Führerprinzip",
            ],
            f"{principle} is enumerated under individualism or collectivism outcomes.",
            "Students pick a Cold War label for a domestic principle example.",
            topic=topic, outcome_code=oc,
            skill_tested=f"Matching examples to {principle}",
            difficulty=_d(i + 1), estimated_time_seconds=80,
        ))

    # --- Origins supplements ---
    for i, (stem, ans, dists, oc, expl, mist) in enumerate([
        ("Classical liberal suspicion of absolute monarchy most directly feeds into later expectations of",
         "constitutional limits on executive power",
         ["racial hierarchy as justice", "one-party show trials", "collective farms abolishing ballots"],
         "2.5k",
         "Locke/Montesquieu traditions distrust unchecked sovereign power.",
         "Students leap to twentieth-century totalitarian models as if they were classical liberalism."),
        ("Mill’s harm principle is least compatible with",
         "punishing peaceful dissenting speech that harms no third party",
         ["limiting assault", "regulating fraud", "stopping direct threats"],
         "2.5k",
         "Mill prioritizes liberty unless harm to others is shown.",
         "Students think Mill banned all regulation."),
        ("Industrial class stratification under classical liberal economies helps explain why",
         "socialism and Marxism developed as critical responses",
         ["Adam Smith became a fascist", "nonalignment began in 1815", "Charter section 33 created mills"],
         "2.7k",
         "Class tensions under industrial liberalism spurred response ideologies.",
         "Students invent anachronistic causes."),
        ("Welfare capitalism differs from revolutionary Marxism primarily because it",
         "retains capitalist ownership while adding stabilizing supports",
         ["abolishes firms overnight", "installs a racial state", "bans wages as such"],
         "2.7k",
         "Welfare capitalism reforms capitalism; Marxism seeks transformative rupture.",
         "Students collapse all ‘welfare’ talk into communism."),
        ("Universal suffrage expands modern liberalism by",
         "widening who counts as a full political citizen",
         ["ending elections", "creating command shoe quotas", "requiring Führer oaths"],
         "2.8k",
         "Suffrage expansion is a listed modern liberal development.",
         "Students see suffrage as anti-liberal."),
        ("Labour standards respond to classical liberal industrialization by",
         "curbing some economic freedom to protect workers’ health and bargaining power",
         ["celebrating unlimited child labour as natural right", "abolishing factories via fascism", "banning unions forever"],
         "2.8k",
         "Modern liberalism reforms classical laissez-faire extremes.",
         "Students treat any labour law as fascism or as classical purity."),
        ("Aboriginal contributions to liberalism discussions matter in 30-1 because they",
         "complicate narratives that liberalism has only European origins",
         ["prove liberalism never harmed Indigenous peoples", "erase colonial imposition", "equate Indigenous law with Nazism"],
         "2.4k",
         "2.4k explores Aboriginal contributions without denying later imposition themes (2.11k).",
         "Students assume recognition cancels critique of imposition."),
        ("Laissez-faire as nineteenth-century practice meant, above all,",
         "minimizing government direction of markets and welfare",
         ["maximum one-party censorship", "mandatory collective farms", "racial empire as first principle"],
         "2.6k",
         "Laissez-faire is a classical liberal economic impact area.",
         "Students confuse laissez-faire with totalitarian control."),
    ]):
        q.append(mc(stem, ans, dists, expl, mist,
                     topic=T_ORIG, outcome_code=oc,
                     skill_tested="Deepening classical/modern liberalism analysis",
                     difficulty=_d(i), estimated_time_seconds=100))

    for i, thinker in enumerate(["John Locke", "Montesquieu", "Adam Smith", "John Stuart Mill"]):
        focus = {
            "John Locke": "consent and natural rights against arbitrary rule",
            "Montesquieu": "separating powers to secure political liberty",
            "Adam Smith": "market coordination arising from individual economic pursuits",
            "John Stuart Mill": "maximizing individuality subject to the harm principle",
        }[thinker]
        q.append(mc(
            f"A student summary stating that {thinker} mainly contributed ideas about {focus} is",
            "consistent with classical liberal origins in the program of studies",
            [
                "a description of Nazi racial ideology",
                "a summary of Stalinist show-trial procedure",
                "an account of command economy grain seizures",
            ],
            f"{thinker} is a PoS classical liberal anchor (2.5k).",
            "Students map classical liberals onto twentieth-century dictators.",
            topic=T_ORIG, outcome_code="2.5k",
            skill_tested=f"Confirming classical liberal summary for {thinker}",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # --- Resistance supplements ---
    for i, (stem, ans, dists, oc, expl, mist) in enumerate([
        ("A regime that keeps markets for some consumer goods but jails all opposition parties is still rejecting liberalism because",
         "liberalism requires political rights and pluralism, not markets alone",
         ["markets automatically equal liberalism fully", "jailing parties is Mill’s harm principle", "party jails are Charter section 1"],
         "2.9k",
         "Political pluralism and rights are central liberal principles; partial markets do not redeem their absence.",
         "Students reduce liberalism to ‘has shops’."),
        ("Containment differs from deterrence in that containment emphasizes",
         "stopping ideological expansion geographically/politically, whereas deterrence emphasizes discouraging attack via threatened costs",
         ["identical meanings always", "only cultural festivals", "only linguistic purity"],
         "2.10k",
         "These Cold War concepts are distinct though related.",
         "Students treat them as synonyms."),
        ("Brinkmanship is riskiest when",
         "actors push a crisis near war believing the other side will blink first",
         ["two states ignore each other for decades", "trade expands quietly", "summits lower rhetoric without crises"],
         "2.10k",
         "Brinkmanship uses crisis coercion near the brink of conflict.",
         "Students confuse brinkmanship with détente."),
        ("Nonalignment meant newly independent states often sought to",
         "avoid formal membership in either Cold War military camp",
         ["join both NATO and the Warsaw Pact simultaneously as obligation", "abolish their own sovereignty", "become provinces of a superpower"],
         "2.10k",
         "Nonalignment is a listed postwar concept.",
         "Students invent opposite meanings."),
        ("Imposition critiques are not identical to fascist rejection of liberalism because imposition analysis often focuses on",
         "liberal norms forced onto peoples with different collective traditions, including Aboriginal experiences",
         ["Führer racial empire as Indigenous policy origin", "command grain seizures in Ukraine as Canadian band council law", "détente missile caps"],
         "2.11k",
         "2.11k is about imposition of liberalism; 2.9k is rejection via communism/fascism—related but not the same frame.",
         "Students swap imposition with fascist ideology wholesale."),
        ("Environmentalism challenges modern liberalism when it claims",
         "ecological limits should constrain consumer and investor freedom",
         ["markets never use resources", "ideology disappeared", "only monarchs pollute"],
         "2.12k",
         "Environmentalism is a listed alternative thought challenge.",
         "Students deny any tension with liberalism."),
        ("Neo-conservatism typically challenges modern liberalism by arguing for",
         "stronger markets and traditional social norms against welfare-state expansion",
         ["Soviet collectivization", "Nazi racial law", "abolition of private firms"],
         "2.12k",
         "Neo-conservatism is listed among challenges to modern liberalism.",
         "Students confuse neo-conservatism with communism."),
        ("Evaluating resistance as justified is most defensible when",
         "resistance targets the violent erasure of rights and pluralist citizenship",
         ["any bomb in a market is automatically ethical", "all criticism of markets is fascism", "evaluation is never allowed"],
         "2.13k",
         "2.13k demands criteria-based evaluation, not blank endorsement of violence or blank rejection of dissent.",
         "Students endorse extremes."),
    ]):
        q.append(mc(stem, ans, dists, expl, mist,
                     topic=T_RES, outcome_code=oc,
                     skill_tested="Extending resistance-to-liberalism analysis",
                     difficulty=_d(i + 2), estimated_time_seconds=110))

    for i, movement in enumerate([
        "an Algerian independence struggle amid superpower attention",
        "a Vietnamese conflict with rival patrons",
        "a southern African anti-colonial campaign",
        "a Central American guerrilla war with competing aid streams",
    ]):
        q.append(mc(
            f"Case: {movement}. Within 2.10k this is best linked to",
            "liberation movements interacting with bipolar ideological rivalry",
            [
                "municipal compost programs",
                "Adam Smith’s customs warehouse notes",
                "Québec Charter drafting in 1982 alone",
            ],
            "Liberation movements are explicitly listed in 2.10k.",
            "Students ignore the Cold War ideological patronage frame.",
            topic=T_RES, outcome_code="2.10k",
            skill_tested="Placing liberation movements in Cold War context",
            difficulty=_d(i), estimated_time_seconds=100,
        ))

    # --- Viability supplements ---
    for i, (stem, ans, dists, oc, expl, mist) in enumerate([
        ("Direct democracy can threaten liberal minority rights when",
         "majorities repeatedly outvote protected groups on fundamental entitlements",
         ["citizens never vote", "courts always vanish automatically", "markets set ballots"],
         "3.5k",
         "Popular mechanisms can conflict with liberal rights protections.",
         "Students assume direct democracy is always rights-safe."),
        ("Command economies conflict with liberalism mainly through",
         "central directives replacing private property and economic freedom norms",
         ["excessively competitive multiparty elections", "too much press freedom", "optional church festivals"],
         "3.5k",
         "Command allocation conflicts with core liberal economic principles.",
         "Students cite unrelated political traits."),
        ("Illiberalism in a democracy is best evidenced by",
         "elections continuing while independent courts and media are hollowed out",
         ["any public school existing", "any income tax existing", "any road existing"],
         "3.6k",
         "Illiberal practices can coexist with elections.",
         "Students think elections make illiberalism impossible."),
        ("Emergencies legislation is most consistent with liberalism when",
         "powers are temporary, reviewed, and rights limits are justified and supervised",
         ["powers never sunset", "oversight is abolished permanently", "critics are jailed without process as routine"],
         "3.8k",
         "3.8k pairs emergencies/security legislation with rights evaluation.",
         "Students either ban all emergency tools or accept permanence."),
        ("Language legislation tests liberalism because it may",
         "promote collective linguistic security while limiting some individual language choices",
         ["have no connection to rights", "only affect airline logos", "abolish citizenship"],
         "3.8k",
         "Language legislation is a named 3.8k focus.",
         "Students ignore collective–individual tension."),
        ("Censorship debates during riots require weighing",
         "safety and dignity claims against viewpoint freedom central to liberalism",
         ["only stock prices", "only map projections", "only mill spindle counts"],
         "3.9k",
         "Censorship is a contemporary viability issue in 3.9k.",
         "Students pick a side without principle balancing."),
        ("Debt and poverty challenge viability when citizens ask whether",
         "liberal political economies can still secure basic dignity and opportunity",
         ["maps cause inflation alone", "nonalignment sets interest rates", "pin factories forbid banks"],
         "3.9k",
         "Debt and poverty are listed contemporary issues.",
         "Students treat poverty as outside ideology."),
        ("Authoritarian systems may hold plebiscites yet still fail liberalism because",
         "without rights, competition, and accountability, popular rituals do not equal liberal democracy",
         ["plebiscites automatically fulfill Mill", "authoritarianism is classical liberalism", "Smith required dictators"],
         "3.5k",
         "Liberal democracy needs more than staged voting.",
         "Students equate any ballot box with liberalism."),
    ]):
        q.append(mc(stem, ans, dists, expl, mist,
                     topic=T_VIA, outcome_code=oc,
                     skill_tested="Deepening viability-of-liberalism analysis",
                     difficulty=_d(i), estimated_time_seconds=115))

    for i, doc in enumerate([
        ("Canadian Charter of Rights and Freedoms", "a rights claim pleaded in a Canadian superior court"),
        ("American Bill of Rights", "an early U.S. constitutional amendment dispute over speech"),
        ("Québec Charter of Human Rights and Freedoms", "a rights argument framed inside Québec’s statutory rights regime"),
        ("First Nations, Métis and Inuit rights", "litigation grounded in Aboriginal and treaty rights recognition"),
    ]):
        q.append(mc(
            f"Source context: {doc[1]}. The rights framework most precisely engaged is",
            doc[0],
            [x for x, _ in [
                ("Canadian Charter of Rights and Freedoms", ""),
                ("American Bill of Rights", ""),
                ("Québec Charter of Human Rights and Freedoms", ""),
                ("First Nations, Métis and Inuit rights", ""),
            ] if x != doc[0]][:3],
            "Precise instrument identification supports 3.8k evaluation.",
            "Students use ‘Charter’ generically for every rights document.",
            topic=T_VIA, outcome_code="3.8k",
            skill_tested="Matching cases to rights instruments",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    # Mixed economy / Canada / equality extras
    for i, scene in enumerate([
        "public universities beside private colleges",
        "regulated banks beside entrepreneur startups",
        "public pensions beside private RRSPs",
        "crown corporations beside competitive retailers",
        "environmental assessments beside resource markets",
        "antitrust rules beside private franchises",
    ]):
        q.append(mc(
            f"An economy featuring {scene} is best described as",
            "mixed",
            ["pure command with zero private activity", "traditional kinship-only", "having no property rules at all"],
            "Mixed economies combine markets with public and regulatory roles—common under modern liberalism.",
            "Students require purity that real liberal democracies rarely show.",
            topic=T_VIA, outcome_code="3.5k",
            skill_tested="Recognizing mixed-economy features",
            difficulty=_d(i + 1), estimated_time_seconds=85,
        ))

    # --- Citizenship supplements ---
    for i, (stem, ans, dists, oc, expl, mist) in enumerate([
        ("Civility is not the same as silence because",
         "citizens can disagree forcefully while still refusing dehumanization",
         ["criticism is always banned", "only applause is legal", "ideology forbids speech"],
         "4.6k",
         "Civility regulates form of disagreement, not the existence of dissent.",
         "Students equate civility with obedience."),
        ("Citizen advocacy differs from mere private grumbling when",
         "people organize to influence public decisions through persuasion and coalition",
         ["they hide opinions forever", "they seize radio towers", "they abolish elections"],
         "4.6k",
         "Advocacy is a named democratic practice.",
         "Students undervalue organized advocacy."),
        ("Antiwar movements test citizenship by asking",
         "when dissent against state violence is a responsibility rather than disloyalty",
         ["whether mill spindles are moral", "whether maps cause wars alone", "whether Smith banned peace"],
         "4.7k",
         "Antiwar movements are a listed conflict context.",
         "Students brand all antiwar dissent as treason automatically."),
        ("Pro-democracy movements abroad matter to Canadian citizenship education because",
         "they highlight rights, participation, and solidarity questions tied to ideology",
         ["they cancel Canadian law", "they replace local voting", "they outlaw Charters"],
         "4.7k",
         "Contemporary and global pro-democracy struggles inform citizenship ideology analysis.",
         "Students treat foreign movements as irrelevant."),
        ("Leadership strategies (4.9k) are weakest when they",
         "impose a single ideology while excluding affected voices from deliberation",
         ["gather evidence", "build coalitions", "include multiple perspectives"],
         "4.9k",
         "Leadership in this program is deliberative and responsible, not domination.",
         "Students confuse leadership with authoritarian command."),
        ("Active citizenship opportunities include digital literacy because",
         "citizens must evaluate media reliability to participate responsibly",
         ["phones abolish democracy", "apps replace rights", "Wi-Fi forbids voting"],
         "4.10k",
         "Media literacy skills support democratic citizenship in contemporary settings.",
         "Students treat digital skills as non-civic."),
        ("McCarthyism warns citizens that",
         "security fear can justify illiberal punishment of dissent inside democracies",
         ["communism invented jazz", "markets forbid film", "détente began in 1690"],
         "4.7k",
         "McCarthyism is named for a reason in 4.7k.",
         "Students reduce it to trivia."),
        ("Worldviews shape ideology when someone",
         "interprets the same crisis through faith, pessimism, or techno-optimism differently",
         ["never thinks", "only flips coins", "outlaws belief"],
         "4.4k",
         "4.4k links worldview and ideology.",
         "Students deny interpretive filters."),
    ]):
        q.append(mc(stem, ans, dists, expl, mist,
                     topic=T_CIT, outcome_code=oc,
                     skill_tested="Extending citizenship and ideology analysis",
                     difficulty=_d(i + 1), estimated_time_seconds=100))

    for i, duo in enumerate([
        ("dissent", "respect for law and order", "marching with a permit while challenging a statute in court"),
        ("political participation", "citizen advocacy", "joining a party and also leading a single-issue lobby"),
        ("civility", "dissent", "criticizing a minister without slurs during question period viewing parties"),
    ]):
        q.append(mc(
            f"The scenario ‘{duo[2]}’ best shows that",
            f"{duo[0]} and {duo[1]} can operate together in liberal citizenship",
            [
                "civic roles never coexist",
                "only fascism allows petitions",
                "ideology bans paired responsibilities",
            ],
            "4.6k presents multiple roles that often must be held jointly.",
            "Students treat roles as mutually exclusive.",
            topic=T_CIT, outcome_code="4.6k",
            skill_tested="Integrating multiple civic roles",
            difficulty="Hard", estimated_time_seconds=115,
        ))

    # Objective NR supplements
    q.append(nr(
        "A principle sort lists individualist liberal principles found in a stem table: "
        "individual rights and freedoms; self-interest; competition; economic freedom; "
        "rule of law; private property. A student highlights only the economic subset: "
        "self-interest; competition; economic freedom; private property. How many principles did the student highlight?",
        "4",
        "Count the four economic-leaning principles named in the stem.",
        "Students include rule of law or rights and answer 5–6.",
        topic=T_ID, outcome_code="1.7k",
        skill_tested="Counting a specified subset of liberal principles",
        difficulty="Medium", estimated_time_seconds=60,
    ))
    q.append(nr(
        "Cold War flashcards show crisis years and alert levels (1–5): 1961: 4; 1962: 5; 1972: 2; 1979: 3. "
        "What alert level is shown for 1962?",
        "5",
        "Read 1962 → 5 from the stem.",
        "Students pick 1961’s 4.",
        topic=T_RES, outcome_code="2.10k",
        skill_tested="Reading alert-level data from a Cold War table",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "A rights instrument matching quiz lists four documents/areas a student correctly identified: "
        "Canadian Charter; Québec Charter; American Bill of Rights; FNMI rights. "
        "How many did the student identify correctly?",
        "4",
        "The stem states four correct identifications.",
        "Students add language legislation and answer 5.",
        topic=T_VIA, outcome_code="3.8k",
        skill_tested="Counting correctly identified rights instruments",
        difficulty="Easy", estimated_time_seconds=35,
    ))
    q.append(nr(
        "Turnout in four student-council elections used as a citizenship mini-case: "
        "2018: 51%; 2019: 47%; 2020: 33%; 2021: 49%. What turnout percentage is listed for 2020?",
        "33",
        "Extract 2020 = 33 from the stem.",
        "Students average the four years.",
        topic=T_CIT, outcome_code="4.6k",
        skill_tested="Reading turnout data tied to political participation",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "A reform timeline lists years when a fictional industrial state adopted modern liberal measures: "
        "factory inspectorate 1878; male household suffrage expansion 1884; old-age pension 1908; "
        "women’s national suffrage 1918; public unemployment insurance 1935. "
        "How many measures are listed on the timeline?",
        "5",
        "Count the five dated measures in the stem.",
        "Students skip one reform and answer 4.",
        topic=T_ORIG, outcome_code="2.8k",
        skill_tested="Counting modern liberal reforms on a timeline",
        difficulty="Easy", estimated_time_seconds=50,
    ))
    q.append(nr(
        "An issues matrix checks whether liberalism is ‘pressured’ (yes=1, no=0) across eight 3.9k issues. "
        "The row sums to 8 ones. How many issues were marked pressured?",
        "8",
        "A sum of eight ones means eight issues marked pressured.",
        "Students answer 3.9 or 9.",
        topic=T_VIA, outcome_code="3.9k",
        skill_tested="Interpreting a simple issues-matrix total",
        difficulty="Easy", estimated_time_seconds=45,
    ))

    # More short scenario MC across units for volume/uniqueness
    # Keep distinctive locale items only (avoid near-duplicate templates)
    q.append(mc(
        "In Harbourview, council protects a minority-language school despite a petition to defund it. "
        "The liberal-democratic reading emphasizes",
        "rights protections may constrain majority will",
        [
            "majority petitions always override entrenched minority rights",
            "language schools are evidence of a command economy",
            "municipal councils must follow one-party purity rules",
        ],
        "Will of the people (3.3k) interacts with rights (3.8k) in liberal democracies.",
        "Students assume a majority petition equals justice automatically.",
        topic=T_VIA, outcome_code="3.3k",
        skill_tested="Balancing majority will and minority-language rights",
        difficulty="Medium", estimated_time_seconds=100,
    ))
    q.append(mc(
        "Prairie Crossing’s school board refuses to scrap Cree immersion after a narrow taxpayer vote. This case best shows",
        "democratic majorities can be limited by collective language and minority protections",
        [
            "tax votes abolish all Charter and Aboriginal rights claims",
            "immersion programs require a command economy",
            "school boards are unauthorized to consider rights arguments",
        ],
        "Collective language rights and minority protections can constrain majority preference.",
        "Students treat every local vote as final for rights questions.",
        topic=T_VIA, outcome_code="3.8k",
        skill_tested="Applying language-rights limits to local democracy",
        difficulty="Hard", estimated_time_seconds=110,
    ))
    q.append(mc(
        "Residents of Cedar Rapids District organize a letter-writing week about polluted wells. This is chiefly",
        "citizen advocacy linking local action to public health responsibility",
        [
            "abandonment of citizenship in favour of private withdrawal",
            "a Cold War brinkmanship exercise between municipalities",
            "proof that ideology never shapes local civic action",
        ],
        "Local advocacy is active citizenship (4.6k/4.10k).",
        "Students dismiss local environmental advocacy as non-ideological.",
        topic=T_CIT, outcome_code="4.10k",
        skill_tested="Recognizing local environmental citizen advocacy",
        difficulty="Easy", estimated_time_seconds=85,
    ))
    q.append(mc(
        "Northbridge neighbours form a monitoring roster to document illegal dumping for council. Best classification:",
        "collective civic advocacy that pairs participation with respect for lawful process",
        [
            "extremism that rejects all democratic institutions",
            "command-economy production quotas for waste",
            "proof citizenship excludes environmental concerns",
        ],
        "Citizen advocacy and political participation can support responsible local governance.",
        "Students label any activist monitoring as extremism.",
        topic=T_CIT, outcome_code="4.6k",
        skill_tested="Classifying lawful collective local advocacy",
        difficulty="Medium", estimated_time_seconds=90,
    ))

    magazines = [
        ("The Weekly Balance", "markets need rules so competition remains fair"),
        ("Commons Ledger", "some goods should stay public to secure equal access"),
        ("Liberty Ink", "speech rights must protect unpopular critics"),
        ("Order & Contract", "predictable courts matter more than charismatic rulers"),
        ("Equal Shares Review", "after-tax gaps threaten social cohesion"),
        ("Green Horizon", "growth without ecological limits is self-defeating"),
    ]
    for i, (mag, claim) in enumerate(magazines):
        q.append(mc(
            f"An editorial in {mag} argues that {claim}. For ideology study, students should first",
            "identify which liberal or collectivist principles the claim prioritizes",
            [
                "memorize the magazine’s fictional address",
                "ignore principles and count adjectives",
                "assume the editorial is nuclear strategy",
            ],
            "Diploma-style source work begins by mapping claims to principles/outcomes.",
            "Students summarize tone without principle coding.",
            topic=T_ID, outcome_code="1.7k",
            skill_tested="Mapping editorial claims to ideological principles",
            difficulty=_d(i + 2), estimated_time_seconds=95,
        ))

    # Final top-up toward ~450 unique stems
    topup = [
        (T_ID, "1.4k", "A mutual-aid pantry run by neighbours beside a luxury condo market most clearly juxtaposes",
         "collectivist mutual responsibility and individualist market housing",
         ["only fascism and communism", "only brinkmanship and détente", "only map scales"],
         "Historic/contemporary individualism–collectivism contrasts (1.4k).",
         "Students force Cold War binaries onto local examples."),
        (T_ID, "1.5k", "Promising a ‘classless future after one decisive rupture’ primarily reveals",
         "a vision for the future characteristic of an ideology",
         ["a bus schedule", "a zoning setback rule only", "a currency ISO code"],
         "Visions for the future are an ideology characteristic (1.5k).",
         "Students miss the characteristic category."),
        (T_ORIG, "2.6k", "Rail networks concentrating labour in factory towns best illustrate",
         "industrialization reshaping society under classical liberal economic expansion",
         ["Charter litigation technique", "nonalignment diplomacy", "Québec language statutes alone"],
         "Industrialization is a 2.6k impact.",
         "Students anachronistically apply Canadian statutes."),
        (T_ORIG, "2.7k", "Defending established churches and gradual reform against rapid liberal remodeling aligns with",
         "classic conservatism",
         ["Marxism", "modern liberal feminism", "Soviet war communism"],
         "Classic conservatism is a listed response ideology.",
         "Students confuse it with neo-conservatism or Marxism."),
        (T_RES, "2.9k", "A one-party state that plans industry and bans rival newspapers is rejecting liberalism mainly by",
         "denying political pluralism, rights, and limited power—even beyond economic planning debates",
         ["offering too many parties", "enforcing Millian individuality", "maximizing Montesquieu’s separations"],
         "Communist rejection includes political-illiberal features (2.9k).",
         "Students discuss only economics."),
        (T_RES, "2.12k", "Calling all progress narratives ‘suspicious local language games’ most closely tracks",
         "postmodern challenges to modern liberal confidence in progress",
         ["Adam Smith’s pin factory notes", "classical conservative throne-and-altar only", "airline yield management"],
         "Postmodernism is listed in 2.12k.",
         "Students mislabel postmodern critique as classical liberalism."),
        (T_VIA, "3.4k", "A government expands child benefits while critics warn about work disincentives. The core exploration is",
         "how far the state should push economic equality tools",
         ["whether missiles have names", "whether Smith disliked pens", "whether maps ban transfers"],
         "3.4k centres economic equality questions.",
         "Students dodge the equality policy question."),
        (T_VIA, "3.7k", "Campaign donors winning niche tax loopholes best exemplifies",
         "interest pressure helping practices diverge from liberal fairness-before-the-law ideals",
         ["perfect classical liberal purity", "nonalignment summitry", "traditional barter only"],
         "3.7k explains principle–practice gaps.",
         "Students moralize without institutional analysis."),
        (T_VIA, "3.9k", "Pandemic rules that fade slowly without evidence reviews threaten viability by",
         "normalizing liberty limits beyond the justified emergency window",
         ["improving pin factories only", "creating nonalignment", "abolishing weather"],
         "Pandemics are a 3.9k issue; temporary limits need ongoing justification.",
         "Students either reject all health rules or accept permanence."),
        (T_CIT, "4.5k", "A voter bloc guided by market-libertarian blogs shows",
         "ideology shaping citizenship preferences and participation",
         ["random citizenship without beliefs", "the end of elections", "command quotas for ballots"],
         "4.5k: ideologies shape citizenship.",
         "Students deny online media as ideological influence."),
        (T_CIT, "4.8k", "Refusing disaster aid to ‘ideological enemies’ among civilians most deserves critique that",
         "ideology should not erase basic humanitarian responsibilities without rigorous justification",
         ["aid is always illegal", "ideology never matters", "only monarchs may help"],
         "4.8k evaluates how far ideology should shape responses.",
         "Students give absolutist free passes to cruelty."),
        (T_CIT, "4.9k", "A youth council co-designs a heat-alert plan with elders. This best models",
         "collective leadership strategy across generations on a public issue",
         ["Führerprinzip", "brinkmanship", "command shoe quotas"],
         "4.9k highlights leadership strategies for issues.",
         "Students overlook youth civic leadership."),
        (T_ID, "1.9k", "Congestion charges that fund transit while limiting some driving choices stage a conflict between",
         "individual mobility preferences and common urban goods",
         ["only medieval guilds", "only nuclear spoilers", "only airline liveries"],
         "Individualism–common good dynamic (1.9k).",
         "Students miss the framed tension."),
        (T_ORIG, "2.8k", "Legal recognition of collective bargaining most clearly marks",
         "modern liberal reform of classical laissez-faire labour markets",
         ["Nazi labour front ideology as liberalism", "abolition of unions by definition of liberalism", "nonalignment labour law"],
         "Labour standards and unions are 2.8k markers.",
         "Students misread unions as fascism or as anti-liberal always."),
        (T_RES, "2.11k", "Survey grids converting communal territories into alienable lots are analyzed as",
         "imposition of liberal property logics on other land relationships",
         ["spontaneous Indigenous invention of NATO", "Smithian détente", "Charter section trivia only"],
         "Imposition perspectives (2.11k).",
         "Students deny property liberalism’s impositions."),
        (T_VIA, "3.6k", "A democracy jails satirists while still holding elections. The illiberalism lesson is that",
         "electoral form can coexist with repression of expression",
         ["elections make repression impossible by definition", "satire proves command economics", "humour bans are mixed economies"],
         "Illiberal practice inside democracies (3.6k).",
         "Students think elections immunize against illiberalism."),
        (T_VIA, "3.5k", "Elders allocate grazing turns by longstanding custom without prices or plans. Label:",
         "traditional economy",
         ["free market economy", "command economy", "representative democracy"],
         "Traditional economies are listed in 3.5k.",
         "Students force market/command labels onto custom systems."),
        (T_ORIG, "2.5k", "‘Life, liberty, property as pre-political claims binding rulers’ is closest to",
         "Lockean classical liberal natural-rights language",
         ["Stalinist class-enemy categories", "Nazi racial cosmology", "Maoist continuous revolution slogans"],
         "Locke is central in 2.5k.",
         "Students attach rights talk to illiberal icons."),
        (T_RES, "2.10k", "Installing a crisis hotline after a nuclear scare while rivalry continues is nearest to managing",
         "deterrence risks on the road toward limited détente practices",
         ["residential school policy", "municipal compost only", "pin-factory aesthetics"],
         "Deterrence/détente interplay in 2.10k.",
         "Students unrelated Canadian domestic labels."),
        (T_CIT, "4.6k", "Training as a scrutineer primarily enacts",
         "political participation supporting electoral integrity",
         ["command planning", "racial hierarchy ideology", "rejection of citizenship"],
         "Political participation is a 4.6k practice.",
         "Students undervalue electoral roles."),
    ]
    for i, (topic, oc, stem, ans, dists, expl, mist) in enumerate(topup):
        q.append(mc(
            stem, ans, dists, expl, mist,
            topic=topic, outcome_code=oc,
            skill_tested="Final-pool curriculum application",
            difficulty=_d(i), estimated_time_seconds=90 + (i % 4) * 10,
        ))

    return q
