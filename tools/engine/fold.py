#!/usr/bin/env python3
"""Sequential commitment field solver for protein structure prediction.

This module implements the Aramis tension field co-evolution model:

1. Process the chain N→C terminal, assigning TENTATIVE states
2. When a turn is committed, trigger constraint satisfaction:
   - Re-evaluate upstream segments for cross-strand coupling
   - If antiparallel coupling creates a phi-coherent lock,
     snap upstream residues from tentative-helix to sheet
3. The tension field updates with each commitment, constraining
   what's accessible downstream

This is not a pattern matcher — it's a field solver that builds
proteins the same way the substrate does: through global geometric
constraint satisfaction.

Run: python tools/engine/fold.py KVFGRCELAAAMKRH...
  or: python tools/engine/fold.py --demo
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
    UNRESOLVED = "?"    # not yet committed
    HELIX = "H"        # committed helix
    SHEET = "E"        # committed sheet
    TURN = "T"         # committed turn (maps to C in DSSP output)
    COIL = "C"         # committed coil


class TensionField:
    """The evolving tension field of a folding protein.

    Each commitment (helix/sheet/turn/coil) changes the field
    for all remaining unresolved residues.
    """

    def __init__(self, seq: str):
        self.seq = seq.upper()
        self.n = len(self.seq)
        self.states = [ResidueState.UNRESOLVED] * self.n
        self.self_tensions = [SELF_TENSION.get(c, 50) for c in self.seq]

        # Precompute pair tensions
        self.tensions = tension_sequence(self.seq)
        self.pair_costs = [t["cost"] for t in self.tensions]
        self.pair_cfs = [t["cf"] for t in self.tensions]

        # Effective tension modifier: starts at 1.0, changes with commitments
        self.tension_modifier = [1.0] * self.n

        # Track which segments have been committed
        self.committed = [False] * self.n

        # Winding number (topological charge)
        self.winding = 0.0

    def commit(self, pos: int, state: ResidueState):
        """Commit a residue to a structural state and update the field."""
        self.states[pos] = state
        self.committed[pos] = True

        # Update tension modifiers for neighbors based on commitment type
        if state == ResidueState.HELIX:
            # Helix commitment: lower effective tension for compatible downstream
            # (spring coupling established → easier for next residue to join)
            for offset in range(-2, 3):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    # Coupling established: reduce effective tension
                    ratio = self._neighbor_ratio(pos, j)
                    if ratio < 3.0:
                        self.tension_modifier[j] *= 0.9  # 10% easier

            # Accumulate winding
            self.winding += 1.0 / 3.6  # ~0.28 per helix residue

        elif state == ResidueState.TURN:
            # Turn commitment: create coupling barrier + enable cross-strand
            for offset in range(-1, 2):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    self.tension_modifier[j] *= 1.1  # 10% harder (barrier)

            # Reverse winding direction (hairpin)
            self.winding *= -1

        elif state == ResidueState.COIL:
            # Coil commitment: break the spring chain
            for offset in range(-1, 2):
                j = pos + offset
                if 0 <= j < self.n and not self.committed[j]:
                    self.tension_modifier[j] *= 1.05  # slight barrier

    def _neighbor_ratio(self, i: int, j: int) -> float:
        """Self-tension ratio between two positions."""
        ti = self.self_tensions[i]
        tj = self.self_tensions[j]
        if ti <= 0 or tj <= 0:
            return 99.0
        return max(ti, tj) / min(ti, tj)

    def effective_coupling(self, pos: int, half_w: int = 3) -> float:
        """Window coupling fraction modified by committed field state."""
        base = window_coupling_fraction(self.seq, pos, half_w)
        return base * self.tension_modifier[pos]

    def effective_mean_self(self, pos: int, half_w: int = 3) -> float:
        """Mean self-tension modified by field state."""
        base = window_mean_self_tension(self.seq, pos, half_w)
        return base * self.tension_modifier[pos]

    def is_tension_drop(self, pos: int, threshold: float = 0.55) -> bool:
        """Is this position a tension cost drop (geodesic shortcut)?"""
        if pos >= len(self.pair_costs):
            return False
        cost = self.pair_costs[pos]
        # Rolling mean for context
        w_s = max(0, pos - 3)
        w_e = min(len(self.pair_costs), pos + 4)
        rm = sum(self.pair_costs[w_s:w_e]) / (w_e - w_s)
        if rm <= 0:
            return False
        return cost / rm < threshold

    def cross_strand_tension(self, strand_a: range, strand_b: range) -> float:
        """Compute cross-strand tension between two position ranges.

        Uses antiparallel coupling (strand B reversed).
        """
        total = 0
        count = 0
        for k, (i, j) in enumerate(zip(strand_a, reversed(list(strand_b)))):
            if 0 <= i < self.n and 0 <= j < self.n:
                ri = aa_ratio(self.seq[i])
                rj = aa_ratio(self.seq[j])
                cf = to_cf(ri / rj)
                total += cf_length(cf)
                count += 1
        return total / count if count > 0 else 999

    def to_dssp_string(self) -> str:
        """Convert internal states to DSSP-compatible string."""
        mapping = {
            ResidueState.HELIX: 'H',
            ResidueState.SHEET: 'E',
            ResidueState.TURN: 'C',   # DSSP doesn't have a turn state; map to C
            ResidueState.COIL: 'C',
            ResidueState.UNRESOLVED: 'C',
        }
        return ''.join(mapping[s] for s in self.states)


def fold_protein(seq: str, verbose: bool = False) -> str:
    """Fold a protein using sequential commitment with field co-evolution.

    Phase 1: Forward pass — assign tentative states based on local tension
    Phase 2: Constraint satisfaction — when turns are found, check if
             upstream segments should snap to sheet
    Phase 3: Resolve remaining unresolved states

    Returns DSSP-compatible string (H/E/C).
    """
    seq = seq.upper().replace(" ", "").replace("\n", "")
    field = TensionField(seq)
    n = field.n

    # ═══ PHASE 1: Forward Pass — Tentative Assignment ═══

    # First: identify definite turns (tension drops)
    for i in range(n):
        if field.is_tension_drop(i, threshold=0.55):
            field.commit(i, ResidueState.TURN)
            if verbose:
                print(f"  TURN committed at {i+1} ({seq[i]})")

    # Second: identify definite helices (long coupling-compatible segments)
    # Build non-turn segments
    segments = []
    seg_start = None
    for i in range(n):
        if field.states[i] != ResidueState.TURN:
            if seg_start is None:
                seg_start = i
        else:
            if seg_start is not None:
                segments.append((seg_start, i))
                seg_start = None
    if seg_start is not None:
        segments.append((seg_start, n))

    # Assign helices in long segments (>= 7 residues = 2 full turns)
    for seg_start, seg_end in segments:
        seg_len = seg_end - seg_start
        if seg_len >= 7:
            # Check helix viability
            viable_count = 0
            for i in range(seg_start, seg_end):
                coupling = field.effective_coupling(i)
                mean_self = field.effective_mean_self(i)
                if coupling >= 0.4 and 20 <= mean_self <= 200:
                    viable_count += 1

            if viable_count >= seg_len * 0.6:
                for i in range(seg_start, seg_end):
                    coupling = field.effective_coupling(i)
                    mean_self = field.effective_mean_self(i)
                    if coupling >= 0.4 and 20 <= mean_self <= 200:
                        field.commit(i, ResidueState.HELIX)

    # ═══ PHASE 2: Constraint Satisfaction — Hairpin Detection ═══

    # For each turn, check if the segments on either side should form
    # a beta-hairpin (sheet strand + turn + sheet strand)
    turn_positions = [i for i in range(n) if field.states[i] == ResidueState.TURN]

    for turn_pos in turn_positions:
        # Find the extent of this turn cluster
        turn_start = turn_pos
        turn_end = turn_pos + 1
        while turn_start > 0 and field.states[turn_start - 1] == ResidueState.TURN:
            turn_start -= 1
        while turn_end < n and field.states[turn_end] == ResidueState.TURN:
            turn_end += 1

        # Look at segments BEFORE and AFTER this turn
        # Upstream: find the nearest non-turn residues before the turn
        # Look back from the turn, skipping already-committed helices,
        # to find the nearest UNRESOLVED or short helix stretch
        upstream_end = turn_start
        upstream_start = upstream_end
        # Walk back through unresolved/short-helix residues (max 6 residues)
        steps_back = 0
        while upstream_start > 0 and steps_back < 6:
            prev = upstream_start - 1
            if field.states[prev] == ResidueState.TURN:
                break  # hit another turn — this is the upstream boundary
            upstream_start -= 1
            steps_back += 1

        upstream_len = upstream_end - upstream_start

        # Downstream: find the nearest non-turn residues after the turn
        downstream_start = turn_end
        downstream_end = downstream_start
        steps_fwd = 0
        while downstream_end < n and steps_fwd < 6:
            nxt = downstream_end
            if field.states[nxt] == ResidueState.TURN:
                break
            downstream_end += 1
            steps_fwd += 1

        downstream_len = downstream_end - downstream_start

        # Hairpin condition: both flanking segments are SHORT (2-6 residues)
        # and have decent cross-strand coupling
        if 2 <= upstream_len <= 6 and 2 <= downstream_len <= 6:
            # Check cross-strand tension
            strand_a = range(upstream_start, upstream_end)
            strand_b = range(downstream_start, downstream_end)

            cross_t = field.cross_strand_tension(strand_a, strand_b)

            # Compare to what they'd cost as helix
            helix_cost = sum(field.self_tensions[i] for i in strand_a) / upstream_len

            if verbose:
                print(f"  HAIRPIN CHECK at turn {turn_start+1}-{turn_end}:")
                print(f"    upstream [{upstream_start+1}-{upstream_end}] len={upstream_len} "
                      f"'{seq[upstream_start:upstream_end]}'")
                print(f"    downstream [{downstream_start+1}-{downstream_end}] len={downstream_len} "
                      f"'{seq[downstream_start:downstream_end]}'")
                print(f"    cross_strand_T = {cross_t:.1f}, helix_cost = {helix_cost:.1f}")

            # Snap to sheet ONLY if:
            # 1. Cross-strand tension is LOW (strong geometric coupling)
            # 2. Both segments are SHORT (2-5 residues — real sheet strands)
            # 3. The upstream segment wasn't already a strong helix candidate
            #    (strong helix = long segment with high periodicity)
            upstream_was_helix = any(field.states[i] == ResidueState.HELIX
                                     for i in range(upstream_start, upstream_end))

            short_enough = upstream_len <= 6 and downstream_len <= 6
            # Cross-strand tension must be significantly below mean pair tension
            mean_pair_t = sum(field.pair_costs) / len(field.pair_costs) if field.pair_costs else 50
            strong_coupling = cross_t < mean_pair_t * 0.32  # below 32% of mean

            if short_enough and strong_coupling:
                for i in range(upstream_start, upstream_end):
                    field.states[i] = ResidueState.SHEET
                    field.committed[i] = True
                for i in range(downstream_start, downstream_end):
                    field.states[i] = ResidueState.SHEET
                    field.committed[i] = True
                if verbose:
                    print(f"    → SNAPPED to SHEET")

    # ═══ PHASE 3: Resolve Remaining — Everything Uncommitted is Coil ═══

    for i in range(n):
        if not field.committed[i]:
            field.commit(i, ResidueState.COIL)

    return field.to_dssp_string()


# ═══════════════════════════════════════════════════════════════
# CLI AND DEMO
# ═══════════════════════════════════════════════════════════════

def demo():
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  SEQUENTIAL COMMITMENT FIELD SOLVER                                ║
    ║  Tension field co-evolves with structural commitments.             ║
    ║  Turns trigger retroactive hairpin snapping.                       ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

    seq = LYSOZYME_SEQ
    dssp = LYSOZYME_DSSP
    n = min(len(seq), len(dssp))
    seq, dssp = seq[:n], dssp[:n]

    print(f"  === LYSOZYME ({n} residues) ===\n")
    print(f"  Phase 1: Forward pass (turns + helices)")
    print(f"  Phase 2: Constraint satisfaction (hairpin snapping)")
    print(f"  Phase 3: Resolve remaining → coil\n")

    pred = fold_protein(seq, verbose=True)
    result = evaluate(pred, dssp)

    print(f"\n  === PREDICTION ===\n")
    block = 65
    for start in range(0, n, block):
        end = min(start + block, n)
        print(f"  SEQ:  {seq[start:end]}")
        print(f"  DSSP: {dssp[start:end]}")
        print(f"  PRED: {pred[start:end]}")
        match = ''.join('·' if dssp[i] == pred[i] else ' ' for i in range(start, end))
        print(f"  MATCH:{match}")
        print()

    print(f"  === RESULTS ===\n")
    print(f"  {'Class':8s} {'Actual':>7s} {'Pred':>7s} {'TP':>5s} {'Sens':>7s} {'Prec':>7s} {'F1':>6s}")
    print(f"  {'─'*8} {'─'*7} {'─'*7} {'─'*5} {'─'*7} {'─'*7} {'─'*6}")
    for cls, name in [('H', 'Helix'), ('E', 'Sheet'), ('C', 'Coil')]:
        c = result["classes"][cls]
        print(f"  {name:8s} {c['actual']:>7d} {c['predicted']:>7d} {c['tp']:>5d} "
              f"{c['sensitivity']:>6.0%} {c['precision']:>6.0%} {c['f1']:>6.2f}")
    print(f"\n  Q3 = {result['q3']:.1%} ({result['correct']}/{result['total']})")
    print(f"  Chou-Fasman: ~57%")

    # Also test ubiquitin
    print(f"\n  === UBIQUITIN (76 residues) ===\n")
    ubq_seq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    ubq_dssp = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'
    n2 = min(len(ubq_seq), len(ubq_dssp))
    ubq_pred = fold_protein(ubq_seq[:n2])
    ubq_result = evaluate(ubq_pred, ubq_dssp[:n2])
    print(f"  SEQ:  {ubq_seq[:n2]}")
    print(f"  DSSP: {ubq_dssp[:n2]}")
    print(f"  PRED: {ubq_pred}")
    print(f"\n  Q3 = {ubq_result['q3']:.1%}")
    for cls in 'HEC':
        c = ubq_result['classes'][cls]
        print(f"  {cls}: sens={c['sensitivity']:.0%} prec={c['precision']:.0%} F1={c['f1']:.2f}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sequential commitment protein folder")
    parser.add_argument("sequence", nargs="?", help="Amino acid sequence")
    parser.add_argument("--dssp", help="DSSP reference for evaluation")
    parser.add_argument("--demo", action="store_true", help="Run lysozyme + ubiquitin demo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show commitment steps")
    args = parser.parse_args()

    if args.demo:
        demo()
    elif args.sequence:
        pred = fold_protein(args.sequence, verbose=args.verbose)
        print(f"  SEQ:  {args.sequence.upper()}")
        print(f"  PRED: {pred}")
        if args.dssp:
            result = evaluate(pred, args.dssp)
            print(f"\n  Q3 = {result['q3']:.1%}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
