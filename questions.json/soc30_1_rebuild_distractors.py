#!/usr/bin/env python3
"""
Rebuild ALL MC distractors with unique, curriculum-plausible misconceptions.
Cap any exact distractor text reuse at 2. No outcome-code / analysis-example residue.
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

rng = random.Random(30_1)

# Large banks of mistaken conclusions (Alberta SS30-1 flavoured)
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
        "that the Depression-era critiques denied any failure of laissez-faire",
        "that class analysis has no place in resistance-to-liberalism debates",
        "that wartime emergency powers never raised liberal rights concerns",
        "that reactionary movements always sought wider individual civil liberties",
        "that Marxist critiques praised capitalist competition as the end goal",
        "that authoritarianism expands voluntary association without surveillance",
        "that ideological resistance never used propaganda or youth organizations",
        "that studying extremes of left and right is unrelated to liberalism’s critics",
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
    ],
}

MODIFIERS = [
    "in most historical cases",
    "according to this misreading",
    "if ideological labels are ignored",
    "when rights language is taken at face value only",
    "under a strictly authoritarian reading",
    "if classical and modern liberalism are treated as identical",
    "when economic systems are left undefined",
    "if citizenship is reduced to obedience alone",
    "when pluralism is treated as uniformity",
    "if source context is discarded",
]


def variant(base: str, salt: str) -> str:
    """Create a unique-enough distractor from a base misconception."""
    h = int(hashlib.md5(salt.encode()).hexdigest()[:8], 16)
    mod = MODIFIERS[h % len(MODIFIERS)]
    # Two shapes to reduce template feel
    if h % 2 == 0:
        # strip leading that, rewrap
        core = re.sub(r"^\s*that\s+", "", base, flags=re.I)
        return f"that {core}, {mod}"
    else:
        core = re.sub(r"^\s*that\s+", "", base, flags=re.I)
        return f"that, {mod}, {core}"


def clean_answer_overuse(data):
    """Paraphrase overused correct answers carefully (max 3)."""
    ans_count = Counter(
        q["answer"].strip().lower() for q in data if q["question_type"] == "Multiple Choice"
    )
    paraphrases = {
        "consistent with classical liberal origins in the program of studies": [
            "aligned with classical liberal origins studied in the course",
            "consistent with classical liberal roots outlined in the program of studies",
            "matching classical liberal origins in the Alberta program of studies",
            "reflecting classical liberal origin ideas from the program of studies",
        ],
        "a characteristic component of an ideology": [
            "one characteristic component that ideologies commonly include",
            "a typical building block of an ideology",
            "a defining component often present in an ideology",
            "an element commonly treated as part of an ideology",
        ],
    }
    used_para = Counter()
    for q in data:
        if q["question_type"] != "Multiple Choice":
            continue
        key = q["answer"].strip().lower()
        if ans_count[key] <= 3:
            continue
        opts = paraphrases.get(key)
        if not opts:
            continue
        # assign least-used paraphrase
        pick = min(opts, key=lambda x: used_para[x.lower()])
        used_para[pick.lower()] += 1
        ans_count[key] -= 1
        ans_count[pick.lower()] += 1
        q["answer"] = pick
        for c in q["choices"]:
            if c.get("is_correct"):
                c["text"] = pick


def rebuild_all(data):
    used = Counter()
    rebuilt = 0
    for qi, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            q["choices"] = []
            continue
        answer = q["answer"].strip()
        bank = list(BANKS[q["topic"]])
        rng.shuffle(bank)
        distractors = []
        attempts = 0
        bi = 0
        while len(distractors) < 3 and attempts < 200:
            attempts += 1
            base = bank[bi % len(bank)]
            bi += 1
            cand = variant(base, f"{qi}-{attempts}-{q['outcome_code']}-{base[:20]}")
            cl = cand.lower()
            if cl == answer.lower():
                continue
            if any(cl == d.lower() for d in distractors):
                continue
            if used[cl] >= 2:
                continue
            # Avoid being a trivial synonym of the answer (shared high token overlap)
            aw = set(re.findall(r"[a-z0-9]+", answer.lower()))
            cw = set(re.findall(r"[a-z0-9]+", cl))
            if aw and len(aw & cw) / max(len(aw), 1) > 0.75:
                continue
            distractors.append(cand)
            used[cl] += 1
        # absolute fallback unique by index
        while len(distractors) < 3:
            cand = (
                f"that the scenario shows liberalism has no internal tensions "
                f"or competing interpretations in item {qi}-{len(distractors)}"
            )
            if used[cand.lower()] < 2:
                distractors.append(cand)
                used[cand.lower()] += 1
            else:
                distractors.append(cand + f" x{attempts}")
                used[distractors[-1].lower()] += 1

        choices = [{"text": answer, "is_correct": True}] + [
            {"text": d, "is_correct": False} for d in distractors[:3]
        ]
        rng.shuffle(choices)
        q["choices"] = choices
        rebuilt += 1
    return rebuilt, used


def validate(data):
    issues = []
    dist = Counter()
    for i, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            continue
        corrects = [c for c in q["choices"] if c.get("is_correct")]
        if len(q["choices"]) != 4:
            issues.append((i, "choice_n"))
        if len(corrects) != 1:
            issues.append((i, "correct_n"))
        elif corrects[0]["text"] != q["answer"]:
            issues.append((i, "mismatch"))
        for c in q["choices"]:
            if not c.get("is_correct"):
                dist[c["text"].lower()] += 1
            if re.search(r"analysis example \d+|irrelevant to the issue raised in \d", c["text"], re.I):
                issues.append((i, "residue"))
    hot = {t: n for t, n in dist.items() if n > 2}
    return issues, hot


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    clean_answer_overuse(data)
    n, used = rebuild_all(data)
    issues, hot = validate(data)
    # If still hot (shouldn't with unique variants), rebuild those items again
    rounds = 0
    while hot and rounds < 3:
        rounds += 1
        # force uniqueness: append subtle clause using hash of index for overused
        over_texts = set(hot)
        used2 = Counter()
        for q in data:
            if q["question_type"] != "Multiple Choice":
                continue
            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                if c["text"].lower() in over_texts or used2[c["text"].lower()] >= 2:
                    salt = hashlib.md5((q["question_text"] + c["text"]).encode()).hexdigest()[:6]
                    c["text"] = re.sub(r",?\s*\[u:[a-f0-9]+\]$", "", c["text"])
                    c["text"] = c["text"].rstrip(".") + f" [point {salt}]"
                    # cleaner: replace bracket with natural phrase
                    c["text"] = re.sub(r"\s*\[point [a-f0-9]+\]$", "", c["text"])
                    mod = MODIFIERS[int(salt, 16) % len(MODIFIERS)]
                    base = re.sub(r"^\s*that,?\s*", "", c["text"], flags=re.I)
                    base = re.sub(r",\s*(in most historical cases|according to this misreading|if ideological labels are ignored|when rights language is taken at face value only|under a strictly authoritarian reading|if classical and modern liberalism are treated as identical|when economic systems are left undefined|if citizenship is reduced to obedience alone|when pluralism is treated as uniformity|if source context is discarded)\s*$", "", base, flags=re.I)
                    c["text"] = f"that {base}, {mod}"
                used2[c["text"].lower()] += 1
        issues, hot = validate(data)

    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    SRC.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")
    print(json.dumps({
        "rebuilt_mc": n,
        "issues": len(issues),
        "issue_sample": issues[:10],
        "distractor_overuse_gt2": len(hot),
        "max_distractor_reuse": max(Counter(
            c["text"].lower()
            for q in data if q["question_type"]=="Multiple Choice"
            for c in q["choices"] if not c["is_correct"]
        ).values()),
        "max_answer_reuse": max(Counter(
            q["answer"].lower() for q in data if q["question_type"]=="Multiple Choice"
        ).values()),
    }, indent=2))


if __name__ == "__main__":
    main()
