"""Quick pool composition analysis for Chemistry 30 balancing."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

pool = json.loads(
    Path(r"C:\AlbertaPrep\questions.json\chemistry30_questions_pool.json").read_text(
        encoding="utf-8"
    )
)

TOPICS = [
    "Thermochemical Changes",
    "Electrochemical Changes",
    "Chemical Changes of Organic Compounds",
    "Chemical Equilibrium Focusing on Acid-Base Systems",
]
WEIGHTS = {"Thermochemical Changes": 0.21, "Electrochemical Changes": 0.31,
           "Chemical Changes of Organic Compounds": 0.21,
           "Chemical Equilibrium Focusing on Acid-Base Systems": 0.31}

print("Pool:", len(pool))
print("Topics:", dict(Counter(q["topic"] for q in pool)))
print("Types:", dict(Counter(q["question_type"] for q in pool)))
print("Diff:", dict(Counter(q["difficulty"] for q in pool)))
print("Outcomes:", len(set(q["outcome_code"] for q in pool)))

by_topic_type = defaultdict(lambda: Counter())
for q in pool:
    by_topic_type[q["topic"]][q["question_type"]] += 1
for t in TOPICS:
    print(t, dict(by_topic_type[t]))

def template_key(q):
    text = " ".join(q["question_text"].split()).casefold()
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    cleaned = re.sub(r"[^a-z#]+", "", text)
    return f"{q['topic']}|{cleaned}"

tmpl = Counter(template_key(q) for q in pool)
print("Template families:", len(tmpl))
print("Max per template:", max(tmpl.values()))

oc = Counter(q["outcome_code"] for q in pool)
print("Outcome counts min/max:", min(oc.values()), max(oc.values()))
print("Outcomes represented:", len(oc))

TARGET = 300
print("\nDiploma topic targets (300):")
for t in TOPICS:
    tgt = round(TARGET * WEIGHTS[t])
    print(f"  {t}: {tgt} (pool {Counter(q['topic'] for q in pool)[t]})")

print("\nType targets 60/40:")
print("  MC:", round(TARGET * 0.60))
print("  NR:", round(TARGET * 0.40))
print("  NR available:", Counter(q["question_type"] for q in pool)["Numerical Response"])
