"""Independently recompute every SCI10 NR answer key from its stem numbers.

For each NR question, try to recognize the calculation type from the stem and
recompute the expected answer, then compare against the stored key. Anything
that cannot be auto-recomputed is listed as 'manual' for human review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BANK = Path(__file__).resolve().parents[2] / "questions.json" / "science10_questions_final.json"

ATOMIC = {"H": 1, "C": 12, "N": 14, "O": 16, "Na": 23, "S": 32, "Cl": 35.5, "Ca": 40, "Mg": 24}

MOLAR_MASS = {
    "(NH$_4$)$_2$SO$_4$": 132, "CO$_2$": 44, "CO2": 44, "NaCl": 58.5, "MgO": 40,
    "CH4": 16, "H2O": 18, "NH3": 17, "CaCO3": 100, "C6H12O6": 180, "H2SO4": 98,
    "Ca(OH)$_2$": 74,
}


def nums(text: str) -> list[float]:
    # strip LaTeX scientific like 3.01 \times 10^{23}
    vals = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*\\times\s*10\^\{?(-?\d+)\}?", text):
        vals.append(float(m.group(1)) * 10 ** int(m.group(2)))
    tmp = re.sub(r"\d+(?:\.\d+)?\s*\\times\s*10\^\{?-?\d+\}?", " ", text)
    for m in re.finditer(r"-?\d+(?:\.\d+)?", tmp):
        vals.append(float(m.group()))
    return vals


def close(a: float, b: float, tol: float = 0.05) -> bool:
    return abs(a - b) <= tol + tol * max(abs(a), abs(b))


def recompute(q: dict):
    t = q["question_text"]
    low = t.lower()
    key = float(q["answer"]) if re.fullmatch(r"-?\d+(?:\.\d+)?", (q.get("answer") or "").strip()) else None
    n = nums(t)

    # moles = mass / molar mass  (both given explicitly) -- check before molar-mass lookup
    if ("how many moles" in low or "amount of" in low) and "molar mass" in low:
        mass = re.search(r"in (\d+(?:\.\d+)?)\s*g", low) or re.search(r"mass of (\d+(?:\.\d+)?)", low)
        mm = re.search(r"molar mass[^=]*=\s*(\d+(?:\.\d+)?)", low)
        if mass and mm:
            return round(float(mass.group(1)) / float(mm.group(1)), 1)
    # mass from moles: moles * molar mass  (check before molar-mass lookup)
    if "what mass" in low and "mol" in low and "molar mass" in low:
        mol = re.search(r"obtain (\d+(?:\.\d+)?)\s*mol", low)
        mm = re.search(r"molar mass[^0-9]*=?\s*(\d+(?:\.\d+)?)", low)
        if mol and mm:
            return round(float(mol.group(1)) * float(mm.group(1)), 1)
    # Molar mass (known compounds) -- only when the stem asks for molar mass directly
    if low.strip().startswith("what is the molar mass"):
        for formula, mm in MOLAR_MASS.items():
            if formula in t:
                return float(mm)
    # energy lost = input - useful
    if "lost to non-useful" in low or "energy is lost" in low or "energy is wasted" in low:
        cand = sorted([x for x in n if x > 1])
        if len(cand) >= 2:
            return cand[-1] - cand[-2]
    # Q = mcDeltaT with explicit c and temperature change or range
    if ("q = mc" in low or "mc\\delta" in low.replace(" ", "") or "4200" in t or "c = 900" in t or "c = 4.18" in t or "c = 800" in t):
        mkg = re.search(r"(\d+(?:\.\d+)?)\s*kg", t)
        mg = re.search(r"(\d+(?:\.\d+)?)\s*g\b", t)
        c = re.search(r"c\s*=\s*(\d+(?:\.\d+)?)", t)
        # temperature change: explicit "by X" or range "from A to B"
        by = re.search(r"by (\d+(?:\.\d+)?)\s*°?c", low)
        rng = re.findall(r"(\d+(?:\.\d+)?)\s*°c", low)
        dT = None
        if by:
            dT = float(by.group(1))
        elif "from" in low and len(rng) >= 2:
            dT = abs(float(rng[1]) - float(rng[0]))
        elif "rises" in low or "rise" in low:
            rise = re.search(r"rises?\s*(\d+(?:\.\d+)?)", low)
            if rise:
                dT = float(rise.group(1))
        mass = None
        if mkg:
            mass = float(mkg.group(1))
        elif mg:
            mass = float(mg.group(1))
        if mass is not None and c and dT is not None:
            if "temperature change" in low or "δt" in low or "\\delta t" in low or "what is the temperature" in low:
                # solving for dT given Q: Q/(mc)
                Q = re.search(r"releases? (\d+(?:\.\d+)?)\s*j", low) or re.search(r"(\d+(?:\.\d+)?)\s*j of heat", low)
                if Q:
                    return round(float(Q.group(1)) / (mass * float(c.group(1))), 1)
            return round(mass * float(c.group(1)) * dT, 0)
    # solving for dT (heat released, mass, c given, asks temperature change)
    if "temperature change" in low and ("releases" in low or "cooling" in low):
        Q = re.search(r"releases? (\d+(?:\.\d+)?)\s*j", low)
        mkg = re.search(r"(\d+(?:\.\d+)?)\s*kg", t)
        c = re.search(r"c\s*=\s*(\d+(?:\.\d+)?)", t)
        if Q and mkg and c:
            return round(float(Q.group(1)) / (float(mkg.group(1)) * float(c.group(1))), 1)
    # neutralization heat -> temp increase: Q/(m*c)
    if "temperature increase" in low and "heat" in low:
        Q = re.search(r"(\d+(?:\.\d+)?)\s*j of heat", low)
        m = re.search(r"(\d+(?:\.\d+)?)\s*g of water", low)
        c = re.search(r"c\s*=\s*(\d+(?:\.\d+)?)", t)
        if Q and m and c:
            return round(float(Q.group(1)) / (float(m.group(1)) * float(c.group(1))), 1)
    # percent increase relative to original
    if "percent increase" in low:
        vals = re.findall(r"(\d+(?:\.\d+)?)\s*ppm", low)
        if len(vals) >= 2:
            a, b = float(vals[0]), float(vals[1])
            lo, hi = min(a, b), max(a, b)
            return round((hi - lo) / lo * 100, 0)
    # ppm increase
    if "increase in ppm" in low or ("ppm" in low and "increase" in low and "percent" not in low):
        vals = re.findall(r"(\d+(?:\.\d+)?)\s*ppm", low)
        if len(vals) >= 2:
            return abs(float(vals[1]) - float(vals[0]))
    # albedo / reflected-absorbed complement
    if "albedo" in low and "reflect" in low:
        a = re.search(r"albedo[^0-9]*(\d+(?:\.\d+)?)", low)
        if a:
            v = float(a.group(1))
            return v * 100 if v < 1 else v
    if "reflects" in low and "absorbed" in low:
        r = re.search(r"reflects (\d+(?:\.\d+)?)%", low)
        if r:
            return 100 - float(r.group(1))
    if "percentage" in low and "absorbed" in low and "reflected" in low:
        vals = [x for x in n if x > 1000]
        if len(vals) >= 2:
            total = max(vals)
            refl = min(vals)
            return round((total - refl) / total * 100, 0)
    # degree-days: temp * days
    if "degree-days" in low or "°c·days" in low:
        temp = re.search(r"(\d+(?:\.\d+)?)\s*°c", low)
        days = re.search(r"(\d+(?:\.\d+)?)\s*days", low)
        if temp and days:
            return float(temp.group(1)) * float(days.group(1))
    # linear projection rate * time
    if "per year" in low and "years" in low:
        rate = re.search(r"(\d+(?:\.\d+)?)\s*mm per year", low)
        yrs = re.search(r"(\d+(?:\.\d+)?)\s*years", low)
        if rate and yrs:
            return float(rate.group(1)) * float(yrs.group(1))
    # rate * time for photosynthesis mol
    if "mol of co" in low and "per hour" in low and "hours" in low:
        rate = re.search(r"(\d+(?:\.\d+)?)\s*mol", low)
        hrs = re.search(r"(\d+(?:\.\d+)?)\s*hours", low)
        if rate and hrs:
            return round(float(rate.group(1)) * float(hrs.group(1)), 1)
    # Avogadro: particles / 6.02e23
    if "avogadro" in low or "\\times 10" in t:
        parts = [x for x in n if x > 1e20]
        if parts:
            return round(parts[0] / 6.02e23, 1)
    # O atoms in n mol CO2
    if "o atoms" in low and "co$_2$" in low:
        mol = re.search(r"(\d+(?:\.\d+)?)\s*mol", low)
        if mol:
            return round(float(mol.group(1)) * 2, 1)
    # stoichiometry: ratio from balanced equation (1:1 or given)
    if "how many moles" in low and "according to" in low:
        # NH3 from H2 (3H2->2NH3): 2 mol NH3 needs 3 mol H2
        if "nh$_2$" in low or "nh3" in low or "nh$_3$" in low:
            want = re.search(r"produce (\d+(?:\.\d+)?)\s*mol", low)
            if want:
                return round(float(want.group(1)) * 3 / 2, 1)
        # NaCl from Na (2Na->2NaCl 1:1); H2O from H2 (2H2->2H2O 1:1)
        frm = re.search(r"from (\d+(?:\.\d+)?)\s*mol", low)
        if frm:
            return round(float(frm.group(1)), 1)
    # mass from moles: moles * molar mass
    if "what mass" in low and "mol" in low and "molar mass" in low:
        mol = re.search(r"obtain (\d+(?:\.\d+)?)\s*mol", low)
        mm = re.search(r"molar mass[^0-9]*(\d+(?:\.\d+)?)", low)
        if mol and mm:
            return round(float(mol.group(1)) * float(mm.group(1)), 1)

    # Efficiency: useful / input * 100
    if "efficien" in low:
        cand = [x for x in n if x > 1]
        if len(cand) >= 2:
            useful, inp = sorted(cand)[:2]
            return round(useful / inp * 100, 1)
    # q = mcDeltaT  (thermal energy)
    if ("mc" in low.replace(" ", "") or "q = mc" in low or "4200" in t or "4.18" in t or "900" in t) and (
        "thermal" in low or "heat" in low or "warm" in low or "temperature" in low or "energy" in low):
        # look for mass, c, deltaT patterns; fall back below
        pass
    # acceleration a = dv/dt
    if "acceler" in low and ("m/s" in low):
        # velocity change / time
        vs = re.findall(r"(\d+(?:\.\d+)?)\s*m/s\b", t)
        ts = re.findall(r"(\d+(?:\.\d+)?)\s*s\b", t)
        if "rest" in low and vs and ts:
            return round(float(vs[0]) / float(ts[-1]), 2)
        if len(vs) >= 2 and ts:
            return round((float(vs[1]) - float(vs[0])) / float(ts[-1]), 2)
    # kinetic energy 1/2 m v^2
    if "kinetic energy" in low:
        mm = re.search(r"(\d+(?:\.\d+)?)\s*kg", t)
        vv = re.search(r"(\d+(?:\.\d+)?)\s*m/s", t)
        if mm and vv:
            return round(0.5 * float(mm.group(1)) * float(vv.group(1)) ** 2, 1)
    # gravitational potential energy mgh
    if "potential energy" in low:
        mm = re.search(r"(\d+(?:\.\d+)?)\s*kg", t)
        hh = re.search(r"(\d+(?:\.\d+)?)\s*m\b", t)
        if mm and hh:
            return round(float(mm.group(1)) * 9.8 * float(hh.group(1)), 1)
    # magnification
    if "magnif" in low:
        if "eyepiece" in low and "objective" in low:
            e = re.search(r"eyepiece[^0-9]*(\d+(?:\.\d+)?)", low)
            o = re.search(r"objective[^0-9]*(\d+(?:\.\d+)?)", low)
            if e and o:
                return float(e.group(1)) * float(o.group(1))
        # given total and eyepiece, solve objective
        if "eyepiece" in low and ("magnifies" in low or "total" in low):
            tot = re.search(r"(\d+(?:\.\d+)?)\s*[×x]\b", t)
            e = re.search(r"(\d+(?:\.\d+)?)\s*[×x]\s*eyepiece", low)
            if tot and e:
                return float(tot.group(1)) / float(e.group(1))
        # image / actual
        dims = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm|μm)", t)
        img = re.search(r"image[^0-9]*(\d+(?:\.\d+)?)", low)
        if img and dims:
            actual = min(float(x) for x in dims)
            return round(float(img.group(1)) / actual, 0) if float(img.group(1)) / actual >= 1 else round(float(img.group(1)) / actual, 2)
        if len(dims) >= 2:
            a, b = sorted(float(x) for x in dims)
            return round(b / a, 0)
    # SA:V cube
    if "surface-area-to-volume" in low or ("surface area" in low and "volume" in low):
        e = (re.search(r"edges? of (\d+(?:\.\d+)?)", low) or re.search(r"(\d+(?:\.\d+)?)\s*μm edges", low)
             or re.search(r"(\d+(?:\.\d+)?)\s*μm on each", low) or re.search(r"measures (\d+(?:\.\d+)?)", low))
        if e:
            edge = float(e.group(1))
            ratio = 6 * edge**2 / edge**3
            return round(ratio, 2) if "two decimal" in low else round(ratio, 1)
    # plasmolysis / percent of cells
    if "plasmoly" in low or ("percent" in low and "cells" in low):
        vals = re.findall(r"(\d+(?:\.\d+)?)", t)
        m = re.search(r"(\d+)\s*of\s*(\d+)", low)
        if m:
            return round(int(m.group(1)) / int(m.group(2)) * 100, 1)
    # stomatal density = count / area
    if "stomatal density" in low or ("stomata" in low and "density" in low):
        count = re.search(r"(\d+(?:\.\d+)?)\s*open stomata", low) or re.search(r"contains (\d+(?:\.\d+)?)", low)
        area = re.search(r"(\d+(?:\.\d+)?)\s*mm", low)
        if count and area:
            return round(float(count.group(1)) / float(area.group(1)), 0)
    # trophic transfer (10% rule)
    if "trophic" in low or ("10%" in t and "energy" in low):
        e = re.search(r"(\d+(?:\.\d+)?)\s*kj", low)
        pct = re.search(r"(\d+(?:\.\d+)?)%", t)
        if e and pct:
            return round(float(e.group(1)) * float(pct.group(1)) / 100, 0)
    return None


def main() -> int:
    d = json.loads(BANK.read_text(encoding="utf-8"))
    nr = [(i, q) for i, q in enumerate(d) if q["question_type"] == "Numerical Response"]
    mism, manual, ok = [], [], 0
    for i, q in nr:
        exp = recompute(q)
        if exp is None:
            manual.append((i, q["answer"], q["question_text"][:70]))
            continue
        try:
            got = float(q["answer"])
        except (TypeError, ValueError):
            mism.append((i, q["answer"], exp, q["question_text"][:70]))
            continue
        if close(exp, got):
            ok += 1
        else:
            mism.append((i, q["answer"], exp, q["question_text"][:70]))
    print(f"NR total {len(nr)} | auto-verified OK {ok} | mismatches {len(mism)} | manual {len(manual)}")
    if mism:
        print("\n--- MISMATCHES ---")
        for m in mism:
            print("  key=", m[1], "recomputed=", m[2], "|", m[3])
    print("\n--- MANUAL (not auto-recomputable) ---")
    for m in manual:
        print("  key=", m[0], m[1], "|", m[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
