#!/usr/bin/env python3
"""Investigation: K coupling gap and CF structure of uncoupled pairs.

The coupling criterion CF[0] = 1 (self-tension ratio < 2:1) breaks
at K(156) paired with A(38), V(57), I(69). These are real backbone
helices that our predictor misses.

Instead of declaring the chain "broken," this investigation examines
the CF STRUCTURE of each uncoupled pair. K(156)/A(38) = [4,9,2] is
not absence of coupling — it's a SPECIFIC geometric relationship
in the Stern-Brocot tree.

Key questions:
1. What does CF[0]=4 mean geometrically? (4th SB neighborhood)
2. What do the deeper coefficients [9,2] tell us about the path?
3. How do the convergents of these CFs relate to the framework?
4. Is there a cross-domain coupling mechanism in the Aramis Field
   that bridges amino acids with CF[0] > 1?

Run: python tools/engine/coupling_gap_investigation.py
"""

import math
import sys
from pathlib import Path
from fractions import Fraction

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, to_cf, cf_length, from_cf, SOL_CARBON
)
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
)
from tools.engine.fold import INTER_GROUND_DEPTH


def factorize(n):
    """Prime factorization."""
    n = abs(n)
    if n == 0:
        return {}
    factors = {}
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    if n > 1:
        factors[n] = 1
    return factors


def factor_str(n):
    f = factorize(n)
    if not f:
        return "0"
    return " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))


def analyze_coupling_pair(aa1, aa2):
    """Deep CF analysis of a coupling pair."""
    t1 = SELF_TENSION[aa1]
    t2 = SELF_TENSION[aa2]
    ratio = Fraction(max(t1, t2), min(t1, t2))
    cf = to_cf(ratio)
    cost = cf_length(cf)

    print(f"\n  {aa1}({t1}) ↔ {aa2}({t2})")
    print(f"    ratio = {ratio} = {float(ratio):.6f}")
    print(f"    CF = {cf}")
    print(f"    depth = {len(cf)}, cost = {cost}")
    print(f"    CF[0] = {cf[0]} → {'COUPLED' if cf[0] == 1 else f'gap = {cf[0] - 1}'}")

    # Convergents — these are the best rational approximations
    # and show the SB tree path to this ratio
    print(f"    Convergents (SB tree path):")
    for k in range(1, len(cf) + 1):
        conv = from_cf(cf[:k])
        err = abs(float(conv) - float(ratio))
        print(f"      [{cf[:k]}] = {conv} = {float(conv):.6f}  err={err:.6f}")

    # What SB neighborhood is the ratio in?
    # CF[0] = floor of the ratio. It determines which major branch.
    # CF[1] determines the sub-branch, etc.
    print(f"    SB neighborhood: {cf[0]}th branch")
    if len(cf) > 1:
        print(f"    Sub-branch: 1/{cf[1]}th of the way from {cf[0]} to {cf[0]+1}")

    # Relationship to framework constants
    # Is the ratio related to φ, inter-ground, or lattice constants?
    phi = (1 + math.sqrt(5)) / 2
    print(f"    ratio/φ = {float(ratio)/phi:.6f}")
    print(f"    ratio/igd = {float(ratio)/INTER_GROUND_DEPTH:.6f}")
    print(f"    ratio × igd = {float(ratio)*INTER_GROUND_DEPTH:.6f}")

    # The PRODUCT of self-tensions (like pair tension)
    product = t1 * t2
    product_cf = to_cf(Fraction(product, 1))
    print(f"    T product = {t1} × {t2} = {product} = {factor_str(product)}")

    # Product ratio to framework constants
    product_ratio_h = Fraction(product, HELIX_GROUND * HELIX_GROUND)
    product_ratio_s = Fraction(product, SHEET_GROUND * SHEET_GROUND)
    print(f"    product / {HELIX_GROUND}² = {float(product_ratio_h):.4f} "
          f"CF={to_cf(product_ratio_h)[:4]}")
    print(f"    product / {SHEET_GROUND}² = {float(product_ratio_s):.4f} "
          f"CF={to_cf(product_ratio_s)[:4]}")

    return cf


def investigate_k_gap():
    """Investigate the K coupling gap in ubiquitin's helix."""
    print("=" * 70)
    print("  K COUPLING GAP INVESTIGATION")
    print("=" * 70)

    # K's coupling landscape
    k_st = SELF_TENSION['K']
    print(f"\n  K self-tension: {k_st}")
    print(f"  K frequency ratio: {aa_ratio('K')} = {float(aa_ratio('K')):.6f}")
    print(f"  K/Sol-Carbon ratio: {float(aa_ratio('K')):.6f}")

    # All coupling pairs with K
    print(f"\n  --- K COUPLING PARTNERS (CF[0] = 1) ---")
    coupled = []
    uncoupled = []
    for aa in sorted(SELF_TENSION.keys()):
        st = SELF_TENSION[aa]
        ratio = Fraction(max(k_st, st), min(k_st, st))
        cf = to_cf(ratio)
        if cf[0] == 1:
            coupled.append((aa, st, cf))
        else:
            uncoupled.append((aa, st, cf))

    for aa, st, cf in coupled:
        print(f"    K↔{aa}({st}): ratio={float(Fraction(max(k_st,st),min(k_st,st))):.3f} "
              f"CF={cf[:4]} ✓")

    print(f"\n  --- K UNCOUPLED PAIRS (CF[0] > 1) ---")
    for aa, st, cf in uncoupled:
        print(f"    K↔{aa}({st}): ratio={float(Fraction(max(k_st,st),min(k_st,st))):.3f} "
              f"CF={cf[:4]} CF[0]={cf[0]}")

    # Deep analysis of key uncoupled pairs
    print(f"\n{'─'*70}")
    print(f"  DEEP CF ANALYSIS OF KEY UNCOUPLED PAIRS")
    print(f"{'─'*70}")

    # The specific pairs that break ubiquitin's helix
    for aa in ['A', 'V', 'I', 'L', 'D', 'N', 'T', 'S']:
        analyze_coupling_pair('K', aa)


def investigate_ubiquitin_helix():
    """Map the coupling chain through ubiquitin's helix region."""
    ubq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    ubq_dssp = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'

    print(f"\n{'='*70}")
    print(f"  UBIQUITIN HELIX COUPLING CHAIN")
    print(f"{'='*70}")

    # Helix region: positions 24-34 (1-indexed), 23-33 (0-indexed)
    print(f"\n  Helix region: positions 24-34")
    print(f"  Sequence: {ubq[23:34]}")
    print(f"  DSSP:     {ubq_dssp[23:34]}")
    print()

    print(f"  {'Pos':>4s} {'AA':>3s} {'ST':>4s} {'Left':>30s} {'Right':>30s}")
    for i in range(22, 36):
        aa = ubq[i]
        st = SELF_TENSION.get(aa, 50)

        # Left coupling
        if i > 0:
            left_aa = ubq[i - 1]
            left_st = SELF_TENSION.get(left_aa, 50)
            ratio_l = Fraction(max(st, left_st), min(st, left_st))
            cf_l = to_cf(ratio_l)
            coupled_l = cf_l[0] == 1
            left_str = (f"{left_aa}({left_st}):{aa}({st}) "
                        f"CF[0]={cf_l[0]} {'✓' if coupled_l else '✗'}")
        else:
            left_str = "—"

        # Right coupling
        if i + 1 < len(ubq):
            right_aa = ubq[i + 1]
            right_st = SELF_TENSION.get(right_aa, 50)
            ratio_r = Fraction(max(st, right_st), min(st, right_st))
            cf_r = to_cf(ratio_r)
            coupled_r = cf_r[0] == 1
            right_str = (f"{aa}({st}):{right_aa}({right_st}) "
                         f"CF[0]={cf_r[0]} {'✓' if coupled_r else '✗'}")
        else:
            right_str = "—"

        d = ubq_dssp[i]
        print(f"  {i+1:>4d} {aa:>3s} {st:>4d}  L:{left_str:>28s}  R:{right_str:>28s}  {d}")

    # Map the coupling chain — which positions are connected?
    print(f"\n  --- COUPLING CHAIN TOPOLOGY ---")
    chain = []
    current_segment = [23]
    for i in range(24, 34):
        prev_st = SELF_TENSION.get(ubq[i - 1], 50)
        curr_st = SELF_TENSION.get(ubq[i], 50)
        ratio = Fraction(max(prev_st, curr_st), min(prev_st, curr_st))
        cf = to_cf(ratio)
        if cf[0] == 1:
            current_segment.append(i)
        else:
            chain.append(current_segment)
            current_segment = [i]
    chain.append(current_segment)

    for seg in chain:
        aas = "".join(ubq[i] for i in seg)
        sts = [SELF_TENSION.get(ubq[i], 50) for i in seg]
        print(f"    Segment [{seg[0]+1}-{seg[-1]+1}]: {aas} "
              f"tensions={sts}")

    print(f"\n  The helix fragments into {len(chain)} coupling segments.")
    print(f"  K(156) creates gaps because its self-tension ratio to")
    print(f"  A(38), V(57), I(69) has CF[0] > 1 (ratio > 2:1).")
    print(f"\n  In the Aramis Field, cross-domain coupling could bridge")
    print(f"  these gaps if K operates in a different temporal domain.")
    print(f"  The CF structure [4,9,2] for K/A is not 'broken' —")
    print(f"  it encodes a specific path in the SB tree.")


def main():
    investigate_k_gap()
    investigate_ubiquitin_helix()


if __name__ == "__main__":
    main()
