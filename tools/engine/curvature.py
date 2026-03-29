#!/usr/bin/env python3
"""Geometric curvature and winding from sequential ratio geodesics.

The sequential ratio R_i = r_{i+1}/r_i encodes the geodesic derivative:
how the Carbon-anchored tension changes from step to step.

CF_length(R_i) = curvature magnitude at step i.
sign(R_i - 1) = curvature direction (+1 increasing, -1 decreasing).
Accumulated signed curvature = geometric winding.

When winding returns to a previously visited value, the chain has
looped back — distant positions are topologically adjacent.
This identifies long-range sheet contacts.

Run: python tools/engine/curvature.py --demo
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import aa_ratio, to_cf, cf_length


def sequential_ratios(seq: str) -> List[Dict]:
    """Compute sequential ratios R_i = r_{i+1}/r_i for the whole chain.

    Returns per-step: ratio, CF, curvature magnitude, sign, pair.
    """
    seq = seq.upper()
    n = len(seq)
    results = []
    for i in range(n - 1):
        r_curr = aa_ratio(seq[i])
        r_next = aa_ratio(seq[i + 1])
        ratio = r_next / r_curr
        cf = to_cf(ratio)
        magnitude = cf_length(cf)
        sign = 1 if float(ratio) >= 1.0 else -1
        results.append({
            "pos": i,
            "pair": seq[i:i+2],
            "ratio": float(ratio),
            "cf": cf,
            "cf_depth": len(cf),
            "magnitude": magnitude,
            "sign": sign,
            "signed_curvature": sign * magnitude,
        })
    return results


def geometric_winding(seq: str) -> List[float]:
    """Compute accumulated geometric winding at each position.

    Winding = sum of signed curvatures from sequential ratios.
    This emerges from the geometry — not imposed.
    """
    ratios = sequential_ratios(seq)
    winding = [0.0]
    for r in ratios:
        winding.append(winding[-1] + r["signed_curvature"])
    return winding


def winding_returns(seq: str, min_separation: int = 10,
                    max_diff: float = 10.0) -> List[Dict]:
    """Find positions where winding returns to a previously visited value.

    When winding(j) ≈ winding(i) with |j - i| > min_separation,
    positions i and j are topologically adjacent (long-range contact).

    Returns list of (pos_i, pos_j, winding_diff) sorted by diff.
    """
    winding = geometric_winding(seq)
    n = len(winding)
    returns = []

    for j in range(min_separation, n):
        for i in range(0, j - min_separation):
            diff = abs(winding[j] - winding[i])
            if diff <= max_diff:
                returns.append({
                    "pos_i": i,
                    "pos_j": j,
                    "aa_i": seq[i] if i < len(seq) else "?",
                    "aa_j": seq[j] if j < len(seq) else "?",
                    "winding_i": winding[i],
                    "winding_j": winding[j],
                    "diff": diff,
                    "separation": j - i,
                })

    returns.sort(key=lambda x: x["diff"])
    return returns


def identify_sheet_contacts(seq: str, dssp: str = None,
                             min_separation: int = 10,
                             max_diff: float = 15.0) -> Dict:
    """Identify long-range sheet contacts from winding returns.

    Positions where accumulated curvature returns to a previous value
    are topologically adjacent — candidates for long-range sheet H-bonds.

    Returns dict with sheet candidate positions and their partners.
    """
    seq = seq.upper()
    n = len(seq)
    winding = geometric_winding(seq)
    returns = winding_returns(seq, min_separation, max_diff)

    # Count how many winding-return partners each position has
    contact_count = [0] * n
    contact_partners = [[] for _ in range(n)]

    for r in returns:
        i, j = r["pos_i"], r["pos_j"]
        if i < n:
            contact_count[i] += 1
            contact_partners[i].append(j)
        if j < n:
            contact_count[j] += 1
            contact_partners[j].append(i)

    # Sheet candidates: positions with multiple winding-return partners
    sheet_candidates = set()
    for i in range(n):
        if contact_count[i] >= 3:  # at least 3 distant partners
            sheet_candidates.add(i)

    return {
        "winding": winding,
        "returns": returns[:50],  # top 50 closest returns
        "contact_count": contact_count,
        "contact_partners": contact_partners,
        "sheet_candidates": sheet_candidates,
    }


def zero_curvature_positions(seq: str) -> List[int]:
    """Find positions where sequential ratio = 1.0 (CF depth = 1).

    These are zero-curvature steps: the chain maintains constant tension.
    Inside helices: AA, LL pairs. Inside sheets: LI, IL pairs.
    """
    ratios = sequential_ratios(seq)
    return [r["pos"] for r in ratios if r["cf_depth"] == 1]


def minimal_curvature_positions(seq: str) -> List[Dict]:
    """Find positions with CF depth = 2 (minimal curvature change).

    These are the simplest possible transitions. ST/TS (depth 2, ratio 5/4)
    are the hairpin markers.
    """
    ratios = sequential_ratios(seq)
    return [r for r in ratios if r["cf_depth"] == 2]


# === Demo ===

def demo():
    print("""
    ================================================================
    GEOMETRIC CURVATURE & WINDING FROM SEQUENTIAL RATIOS
    Winding emerges from CF arithmetic — not imposed.
    Returns to previous winding values = topological adjacency.
    ================================================================
    """)

    # === UBIQUITIN ===
    ubq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    dssp_ubq = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'
    n = min(len(ubq), len(dssp_ubq))

    print(f"  === UBIQUITIN ({n} residues) ===\n")

    # Zero curvature positions
    zeros = zero_curvature_positions(ubq[:n])
    print(f"  Zero-curvature positions (ratio=1.0, CF depth=1):")
    for i in zeros:
        print(f"    pos {i+1}: {ubq[i:i+2]} (DSSP={dssp_ubq[i]})")

    # Minimal curvature positions
    minimals = minimal_curvature_positions(ubq[:n])
    print(f"\n  Minimal-curvature positions (CF depth=2):")
    for m in minimals:
        print(f"    pos {m['pos']+1}: {m['pair']} ratio={m['ratio']:.4f} CF={m['cf']} (DSSP={dssp_ubq[m['pos']]})")

    # Winding profile
    winding = geometric_winding(ubq[:n])
    print(f"\n  Winding profile (accumulated signed curvature):")
    print(f"  {'Pos':>4s} {'AA':>3s} {'DSSP':>5s} {'Winding':>9s}")
    print(f"  {'─'*4} {'─'*3} {'─'*5} {'─'*9}")
    for i in range(0, n, 5):
        print(f"  {i+1:>4d} {ubq[i]:>3s} {dssp_ubq[i]:>5s} {winding[i]:>9.1f}")

    # Winding returns (long-range sheet contacts)
    result = identify_sheet_contacts(ubq[:n], dssp_ubq[:n])

    print(f"\n  Top winding returns (topological adjacency):")
    print(f"  {'Pos_i':>6s} {'Pos_j':>6s} {'AA':>5s} {'Diff':>6s} {'Sep':>5s} {'DSSP':>7s}")
    print(f"  {'─'*6} {'─'*6} {'─'*5} {'─'*6} {'─'*5} {'─'*7}")
    seen = set()
    for r in result["returns"][:25]:
        key = (r["pos_i"], r["pos_j"])
        if key in seen:
            continue
        seen.add(key)
        d_i = dssp_ubq[r["pos_i"]] if r["pos_i"] < n else "?"
        d_j = dssp_ubq[r["pos_j"]] if r["pos_j"] < n else "?"
        print(f"  {r['pos_i']+1:>6d} {r['pos_j']+1:>6d} "
              f"{r['aa_i']}-{r['aa_j']} {r['diff']:>6.1f} {r['separation']:>5d} "
              f"{d_i}/{d_j}")

    # Sheet candidates
    print(f"\n  Sheet candidates (>= 3 winding-return partners):")
    for i in sorted(result["sheet_candidates"]):
        d = dssp_ubq[i] if i < n else "?"
        partners = result["contact_partners"][i][:5]
        print(f"    pos {i+1} ({ubq[i]}, DSSP={d}): partners at {[p+1 for p in partners]}")

    # Evaluate: how many sheet candidates are actual DSSP sheets?
    actual_sheets = set(i for i in range(n) if dssp_ubq[i] == 'E')
    predicted_sheets = result["sheet_candidates"]
    tp = len(actual_sheets & predicted_sheets)
    if actual_sheets:
        sens = tp / len(actual_sheets)
        print(f"\n  Sheet detection: {tp}/{len(actual_sheets)} actual sheets found = {sens:.0%} sensitivity")
    if predicted_sheets:
        prec = tp / len(predicted_sheets)
        print(f"  Precision: {tp}/{len(predicted_sheets)} = {prec:.0%}")

    # === LYSOZYME ===
    print(f"\n  === LYSOZYME ===\n")
    from tools.engine.predict import LYSOZYME_SEQ, LYSOZYME_DSSP
    lyz = LYSOZYME_SEQ
    dssp_lyz = LYSOZYME_DSSP
    nl = min(len(lyz), len(dssp_lyz))

    result_lyz = identify_sheet_contacts(lyz[:nl], dssp_lyz[:nl])
    actual_sheets_lyz = set(i for i in range(nl) if dssp_lyz[i] == 'E')
    predicted_lyz = result_lyz["sheet_candidates"]
    tp_lyz = len(actual_sheets_lyz & predicted_lyz)
    if actual_sheets_lyz:
        print(f"  Sheet detection: {tp_lyz}/{len(actual_sheets_lyz)} actual = "
              f"{tp_lyz/len(actual_sheets_lyz):.0%} sensitivity")
    if predicted_lyz:
        print(f"  Precision: {tp_lyz}/{len(predicted_lyz)} = "
              f"{tp_lyz/len(predicted_lyz):.0%}")
    print(f"  Sheet candidates: {sorted(i+1 for i in predicted_lyz)}")


def main():
    import argparse
    p = argparse.ArgumentParser(description="Geometric curvature and winding analysis")
    p.add_argument("sequence", nargs="?")
    p.add_argument("--dssp")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--winding", action="store_true", help="Show winding profile")
    p.add_argument("--returns", action="store_true", help="Show winding returns")
    args = p.parse_args()

    if args.demo:
        demo()
    elif args.sequence:
        seq = args.sequence.upper()
        if args.winding:
            w = geometric_winding(seq)
            for i in range(len(seq)):
                print(f"  {i+1:>4d} {seq[i]} {w[i]:>10.1f}")
        elif args.returns:
            rets = winding_returns(seq)
            for r in rets[:20]:
                print(f"  {r['pos_i']+1:>4d} ↔ {r['pos_j']+1:>4d}  diff={r['diff']:.1f}")
        else:
            result = identify_sheet_contacts(seq, args.dssp)
            print(f"  Sheet candidates: {sorted(i+1 for i in result['sheet_candidates'])}")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
