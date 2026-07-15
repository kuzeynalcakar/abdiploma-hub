#!/usr/bin/env python3
"""Deeper Grade-12 student pass: find remaining production smells and fix them."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "questions.json"
SRC = QDIR / "soc30-1_questions_final.json"
ALIAS = QDIR / "course_questions_final.json"

# Pattern libraries
AI_TELLS = [
    (r"\bin this case\b", "answer_tail_in_this_case"),
    (r"analysis example \d+", "residue_example_n"),
    (r"Applied here to outcome", "applied_here"),
    (r"In items like this one", "items_like_this"),
    (r"diploma preparation excludes", "meta_diploma_prep"),
    (r"fictional classroom towns", "meta_fiction"),
    (r"related-issue principles", "meta_related_issue"),
    (r"\(Case study \d+\)", "case_study_suffix"),
    (r"proves liberalism has no competing interpretations", "fallback_distractor"),
    (r"unlimited state power without rights protections", "fallback_distractor2"),
]

STEM_TEMPLATE_PREFIXES = [
    "Relative to principles of liberalism,",
    "Measured against liberal principles",
    "Compared with liberal market principles",
    "Against liberal criteria of rights",
    "Which label best fits",
    "A student summary stating that",
    "An editorial claims that",
]


def load():
    return json.loads(SRC.read_text(encoding="utf-8"))


def save(data):
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    SRC.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")


def scan(data):
    flags = defaultdict(list)
    for i, q in enumerate(data):
        blob = " | ".join(
            [
                q["question_text"],
                q["answer"],
                q.get("explanation", ""),
                q.get("common_mistake", ""),
                " || ".join(c["text"] for c in q.get("choices") or []),
            ]
        )
        for pat, name in AI_TELLS:
            if re.search(pat, blob, re.I):
                flags[name].append(i)
        for pref in STEM_TEMPLATE_PREFIXES:
            if q["question_text"].startswith(pref):
                flags[f"stem_prefix::{pref[:40]}"].append(i)

    # duplicate answers within same stem family
    texts = Counter(q["question_text"].strip().lower() for q in data)
    for t, n in texts.items():
        if n > 1:
            flags["exact_duplicate_stem"].append(t[:80])

    # MC integrity
    for i, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            continue
        corrects = [c for c in q["choices"] if c.get("is_correct")]
        if len(corrects) != 1:
            flags["bad_correct_count"].append(i)
        elif corrects[0]["text"] != q["answer"]:
            flags["answer_mismatch"].append(i)
        # weak: distractor equals substring of answer
        for c in q["choices"]:
            if not c.get("is_correct") and c["text"].strip().lower() == q["answer"].strip().lower():
                flags["duplicate_correct_as_distractor"].append(i)

    # Distractor reuse
    dist = Counter()
    for q in data:
        for c in q.get("choices") or []:
            if not c.get("is_correct"):
                dist[c["text"].strip().lower()] += 1
    hot = [(t, n) for t, n in dist.items() if n > 2]
    flags["distractor_overuse_gt2"] = [f"{n}× {t[:70]}" for t, n in sorted(hot, key=lambda x: -x[1])[:30]]

    ans = Counter(q["answer"].strip().lower() for q in data if q["question_type"] == "Multiple Choice")
    hot_a = [(t, n) for t, n in ans.items() if n > 3]
    flags["answer_overuse_gt3"] = [f"{n}× {t[:70]}" for t, n in sorted(hot_a, key=lambda x: -x[1])[:20]]

    return flags


def fix(data, flags):
    fixes = Counter()

    # Remove "in this case" answer tails
    for i in flags.get("answer_tail_in_this_case", []):
        q = data[i]
        new_ans = re.sub(r"\s+in this case\s*$", "", q["answer"], flags=re.I).strip()
        if new_ans != q["answer"]:
            q["answer"] = new_ans
            for c in q.get("choices") or []:
                if c.get("is_correct"):
                    c["text"] = new_ans
                else:
                    c["text"] = re.sub(r"\s+in this case\s*$", "", c["text"], flags=re.I).strip()
            fixes["stripped_in_this_case"] += 1

    # Remove Case study suffixes
    for i in flags.get("case_study_suffix", []):
        q = data[i]
        q["question_text"] = re.sub(r"\s*\(Case study \d+\)\.?\s*$", "", q["question_text"]).strip()
        if not q["question_text"].endswith((".", "?", "!")):
            # leave as was
            pass
        fixes["stripped_case_study"] += 1

    # Replace meta / fallback distractors
    TOPIC_POOL = {
        "Ideology and Identity": [
            "that ideology never shapes how people interpret events",
            "that individualism always requires identical outcomes for every citizen",
            "that collective identity cannot coexist with individual rights",
            "that Canadian civic life has only one legitimate ideology",
        ],
        "Origins of Liberalism": [
            "that early liberals rejected constitutional limits on rulers",
            "that classical liberalism centred hereditary privilege as its core aim",
            "that Locke argued rights originate only from royal decree",
            "that Smith argued prices should always be set by a central plan",
        ],
        "Resistance to Liberalism": [
            "that fascist systems maximized multiparty competition and free press",
            "that Soviet planned economies maximized consumer market choice",
            "that classical conservatives always endorsed sudden revolution",
            "that collectivist resistance never criticized liberal capitalism",
        ],
        "The Viability of Contemporary Liberalism": [
            "that modern liberalism never debates environment or equality",
            "that the Charter has no practical effect on Canadian rights claims",
            "that neoliberalism always expands redistributive welfare programs",
            "that Aboriginal rights sit outside Canadian liberal-democratic debate",
        ],
        "Citizenship and Ideology": [
            "that responsible citizenship excludes advocacy and petition",
            "that civic disagreement must always silence opposing views",
            "that ideology never influences citizenship rituals or campaigns",
            "that youth co-leadership cannot model public-issue strategies",
        ],
    }
    used = Counter()
    for q in data:
        for c in q.get("choices") or []:
            if not c.get("is_correct"):
                used[c["text"].strip().lower()] += 1

    meta_pats = [
        r"diploma preparation excludes",
        r"fictional classroom",
        r"related-issue principles",
        r"proves liberalism has no competing",
        r"unlimited state power without rights protections",
        r"source analysis should ignore ideology",
        r"economic systems? labels are interchangeable",
        r"Cold War concepts apply only to municipal",
        r"citizenship outcomes reject peaceful",
        r"collectivism forbids examining individual rights",
        r"classical and modern liberalism cannot be distinguished",
    ]

    for q in data:
        if q["question_type"] != "Multiple Choice":
            continue
        pool = list(TOPIC_POOL.get(q["topic"], []))
        changed = False
        for c in q["choices"]:
            if c.get("is_correct"):
                continue
            t = c["text"]
            if any(re.search(p, t, re.I) for p in meta_pats):
                # pick replacement
                repl = None
                for cand in sorted(pool, key=lambda x: (used[x.lower()], x)):
                    if cand.lower() != q["answer"].lower() and used[cand.lower()] < 2:
                        repl = cand
                        break
                if not repl:
                    repl = f"that the example supports rule without rights protections in {q['outcome_code']}"
                # decrement old, increment new
                used[t.strip().lower()] = max(0, used[t.strip().lower()] - 1)
                c["text"] = repl
                used[repl.lower()] += 1
                changed = True
                fixes["meta_distractor_replaced"] += 1
        if changed:
            # reshuffle not required
            pass

    # Cap distractor reuse > 2 by replacing excess occurrences
    dist_idx = defaultdict(list)
    for i, q in enumerate(data):
        if q["question_type"] != "Multiple Choice":
            continue
        for ci, c in enumerate(q["choices"]):
            if not c.get("is_correct"):
                dist_idx[c["text"].strip().lower()].append((i, ci))

    for text_l, locs in dist_idx.items():
        if len(locs) <= 2:
            continue
        for i, ci in locs[2:]:
            q = data[i]
            pool = TOPIC_POOL.get(q["topic"], TOPIC_POOL["Ideology and Identity"])
            repl = None
            existing = {c["text"].strip().lower() for c in q["choices"]}
            for cand in pool:
                cl = cand.lower()
                if cl not in existing and used[cl] < 2 and cl != q["answer"].strip().lower():
                    repl = cand
                    break
            if not repl:
                repl = f"that liberalism is irrelevant to the issue raised in {q['outcome_code']}"
            old = q["choices"][ci]["text"]
            used[old.strip().lower()] = max(0, used[old.strip().lower()] - 1)
            q["choices"][ci]["text"] = repl
            used[repl.lower()] += 1
            fixes["distractor_reuse_capped"] += 1

    # Fact sanity auto-fixes: known wrong-key patterns
    for q in data:
        qt = q["question_text"].lower()
        ans = q["answer"].lower()
        # Mill harm principle wrong key
        if "harm principle" in qt and ("bans all speech" in ans or "ban all" in ans):
            q["answer"] = "limits interference to preventing harm to others"
            for c in q.get("choices") or []:
                if c.get("is_correct"):
                    c["text"] = q["answer"]
            fixes["key_mill"] += 1
        # Representative democracy
        if "elected legislators debate and pass laws" in qt and "direct democracy" in ans:
            q["answer"] = "representative democracy"
            for c in q.get("choices") or []:
                if c.get("is_correct"):
                    c["text"] = q["answer"]
            fixes["key_rep_dem"] += 1

    # Grammar: leading "that" after stems ending with "as" where correct is noun phrase —
    # leave distractors as clauses (acceptable Alberta style on many items).

    # Clean skill_tested ending with ellipsis mid-word already handled

    # Indigenous already fixed; double-check aboriginal in answers/expl
    for q in data:
        for field in ("question_text", "answer", "explanation", "common_mistake"):
            if field in q and q[field]:
                new = re.sub(r"\bindigenous\b", "Indigenous", q[field])
                new = re.sub(r"\baboriginal\b", "Aboriginal", new)
                if new != q[field]:
                    q[field] = new
                    fixes["capitalization"] += 1
        for c in q.get("choices") or []:
            new = re.sub(r"\bindigenous\b", "Indigenous", c["text"])
            new = re.sub(r"\baboriginal\b", "Aboriginal", new)
            if new != c["text"]:
                c["text"] = new
                fixes["capitalization"] += 1

    return fixes


def curriculum_solve_sample(data):
    """Act like a student: verify a stratified sample's keys look correct."""
    notes = []
    by_topic = defaultdict(list)
    for q in data:
        by_topic[q["topic"]].append(q)

    checks = []
    for topic, qs in by_topic.items():
        # take 8 per topic across difficulties
        for diff in ("Easy", "Medium", "Hard"):
            bucket = [q for q in qs if q["difficulty"] == diff]
            checks.extend(bucket[:3])

    for q in checks:
        qt = q["question_text"]
        ans = q["answer"]
        ok = True
        reason = "plausible"
        # Heuristic contradictions
        low_q, low_a = qt.lower(), ans.lower()
        if "fascis" in low_q and any(x in low_a for x in ("expanded liberal", "multiparty democracy", "free press maximized")):
            ok = False
            reason = "fascism keyed as liberal democracy"
        if "command econom" in low_q and "private property" in low_a and "maximize" in low_a:
            ok = False
            reason = "command keyed as private property"
        if "adam smith" in low_q and "command" in low_a:
            ok = False
            reason = "Smith keyed as command"
        if "mccarthy" in low_q and "strengthened liberal free association" in low_a:
            ok = False
            reason = "McCarthyism keyed as strengthening liberal association"
        if q["question_type"] == "Numerical Response":
            if not re.fullmatch(r"\d+(\.\d+)?", str(ans).strip()):
                ok = False
                reason = "NR answer not numeric"
            # count questions: verify enumeration
            m = re.search(r"list:\s*(.+?)\.\s*How many", qt, re.I)
            if m:
                parts = [p.strip() for p in re.split(r";|,", m.group(1)) if p.strip()]
                # crude; semicolon lists preferred
                parts = [p.strip() for p in m.group(1).split(";") if p.strip()]
                if parts and str(len(parts)) != str(ans).strip():
                    ok = False
                    reason = f"NR count mismatch list={len(parts)} ans={ans}"
        notes.append(
            {
                "topic": q["topic"],
                "difficulty": q["difficulty"],
                "outcome": q["outcome_code"],
                "ok": ok,
                "reason": reason,
                "q": qt[:120],
                "a": ans[:100],
            }
        )
    return notes


def main():
    data = load()
    flags = scan(data)
    print("PRE_SCAN")
    for k, v in sorted(flags.items(), key=lambda kv: -len(kv[1])):
        print(f"  {k}: {len(v)}")
        if k.startswith("distractor") or k.startswith("answer_over"):
            for line in v[:8]:
                print(f"    {line}")

    first_fixes = fix(data, flags)
    print("FIXES", dict(first_fixes))

    # Iterate until distractor overuse clear / meta gone
    for round_i in range(4):
        flags = scan(data)
        if (
            not flags.get("distractor_overuse_gt2")
            and not flags.get("answer_tail_in_this_case")
            and not flags.get("meta_diploma_prep")
            and not flags.get("fallback_distractor")
            and not flags.get("residue_example_n")
            and not flags.get("bad_correct_count")
            and not flags.get("answer_mismatch")
        ):
            print(f"CLEAN after round {round_i}")
            break
        fix(data, flags)
        print(f"round {round_i} residual overuse", len(flags.get("distractor_overuse_gt2", [])))

    notes = curriculum_solve_sample(data)
    bad = [n for n in notes if not n["ok"]]
    print("SOLVE_SAMPLE", len(notes), "BAD", len(bad))
    for b in bad[:20]:
        print(" BAD", b)

    # Fix NR count mismatches found
    for b in bad:
        if b["reason"].startswith("NR count mismatch"):
            # find and fix
            for q in data:
                if q["outcome_code"] == b["outcome"] and q["question_text"].startswith(b["q"][:40]):
                    m = re.search(r"list:\s*(.+?)\.\s*How many", q["question_text"], re.I)
                    if m:
                        parts = [p.strip() for p in m.group(1).split(";") if p.strip()]
                        q["answer"] = str(len(parts))
                        print(" fixed NR", q["outcome_code"], q["answer"])

    flags = scan(data)
    notes = curriculum_solve_sample(data)
    bad = [n for n in notes if not n["ok"]]
    save(data)

    summary = {
        "ai_tells": {k: len(v) for k, v in flags.items() if not k.startswith("stem_prefix")},
        "stem_families": {k: len(v) for k, v in flags.items() if k.startswith("stem_prefix")},
        "solve_sample_n": len(notes),
        "solve_sample_bad": bad,
        "distractor_overuse_gt2": flags.get("distractor_overuse_gt2", []),
        "answer_overuse_gt3": flags.get("answer_overuse_gt3", []),
    }
    Path(QDIR / "soc30_1_student_audit_pass2.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("ai_tells", "solve_sample_n", "solve_sample_bad", "distractor_overuse_gt2", "answer_overuse_gt3")}, indent=2)[:4000])


if __name__ == "__main__":
    main()
