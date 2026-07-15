"""Unit B: Electrochemical Changes — original Chemistry 30 questions."""

from .helpers import mc, nr

TOPIC = "Electrochemical Changes"


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
            "Oxidation is defined operationally as",
            "loss of electrons by a species",
            ["gain of electrons by a species", "gain of protons only without electron transfer", "decrease in mass of the solution"],
            "Operational definition: oxidation = electron loss (OIL).",
            "Students confuse oxidation with oxygen addition only (theoretical definition context).",
            "B1.1k", "Defining oxidation operationally", "Easy", 60,
        ),
        (
            "Reduction is defined theoretically as",
            "gain of electrons by a species",
            ["loss of electrons by a species", "loss of oxygen atoms in all cases", "increase in oxidation number always"],
            "Theoretical definition: reduction = electron gain (RIG).",
            "Students reverse oxidation and reduction definitions.",
            "B1.1k", "Defining reduction theoretically", "Easy", 60,
        ),
        (
            "In the reaction $2\\text{H}_2\\text{O}_2(l) \\rightarrow 2\\text{H}_2\\text{O}(l) + \\text{O}_2(g)$, hydrogen peroxide undergoes",
            "disproportionation",
            ["simple precipitation", "esterification", "neutralization only"],
            "H$_2$O$_2$ is both oxidized (to O$_2$) and reduced (to H$_2$O) — disproportionation.",
            "Students classify all decomposition reactions as simple redox without disproportionation.",
            "B1.2k", "Identifying disproportionation in H₂O₂ decomposition", "Medium", 85,
        ),
        (
            "The oxidizing agent in a redox reaction is the species that",
            "is reduced (gains electrons)",
            ["is oxidized (loses electrons)", "always appears on the left side only", "has the lowest oxidation number"],
            "Oxidizing agent accepts electrons and is itself reduced.",
            "Students select the species that is oxidized instead of the oxidizing agent.",
            "B1.2k", "Identifying the oxidizing agent", "Easy", 70,
        ),
        (
            "The reducing agent in a redox reaction is the species that",
            "is oxidized (loses electrons)",
            ["is reduced (gains electrons)", "always a metal cation", "catalyzes without electron transfer"],
            "Reducing agent donates electrons and is itself oxidized.",
            "Students confuse reducing agent with oxidizing agent.",
            "B1.2k", "Identifying the reducing agent", "Easy", 70,
        ),
        (
            "Cellular respiration involves glucose as a",
            "reducing agent that is oxidized",
            ["oxidizing agent that is reduced", "catalyst that is unchanged", "spectator ion"],
            "Glucose donates electrons (oxidized); O$_2$ is the oxidizing agent (reduced).",
            "Students think O$_2$ is the reducing agent because it is consumed.",
            "B1.4k", "Identifying reducing agent in cellular respiration", "Medium", 85,
        ),
        (
            "Rusting of iron in moist air involves iron acting as",
            "the reducing agent (oxidized to Fe$^{3+}$)",
            ["the oxidizing agent (reduced)", "an inert spectator metal", "a catalyst only"],
            "Iron loses electrons to oxygen/water — iron is oxidized (reducing agent).",
            "Students think oxygen is reduced so iron must also be reduced.",
            "B1.4k", "Identifying redox roles in iron corrosion", "Medium", 80,
        ),
        (
            "Cathodic protection of an iron pipeline uses a more reactive metal to",
            "act as a sacrificial anode that oxidizes instead of the iron",
            ["coat iron with plastic permanently", "reduce all oxygen in the atmosphere", "increase iron's oxidation number"],
            "Sacrificial zinc/magnesium anode corrodes preferentially, protecting iron cathode.",
            "Students think cathodic protection involves painting only.",
            "B1.1sts", "Explaining cathodic corrosion protection", "Medium", 85,
        ),
        (
            "A standard reduction potential table lists half-reactions with",
            "reduction potentials relative to the standard hydrogen electrode (0 V)",
            ["oxidation potentials only with no reference electrode", "enthalpy changes in kJ/mol exclusively", "equilibrium constants without voltage"],
            "All E° values are reduction potentials vs SHE at 25°C and 1.0 mol/L.",
            "Students think listed values are oxidation potentials or arbitrary numbers.",
            "B2.5k", "Explaining reference for standard reduction potentials", "Medium", 80,
        ),
        (
            "In a voltaic (galvanic) cell, the anode is the electrode where",
            "oxidation occurs",
            ["reduction occurs", "only cations are reduced", "external power is supplied"],
            "Anode = oxidation; cathode = reduction. In voltaic cells, anode is negative.",
            "Students associate anode with positive electrode in all cell types.",
            "B2.1k", "Defining anode in electrochemical cells", "Easy", 65,
        ),
        (
            "In an electrolytic cell, the cathode is the electrode where",
            "reduction occurs",
            ["oxidation occurs", "spontaneous reaction drives current", "no ions move"],
            "Cathode = reduction in both voltaic and electrolytic cells.",
            "Students think cathode is always positive; in electrolytic cells cathode is negative.",
            "B2.1k", "Defining cathode in electrochemical cells", "Easy", 65,
        ),
        (
            "A voltaic cell requires a salt bridge or porous barrier to",
            "maintain charge neutrality between half-cells",
            ["supply external electrical power", "prevent all ion movement", "convert chemical energy to heat only"],
            "Salt bridge allows ion migration to balance charge as redox proceeds.",
            "Students think salt bridge participates in the redox reaction directly.",
            "B2.1k", "Explaining salt bridge function in voltaic cells", "Medium", 80,
        ),
        (
            "An electrolytic cell differs from a voltaic cell because an electrolytic cell",
            "requires an external power source to drive a non-spontaneous reaction",
            ["produces spontaneous electrical current without external input", "never involves oxidation at any electrode", "cannot be used for electroplating"],
            "Electrolytic cells use external voltage to force non-spontaneous redox.",
            "Students think all electrochemical cells are spontaneous.",
            "B2.2k", "Distinguishing electrolytic from voltaic cells", "Medium", 85,
        ),
        (
            "During electrolysis of aqueous NaCl, the chloride anomaly means",
            "Cl$^-$ is oxidized before H$_2$O despite E° suggesting water oxidation is possible",
            ["chloride ions are never oxidized under any conditions", "sodium metal forms at the anode", "no overvoltage is ever required"],
            "Overvoltage for water oxidation is higher, so Cl$^-$ oxidizes first at the anode.",
            "Students rely solely on E° values without considering overvoltage.",
            "B2.4k", "Explaining chloride anomaly in brine electrolysis", "Hard", 120,
        ),
        (
            "As a voltaic cell discharges and approaches equilibrium, the cell voltage",
            "decreases toward zero",
            ["increases without limit", "remains constant at E°cell indefinitely", "becomes equal to the Nernst equation value at 0°C only"],
            "Reactant depletion reduces driving force; at equilibrium no net current flows.",
            "Students think voltage stays at E°cell throughout discharge.",
            "B2.5k", "Predicting voltage change as voltaic cell discharges", "Medium", 90,
        ),
        (
            "Faraday's law relates the mass of substance deposited during electrolysis to",
            "the quantity of electric charge passed (current × time)",
            ["only the voltage of the power supply", "the activation energy of the reaction", "the equilibrium constant Kc"],
            "Mass $\\propto Q = I \\times t$ through molar charge (Faraday constant).",
            "Students use voltage alone without current and time.",
            "B2.8k", "Stating Faraday's law relationship", "Medium", 85,
        ),
        (
            "In line notation $\\text{Zn}(s)\\ |\\ \\text{Zn}^{2+}(aq)\\ \\|\\ \\text{Cu}^{2+}(aq)\\ |\\ \\text{Cu}(s)$, the single vertical line at the far left indicates",
            "a phase boundary between solid Zn and Zn$^{2+}$ solution",
            ["the salt bridge between half-cells", "the external wire connection", "a porous barrier only"],
            "Single lines = phase boundaries; double line = salt bridge.",
            "Students confuse single phase boundaries with salt bridge (double line).",
            "B2.3k", "Interpreting electrochemical cell line notation", "Medium", 90,
        ),
        (
            "A fuel cell converts chemical energy of a fuel directly into",
            "electrical energy through continuous redox reactions",
            ["nuclear energy without any chemical change", "mechanical energy via pistons only", "light energy without electron transfer"],
            "Fuel cells are voltaic systems with continuous fuel/oxidant supply.",
            "Students confuse fuel cells with heat engines (combustion only).",
            "B2.1sts", "Describing fuel cell energy conversion", "Easy", 70,
        ),
        (
            "Electroplating jewelry with silver uses an electrolytic cell where the jewelry is the",
            "cathode where Ag$^+$ ions are reduced to Ag metal",
            ["anode where silver dissolves", "salt bridge only", "power supply itself"],
            "Object to be plated is cathode; silver anode supplies Ag$^+$ ions.",
            "Students reverse anode and cathode roles in electroplating.",
            "B2.1sts", "Explaining electroplating cell electrode roles", "Medium", 85,
        ),
        (
            "Best practice for accurate volumetric analysis in a redox titration requires",
            "a volumetric pipette to deliver the analyte volume",
            ["a graduated cylinder for all precise transfers", "estimating volumes by eye", "using a beaker instead of a flask"],
            "Volumetric pipettes deliver precise volumes; graduated cylinders are less precise.",
            "Students use graduated cylinders for titration aliquots (not best practice).",
            "B1.2s", "Selecting glassware for redox volumetric analysis", "Easy", 65,
        ),
        (
            "The oxidation number of oxygen in hydrogen peroxide (H$_2$O$_2$) is",
            "$-1$",
            ["$-2$ as in most compounds", "$+1$", "$0$ as in an element"],
            "Peroxides assign O an oxidation number of $-1$, not the usual $-2$.",
            "Students always assign $-2$ to oxygen regardless of compound class.",
            "B1.7k", "Assigning oxidation number of oxygen in peroxides", "Medium", 85,
        ),
        (
            "The oxidation number of hydrogen in sodium hydride (NaH) is",
            "$-1$",
            ["$+1$ as in most compounds", "$0$", "$+2$"],
            "Metal hydrides (NaH) assign H an oxidation number of $-1$.",
            "Students always assign $+1$ to hydrogen.",
            "B1.7k", "Assigning oxidation number of hydrogen in hydrides", "Medium", 85,
        ),
        (
            "When balancing a redox equation in acidic solution, H$^+$(aq) and H$_2$O(l) may be added to",
            "balance oxygen and hydrogen atoms after electron balance",
            ["replace all spectator ions with sodium", "eliminate the need for half-reactions", "change the oxidation state of nitrogen only"],
            "Acidic balancing uses H$^+$ and H$_2$O to complete atom balance after e$^-$ balance.",
            "Students add OH$^-$ in acidic medium or skip atom balancing.",
            "B1.7k", "Balancing redox equations in acidic medium", "Hard", 130,
        ),
        (
            "A species with the highest (most positive) standard reduction potential is the strongest",
            "oxidizing agent",
            ["reducing agent", "spectator ion", "catalyst"],
            "Higher E° (reduction) = greater tendency to gain electrons = stronger oxidizing agent.",
            "Students select lowest E° as strongest oxidizing agent.",
            "B1.5k", "Relating E° to oxidizing agent strength", "Medium", 85,
        ),
        (
            "Predicting whether Zn$^{2+}$(aq) can oxidize Cu(s) using standard potentials, the reaction is",
            "non-spontaneous (Cu cannot reduce Zn$^{2+}$ under standard conditions)",
            ["spontaneous with Cu oxidizing Zn$^{2+}$", "impossible to determine from E° values", "always at equilibrium"],
            "Cu(s) + Zn$^{2+}$(aq) has E°cell < 0 — non-spontaneous; reverse reaction is spontaneous.",
            "Students assume any metal reacts with any metal ion.",
            "B1.6k", "Predicting redox spontaneity from standard potentials", "Medium", 95,
        ),
        (
            "Redox reactions used in water treatment plants may involve",
            "chlorine oxidizing harmful bacteria and organic contaminants",
            ["only precipitation with no electron transfer", "esterification of dissolved salts", "polymerization of water molecules"],
            "Chlorine acts as oxidizing agent disinfecting water — industrial redox application.",
            "Students think water treatment uses only physical filtration.",
            "B1.2sts", "Identifying redox in water treatment industry", "Easy", 70,
        ),
        (
            "In a labelled voltaic cell diagram, the observation at the cathode during discharge often includes",
            "deposition of metal or reduction of ions (mass increase on cathode)",
            ["dissolution of the cathode metal always", "release of oxygen gas at cathode always", "no observable change ever"],
            "Cathode reduction often deposits metal (e.g., Cu on copper cathode).",
            "Students predict gas evolution at both electrodes in all cells.",
            "B2.1s", "Predicting cathode observations in voltaic cells", "Medium", 90,
        ),
        (
            "The Nernst equation is",
            "beyond the scope of Chemistry 30 for calculating non-standard potentials",
            ["required for all standard cell potential calculations", "used instead of Faraday's law for mass", "the method for balancing all organic equations"],
            "Alberta POS excludes Nernst; students need qualitative understanding of concentration effects.",
            "Students attempt Nernst calculations on diploma-style items.",
            "B2.5k", "Recognizing Nernst equation scope limits", "Easy", 60,
        ),
    ])

    q += [
        nr(
            "What is the oxidation number of sulfur in $\\text{SO}_4^{2-}$? Record as a signed integer.",
            "-6",
            "Let S = $x$: $x + 4(-2) = -2$, so $x = -6$.",
            "Students forget the overall ion charge when summing oxidation numbers.",
            topic=TOPIC, outcome_code="B1.7k",
            skill_tested="Calculating oxidation number in polyatomic ion",
            difficulty="Medium", estimated_time_seconds=100,
        ),
        nr(
            "A voltaic cell has $E°_{cathode} = +0.34\\ \\text{V}$ and $E°_{anode} = -0.76\\ \\text{V}$. "
            "Calculate $E°_{cell}$ in V to two decimal places.",
            "1.10",
            "$E°_{cell} = E°_{cathode} - E°_{anode} = 0.34 - (-0.76) = 1.10\\ \\text{V}$.",
            "Students add both values or subtract in wrong order.",
            topic=TOPIC, outcome_code="B2.6k",
            skill_tested="Calculating standard cell potential",
            difficulty="Medium", estimated_time_seconds=100,
        ),
        nr(
            "During electrolysis, a current of $2.50\\ \\text{A}$ flows for $1930\\ \\text{s}$. "
            "How many moles of electrons pass through the circuit? "
            "Use $F = 96500\\ \\text{C/mol}$. Express to two decimal places.",
            "0.05",
            "$Q = It = 2.50 \\times 1930 = 4825\\ \\text{C}$. Moles e$^-$ = $4825/96500 = 0.050$.",
            "Students forget to convert charge to moles using Faraday constant.",
            topic=TOPIC, outcome_code="B2.8k",
            skill_tested="Calculating moles of electrons from current and time",
            difficulty="Hard", estimated_time_seconds=150,
        ),
        nr(
            "In a redox titration, $25.00\\ \\text{mL}$ of $0.0200\\ \\text{mol/L}$ $\\text{Fe}^{2+}$ "
            "reacts with $\\text{MnO}_4^-$ in acidic solution (1:1 mole ratio for Fe$^{2+}$:MnO$_4^-$). "
            "How many millimoles of $\\text{MnO}_4^-$ were required? Express to two decimal places.",
            "0.50",
            "mmol Fe$^{2+}$ = $25.00 \\times 0.0200 = 0.50\\ \\text{mmol}$ = mmol MnO$_4^-$.",
            "Students forget to convert mL to L or use wrong stoichiometric ratio.",
            topic=TOPIC, outcome_code="B1.8k",
            skill_tested="Calculating titrant amount in redox titration",
            difficulty="Medium", estimated_time_seconds=120,
        ),
        nr(
            "What is the oxidation number of carbon in $\\text{CO}_3^{2-}$? Record as a signed integer.",
            "4",
            "$x + 3(-2) = -2$, so $x = +4$.",
            "Students assign $-4$ or forget carbonate ion charge.",
            topic=TOPIC, outcome_code="B1.7k",
            skill_tested="Calculating oxidation number of carbon in carbonate",
            difficulty="Easy", estimated_time_seconds=80,
        ),
    ]

    return q
