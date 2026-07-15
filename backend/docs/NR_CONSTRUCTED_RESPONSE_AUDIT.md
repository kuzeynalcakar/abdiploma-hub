# Constructed-response (NR) auto-grade audit

**Dry run:** `False`
**Questions rewritten:** `48`
**Backup:** `C:\AlbertaPrep\backend\backups\albertaprep.db.bak-nr-rewrite-20260715_051034`
**Remaining written_response:** `0`

## Finding

All active `numerical_response` items already had a single numeric key and were auto-gradable. The invalid constructed-response items were the **48** active `written_response` questions (BIO30 + MATH30-1), which require subjective / multi-part marking.

Each was rewritten to an automatically graded short-answer `numerical_response` with `accepted_answers`. Stems only were rewritten; explanations, outcomes, difficulty, and skills preserved. MC questions were not modified. Banks were not regenerated.

## Rewrite table

| Course | Question ID | Reason invalid | Accepted answers |
|--------|-------------|----------------|------------------|
| MATH30-1 | 10 | Solve algebraically / state solutions (multi-value WR) | `3; 3` |
| MATH30-1 | 30 | Multi-part transformation WR | `4.5; 4.5; 9/2; 4.50` |
| MATH30-1 | 50 | Multi-part domain WR | `2; 2` |
| MATH30-1 | 68 | Multi-part composition / inverse WR | `yes; yes; Yes; y; true` |
| MATH30-1 | 86 | Multi-part inverse WR | `-5; -5` |
| MATH30-1 | 105 | Multi-part exponential equation WR | `0; 0` |
| MATH30-1 | 125 | Multi-part continuous growth WR | `22.0; 22.0; 22; 21.97; 21.972` |
| MATH30-1 | 144 | Multi-part factoring WR | `4; 4` |
| MATH30-1 | 164 | Multi-part arc angle WR | `1.5; 1.5; 3/2; 1.50` |
| MATH30-1 | 184 | Multi-part sinusoidal modelling WR | `10; 10; 10.0` |
| MATH30-1 | 204 | Prove identity / state restrictions WR | `2; 2` |
| MATH30-1 | 224 | Explain + calculate partitioning WR | `27720; 27720; 27,720` |
| MATH30-1 | 244 | Multi-part binomial expansion WR | `3.75; 3.75; 15/4; 3.750; 15/4` |
| MATH30-1 | 268 | Solve with verification WR | `4; 4` |
| MATH30-1 | 269 | Describe transformations WR | `-3; -3` |
| MATH30-1 | 292 | Describe asymptotes/domain WR | `x = 3; x = 3; x=3; x= 3; x =3; 3` |
| MATH30-1 | 293 | Solve rational equation WR (multiple solutions) | `2; 2` |
| MATH30-1 | 294 | Construct / justify rational function WR | `x/(x+2); x/(x+2); x / (x + 2); f(x)=x/(x+2); f(x) = x/(x+2); (x)/(x+2)` |
| BIO30 | 354 | Explain... (requires subjective/paragraph marking) | `ADH; ADH; adh; antidiuretic hormone; anti-diuretic hormone; vasopressin` |
| BIO30 | 355 | Explain... multi-step synaptic description | `Ca2+; Ca2+; Ca^{2+}; calcium; calcium ion; calcium ions` |
| BIO30 | 356 | Compare... autonomic divisions | `sympathetic; sympathetic; sympathetic nervous system; SNS; sympathetic division` |
| BIO30 | 357 | Describe... multi-system glucose regulation | `insulin; insulin; Insulin` |
| BIO30 | 358 | Compare... rod vs cone | `rods; rods; rod; rod cells; rod cell` |
| BIO30 | 359 | Explain... thyroid feedback | `TSH; TSH; tsh; thyroid-stimulating hormone; thyroid stimulating hormone; thyrotropin` |
| BIO30 | 360 | Explain... thyroid feedback | `TRH; TRH; trh; thyrotropin-releasing hormone; thyrotropin releasing hormone` |
| BIO30 | 361 | Explain... pupillary reflex | `parasympathetic; parasympathetic; parasympathetic nervous system; PNS; parasympathetic division` |
| BIO30 | 416 | Discuss... STS essay prompt | `ecological; ecological; ecology; environmental; Ecological` |
| BIO30 | 417 | Compare... spermatogenesis vs oogenesis | `4; 4; four` |
| BIO30 | 418 | Describe... ovarian cycle hormones | `LH; LH; lh; luteinizing hormone; luteinising hormone` |
| BIO30 | 419 | Explain... teratogen critical periods | `organogenesis; organogenesis; organogenesis period; critical period of organogenesis` |
| BIO30 | 420 | Describe... luteal phase | `corpus luteum; corpus luteum; the corpus luteum; Corpus luteum` |
| BIO30 | 421 | Explain... three factor types | `Hox genes; Hox genes; hox genes; Hox; homeobox genes; Hox gene` |
| BIO30 | 463 | Explain... nondisjunction/trisomy | `47; 47; 2n+1; trisomy` |
| BIO30 | 464 | Describe... prophase I variation | `crossing over; crossing over; crossover; crossing-over; genetic recombination; recombination` |
| BIO30 | 465 | Compare... mitosis vs meiosis | `2; 2; two` |
| BIO30 | 466 | Explain... tumour suppressor | `p53; p53; TP53; tp53; P53` |
| BIO30 | 534 | Evaluate... pedigree claim | `X-linked dominant; X-linked dominant; x-linked dominant; X linked dominant; sex-linked dominant` |
| BIO30 | 535 | Describe... DNA replication enzymes | `helicase; helicase; DNA helicase; Helicase` |
| BIO30 | 536 | Explain... CRISPR plus ethics | `guide RNA; guide RNA; gRNA; sgRNA; guide rna; Guide RNA` |
| BIO30 | 537 | Describe... frameshift effect | `frameshift; frameshift; frameshift mutation; frame-shift; frame shift` |
| BIO30 | 538 | Explain... X-linked colour blindness | `XNXc; XNXc; X^N X^c; XNXC; carrier; heterozygous carrier` |
| BIO30 | 539 | Explain... central dogma | `RNA; RNA; mRNA; rna; messenger RNA` |
| BIO30 | 540 | Distinguish... mutation types | `point mutation; point mutation; point; substitution; base substitution` |
| BIO30 | 541 | Explain... PCR + electrophoresis | `PCR; PCR; pcr; polymerase chain reaction; Polymerase Chain Reaction` |
| BIO30 | 583 | Explain... antibiotic selection | `natural selection; natural selection; selection; directional selection` |
| BIO30 | 584 | Explain... microevolution mechanisms | `genetic drift; genetic drift; drift; founder effect; bottleneck effect` |
| BIO30 | 585 | Predict... trophic cascade essay | `trophic cascade; trophic cascade; trophic cascades; cascade; top-down control` |
| BIO30 | 586 | Describe... three impacts essay | `wildlife corridors; wildlife corridors; wildlife corridor; habitat corridor; habitat corridors; ecological corridors` |

## Detail

### MATH30-1 #10

**Reason invalid:** Solve algebraically / state solutions (multi-value WR)

**Original:**

Solve the trigonometric equation $2\cos^2(x) - \sin(x) - 1 = 0$ algebraically over the domain $0 \le x < 2\pi$. State your solutions as exact values.

**New question:**

How many solutions does $2\cos^2(x) - \sin(x) - 1 = 0$ have over $0 \le x < 2\pi$? Record the integer count.

**Accepted answers:** 3, 3

### MATH30-1 #30

**Reason invalid:** Multi-part transformation WR

**Original:**

A function $y = f(x)$ has a domain of $[-6, 9]$ and a range of $[-4, 16]$. A student applies a transformation to create a new function, $g(x) = -3f(2x)$. 

a) State the coordinate mapping notation that describes this transformation.

b) Algebraically determine the domain and range of the transformed function $y = g(x)$.

**New question:**

If $y=f(x)$ has domain $[-6,9]$ and $g(x)=-3f(2x)$, what is the upper bound of the domain of $g$? Record as a decimal.

**Accepted answers:** 4.5, 4.5, 9/2, 4.50

### MATH30-1 #50

**Reason invalid:** Multi-part domain WR

**Original:**

Two functions are given by $f(x) = \sqrt{16 - x^2}$ and $g(x) = x^2 - 3x - 4$.

a) Determine the domain of $f(x)$ and the domain of $g(x)$.

b) Write the explicit equation for the quotient function $h(x) = \left(\frac{f}{g}\right)(x)$ and determine its exact domain restriction set.

**New question:**

For $f(x)=\sqrt{16-x^2}$ and $g(x)=x^2-3x-4$, how many real values must be excluded from the domain of $(f/g)(x)$ within $[-4,4]$? Record the integer count.

**Accepted answers:** 2, 2

### MATH30-1 #68

**Reason invalid:** Multi-part composition / inverse WR

**Original:**

Consider the function $f(x) = \frac{x + 2}{x - 1}$, where $x \neq 1$.

a) Algebraically determine the explicit equation for the composite function $f(f(x))$. Simplify completely.

b) Explain what your result from part a) implies about the geometric relationship between the graph of $f(x)$ and the line $y = x$.

**New question:**

If $f(x)=\dfrac{x+2}{x-1}$ and $f(f(x))=x$ (for permissible $x$), is $f$ its own inverse? Enter yes or no.

**Accepted answers:** yes, yes, Yes, y, true

### MATH30-1 #86

**Reason invalid:** Multi-part inverse WR

**Original:**

Consider the function $f(x) = -\sqrt{25 - x^2}$ defined over the domain $0 \le x \le 5$.

a) State the range of $f(x)$ over this specific domain interval.

b) Algebraically determine the explicit equation for the inverse function $f^{-1}(x)$ and state its exact domain restriction.

**New question:**

For $f(x)=-\sqrt{25-x^2}$ on $0\le x\le 5$, what is the lower bound of the range of $f$? Record the integer.

**Accepted answers:** -5, -5

### MATH30-1 #105

**Reason invalid:** Multi-part exponential equation WR

**Original:**

An exponential equation is given by $\left(\frac{4}{9}\right)^{x-3} = \left(\frac{27}{8}\right)^{x+2}$.

a) Express both sides of the equation using a common prime base fraction.

b) Algebraically solve the equation to find the exact value of $x$.

**New question:**

Solve $\left(\frac{4}{9}\right)^{x-3}=\left(\frac{27}{8}\right)^{x+2}$. Record the exact value of $x$.

**Accepted answers:** 0, 0

### MATH30-1 #125

**Reason invalid:** Multi-part continuous growth WR

**Original:**

An investment grows according to the continuous compounding formula $A = P\cdot e^{rt}$, where $A$ is the final amount, $P$ is the initial principal, $r$ is the annual interest rate, and $t$ is the time in years.

a) Rearrange the equation to isolate the time variable $t$ explicitly using natural logarithms ($\ln$).

b) Algebraically calculate the exact number of years required for an initial investment to triple if the annual interest rate is $5\%$ ($r = 0.05$). Round your answer to the nearest tenth of a year.

**New question:**

Using $A=Pe^{rt}$ with $r=0.05$, how many years are required for an investment to triple? Round to the nearest tenth.

**Accepted answers:** 22.0, 22.0, 22, 21.97, 21.972

### MATH30-1 #144

**Reason invalid:** Multi-part factoring WR

**Original:**

Consider the quartic polynomial function $P(x) = x^4 - 5x^2 + 4$.

a) Show algebraically that both $(x - 1)$ and $(x + 2)$ are valid factors of $P(x)$.

b) Factor $P(x)$ completely into linear factors and state all of its exact $x$-intercepts.

**New question:**

How many distinct real $x$-intercepts does $P(x)=x^4-5x^2+4$ have? Record the integer.

**Accepted answers:** 4, 4

### MATH30-1 #164

**Reason invalid:** Multi-part arc angle WR

**Original:**

A satellite travels in a circular orbit around a planet. The radius of the orbit is 8000 km. 

a) If the satellite travels along an arc length of 12000 km, calculate its angular displacement, $\theta$, in radians.

b) Convert this angular displacement into degrees. Round your answer to the nearest tenth of a degree.

**New question:**

A satellite orbit has radius $8000$ km and arc length $12000$ km. What is the angular displacement in radians?

**Accepted answers:** 1.5, 1.5, 3/2, 1.50

### MATH30-1 #184

**Reason invalid:** Multi-part sinusoidal modelling WR

**Original:**

The depth of water, $d$ meters, at a seaport harbor varies sinusoidally with time, $t$ hours after midnight. At high tide ($t=2$), the water depth reaches its maximum of 16 meters. At the next low tide ($t=8$), the depth drops to its minimum of 4 meters.

a) Formulate a cosine function in the form $d(t) = a\cos(b(t-c)) + d$ to model this behavior.

b) Algebraically calculate the water depth at 5:00 AM ($t=5$).

**New question:**

Harbor depth is $16$ m at $t=2$ (high tide) and $4$ m at $t=8$ (low tide). Using the cosine model $d(t)=6\cos\left(\frac{\pi}{6}(t-2)\right)+10$, what is the depth in metres at $t=5$?

**Accepted answers:** 10, 10, 10.0

### MATH30-1 #204

**Reason invalid:** Prove identity / state restrictions WR

**Original:**

Consider the equation $\frac{\sin(2x)}{1 + \cos(2x)} = \tan(x)$.

a) State all non-permissible values for this equation within the interval $0 \le x < 2\pi$.

b) Algebraically prove that this equation is an identity for all permissible values.

**New question:**

For $\dfrac{\sin(2x)}{1+\cos(2x)}=\tan(x)$ on $0\le x<2\pi$, how many non-permissible $x$-values are there in the interval? Record the integer.

**Accepted answers:** 2, 2

### MATH30-1 #224

**Reason invalid:** Explain + calculate partitioning WR

**Original:**

A group of 12 volunteers is being split into three distinct working teams. Team A must have 5 members, Team B must have 4 members, and Team C must have 3 members. 

a) Explain why combinations are used to solve this assignment problem rather than permutations.

b) Algebraically calculate the total number of unique ways to partition the volunteers into these three groups.

**New question:**

In how many ways can 12 volunteers be partitioned into teams of sizes 5, 4, and 3 (teams distinct)? Record the integer.

**Accepted answers:** 27720, 27720, 27,720

### MATH30-1 #244

**Reason invalid:** Multi-part binomial expansion WR

**Original:**

Consider the binomial expression $\left(2x^2 - \frac{1}{2x}\right)^6$.

a) Determine the total number of terms in this expansion.

b) Algebraically find the simplified expression for the term that is independent of $x$ (the constant term).

**New question:**

In the expansion of $\left(2x^2-\frac{1}{2x}\right)^6$, what is the constant term? Record as a decimal.

**Accepted answers:** 3.75, 3.75, 15/4, 3.750, 15/4

### MATH30-1 #268

**Reason invalid:** Solve with verification WR

**Original:**

Solve $\sqrt{x + 5} = x - 1$. Show all algebraic steps and verify each potential solution in the original equation.

**New question:**

Solve $\sqrt{x+5}=x-1$. Record the valid solution.

**Accepted answers:** 4, 4

### MATH30-1 #269

**Reason invalid:** Describe transformations WR

**Original:**

Describe the sequence of transformations that maps $y = \sqrt{x}$ onto $y = -2\sqrt{x + 3} - 1$. Include the starting point of the transformed graph.

**New question:**

The graph of $y=-2\sqrt{x+3}-1$ is obtained from $y=\sqrt{x}$. What is the $x$-coordinate of the transformed starting point?

**Accepted answers:** -3, -3

### MATH30-1 #292

**Reason invalid:** Describe asymptotes/domain WR

**Original:**

Given $f(x) = \dfrac{2x}{x - 3}$, determine all asymptotes, intercepts, and the domain. State whether the function has any holes.

**New question:**

For $f(x)=\dfrac{2x}{x-3}$, what is the equation of the vertical asymptote? Enter as x = k.

**Accepted answers:** x = 3, x = 3, x=3, x= 3, x =3, 3

### MATH30-1 #293

**Reason invalid:** Solve rational equation WR (multiple solutions)

**Original:**

Solve $\dfrac{1}{x} + \dfrac{1}{x + 2} = \dfrac{3}{4}$. Show algebraic steps and identify any excluded values.

**New question:**

Solve $\dfrac{1}{x}+\dfrac{1}{x+2}=\dfrac{3}{4}$. Record the positive solution.

**Accepted answers:** 2, 2

### MATH30-1 #294

**Reason invalid:** Construct / justify rational function WR

**Original:**

A rational function has a vertical asymptote at $x = -2$, a horizontal asymptote at $y = 1$, and passes through $(0, 0)$. Write one possible equation and justify each feature.

**New question:**

A rational function has vertical asymptote $x=-2$, horizontal asymptote $y=1$, and passes through $(0,0)$. Enter one possible equation (simplified).

**Accepted answers:** x/(x+2), x/(x+2), x / (x + 2), f(x)=x/(x+2), f(x) = x/(x+2), (x)/(x+2), \frac{x}{x+2}

### BIO30 #354

**Reason invalid:** Explain... (requires subjective/paragraph marking)

**Original:**

Explain how the human body maintains water balance on a hot day when sweating increases, referencing ADH and at least one target organ.

**New question:**

After heavy sweating raises blood osmolarity, which hormone increases water reabsorption in the kidney collecting ducts?

**Accepted answers:** ADH, ADH, adh, antidiuretic hormone, anti-diuretic hormone, vasopressin

### BIO30 #355

**Reason invalid:** Explain... multi-step synaptic description

**Original:**

Explain the events of synaptic transmission at a cholinergic synapse, from the arrival of an action potential at the presynaptic terminal to the response in the postsynaptic cell. Your answer should include at least four distinct steps.

**New question:**

At a cholinergic synapse, which ion enters the presynaptic terminal through voltage-gated channels to trigger vesicle exocytosis of acetylcholine?

**Accepted answers:** Ca2+, Ca2+, Ca^{2+}, calcium, calcium ion, calcium ions, Ca++

### BIO30 #356

**Reason invalid:** Compare... autonomic divisions

**Original:**

Compare the sympathetic and parasympathetic divisions of the autonomic nervous system in terms of general function, one physiological effect on the heart, and one physiological effect on digestion.

**New question:**

Which autonomic division is primarily responsible for fight-or-flight responses such as increased heart rate?

**Accepted answers:** sympathetic, sympathetic, sympathetic nervous system, SNS, sympathetic division

### BIO30 #357

**Reason invalid:** Describe... multi-system glucose regulation

**Original:**

Describe how the nervous and endocrine systems work together to regulate blood glucose levels after a person eats a large carbohydrate meal. Include at least one hormone, one gland, and one nervous system component in your answer.

**New question:**

After a large carbohydrate meal raises blood glucose, which hormone is secreted by pancreatic beta cells to lower blood glucose?

**Accepted answers:** insulin, insulin, Insulin

### BIO30 #358

**Reason invalid:** Compare... rod vs cone

**Original:**

Compare rod and cone cells in terms of light sensitivity, colour detection, and distribution in the retina.

**New question:**

Which photoreceptor cells are more sensitive in dim light and do not detect colour?

**Accepted answers:** rods, rods, rod, rod cells, rod cell

### BIO30 #359

**Reason invalid:** Explain... thyroid feedback

**Original:**

Explain how negative feedback maintains thyroid hormone levels in the body. Include the roles of the hypothalamus, pituitary, thyroid, and at least one hormone in your answer.

**New question:**

Which anterior-pituitary hormone stimulates the thyroid gland to release T3 and T4?

**Accepted answers:** TSH, TSH, tsh, thyroid-stimulating hormone, thyroid stimulating hormone, thyrotropin

### BIO30 #360

**Reason invalid:** Explain... thyroid feedback

**Original:**

Explain how negative feedback regulates thyroid hormone levels. Include TRH, TSH, T3/T4, and the glands involved.

**New question:**

Elevated blood T3/T4 primarily inhibits release of which hypothalamic hormone in the thyroid axis?

**Accepted answers:** TRH, TRH, trh, thyrotropin-releasing hormone, thyrotropin releasing hormone

### BIO30 #361

**Reason invalid:** Explain... pupillary reflex

**Original:**

A researcher measures pupil diameter in dim light ($6$ mm) and bright light ($2$ mm). Explain the reflex pathway responsible for the change and identify which division of the autonomic nervous system mediates the response in bright light.

**New question:**

In bright light, which autonomic division mediates pupil constriction of the iris sphincter?

**Accepted answers:** parasympathetic, parasympathetic, parasympathetic nervous system, PNS, parasympathetic division

### BIO30 #416

**Reason invalid:** Discuss... STS essay prompt

**Original:**

Discuss one ethical, one economic, and one ecological consideration related to the use of hormonal contraceptives in society.

**New question:**

Trace hormones from hormonal contraceptives entering aquatic ecosystems via wastewater raise which type of environmental concern: ethical, economic, or ecological?

**Accepted answers:** ecological, ecological, ecology, environmental, Ecological

### BIO30 #417

**Reason invalid:** Compare... spermatogenesis vs oogenesis

**Original:**

Compare spermatogenesis and oogenesis in terms of timing of completion, number of functional gametes produced per meiosis, and cytoplasmic distribution.

**New question:**

How many functional gametes does one primary spermatocyte typically produce through meiosis?

**Accepted answers:** 4, 4, four

### BIO30 #418

**Reason invalid:** Describe... ovarian cycle hormones

**Original:**

Describe the hormonal regulation of the ovarian cycle from the follicular phase through ovulation. Include the roles of FSH, estrogen, LH, and the corpus luteum.

**New question:**

Which hormone surge immediately triggers ovulation in the ovarian cycle?

**Accepted answers:** LH, LH, lh, luteinizing hormone, luteinising hormone

### BIO30 #419

**Reason invalid:** Explain... teratogen critical periods

**Original:**

Explain why teratogen exposure during organogenesis can cause permanent birth defects while the same exposure after birth may have less severe effects.

**New question:**

During which embryonic process are organs rapidly forming, making teratogen exposure especially likely to cause permanent structural birth defects?

**Accepted answers:** organogenesis, organogenesis, organogenesis period, critical period of organogenesis

### BIO30 #420

**Reason invalid:** Describe... luteal phase

**Original:**

Describe hormonal changes during the luteal phase and explain what happens if fertilization does not occur.

**New question:**

After ovulation, which temporary endocrine structure secretes progesterone to maintain the endometrium?

**Accepted answers:** corpus luteum, corpus luteum, the corpus luteum, Corpus luteum

### BIO30 #421

**Reason invalid:** Explain... three factor types

**Original:**

Explain how cell differentiation and development are influenced by genetic, endocrine, and environmental factors. Provide one specific example for each factor type.

**New question:**

Which class of genes helps establish anterior–posterior body segment identity during development?

**Accepted answers:** Hox genes, Hox genes, hox genes, Hox, homeobox genes, Hox gene

### BIO30 #463

**Reason invalid:** Explain... nondisjunction/trisomy

**Original:**

Explain how nondisjunction during meiosis can lead to trisomy in a zygote. Include which division may be affected and the chromosome number in the resulting gamete.

**New question:**

If nondisjunction produces an n+1 gamete that is fertilized by a normal n gamete, what is the resulting zygote chromosome number in humans (use digit form, e.g. 47)?

**Accepted answers:** 47, 47, 2n+1, trisomy

### BIO30 #464

**Reason invalid:** Describe... prophase I variation

**Original:**

Describe the events of prophase I of meiosis that contribute to genetic variation, naming at least two processes.

**New question:**

Which prophase I process exchanges DNA between non-sister chromatids of homologous chromosomes?

**Accepted answers:** crossing over, crossing over, crossover, crossing-over, genetic recombination, recombination

### BIO30 #465

**Reason invalid:** Compare... mitosis vs meiosis

**Original:**

Compare mitosis and meiosis in terms of purpose, number of divisions, and genetic variation in daughter cells.

**New question:**

How many nuclear divisions occur in meiosis?

**Accepted answers:** 2, 2, two

### BIO30 #466

**Reason invalid:** Explain... tumour suppressor

**Original:**

Explain how a mutation in a tumour suppressor gene such as p53 can contribute to cancer development.

**New question:**

Which tumour-suppressor gene normally pauses the cell cycle for DNA repair or triggers apoptosis when damage is detected?

**Accepted answers:** p53, p53, TP53, tp53, P53

### BIO30 #534

**Reason invalid:** Evaluate... pedigree claim

**Original:**

A student claims a trait showing affected males passing to all daughters but no sons is X-linked dominant. Evaluate this claim using pedigree reasoning.

**New question:**

A trait where affected fathers transmit the trait to all daughters but never to sons is most consistent with which inheritance pattern?

**Accepted answers:** X-linked dominant, X-linked dominant, x-linked dominant, X linked dominant, sex-linked dominant

### BIO30 #535

**Reason invalid:** Describe... DNA replication enzymes

**Original:**

Describe the process of DNA replication, identifying the roles of helicase, primase, DNA polymerase, and ligase.

**New question:**

Which enzyme unwinds the DNA double helix at the replication fork?

**Accepted answers:** helicase, helicase, DNA helicase, Helicase

### BIO30 #536

**Reason invalid:** Explain... CRISPR plus ethics

**Original:**

Explain how CRISPR-Cas9 can be used to edit a specific gene and discuss one ethical consideration.

**New question:**

In CRISPR-Cas9 editing, which molecule directs Cas9 to a matching genomic DNA sequence?

**Accepted answers:** guide RNA, guide RNA, gRNA, sgRNA, guide rna, Guide RNA

### BIO30 #537

**Reason invalid:** Describe... frameshift effect

**Original:**

Describe how a deletion of two base pairs in the middle of an open reading frame can affect the resulting protein.

**New question:**

Deleting two base pairs from the middle of an open reading frame typically causes which class of mutation?

**Accepted answers:** frameshift, frameshift, frameshift mutation, frame-shift, frame shift

### BIO30 #538

**Reason invalid:** Explain... X-linked colour blindness

**Original:**

A couple with normal vision has a colour-blind son. Explain how this pattern is consistent with X-linked recessive inheritance and state the mother's likely genotype.

**New question:**

A couple with normal vision has a colour-blind son. What is the mother’s most likely genotype for an X-linked recessive trait (use carrier notation such as XNXc)?

**Accepted answers:** XNXc, XNXc, X^N X^c, XNXC, carrier, heterozygous carrier, X^N X^c

### BIO30 #539

**Reason invalid:** Explain... central dogma

**Original:**

Explain the central dogma of molecular biology and describe what happens during each of transcription and translation in a eukaryotic cell.

**New question:**

According to the central dogma, DNA is transcribed into which molecule before proteins are made?

**Accepted answers:** RNA, RNA, mRNA, rna, messenger RNA

### BIO30 #540

**Reason invalid:** Distinguish... mutation types

**Original:**

Distinguish between a point mutation, a frameshift mutation, and a chromosomal deletion, giving one consequence of each.

**New question:**

A mutation that changes a single DNA base pair is called what type of mutation?

**Accepted answers:** point mutation, point mutation, point, substitution, base substitution

### BIO30 #541

**Reason invalid:** Explain... PCR + electrophoresis

**Original:**

Explain how gel electrophoresis and PCR could be used together to confirm whether two individuals share a specific DNA marker.

**New question:**

Which technique amplifies a specific DNA region using primers before fragments are compared by gel electrophoresis?

**Accepted answers:** PCR, PCR, pcr, polymerase chain reaction, Polymerase Chain Reaction

### BIO30 #583

**Reason invalid:** Explain... antibiotic selection

**Original:**

Explain how antibiotic use in agriculture can drive natural selection for antibiotic-resistant bacteria in the environment.

**New question:**

Antibiotic use that kills susceptible bacteria while resistant bacteria survive and reproduce is an example of which evolutionary mechanism?

**Accepted answers:** natural selection, natural selection, selection, directional selection

### BIO30 #584

**Reason invalid:** Explain... microevolution mechanisms

**Original:**

Explain how gene flow, genetic drift, and natural selection can each cause allele frequency changes in a population, providing one example of each.

**New question:**

Random change in allele frequencies due to chance in a small population is called what?

**Accepted answers:** genetic drift, genetic drift, drift, founder effect, bottleneck effect

### BIO30 #585

**Reason invalid:** Predict... trophic cascade essay

**Original:**

A lake ecosystem loses its top predator due to overfishing. Predict two ecological changes that may follow and explain them using community ecology concepts.

**New question:**

Loss of a lake’s top predator leading to increases in herbivores and declines in producers is an example of which ecological concept?

**Accepted answers:** trophic cascade, trophic cascade, trophic cascades, cascade, top-down control

### BIO30 #586

**Reason invalid:** Describe... three impacts essay

**Original:**

Describe three ways human activities can reduce biodiversity in Alberta ecosystems and propose one scientifically sound mitigation strategy for each.

**New question:**

Connecting fragmented habitat patches with strips of habitat so wildlife can move between them is an example of which mitigation strategy?

**Accepted answers:** wildlife corridors, wildlife corridors, wildlife corridor, habitat corridor, habitat corridors, ecological corridors, corridors

