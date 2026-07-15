"""
Build an unbalanced ~450-item SOCIAL STUDIES 30-1 question pool.

Alberta PoS-aligned, diploma-style practice. Original wording only.
No released diploma content. NR only when objectively auto-gradable.
"""

from __future__ import annotations

import itertools
import random
from typing import Callable

from .helpers import mc, nr

T_ID = "Ideology and Identity"
T_ORIG = "Origins of Liberalism"
T_RES = "Resistance to Liberalism"
T_VIA = "The Viability of Contemporary Liberalism"
T_CIT = "Citizenship and Ideology"

DIFFS = ("Easy", "Medium", "Hard")


def _d(i: int) -> str:
    return DIFFS[i % 3]


def _t(easy: int, mid: int, hard: int, i: int) -> int:
    return [easy, mid, hard][i % 3]


# ---------------------------------------------------------------------------
# Related Issue 1 — Ideology and Identity
# ---------------------------------------------------------------------------

def _ri1() -> list:
    q: list = []

    factors = [
        ("language policy that privileges one official tongue in schooling", "language as a factor shaping collective belief"),
        ("a livestream influencer framing national pride as personal virtue", "media as a factor shaping beliefs and values"),
        ("seasonal hunting practices tying belonging to a shared territory", "relationship to land as a factor shaping identity"),
        ("faith-based charity networks organizing neighbourhood mutual aid", "religion and spirituality shaping collective values"),
        ("a youth movement describing progress as inevitable technological uplift", "ideological progressivism shaping collective hope"),
        ("gendered expectations about who speaks in community councils", "gender as a factor influencing beliefs about social roles"),
        ("documentary footage emphasizing environmental stewardship of rivers", "environment as a factor shaping collective values"),
        ("heritage festivals celebrating immigrant languages in city plazas", "culture as a factor influencing individual and collective identity"),
    ]
    for i, (scene, skill) in enumerate(factors):
        q.append(mc(
            f"A case study describes {scene}. Within Social Studies 30-1, this example best illustrates",
            "a factor that may influence individual and collective beliefs and values",
            [
                "proof that ideology never interacts with identity",
                "evidence that governments must abolish private property",
                "a Cold War deterrence doctrine unrelated to identity",
            ],
            "Outcome 1.3k identifies culture, language, media, land, environment, gender, religion, spirituality, and ideology as identity influences.",
            "Students may jump to policy prescriptions instead of classifying the identity factor.",
            topic=T_ID, outcome_code="1.3k", skill_tested=skill,
            difficulty=_d(i), estimated_time_seconds=_t(70, 90, 110, i),
        ))

    indiv_collect = [
        (
            "A co-op housing charter requires members to pool maintenance labour and share surplus food.",
            "a contemporary expression of collectivist norms around cooperation and shared responsibility",
            "classical liberal insistence on unregulated self-interest alone",
            "Students misread any cooperation as fascism or as classical liberalism.",
        ),
        (
            "A start-up founder argues that personal patents and stock options best reward innovation.",
            "a contemporary expression of individualism emphasizing self-interest and private property",
            "collectivist insistence on public ownership of productive assets",
            "Students confuse entrepreneurship rhetoric with command socialism.",
        ),
        (
            "A wartime poster urges citizens to accept rationing so no household gains unfair surplus.",
            "collectivist emphasis on collective interest and economic equality under strain",
            "laissez-faire rejection of any wartime coordination",
            "Students treat all wartime posters as fascist propaganda by default.",
        ),
        (
            "A city bylaw protects a homeowner’s title even when neighbours prefer a denser rezoning plan.",
            "individualist priority for private property within a rules-based order",
            "Aboriginal collective thought rejecting all land titles",
            "Students assume property protections cannot coexist with democratic zoning debates.",
        ),
        (
            "Employees vote to create a workplace fund that covers medical gaps for all staff equally.",
            "collectivist practice stressing collective responsibility and economic equality",
            "neo-conservative preference for cutting all social programs",
            "Students equate any workplace benefit with Soviet communism.",
        ),
        (
            "An athlete markets a personal brand while refusing team revenue sharing beyond contract terms.",
            "individualist framing of self-interest and economic freedom",
            "Marxist call to abolish class distinctions through public property",
            "Students overread market behaviour as an entire ideology’s rejection.",
        ),
    ]
    for i, (stem, ans, distract, mistake) in enumerate(indiv_collect):
        q.append(mc(
            f"{stem} This scenario most clearly shows",
            ans,
            [
                distract,
                "that ideology cannot shape daily economic choices",
                "that illiberal emergencies must suspend all civic roles",
            ],
            "Outcome 1.4k asks students to examine historic and contemporary expressions of individualism and collectivism.",
            mistake,
            topic=T_ID, outcome_code="1.4k",
            skill_tested="Classifying individualism and collectivism in contemporary cases",
            difficulty=_d(i + 1), estimated_time_seconds=_t(80, 100, 120, i),
        ))

    characteristics = [
        ("claims that humans are naturally competitive and need limited government restraint", "beliefs about human nature as a characteristic of ideology"),
        ("narrates the past as a story of gradual rights expansion for citizens", "interpretations of history as a characteristic of ideology"),
        ("proposes a future where class conflict disappears through planned production", "visions for the future as a characteristic of ideology"),
        ("describes society as a hierarchy of organic roles rather than equal citizen contracts", "beliefs about the structure of society as a characteristic of ideology"),
        ("treats industrial growth as the main storyline of national success", "interpretations of history linked to ideological themes of progress"),
        ("assumes people flourish mainly through voluntary market exchange", "beliefs about human nature underpinning market-centred ideology"),
    ]
    for i, (claim, skill) in enumerate(characteristics):
        q.append(mc(
            f"An editorial {claim}. As used in the program of studies, this excerpt chiefly reveals",
            "a characteristic component of an ideology",
            [
                "a geographic skill unrelated to ideology",
                "proof that citizenship duties never change",
                "a numerical model of GDP alone",
            ],
            "Outcome 1.5k frames ideology through interpretations of history, beliefs about human nature and social structure, and visions of the future.",
            "Students often reduce ideology to party labels instead of these characteristics.",
            topic=T_ID, outcome_code="1.5k", skill_tested=skill,
            difficulty=_d(i), estimated_time_seconds=_t(75, 95, 115, i),
        ))

    themes = [
        ("nation", "a pamphlet defining belonging by shared ancestry and homeland myths"),
        ("class", "a manifesto arguing history is driven by owners versus workers"),
        ("relationship to land", "a statement that sacred territory, not markets, should set resource rules"),
        ("environment", "a platform ranking ecological limits above consumer choice"),
        ("religion", "a movement insisting public law must mirror scriptural ethics"),
        ("progressivism", "a speech claiming continuous reform is history’s moral direction"),
    ]
    for i, (theme, scene) in enumerate(themes):
        q.append(mc(
            f"Consider {scene}. The ideological theme most clearly highlighted is",
            theme,
            [t for t, _ in themes if t != theme][:3],
            f"Outcome 1.6k lists themes of ideologies including {theme}.",
            "Students interchange nation and class themes when rhetoric mentions ‘the people.’",
            topic=T_ID, outcome_code="1.6k",
            skill_tested=f"Identifying the ideological theme of {theme}",
            difficulty=_d(i + 2), estimated_time_seconds=_t(70, 90, 110, i),
        ))

    lib_principles = [
        ("individual rights and freedoms", "A court blocks a ministry from jailing critics who publish peaceful dissent."),
        ("self-interest", "A shopkeeper chooses inventory based on expected personal profit, not a production quota."),
        ("competition", "Two airlines lower fares to attract the same corridor of travellers."),
        ("economic freedom", "Citizens may open bakeries without joining a state-mandated guild."),
        ("rule of law", "A powerful official faces the same traffic penalties as any other driver."),
        ("private property", "Title documents let a family decide whether to sell farmland on the open market."),
    ]
    for i, (principle, scene) in enumerate(lib_principles):
        wrong = [p for p, _ in lib_principles if p != principle][:3]
        q.append(mc(
            f"{scene} This example best illustrates which principle of liberalism tied to individualism?",
            principle,
            wrong,
            "Outcome 1.7k lists individual rights and freedoms, self-interest, competition, economic freedom, rule of law, and private property.",
            "Students often swap rule of law with economic freedom when courts and markets both appear.",
            topic=T_ID, outcome_code="1.7k",
            skill_tested=f"Linking scenarios to the liberal principle of {principle}",
            difficulty=_d(i), estimated_time_seconds=_t(70, 95, 120, i),
        ))

    coll_principles = [
        ("collective responsibility", "Neighbours accept a rotating duty schedule so elders’ snow is cleared even in tough weeks."),
        ("collective interest", "A fishery council sets catch limits so the stock survives for the whole community."),
        ("cooperation", "Rival farming families jointly fund a shared irrigation canal."),
        ("economic equality", "A policy narrows after-tax income gaps through progressive transfers."),
        ("adherence to collective norms", "Members face social penalty if they violate the co-op’s work-share rules."),
        ("public property", "A shoreline park is owned by the municipality rather than sold to resorts."),
    ]
    for i, (principle, scene) in enumerate(coll_principles):
        wrong = [p for p, _ in coll_principles if p != principle][:3]
        q.append(mc(
            f"{scene} This practice most directly reflects which principle of collectivism?",
            principle,
            wrong,
            "Outcome 1.8k lists collective responsibility, collective interest, cooperation, economic equality, adherence to collective norms, and public property.",
            "Students confuse collective interest (shared benefit) with economic equality (narrowed material gaps).",
            topic=T_ID, outcome_code="1.8k",
            skill_tested=f"Identifying collectivist principle: {principle}",
            difficulty=_d(i + 1), estimated_time_seconds=_t(70, 95, 120, i),
        ))

    common_good = [
        (
            "A pandemic curfew limits night gatherings yet leaves grocery access intact.",
            "tension between individual freedom of movement and collective public-health goals",
        ),
        (
            "Mandatory bike-helmet laws reduce injury costs borne by the health system.",
            "balancing personal lifestyle choice against a broader social interest in lower harm",
        ),
        (
            "A city expands shelters using tax revenue some residents wanted for tax cuts.",
            "trade-off between individual economic preferences and collective welfare aims",
        ),
        (
            "Whistle-blower protections shield employees who report toxic dumping.",
            "using individual rights mechanisms to advance a wider environmental common good",
        ),
    ]
    for i, (scene, ans) in enumerate(common_good):
        q.append(mc(
            f"{scene} Analysis of this case for Social Studies 30-1 should focus on",
            ans,
            [
                "whether Adam Smith invented modern surplus value theory",
                "whether fascism uniquely invented income tax",
                "whether maps alone determine citizenship duties",
            ],
            "Outcome 1.9k targets the dynamic between individualism and the common good in contemporary societies.",
            "Students may moralize instead of naming the individualism–common good tension.",
            topic=T_ID, outcome_code="1.9k",
            skill_tested="Analyzing individualism versus common good tensions",
            difficulty=_d(i + 2), estimated_time_seconds=_t(90, 110, 130, i),
        ))

    identity_eval = [
        (
            "A voter who changes parties after reading competing platforms while keeping family cultural traditions",
            "identity may draw on ideology without being wholly determined by one doctrine",
        ),
        (
            "A recruit who replaces all friendships after joining a movement that forbids outside media",
            "ideology can dominate identity when exclusive commitments overwrite prior affiliations",
        ),
        (
            "A bilingual graduate who supports free enterprise yet marches for Indigenous language funding",
            "people can hold layered identities that mix liberal economics with collective cultural goals",
        ),
        (
            "A citizen who treats a leader’s tweets as the only acceptable identity script",
            "uncritical ideological capture can shrink the space for independent identity formation",
        ),
    ]
    for i, (scene, ans) in enumerate(identity_eval):
        q.append(mc(
            f"Consider {scene}. The strongest 30-1 evaluation is that",
            ans,
            [
                "ideology never influences personal identity in democracies",
                "only class themes can shape identity legally",
                "identity formation ends when ballots are cast",
            ],
            "Outcome 1.10k asks students to evaluate how far personal identity should be shaped by ideologies.",
            "Students answer with absolutes (‘always’/‘never’) instead of nuanced evaluation.",
            topic=T_ID, outcome_code="1.10k",
            skill_tested="Evaluating ideology’s influence on personal identity",
            difficulty=_d(i), estimated_time_seconds=_t(100, 120, 140, i),
        ))

    # Extra RI1 scenario hybrids for pool depth
    extra_ri1 = [
        ("1.5k", "A podcast claims ‘history proves winners deserved conquest.’ Which ideology characteristic is most on display?",
         "an interpretation of history used to justify present arrangements",
         ["a precise GDP accounting method", "a Cold War deterrence timetable", "a zoning bylaw technical annex"],
         "Ideologies organize history into moral narratives that legitimize preferred futures.",
         "Students treat every history claim as neutral chronology."),
        ("1.7k", "Which arrangement most clearly expresses economic freedom within classical liberal logic?",
         "households choose occupations and may save or invest with limited state direction",
         ["the state assigns all jobs from a five-year plan", "party cadres set farm production quotas alone", "courts abolish all contracts as bourgeois relics"],
         "Economic freedom centres voluntary economic choices rather than comprehensive state assignment of labour.",
         "Students confuse economic freedom with the absence of any regulation whatever."),
        ("1.8k", "Public ownership of an urban transit network is closest to which collectivist principle?",
         "public property",
         ["self-interest", "private property", "economic freedom as laissez-faire"],
         "Public property places assets under communal or state ownership rather than private title.",
         "Students mislabel transit as private property because riders pay fares."),
        ("1.3k", "A virtual reality game teaches players that national destiny equals military expansion. The influential factor highlighted is chiefly",
         "media shaping beliefs and values about nationhood",
         ["random genetic mutation alone", "currency board rules only", "mineral assay techniques"],
         "Media messages can transmit ideological themes that shape identity and belief.",
         "Students overlook media as an identity factor listed in 1.3k."),
        ("1.9k", "A privacy bill lets people refuse government health apps while funding anonymous outbreak data systems. The case best probes",
         "how societies negotiate individual liberty and common health goods together",
         ["whether Montesquieu invented surplus value", "whether nonalignment ends all alliances", "whether mixed economies forbid courts"],
         "Contemporary governance often balances rights against shared objectives.",
         "Students pick a historical trivia distractor instead of the individuality–common good frame."),
        ("1.4k", "Workers in a nineteenth-century mill town share a community fund for burial costs while factory owners lobby against labour laws. The contrast demonstrates",
         "overlapping historic expressions of collectivism among workers and individualism among owners",
         ["that fascism already dominated all mill towns", "that liberalism forbids charity", "that ideology appears only after 1945"],
         "Historic settings often show individualism and collectivism operating among different groups at once.",
         "Students assume only one ideological expression can exist in a period."),
        ("1.6k", "If a party platform places ‘sacred territory reclaimed from developers’ at its centre, the strongest thematic label is",
         "relationship to land",
         ["competition among airlines", "rule of law traffic fines", "stock option incentives"],
         "Themes include relationship to land when territory and belonging structure the ideology.",
         "Students default to class even when land rhetoric dominates."),
        ("1.10k", "The claim ‘you are your ideology or you are nothing’ is most vulnerable to critique that",
         "people typically hold plural identities that ideology alone should not monopolize",
         ["ideology has never motivated citizens", "courts have banned all ideologies", "GDP makes ideology illegal"],
         "1.10k invites evaluation of how far ideology should shape identity, not totalizing claims.",
         "Students accept slogan absolutism as if it were analytic evaluation."),
    ]
    for i, (oc, stem, ans, dist, expl, mist) in enumerate(extra_ri1):
        q.append(mc(
            stem, ans, dist, expl, mist,
            topic=T_ID, outcome_code=oc,
            skill_tested="Applying ideology concepts to novel scenarios",
            difficulty=_d(i + 1), estimated_time_seconds=_t(80, 100, 125, i),
        ))

    # NR: count principles from a provided list (objectively gradable)
    q.append(nr(
        "A study sheet lists six principles of liberalism associated with individualism: "
        "individual rights and freedoms; self-interest; competition; economic freedom; "
        "rule of law; private property. How many principles are listed?",
        "6",
        "The program of studies enumerates six liberal principles under individualism (1.7k).",
        "Students add collectivist principles and answer 12, or forget one and answer 5.",
        topic=T_ID, outcome_code="1.7k",
        skill_tested="Counting enumerated liberal principles from given text",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "A table of collectivist principles names: collective responsibility; collective interest; "
        "cooperation; economic equality; adherence to collective norms; public property. "
        "How many collectivist principles appear in the table?",
        "6",
        "Outcome 1.8k lists six collectivist principles.",
        "Students double-count ‘collective’ phrases as separate extras.",
        topic=T_ID, outcome_code="1.8k",
        skill_tested="Counting collectivist principles from a supplied list",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "Identity-factor flashcards name exactly these influences: culture; language; media; "
        "relationship to land; environment; gender; religion; spirituality; ideology. "
        "How many distinct factors are on the cards?",
        "9",
        "Outcome 1.3k lists nine bracketed factors.",
        "Students merge religion/spirituality and undercount.",
        topic=T_ID, outcome_code="1.3k",
        skill_tested="Counting identity factors listed in a stem",
        difficulty="Easy", estimated_time_seconds=50,
    ))

    return q


# ---------------------------------------------------------------------------
# Related Issue 2 origins — classical to modern liberalism
# ---------------------------------------------------------------------------

def _ri2a() -> list:
    q: list = []

    aboriginal = [
        (
            "Haudenosaunee consensus traditions that European observers compared with balanced government",
            "Aboriginal political practices that some scholars link to liberal ideas of balanced authority",
        ),
        (
            "Indigenous diplomatic protocols stressing mutual obligation rather than absolute monarchy",
            "Aboriginal contributions that complicate the story of liberalism as solely European",
        ),
        (
            "Community decision models that settlers selectively praised while still dispossessing land",
            "how Aboriginal governance ideas could inform liberal thought even amid imposition and harm",
        ),
    ]
    for i, (scene, ans) in enumerate(aboriginal):
        q.append(mc(
            f"Historians discuss {scene}. For outcome 2.4k, the most accurate takeaway is",
            ans,
            [
                "that Aboriginal societies never had political thought",
                "that fascism originated in Indigenous councils",
                "that liberalism forbids studying Aboriginal history",
            ],
            "Outcome 2.4k asks students to explore Aboriginal contributions to the development of liberalism without erasing later imposition.",
            "Students may treat recognition of contribution as denial of colonial harm, or vice versa.",
            topic=T_ORIG, outcome_code="2.4k",
            skill_tested="Explaining Aboriginal contributions related to liberal development",
            difficulty=_d(i), estimated_time_seconds=_t(90, 110, 130, i),
        ))

    thinkers = [
        ("John Locke", "government legitimacy rests on consent and protection of natural rights to life, liberty, and property",
         "abolishing private property through a dictatorship of the proletariat"),
        ("Montesquieu", "political liberty is safer when legislative, executive, and judicial powers are separated",
         "uniting all power in a single revolutionary party secretariat"),
        ("Adam Smith", "markets guided by individual pursuit of gain can coordinate production better than heavy state direction",
         "the labour theory of surplus value requiring class revolution"),
        ("John Stuart Mill", "individual liberty should be maximized unless harm to others justifies limits, including space for dissent",
         "racial hierarchy as the organising principle of the state"),
    ]
    for i, (name, idea, anti) in enumerate(thinkers):
        q.append(mc(
            f"A quotation most consistent with {name}’s classical liberal contribution would emphasize that",
            idea,
            [
                anti,
                "the Führer principle replaces consent",
                "command quotas replace all contracts permanently",
            ],
            f"Outcome 2.5k links classical liberal thought to thinkers including {name}.",
            f"Students attribute collectivist or fascist doctrines to {name}.",
            topic=T_ORIG, outcome_code="2.5k",
            skill_tested=f"Matching classical liberal ideas to {name}",
            difficulty=_d(i + 1), estimated_time_seconds=_t(85, 105, 125, i),
        ))
        q.append(mc(
            f"Which policy direction would {name} be least likely to endorse as a classical liberal thinker?",
            anti if "abolishing" in anti or "uniting" in anti or "racial" in anti or "labour theory" in anti else anti,
            [
                idea,
                "protecting contracts under known laws",
                "limiting arbitrary royal power over subjects",
            ],
            f"Classical liberals such as {name} critiqued arbitrary power and advanced rights, markets, or separated powers—not totalitarian or revolutionary collectivist programs.",
            "Students reverse classical liberalism with later illiberal or Marxist systems.",
            topic=T_ORIG, outcome_code="2.5k",
            skill_tested=f"Distinguishing {name} from anti-liberal programs",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    impacts_19c = [
        ("laissez-faire capitalism", "factory owners resist safety rules as interference with market self-regulation",
         "the state owns all factories and sets output quotas"),
        ("industrialization", "steam-powered mills concentrate workers in rapidly growing urban centres",
         "monasteries replace factories as the main production sites"),
        ("class system", "a visible divide grows between industrial capitalists and wage labourers",
         "class labels are abolished by fascism’s corporative myth alone"),
        ("limited government", "parliament’s role is framed as protecting property and order more than running industry",
         "the politburo directs every enterprise daily"),
    ]
    for i, (concept, scene, wrong) in enumerate(impacts_19c):
        q.append(mc(
            f"{scene.capitalize()}. This development is best labelled as connected to",
            concept,
            [
                wrong,
                "détente between superpowers after 1970",
                "Charter section testing in Canadian courts",
            ],
            "Outcome 2.6k examines laissez-faire capitalism, industrialization, class system, and limited government as impacts of classical liberal thought.",
            f"Students misapply Cold War or contemporary Canadian labels to nineteenth-century {concept}.",
            topic=T_ORIG, outcome_code="2.6k",
            skill_tested=f"Identifying nineteenth-century impacts: {concept}",
            difficulty=_d(i), estimated_time_seconds=_t(80, 100, 120, i),
        ))

    responses = [
        ("classic conservatism", "defends inherited traditions and cautious change against rapid liberal remaking of society",
         "abolishes religion and monarchy overnight in the name of pure reason"),
        ("Marxism", "analyzes capitalism as class exploitation and looks toward revolutionary transformation",
         "celebrates laissez-faire as the end of history"),
        ("socialism", "seeks greater social ownership or control to remedy inequality produced under industrial capitalism",
         "insists inequality is always morally ideal"),
        ("welfare capitalism", "accepts markets but adds employer or state supports to stabilize workers’ lives",
         "rejects any wages, markets, or firms whatsoever"),
    ]
    for i, (label, desc, anti) in enumerate(responses):
        q.append(mc(
            f"An ideology that {desc} is best identified as",
            label,
            [x for x, _, _ in responses if x != label][:3],
            "Outcome 2.7k lists classic conservatism, Marxism, socialism, and welfare capitalism as responses to classical liberalism.",
            f"Students confuse {label} with unrelated twentieth-century fascism or with classical liberalism itself.",
            topic=T_ORIG, outcome_code="2.7k",
            skill_tested=f"Identifying {label} as a response to classical liberalism",
            difficulty=_d(i + 2), estimated_time_seconds=_t(85, 105, 125, i),
        ))
        q.append(mc(
            f"Which statement conflicts with {label} as a nineteenth/early response ideology?",
            anti,
            [
                desc,
                "It emerged in dialogue with industrial capitalist change.",
                "It offered an alternative reading of liberal industrial society.",
            ],
            f"{label} is defined against aspects of classical liberal industrial society; the conflicting statement denies that orientation.",
            "Students pick a compatible description as if it were the conflict.",
            topic=T_ORIG, outcome_code="2.7k",
            skill_tested=f"Eliminating statements incompatible with {label}",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    modern_lib = [
        ("labour standards and unions", "laws on hours and collective bargaining respond to industrial harm under classical liberal markets"),
        ("universal suffrage", "voting rights expand beyond propertied men toward broader citizen inclusion"),
        ("welfare state", "public pensions and unemployment supports modify pure market outcomes"),
        ("protection of human rights", "statutory and constitutional rights constrain what majorities and markets may do to persons"),
        ("feminism", "movements challenge legal and economic barriers that limited women’s liberal citizenship in practice"),
    ]
    for i, (feature, gloss) in enumerate(modern_lib):
        q.append(mc(
            f"Modern liberalism’s evolution is illustrated when societies adopt {feature} because",
            gloss,
            [
                "classical liberalism already mandated one-party states",
                "fascism required feminist labour codes",
                "command economies invented universal shareholder dividends",
            ],
            "Outcome 2.8k frames modern liberalism as responding to classical liberalism through labour standards, suffrage, welfare state, rights, and feminism.",
            "Students treat modern liberalism as identical to classical laissez-faire or as Marxism.",
            topic=T_ORIG, outcome_code="2.8k",
            skill_tested=f"Explaining modern liberal development: {feature}",
            difficulty=_d(i), estimated_time_seconds=_t(85, 105, 125, i),
        ))

    # Scenario comparison items
    comparisons = [
        (
            "2.5k",
            "Source A praises divided chambers checking a monarch; Source B praises unregulated mill owners dismissing injured workers. A student comparing classical liberal theory to practice should note",
            "Montesquieu-style constitutionalism can coexist historically with harsh laissez-faire labour conditions",
            ["classical liberalism forbade any factories", "Source B proves Locke demanded gulags", "divided powers require command pricing"],
            "Classical liberal ideas about power and markets do not erase the human costs of industrial laissez-faire.",
            "Students assume theory and factory practice must be identical in every respect.",
        ),
        (
            "2.6k",
            "Urban smog maps from the 1870s sit beside pamphlets celebrating ‘self-regulating industry.’ The pairing best supports the claim that",
            "industrialization under classical liberal economics produced social and environmental strains",
            ["détente caused nineteenth-century smog", "Charter litigation built the first mills", "fascism invented coal"],
            "2.6k links classical liberal economic impacts to industrial society’s pressures.",
            "Students drag twentieth-century labels into nineteenth-century evidence.",
        ),
        (
            "2.8k",
            "A progressive reformer supports factory inspectors yet defends competitive elections and private shops. This combination is closest to",
            "modern liberalism reforming classical liberalism without adopting revolutionary communism",
            ["Nazi racial state theory", "pure anarcho-primitivism", "Stalinist collectivization"],
            "Modern liberalism reforms markets and rights while remaining within liberal democratic horizons.",
            "Students label any reform as either ‘still classical laissez-faire’ or ‘communism.’",
        ),
        (
            "2.7k",
            "A landowner-politician warns that sudden universal manhood suffrage will destroy inherited order, preferring slow elite-guided change. The stance aligns most with",
            "classic conservatism responding to liberal democratic expansion",
            ["Marxist internationalism", "modern liberal feminism", "neo-conservatism of the 1980s only"],
            "Classic conservatism is a recognized response ideology emphasizing tradition and gradualism.",
            "Students confuse classic conservatism with twentieth-century neo-conservatism automatically.",
        ),
        (
            "2.5k",
            "An exam source credits ‘invisible hand’ coordination of bakers and butchers. The classical liberal thinker most directly evoked is",
            "Adam Smith",
            ["Joseph Stalin", "Benito Mussolini", "Mao Zedong"],
            "Adam Smith’s market imagery is central to classical liberal economic thought in 2.5k.",
            "Students attach market language to twentieth-century dictators.",
        ),
        (
            "2.8k",
            "Extending voting rights to women while keeping constitutional courts is best read as",
            "modern liberal expansion of political inclusion within a rights-based state",
            ["proof that liberalism rejected elections", "a fascist gender hierarchy program", "command economy labour assignment"],
            "Feminism and suffrage expansions are listed within modern liberalism’s evolution.",
            "Students treat suffrage reform as abandonment of liberalism.",
        ),
    ]
    for i, (oc, stem, ans, dist, expl, mist) in enumerate(comparisons):
        q.append(mc(
            stem, ans, dist, expl, mist,
            topic=T_ORIG, outcome_code=oc,
            skill_tested="Interpreting sources on liberal evolution",
            difficulty=_d(i + 1), estimated_time_seconds=_t(100, 120, 140, i),
        ))

    # More thinker/application stems
    for i, decade in enumerate([1830, 1848, 1867, 1871, 1884, 1890]):
        q.append(mc(
            f"A novel set around {decade} shows parliament debating whether to shorten children’s mill hours. "
            f"Within 30-1, the debate is best situated as",
            "pressure on classical liberal limited government arising from industrial society",
            [
                "a Cuban Missile Crisis brinkmanship exercise",
                "a Charter section 1 Oakes test rehearsal",
                "a nonalignment conference between superpowers",
            ],
            "Labour regulation debates mark the contested edge of classical liberal economic freedom in industrializing societies.",
            "Students misplace nineteenth-century labour politics into Cold War or Canadian Charter frames.",
            topic=T_ORIG, outcome_code="2.6k",
            skill_tested="Situating industrial reform debates historically",
            difficulty=_d(i), estimated_time_seconds=95,
        ))

    union_items = [
        "craft workers organize against wage cuts after a mechanization wave",
        "a strike fund pools dues to support members locked out by owners",
        "legislators argue for a minimum age before children may enter mines",
        "reformers publish morbidity tables from textile districts",
        "a party platform links ‘social insurance’ to stabilizing market society",
        "suffragists connect political voice to factory women lacking legal status",
    ]
    for i, scene in enumerate(union_items):
        q.append(mc(
            f"When {scene}, modern liberal evolution is most clearly suggested by movement toward",
            "institutional reforms that blunt classical laissez-faire extremes while keeping liberal political frameworks",
            [
                "immediate abolition of elections under a racial state",
                "permanent wartime martial law as the normal constitution",
                "rejection of any concept of rights or citizenship",
            ],
            "Modern liberalism answers industrial harms through unions, standards, welfare tools, rights, and inclusion.",
            "Students equate reform with totalitarian replacement of liberalism.",
            topic=T_ORIG, outcome_code="2.8k",
            skill_tested="Recognizing modern liberal reform trajectories",
            difficulty=_d(i + 2), estimated_time_seconds=100,
        ))

    # NR objectively from tables in stem
    q.append(nr(
        "A timeline card lists four classical liberal thinkers named in outcome 2.5k: "
        "John Locke; Montesquieu; Adam Smith; John Stuart Mill. How many thinkers are named?",
        "4",
        "The PoS brackets four thinkers for classical liberal thought.",
        "Students add Marx or Keynes and overcount.",
        topic=T_ORIG, outcome_code="2.5k",
        skill_tested="Counting named classical liberal thinkers from a list",
        difficulty="Easy", estimated_time_seconds=40,
    ))
    q.append(nr(
        "A review chart shows share of children under 12 among mill workers in one district: "
        "1820 = 28%; 1840 = 21%; 1860 = 12%; 1880 = 6%. What percentage is shown for 1860?",
        "12",
        "Read the 1860 value directly from the supplied chart data.",
        "Students average all years or pick 1840’s 21.",
        topic=T_ORIG, outcome_code="2.6k",
        skill_tested="Reading a percentage from provided industrial data",
        difficulty="Easy", estimated_time_seconds=50,
    ))
    q.append(nr(
        "Factory inspector reports in a workbook table list annual recorded limb injuries: "
        "Year 1: 40; Year 2: 35; Year 3: 30; Year 4: 25. What is the injury count for Year 3?",
        "30",
        "The stem states Year 3 = 30.",
        "Students compute the mean (32.5) instead of reading Year 3.",
        topic=T_ORIG, outcome_code="2.6k",
        skill_tested="Extracting a table value from industrial reform context",
        difficulty="Easy", estimated_time_seconds=45,
    ))
    q.append(nr(
        "A reform ledger lists five modern liberal response areas from outcome 2.8k: "
        "labour standards and unions; universal suffrage; welfare state; protection of human rights; feminism. "
        "How many areas are listed?",
        "5",
        "Outcome 2.8k enumerates five bracketed developments.",
        "Students omit feminism or add Marxism.",
        topic=T_ORIG, outcome_code="2.8k",
        skill_tested="Counting modern liberal developments from a given list",
        difficulty="Easy", estimated_time_seconds=40,
    ))

    # Additional MC to deepen pool
    extras = [
        ("2.5k", "Separation of powers is primarily associated in 30-1 classical liberalism with",
         "Montesquieu", ["Joseph Stalin", "Benito Mussolini", "Leonid Brezhnev"],
         "Montesquieu’s spirit of the laws tradition emphasizes divided powers.",
         "Students confuse separation of powers with twentieth-century dictators."),
        ("2.5k", "Consent of the governed and natural rights rhetoric in classical liberalism most closely tracks",
         "John Locke", ["Adolf Hitler", "Vladimir Lenin", " Augusto Pinochet as a fascist theorist"],
         "Locke is the PoS anchor for consent and natural rights in classical liberal origins.",
         "Students attach rights language to illiberal rulers."),
        ("2.7k", "An analyst who argues capitalism’s contradictions will yield proletarian revolution is drawing on",
         "Marxism", ["classic conservatism’s defence of tradition", "Adam Smith’s invisible hand as final goal", "Mill’s harm principle alone"],
         "Marxism is listed among ideologies responding to classical liberalism.",
         "Students mislabel Marxist revolution as modern liberalism."),
        ("2.7k", "Company-funded clinics and pensions meant to keep markets stable without socialism best fit",
         "welfare capitalism", ["Soviet war communism", "Nazi Gleichschaltung", "pure anarchism"],
         "Welfare capitalism softens industrial capitalism while retaining capitalist structures.",
         "Students call any welfare tool ‘communism.’"),
        ("2.6k", "‘The government that governs least protects wealth best’ as a nineteenth-century slogan aligns with",
         "limited government under classical liberal political economy",
         ["command economy five-year planning", "fascist total mobilization as peacetime normal", "nonalignment summits"],
         "Limited government is a named impact area in 2.6k.",
         "Students confuse limited government with authoritarian minimal personal freedom."),
        ("2.8k", "Creating unemployment insurance while preserving multi-party elections exemplifies",
         "welfare-state instruments inside modern liberal democracy",
         ["rejection of all liberal principles via fascism", "abolition of markets under war communism", "racial state theory"],
         "The welfare state is a modern liberal evolution, not fascism or Soviet communism.",
         "Students treat social insurance as proof liberalism ended."),
    ]
    for i, (oc, stem, ans, dist, expl, mist) in enumerate(extras):
        q.append(mc(
            stem, ans, dist, expl, mist,
            topic=T_ORIG, outcome_code=oc,
            skill_tested="Applying classical/modern liberal concepts",
            difficulty=_d(i), estimated_time_seconds=_t(80, 100, 120, i),
        ))

    return q


def _shift_choices(items: list) -> list:
    """Rotate choice order so the correct option is not always first."""
    out = []
    for i, item in enumerate(items):
        if item["question_type"] != "Multiple Choice":
            out.append(item)
            continue
        choices = item["choices"][:]
        rot = i % 4
        choices = choices[rot:] + choices[:rot]
        item = dict(item)
        item["choices"] = choices
        out.append(item)
    return out


def build_all() -> list:
    """Assemble full pool (unbalanced). Additional units imported below."""
    from . import unit_ri2b_ri3_ri4 as rest
    from . import unit_supplement as supplement

    pool = []
    pool.extend(_ri1())
    pool.extend(_ri2a())
    pool.extend(rest.build_questions())
    pool.extend(supplement.build_questions())
    pool = _shift_choices(pool)
    # Deterministic shuffle for variety without balancing
    rng = random.Random(301)
    rng.shuffle(pool)
    return pool
