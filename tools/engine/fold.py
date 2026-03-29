#!/usr/bin/env python3
"""Sequential commitment field solver for protein structure prediction.

Implements the Aramis tension field co-evolution model using ALL computed
features: pair tensions, CF expansions, periodicity, singularity detection,
cross-strand coupling, and hydration.

Phase 1: HELIX via pair tension periodicity + coupling + hydration
Phase 2: TURNS from tension drops in non-helix regions
Phase 3: SHEETS via hairpin snapping at turns
Phase 4: COIL for everything remaining

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
    aa_ratio, to_cf, cf_length, tension_sequence, tension_periodicity, SOL_CARBON
)
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
    window_coupling_fraction, window_mean_self_tension,
    neighbor_tension_ratio, evaluate,
    LYSOZYME_SEQ, LYSOZYME_DSSP,
)


class ResidueState(Enum):
    UNRESOLVED = "?"
    HELIX = "H"
    SHEET = "E"
    TURN = "T"
    COIL = "C"


class TensionField:
    """The evolving tension field of a folding protein."""

    def __init__(self, seq: str):
        self.seq = seq.upper()
        self.n = len(self.seq)
        self.states = [ResidueState.UNRESOLVED] * self.n
        self.self_tensions = [SELF_TENSION.get(c, 50) for c in self.seq]
        self.tensions = tension_sequence(self.seq)
        self.pair_costs = [t["cost"] for t in self.tensions]
        self.pair_cfs = [t["cf"] for t in self.tensions]
        self.tension_modifier = [1.0] * self.n
        self.committed = [False] * self.n
        self.winding = 0.0

    def commit(self, pos: int, state: ResidueState):
        self.states[pos] = state
        self.committed[pos] = True
        if state == ResidueState.HELIX:
            for offset in range(-2, 3):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    ratio = self._nbr_ratio(pos, j)
                    if ratio < 3.0:
                        self.tension_modifier[j] *= 0.9
            self.winding += 1.0 / 3.6
        elif state == ResidueState.TURN:
            for offset in range(-1, 2):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    self.tension_modifier[j] *= 1.1
            self.winding *= -1
        elif state == ResidueState.COIL:
            for offset in range(-1, 2):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    self.tension_modifier[j] *= 1.05

    def _nbr_ratio(self, i, j):
        ti, tj = self.self_tensions[i], self.self_tensions[j]
        if ti <= 0 or tj <= 0:
            return 99.0
        return max(ti, tj) / min(ti, tj)

    def eff_coupling(self, pos, hw=3):
        return window_coupling_fraction(self.seq, pos, hw) * self.tension_modifier[pos]

    def eff_mean_self(self, pos, hw=3):
        return window_mean_self_tension(self.seq, pos, hw) * self.tension_modifier[pos]

    def is_tension_drop(self, pos, threshold=0.55):
        if pos >= len(self.pair_costs):
            return False
        cost = self.pair_costs[pos]
        ws = max(0, pos - 3)
        we = min(len(self.pair_costs), pos + 4)
        rm = sum(self.pair_costs[ws:we]) / (we - ws)
        return (cost / rm < threshold) if rm > 0 else False

    def cross_strand_tension(self, strand_a, strand_b):
        total, count = 0, 0
        for i, j in zip(strand_a, reversed(list(strand_b))):
            if 0 <= i < self.n and 0 <= j < self.n:
                ri, rj = aa_ratio(self.seq[i]), aa_ratio(self.seq[j])
                total += cf_length(to_cf(ri / rj))
                count += 1
        return total / count if count > 0 else 999

    def to_dssp(self):
        m = {ResidueState.HELIX: 'H', ResidueState.SHEET: 'E',
             ResidueState.TURN: 'C', ResidueState.COIL: 'C',
             ResidueState.UNRESOLVED: 'C'}
        return ''.join(m[s] for s in self.states)


def fold_protein(seq: str, verbose: bool = False) -> str:
    """Fold a protein using ALL computed tension features + field co-evolution."""
    seq = seq.upper().replace(" ", "").replace("\n", "")
    field = TensionField(seq)
    n = field.n
    costs = field.pair_costs
    cfs = field.pair_cfs

    # === HYDRATION COUPLING ===
    POLAR = {'S', 'T', 'N', 'D', 'Q', 'E', 'K', 'R', 'H'}
    for i in range(n):
        if seq[i] in POLAR:
            field.tension_modifier[i] *= 0.85  # water dampens polar tension

    # === PRECOMPUTE: Periodicity + CF singularities ===
    periodicity_map = [0.0] * n
    for i in range(n - 8 + 1):
        seg = costs[max(0, i):i + 8]
        if len(seg) >= 4:
            period, strength = tension_periodicity(seg, max_period=6)
            if period in (3, 4, 5):
                for k in range(i, min(i + 8, n)):
                    periodicity_map[k] = max(periodicity_map[k], strength)

    cf_boundary = [False] * n
    for i in range(len(cfs)):
        if any(c > 100 for c in cfs[i]):
            for k in (i, i + 1):
                if 0 <= k < n:
                    cf_boundary[k] = True

    # === PHASE 1: TURNS FIRST (topology defines everything) ===
    # Detect tension drops, then extend turns to include immediate neighbors
    # that also have below-average tension (turns are 2-4 residues, not just 1)
    raw_drops = set()
    for i in range(n):
        if field.is_tension_drop(i, 0.55):
            raw_drops.add(i)

    # Extend: if position i is a drop, check i-1 and i+1
    # If their tension is below the median, include them in the turn
    median_cost = sorted(costs)[len(costs) // 2] if costs else 50
    turn_set = set(raw_drops)
    for i in raw_drops:
        for offset in (-1, 0, 1):
            j = i + offset
            if 0 <= j < len(costs) and costs[j] < median_cost * 0.60:
                turn_set.add(j)
            if 0 <= j + 1 < n and costs[j] < median_cost * 0.75 if j < len(costs) else False:
                turn_set.add(j + 1)

    for i in sorted(turn_set):
        if i < n:
            field.commit(i, ResidueState.TURN)
            if verbose:
                print(f"  TURN at {i+1} ({seq[i]})")

    # === PHASE 2: HAIRPIN DETECTION (before helix assignment) ===
    turn_positions = [i for i in range(n) if field.states[i] == ResidueState.TURN]
    processed_hp = set()
    mean_pair_t = sum(costs) / len(costs) if costs else 50

    for tp in turn_positions:
        if tp in processed_hp:
            continue
        ts, te = tp, tp + 1
        while ts > 0 and field.states[ts - 1] == ResidueState.TURN:
            ts -= 1
        while te < n and field.states[te] == ResidueState.TURN:
            te += 1
        for t in range(ts, te):
            processed_hp.add(t)

        us = ts
        while us > 0 and ts - us < 6:
            if field.states[us - 1] in (ResidueState.TURN,):
                break
            us -= 1
        de = te
        while de < n and de - te < 6:
            if field.states[de] in (ResidueState.TURN,):
                break
            de += 1

        ulen, dlen = ts - us, de - te
        if ulen >= 2 and dlen >= 2:
            cross_t = field.cross_strand_tension(range(us, ts), range(te, de))
            relative = cross_t / mean_pair_t if mean_pair_t > 0 else 1.0
            if verbose:
                print(f"  HAIRPIN turn {ts+1}-{te}: up=[{us+1}-{ts}] "
                      f"down=[{te+1}-{de}] cross_T={cross_t:.1f} ({relative:.0%})")
            if relative < 0.38:
                for i in range(us, ts):
                    field.states[i] = ResidueState.SHEET
                    field.committed[i] = True
                for i in range(te, de):
                    field.states[i] = ResidueState.SHEET
                    field.committed[i] = True
                if verbose:
                    print(f"    -> SHEET")

    # === PHASE 3: HELIX via periodicity (everything not turn/sheet) ===
    for i in range(n):
        if field.committed[i]:
            continue
        coupling = field.eff_coupling(i)
        mean_self = field.eff_mean_self(i)
        periodic = periodicity_map[i] > 0.30

        if periodic and coupling >= 0.4 and 20 <= mean_self <= 200:
            field.commit(i, ResidueState.HELIX)

    # Bridge 1-residue gaps in helices (not across turns, CF singularities, or sheets)
    for _ in range(2):
        for i in range(1, n - 1):
            if field.states[i] not in (ResidueState.HELIX, ResidueState.TURN, ResidueState.SHEET):
                if (field.states[i-1] == ResidueState.HELIX and
                        field.states[i+1] == ResidueState.HELIX and
                        not cf_boundary[i] and field.self_tensions[i] < 300):
                    field.commit(i, ResidueState.HELIX)

    # (Hairpin detection done in Phase 2 above)
    # === PHASE 4: COIL for everything remaining ===
    for i in range(n):
        if not field.committed[i]:
            field.commit(i, ResidueState.COIL)

    return field.to_dssp()


def demo():
    print("""
    ===============================================================
    SEQUENTIAL COMMITMENT FIELD SOLVER v2
    Uses ALL computed features: pair tensions, CF singularities,
    periodicity, hydration coupling, cross-strand tension.
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
    for c, nm in [('H','Helix'),('E','Sheet'),('C','Coil')]:
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
    for c in 'HEC':
        d = r2['classes'][c]
        print(f"    {c}: sens={d['sensitivity']:.0%} prec={d['precision']:.0%} F1={d['f1']:.2f}")


def main():
    import argparse
    p = argparse.ArgumentParser(description="Protein field solver")
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
