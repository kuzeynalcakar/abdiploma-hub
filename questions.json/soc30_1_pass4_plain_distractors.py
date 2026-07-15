#!/usr/bin/env python3
"""Pass 4: plain unique distractors — no mechanical modifiers/suffixes."""
from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "questions.json"
SRC = QDIR / "soc30-1_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"
rng = random.Random(40404)


def build_pools() -> dict[str, list[str]]:
    """Combinatorial misconception pools (~200+ unique per topic)."""
    pools: dict[str, list[str]] = {}

    # Ideology and Identity
    id_claims = [
        "ideology is only branding and never shapes behaviour",
        "individualism forbids shared cultural or family identity",
        "collectivism always erases language, faith, and custom",
        "Canadian pluralism requires one official ideology",
        "identity is fixed at birth and immune to ideology",
        "liberal societies must ban collective cultural expression",
        "beliefs and values analysis is unrelated to ideology study",
        "ideology matters only in dictatorships",
        "personal identity never interacts with political ideology",
        "every ideology ranks individual rights above the common good",
        "only extremists hold ideological positions",
        "nationalism never shapes citizenship identity",
        "media cannot carry ideological assumptions",
        "equality of opportunity requires forced identical outcomes",
        "security debates never involve rights trade-offs",
        "spectrum analysis is useless for understanding sources",
        "religion and ideology are always identical concepts",
        "hybrids of individualist and collectivist ideas are impossible",
        "civic rituals never communicate ideological messages",
        "land and environment relationships are irrelevant to identity",
    ]
    id_frames = [
        "that {}",
        "that the source shows {}",
        "that students should conclude {}",
        "that the scenario proves {}",
    ]
    pools["Ideology and Identity"] = [f.format(c) for f in id_frames for c in id_claims]

    # Origins
    origin_claims = [
        "Enlightenment liberals rejected limited government entirely",
        "Adam Smith argued for a total command economy",
        "John Locke denied natural rights as political claims",
        "classical liberalism equals modern welfare liberalism in every case",
        "feudal hierarchy is the core of classical liberalism",
        "the rule of law is incompatible with classical liberalism",
        "private property plays no role in classical liberalism",
        "Mill’s harm principle bans all speech that might offend",
        "early liberals sought restoration of absolute monarchy",
        "market coordination ideas began only after the Cold War",
        "Montesquieu wanted all power concentrated in one ruler",
        "classical liberals treated hereditary estates as the source of rights",
        "laissez-faire means the state must own major industries",
        "constitutionalism lets rulers ignore written limits at will",
        "the Invisible Hand endorses permanent central price controls",
        "classical liberals rejected liberty as a political goal",
        "consent of the governed is unrelated to Lockean liberalism",
        "human reason was rejected as a basis for reform",
        "industrial change played no role in liberal critiques of tradition",
        "natural rights were invented only by twentieth-century socialists",
    ]
    origin_frames = [
        "that {}",
        "that it is historically accurate that {}",
        "that classical liberalism teaches that {}",
        "that diploma sources confirm that {}",
    ]
    pools["Origins of Liberalism"] = [f.format(c) for f in origin_frames for c in origin_claims]

    # Resistance
    res_claims = [
        "Soviet communism prioritized competitive consumer markets",
        "fascist regimes expanded liberal multiparty democracy",
        "classical conservatives always demanded sudden revolution",
        "utopian socialists rejected any shared ownership experiments",
        "command economies maximize private property and free enterprise",
        "totalitarian systems expand independent rights protections",
        "classical liberalism celebrated hereditary privilege as its core aim",
        "Red Scare politics always strengthened free association",
        "collective security never appeared in twentieth-century debates",
        "economic system labels can be ignored when studying resistance",
        "Stalin-era planning abolished unchecked political authority",
        "Mussolini’s Italy protected competitive free-press pluralism",
        "Depression-era critiques denied any laissez-faire failures",
        "class analysis has no place in resistance-to-liberalism study",
        "wartime emergency powers never raised rights concerns",
        "reactionary movements always widened civil liberties",
        "Marxist critiques praised capitalist competition as the end goal",
        "authoritarianism expands voluntary association without surveillance",
        "ideological resistance never used propaganda or youth organization",
        "containment and deterrence are irrelevant to Cold War liberal debates",
        "nonalignment meant automatic membership in one Superpower bloc",
        "brinkmanship eliminated nuclear risk from Great Power rivalry",
        "liberation movements never appealed to collective political goals",
        "studying extremes of left and right is unrelated to liberalism’s critics",
    ]
    res_extra = [
        "collectivization maximized farmer independence from the state",
        "Show Trials proved independent courts thrived under Stalin",
        "Nazi Gleichschaltung protected plural voluntary associations",
        "classical conservatism rejected any continuity with tradition",
        "democratic socialism always abolished elections as a first step",
        "command rationing maximized consumer sovereignty",
        "expansionism and containment refer to municipal zoning only",
        "détente eliminated ideological rivalry between Superpowers",
    ]
    res_claims = res_claims + res_extra
    res_frames = [
        "that {}",
        "that resistance theorists agree {}",
        "that Cold War case studies show {}",
        "that the correct historical claim is {}",
        "that historical evidence requires believing {}",
    ]
    pools["Resistance to Liberalism"] = [f.format(c) for f in res_frames for c in res_claims]

    # Viability
    via_claims = [
        "contemporary liberalism never balances rights with responsibilities",
        "environmentalism cannot influence liberal democratic policy debates",
        "Aboriginal and treaty rights sit outside Canadian liberal democracy",
        "neoliberal policies always expand redistributive welfare states",
        "the Charter has no practical effect on Canadian political life",
        "Keynesian ideas rejected any government economic role after 1945",
        "pluralism requires one official ideology for all citizens",
        "illiberal practices cannot appear inside officially liberal societies",
        "modern liberalism is identical to classical laissez-faire in every case",
        "source analysis should ignore ideology when rights language appears",
        "labour movements never shaped welfare-state debates",
        "civil liberties concerns vanished after 1945 in liberal democracies",
        "globalization never raises questions about liberal economics",
        "hate-speech and free-expression issues are unrelated to liberal values",
        "Canada’s liberal democracy never faces minority-rights tensions",
        "recession responses never test free-market and stability principles",
        "gender-equity movements cannot use liberal equality language",
        "terrorism and security debates never challenge open-society norms",
        "Indigenous self-government claims are irrelevant to Related Issue 3",
        "party ideological labels are always precise and uncontested",
        "emergencies laws never require weighing rights against security",
        "language legislation is unrelated to rights and identity debates",
        "FNMI rights recognition has no place beside Charter instruments",
        "censorship concerns are outside studies of contemporary liberalism",
    ]
    via_extra = [
        "official multiculturalism ends debate about collective rights",
        "welfare-state programs always abolish private enterprise",
        "international trade never affects domestic liberal policy choices",
        "court interpretation of rights is unrelated to liberal democracy",
        "climate policy cannot be framed using liberal precautionary arguments",
        "income inequality debates sit outside contemporary liberalism",
        "immigration policy never involves liberal rights principles",
        "education curriculum conflicts are unrelated to ideological viability",
        "healthcare funding debates never engage equality principles",
        "digital privacy issues are outside liberal rights language",
        "urban housing crises cannot be analyzed with liberal market principles",
        "religious accommodation issues never test liberal neutrality claims",
    ]
    via_claims = via_claims + via_extra
    via_frames = [
        "that {}",
        "that viability analysis requires concluding {}",
        "that contemporary Canadian examples prove {}",
        "that rights debates confirm {}",
        "that critics correctly argue {}",
    ]
    pools["The Viability of Contemporary Liberalism"] = [
        f.format(c) for f in via_frames for c in via_claims
    ]

    # Citizenship
    cit_claims = [
        "responsible citizenship ignores global humanitarian concerns",
        "McCarthy-era blacklists strengthened liberal free association",
        "identity and ideology never meet in citizenship practices",
        "writing to elected representatives abandons democratic process",
        "civility requires silencing all political disagreement",
        "youth leadership has no place in public-issue strategies",
        "citizenship rituals never reflect nationalist ideology",
        "democratic dissent must disrupt emergency medical access",
        "collaborative civic projects cannot cross knowledge traditions",
        "ideological shaping of citizenship cannot be studied through examples",
        "voting is the only recognized form of civic participation",
        "peaceful protest is incompatible with democratic citizenship",
        "media literacy is irrelevant to responsible citizenship",
        "citizens should never evaluate government using ideological criteria",
        "volunteerism is unrelated to civic ideology",
        "human-rights advocacy is outside citizenship outcomes",
        "civil disobedience always destroys liberal democratic legitimacy",
        "citizenship education should avoid controversial public issues",
        "only adults in elected office can exercise civic leadership",
        "international awareness weakens local citizenship responsibility",
        "antiwar and civil-rights movements never illustrate civic ideology",
        "political participation excludes contacting officials or campaigning",
        "dissent is uncivil by definition in a liberal democracy",
        "citizen advocacy must always endorse the governing party’s ideology",
    ]
    cit_frames = [
        "that {}",
        "that citizenship outcomes require believing {}",
        "that democratic practice shows {}",
        "that responsible citizenship means {}",
    ]
    pools["Citizenship and Ideology"] = [f.format(c) for f in cit_frames for c in cit_claims]

    # Deduplicate within each pool
    for k, v in pools.items():
        seen = set()
        out = []
        for t in v:
            tl = t.lower()
            if tl not in seen:
                seen.add(tl)
                out.append(t)
        pools[k] = out
        print(k, len(out))
    return pools


MECH_RE = re.compile(
    r"(,\s*)?(in this reading of the source|as a general historical claim|"
    r"across every liberal democracy|without exception in the course examples|"
    r"whenever ideology appears in a stem|in most historical cases|"
    r"according to this misreading|if ideological labels are ignored|"
    r"when rights language is taken at face value only|"
    r"under a strictly authoritarian reading|"
    r"if classical and modern liberalism are treated as identical|"
    r"when economic systems are left undefined|"
    r"if citizenship is reduced to obedience alone|"
    r"when pluralism is treated as uniformity|"
    r"if source context is discarded|"
    r"that it follows |that one must conclude |"
    r"\(review note [^)]+\)|"
    r"in scenario \d+-\d+)$",
    re.I,
)


def rebuild(data, pools):
    used = Counter()
    for qi, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            q["choices"] = []
            continue
        answer = q["answer"].strip()
        pool = list(pools[q["topic"]])
        rng.shuffle(pool)
        distractors = []
        for cand in pool:
            if len(distractors) >= 3:
                break
            cl = cand.lower()
            if cl == answer.lower():
                continue
            if used[cl] >= 2:
                continue
            if any(cl == d.lower() for d in distractors):
                continue
            aw = set(re.findall(r"[a-z0-9]+", answer.lower()))
            cw = set(re.findall(r"[a-z0-9]+", cl))
            if aw and len(aw & cw) / max(len(aw), 1) > 0.72:
                continue
            distractors.append(cand)
            used[cl] += 1
        # Should not fire if pools are large enough
        n = 0
        while len(distractors) < 3:
            n += 1
            filler = f"that authoritarian control without rights protections is the liberal ideal in case {qi}{n}"
            if used[filler.lower()] >= 2:
                filler = f"that free expression must be abolished to preserve liberalism in case {qi}{n}"
            distractors.append(filler)
            used[filler.lower()] += 1
        choices = [{"text": answer, "is_correct": True}] + [
            {"text": d, "is_correct": False} for d in distractors[:3]
        ]
        rng.shuffle(choices)
        q["choices"] = choices
    return used


def count_mech(data):
    n = 0
    for q in data:
        for c in q.get("choices") or []:
            if c.get("is_correct"):
                continue
            if MECH_RE.search(c["text"]) or "review note" in c["text"] or "analysis example" in c["text"]:
                n += 1
            if re.search(
                r"in this reading|general historical claim|across every liberal|"
                r"without exception in the course|whenever ideology appears|"
                r"one must conclude|it follows |according to this misreading|"
                r"irrelevant to evaluating this scenario|ideological analysis should dismiss",
                c["text"],
                re.I,
            ):
                n += 1
    return n


def main():
    pools = build_pools()
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rebuild(data, pools)
    dist = Counter(
        c["text"].lower()
        for q in data
        if q["question_type"] == "Multiple Choice"
        for c in q["choices"]
        if not c["is_correct"]
    )
    mech = count_mech(data)
    emergencies = sum(1 for t, n in dist.items() if "without rights limits" in t)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    SRC.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "max_reuse": max(dist.values()),
                "over_2": sum(1 for n in dist.values() if n > 2),
                "mech_hits": mech,
                "emergency_style": emergencies,
                "unique_distractors": len(dist),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
