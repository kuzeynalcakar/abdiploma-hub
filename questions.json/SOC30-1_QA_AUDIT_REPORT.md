# SOC30-1 Question Pool — Production QA Audit Report

**Status: CLEAN (critical residuals = 0)**  
**Pool file:** `questions.json/soc30-1_questions_pool.json`  
**Final count:** 364 questions (unbalanced pool after QA; not the 300 production cut)

## Automated + content QA criteria

| Check | Result |
|-------|--------|
| Incorrect answer keys | **0** |
| Exact duplicate stems | **0** |
| Near-duplicate pairs (≥0.90 similarity) | **0** |
| Schema / validator errors | **0** |
| Curriculum / outcome–topic mismatches | **0** |
| Unit field mismatches | **0** |
| Ambiguous near-identical choice pairs | **0** |
| Absurd / implausible distractors | **0** |
| Non-label short distractors on prose items | **0** |
| Repeated explanations | **0** (max repeat = 1) |
| Repeated common_mistake | **0** (max repeat = 1) |
| Repeated skill_tested | **0** (max repeat = 1) |
| Biology/chemistry/physics factual bleed | **0** |
| Sequence-code / non-numeric NR | **0** |
| Grading ambiguity (NR not objectively numeric) | **0** |

## What was fixed

1. **Template clone families removed or capped**  
   Containment year-loops, “source booklet / debates over [issue]” clones, locale-school/wells clones, economy-featuring clones, policy-controversy clones, mill-novel year clones, citizen-action clones, vignette duplicates.

2. **Distractors strengthened (114+ sets in pass 2)**  
   Replaced joke/off-domain options (airline liveries, pin factories, GDP trivia, “Smith disliked tea”, etc.) with plausible ideological misconceptions aligned to each related issue.

3. **Metadata uniquified**  
   Explanations, common mistakes, and `skill_tested` strings made item-specific so diploma-style review does not show copy-paste cues.

4. **Schema / keys / outcomes revalidated**  
   Bio/Math 14-field schema; MC = 4 choices / 1 correct; NR numeric + empty choices; outcomes constrained to PoS codes for each seeded topic.

5. **Generator hardened**  
   Source modules updated so regeneration will not recreate the containment year-loop or 8× locale-template swarm.

## Final distribution (QA’d pool)

| Topic | Count |
|-------|------:|
| Ideology and Identity | 83 |
| Origins of Liberalism | 51 |
| Resistance to Liberalism | 77 |
| The Viability of Contemporary Liberalism | 92 |
| Citizenship and Ideology | 61 |
| **Total** | **364** |

| Type | Count |
|------|------:|
| Multiple Choice | 341 |
| Numerical Response | 23 |

| Difficulty | Count |
|------------|------:|
| Easy | 127 |
| Medium | 116 |
| Hard | 121 |

## QA tooling (repeatable)

```text
python -m soc30_questions.qa_clean_pool
python -m soc30_questions.qa_pass2_distractors
python -m soc30_questions.qa_pass3_finalize
```

## Next step

Pool is QA-clean but **not balanced** to the 300-item production blueprint. Run the cleaner (`TOPIC_TARGETS` / type / difficulty) when ready to cut the production bank.

## Pass 3 finalize
- Key semantic fixes applied: 0
- Least-likely liberalish items dropped: 0
- Final residual: `{"total": 364, "exact_dup_stems": 0, "near_dup_pairs_ge_90": 0, "schema_errors": 0, "bad_keys": 0, "curriculum_outcome_mismatches": 0, "unit_mismatches": 0, "explanation_max_repeat": 1, "common_mistake_max_repeat": 1, "skill_max_repeat": 1, "by_topic": {"Resistance to Liberalism": 77, "Origins of Liberalism": 51, "Ideology and Identity": 83, "Citizenship and Ideology": 61, "The Viability of Contemporary Liberalism": 92}, "by_type": {"Multiple Choice": 341, "Numerical Response": 23}, "by_difficulty": {"Easy": 127, "Hard": 121, "Medium": 116}}`

### Sample key review (random 12)
- **3.5k** Authoritarian systems may hold plebiscites yet still fail liberalism because
  - KEY: without rights, competition, and accountability, popular rituals do not equal liberal democracy
- **3.6k** Partisan officials purge independent statistical agencies. The strongest 30-1 classification is
  - KEY: eroding information integrity needed for liberal accountability
- **3.6k** Surveillance laws gather opposition data with weak oversight. The strongest 30-1 classification is
  - KEY: security tools that can become illiberal within democracies
- **2.6k** Parliament’s role is framed as protecting property and order more than running industry. This develo
  - KEY: limited government
- **3.9k** Debt and poverty challenge viability when citizens ask whether
  - KEY: liberal political economies can still secure basic dignity and opportunity
- **1.10k** The claim ‘you are your ideology or you are nothing’ is most vulnerable to critique that
  - KEY: people typically hold plural identities that ideology alone should not monopolize
- **1.7k** A court blocks a ministry from jailing critics who publish peaceful dissent. This example best illus
  - KEY: individual rights and freedoms
- **3.5k** Elected legislators debate and pass laws on voters’ behalf. This description best matches
  - KEY: representative democracy
- **3.5k** Strongia (fictional) with jails for peaceful bloggers is described in a source set. The best system 
  - KEY: authoritarian political practice incompatible with liberal rights
- **4.7k** Loyalty scare tactics chill dissent under anti-communist suspicion. The conflict-context label from 
  - KEY: McCarthyism
- **4.7k** During episodes of humanitarian crises, liberal citizenship analysis should especially consider
  - KEY: how rights, dissent, and security claims collide under pressure
- **2.10k** Considering a Guatemalan reformer courted by rival intelligence services, a 30-1 analysis should con
  - KEY: liberation movements / ideological patronage

**CRITICAL_RESIDUAL_SUM=0**
