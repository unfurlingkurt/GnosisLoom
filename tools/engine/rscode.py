#!/usr/bin/env python3
"""RatioSpace Protein Opcode — Continued Fraction Structural Encoding.

Converts protein sequences into geodesic paths through the Stern-Brocot /
Farey tree. The continued fraction expansion of the composed ratio IS the
structural code — helices and sheets trace different attractor basins.

The key insight: DON'T add frequencies. COMPOSE them as ratios through
the Farey tree using the mediant operation. The CF tail motifs encode
the geometry (helix twist vs sheet pleat).

Pipeline:
    Step A: Anchor translation (AA freq → exact ratio to water clock)
    Step B: Sequential composition via mediant (trace the geodesic)
    Step C: Extract invariants (tau-cost, RS-Code, phi-coherence)
"""

import math
from fractions import Fraction
from typing import List, Tuple

# === Constants ===

PHI = (1 + math.sqrt(5)) / 2
WATER_CLOCK = Fraction(186, 100)  # 1.86 Hz as exact fraction
SOL_CARBON = Fraction(153, 100)   # 1.53 Hz as exact fraction

# Amino acid frequencies as exact fractions (Hz × 100 to avoid float)
AA_FREQ_EXACT = {
    "G": Fraction(310, 100),   # 3.10
    "A": Fraction(463, 100),   # 4.63
    "S": Fraction(612, 100),   # 6.12
    "V": Fraction(769, 100),   # 7.69
    "T": Fraction(765, 100),   # 7.65
    "N": Fraction(772, 100),   # 7.72
    "C": Fraction(872, 100),   # 8.72
    "P": Fraction(887, 100),   # 8.87
    "I": Fraction(922, 100),   # 9.22
    "L": Fraction(922, 100),   # 9.22
    "Q": Fraction(925, 100),   # 9.25
    "D": Fraction(951, 100),   # 9.51
    "K": Fraction(1052, 100),  # 10.52
    "E": Fraction(1104, 100),  # 11.04
    "H": Fraction(1155, 100),  # 11.55
    "M": Fraction(1240, 100),  # 12.40
    "R": Fraction(1326, 100),  # 13.26
    "F": Fraction(1301, 100),  # 13.01
    "Y": Fraction(1454, 100),  # 14.54
    "W": Fraction(1625, 100),  # 16.25
}


# === Continued Fraction Operations ===

def to_cf(frac, max_terms=20):
    """Convert a Fraction to its continued fraction expansion [a0; a1, a2, ...]."""
    if isinstance(frac, float):
        frac = Fraction(frac).limit_denominator(10000)
    coeffs = []
    p, q = frac.numerator, frac.denominator
    while q != 0 and len(coeffs) < max_terms:
        a = p // q
        coeffs.append(int(a))
        p, q = q, p - a * q
    return coeffs


def from_cf(coeffs):
    """Convert a continued fraction [a0; a1, a2, ...] back to a Fraction."""
    if not coeffs:
        return Fraction(0)
    result = Fraction(coeffs[-1])
    for i in range(len(coeffs) - 2, -1, -1):
        if result != 0:
            result = coeffs[i] + Fraction(1, result)
        else:
            result = Fraction(coeffs[i])
    return result


def cf_length(coeffs):
    """Total CF cost: sum of all coefficients (total geodesic work)."""
    return sum(abs(c) for c in coeffs)


def cf_depth(coeffs):
    """CF depth: number of terms (geodesic complexity)."""
    return len(coeffs)


# === Mediant and Composition ===

def mediant(a, b):
    """Farey mediant: (p1+p2)/(q1+q2). The fundamental Stern-Brocot operation."""
    return Fraction(a.numerator + b.numerator, a.denominator + b.denominator)


def multiplicative_compose(a, b):
    """Multiplicative composition in ratio-space."""
    return a * b


def sequential_mediant(ratios):
    """Compose a sequence of ratios by successive mediant operations.

    This traces the geodesic path through the Farey tree,
    accumulating the geometric 'twist' of each residue.
    """
    if not ratios:
        return Fraction(1)
    result = ratios[0]
    for r in ratios[1:]:
        result = mediant(result, r)
    return result


def sequential_multiply(ratios):
    """Compose by multiplication (geometric product)."""
    result = Fraction(1)
    for r in ratios:
        result *= r
    return result


# === Step A: Anchor Translation ===

def aa_to_anchor_ratio(aa_code, anchor=None):
    """Convert amino acid to exact ratio relative to anchor frequency."""
    anchor = anchor or WATER_CLOCK
    freq = AA_FREQ_EXACT.get(aa_code.upper())
    if freq is None:
        return Fraction(1)
    return freq / anchor


def sequence_to_ratios(seq, anchor=None):
    """Convert a protein sequence to a list of anchor ratios."""
    return [aa_to_anchor_ratio(c, anchor) for c in seq.upper()]


# === Step B & C: Opcode Extraction ===

def extract_opcode(seq, anchor=None, method="mediant"):
    """Extract the full protein opcode from a sequence.

    Returns:
        tau: the composed ratio (total phase-time cost)
        rs_code: continued fraction expansion (the structural address)
        tau_cost: CF length (total geodesic work)
        phi_coherence: alignment with phi-harmonic scaling
    """
    ratios = sequence_to_ratios(seq, anchor)

    if method == "mediant":
        tau = sequential_mediant(ratios)
    elif method == "multiply":
        tau = sequential_multiply(ratios)
    else:
        tau = sequential_mediant(ratios)

    rs_code = to_cf(tau)
    tau_cost = cf_length(rs_code)

    # Phi coherence: how close is tau to a power of phi?
    tau_float = float(tau)
    if tau_float > 0:
        log_phi = math.log(tau_float) / math.log(PHI)
        phi_coherence = 1.0 - abs(log_phi - round(log_phi))
    else:
        phi_coherence = 0.0

    return {
        "tau": tau,
        "tau_float": float(tau),
        "rs_code": rs_code,
        "tau_cost": tau_cost,
        "cf_depth": len(rs_code),
        "phi_coherence": phi_coherence,
    }


def extract_windowed_opcodes(seq, window=6, stride=1, anchor=None, method="mediant"):
    """Extract opcodes for sliding windows across a sequence.

    Returns list of (position, opcode_dict) tuples.
    """
    results = []
    for i in range(0, len(seq) - window + 1, stride):
        segment = seq[i:i+window]
        opcode = extract_opcode(segment, anchor, method)
        opcode["position"] = i
        opcode["segment"] = segment
        results.append(opcode)
    return results


# === Analysis Functions ===

def cf_tail_motif(rs_code, tail_length=4):
    """Extract the tail motif of a CF expansion.

    The tail encodes the fine geometric structure — helix vs sheet
    should have characteristically different tail patterns.
    """
    if len(rs_code) <= tail_length:
        return tuple(rs_code)
    return tuple(rs_code[-tail_length:])


def cf_pattern_signature(rs_code):
    """Extract a pattern signature from the CF expansion.

    Looks for:
    - Periodicity (repeating patterns → regular geometry)
    - Dominance of 1s and 2s (→ phi-related geometry)
    - Large coefficients (→ near-rational, simple structure)
    """
    if not rs_code:
        return {"periodic": False, "phi_like": 0, "max_coeff": 0}

    # Check for approximate periodicity
    n = len(rs_code)
    best_period = 0
    best_match = 0
    for period in range(1, min(n // 2 + 1, 6)):
        matches = 0
        comparisons = 0
        for i in range(period, n):
            if rs_code[i] == rs_code[i % period]:
                matches += 1
            comparisons += 1
        if comparisons > 0:
            match_rate = matches / comparisons
            if match_rate > best_match:
                best_match = match_rate
                best_period = period

    # Phi-like: count of 1s (CF of phi = [1;1,1,1,...])
    ones_fraction = rs_code.count(1) / len(rs_code) if rs_code else 0

    # Count 1s and 2s (simple geometric turns)
    simple_fraction = sum(1 for c in rs_code if c in (1, 2)) / len(rs_code)

    return {
        "period": best_period,
        "periodicity": best_match,
        "phi_like": ones_fraction,
        "simple_turns": simple_fraction,
        "max_coeff": max(rs_code) if rs_code else 0,
        "mean_coeff": sum(rs_code) / len(rs_code) if rs_code else 0,
    }


# === Demo / Main ===

def demo():
    """Demonstrate RS-Code extraction on known protein segments."""
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  RATIOSPACE PROTEIN OPCODE — Geodesic Structural Encoding          ║
    ║  Continued fractions through the Farey tree, not Hz addition       ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

    # === Step A: Show anchor ratios ===
    print("  Step A: Amino Acid → Water Clock Ratios (exact fractions)\n")
    print(f"  {'AA':4s} {'Freq':>6s} {'Ratio':>12s} {'CF Expansion':>30s} {'CF Cost':>8s}")
    print(f"  {'─'*4} {'─'*6} {'─'*12} {'─'*30} {'─'*8}")
    for aa in "GALVIPFWEDKRHYCMSTNQ":
        freq = AA_FREQ_EXACT.get(aa, Fraction(0))
        ratio = freq / WATER_CLOCK
        cf = to_cf(ratio)
        print(f"  {aa:4s} {float(freq):>5.2f} {str(ratio):>12s} {str(cf):>30s} {cf_length(cf):>8d}")

    # === Known protein segments ===
    print(f"\n{'='*74}")
    print(f"  Step B+C: Sequence → Geodesic Path → RS-Code")
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

    # Collect all opcodes for comparison
    all_opcodes = {}

    for stype, seqs in segments.items():
        print(f"  --- {stype.upper()} ---")
        opcodes = []
        for name, seq in seqs:
            op = extract_opcode(seq, method="mediant")
            sig = cf_pattern_signature(op["rs_code"])
            opcodes.append((name, seq, op, sig))
            all_opcodes.setdefault(stype, []).append((name, op, sig))

            print(f"    {name:15s} [{seq[:12]:12s}]")
            print(f"      tau = {op['tau_float']:.6f}  cost={op['tau_cost']:4d}  "
                  f"depth={op['cf_depth']:2d}  phi_coh={op['phi_coherence']:.3f}")
            print(f"      RS-Code: {op['rs_code'][:12]}{'...' if len(op['rs_code']) > 12 else ''}")
            print(f"      pattern: period={sig['period']} periodicity={sig['periodicity']:.2f} "
                  f"phi_like={sig['phi_like']:.2f} simple={sig['simple_turns']:.2f} "
                  f"mean_cf={sig['mean_coeff']:.1f}")
        print()

    # === Discrimination analysis ===
    print(f"{'='*74}")
    print(f"  DISCRIMINATION: Do RS-Code properties separate helix/sheet/coil?")
    print(f"{'='*74}\n")

    print(f"  {'Type':8s} {'tau_cost':>9s} {'cf_depth':>9s} {'phi_coh':>8s} {'phi_like':>9s} "
          f"{'simple':>7s} {'period':>7s} {'mean_cf':>8s}")
    print(f"  {'─'*8} {'─'*9} {'─'*9} {'─'*8} {'─'*9} {'─'*7} {'─'*7} {'─'*8}")

    for stype in ["helix", "sheet", "coil"]:
        ops = all_opcodes[stype]
        n = len(ops)
        avg_cost = sum(o[1]["tau_cost"] for o in ops) / n
        avg_depth = sum(o[1]["cf_depth"] for o in ops) / n
        avg_phi = sum(o[1]["phi_coherence"] for o in ops) / n
        avg_phi_like = sum(o[2]["phi_like"] for o in ops) / n
        avg_simple = sum(o[2]["simple_turns"] for o in ops) / n
        avg_period = sum(o[2]["period"] for o in ops) / n
        avg_mean_cf = sum(o[2]["mean_coeff"] for o in ops) / n

        print(f"  {stype.upper():8s} {avg_cost:>9.1f} {avg_depth:>9.1f} {avg_phi:>8.3f} "
              f"{avg_phi_like:>9.2f} {avg_simple:>7.2f} {avg_period:>7.1f} {avg_mean_cf:>8.1f}")

    # === Try classification ===
    print(f"\n  === CLASSIFICATION TEST ===\n")
    correct = 0
    total = 0
    for stype, ops in all_opcodes.items():
        for name, op, sig in ops:
            # Classification based on RS-Code properties
            cost = op["tau_cost"]
            depth = op["cf_depth"]
            phi_like = sig["phi_like"]
            simple = sig["simple_turns"]
            mean_cf = sig["mean_coeff"]
            phi_coh = op["phi_coherence"]

            # Try: helix = high phi_like + moderate cost
            #       sheet = high simple_turns + lower phi_like
            #       coil = low simple_turns OR high mean_cf
            if phi_like > 0.45 and mean_cf < 15:
                pred = "helix"
            elif simple > 0.55 and phi_like <= 0.45:
                pred = "sheet"
            else:
                pred = "coil"

            ok = pred == stype
            if ok:
                correct += 1
            total += 1
            print(f"  {'✓' if ok else '✗'} {name:15s} actual={stype:6s} pred={pred:6s} "
                  f"phi_like={phi_like:.2f} simple={simple:.2f} mean_cf={mean_cf:.1f}")

    print(f"\n  Accuracy: {correct}/{total} = {correct/total:.0%}")


if __name__ == "__main__":
    demo()
