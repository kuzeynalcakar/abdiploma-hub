"""Unit D: Chemical Equilibrium Focusing on Acid-Base Systems — original Chemistry 30 questions."""

from .helpers import mc, nr

TOPIC = "Chemical Equilibrium Focusing on Acid-Base Systems"


def _batch_mc(items):
    return [
        mc(q, a, d, e, m, topic=TOPIC, outcome_code=oc, skill_tested=s,
           difficulty=diff, estimated_time_seconds=t)
        for q, a, d, e, m, oc, s, diff, t in items
    ]


def questions():
    q = []

    q += _batch_mc([
        (
            "A chemical system is at equilibrium when",
            "forward and reverse reaction rates are equal in a closed system",
            ["all reactants are completely consumed", "the reaction has stopped at the molecular level", "mass is no longer conserved"],
            "Equilibrium: equal rates, closed system, constant macroscopic properties.",
            "Students think reactions stop entirely rather than continuing at equal rates.",
            "D1.1k", "Defining chemical equilibrium criteria", "Easy", 65,
        ),
        (
            "Conservation of mass in a closed container",
            "does not by itself prove equilibrium has been reached",
            ["guarantees the system is at equilibrium", "only applies to open systems", "prevents any reversible reactions"],
            "Mass is conserved in closed systems regardless of equilibrium state.",
            "Students equate mass conservation with equilibrium.",
            "D1.1k", "Distinguishing mass conservation from equilibrium", "Medium", 80,
        ),
        (
            "According to Le Châtelier's principle, increasing the concentration of a product will shift equilibrium",
            "toward reactants (left)",
            ["toward more products (right)", "without any shift occurring", "only if a catalyst is added"],
            "Adding product favours reverse reaction to partially offset the increase.",
            "Students think adding product always increases product concentration further.",
            "D1.3k", "Predicting Le Châtelier shift from product addition", "Easy", 70,
        ),
        (
            "Adding an inert gas at constant volume to a gaseous equilibrium system",
            "does not shift equilibrium (no change in partial pressures of reactants/products)",
            ["always shifts toward products", "always increases Kc value", "decreases temperature automatically"],
            "Inert gas at constant V does not change concentrations of reacting species.",
            "Students think any pressure increase shifts equilibrium.",
            "D1.3k", "Predicting effect of inert gas at constant volume", "Medium", 90,
        ),
        (
            "Decreasing the volume of a gaseous equilibrium container (with no temperature change) shifts equilibrium toward",
            "the side with fewer moles of gas",
            ["the side with more moles of gas always", "neither side in all cases", "only the solid product side"],
            "Volume decrease increases pressure; system shifts to reduce gas mole count.",
            "Students think volume change always favours products.",
            "D1.3k", "Predicting Le Châtelier shift from volume decrease", "Medium", 85,
        ),
        (
            "For an exothermic gaseous equilibrium, increasing temperature will",
            "decrease the value of Kc",
            ["increase Kc", "have no effect on Kc", "always double Kc"],
            "Only temperature changes K; exothermic + heat favours reactants, lowering K.",
            "Students think pressure or concentration changes alter K.",
            "D1.3k", "Relating temperature increase to Kc for exothermic reaction", "Medium", 90,
        ),
        (
            "In the equilibrium expression for $\\text{CO}(g) + 2\\text{H}_2(g) \\rightleftharpoons \\text{CH}_3\\text{OH}(g)$, the denominator includes",
            "[CO] and [H$_2$]$^2$",
            ["[CH$_3$OH] only", "solid catalyst concentration", "[H$_2$O(l)]"],
            "$K_c = [\\text{CH}_3\\text{OH}]/([\\text{CO}][\\text{H}_2]^2)$ — products over reactants with stoichiometric powers.",
            "Students invert the expression or omit exponents.",
            "D1.4k", "Writing Kc expression for gaseous equilibrium", "Medium", 95,
        ),
        (
            "Pure solids are excluded from Kc expressions because",
            "their concentration (density) does not change significantly",
            ["solids cannot participate in equilibrium", "solids are always products", "solids have zero mass"],
            "Heterogeneous equilibria omit pure liquids and solids from K expressions.",
            "Students include solid concentrations in K expressions.",
            "D1.4k", "Explaining exclusion of solids from Kc", "Easy", 70,
        ),
        (
            "A Brønsted-Lowry acid is defined as a",
            "proton (H$^+$) donor",
            ["proton acceptor", "electron donor only", "hydroxide ion source always"],
            "BL acid donates H$^+$; base accepts H$^+$.",
            "Students confuse Arrhenius (OH$^-$ producer) with Brønsted-Lowry definitions.",
            "D1.5k", "Defining Brønsted-Lowry acid", "Easy", 60,
        ),
        (
            "In the reaction $\\text{NH}_4^+(aq) + \\text{H}_2\\text{O}(l) \\rightleftharpoons \\text{NH}_3(aq) + \\text{H}_3\\text{O}^+(aq)$, the conjugate base of NH$_4^+$ is",
            "NH$_3$",
            ["H$_2$O", "H$_3$O$^+$", "NH$_4^+$"],
            "NH$_4^+$ donates H$^+$ to form NH$_3$ — conjugate base is NH$_3$.",
            "Students select H$_3$O$^+$ or water as the conjugate base of ammonium.",
            "D1.7k", "Identifying conjugate base of ammonium ion", "Medium", 85,
        ),
        (
            "HCO$_3^-$(aq) is amphiprotic because it can",
            "act as both a Brønsted-Lowry acid and base",
            ["only donate protons", "only accept protons", "neither donate nor accept protons"],
            "HCO$_3^-$ can donate H$^+$ (to form CO$_3^{2-}$) or accept H$^+$ (to form H$_2$CO$_3$).",
            "Students think amphiprotic species are only acids or only bases.",
            "D1.7k", "Explaining amphiprotic nature of bicarbonate", "Medium", 85,
        ),
        (
            "A buffer solution effectively resists pH change when",
            "small amounts of strong acid or base are added to a mixture of weak acid and conjugate base",
            ["large amounts of strong acid completely replace the buffer", "only strong acids are present with no conjugate pair", "the solution contains only strong acid and strong base"],
            "Buffer = weak acid/base + conjugate partner in comparable amounts.",
            "Students think any acidic solution is a buffer.",
            "D1.8k", "Defining buffer solution conditions", "Medium", 85,
        ),
        (
            "At the equivalence point of a strong acid–strong base titration, the pH is",
            "7 (neutral)",
            ["greater than 7 always", "less than 7 always", "equal to the pKa of the indicator only"],
            "Strong acid + strong base → neutral salt; pH = 7 at equivalence (no hydrolysis).",
            "Students think all equivalence points have pH = 7.",
            "D1.3s", "Predicting pH at SA/SB equivalence point", "Easy", 70,
        ),
        (
            "At the equivalence point of a weak acid–strong base titration, the pH is",
            "greater than 7 (basic)",
            ["equal to 7", "less than 7", "exactly 0"],
            "Conjugate base of weak acid hydrolyzes water, producing OH$^-$ — pH > 7.",
            "Students apply pH = 7 to all titration equivalence points.",
            "D1.3s", "Predicting pH at WA/SB equivalence point", "Medium", 90,
        ),
        (
            "The flat region before the steep rise on a weak acid–strong base titration curve (not at equivalence) represents",
            "a buffer region",
            ["excess strong base only", "the endpoint of any indicator always", "complete neutralization with pH = 7"],
            "Buffer region: weak acid and conjugate base coexist in similar concentrations.",
            "Students label any flat region as buffering, including post-equivalence excess base.",
            "D1.8k", "Identifying buffer region on titration curve", "Hard", 110,
        ),
        (
            "The relationship $K_a \\times K_b = K_w$ applies to",
            "a conjugate acid-base pair at a given temperature",
            ["any two unrelated acids in solution", "only strong acids and strong bases", "solid precipitates in heterogeneous equilibria"],
            "For conjugate pairs: $K_a \\cdot K_b = K_w$ (at 25°C, $K_w = 1.0 \\times 10^{-14}$).",
            "Students multiply Ka of any two random acids.",
            "D2.2k", "Applying Ka × Kb = Kw to conjugate pairs", "Medium", 90,
        ),
        (
            "The approximation method for weak acid pH is valid when",
            "initial acid concentration is at least 1000 times greater than $K_a$",
            ["$K_a$ exceeds initial concentration", "the acid is 100% ionized", "a buffer is always present"],
            "Large C$_0$/K$_a$ ratio allows neglecting x in denominator of ICE table.",
            "Students use approximation when C$_0$ ≈ K$_a$ (invalid).",
            "D2.3k", "Stating validity condition for weak acid approximation", "Hard", 110,
        ),
        (
            "The Haber-Bosch process for ammonia synthesis is an industrial application of",
            "chemical equilibrium principles (high pressure, moderate temperature, catalyst)",
            ["only electrochemical cells", "organic polymerization exclusively", "nuclear transmutation"],
            "Haber process optimizes N$_2$ + 3H$_2$ ⇌ 2NH$_3$ yield using Le Châtelier and kinetics.",
            "Students do not connect industrial synthesis to equilibrium shifts.",
            "D1.3sts", "Linking Haber process to equilibrium principles", "Medium", 85,
        ),
        (
            "Buffers in blood plasma help maintain pH near 7.4 by",
            "resisting pH changes from metabolic acids and bases (e.g., carbonic acid/bicarbonate system)",
            ["eliminating all CO$_2$ from the body instantly", "converting all acids to strong bases", "preventing any chemical reactions in blood"],
            "Bicarbonate buffer system is a key physiological equilibrium application.",
            "Students think buffers eliminate all pH variation completely.",
            "D1.1sts", "Explaining blood buffer physiological role", "Medium", 85,
        ),
        (
            "The equivalence point in a titration is defined as",
            "the point where reactants are stoichiometrically equivalent",
            ["the point where the indicator changes colour always", "the point where pH = 7 in all cases", "the midpoint of the buffer region only"],
            "Equivalence = stoichiometric completion; endpoint = indicator colour change (may differ slightly).",
            "Students equate equivalence point with endpoint or pH 7 universally.",
            "D1.3s", "Distinguishing equivalence point from endpoint", "Easy", 65,
        ),
        (
            "For $\\text{CH}_3\\text{COOH}(aq) + \\text{H}_2\\text{O}(l) \\rightleftharpoons \\text{CH}_3\\text{COO}^-(aq) + \\text{H}_3\\text{O}^+(aq)$, the Kc expression includes",
            "[CH$_3$COOH] in the denominator and [CH$_3$COO$^-$][H$_3$O$^+$] in the numerator (H$_2$O omitted)",
            ["[H$_2$O] raised to the first power in the denominator", "only [CH$_3$COOH] in the numerator", "[CH$_3$COOH] in the numerator"],
            "Aqueous acid equilibrium: omit pure liquid water; include aqueous species.",
            "Students include H$_2$O(l) or invert the expression.",
            "D1.4k", "Writing Kc for weak acid dissociation in water", "Medium", 90,
        ),
        (
            "Adding a catalyst to a system at equilibrium",
            "speeds attainment of equilibrium but does not shift equilibrium position or change Kc",
            ["shifts equilibrium toward products", "increases Kc value", "decreases activation energy of products only permanently"],
            "Catalysts affect rate, not thermodynamic position or K.",
            "Students think catalysts favour products or change K.",
            "D1.3k", "Predicting catalyst effect on equilibrium", "Easy", 65,
        ),
        (
            "If pH = 3.00, the hydronium ion concentration [H$_3$O$^+$] is",
            "$1.0 \\times 10^{-3}$ mol/L",
            ["$3.0$ mol/L", "$1.0 \\times 10^{-11}$ mol/L", "$0.30$ mol/L"],
            "pH = -log[H$_3$O$^+$]; [H$_3$O$^+$] = $10^{-3.00} = 1.0 \\times 10^{-3}$ mol/L.",
            "Students use pH value directly as concentration or invert the log.",
            "D2.1k", "Converting pH to hydronium concentration", "Easy", 70,
        ),
        (
            "At 25°C, if pOH = 5.00, then pH equals",
            "9.00",
            ["5.00", "14.00", "7.00 always"],
            "pH + pOH = 14 (at 25°C); pH = 14 - 5 = 9.",
            "Students think pH = pOH always or forget to subtract from 14.",
            "D2.1k", "Calculating pH from pOH at 25°C", "Easy", 65,
        ),
        (
            "A monoprotic acid donates",
            "one proton per acid molecule in a single equilibrium step",
            ["two protons always", "no protons (only accepts them)", "one proton only in basic solution"],
            "Monoprotic: one ionizable H$^+$ (e.g., HCl, CH$_3$COOH).",
            "Students confuse monoprotic with diprotic (H$_2$SO$_4$ first proton).",
            "D1.6k", "Defining monoprotic acid behaviour", "Easy", 60,
        ),
        (
            "Removing gaseous product from an equilibrium system at constant temperature will shift equilibrium",
            "toward products (right) to replace what was removed",
            ["toward reactants (left)", "without any shift", "only if Kc decreases"],
            "Removing product is equivalent to decreasing product concentration — shift right.",
            "Students think removing product shifts left.",
            "D1.3k", "Predicting shift when gaseous product is removed", "Medium", 80,
        ),
        (
            "Carbon dioxide escaping from an open carbonated beverage illustrates",
            "equilibrium shift as CO$_2$(g) leaves the open system",
            ["a closed system at constant equilibrium forever", "only an irreversible nuclear reaction", "buffer action maintaining constant CO$_2$ pressure"],
            "Open bottle: CO$_2$ escapes, decreasing dissolved CO$_2$, shifting dissolution equilibrium.",
            "Students do not connect everyday phenomena to Le Châtelier.",
            "D1.1sts", "Applying equilibrium to open carbonated beverage", "Easy", 70,
        ),
    ])

    q += [
        nr(
            "What is the pH of a solution with $[\\text{H}_3\\text{O}^+] = 1.0 \\times 10^{-4}$ mol/L? "
            "Express to two decimal places.",
            "4.00",
            "pH = $-\\log(1.0 \\times 10^{-4}) = 4.00$.",
            "Students report $10^{-4}$ directly as pH or use positive exponent.",
            topic=TOPIC, outcome_code="D2.1k",
            skill_tested="Calculating pH from hydronium concentration",
            difficulty="Easy", estimated_time_seconds=70,
        ),
        nr(
            "At 25°C, $K_w = 1.0 \\times 10^{-14}$. What is the pOH of pure water? Express to two decimal places.",
            "7.00",
            "Neutral water: pH = 7, so pOH = 7 also.",
            "Students report 14 or 0 instead of 7.",
            topic=TOPIC, outcome_code="D2.1k",
            skill_tested="Determining pOH of neutral water",
            difficulty="Easy", estimated_time_seconds=60,
        ),
        nr(
            "A weak acid has $K_a = 1.8 \\times 10^{-5}$. What is $K_b$ for its conjugate base at 25°C? "
            "Express in scientific notation as the coefficient to two significant figures (e.g., if $5.6 \\times 10^{-10}$, record 5.6).",
            "5.6",
            "$K_b = K_w/K_a = 1.0 \\times 10^{-14}/(1.8 \\times 10^{-5}) = 5.6 \\times 10^{-10}$.",
            "Students multiply Ka × Kb instead of dividing Kw by Ka.",
            topic=TOPIC, outcome_code="D2.2k",
            skill_tested="Calculating Kb from Ka using Kw",
            difficulty="Medium", estimated_time_seconds=120,
        ),
        nr(
            "For $\\text{N}_2(g) + 3\\text{H}_2(g) \\rightleftharpoons 2\\text{NH}_3(g)$ at equilibrium, "
            "$[\\text{N}_2] = 0.50\\ \\text{mol/L}$, $[\\text{H}_2] = 1.5\\ \\text{mol/L}$, and "
            "$[\\text{NH}_3] = 0.20\\ \\text{mol/L}$. Calculate $K_c$ to two decimal places.",
            "0.02",
            "$K_c = (0.20)^2/(0.50 \\times 1.5^3) = 0.04/1.6875 = 0.024 \\approx 0.02$.",
            "Students forget to cube [H$_2$] or invert the expression.",
            topic=TOPIC, outcome_code="D2.3k",
            skill_tested="Calculating Kc from equilibrium concentrations",
            difficulty="Hard", estimated_time_seconds=150,
        ),
        nr(
            "A $0.010\\ \\text{mol/L}$ weak acid solution has $[\\text{H}_3\\text{O}^+] = 1.0 \\times 10^{-3}\\ \\text{mol/L}$. "
            "What is the percent ionization? Express to the nearest whole number.",
            "10",
            "% ionization = $(1.0 \\times 10^{-3}/0.010) \\times 100 = 10\\%$.",
            "Students use pH directly as percent ionization.",
            topic=TOPIC, outcome_code="D2.2k",
            skill_tested="Calculating percent ionization from hydronium and initial concentration",
            difficulty="Medium", estimated_time_seconds=110,
        ),
    ]

    return q
