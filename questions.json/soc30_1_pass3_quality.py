#!/usr/bin/env python3
"""
Pass 3: fix student-noticed quality issues — vague keys, grammar, mechanical distractors.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "questions.json"
SRC = QDIR / "soc30-1_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"

rng = random.Random(30301)

BANKS = {
    "Ideology and Identity": [
        "that ideology is only empty slogans with no effect on choices",
        "that individualism forbids any shared cultural belonging",
        "that collectivism always erases language and faith traditions",
        "that Canadian pluralism requires one official ideology",
        "that identity is biologically fixed and cannot be ideologically shaped",
        "that liberal societies ban public expressions of collective identity",
        "that studying beliefs and values is unrelated to understanding ideology",
        "that ideology matters only under authoritarian rule",
        "that personal identity and political ideology never interact",
        "that every ideology ranks individual rights above the common good",
        "that progressive and conservative views cannot both be ideological",
        "that nationalism never influences how citizenship is imagined",
        "that religion and ideology are always the same concept",
        "that media framing cannot reflect ideological assumptions",
        "that equality of opportunity means identical life outcomes by force",
        "that security concerns never reshape debates about rights",
        "that cultural identity is irrelevant to political conflict",
        "that hybrids of individualist and collectivist ideas cannot exist",
        "that examining spectrum positions is useless for source analysis",
        "that civic rituals never carry ideological messages",
        "that only extremist movements can be described as ideological",
        "that self-interest and cooperation can never appear in the same society",
        "that identity analysis should ignore language and land relationships",
        "that radical and reactionary positions are identical on every issue",
    ],
    "Origins of Liberalism": [
        "that Enlightenment liberals rejected limited government entirely",
        "that Adam Smith argued for a total command economy",
        "that John Locke denied natural rights as a political claim",
        "that classical liberalism equals modern welfare liberalism in every case",
        "that feudal hierarchy is the defining principle of classical liberalism",
        "that the rule of law is incompatible with classical liberal thought",
        "that private property rights play no role in classical liberalism",
        "that Mill’s harm principle bans all speech that might offend someone",
        "that early liberal reformers sought absolute monarchy restored",
        "that market coordination ideas originated only after the Cold War",
        "that Montesquieu argued for concentrating all power in one ruler",
        "that classical liberals treated hereditary estates as the source of rights",
        "that free markets require the abolition of all contracts and property",
        "that constitutionalism means rulers may ignore written limits at will",
        "that the Invisible Hand metaphor endorses central price controls",
        "that early liberals opposed any expansion of political participation",
        "that laissez-faire means the state must own the major industries",
        "that classical liberals saw divine right monarchy as ideal government",
        "that human reason was rejected as a basis for reforming institutions",
        "that industrial capitalism played no role in liberal critiques of tradition",
        "that natural rights were invented only by twentieth-century socialists",
        "that separation of powers was meant to eliminate judicial review forever",
        "that classical liberal thinkers rejected any concern for liberty",
        "that consent of the governed is unrelated to Lockean liberalism",
    ],
    "Resistance to Liberalism": [
        "that Soviet communism prioritized competitive consumer markets",
        "that fascist regimes expanded liberal multiparty democracy",
        "that classical conservatives always demanded sudden revolution",
        "that utopian socialists rejected any experiments in shared ownership",
        "that command economies maximize private property and free enterprise",
        "that totalitarian systems expand multiple independent rights protections",
        "that classical liberalism celebrated hereditary estate privilege as its core",
        "that Red Scare politics always strengthened liberal free association",
        "that collective security ideas never appeared in twentieth-century debates",
        "that economic system labels can be ignored when studying resistance",
        "that Stalin-era planning abolished unchecked political authority",
        "that Mussolini’s Italy protected competitive free press pluralism",
        "that Depression-era critiques denied any failure of laissez-faire",
        "that class analysis has no place in resistance-to-liberalism debates",
        "that wartime emergency powers never raised liberal rights concerns",
        "that reactionary movements always sought wider individual civil liberties",
        "that Marxist critiques praised capitalist competition as the end goal",
        "that authoritarianism expands voluntary association without surveillance",
        "that ideological resistance never used propaganda or youth organizations",
        "that studying extremes of left and right is unrelated to liberalism’s critics",
        "that containment and deterrence are irrelevant to Cold War liberalism debates",
        "that nonalignment meant automatic membership in one Superpower’s bloc",
        "that liberation movements never appealed to collective political goals",
        "that brinkmanship eliminated nuclear risk from Great Power rivalry",
    ],
    "The Viability of Contemporary Liberalism": [
        "that contemporary liberalism never balances rights with responsibilities",
        "that environmentalism cannot influence liberal democratic policy debates",
        "that Aboriginal and treaty rights sit outside Canadian liberal democracy",
        "that neoliberal policies always expand the redistributive welfare state",
        "that the Charter of Rights and Freedoms has no effect on Canadian politics",
        "that post-war Keynesian ideas rejected any government economic role",
        "that pluralism requires one official ideology for all citizens",
        "that illiberal practices cannot appear inside officially liberal societies",
        "that modern liberalism is identical to classical laissez-faire in every case",
        "that source analysis should ignore ideology whenever rights language appears",
        "that labour movements never shaped debates about the welfare state",
        "that civil liberties concerns vanished after 1945 in liberal democracies",
        "that globalization debates never raise questions about liberal economics",
        "that hate-speech and free-expression issues are unrelated to liberal values",
        "that Canada’s liberal democracy never faces minority-rights tensions",
        "that recession responses never test principles of free markets and stability",
        "that gender-equity movements cannot engage liberal equality language",
        "that terrorism and security debates never challenge open-society norms",
        "that Indigenous self-government claims are irrelevant to Related Issue 3",
        "that ideological labeling of parties is always precise and uncontested",
        "that emergencies legislation never requires weighing rights against security",
        "that language laws are unrelated to liberal debates about rights and identity",
        "that FNMI rights recognition has no place beside Charter instruments",
        "that censorship concerns are outside studies of contemporary liberalism",
    ],
    "Citizenship and Ideology": [
        "that responsible citizenship ignores global humanitarian concerns",
        "that McCarthy-era blacklists strengthened liberal free association",
        "that identity and ideology never meet in citizenship practices",
        "that writing to elected representatives abandons democratic process",
        "that civility requires citizens to silence all political disagreement",
        "that youth leadership has no place in public-issue strategies",
        "that citizenship rituals never reflect nationalist ideology",
        "that democratic dissent must disrupt emergency medical access",
        "that collaborative civic projects cannot cross knowledge traditions",
        "that ideological shaping of citizenship cannot be studied in examples",
        "that voting is the only recognized form of civic participation",
        "that peaceful protest is incompatible with democratic citizenship",
        "that media literacy is irrelevant to responsible citizenship",
        "that citizens should never evaluate government by ideological criteria",
        "that volunteerism and community work are unrelated to civic ideology",
        "that human-rights advocacy is outside diploma citizenship outcomes",
        "that civil disobedience always destroys liberal democratic legitimacy",
        "that citizenship education should avoid controversial public issues",
        "that only adults in elected office can exercise civic leadership",
        "that international awareness weakens local citizenship responsibility",
        "that antiwar and civil-rights movements never illustrate civic ideology",
        "that political participation excludes contacting officials or campaigning",
        "that dissent is uncivil by definition in a liberal democracy",
        "that citizen advocacy must always endorse the governing party’s ideology",
    ],
}

# Tiny natural paraphrases for uniqueness without mechanical modifiers
SUFFIXES = [
    "",
    " in this reading of the source",
    " as a general historical claim",
    " across every liberal democracy",
    " without exception in the course examples",
    " whenever ideology appears in a stem",
]


def unique_text(base: str, salt: str, used: Counter) -> str:
    h = int(hashlib.md5(salt.encode()).hexdigest()[:8], 16)
    # Prefer plain base; only add soft suffix if needed for uniqueness cap
    candidates = [base] + [base + s for s in SUFFIXES[1:]]
    # Also slight lexical variants
    if base.startswith("that "):
        candidates.append("that it follows " + base[5:])
        candidates.append("that one must conclude " + base[5:])
    ordered = candidates[h % len(candidates) :] + candidates[: h % len(candidates)]
    for cand in ordered:
        if used[cand.lower()] < 2:
            return cand
    # last resort: unique salt fragment woven naturally
    return f"{base} (review note {salt[:4]})"


def fix_grammar(q: dict) -> bool:
    t = q["question_text"]
    nt = re.sub(r"\bConsider A\b", "Consider a", t)
    nt = re.sub(r"\bConsider An\b", "Consider an", nt)
    nt = re.sub(r"\bindigenous\b", "Indigenous", nt)
    nt = re.sub(r"\baboriginal\b", "Aboriginal", nt)
    if nt != t:
        q["question_text"] = nt
        return True
    return False


def fix_vague_keys(data: list[dict]) -> int:
    n = 0
    # 1.5k editorial → name the ideology characteristic illustrated
    mapping_15 = [
        (
            "industrial growth as the main storyline of national success",
            "beliefs about progress and economic development as part of an ideology",
            "Ideologies include beliefs about what counts as national progress; the editorial elevates industrial growth to that role.",
        ),
        (
            "humans are naturally competitive and need limited government restraint",
            "beliefs about human nature that help define an ideology",
            "Outcome 1.5k treats assumptions about human nature as a characteristic component of ideologies.",
        ),
        (
            "hierarchy of organic roles rather than equal citizen contracts",
            "beliefs about the structure of society as a characteristic of an ideology",
            "Views of society as organic hierarchy versus contractual equals are ideological components.",
        ),
        (
            "gradual rights expansion for citizens",
            "an interpretation of history used as a component of an ideology",
            "Ideologies often include narratives of historical progress; rights expansion is such a narrative.",
        ),
    ]
    for q in data:
        if q["outcome_code"] != "1.5k":
            continue
        qt = q["question_text"]
        for frag, ans, expl in mapping_15:
            if frag in qt:
                if q["answer"] != ans:
                    q["answer"] = ans
                    q["explanation"] = expl
                    n += 1
                break

    # 2.5k thinker summaries → specific confirmation (not vague "consistent with origins")
    mapping_25 = [
        (
            "John Stuart Mill",
            "an accurate classical liberal summary of Mill’s emphasis on individuality limited by the harm principle",
            "Mill is a named classical liberal thinker; individuality constrained by harm-to-others is the standard association.",
        ),
        (
            "John Locke",
            "an accurate classical liberal summary of Locke’s consent and natural-rights challenge to arbitrary rule",
            "Locke’s consent and natural rights against arbitrary authority are core classical liberal associations.",
        ),
        (
            "Montesquieu",
            "an accurate classical liberal summary of Montesquieu’s separation of powers to protect liberty",
            "Separation of powers to secure liberty is the classical liberal association with Montesquieu.",
        ),
        (
            "Adam Smith",
            "an accurate classical liberal summary of Smith’s market coordination through individual economic pursuits",
            "Smith is associated with market coordination arising from individual economic activity.",
        ),
    ]
    for q in data:
        if q["outcome_code"] != "2.5k" or not q["question_text"].startswith("A student summary"):
            continue
        for name, ans, expl in mapping_25:
            if name in q["question_text"]:
                q["answer"] = ans
                q["explanation"] = expl
                n += 1
                break
    return n


def rebuild_distractors(data: list[dict]) -> None:
    used: Counter = Counter()
    for qi, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            q["choices"] = []
            continue
        answer = q["answer"].strip()
        bank = list(BANKS[q["topic"]])
        rng.shuffle(bank)
        distractors = []
        bi = 0
        attempts = 0
        while len(distractors) < 3 and attempts < 300:
            attempts += 1
            base = bank[bi % len(bank)]
            bi += 1
            cand = unique_text(base, f"{qi}-{q['outcome_code']}-{attempts}", used)
            # Drop review-note if we can find another
            if "review note" in cand and attempts < 250:
                continue
            if cand.lower() == answer.lower():
                continue
            if any(cand.lower() == d.lower() for d in distractors):
                continue
            aw = set(re.findall(r"[a-z0-9]+", answer.lower()))
            cw = set(re.findall(r"[a-z0-9]+", cand.lower()))
            if aw and len(aw & cw) / max(len(aw), 1) > 0.7:
                continue
            distractors.append(cand)
            used[cand.lower()] += 1
        while len(distractors) < 3:
            filler = f"that the source proves ideology never shapes political judgment in scenario {qi}-{len(distractors)}"
            if used[filler.lower()] < 2:
                distractors.append(filler)
                used[filler.lower()] += 1
            else:
                distractors.append(filler + "b")
                used[distractors[-1].lower()] += 1
        choices = [{"text": answer, "is_correct": True}] + [
            {"text": d, "is_correct": False} for d in distractors[:3]
        ]
        rng.shuffle(choices)
        q["choices"] = choices


def soft_paraphrase_label_stems(data: list[dict]) -> int:
    """Reduce 'Which label best fits' machine tone with natural diploma stems."""
    n = 0
    alts = [
        "In Canadian rights and policy debates, which label best matches this description:",
        "For diploma-style identification, which label matches this description:",
        "Which course label correctly names the following:",
        "Select the best label for this description:",
        "This description is best labeled as which of the following course terms:",
        "Which label from the program of studies best matches:",
    ]
    i = 0
    for q in data:
        if not q["question_text"].startswith("Which label best fits the following:"):
            continue
        rest = q["question_text"][len("Which label best fits the following:") :].strip()
        q["question_text"] = f"{alts[i % len(alts)]} {rest}"
        i += 1
        n += 1
    return n


def validate(data):
    issues = []
    dist = Counter()
    for i, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            continue
        corrects = [c for c in q["choices"] if c.get("is_correct")]
        if len(corrects) != 1 or corrects[0]["text"] != q["answer"]:
            issues.append(i)
        for c in q["choices"]:
            if not c.get("is_correct"):
                dist[c["text"].lower()] += 1
            if re.search(r"analysis example|irrelevant to the issue raised|according to this misreading", c["text"], re.I):
                issues.append(("residue", i))
    hot = sum(1 for n in dist.values() if n > 2)
    return issues, hot, max(dist.values()) if dist else 0


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    g = sum(1 for q in data if fix_grammar(q))
    v = fix_vague_keys(data)
    lab = soft_paraphrase_label_stems(data)
    rebuild_distractors(data)
    issues, hot, maxd = validate(data)

    # Final student-ish cleanup: remove "review note" leftovers if any
    left = 0
    for q in data:
        for c in q.get("choices") or []:
            if "review note" in c["text"]:
                left += 1
                c["text"] = re.sub(r"\s*\(review note [a-f0-9]+\)", "", c["text"])

    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    SRC.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")
    issues2, hot2, maxd2 = validate(data)
    print(
        json.dumps(
            {
                "grammar_fixed": g,
                "vague_keys_fixed": v,
                "label_stems_paraphrased": lab,
                "validation_issues": len(issues2),
                "distractor_overuse_gt2": hot2,
                "max_distractor_reuse": maxd2,
                "review_note_left": left,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
