"""Resistance, Viability, and Citizenship question banks for SOC30-1 pool."""

from __future__ import annotations

from .helpers import mc, nr

T_RES = "Resistance to Liberalism"
T_VIA = "The Viability of Contemporary Liberalism"
T_CIT = "Citizenship and Ideology"

DIFFS = ("Easy", "Medium", "Hard")


def _d(i: int) -> str:
    return DIFFS[i % 3]


def _t(i: int) -> int:
    return (70, 95, 120)[i % 3]


def build_questions() -> list:
    q: list = []
    q.extend(_resistance())
    q.extend(_viability())
    q.extend(_citizenship())
    return q


def _resistance() -> list:
    q: list = []

    # 2.9k — systems that rejected liberalism
    ussr_features = [
        ("one-party rule silencing rival parties", "rejection of competitive liberal political pluralism"),
        ("forced collectivization of agriculture", "abolition of liberal private-property norms in the countryside"),
        ("state ownership of industry under planning", "command control replacing liberal market allocation"),
        ("secret-police intimidation of dissidents", "crushing individual rights and freedoms associated with liberalism"),
        ("censorship of press and literature", "denial of liberal free expression"),
        ("show trials that abandoned fair procedure", "attack on rule-of-law expectations"),
        ("class-enemy categories overriding equal citizenship", "illiberal subordination of persons to ideological class war"),
        ("closed borders limiting voluntary exit", "constraint on personal liberty prized in liberal thought"),
    ]
    for i, (feat, ans) in enumerate(ussr_features):
        q.append(mc(
            f"In the Soviet context, {feat} is best interpreted as",
            ans,
            [
                "a modern liberal expansion of welfare rights",
                "a classical liberal defence of laissez-faire",
                "an example of Canadian Charter balancing",
            ],
            "Outcome 2.9k evaluates communism in the Soviet Union as an ideological system that rejected liberal principles.",
            "Students mislabel Soviet practices as modern liberalism because both critique laissez-faire.",
            topic=T_RES, outcome_code="2.9k",
            skill_tested="Evaluating Soviet rejection of liberal principles",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))

    nazi_features = [
        ("Führer principle concentrating authority", "rejection of liberal limited government and divided power"),
        ("racial hierarchy as state ideology", "denial of equal individual rights central to liberalism"),
        ("abolition of genuine multiparty competition", "destruction of liberal democratic contestation"),
        ("Gleichschaltung forcing institutions into party line", "elimination of pluralist civil society space"),
        ("aggressive expansionism framed as destiny", "illiberal subordination of other peoples to racial empire"),
        ("terror against targeted minorities", "violent negation of liberal protections of persons"),
        ("corporative myths denying independent labour politics", "closing liberal channels for dissent and association"),
        ("propaganda monopolies replacing open debate", "attack on liberal media and viewpoint pluralism"),
    ]
    for i, (feat, ans) in enumerate(nazi_features):
        q.append(mc(
            f"Nazi Germany’s use of {feat} most clearly demonstrates",
            ans,
            [
                "commitment to Mill’s harm principle",
                "Lockean consent as the regime’s core",
                "Smithian belief in open competitive markets as the highest end",
            ],
            "Outcome 2.9k treats fascism in Nazi Germany as rejecting principles of liberalism.",
            "Students confuse fascist economic interventions with modern liberal welfare democracy.",
            topic=T_RES, outcome_code="2.9k",
            skill_tested="Evaluating fascist rejection of liberalism",
            difficulty=_d(i + 1), estimated_time_seconds=_t(i + 1),
        ))

    compare_reject = [
        (
            "Both Soviet communism and Nazi fascism, despite opposing economic myths, rejected liberalism by",
            "concentrating power and crushing pluralist rights-based politics",
            ["implementing Canadian-style Charter review", "maximizing laissez-faire night-watchman states", "prioritizing Montesquieu’s separated powers"],
        ),
        (
            "A key distinction stressed in 30-1 is that Soviet ideology claimed classless equality while Nazism claimed",
            "racial hierarchy and national rebirth through exclusion",
            ["identical Lockean natural rights for all", "Adam Smith’s invisible hand as official dogma", "UN Charter feminist labour codes as its origin"],
        ),
        (
            "When an exam source shows smashed ballot boxes under a single-party banner, the liberal principle most directly rejected is",
            "political competition and citizen rights to choose governments",
            ["public transit ownership alone", "progressive income tax alone", "municipal snow clearing"],
        ),
        (
            "Night-of-terror roundups of unpopular minorities primarily assault which liberal commitment?",
            "individual rights and freedoms under rule of law",
            ["airline price competition", "patent length debates", "municipal zoo funding"],
        ),
    ]
    for i, (stem, ans, dist) in enumerate(compare_reject):
        q.append(mc(
            stem, ans, dist,
            "Systems that rejected liberalism (2.9k) attacked rights, pluralism, and limited power even when their economic stories differed.",
            "Students equate ‘anti-liberal’ only with ‘left’ or only with ‘right,’ missing the shared illiberal features.",
            topic=T_RES, outcome_code="2.9k",
            skill_tested="Comparing systems that rejected liberalism",
            difficulty=_d(i + 2), estimated_time_seconds=110,
        ))

    # 2.10k Cold War
    cold_war = [
        ("expansionism", "A superpower extends influence into neighbouring states through force or satellite control.",
         "pushing a bloc’s system outward beyond prior borders"),
        ("containment", "Diplomats argue communism must be held behind a perimeter through alliances and aid.",
         "strategies aimed at stopping further ideological expansion"),
        ("deterrence", "Leaders stockpile second-strike nuclear forces so adversaries fear catastrophic retaliation.",
         "discouraging attack by threatening unacceptable costs"),
        ("brinkmanship", "Negotiators push a crisis near conflict to compel the other side to back down.",
         "coercive crisis tactics that risk open war for leverage"),
        ("détente", "Rivals sign arms limits and increase trade to lower tension without ending competition.",
         "easing of strained relations while rivalry continues"),
        ("nonalignment", "A newly independent state refuses formal membership in either Cold War bloc.",
         "staying outside the two-camp alliance structure"),
        ("liberation movements", "Anti-colonial fighters seek independence amid superpower courting and weapons flows.",
         "struggles to end imperial control in a bipolar world"),
    ]
    for i, (term, scene, gloss) in enumerate(cold_war):
        wrong = [t for t, _, _ in cold_war if t != term][:3]
        q.append(mc(
            f"{scene} This pattern is best labelled",
            term,
            wrong,
            f"Outcome 2.10k includes {term} among ways ideological conflict shaped postwar international relations. {gloss.capitalize()}.",
            "Students swap containment, deterrence, and brinkmanship when crisis vocabulary overlaps.",
            topic=T_RES, outcome_code="2.10k",
            skill_tested=f"Identifying Cold War concept: {term}",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))
        q.append(mc(
            f"Which vignette best matches {term}?",
            scene,
            [s for t, s, _ in cold_war if t != term][:3],
            f"{term}: {gloss}.",
            f"Students attach the wrong vignette to {term}.",
            topic=T_RES, outcome_code="2.10k",
            skill_tested=f"Matching scenarios to {term}",
            difficulty=_d(i + 1), estimated_time_seconds=100,
        ))

    # 2.11k imposition
    imposition = [
        (
            "Residential school policies aimed at assimilating Indigenous children into settler norms",
            "imposition of liberal-settler cultural and political expectations on Aboriginal peoples",
        ),
        (
            "Treaty processes that extinguished Aboriginal title while promising ‘civilizing’ benefits",
            "liberal legal frameworks used to restructure Indigenous land and governance",
        ),
        (
            "Band councils redesigned under federal statutes modelled on European municipal forms",
            "reshaping Indigenous political authority through imposed liberal institutional templates",
        ),
        (
            "Contemporary trade packages that demand market openings as the price of recognition",
            "ongoing debates about imposing liberal economic norms on communities with other priorities",
        ),
        (
            "Mission schools teaching private property as moral duty while forbidding ceremony",
            "cultural imposition framed as liberal progress",
        ),
        (
            "Survey grids overlaying communal territories with alienable parcels",
            "property liberalism inscribed onto landscapes previously ordered differently",
        ),
    ]
    for i, (scene, ans) in enumerate(imposition):
        q.append(mc(
            f"{scene}. For outcome 2.11k, this is best analyzed as",
            ans,
            [
                "proof Aboriginal peoples invented nuclear deterrence",
                "a pure example of Soviet collectivization in Canada",
                "evidence liberalism never influenced Canadian history",
            ],
            "Outcome 2.11k examines perspectives on the imposition of liberalism, including Aboriginal experiences.",
            "Students deny imposition or treat all liberalism as identical to fascism.",
            topic=T_RES, outcome_code="2.11k",
            skill_tested="Analyzing imposition of liberalism perspectives",
            difficulty=_d(i + 2), estimated_time_seconds=115,
        ))

    # 2.12k alternative thought
    alternatives = [
        ("Aboriginal collective thought", "decisions prioritize reciprocal duties to kin and land over atomized consumer choice"),
        ("environmentalism", "resource use must respect ecological limits even when markets demand more extraction"),
        ("religious perspectives", "public ethics should answer revealed obligations, not only individual preference"),
        ("neo-conservatism", "modern welfare liberalism should be rolled back toward stronger markets and traditional social norms"),
        ("postmodernism", "grand ideological narratives of inevitable progress deserve suspicion and deconstruction"),
        ("extremism", "violence or absolute purity tests replace pluralist persuasion inside liberal orders"),
    ]
    for i, (label, scene) in enumerate(alternatives):
        wrong = [a for a, _ in alternatives if a != label][:3]
        q.append(mc(
            f"A movement argues that {scene}. The challenge to modern liberalism most accurately labelled is",
            label,
            wrong,
            "Outcome 2.12k lists Aboriginal collective thought, environmentalism, religious perspectives, neo-conservatism, postmodernism, and extremism.",
            f"Students confuse {label} with classical liberalism or with Soviet communism automatically.",
            topic=T_RES, outcome_code="2.12k",
            skill_tested=f"Identifying alternative thought: {label}",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))

    # 2.13k evaluate resistance
    evaluate = [
        (
            "A dissident underground publishes banned literature under a fascist regime",
            "resistance can be justified when liberalism’s rights are violently extinguished",
        ),
        (
            "Paramilitaries bomb civilian markets to ‘purify’ a democracy they dislike",
            "violent extremism may claim resistance while violating the civic values it pretends to defend",
        ),
        (
            "Indigenous land defenders use courts and peaceful blockades against imposed resource projects",
            "resistance may be framed as defending collective continuity against imposition of liberal development norms",
        ),
        (
            "A lobby seeks to dismantle all elections because markets alone should rule",
            "rejection of democratic self-government undercuts liberal political principles even if framed as freedom",
        ),
        (
            "Citizens repeal emergency powers that indefinitely suspended hearings without review",
            "resistance to illiberal security practices should be weighed against genuine safety needs",
        ),
        (
            "Activists refuse vaccines while denying others’ hospital access during crisis",
            "claims of liberal freedom can conflict with collective responsibilities—evaluation must weigh harms",
        ),
    ]
    for i, (scene, ans) in enumerate(evaluate):
        q.append(mc(
            f"{scene}. The most balanced 30-1 evaluation is that",
            ans,
            [
                "resistance is never justifiable under any condition",
                "any opposition to markets is automatically fascism",
                "evaluation is unnecessary because ideology never matters",
            ],
            "Outcome 2.13k requires evaluating the extent to which resistance to liberalism is justified—case by case, not with slogans.",
            "Students give absolute yes/no instead of criterion-based evaluation.",
            topic=T_RES, outcome_code="2.13k",
            skill_tested="Evaluating justifications for resistance to liberalism",
            difficulty=_d(i + 1), estimated_time_seconds=130,
        ))

    # Two distinct containment scenarios only (avoid year-loop clones)
    q.append(mc(
        "A 1949 memorandum argues Western aid should shore up vulnerable governments so a rival ideology gains no further foothold in Europe. "
        "The Cold War concept highlighted is chiefly",
        "containment",
        [
            "détente focused on easing tension through trade and arms talks",
            "nonalignment by refusing membership in either bloc",
            "brinkmanship pushing a crisis to the edge of open war",
        ],
        "Containment strategies aimed to prevent further expansion of rival ideology without necessarily seeking immediate détente.",
        "Students call every postwar aid policy brinkmanship or détente.",
        topic=T_RES, outcome_code="2.10k",
        skill_tested="Identifying containment in early Cold War aid policy",
        difficulty="Medium", estimated_time_seconds=95,
    ))
    q.append(mc(
        "Alliance planners in Asia justify security commitments as a perimeter against further ideological expansion after a neighbouring state falls to a rival system. "
        "This reasoning best matches",
        "containment",
        [
            "postmodern rejection of all political narratives",
            "classical conservative defence of hereditary monarchy alone",
            "welfare capitalism inside a single private firm",
        ],
        "Containment frames policy as stopping further expansion of a rival ideology.",
        "Students confuse containment with domestic welfare arrangements.",
        topic=T_RES, outcome_code="2.10k",
        skill_tested="Applying containment beyond European examples",
        difficulty="Hard", estimated_time_seconds=100,
    ))

    for i, actor in enumerate([
        "a Guatemalan reformer courted by rival intelligence services",
        "an Indonesian conference hosting newly independent states",
        "a Berlin corridor crisis with tanks facing tanks",
        "a hotline installed after nuclear scare",
        "a proxy war funded quietly on another continent",
        "a trade deal paired with missile caps",
    ]):
        concept = [
            "liberation movements / ideological patronage",
            "nonalignment",
            "brinkmanship",
            "deterrence management after crisis",
            "expansionism via proxies",
            "détente tools",
        ][i]
        q.append(mc(
            f"Considering {actor}, a 30-1 analysis should connect the episode primarily to",
            concept,
            [
                "Mill’s harm principle as a Nazi slogan",
                "residential school curriculum design only",
                "municipal recycling bylaws alone",
            ],
            "Postwar ideological conflict (2.10k) includes alliance crises, nonalignment, proxies, and détente instruments.",
            "Students ignore the international ideological frame.",
            topic=T_RES, outcome_code="2.10k",
            skill_tested="Linking Cold War episodes to course concepts",
            difficulty=_d(i + 2), estimated_time_seconds=105,
        ))

    q.append(nr(
        "A comparison chart lists seven Cold War concepts from outcome 2.10k: expansionism; containment; "
        "deterrence; brinkmanship; détente; nonalignment; liberation movements. How many concepts are listed?",
        "7",
        "The PoS brackets seven concepts under postwar ideological conflict.",
        "Students omit nonalignment or liberation movements.",
        topic=T_RES, outcome_code="2.10k",
        skill_tested="Counting Cold War concepts from a supplied list",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "A quiz table shows estimated nuclear warheads for Superpower A across four review years: "
        "1955: 2000; 1965: 5000; 1975: 9000; 1985: 12000. What value is listed for 1965?",
        "5000",
        "Read 1965 = 5000 from the stem table.",
        "Students pick 1975’s 9000 or sum the column.",
        topic=T_RES, outcome_code="2.10k",
        skill_tested="Reading a numeric value from a deterrence-related table",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "Alternative-thought cards list: Aboriginal collective thought; environmentalism; religious perspectives; "
        "neo-conservatism; postmodernism; extremism. How many challenges are listed?",
        "6",
        "Outcome 2.12k lists six alternative thought challenges.",
        "Students add Marxism or fascism from 2.9k.",
        topic=T_RES, outcome_code="2.12k",
        skill_tested="Counting alternative thought categories from a list",
        difficulty="Easy", estimated_time_seconds=40,
    ))

    return q


def _viability() -> list:
    q: list = []

    # 3.3k will of the people
    will = [
        (
            "A government loses repeated free elections yet refuses to leave office",
            "failure to reflect the democratic will of the people",
        ),
        (
            "Voters approve a referendum that politicians then ignore without legal process",
            "tension between popular will and elite noncompliance",
        ),
        (
            "Courts strike down a popular law that violates entrenched rights",
            "liberal democracies sometimes limit majority will to protect rights",
        ),
        (
            "Authorities ban opposition campaigns before polling day",
            "undermining fair measurement of the people’s will",
        ),
        (
            "Citizen assemblies recommend electoral reform that legislatures adopt",
            "institutional efforts to translate public judgment into policy",
        ),
        (
            "Emergency decrees continue years after the crisis without legislative renewal",
            "executive practice drifting from ongoing popular authorization",
        ),
    ]
    for i, (scene, ans) in enumerate(will):
        q.append(mc(
            f"{scene}. The case best invites exploration of",
            ans,
            [
                "whether Adam Smith designed the Charter",
                "whether nuclear deterrence invented municipalities",
                "whether public property forbids sidewalks",
            ],
            "Outcome 3.3k explores how far governments should reflect the will of the people.",
            "Students treat majority will as always absolute or never relevant.",
            topic=T_VIA, outcome_code="3.3k",
            skill_tested="Exploring governments and the will of the people",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))

    # 3.4k economic equality
    equality = [
        ("steeply progressive taxes funding universal pharmacare", "government action aimed at greater economic equality"),
        ("abolishing all transfers so market incomes stand untouched", "retreat from state-driven economic equalization"),
        ("raising minimum wages while debating small-business impacts", "policy trade-offs around economic equality tools"),
        ("regional development grants to poorer provinces", "redistributive efforts across uneven economies"),
        ("regressive fees that hit low-income riders hardest", "policy that may worsen economic inequality"),
        ("sovereign wealth dividends paid equally to residents", "equalizing cash transfers from shared resource wealth"),
    ]
    for i, (scene, ans) in enumerate(equality):
        q.append(mc(
            f"A legislature considers {scene}. Analysis under 3.4k should centre on",
            ans,
            [
                "Montesquieu’s views on mill child labour only",
                "whether brinkmanship names a ballet",
                "airline logo redesigns",
            ],
            "Outcome 3.4k explores the extent to which governments should encourage economic equality.",
            "Students moralize without naming the equality policy question.",
            topic=T_VIA, outcome_code="3.4k",
            skill_tested="Exploring government roles in economic equality",
            difficulty=_d(i + 1), estimated_time_seconds=_t(i),
        ))

    # 3.5k systems
    systems = [
        ("consensus decision making", "Participants discuss until a broadly acceptable agreement emerges rather than a simple majority crush."),
        ("direct democracy", "Citizens themselves vote on statutes in frequent referendums."),
        ("representative democracy", "Elected legislators debate and pass laws on voters’ behalf."),
        ("authoritarian political systems", "Power is concentrated; meaningful opposition and rights are sharply limited."),
        ("traditional economies", "Custom and kinship largely allocate work and goods."),
        ("free market economies", "Private owners and prices coordinate most production with limited direction."),
        ("command economies", "Central planners set output and allocate resources by directive."),
        ("mixed economies", "Markets operate alongside substantial public services, regulation, and transfers."),
    ]
    for i, (label, scene) in enumerate(systems):
        wrong = [s for s, _ in systems if s != label][:3]
        q.append(mc(
            f"{scene} This description best matches",
            label,
            wrong,
            "Outcome 3.5k requires analyzing political and economic systems in relation to liberalism’s principles.",
            f"Students confuse {label} with neighbouring system labels.",
            topic=T_VIA, outcome_code="3.5k",
            skill_tested=f"Identifying system: {label}",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))
        q.append(mc(
            f"Relative to principles of liberalism, {label} is most accurately assessed as",
            {
                "consensus decision making": "potentially compatible when participation and rights remain intact",
                "direct democracy": "compatible with popular sovereignty yet possibly tense with minority rights",
                "representative democracy": "a common liberal-democratic mechanism for translating citizenship into law",
                "authoritarian political systems": "largely incompatible with liberal political rights and limited power",
                "traditional economies": "not defined as liberal markets, though liberalism may encounter them",
                "free market economies": "aligned with economic freedom yet possibly harsh without rights/welfare offsets",
                "command economies": "largely at odds with liberal economic freedom and private property norms",
                "mixed economies": "often how modern liberal democracies combine markets with public aims",
            }[label],
            [
                "identical to Nazi racial theory in every case",
                "proof ideology never shapes economies",
                "forbidden by all definitions of citizenship",
            ],
            "3.5k asks how far practices reflect liberal principles—not a single slogan.",
            "Students treat every non-market trait as fascism or every market as justice.",
            topic=T_VIA, outcome_code="3.5k",
            skill_tested=f"Assessing {label} against liberal principles",
            difficulty="Hard", estimated_time_seconds=125,
        ))

    # 3.6k illiberal practices in democracies
    illiberal = [
        (
            "A democracy indefinitely detains citizens without charge after a panic statute",
            "illiberal security practice inside a formally liberal democratic state",
        ),
        (
            "Police break up peaceful press conferences while elections still occur",
            "illiberal constraint on expression coexisting with electoral form",
        ),
        (
            "A majority uses ordinary legislation to strip a minority’s language school rights",
            "democratic procedure delivering illiberal outcomes for a minority",
        ),
        (
            "Surveillance laws gather opposition data with weak oversight",
            "security tools that can become illiberal within democracies",
        ),
        (
            "Emergency powers renew automatically without parliamentary debate",
            "normalized exceptionalism risking illiberal governance habits",
        ),
        (
            "Partisan officials purge independent statistical agencies",
            "eroding information integrity needed for liberal accountability",
        ),
        (
            "Canada’s historical use of the War Measures Act / emergencies powers prompts classroom debate",
            "Canadian examples used to analyze illiberal moments inside liberal democracy",
        ),
        (
            "A wartime democracy interned citizens on ethnic suspicion despite constitutional rhetoric",
            "historic illiberal practice under democratic wartime governments",
        ),
    ]
    for i, (scene, ans) in enumerate(illiberal):
        q.append(mc(
            f"{scene}. The strongest 30-1 classification is",
            ans,
            [
                "classical liberalism at its laissez-faire purest",
                "proof democracies cannot act illiberally by definition",
                "identical to nonalignment foreign policy",
            ],
            "Outcome 3.6k analyzes how liberal democracies can reflect illiberal thought and practice (Canada and contemporary examples). "
            "Illiberalism here means practices inside democracies that undercut liberal rights/norms—not a synonym for all dictatorship.",
            "Students believe illiberalism only exists outside democracies.",
            topic=T_VIA, outcome_code="3.6k",
            skill_tested="Identifying illiberal practices in democracies",
            difficulty=_d(i + 2), estimated_time_seconds=120,
        ))

    # 3.7k why practices diverge
    diverge = [
        ("voters reward short-term stimulus over long-term fiscal rules", "electoral incentives can pull governments from liberal economic restraint"),
        ("security bureaucracies expand quietly after attacks", "institutional momentum can outpace liberal oversight norms"),
        ("lobbyists secure exemptions that distort competitive markets", "interest power may warp liberal equality before the law in markets"),
        ("coalition partners force compromises that dilute platform rights pledges", "governing arithmetic may separate practice from liberal promises"),
        ("public panic after scandals demands visible crackdowns", "popular pressure can authorize illiberal shortcuts"),
        ("international lenders condition loans on rapid privatization", "external constraints shape how liberal reforms appear in practice"),
    ]
    for i, (scene, ans) in enumerate(diverge):
        q.append(mc(
            f"Governments sometimes diverge from liberal principles when {scene}. The best analytic focus is",
            ans,
            [
                "that ideology labels have no practical effects",
                "that only monarchies face such pressures",
                "that GDP forbids political analysis",
            ],
            "Outcome 3.7k analyzes why government practices may not reflect principles of liberalism.",
            "Students answer with conspiracy slogans instead of institutional incentives.",
            topic=T_VIA, outcome_code="3.7k",
            skill_tested="Explaining gaps between liberal principles and practice",
            difficulty=_d(i), estimated_time_seconds=110,
        ))

    # 3.8k rights documents
    rights = [
        ("American Bill of Rights", "early constitutional amendments limiting federal power over speech, religion, and fair process"),
        ("Canadian Charter of Rights and Freedoms", "constitutional rights enforceable in Canadian courts, subject to justified limits"),
        ("Québec Charter of Human Rights and Freedoms", "provincial quasi-constitutional rights instrument within Québec’s legal order"),
        ("First Nations, Métis and Inuit rights", "distinct Aboriginal and treaty rights recognized alongside other Canadian rights regimes"),
        ("language legislation", "statutes shaping official language use in services, schools, or workplaces"),
        ("emergencies and security legislation", "laws granting exceptional powers that must be weighed against rights protections"),
    ]
    for i, (label, gloss) in enumerate(rights):
        wrong = [r for r, _ in rights if r != label][:3]
        q.append(mc(
            f"Which label best fits the following: {gloss}?",
            label,
            wrong,
            "Outcome 3.8k evaluates how far governments should promote individual and collective rights, naming these instruments and issues.",
            f"Students mix up {label} with another rights document or statute type.",
            topic=T_VIA, outcome_code="3.8k",
            skill_tested=f"Identifying rights framework: {label}",
            difficulty=_d(i + 1), estimated_time_seconds=100,
        ))
        q.append(mc(
            f"A case hinging on {label} most directly supports classroom focus on",
            "evaluating promotion of individual and/or collective rights within liberal democracy",
            [
                "memorizing Adam Smith’s birth parish only",
                "plotting missile throw-weights alone",
                "listing mill machines by brand",
            ],
            "3.8k centres rights promotion questions, not trivia.",
            "Students reduce rights cases to memorization disconnected from viability of liberalism.",
            topic=T_VIA, outcome_code="3.8k",
            skill_tested="Connecting rights instruments to outcome 3.8k",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    # 3.9k contemporary issues
    issues = [
        ("environment concerns", "carbon limits challenge unlimited consumer choice yet may protect shared ecological goods"),
        ("resource use and development", "pipeline disputes pit economic freedom and jobs against land and community claims"),
        ("debt and poverty", "austerity or stimulus debates test liberalism’s capacity to secure dignified life chances"),
        ("racism", "equal rights promises collide with systemic discrimination inside liberal societies"),
        ("pandemics", "quarantines and mandates strain liberty while aiming at common health"),
        ("terrorism", "security responses may expand surveillance beyond liberal comfort"),
        ("censorship", "content bans claim safety or dignity while risking viewpoint suppression"),
        ("illiberalism", "elected leaders hollow out courts and media even without formal coups"),
    ]
    for i, (issue, gloss) in enumerate(issues):
        q.append(mc(
            f"Debates over {issue} test liberalism’s viability because",
            gloss,
            [
                "ideology vanished after 1991 automatically",
                "only traditional economies face modern issues",
                "Montesquieu banned discussion of health",
            ],
            "Outcome 3.9k evaluates liberalism amid environment, resources, debt/poverty, racism, pandemics, terrorism, censorship, and illiberalism.",
            f"Students treat {issue} as irrelevant to ideology.",
            topic=T_VIA, outcome_code="3.9k",
            skill_tested=f"Evaluating liberalism amid {issue}",
            difficulty=_d(i), estimated_time_seconds=115,
        ))
        q.append(mc(
            f"A source booklet pairs conflicting perspectives on {issue}. The 30-1 task is primarily to",
            "evaluate how liberal principles hold up when this contemporary pressure intensifies",
            [
                "ignore principles and count syllables",
                "assume fascism and liberalism are synonyms",
                "reduce the issue to a single multiple of GDP",
            ],
            "Viability analysis weighs principles against contemporary strains using multiple perspectives.",
            "Students pick a side slogan without principle-based evaluation.",
            topic=T_VIA, outcome_code="3.9k",
            skill_tested=f"Framing viability analysis for {issue}",
            difficulty=_d(i + 2), estimated_time_seconds=120,
        ))

    # Canada-focused viability extras
    canada_cases = [
        ("3.5k", "Canada’s blend of private enterprise, public health care, and regulation is typically classified as",
         "a mixed economy",
         ["a pure command economy with no markets", "a traditional kinship-only economy", "an economy without property law"],
         "Mixed economies combine markets with public provision—common in liberal democracies.",
         "Students call Canada a command economy because of health care."),
        ("3.5k", "Parliamentary elections with competing parties most closely exemplify",
         "representative democracy",
         ["command economy planning boards", "traditional barter alone", "Führerprinzip"],
         "Voters authorize representatives rather than voting every statute.",
         "Students confuse representative with direct democracy."),
        ("3.6k", "Internment of Japanese Canadians during WWII is studied in 30-1 chiefly as",
         "an illiberal practice carried out by a wartime democracy",
         ["proof Canada was a Soviet republic", "a détente cultural exchange", "a free-market textbook example"],
         "Canadian history supplies examples of illiberal practice inside democratic forms.",
         "Students deny democracies can act illiberally."),
        ("3.8k", "Section 1 of the Canadian Charter allows justified limits on rights. This structure mainly shows",
         "liberal democracies balancing rights against pressing objectives under law",
         ["abolition of all rights", "command pricing of speech", "nonalignment foreign policy"],
         "Charter rights are real yet not absolute—central to 3.8k evaluation.",
         "Students think any limit equals fascism, or that rights never limit government."),
        ("3.9k", "A province debates logging in caribou habitat while towns fear job loss. Viability analysis should weigh",
         "economic freedom and development against environmental and collective land concerns",
         ["only airline privatization trivia", "only seventeenth-century absolutism", "only nuclear throw-weight tables"],
         "Resource and environment issues are named in 3.9k.",
         "Students ignore one pole of the trade-off."),
        ("3.4k", "Guaranteed basic income pilots are best discussed under",
         "how far governments should encourage economic equality",
         ["whether Montesquieu invented vaccines", "Cold War brinkmanship etiquette", "airline livery"],
         "Equality-promoting instruments sit under 3.4k.",
         "Students misfile income policy under nuclear strategy."),
    ]
    for i, (oc, stem, ans, dist, expl, mist) in enumerate(canada_cases):
        q.append(mc(
            stem, ans, dist, expl, mist,
            topic=T_VIA, outcome_code=oc,
            skill_tested="Applying viability concepts to Canadian cases",
            difficulty=_d(i), estimated_time_seconds=105,
        ))

    # More system application stems
    for i, country in enumerate([
        "Nordica (fictional) with private shops plus universal care",
        "Planovia (fictional) with state-set shoe quotas",
        "Electia (fictional) with free media and multiparty ballots",
        "Strongia (fictional) with jails for peaceful bloggers",
        "Customia (fictional) where elders assign harvest shares by custom",
        "Referendia (fictional) where citizens vote monthly on tax rates",
    ]):
        mapping = [
            ("mixed economy features inside a liberal welfare order", "3.5k"),
            ("command economy allocation", "3.5k"),
            ("representative / liberal democratic political practice", "3.5k"),
            ("authoritarian political practice incompatible with liberal rights", "3.5k"),
            ("traditional economy patterns", "3.5k"),
            ("direct democracy mechanisms", "3.5k"),
        ][i]
        q.append(mc(
            f"{country} is described in a source set. The best system label for the highlighted feature is",
            mapping[0],
            [
                "proof ideology never varies by place",
                "identical to Adam Smith’s pin factory alone",
                "a numerical radar frequency",
            ],
            "Invented cases still map to 3.5k system categories used in Alberta’s program of studies.",
            "Students refuse to classify fictionalized diploma-style countries.",
            topic=T_VIA, outcome_code=mapping[1],
            skill_tested="Classifying political/economic systems from sources",
            difficulty=_d(i + 1), estimated_time_seconds=100,
        ))

    # NR for viability — objective reads
    q.append(nr(
        "A rights-review worksheet lists six focus areas from outcome 3.8k: American Bill of Rights; "
        "Canadian Charter of Rights and Freedoms; Québec Charter of Human Rights and Freedoms; "
        "First Nations, Métis and Inuit rights; language legislation; emergencies and security legislation. "
        "How many focus areas are listed?",
        "6",
        "Count the six bracketed areas in 3.8k as enumerated in the stem.",
        "Students merge the two Charters and undercount.",
        topic=T_VIA, outcome_code="3.8k",
        skill_tested="Counting rights-related focus areas from a list",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "A contemporary-issues checklist names: environment concerns; resource use and development; "
        "debt and poverty; racism; pandemics; terrorism; censorship; illiberalism. How many issues are named?",
        "8",
        "Outcome 3.9k lists eight contemporary issue areas.",
        "Students omit illiberalism or censorship.",
        topic=T_VIA, outcome_code="3.9k",
        skill_tested="Counting contemporary viability issues from a list",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "An economic-system chart in the stem shows unemployment rates: Marketland 6%; Mixland 7%; "
        "Commandland 4% (official); Tradland not reported. What unemployment percentage is shown for Mixland?",
        "7",
        "Read Mixland = 7 from the stem.",
        "Students average the numbers or pick Marketland.",
        topic=T_VIA, outcome_code="3.5k",
        skill_tested="Reading an unemployment figure from a comparative table",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "Poll data in a source show support for stronger equality policy: Age 18–29: 62%; 30–49: 48%; "
        "50–64: 41%; 65+: 38%. What percentage support is listed for ages 30–49?",
        "48",
        "Extract 48 from the supplied poll table.",
        "Students pick 62 from the youngest cohort.",
        topic=T_VIA, outcome_code="3.4k",
        skill_tested="Reading poll percentages on equality policy",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "A classroom tally records how many of the following system cards are political (not economic): "
        "consensus decision making; direct democracy; representative democracy; authoritarian political systems; "
        "traditional economies; free market economies; command economies; mixed economies. "
        "Count only the political cards listed.",
        "4",
        "Political: consensus, direct democracy, representative democracy, authoritarian (4). "
        "Economic: traditional, free market, command, mixed (4).",
        "Students count all eight or miss consensus as political.",
        topic=T_VIA, outcome_code="3.5k",
        skill_tested="Counting political system cards from a mixed list",
        difficulty="Medium", estimated_time_seconds=70,
    ))

    # Additional viability MC for volume
    for i, pair in enumerate([
        ("free market economies", "command economies", "private price signals versus central directives"),
        ("direct democracy", "representative democracy", "citizen-voted laws versus legislator-made laws"),
        ("mixed economies", "traditional economies", "regulated markets with public services versus custom-based allocation"),
        ("authoritarian political systems", "representative democracy", "concentrated coercion versus competitive elections and rights"),
    ]):
        a, b, contrast = pair
        q.append(mc(
            f"The clearest contrast between {a} and {b} for 30-1 purposes is",
            contrast,
            [
                "that both equally enact Mill’s feminism",
                "that both forbid any ideology discussion",
                "that both are identical to nonalignment",
            ],
            f"System distinctions in 3.5k hinge on {contrast}.",
            "Students invent false equivalences between unlike systems.",
            topic=T_VIA, outcome_code="3.5k",
            skill_tested=f"Contrasting {a} with {b}",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    for i, topic_issue in enumerate([
        "pandemic border closures lasting after risk falls",
        "platform bans of political satire after riots",
        "anti-terror laws allowing secret evidence in immigration hearings",
        " austerity budgets closing rural clinics",
        "hate-speech prosecutions with vague definitions",
        " resource megaprojects approved over Indigenous objections without consultation",
        " emergency spy powers renewed by quiet orders-in-council",
        "racial profiling defended as efficient policing",
    ]):
        q.append(mc(
            f"Policy controversy: {topic_issue}. A viability-minded student should first identify",
            "which liberal principles are strained and which public objectives are claimed",
            [
                "only the font size on the statute",
                "whether Smith disliked tea",
                "missile counts unrelated to the policy",
            ],
            "3.9k/3.6k-style analysis begins by naming principles and claimed objectives before judging.",
            "Students jump to outrage without principle mapping.",
            topic=T_VIA, outcome_code="3.9k",
            skill_tested="Structuring viability analysis of contemporary policy",
            difficulty=_d(i), estimated_time_seconds=115,
        ))

    return q


def _citizenship() -> list:
    q: list = []

    # 4.4k worldviews
    worldviews = [
        (
            "A pacifist refuses combat roles citing sacred nonviolence while supporting civilian aid",
            "personal worldview shaping how ideology translates into citizenship practice",
        ),
        (
            "A techno-optimist trusts markets and gadgets to fix scarcity before politics must",
            "worldview assumptions steering ideological and civic priorities",
        ),
        (
            "A community elder frames duties to grandchildren as duties to land first",
            "collective worldview linking ideology, identity, and citizenship obligations",
        ),
        (
            "A skeptic distrusts all parties yet still votes as damage control",
            "worldview of suspicion coexisting with minimal civic participation",
        ),
    ]
    for i, (scene, ans) in enumerate(worldviews):
        q.append(mc(
            f"{scene}. This best illustrates",
            ans,
            [
                "that worldviews replace the need for any government",
                "that ideology is illegal in Canada",
                "that Cold War brinkmanship defines all voting",
            ],
            "Outcome 4.4k explores relationships among personal/collective worldviews and ideology.",
            "Students treat worldview as irrelevant to citizenship.",
            topic=T_CIT, outcome_code="4.4k",
            skill_tested="Relating worldviews to ideology and citizenship",
            difficulty=_d(i), estimated_time_seconds=_t(i),
        ))

    # 4.5k ideologies shape citizenship
    shape = [
        ("liberal rights culture", "citizens petition courts when ministries overreach"),
        ("collectivist neighbourhood norms", "residents accept rotating duties for shared gardens"),
        ("religious ideological commitments", "voters prioritize conscience exemptions in party platforms"),
        ("environmentalist ideology", "citizens boycott high-emission firms and lobby for carbon caps"),
        ("nationalist ideology", "citizenship rituals emphasize military remembrance and language purity"),
        ("social-democratic ideology", "activists campaign for expanded public services as civic duty"),
    ]
    for i, (ideo, practice) in enumerate(shape):
        q.append(mc(
            f"When {practice}, the example most clearly shows",
            f"how {ideo} can shape individual or collective citizenship action",
            [
                "that citizenship never intersects ideology",
                "that only fascism produces petitions",
                "that markets forbid volunteering",
            ],
            "Outcome 4.5k explores how ideologies shape citizenship.",
            "Students describe the action without naming ideological shaping.",
            topic=T_CIT, outcome_code="4.5k",
            skill_tested="Explaining ideological shaping of citizenship",
            difficulty=_d(i + 1), estimated_time_seconds=95,
        ))

    # 4.6k democratic roles
    roles = [
        ("respect for law and order", "obeying court injunctions while still planning a lawful appeal"),
        ("dissent", "publishing criticism of cabinet policy without incitement to violence"),
        ("civility", "debating opponents without dehumanizing rhetoric in public forums"),
        ("political participation", "canvassing, voting, and attending riding associations"),
        ("citizen advocacy", "organizing a coalition to lobby for accessible transit"),
    ]
    for i, (role, scene) in enumerate(roles):
        wrong = [r for r, _ in roles if r != role][:3]
        q.append(mc(
            f"{scene.capitalize()}. This civic behaviour best exemplifies",
            role,
            wrong,
            "Outcome 4.6k analyzes perspectives on rights, roles, and responsibilities including these practices.",
            f"Students mis-tag the scene as a different role than {role}.",
            topic=T_CIT, outcome_code="4.6k",
            skill_tested=f"Identifying civic role: {role}",
            difficulty=_d(i), estimated_time_seconds=90,
        ))

    # 4.7k conflict contexts
    conflict = [
        ("humanitarian crises", "volunteers and states respond to famine while debating sovereignty and aid conditions"),
        ("civil rights movements", "campaigners challenge discriminatory laws through marches and litigation"),
        ("antiwar movements", "protesters oppose military deployments they view as unjust"),
        ("McCarthyism", "loyalty scare tactics chill dissent under anti-communist suspicion"),
        ("pro-democracy movements", "crowds demand elections and rights against authoritarian rulers"),
        ("contemporary examples", "digital organizers livestream election fraud allegations and rights abuses"),
    ]
    for i, (label, scene) in enumerate(conflict):
        q.append(mc(
            f"{scene.capitalize()}. The conflict-context label from 4.7k is",
            label,
            [x for x, _ in conflict if x != label][:3],
            "Outcome 4.7k examines citizenship roles during conflict periods and movements.",
            f"Students confuse {label} with a different conflict category.",
            topic=T_CIT, outcome_code="4.7k",
            skill_tested=f"Identifying conflict context: {label}",
            difficulty=_d(i + 2), estimated_time_seconds=100,
        ))
        q.append(mc(
            f"During episodes of {label}, liberal citizenship analysis should especially consider",
            "how rights, dissent, and security claims collide under pressure",
            [
                "only commodity futures ticker symbols",
                "only pin-factory productivity jokes",
                "only whether Smith preferred oatmeal",
            ],
            "Conflict contexts stress-test rights and responsibilities (4.7k).",
            "Students ignore the rights–security tension.",
            topic=T_CIT, outcome_code="4.7k",
            skill_tested=f"Analyzing citizenship under {label}",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # 4.8k evaluate ideology shaping responses
    evaluate_cit = [
        (
            "A politician refuses refugee aid citing ideological purity about closed borders",
            "ideology can harden responses in ways that require ethical and empirical scrutiny",
        ),
        (
            "Aid groups bracket party ideology to deliver water in a disaster zone",
            "some civic responses deliberately mute ideology to prioritize humanitarian need",
        ),
        (
            "Voters back climate rules because ecological ideology shapes their duty narrative",
            "ideology can productively organize collective responses to shared risks",
        ),
        (
            "Partisans deny plague data that contradict their media worldview",
            "ideological identity can obstruct responsible citizenship when evidence is sidelined",
        ),
    ]
    for i, (scene, ans) in enumerate(evaluate_cit):
        q.append(mc(
            f"{scene}. Evaluation under 4.8k supports the claim that",
            ans,
            [
                "ideology must always dictate identical answers worldwide",
                "citizenship ends when ideology begins",
                "only monarchs may hold ideologies",
            ],
            "Outcome 4.8k evaluates how far ideology should shape responses to contemporary issues.",
            "Students give absolutist answers without criteria.",
            topic=T_CIT, outcome_code="4.8k",
            skill_tested="Evaluating ideology’s role in civic responses",
            difficulty=_d(i), estimated_time_seconds=120,
        ))

    # 4.9k / 4.10k strategies and opportunities
    strategies = [
        ("forming a nonpartisan fact-check coop before municipal votes", "collective leadership strategy informing local democratic choice"),
        ("student climate briefs presented to a school board", "youth leadership addressing a public issue with evidence"),
        ("sister-city fundraising after an overseas earthquake", "collective action linking local citizenship to global need"),
        ("a workplace petition for safer temp-worker rules", "individual and collective advocacy inside economic life"),
        ("translating ballot information into additional languages", "inclusion strategy expanding meaningful participation"),
        ("citizen science water sampling shared with Indigenous guardians", "collaborative leadership across knowledge traditions"),
    ]
    for i, (scene, ans) in enumerate(strategies):
        q.append(mc(
            f"{scene.capitalize()}. This example best fits",
            ans,
            [
                "nuclear brinkmanship doctrine",
                "rejection of all civic action",
                "proof rights documents forbid volunteering",
            ],
            "Outcomes 4.9k and 4.10k emphasize strategies and opportunities for active, responsible citizenship.",
            "Students dismiss local actions as unrelated to ideology/citizenship study.",
            topic=T_CIT, outcome_code="4.9k" if i % 2 == 0 else "4.10k",
            skill_tested="Recognizing active citizenship strategies",
            difficulty=_d(i + 1), estimated_time_seconds=90,
        ))

    # Extra citizenship scenarios
    extras = [
        ("4.6k", "Blocking an ambulance during a protest would most clearly fail which paired civic expectation?",
         "civility and respect for urgent lawful protections of persons",
         ["paying bus fare", "watching hockey", "planting marigolds"],
         "Dissent in liberal democracy is bounded by responsibilities not to destroy others’ basic safety.",
         "Students treat any protest harm as automatically protected dissent."),
        ("4.6k", "Writing an op-ed criticizing a premier without threats primarily exercises",
         "dissent within democratic citizenship",
         ["command economy quota setting", "fascist Gleichschaltung", "nonalignment summit hosting"],
         "Peaceful criticism is core dissent/participation space.",
         "Students equate criticism with extremism."),
        ("4.7k", "Hollywood blacklists under anti-communist panic are studied as aspects of",
         "McCarthyism chilling civic and cultural participation",
         ["welfare capitalism’s clinic model", "Adam Smith’s customs duties", "direct democracy monthly tax votes"],
         "McCarthyism is a named 4.7k conflict context.",
         "Students misplace blacklists under economic system labels."),
        ("4.5k", "A voter guided chiefly by encyclicals on social justice shows",
         "religious ideological commitments shaping citizenship choices",
         ["random coin-flip citizenship with no beliefs", "inevitable fascism", "abolition of voting"],
         "Ideologies, including religiously informed ones, shape civic priorities (4.5k).",
         "Students deny religion can interact with citizenship ideology."),
        ("4.8k", "The claim ‘my ideology answers every disaster identically’ is weakest because",
         "contemporary issues often require weighing principles against specific evidence and harms",
         ["ideologies never influence people", "disasters outlaw thinking", "only GDP may guide ethics"],
         "4.8k expects evaluative judgment, not reflex dogma.",
         "Students confuse evaluation with abandoning all principles."),
        ("4.10k", "Joining a community league to improve park safety is best seen as",
         "an opportunity for active local citizenship",
         ["treason against liberalism", "a command economy five-year plan", "brinkmanship"],
         "4.10k highlights everyday opportunities for responsible action.",
         "Students only recognize citizenship in federal elections."),
    ]
    for i, (oc, stem, ans, dist, expl, mist) in enumerate(extras):
        q.append(mc(
            stem, ans, dist, expl, mist,
            topic=T_CIT, outcome_code=oc,
            skill_tested="Applying citizenship outcomes to cases",
            difficulty=_d(i + 2), estimated_time_seconds=100,
        ))

    q.append(nr(
        "A citizenship checklist names five democratic practices from outcome 4.6k: respect for law and order; "
        "dissent; civility; political participation; citizen advocacy. How many practices are named?",
        "5",
        "Count the five bracketed practices in the stem (4.6k).",
        "Students add protest/civil disobedience from 30-2 wording and overcount.",
        topic=T_CIT, outcome_code="4.6k",
        skill_tested="Counting democratic citizenship practices from a list",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "Conflict-context cards list: humanitarian crises; civil rights movements; antiwar movements; "
        "McCarthyism; pro-democracy movements; contemporary examples. How many cards are in the set?",
        "6",
        "Outcome 4.7k lists six conflict contexts in the stem enumeration.",
        "Students omit contemporary examples.",
        topic=T_CIT, outcome_code="4.7k",
        skill_tested="Counting conflict contexts from a supplied list",
        difficulty="Easy", estimated_time_seconds=40,
    ))

    # Pad citizenship with more original stems
    for i, action in enumerate([
        "hosting an all-candidates meeting at a library",
        "translating healthcare forms for newcomers",
        "monitoring a local poll desk as a scrutineer",
        "launching a petition on unsafe crosswalks",
        "writing MLAs about solitary confinement rules",
        "organizing interfaith meals after hate vandalism",
        " crowdfunding legal support for a wrongfully detained protester",
        "teaching seniors to spot deepfake political ads",
    ]):
        q.append(mc(
            f"A citizen is {action}. Relative to Social Studies 30-1 citizenship outcomes, this is best classified as",
            "active civic practice expressing rights, roles, or responsibilities in a democracy",
            [
                "abandonment of all civic duty",
                "automatic proof of extremism",
                "a command economy production quota",
            ],
            "4.6k/4.10k recognize varied lawful participatory and advocacy practices.",
            "Students only count voting as citizenship.",
            topic=T_CIT, outcome_code="4.10k",
            skill_tested="Classifying active citizenship actions",
            difficulty=_d(i), estimated_time_seconds=85,
        ))

    return q
