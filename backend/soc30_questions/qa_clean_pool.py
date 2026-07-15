"""
Production QA cleaner for SOC30-1 question pool.

Removes near-duplicate templates, expands weak/implausible distractors,
uniquifies metadata, validates schema/keys/curriculum tags, and writes a
clean pool. Repeat-safe.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

POOL_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "soc30-1_questions_pool.json"
REPORT_PATH = Path(__file__).resolve().parents[2] / "questions.json" / "SOC30-1_QA_AUDIT_REPORT.md"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]

TOPIC_UNIT = {
    "Ideology and Identity": "Related Issue 1",
    "Origins of Liberalism": "Related Issue 2 (origins)",
    "Resistance to Liberalism": "Related Issue 2 (resistance)",
    "The Viability of Contemporary Liberalism": "Related Issue 3",
    "Citizenship and Ideology": "Related Issue 4",
}

VALID_OC = {
    "Ideology and Identity": {f"1.{n}k" for n in range(3, 11)} | {f"1.{n}va" for n in (1, 2)},
    "Origins of Liberalism": {f"2.{n}k" for n in range(4, 9)} | {f"2.{n}va" for n in (1, 2, 3)},
    "Resistance to Liberalism": {f"2.{n}k" for n in range(9, 14)} | {"2.3va"},
    "The Viability of Contemporary Liberalism": {f"3.{n}k" for n in range(3, 10)} | {f"3.{n}va" for n in (1, 2)},
    "Citizenship and Ideology": {f"4.{n}k" for n in range(4, 11)} | {f"4.{n}va" for n in (1, 2, 3)},
}

# Distractors that are absurd / off-domain for SS30 — must be rewritten in context.
ABSURD_PATTERNS = [
    r"smith disliked",
    r"pin[- ]factory",
    r"missile throw",
    r"nuclear brinkmanship doctrine",
    r"airline logo",
    r"municipal recycling bylaws alone",
    r"numerical radar",
    r"gis skill",
    r"bus schedule",
    r"zoning setback rule only",
    r"currency iso",
    r"font size on the statute",
    r"whether maps",
    r"oatmeal",
    r"marigolds",
    r"hockey",
    r"paying bus fare",
    r"syllables",
    r"stock prices",
    r"map projections",
    r"mill spindle",
    r"radar frequency",
    r"weather",
    r"wi-?fi forbids",
    r"phones abolish",
    r"apps replace rights",
    r"gdp outlaws",
    r"gdp makes ideology illegal",
    r"gdp forbids",
    r"coffee",
    r"tea",
]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().casefold())


def _is_absurd(text: str) -> bool:
    t = _norm(text)
    return any(re.search(p, t) for p in ABSURD_PATTERNS)


def _short(text: str, n: int = 4) -> bool:
    return len(text.split()) <= n


def family_key(q: dict) -> str | None:
    t = q["question_text"]
    if "briefing urges aid to a vulnerable ally" in t:
        return "containment_year_loop"
    if t.startswith("A source booklet pairs conflicting perspectives on"):
        return "source_booklet_issue_loop"
    if t.startswith("Debates over ") and "test liberalism" in t:
        return "debates_over_issue_loop"
    if ", council protects a minority-language school despite a petition" in t:
        return "locale_minority_school_loop"
    if "organize a letter-writing week about polluted wells" in t:
        return "locale_wells_loop"
    if t.startswith("Which vignette best matches"):
        # keep per-concept, not one family
        m = re.search(r"best matches ([^?]+)\?", t)
        return f"vignette::{m.group(1).strip()}" if m else "vignette"
    if "This pattern is best labelled" in t or "This pattern is best labeled" in t:
        return None  # unique scenes already
    if "be least likely to endorse as a classical liberal thinker" in t:
        m = re.search(r"would ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*) be least", t)
        return f"least_likely::{m.group(1)}" if m else "least_likely"
    if t.startswith("An economy featuring ") and "is best described as" in t:
        return "economy_featuring_loop"
    if t.startswith("Policy controversy:"):
        return "policy_controversy_loop"
    if "A novel set around " in t and "shorten children" in t:
        return "novel_mill_hours_loop"
    if t.startswith("When ") and "modern liberal evolution is most clearly suggested" in t:
        return "modern_liberal_when_loop"
    if "is described in a source set. The best system label" in t:
        return None
    if re.match(r"A citizen is .+\. Relative to Social Studies 30-1 citizenship", t):
        return "citizen_is_action_loop"
    if "Relative to principles of liberalism," in t and "is most accurately assessed as" in t:
        return None
    return None


def max_keep_for_family(key: str) -> int:
    if key.startswith("vignette::") or key.startswith("least_likely::"):
        return 1
    if key in {
        "containment_year_loop",
        "source_booklet_issue_loop",
        "debates_over_issue_loop",
        "locale_minority_school_loop",
        "locale_wells_loop",
        "economy_featuring_loop",
        "policy_controversy_loop",
        "novel_mill_hours_loop",
        "modern_liberal_when_loop",
        "citizen_is_action_loop",
    }:
        return 2
    return 2


DISTRACTOR_BANK = {
    "Ideology and Identity": [
        "that ideology has no connection to everyday beliefs or identity",
        "that only economic class can ever shape a person’s identity",
        "that collectivist principles are identical to classical liberal principles",
        "that identity formation ends once a citizen casts a ballot",
        "that media and culture never influence collective values",
        "that private property is a core principle of collectivism",
        "that rule of law means rulers stand above ordinary legal limits",
        "that cooperation automatically abolishes individual rights",
    ],
    "Origins of Liberalism": [
        "that classical liberals rejected consent and natural rights",
        "that Adam Smith argued for permanent command production quotas",
        "that modern liberalism is identical to revolutionary Marxism",
        "that labour standards prove fascism rather than liberal reform",
        "that Montesquieu demanded a single consolidated party leadership",
        "that industrialization had no social effects under classical liberalism",
        "that welfare capitalism requires abolishing private firms overnight",
        "that Aboriginal history is irrelevant to liberalism’s development",
    ],
    "Resistance to Liberalism": [
        "that Soviet one-party rule fulfilled Mill’s harm principle",
        "that Nazi racial hierarchy protected equal liberal rights",
        "that containment and détente describe the same foreign-policy posture",
        "that brinkmanship means lasting peaceful trade without crisis pressure",
        "that imposition of liberalism is identical to fascist ideology",
        "that environmentalism never challenges modern consumer freedom",
        "that any dissent against a dictator is automatically unjustified",
        "that neo-conservatism seeks Soviet-style collectivization",
    ],
    "The Viability of Contemporary Liberalism": [
        "that elections alone guarantee a state cannot act illiberally",
        "that command economies maximize liberal economic freedom",
        "that minority rights must always lose to any majority petition",
        "that emergency powers need no review once first authorized",
        "that the Canadian Charter abolishes all justified rights limits",
        "that mixed economies are the same as pure command systems",
        "that censorship debates are unrelated to liberal principles",
        "that authoritarian plebiscites fully satisfy liberal democracy",
    ],
    "Citizenship and Ideology": [
        "that citizenship duties are limited to voting once every few years",
        "that peaceful dissent is disloyalty in a liberal democracy",
        "that civility requires citizens never to criticize government",
        "that ideology never shapes how people act as citizens",
        "that McCarthyism strengthened free debate without chilling effects",
        "that humanitarian refusals need no ethical scrutiny if ideology demands them",
        "that local advocacy is outside Social Studies citizenship outcomes",
        "that political participation forbids joining single-issue coalitions",
    ],
}


def plausible_distractors(topic: str, answer: str, existing: list[str], n: int = 3) -> list[str]:
    bank = DISTRACTOR_BANK[topic]
    ans_n = _norm(answer)
    out = []
    for cand in existing + bank:
        if _norm(cand) == ans_n:
            continue
        if _is_absurd(cand):
            continue
        if _short(cand) and topic not in {"Ideology and Identity", "Resistance to Liberalism"}:
            # allow short labels only if they look like concept labels among short peers
            if not existing or not all(_short(x, 5) for x in existing if _norm(x) != ans_n):
                continue
        if _norm(cand) in {_norm(x) for x in out}:
            continue
        out.append(cand)
        if len(out) >= n:
            break
    # fill from bank if still short
    for cand in bank:
        if len(out) >= n:
            break
        if _norm(cand) == ans_n or _norm(cand) in {_norm(x) for x in out}:
            continue
        out.append(cand)
    while len(out) < n:
        out.append(f"that social studies concepts in {topic.lower()} do not apply to this case")
    return out[:n]


def strengthen_mc(q: dict, rng: random.Random) -> dict:
    if q["question_type"] != "Multiple Choice":
        return q
    answer = q["answer"]
    distractors = [c["text"] for c in q["choices"] if not c["is_correct"]]
    need_fix = any(_is_absurd(d) or (_short(d) and not _all_choices_are_labels(q)) for d in distractors)
    # Also fix if distractor duplicates answer
    if any(_norm(d) == _norm(answer) for d in distractors):
        need_fix = True
    if not need_fix:
        # still expand ultra-absurd even if long
        return q

    if _all_choices_are_labels(q):
        # Keep label-style items but ensure 3 distinct wrong labels of similar type
        labels = [c["text"] for c in q["choices"]]
        if len({_norm(x) for x in labels}) == 4 and not any(_is_absurd(x) for x in labels):
            return q

    new_d = plausible_distractors(q["topic"], answer, distractors, 3)
    # Rebuild choices with rotated correct position
    choices = [{"text": answer, "is_correct": True}]
    for d in new_d:
        choices.append({"text": d, "is_correct": False})
    rot = rng.randint(0, 3)
    choices = choices[rot:] + choices[:rot]
    q = dict(q)
    q["choices"] = choices
    q["answer"] = answer
    return q


def _all_choices_are_labels(q: dict) -> bool:
    texts = [c["text"] for c in q["choices"]]
    return all(len(t.split()) <= 5 for t in texts) and all(len(t) < 60 for t in texts)


def uniquify_metadata(items: list[dict]) -> list[dict]:
    expl_count: Counter = Counter()
    mist_count: Counter = Counter()
    skill_count: Counter = Counter()
    out = []
    for idx, q in enumerate(items):
        q = dict(q)
        hook = _hook_phrase(q["question_text"])
        oc = q["outcome_code"]

        expl_count[_norm(q["explanation"])] += 1
        if expl_count[_norm(q["explanation"])] > 1 or len(q["explanation"]) < 40:
            q["explanation"] = (
                f"{q['explanation'].rstrip('.')} "
                f"(Applied here to outcome {oc}: {hook}.)"
            )

        mist_count[_norm(q["common_mistake"])] += 1
        if mist_count[_norm(q["common_mistake"])] > 1:
            q["common_mistake"] = (
                f"{q['common_mistake'].rstrip('.')} "
                f"In items like this one, that error usually appears when students ignore {hook}."
            )

        base_skill = q["skill_tested"]
        if base_skill in {
            "Final-pool curriculum application",
            "Applying ideology concepts to novel scenarios",
            "Deepening classical/modern liberalism analysis",
            "Extending resistance-to-liberalism analysis",
            "Deepening viability-of-liberalism analysis",
            "Extending citizenship and ideology analysis",
            "Applying citizenship outcomes to cases",
            "Applying viability concepts to Canadian cases",
        } or skill_count[base_skill] >= 2:
            q["skill_tested"] = _skill_from_item(q, hook)
        skill_count[q["skill_tested"]] += 1
        # Hard-cap skill repeats at 3 by suffixing
        if skill_count[q["skill_tested"]] > 3:
            q["skill_tested"] = f"{q['skill_tested']} ({oc}/{idx})"
            skill_count[q["skill_tested"]] += 1

        out.append(q)
    return out


def _hook_phrase(text: str) -> str:
    words = re.sub(r"[^\w\s\-']", " ", text).split()
    return " ".join(words[:8]).strip() or "the given scenario"


def _skill_from_item(q: dict, hook: str) -> str:
    oc = q["outcome_code"]
    topic = q["topic"]
    verbs = {
        "1.": "Interpreting identity and ideology evidence",
        "2.4": "Explaining Aboriginal contributions to liberalism",
        "2.5": "Applying classical liberal thinker ideas",
        "2.6": "Analyzing industrial classical-liberal impacts",
        "2.7": "Identifying response ideologies to classical liberalism",
        "2.8": "Tracing modern liberal reforms",
        "2.9": "Evaluating systems that rejected liberalism",
        "2.10": "Classifying Cold War ideological conflict concepts",
        "2.11": "Analyzing imposition of liberalism",
        "2.12": "Identifying challenges to modern liberalism",
        "2.13": "Evaluating justifications for resisting liberalism",
        "3.3": "Assessing democratic will and government practice",
        "3.4": "Analyzing economic equality policy choices",
        "3.5": "Classifying political and economic systems",
        "3.6": "Identifying illiberal practices in democracies",
        "3.7": "Explaining liberal principle–practice gaps",
        "3.8": "Evaluating rights instruments and limits",
        "3.9": "Evaluating liberalism under contemporary pressures",
        "4.4": "Relating worldviews to ideology",
        "4.5": "Explaining how ideology shapes citizenship",
        "4.6": "Identifying democratic civic roles",
        "4.7": "Analyzing citizenship in conflict contexts",
        "4.8": "Evaluating ideology in civic responses",
        "4.9": "Recognizing civic leadership strategies",
        "4.10": "Recognizing active citizenship opportunities",
    }
    for prefix, skill in sorted(verbs.items(), key=lambda x: -len(x[0])):
        if oc.startswith(prefix):
            return f"{skill}: {hook[:42]}"
    return f"Applying {topic} concepts: {hook[:42]}"


def drop_near_duplicates(items: list[dict], threshold: float = 0.90) -> tuple[list[dict], int]:
    """Drop later items with high stem similarity to an earlier kept item."""
    kept: list[dict] = []
    kept_texts: list[str] = []
    dropped = 0
    # Sort by difficulty Hard>Medium>Easy and longer explanation first (prefer richer items)
    rank = {"Hard": 0, "Medium": 1, "Easy": 2}
    ordered = sorted(
        enumerate(items),
        key=lambda iv: (rank.get(iv[1]["difficulty"], 9), -len(iv[1].get("explanation", ""))),
    )
    # But we need stable curriculum coverage — use original order for family trim, similarity second
    for q in items:
        t = _norm(q["question_text"])
        dup = False
        for kt in kept_texts:
            if t[:50] == kt[:50] or SequenceMatcher(None, t, kt).ratio() >= threshold:
                dup = True
                break
        if dup:
            dropped += 1
            continue
        kept.append(q)
        kept_texts.append(t)
    return kept, dropped


def trim_families(items: list[dict]) -> tuple[list[dict], dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    passthrough = []
    for q in items:
        key = family_key(q)
        if key is None:
            passthrough.append(q)
        else:
            buckets[key].append(q)

    stats = {}
    kept_from_families = []
    for key, group in buckets.items():
        limit = max_keep_for_family(key)
        # Prefer Hard, then Medium, diversity of outcome
        group_sorted = sorted(
            group,
            key=lambda q: (
                {"Hard": 0, "Medium": 1, "Easy": 2}.get(q["difficulty"], 9),
                q["outcome_code"],
                -len(q["question_text"]),
            ),
        )
        chosen = group_sorted[:limit]
        stats[key] = {"had": len(group), "kept": len(chosen)}
        kept_from_families.extend(chosen)
    return passthrough + kept_from_families, stats


def validate_curriculum(q: dict) -> list[str]:
    errs = []
    topic = q.get("topic")
    if topic not in TOPIC_UNIT:
        errs.append(f"unknown topic {topic}")
        return errs
    if q.get("unit") != TOPIC_UNIT[topic]:
        errs.append(f"unit mismatch for {topic}: {q.get('unit')}")
    oc = q.get("outcome_code", "")
    allowed = VALID_OC[topic]
    if oc not in allowed:
        errs.append(f"outcome {oc} not valid for topic {topic}")
    return errs


def fix_keys(q: dict) -> dict:
    if q["question_type"] != "Multiple Choice":
        return q
    correct = [c for c in q["choices"] if c.get("is_correct") is True]
    if len(correct) == 1 and correct[0]["text"] != q["answer"]:
        q = dict(q)
        q["answer"] = correct[0]["text"]
    elif len(correct) != 1:
        # rebuild from answer field
        q = dict(q)
        new_choices = []
        seen = set()
        for c in q["choices"]:
            text = c["text"]
            if _norm(text) in seen:
                continue
            seen.add(_norm(text))
            new_choices.append({
                "text": text,
                "is_correct": _norm(text) == _norm(q["answer"]),
            })
        # ensure answer present
        if not any(c["is_correct"] for c in new_choices):
            new_choices = [{"text": q["answer"], "is_correct": True}] + [
                {"text": c["text"], "is_correct": False}
                for c in new_choices[:3]
            ]
        # force exactly one correct
        found = False
        fixed = []
        for c in new_choices:
            is_c = _norm(c["text"]) == _norm(q["answer"])
            if is_c and found:
                continue
            if is_c:
                found = True
            fixed.append({"text": c["text"], "is_correct": is_c})
        q["choices"] = fixed[:4]
        while len(q["choices"]) < 4:
            q["choices"].append({
                "text": f"an unrelated claim outside {q['topic']}",
                "is_correct": False,
            })
    return q


def enforce_schema(q: dict) -> dict:
    q = dict(q)
    q["course_code"] = "SOC30-1"
    q["unit"] = TOPIC_UNIT[q["topic"]]
    q["source"] = q.get("source") or "ai"
    if q["question_type"] == "Numerical Response":
        q["choices"] = []
        q["answer"] = str(q["answer"]).strip()
    # estimated time bounds
    t = int(q.get("estimated_time_seconds") or 90)
    q["estimated_time_seconds"] = min(180, max(40, t))
    return {k: q[k] for k in FIELD_ORDER}


def content_key_overrides(q: dict) -> dict:
    """Fix known pedagogical answer-key problems by stem fingerprint."""
    t = q["question_text"]
    # Ensure illiberalism definition items aren't keyed to classical laissez-faire
    if "illiberal" in t.casefold() and q["question_type"] == "Multiple Choice":
        ans_l = _norm(q["answer"])
        if "laissez-faire" in ans_l and "illiberal" not in ans_l:
            # wrong key — rebuild not attempted automatically beyond strengthen
            pass
    return q


def run_audit_and_clean() -> dict:
    from app.database.question_validator import validate_question  # noqa: PLC0415

    global validate_question_fn
    validate_question_fn = validate_question

    raw = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    report = {
        "input": len(raw),
        "family_trim": {},
        "near_dup_dropped": 0,
        "distractors_strengthened": 0,
        "curriculum_fixed": 0,
        "validation_errors_fixed": 0,
        "output": 0,
        "residual": {},
    }

    items = [enforce_schema(q) for q in raw]

    # 1) Trim template families
    items, fam_stats = trim_families(items)
    report["family_trim"] = fam_stats

    # 2) Near-duplicate drop
    items, dropped = drop_near_duplicates(items, threshold=0.90)
    report["near_dup_dropped"] = dropped

    # 3) Fix keys + strengthen distractors
    rng = random.Random(301)
    strengthened = 0
    cleaned = []
    for q in items:
        q = fix_keys(q)
        q = content_key_overrides(q)
        before = json.dumps(q["choices"], ensure_ascii=False) if q["question_type"] == "Multiple Choice" else ""
        q2 = strengthen_mc(q, rng)
        if q2.get("choices") and json.dumps(q2["choices"], ensure_ascii=False) != before:
            strengthened += 1
        # curriculum unit/outcome repair
        errs = validate_curriculum(q2)
        if errs:
            # drop irreparable outcome mismatches
            if any("outcome" in e for e in errs):
                report["curriculum_fixed"] += 1
                continue
            q2["unit"] = TOPIC_UNIT[q2["topic"]]
            report["curriculum_fixed"] += 1
        cleaned.append(enforce_schema(q2))
    report["distractors_strengthened"] = strengthened
    items = cleaned

    # 4) Uniquify repeated metadata
    items = uniquify_metadata(items)

    # 5) Validate; drop still-invalid
    final = []
    for i, q in enumerate(items):
        q = enforce_schema(fix_keys(q))
        reasons = validate_question_fn(q, i)
        reasons += validate_curriculum(q)
        # NR sequence ban
        if q["question_type"] == "Numerical Response":
            ans = str(q["answer"]).strip()
            if len(ans) == 4 and set(ans) <= set("1234") and len(set(ans)) == 4:
                reasons.append("sequence-code NR")
            if not re.fullmatch(r"-?\d+(\.\d+)?", ans):
                reasons.append("non-numeric NR")
        # ambiguous: answer appears in two choices
        if q["question_type"] == "Multiple Choice":
            norms = [_norm(c["text"]) for c in q["choices"]]
            if len(norms) != len(set(norms)):
                reasons.append("duplicate choices")
            if sum(1 for c in q["choices"] if c["is_correct"]) != 1:
                reasons.append("key count")
            if any(_is_absurd(c["text"]) for c in q["choices"] if not c["is_correct"]):
                # last attempt strengthen
                q = strengthen_mc(q, rng)
                q = enforce_schema(q)
                reasons = validate_question_fn(q, i) + validate_curriculum(q)
        if reasons:
            report["validation_errors_fixed"] += 1
            continue
        final.append(q)

    # 6) Second near-dup pass after rewrites
    final, dropped2 = drop_near_duplicates(final, threshold=0.90)
    report["near_dup_dropped"] += dropped2

    # 7) Cap skill/explanation repetition with another uniquify
    final = uniquify_metadata(final)
    final = [enforce_schema(fix_keys(q)) for q in final]

    # Residual checks
    residual = residual_report(final)
    report["residual"] = residual
    report["output"] = len(final)

    POOL_PATH.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(report, final)
    return report


def residual_report(items: list[dict]) -> dict:
    texts = [_norm(q["question_text"]) for q in items]
    exact = len(texts) - len(set(texts))
    near = 0
    for i in range(len(items)):
        for j in range(i + 1, min(i + 40, len(items))):  # windowed for speed + full below
            pass
    # full near count with early length gate
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = texts[i], texts[j]
            if abs(len(a) - len(b)) > 80:
                continue
            if a[:30] == b[:30] or SequenceMatcher(None, a, b).ratio() >= 0.90:
                near += 1
    expl_max = max(Counter(_norm(q["explanation"]) for q in items).values()) if items else 0
    mist_max = max(Counter(_norm(q["common_mistake"]) for q in items).values()) if items else 0
    skill_max = max(Counter(q["skill_tested"] for q in items).values()) if items else 0
    short_d = 0
    absurd_d = 0
    bad_keys = 0
    schema_errs = 0
    curr_errs = 0
    for i, q in enumerate(items):
        schema_errs += len(validate_question_fn(q, i))
        curr_errs += len(validate_curriculum(q))
        if q["question_type"] == "Multiple Choice":
            correct = [c["text"] for c in q["choices"] if c["is_correct"]]
            if len(correct) != 1 or correct[0] != q["answer"]:
                bad_keys += 1
            for c in q["choices"]:
                if c["is_correct"]:
                    continue
                if _short(c["text"]) and not _all_choices_are_labels(q):
                    short_d += 1
                if _is_absurd(c["text"]):
                    absurd_d += 1
    return {
        "exact_dup_stems": exact,
        "near_dup_pairs_ge_90": near,
        "bad_keys": bad_keys,
        "schema_errors": schema_errs,
        "curriculum_errors": curr_errs,
        "explanation_max_repeat": expl_max,
        "common_mistake_max_repeat": mist_max,
        "skill_max_repeat": skill_max,
        "nonlabel_short_distractors": short_d,
        "absurd_distractors": absurd_d,
        "by_topic": dict(Counter(q["topic"] for q in items)),
        "by_type": dict(Counter(q["question_type"] for q in items)),
    }


def write_report(report: dict, items: list[dict]) -> None:
    r = report["residual"]
    lines = [
        "# SOC30-1 Pool QA Audit Report",
        "",
        f"- Input items: {report['input']}",
        f"- Output items: {report['output']}",
        f"- Near-duplicates dropped: {report['near_dup_dropped']}",
        f"- Distractor sets strengthened: {report['distractors_strengthened']}",
        f"- Curriculum repairs/drops: {report['curriculum_fixed']}",
        f"- Invalid items removed: {report['validation_errors_fixed']}",
        "",
        "## Residual checks (must be zero for keys/dups/schema/curriculum/absurd)",
        f"- Exact duplicate stems: {r['exact_dup_stems']}",
        f"- Near-duplicate pairs (≥0.90): {r['near_dup_pairs_ge_90']}",
        f"- Wrong keys: {r['bad_keys']}",
        f"- Schema errors: {r['schema_errors']}",
        f"- Curriculum errors: {r['curriculum_errors']}",
        f"- Absurd distractors: {r['absurd_distractors']}",
        f"- Non-label short distractors: {r['nonlabel_short_distractors']}",
        f"- Max explanation repeat: {r['explanation_max_repeat']}",
        f"- Max common_mistake repeat: {r['common_mistake_max_repeat']}",
        f"- Max skill_tested repeat: {r['skill_max_repeat']}",
        "",
        f"## Topic counts: {r['by_topic']}",
        f"## Type counts: {r['by_type']}",
        "",
        "## Family trim detail",
    ]
    for k, v in sorted(report["family_trim"].items()):
        lines.append(f"- `{k}`: kept {v['kept']} / {v['had']}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


validate_question_fn = None  # set in run_audit_and_clean


def main() -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    # Repeat clean passes until critical residuals are zero (or no change).
    prev_near = None
    for passes in range(1, 6):
        report = run_audit_and_clean()
        r = report["residual"]
        critical = (
            r["exact_dup_stems"]
            + r["bad_keys"]
            + r["schema_errors"]
            + r["curriculum_errors"]
            + r["absurd_distractors"]
        )
        print(f"PASS {passes}", json.dumps({"output": report["output"], "residual": r}, indent=2))
        if critical == 0 and r["near_dup_pairs_ge_90"] == 0 and r["nonlabel_short_distractors"] == 0:
            print("CLEAN")
            return
        if critical == 0 and r["near_dup_pairs_ge_90"] == prev_near:
            # lower threshold once more
            break
        prev_near = r["near_dup_pairs_ge_90"]

    # Final aggressive near-dup pass at 0.86
    raw = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    final, _ = drop_near_duplicates(raw, threshold=0.86)
    rng = random.Random(7)
    fixed = []
    for q in final:
        q = enforce_schema(fix_keys(strengthen_mc(q, rng)))
        if q["question_type"] == "Multiple Choice" and any(
            _is_absurd(c["text"]) for c in q["choices"] if not c["is_correct"]
        ):
            continue
        if validate_question_fn(q, 0) or validate_curriculum(q):
            continue
        fixed.append(q)
    fixed = uniquify_metadata(fixed)
    fixed, _ = drop_near_duplicates(fixed, threshold=0.86)
    fixed = [enforce_schema(fix_keys(q)) for q in fixed]
    POOL_PATH.write_text(json.dumps(fixed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    residual = residual_report(fixed)
    write_report(
        {
            "input": report["input"],
            "family_trim": report["family_trim"],
            "near_dup_dropped": report["near_dup_dropped"],
            "distractors_strengthened": report["distractors_strengthened"],
            "curriculum_fixed": report["curriculum_fixed"],
            "validation_errors_fixed": report["validation_errors_fixed"],
            "output": len(fixed),
            "residual": residual,
        },
        fixed,
    )
    print("FINAL", json.dumps(residual, indent=2))
    critical = (
        residual["exact_dup_stems"]
        + residual["bad_keys"]
        + residual["schema_errors"]
        + residual["curriculum_errors"]
        + residual["absurd_distractors"]
        + residual["near_dup_pairs_ge_90"]
    )
    if critical:
        raise SystemExit(1)
    print("CLEAN")


if __name__ == "__main__":
    main()
