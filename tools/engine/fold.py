#!/usr/bin/env python3
"""Geometric field solver for protein structure prediction.

ALL decisions are made by continued fraction arithmetic.
NO floating-point thresholds. NO averaging. NO probability.

Two operations: mediant (⊕) and composition (⊗).
Every criterion is a CF depth check, exact ratio match, or structural invariant.

Backbone geometry (turns, hairpins) uses raw Carbon-anchored ratios.
Environmental coupling (helix vs coil) uses hydrated ratios (composition
with Water/Carbon = 51/62 for polar residues).

Phase 1: GEODESIC BOUNDARIES — pair tension CF depth ≤ inter-ground depth (raw)
Phase 2: HAIRPIN SHEETS — CF depth=1, non-square product (raw backbone)
Phase 3: HELIX SEEDS — CF motif (L > H; hw=1 hydrated) AND φ-coupled
                        AND curvature regularity ≤ inter-ground depth
         HELIX EXTENSION — propagate via coupled neighbors + wider motif
         GAP BRIDGING — fill 1-residue gaps between helices
Phase 4: COIL — everything remaining

Run: python tools/engine/fold.py --demo
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from typing import List, Dict, Tuple, Optional
from enum import Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, hydrated_ratio, to_cf, cf_length, tension_sequence,
    cf_motif_counts, phi_coherence, mediant, SOL_CARBON, WATER_CARBON, POLAR_AA
)
from tools.engine.curvature import (
    geometric_winding, winding_returns, sequential_ratios
)
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
    evaluate, LYSOZYME_SEQ, LYSOZYME_DSSP,
)


class SS(Enum):
    """Secondary structure states."""
    UNRESOLVED = "?"
    HELIX = "H"
    SHEET = "E"
    TURN = "T"
    COIL = "C"


def raw_tension_sequence(seq: str):
    """Raw backbone tension sequence (Carbon-anchored, no hydration).

    Used for turn detection and hairpin criterion where the
    backbone geometry must be exact (ST product = 20, etc.).
    """
    return tension_sequence(seq)


def hydrated_tension_sequence(seq: str):
    """Tension sequence with hydration coupling via composition.

    Polar residues compose with Water/Carbon (51/62) before
    tension computation. Used for CF motif analysis (helix vs coil).
    """
    seq = seq.upper()
    ratios = [hydrated_ratio(c) for c in seq]
    tensions = []
    for i in range(len(ratios) - 1):
        product = ratios[i] * ratios[i + 1]
        cf = to_cf(product)
        tensions.append({
            "pair": seq[i:i+2],
            "cost": cf_length(cf),
            "cf": cf,
            "cf_depth": len(cf),
        })
    return tensions


def is_neighbor_coupled(seq: str, pos: int) -> bool:
    """Check if position has at least one φ-coupled neighbor.

    Two residues are coupled when their self-tension ratio has CF[0] = 1,
    meaning the ratio is < 2:1. This is a strict per-pair geometric check.
    """
    n = len(seq)
    t_self = SELF_TENSION.get(seq[pos], 50)
    for offset in (-1, 1):
        j = pos + offset
        if 0 <= j < n:
            t_j = SELF_TENSION.get(seq[j], 50)
            if t_self > 0 and t_j > 0:
                ratio = Fraction(max(t_self, t_j), min(t_self, t_j))
                cf = to_cf(ratio)
                if cf[0] == 1:  # ratio < 2:1
                    return True
    return False


def window_cf_motif(pair_cfs: list, pos: int, hw: int = 1) -> Tuple[int, int]:
    """Count low (1,2) and high (≥5) CF coefficients in window.

    Returns (total_low, total_high) — exact integer counts.
    Default hw=1: uses only the immediate flanking pair CFs (most local).
    Helix signal: low > high (dense 1s and 2s = tight coil).
    """
    start = max(0, pos - hw)
    end = min(len(pair_cfs), pos + hw + 1)
    total_low = 0
    total_high = 0
    for cf in pair_cfs[start:end]:
        for c in cf:
            if c in (1, 2):
                total_low += 1
            elif c >= 5:
                total_high += 1
    return total_low, total_high


def curvature_regularity_depth(pos: int, increments: list, hw: int = 2) -> int:
    """CF depth of max/min curvature magnitude ratio in ±hw window.

    Measures how REGULAR the local curvature is.
    Low depth (1-2) = very regular (suitable for helix crystallization).
    High depth (3+) = irregular (prevents helix formation).

    The ratio max_mag/min_mag as a continued fraction captures the
    complexity of curvature variation. Helix requires regular curvature;
    sheet and coil have irregular curvature patterns.
    """
    start = max(0, pos - hw)
    end = min(len(increments), pos + hw + 1)
    if start >= end:
        return 10
    mags = [abs(increments[j]) for j in range(start, end)]
    mx = max(mags)
    mn = min(mags)
    if mn == 0:
        mn = 1
    ratio = Fraction(mx, mn)
    cf = to_cf(ratio)
    return len(cf)


def fold_protein(seq: str, verbose: bool = False) -> str:
    """Fold a protein using purely geometric CF criteria.

    Every decision is a CF depth check, exact integer match,
    or ratio of integer counts. No floats. No imposed thresholds.

    The inter-ground depth (CF depth of SHEET_GROUND/HELIX_GROUND = 57/38
    = [1,2], depth 2) serves as the universal structural scale:
    - Boundaries: pair tension CF depth ≤ inter-ground depth
    - Helix regularity: curvature regularity ≤ inter-ground depth
    - Sheet extension: cross-strand depth ≤ 3 × inter-ground depth
    """
    seq = seq.upper().replace(" ", "").replace("\n", "")
    n = len(seq)

    # Raw backbone tensions (for turns + hairpins)
    raw_tensions = raw_tension_sequence(seq)
    raw_cfs = [t["cf"] for t in raw_tensions]
    raw_costs = [t["cost"] for t in raw_tensions]
    raw_depths = [len(t["cf"]) for t in raw_tensions]

    # Hydrated tensions (for CF motif analysis)
    hyd_tensions = hydrated_tension_sequence(seq)
    hyd_cfs = [t["cf"] for t in hyd_tensions]

    # Sequential ratio curvature (for regularity analysis)
    seq_ratios = sequential_ratios(seq)
    increments = [r["signed_curvature"] for r in seq_ratios]

    # Inter-ground depth: the universal structural scale
    # CF depth of SHEET_GROUND/HELIX_GROUND = 57/38 = [1,2] = depth 2
    inter_ground_cf = to_cf(Fraction(SHEET_GROUND, HELIX_GROUND))
    inter_ground_depth = len(inter_ground_cf)  # = 2

    states = [SS.UNRESOLVED] * n
    committed = [False] * n

    def commit(pos, state):
        if 0 <= pos < n and not committed[pos]:
            states[pos] = state
            committed[pos] = True
            return True
        return False

    # === PHASE 1: GEODESIC BOUNDARIES (raw backbone) ===
    # Pair tension CF depth ≤ inter-ground depth = structurally simple transition.
    # These mark where the chain can change direction.
    boundaries = set()
    for i in range(len(raw_depths)):
        if raw_depths[i] <= inter_ground_depth:
            boundaries.add(i)
            commit(i, SS.TURN)
            if i + 1 < n:
                commit(i + 1, SS.TURN)
            if verbose:
                print(f"  BOUNDARY at pair {i+1} ({raw_tensions[i]['pair']}) "
                      f"CF={raw_cfs[i]} depth={raw_depths[i]}")

    # === PHASE 2: HAIRPIN SHEETS (raw backbone) ===
    # ST/TS pairs: CF depth = 1, product is non-square integer.
    # These are exact geometric hairpin markers in the backbone.
    # Extend anti-parallel sheet strands via CROSS-STRAND CONSONANCE:
    # positions equidistant from the hairpin are sheet if their
    # cross-strand tension has CF depth ≤ 3 × inter-ground depth.
    for i in range(len(raw_cfs)):
        if len(raw_cfs[i]) != 1:  # must be CF depth 1
            continue
        product = raw_costs[i]
        sqrt_p = int(math.sqrt(product) + 0.5)
        if sqrt_p * sqrt_p == product:  # perfect square = not hairpin
            continue

        if verbose:
            print(f"  HAIRPIN at pair {i+1} ({raw_tensions[i]['pair']}) product={product}")

        # Extend anti-parallel strands using cross-strand consonance
        for k in range(1, 8):
            up_pos = i - k
            dn_pos = i + 1 + k
            if up_pos < 0 or dn_pos >= n:
                break
            if committed[up_pos] or committed[dn_pos]:
                break

            r_up = aa_ratio(seq[up_pos])
            r_dn = aa_ratio(seq[dn_pos])
            cross_cf = to_cf(r_up * r_dn)
            cross_depth = len(cross_cf)

            if cross_depth <= inter_ground_depth * 3:
                commit(up_pos, SS.SHEET)
                commit(dn_pos, SS.SHEET)
                if verbose:
                    print(f"    STRAND k={k}: pos {up_pos+1},{dn_pos+1} "
                          f"cross_depth={cross_depth}")
            else:
                break

    # === PHASE 3: HELIX SEEDS (hydrated CF motif + coupling + regularity) ===
    # Three geometric criteria for helix crystallization:
    # 1. CF motif: more low coefficients (1,2) than high (≥5) in immediate pairs
    #    (hw=1, hydrated tensions — most local signal)
    # 2. At least one neighbor is φ-coupled (self-tension ratio CF[0] = 1)
    # 3. Curvature regularity: max/min curvature ratio CF depth ≤ inter-ground depth
    #    (helix requires REGULAR local curvature to crystallize)
    for i in range(n):
        if committed[i]:
            continue
        L, H = window_cf_motif(hyd_cfs, i, hw=1)
        if L <= H:
            continue
        if not is_neighbor_coupled(seq, i):
            continue
        reg = curvature_regularity_depth(i, increments, hw=2)
        if reg <= inter_ground_depth:
            commit(i, SS.HELIX)
            if verbose:
                print(f"  HELIX SEED at {i+1} ({seq[i]}) L={L} H={H} reg={reg}")

    # === PHASE 3b: HELIX EXTENSION ===
    # Propagate helix from seeds through coupled neighbors.
    # Extension uses wider window (hw=2) and requires coupling but
    # not the regularity check — once a helix nucleates from a seed,
    # it can extend through positions with less regular curvature
    # as long as the CF motif and coupling conditions hold.
    changed = True
    passes = 0
    while changed and passes < 5:
        changed = False
        passes += 1
        for i in range(n):
            if committed[i]:
                continue
            has_helix_neighbor = False
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n and states[j] == SS.HELIX:
                    has_helix_neighbor = True
                    break
            if not has_helix_neighbor:
                continue
            L, H = window_cf_motif(hyd_cfs, i, hw=2)
            if L <= H:
                continue
            if not is_neighbor_coupled(seq, i):
                continue
            if commit(i, SS.HELIX):
                changed = True
                if verbose:
                    print(f"  HELIX EXT at {i+1} ({seq[i]}) pass={passes} L={L} H={H}")

    # Bridge single-residue gaps in helices
    # Only if coupled to BOTH flanking helix residues (CF[0] ≤ 2)
    for _ in range(2):
        for i in range(1, n - 1):
            if states[i] in (SS.HELIX, SS.TURN, SS.SHEET):
                continue
            if states[i-1] == SS.HELIX and states[i+1] == SS.HELIX:
                t_self = SELF_TENSION.get(seq[i], 50)
                t_prev = SELF_TENSION.get(seq[i-1], 50)
                t_next = SELF_TENSION.get(seq[i+1], 50)
                r_prev = Fraction(max(t_self, t_prev), min(t_self, t_prev))
                r_next = Fraction(max(t_self, t_next), min(t_self, t_next))
                if to_cf(r_prev)[0] <= 2 and to_cf(r_next)[0] <= 2:
                    commit(i, SS.HELIX)

    # === PHASE 4: COIL ===
    for i in range(n):
        if not committed[i]:
            commit(i, SS.COIL)

    # Convert to DSSP-compatible output
    dssp_map = {
        SS.HELIX: 'H', SS.SHEET: 'E',
        SS.TURN: 'C', SS.COIL: 'C',
        SS.UNRESOLVED: 'C'
    }
    return ''.join(dssp_map[s] for s in states)


def demo():
    print("""
    ===============================================================
    GEOMETRIC FIELD SOLVER v4
    All-CF criteria. No float thresholds. No averaging.
    Helix: seed (hw=1 + regularity) + extend (hw=2 + coupled).
    Boundaries: CF depth ≤ inter-ground depth (= 2).
    ===============================================================
    """)

    seq = LYSOZYME_SEQ
    dssp = LYSOZYME_DSSP
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]

    pred = fold_protein(seq, verbose=True)
    result = evaluate(pred, dssp)

    print(f"\n  SEQ:  {seq[:65]}")
    print(f"  DSSP: {dssp[:65]}")
    print(f"  PRED: {pred[:65]}")
    print(f"\n  SEQ:  {seq[65:]}")
    print(f"  DSSP: {dssp[65:]}")
    print(f"  PRED: {pred[65:]}")

    print(f"\n  {'Cls':5s} {'Act':>4s} {'Prd':>4s} {'TP':>4s} {'Sens':>6s} {'Prec':>6s} {'F1':>5s}")
    print(f"  {'---':5s} {'---':>4s} {'---':>4s} {'---':>4s} {'---':>6s} {'---':>6s} {'---':>5s}")
    for c, nm in [('H', 'Helix'), ('E', 'Sheet'), ('C', 'Coil')]:
        d = result['classes'][c]
        print(f"  {nm:5s} {d['actual']:>4d} {d['predicted']:>4d} {d['tp']:>4d} "
              f"{d['sensitivity']:>5.0%} {d['precision']:>5.0%} {d['f1']:>5.2f}")
    print(f"\n  Q3 = {result['q3']:.1%}")

    # Ubiquitin
    ubq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    ubq_d = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'
    n2 = min(len(ubq), len(ubq_d))
    p2 = fold_protein(ubq[:n2])
    r2 = evaluate(p2, ubq_d[:n2])
    print(f"\n  Ubiquitin Q3 = {r2['q3']:.1%}")
    print(f"  SEQ:  {ubq[:n2]}")
    print(f"  DSSP: {ubq_d[:n2]}")
    print(f"  PRED: {p2}")
    for c in 'HEC':
        d = r2['classes'][c]
        print(f"    {c}: sens={d['sensitivity']:.0%} prec={d['precision']:.0%} F1={d['f1']:.2f}")


def main():
    import argparse
    p = argparse.ArgumentParser(description="Geometric protein field solver")
    p.add_argument("sequence", nargs="?")
    p.add_argument("--dssp")
    p.add_argument("--demo", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    if args.demo:
        demo()
    elif args.sequence:
        pred = fold_protein(args.sequence, args.verbose)
        print(f"  SEQ:  {args.sequence.upper()}")
        print(f"  PRED: {pred}")
        if args.dssp:
            r = evaluate(pred, args.dssp)
            print(f"  Q3 = {r['q3']:.1%}")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
