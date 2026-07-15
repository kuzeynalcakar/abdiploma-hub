"""Pass 2: rewrite remaining weak/absurd MC distractors in the SOC30-1 pool."""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.question_validator import validate_question

POOL = Path(__file__).resolve().parents[2] / "questions.json" / "soc30-1_questions_pool.json"
REPORT = Path(__file__).resolve().parents[2] / "questions.json" / "SOC30-1_QA_AUDIT_REPORT.md"

TOPIC_UNIT = {
    "Ideology and Identity": "Related Issue 1",
    "Origins of Liberalism": "Related Issue 2 (origins)",
    "Resistance to Liberalism": "Related Issue 2 (resistance)",
    "The Viability of Contemporary Liberalism": "Related Issue 3",
    "Citizenship and Ideology": "Related Issue 4",
}

BANK = {
    "Ideology and Identity": [
        "that ideology has no meaningful link to personal or collective identity",
        "that collectivist principles are the same as classical liberal principles",
        "that only economic class can shape beliefs, never culture or media",
        "that private property is classified as a collectivist principle",
        "that rule of law places political leaders above ordinary legal limits",
        "that cooperation in a community automatically abolishes individual rights",
    ],
    "Origins of Liberalism": [
        "that classical liberals rejected consent, rights, and limited government",
        "that Adam Smith argued for permanent centrally planned production quotas",
        "that modern liberal reforms are identical to revolutionary Marxism",
        "that labour standards and unions prove a regime has become fascist",
        "that Montesquieu required all power to be held by one party leader",
        "that industrial society created no pressures on classical liberal limited government",
    ],
    "Resistance to Liberalism": [
        "that Soviet one-party censorship fulfilled liberal free-expression norms",
        "that Nazi racial hierarchy protected equal individual rights under liberalism",
        "that containment and detente describe the same unchanged foreign-policy stance",
        "that imposition of liberalism is conceptually identical to fascist ideology",
        "that environmentalism never conflicts with unlimited consumer freedom",
        "that neo-conservatism seeks Soviet-style collectivization of industry",
    ],
    "The Viability of Contemporary Liberalism": [
        "that holding elections makes illiberal rights violations impossible by definition",
        "that command economies maximize liberal private property and economic freedom",
        "that any majority petition must override entrenched minority rights",
        "that emergency powers, once created, need no legislative renewal or review",
        "that mixed economies are indistinguishable from pure command systems",
        "that authoritarian plebiscites fully satisfy the requirements of liberal democracy",
    ],
    "Citizenship and Ideology": [
        "that responsible citizenship is limited to casting a ballot every few years",
        "that peaceful public criticism of government is disloyalty in a democracy",
        "that civility requires citizens to avoid all disagreement with officials",
        "that ideology never influences how people understand civic duties",
        "that McCarthyism strengthened open debate without chilling dissent",
        "that local advocacy on public issues falls outside citizenship outcomes",
    ],
}

ABSURD = re.compile(
    r"invented vaccines|brinkmanship etiquette|airline livery|airline yield|nuclear spoilers|"
    r"medieval guilds|radio towers|f[uü]hrer oaths|command shoe|any public school existing|"
    r"any income tax existing|any road existing|pin.?factory|disliked tea|missile throw|"
    r"recycling bylaws alone|radar frequency|marigolds|watching hockey|paying bus fare|"
    r"map projections|mill spindle|outlaws identity|gdp |wi-?fi|phones abolish|font size|"
    r"oatmeal|syllables|stock prices|whether maps|bus schedule|gis skill|"
    r"currency iso|zoning setback|weather|apps replace|abolishes democracy|yield management|"
    r"throne-and-altar only|hide opinions forever|seize radio|"
    r"^ending elections$|^requiring |^creating command|^any |^only |^whether |^they ",
    re.I,
)

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().casefold())


def all_label_choices(q: dict) -> bool:
    texts = [c["text"] for c in q["choices"]]
    return all(len(t.split()) <= 5 and len(t) < 55 for t in texts)


def needs_rewrite(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    if all_label_choices(q):
        return False
    ans_len = len(q["answer"].split())
    for c in q["choices"]:
        if c["is_correct"]:
            continue
        t = c["text"]
        if ABSURD.search(t):
            return True
        if len(t.split()) <= 4 and ans_len >= 6:
            return True
        if len(t.split()) <= 3:
            return True
    return False


def rebuild(q: dict, rng: random.Random) -> dict:
    ans = q["answer"]
    bank = list(BANK[q["topic"]])
    rng.shuffle(bank)
    dist: list[str] = []
    for cand in bank:
        if norm(cand) == norm(ans):
            continue
        if norm(cand) in {norm(x) for x in dist}:
            continue
        dist.append(cand)
        if len(dist) == 3:
            break
    fillers = [
        f"that this scenario does not engage {q['topic']} concepts",
        f"that outcome {q['outcome_code']} is unrelated to source interpretation",
        "that ideological principles cannot be applied to contemporary cases",
    ]
    for f in fillers:
        if len(dist) >= 3:
            break
        if norm(f) != norm(ans) and norm(f) not in {norm(x) for x in dist}:
            dist.append(f)

    choices = [{"text": ans, "is_correct": True}]
    for d in dist[:3]:
        choices.append({"text": d, "is_correct": False})
    rot = rng.randint(0, 3)
    choices = choices[rot:] + choices[:rot]
    q = dict(q)
    q["choices"] = choices
    q["answer"] = ans
    if ABSURD.search(q.get("common_mistake", "")):
        q["common_mistake"] = (
            "Students choose an off-scope or joke-like option instead of applying the targeted outcome."
        )
    return q


def order_item(q: dict) -> dict:
    q = dict(q)
    q["course_code"] = "SOC30-1"
    q["unit"] = TOPIC_UNIT[q["topic"]]
    q["source"] = q.get("source") or "ai"
    if q["question_type"] == "Numerical Response":
        q["choices"] = []
    return {k: q[k] for k in FIELD_ORDER}


def main() -> None:
    data = json.loads(POOL.read_text(encoding="utf-8"))
    rng = random.Random(42)
    fixed = 0
    out = []
    for q in data:
        if needs_rewrite(q):
            q = rebuild(q, rng)
            fixed += 1
        out.append(order_item(q))

    # Drop any remaining near-dups (>=0.90)
    from difflib import SequenceMatcher

    kept: list[dict] = []
    kept_t: list[str] = []
    for q in out:
        t = norm(q["question_text"])
        if any(
            t[:40] == kt[:40] or SequenceMatcher(None, t, kt).ratio() >= 0.90
            for kt in kept_t
        ):
            continue
        kept.append(q)
        kept_t.append(t)

    schema_errs = 0
    bad_keys = 0
    absurd_left = 0
    short_left = 0
    for i, q in enumerate(kept):
        reasons = validate_question(q, i)
        if reasons:
            schema_errs += 1
        if q["question_type"] == "Multiple Choice":
            correct = [c["text"] for c in q["choices"] if c["is_correct"]]
            if len(correct) != 1 or correct[0] != q["answer"]:
                bad_keys += 1
            label = all_label_choices(q)
            for c in q["choices"]:
                if c["is_correct"]:
                    continue
                if ABSURD.search(c["text"]):
                    absurd_left += 1
                if (not label) and len(c["text"].split()) <= 4 and len(q["answer"].split()) >= 6:
                    short_left += 1

    POOL.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "rewrote_distractor_sets": fixed,
        "output": len(kept),
        "schema_errors": schema_errs,
        "bad_keys": bad_keys,
        "absurd_left": absurd_left,
        "short_left": short_left,
        "exact_dups": len(kept_t) - len(set(kept_t)),
        "by_topic": dict(Counter(q["topic"] for q in kept)),
        "by_type": dict(Counter(q["question_type"] for q in kept)),
    }
    print(json.dumps(summary, indent=2))

    # append to report
    block = [
        "",
        "## Pass 2 distractor rewrite",
        f"- Rewrote distractor sets: {fixed}",
        f"- Output: {len(kept)}",
        f"- Schema errors: {schema_errs}",
        f"- Bad keys: {bad_keys}",
        f"- Absurd distractors left: {absurd_left}",
        f"- Non-label short distractors left: {short_left}",
        f"- Topics: {summary['by_topic']}",
        "",
    ]
    prev = REPORT.read_text(encoding="utf-8") if REPORT.exists() else "# SOC30-1 Pool QA Audit Report\n"
    REPORT.write_text(prev.rstrip() + "\n" + "\n".join(block), encoding="utf-8")

    if schema_errs or bad_keys or absurd_left or short_left or summary["exact_dups"]:
        raise SystemExit(1)
    print("PASS2_CLEAN")


if __name__ == "__main__":
    main()
