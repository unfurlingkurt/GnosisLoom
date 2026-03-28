#!/usr/bin/env python3
"""RatioSpace Protein Opcode — Continued Fraction Structural Encoding.

Converts protein sequences into geodesic paths through the Stern-Brocot /
Farey tree. The continued fraction expansion of the composed ratio IS the
structural code — helices and sheets trace different attractor basins.

Pipeline:
    Step A: Anchor to Sol-Carbon (1.53 Hz) — the polypeptide backbone anchor
    Step B: Multiplicative composition (otimes) for TENSION between adjacent
            residue ratios: T(r1,r2) = CF_Length[r1 * r2]
    Step C: Extract CF tail motifs:
            - Helix: dense 1s and 2s (tight recursive coil, high alternation)
            - Sheet: large integer spikes (extended glide, abrupt adjustments)
            - Coil: irregular, high geodesic cost
"""

import math
from fractions import Fraction
from typing import List, Tuple, Dict

# === Constants ===

PHI = (1 + math.sqrt(5)) / 2
SOL_CARBON = Fraction(153, 100)   # 1.53 Hz — polypeptide backbone anchor
WATER_CLOCK = Fraction(186, 100)  # 1.86 Hz — hydration shell GRF envelope

# Amino acid frequencies as exact fractions
AA_FREQ = {
    "G": Fraction(310, 100),  "A": Fraction(463, 100),  "S": Fraction(612, 100),
    "V": Fraction(769, 100),  "T": Fraction(765, 100),  "N": Fraction(772, 100),
    "C": Fraction(872, 100),  "P": Fraction(887, 100),  "I": Fraction(922, 100),
    "L": Fraction(922, 100),  "Q": Fraction(925, 100),  "D": Fraction(951, 100),
    "K": Fraction(1052, 100), "E": Fraction(1104, 100), "H": Fraction(1155, 100),
    "M": Fraction(1240, 100), "R": Fraction(1326, 100), "F": Fraction(1301, 100),
    "Y": Fraction(1454, 100), "W": Fraction(1625, 100),
}


# === Continued Fraction Core ===

def to_cf(frac, max_terms=20):
    """Continued fraction expansion [a0; a1, a2, ...]."""
    if isinstance(frac, float):
        frac = Fraction(frac).limit_denominator(100000)
    coeffs = []
    p, q = abs(frac.numerator), abs(frac.denominator)
    while q != 0 and len(coeffs) < max_terms:
        a = p // q
        coeffs.append(int(a))
        p, q = q, p - a * q
    return coeffs


def cf_length(coeffs):
    """Total CF cost (sum of all coefficients = geodesic work)."""
    return sum(abs(c) for c in coeffs)


def from_cf(coeffs):
    """Reconstruct Fraction from CF expansion."""
    if not coeffs:
        return Fraction(0)
    result = Fraction(coeffs[-1])
    for i in range(len(coeffs) - 2, -1, -1):
        if result != 0:
            result = coeffs[i] + Fraction(1, result)
        else:
            result = Fraction(coeffs[i])
    return result


# === Step A: Anchor to Sol-Carbon ===

def aa_ratio(aa_code, anchor=None):
    """Amino acid frequency as exact ratio to Sol-Carbon anchor."""
    anchor = anchor or SOL_CARBON
    freq = AA_FREQ.get(aa_code.upper(), Fraction(5, 1))
    return freq / anchor


# === Step B: Tension via Multiplicative Composition ===

def tension(r1, r2):
    """Tension between two ratios: T(r1, r2) = CF_Length[r1 * r2].

    This is the core operation. The CF cost of the PRODUCT encodes
    the geometric stress of transitioning from one residue to the next.
    """
    product = r1 * r2
    cf = to_cf(product)
    return cf_length(cf), cf


def tension_sequence(seq, anchor=None):
    """Extract the full tension sequence for a protein chain.

    For each adjacent pair (i, i+1), computes T = CF_Length[r_i * r_{i+1}].
    Returns list of (tension_cost, cf_expansion) tuples.
    """
    ratios = [aa_ratio(c, anchor) for c in seq.upper()]
    tensions = []
    for i in range(len(ratios) - 1):
        t_cost, t_cf = tension(ratios[i], ratios[i + 1])
        tensions.append({
            "pair": seq[i:i+2],
            "cost": t_cost,
            "cf": t_cf,
            "r1": float(ratios[i]),
            "r2": float(ratios[i + 1]),
            "product": float(ratios[i] * ratios[i + 1]),
        })
    return tensions


# === Step C: CF Motif Classification ===

def motif_density(cf_coeffs):
    """Classify CF tail by run-length and magnitude.

    Returns:
        low_count: number of small coefficients (1 or 2) — helix signal
        high_count: number of large coefficients (>= 5) — sheet signal
        alternation: how frequently the magnitude changes — helix = high
        max_coeff: largest single coefficient — sheet indicator
    """
    if not cf_coeffs:
        return {"low_count": 0, "high_count": 0, "alternation": 0, "max_coeff": 0,
                "low_fraction": 0, "high_fraction": 0}

    low = sum(1 for c in cf_coeffs if c in (1, 2))
    high = sum(1 for c in cf_coeffs if c >= 5)
    n = len(cf_coeffs)

    # Alternation: count transitions between low and high values
    alternations = 0
    for i in range(1, n):
        prev_low = cf_coeffs[i-1] <= 2
        curr_low = cf_coeffs[i] <= 2
        if prev_low != curr_low:
            alternations += 1

    return {
        "low_count": low,
        "high_count": high,
        "low_fraction": low / n if n > 0 else 0,
        "high_fraction": high / n if n > 0 else 0,
        "alternation": alternations / max(1, n - 1),
        "max_coeff": max(cf_coeffs) if cf_coeffs else 0,
        "mean_coeff": sum(cf_coeffs) / n if n > 0 else 0,
        "depth": n,
    }


def tension_periodicity(costs, max_period=6):
    """Detect periodicity in the tension cost sequence.

    Helices show strong periodicity (3-4 step period from the 3.6 residue turn).
    Sheets show weak alternation (period 2 from pleating).
    Coils show no periodicity.
    """
    n = len(costs)
    if n < 4:
        return 0, 0.0

    best_period = 0
    best_score = 0.0

    for period in range(2, min(max_period + 1, n // 2 + 1)):
        # Autocorrelation at this lag
        pairs = [(costs[i], costs[i + period]) for i in range(n - period)]
        if not pairs:
            continue
        mean_c = sum(c for c, _ in pairs) / len(pairs)
        if mean_c == 0:
            continue
        # Normalized similarity: how similar are values separated by 'period' steps
        diffs = [abs(a - b) / max(mean_c, 1) for a, b in pairs]
        similarity = 1.0 - min(1.0, sum(diffs) / len(diffs))
        if similarity > best_score:
            best_score = similarity
            best_period = period

    return best_period, best_score


def classify_segment(tensions):
    """Classify a protein segment from its tension sequence.

    Three-signal classification:
    1. CF motif density (low_fraction of 1s/2s): helix > sheet > coil
    2. Tension cost periodicity: helix (period 3-4) > sheet (period 2) > coil (none)
    3. Base tension cost level: sheet > helix (higher GRF = higher base cost)
    """
    if not tensions:
        return "unknown", {}

    # Aggregate CF coefficients from all tension pairs
    all_cfs = []
    total_cost = 0
    for t in tensions:
        all_cfs.extend(t["cf"])
        total_cost += t["cost"]

    motif = motif_density(all_cfs)
    avg_cost = total_cost / len(tensions)

    # Per-pair tension costs
    costs = [t["cost"] for t in tensions]
    cost_variance = sum((c - avg_cost)**2 for c in costs) / len(costs) if costs else 0

    # Periodicity detection
    period, periodicity = tension_periodicity(costs)

    # Net motif balance
    motif_balance = motif["low_fraction"] - motif["high_fraction"]

    # Three-signal scoring:
    # Helix: high motif balance + periodicity (period 3-5)
    # Sheet: moderate motif + high base cost + period 2 or high variance
    # Coil: low motif balance + no periodicity

    helix_score = (motif_balance * 2
                   + (1.5 if period in (3, 4, 5) and periodicity > 0.3 else 0)
                   + periodicity * 1.0)

    sheet_score = ((1.0 if period == 2 and periodicity > 0.2 else 0)
                   + min(1.0, cost_variance / 5000.0) * 1.5
                   + (1.0 if avg_cost > 60 else 0))

    coil_score = ((1.0 - motif_balance) * 1.0
                  + (1.5 if periodicity < 0.3 else 0)
                  + motif["high_fraction"] * 2.0)

    scores = {"helix": helix_score, "sheet": sheet_score, "coil": coil_score}
    prediction = max(scores, key=scores.get)

    return prediction, {
        "scores": scores,
        "motif": motif,
        "avg_cost": avg_cost,
        "total_cost": total_cost,
        "cost_variance": cost_variance,
        "period": period,
        "periodicity": periodicity,
    }


# === Full Pipeline ===

def analyze_segment(seq, anchor=None):
    """Full RS-Code analysis pipeline for a protein segment."""
    tensions = tension_sequence(seq, anchor)
    prediction, analysis = classify_segment(tensions)
    return {
        "sequence": seq,
        "prediction": prediction,
        "tensions": tensions,
        **analysis,
    }


# === Demo ===

def demo():
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  RATIOSPACE PROTEIN OPCODE v2 — Carbon-Anchored Tension Geometry   ║
    ║  Multiplicative composition. CF motif density. Sol-Carbon 1.53 Hz  ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

    # Step A: Show Carbon-anchored ratios
    print("  Step A: Amino Acid → Sol-Carbon (1.53 Hz) Ratios\n")
    print(f"  {'AA':4s} {'Freq':>6s} {'Ratio':>12s} {'Float':>8s} {'CF':>25s} {'Cost':>5s}")
    print(f"  {'─'*4} {'─'*6} {'─'*12} {'─'*8} {'─'*25} {'─'*5}")
    for aa in "GALVIPFWEDKRHYCMSTNQ":
        r = aa_ratio(aa)
        cf = to_cf(r)
        print(f"  {aa:4s} {float(AA_FREQ[aa]):>5.2f} {str(r):>12s} {float(r):>8.4f} {str(cf):>25s} {cf_length(cf):>5d}")

    # Step B: Show tension between sample pairs
    print(f"\n  Step B: Tension = CF_Length[r_i × r_{{i+1}}] (adjacent pair stress)\n")
    print(f"  {'Pair':6s} {'r1':>7s} {'r2':>7s} {'Product':>9s} {'Tension':>8s} {'CF':>25s}")
    print(f"  {'─'*6} {'─'*7} {'─'*7} {'─'*9} {'─'*8} {'─'*25}")
    for pair in ["AA", "AL", "AE", "VV", "VI", "VF", "GP", "GS", "PG"]:
        r1, r2 = aa_ratio(pair[0]), aa_ratio(pair[1])
        t_cost, t_cf = tension(r1, r2)
        print(f"  {pair:6s} {float(r1):>7.3f} {float(r2):>7.3f} {float(r1*r2):>9.4f} {t_cost:>8d} {str(t_cf):>25s}")

    # Step C: Classify known segments
    print(f"\n{'='*74}")
    print(f"  Step C: Segment Classification via Tension CF Motifs")
    print(f"{'='*74}\n")

    segments = {
        "helix": [
            ("Lysozyme H1", "RCELAAAMKRH"),
            ("Myoglobin A", "LSDGEWQLVLNVWGK"),
            ("CI2 helix", "EKKALESQILA"),
            ("Ubiq helix", "IENVKAKIQDKE"),
            ("Poly-Ala", "AAAAAAAAAA"),
            ("Leu zipper", "AELKAELKAEL"),
        ],
        "sheet": [
            ("Lysozyme S1", "NTDGSTDYGILQ"),
            ("Ubiq sheet1", "MQIFVKT"),
            ("Silk fibroin", "GAGAGSGA"),
            ("SH3 sheet", "YVALYD"),
            ("Poly-Val", "VVVVVVVVVV"),
            ("Immunoglob", "EVQLVESGGG"),
        ],
        "coil": [
            ("Lysozyme L1", "SRWWCNDGRTP"),
            ("Myo EF loop", "GHPET"),
            ("Ubiq loop", "LTGKT"),
            ("Poly-GP", "GPGPGPGPGP"),
            ("Poly-SN", "SNSNSNSNSN"),
            ("Random", "GSNDPQKAET"),
        ],
    }

    all_analyses = {}
    for stype, seqs in segments.items():
        for name, seq in seqs:
            result = analyze_segment(seq)
            all_analyses.setdefault(stype, []).append((name, result))

    # Print averages
    print(f"  {'Type':8s} {'AvgCost':>8s} {'Variance':>9s} {'LowFrac':>8s} {'HighFrac':>9s} {'Altern':>7s} {'MaxCF':>6s} {'MeanCF':>7s}")
    print(f"  {'─'*8} {'─'*8} {'─'*9} {'─'*8} {'─'*9} {'─'*7} {'─'*6} {'─'*7}")

    for stype in ["helix", "sheet", "coil"]:
        analyses = [a[1] for a in all_analyses[stype]]
        n = len(analyses)
        avg_cost = sum(a["avg_cost"] for a in analyses) / n
        avg_var = sum(a["cost_variance"] for a in analyses) / n
        avg_low = sum(a["motif"]["low_fraction"] for a in analyses) / n
        avg_high = sum(a["motif"]["high_fraction"] for a in analyses) / n
        avg_alt = sum(a["motif"]["alternation"] for a in analyses) / n
        avg_max = sum(a["motif"]["max_coeff"] for a in analyses) / n
        avg_mean = sum(a["motif"]["mean_coeff"] for a in analyses) / n

        print(f"  {stype.upper():8s} {avg_cost:>8.1f} {avg_var:>9.1f} {avg_low:>8.3f} {avg_high:>9.3f} "
              f"{avg_alt:>7.3f} {avg_max:>6.1f} {avg_mean:>7.1f}")

    # Classification results
    print(f"\n  === CLASSIFICATION ===\n")
    correct = 0
    total = 0
    for stype in ["helix", "sheet", "coil"]:
        for name, result in all_analyses[stype]:
            pred = result["prediction"]
            ok = pred == stype
            if ok:
                correct += 1
            total += 1
            m = result["motif"]
            s = result["scores"]
            per = result.get("period", 0)
            prd = result.get("periodicity", 0)
            print(f"  {'✓' if ok else '✗'} {name:15s} actual={stype:6s} pred={pred:6s} "
                  f"H={s['helix']:.2f} S={s['sheet']:.2f} C={s['coil']:.2f} "
                  f"per={per} prd={prd:.2f} low={m['low_fraction']:.2f}")

    print(f"\n  Accuracy: {correct}/{total} = {correct/total:.0%}")

    # Detail on a few segments
    print(f"\n  === TENSION DETAIL (sample segments) ===\n")
    for stype, name_idx in [("helix", 0), ("sheet", 0), ("coil", 0)]:
        name, result = all_analyses[stype][name_idx]
        print(f"  {stype.upper()}: {name} [{result['sequence']}]")
        print(f"    Tension costs: {[t['cost'] for t in result['tensions']]}")
        print(f"    All CF coeffs: ", end="")
        all_cf = []
        for t in result["tensions"]:
            all_cf.extend(t["cf"])
        print(f"{all_cf[:30]}{'...' if len(all_cf) > 30 else ''}")
        print()


if __name__ == "__main__":
    demo()
