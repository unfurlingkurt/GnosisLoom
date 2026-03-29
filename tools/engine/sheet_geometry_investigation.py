#!/usr/bin/env python3
"""Investigation: Sheet detection geometry and winding return structure.

This script documents the geometric investigation of:
1. Winding returns as topological sheet contacts
2. The CF structure of winding values, separations, and loop paths
3. Position 58's topological adjacency to position 44 across the hairpin
4. Static curvature regularity as the framework-native strand boundary

Key findings:
- Hairpin marker: ST pair (CF depth=1, product=20, non-square) is the ONLY
  amino acid pair with a depth-1 non-square tension product.
- Winding returns with exact integer match detect topological loops.
- Static curvature regularity (from initial ratios) cleanly separates
  sheet (100% irregular, depth > igd) from helix (58% regular).
- The winding value 506 = 2×11×23, and 506/153 = [3,3,3,1,11] — the ratio
  to Sol-Carbon has CF coefficients in the {1,2,3} coherent neighborhood.

Run: python tools/engine/sheet_geometry_investigation.py
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, hydrated_ratio, to_cf, cf_length, from_cf,
    tension_sequence, SOL_CARBON, WATER_CARBON
)
from tools.engine.curvature import (
    geometric_winding, winding_returns, sequential_ratios
)
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
    evaluate, LYSOZYME_SEQ, LYSOZYME_DSSP,
)
from tools.engine.fold import (
    SS, INTER_GROUND_CF, INTER_GROUND_DEPTH,
    _cf_coherent_count, _is_coupled, _curvature_regularity,
    fold_protein,
)


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
    """Pretty-print factorization."""
    f = factorize(n)
    if not f:
        return "0"
    return " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))


def investigate_winding_returns(seq, dssp, name="Protein"):
    """Investigate winding return geometry for a protein."""
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]

    print(f"\n{'='*70}")
    print(f"  WINDING RETURN GEOMETRY: {name} ({n} residues)")
    print(f"{'='*70}")

    winding = geometric_winding(seq)
    wr_exact = winding_returns(seq, min_separation=INTER_GROUND_DEPTH + 1, max_diff=0)

    # --- Hairpin markers ---
    tensions = tension_sequence(seq)
    hairpins = []
    for i in range(len(tensions)):
        if len(tensions[i]["cf"]) == 1:
            product = tensions[i]["cost"]
            sqrt_p = int(math.sqrt(product) + 0.5)
            if sqrt_p * sqrt_p != product:
                hairpins.append(i)

    print(f"\n  Hairpin markers: {len(hairpins)}")
    for h in hairpins:
        print(f"    pair {h+1} ({tensions[h]['pair']}): product={tensions[h]['cost']} "
              f"CF={tensions[h]['cf']}")

    # --- Exact winding returns ---
    print(f"\n  Exact winding returns: {len(wr_exact)}")
    print(f"  {'i':>4s} {'j':>4s} {'AA':>5s} {'DSSP':>7s} {'sep':>4s} {'factors':>15s} "
          f"{'winding':>8s} {'w_factors':>15s} {'w/153 CF':>15s}")
    print(f"  {'─'*4} {'─'*4} {'─'*5} {'─'*7} {'─'*4} {'─'*15} "
          f"{'─'*8} {'─'*15} {'─'*15}")

    for r in wr_exact:
        i, j = r["pos_i"], r["pos_j"]
        sep = r["separation"]
        w = abs(int(winding[i]))
        d_i = dssp[i] if i < n else "?"
        d_j = dssp[j] if j < n else "?"

        # CF of winding / Sol-Carbon
        if w > 0:
            w_sc = to_cf(Fraction(w, 153))
            w_sc_str = str(w_sc[:5])
        else:
            w_sc_str = "[0]"

        # Check if return spans a hairpin
        spans = any(i <= h <= j for h in hairpins)
        span_mark = " ←HAIRPIN" if spans else ""

        print(f"  {i+1:>4d} {j+1:>4d} {seq[i]}-{seq[j]} {d_i}/{d_j:>4s} "
              f"{sep:>4d} {factor_str(sep):>15s} "
              f"{w:>8d} {factor_str(w):>15s} {w_sc_str:>15s}{span_mark}")

    # --- Sheet positions vs winding return positions ---
    actual_sheets = set(i for i in range(n) if dssp[i] == 'E')
    wr_positions = set()
    for r in wr_exact:
        wr_positions.add(r["pos_i"])
        wr_positions.add(r["pos_j"])

    print(f"\n  DSSP sheet positions: {sorted(i+1 for i in actual_sheets)}")
    print(f"  Winding return positions: {sorted(i+1 for i in wr_positions)}")
    overlap = actual_sheets & wr_positions
    print(f"  Overlap: {sorted(i+1 for i in overlap)} ({len(overlap)}/{len(actual_sheets)})")

    return wr_exact, hairpins, winding


def investigate_position_58(seq, dssp):
    """Deep investigation of position 58's topological adjacency."""
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]

    print(f"\n{'='*70}")
    print(f"  POSITION 58 TOPOLOGICAL INVESTIGATION")
    print(f"{'='*70}")

    winding = geometric_winding(seq)

    # The winding return: 44(N) ↔ 58(I) with winding value -506
    pos_a, pos_b = 43, 57  # 0-indexed
    w = abs(int(winding[pos_a]))

    print(f"\n  Return pair: pos {pos_a+1}({seq[pos_a]}, DSSP={dssp[pos_a]}) "
          f"↔ pos {pos_b+1}({seq[pos_b]}, DSSP={dssp[pos_b]})")
    print(f"  Winding value: {winding[pos_a]:.0f} (exact match: {winding[pos_a] == winding[pos_b]})")

    # Winding value structure
    print(f"\n  --- Winding value {w} ---")
    print(f"  Factorization: {w} = {factor_str(w)}")
    w_sc = Fraction(w, 153)
    w_cf = to_cf(w_sc)
    print(f"  w/Sol-Carbon = {w}/153 = {float(w_sc):.6f}")
    print(f"  CF(w/153) = {w_cf}")
    print(f"  depth = {len(w_cf)}, cost = {cf_length(w_cf)}")

    # Convergents
    print(f"  Convergents:")
    for k in range(1, len(w_cf) + 1):
        conv = from_cf(w_cf[:k])
        print(f"    [{w_cf[:k]}] = {conv} = {float(conv):.6f}")

    # Cross-position geometry
    r_a = aa_ratio(seq[pos_a])
    r_b = aa_ratio(seq[pos_b])
    print(f"\n  --- Cross-position geometry ---")
    print(f"  r({pos_a+1}) = {r_a} = {float(r_a):.6f} ({seq[pos_a]})")
    print(f"  r({pos_b+1}) = {r_b} = {float(r_b):.6f} ({seq[pos_b]})")

    product = r_a * r_b
    product_cf = to_cf(product)
    print(f"  Product r_a × r_b = {float(product):.6f}")
    print(f"    CF = {product_cf}")
    print(f"    depth = {len(product_cf)}, cost = {cf_length(product_cf)}")
    print(f"    denominator = {product.denominator} = {factor_str(product.denominator)}")

    ratio = Fraction(max(r_a, r_b), min(r_a, r_b)) if r_a != r_b else Fraction(1)
    ratio_cf = to_cf(ratio)
    print(f"  Ratio max/min = {float(ratio):.6f}")
    print(f"    CF = {ratio_cf}")
    print(f"    depth = {len(ratio_cf)}, cost = {cf_length(ratio_cf)}")

    # Separation structure
    sep = pos_b - pos_a
    print(f"\n  --- Separation {sep} ---")
    print(f"  {sep} = {factor_str(sep)}")
    print(f"  {sep}/igd = {sep}/{INTER_GROUND_DEPTH} = {Fraction(sep, INTER_GROUND_DEPTH)}")
    print(f"  CF({sep}/igd) = {to_cf(Fraction(sep, INTER_GROUND_DEPTH))}")

    # Curvature path between the two positions
    print(f"\n  --- Curvature path {pos_a+1} → {pos_b+1} ---")
    print(f"  {'Pos':>4s} {'AA':>3s} {'DSSP':>5s} {'Winding':>8s} {'Delta':>7s} {'D factors':>15s}")
    for i in range(pos_a, min(pos_b + 1, n)):
        delta = int(winding[i+1] - winding[i]) if i + 1 < len(winding) else 0
        d = dssp[i] if i < len(dssp) else "?"
        d_fact = factor_str(abs(delta)) if delta != 0 else "0"
        print(f"  {i+1:>4d} {seq[i]:>3s} {d:>5s} {winding[i]:>8.0f} {delta:>+7d} {d_fact:>15s}")

    # What is the net curvature contribution of each structural region?
    print(f"\n  --- Regional curvature contributions ---")
    regions = [
        ("Sheet strand 1 (44-46)", pos_a, 45),
        ("Turn (47-48)", 46, 47),
        ("Sheet strand 2 (49-52)", 48, 51),
        ("Coil exit (53-58)", 52, pos_b),
    ]
    for label, start, end in regions:
        w_start = winding[start]
        w_end = winding[end + 1] if end + 1 < len(winding) else winding[end]
        net = int(w_end - w_start)
        print(f"  {label}: Δw = {net:+d} ({factor_str(abs(net)) if net != 0 else '0'})")


def investigate_static_regularity(seq, dssp, name="Protein"):
    """Analyze static curvature regularity distribution by SS type."""
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]

    print(f"\n{'='*70}")
    print(f"  STATIC CURVATURE REGULARITY: {name}")
    print(f"{'='*70}")

    # Compute static curvatures from initial ratios
    field = [aa_ratio(c) for c in seq]
    curvatures = []
    for i in range(n - 1):
        ratio = field[i + 1] / field[i]
        cf = to_cf(ratio)
        mag = cf_length(cf)
        sign = 1 if float(ratio) >= 1.0 else -1
        curvatures.append(sign * mag)

    static_reg = [_curvature_regularity(i, curvatures, [False] * n) for i in range(n)]

    # Distribution by SS type
    for ss_type, label in [('H', 'Helix'), ('E', 'Sheet'), ('C', 'Coil')]:
        positions = [i for i in range(n) if dssp[i] == ss_type]
        if not positions:
            continue
        regs = [static_reg[i] for i in positions]
        regular = sum(1 for r in regs if r <= INTER_GROUND_DEPTH)
        irregular = sum(1 for r in regs if r > INTER_GROUND_DEPTH)
        print(f"\n  {label}: {len(positions)} positions, "
              f"{regular} regular ({regular/len(positions):.0%}), "
              f"{irregular} irregular ({irregular/len(positions):.0%})")
        dist = Counter(regs)
        for d in sorted(dist):
            bar = "█" * dist[d]
            marker = " ← ≤ igd" if d <= INTER_GROUND_DEPTH else ""
            print(f"    depth {d}: {dist[d]:2d} {bar}{marker}")


def investigate_error_classification(seq, dssp, name="Protein"):
    """Classify prediction errors against DSSP."""
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]
    pred = fold_protein(seq)
    result = evaluate(pred, dssp)

    print(f"\n{'='*70}")
    print(f"  ERROR CLASSIFICATION: {name}")
    print(f"{'='*70}")

    print(f"\n  Q3 = {result['q3']:.1%}")
    for c in 'HEC':
        d = result['classes'][c]
        print(f"  {c}: sens={d['sensitivity']:.0%} prec={d['precision']:.0%} "
              f"F1={d['f1']:.2f} act={d['actual']} pred={d['predicted']} tp={d['tp']}")

    # Classify errors
    errors = []
    for i in range(n):
        if pred[i] != dssp[i]:
            at_boundary = any(0 <= i + d < n and dssp[i + d] != dssp[i]
                              for d in [-2, -1, 1, 2])
            errors.append({
                "pos": i,
                "aa": seq[i],
                "dssp": dssp[i],
                "pred": pred[i],
                "boundary": at_boundary,
                "self_t": SELF_TENSION.get(seq[i], 50),
            })

    boundary_count = sum(1 for e in errors if e["boundary"])
    print(f"\n  Total errors: {len(errors)}/{n}")
    print(f"  Boundary-adjacent: {boundary_count} ({boundary_count/len(errors):.0%} of errors)")

    # Group by error type
    error_types = Counter((e["dssp"], e["pred"]) for e in errors)
    print(f"\n  Error types:")
    for (actual, predicted), count in error_types.most_common():
        label = {"H": "Helix", "E": "Sheet", "C": "Coil"}
        print(f"    {label[actual]} → {label[predicted]}: {count}")

    # Detail
    print(f"\n  {'Pos':>4s} {'AA':>3s} {'ST':>4s} {'DSSP':>5s} {'Pred':>5s} {'Bnd':>4s}")
    print(f"  {'─'*4} {'─'*3} {'─'*4} {'─'*5} {'─'*5} {'─'*4}")
    for e in errors:
        bnd = "BND" if e["boundary"] else ""
        print(f"  {e['pos']+1:>4d} {e['aa']:>3s} {e['self_t']:>4d} "
              f"{e['dssp']:>5s} {e['pred']:>5s} {bnd:>4s}")


def main():
    seq = LYSOZYME_SEQ
    dssp = LYSOZYME_DSSP
    n = min(len(seq), len(dssp))

    # 1. Winding return geometry
    investigate_winding_returns(seq[:n], dssp[:n], "Lysozyme")

    # 2. Position 58 deep dive
    investigate_position_58(seq[:n], dssp[:n])

    # 3. Static regularity distribution
    investigate_static_regularity(seq[:n], dssp[:n], "Lysozyme")

    # 4. Error classification
    investigate_error_classification(seq[:n], dssp[:n], "Lysozyme")

    # 5. Ubiquitin
    ubq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    ubq_d = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'
    n2 = min(len(ubq), len(ubq_d))

    investigate_winding_returns(ubq[:n2], ubq_d[:n2], "Ubiquitin")
    investigate_static_regularity(ubq[:n2], ubq_d[:n2], "Ubiquitin")
    investigate_error_classification(ubq[:n2], ubq_d[:n2], "Ubiquitin")


if __name__ == "__main__":
    main()
