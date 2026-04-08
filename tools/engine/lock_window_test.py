#!/usr/bin/env python3
"""Focused test: LOCK step CF motif window size.

The fold.py LOCK step uses 2 pair CFs: hyd_cfs[i-1] and hyd_cfs[i]
(the pairs TOUCHING position i).

The EXTENSION step uses 3 pair CFs: hyd_cfs[i-1], hyd_cfs[i], hyd_cfs[i+1]

What if LOCK should also use 3? This is a minor asymmetry fix, not a
major architecture change.

Also: what about the SEQUENTIAL ORDER of steps within a cycle?
The 7-step process has a natural ordering where each step sees
the results of ALL previous steps. Let me track what information
each step has access to.
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from enum import Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, hydrated_ratio, to_cf, cf_length, tension_sequence,
    mediant, SOL_CARBON, WATER_CARBON, POLAR_AA
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


def fold_lock_window(seq: str, lock_pairs: int = 2, verbose: bool = False) -> str:
    """Fold with variable LOCK step CF motif window.

    lock_pairs: number of pair CFs to check in LOCK seed step
      2 = current (pairs touching position: i-1, i)
      3 = symmetric (pairs on both sides: i-1, i, i+1) = same as extension
      4 = wider
    """
    seq = seq.upper().replace(" ", "").replace("\n", "")
    n = len(seq)

    field = [aa_ratio(c) for c in seq]
    hyd_field = [hydrated_ratio(c) for c in seq]

    raw_tensions = tension_sequence(seq)
    raw_cfs = [t["cf"] for t in raw_tensions]
    raw_costs = [t["cost"] for t in raw_tensions]
    raw_depths = [len(t["cf"]) for t in raw_tensions]

    self_t = [SELF_TENSION.get(c, 50) for c in seq]

    states = [SS.UNRESOLVED] * n
    locked = [False] * n

    def commit(pos, state):
        if 0 <= pos < n and not locked[pos]:
            states[pos] = state
            locked[pos] = True
            return True
        return False

    cycle = 0
    while True:
        cycle += 1
        changed = False

        hyd_cfs = []
        for i in range(n - 1):
            product = hyd_field[i] * hyd_field[i + 1]
            hyd_cfs.append(to_cf(product))

        curvatures = []
        for i in range(n - 1):
            ratio = field[i + 1] / field[i]
            cf = to_cf(ratio)
            mag = cf_length(cf)
            sign = 1 if float(ratio) >= 1.0 else -1
            curvatures.append(sign * mag)

        # Step 2: DETECT
        for i in range(len(raw_depths)):
            if raw_depths[i] <= INTER_GROUND_DEPTH:
                if commit(i, SS.TURN):
                    changed = True
                if i + 1 < n and commit(i + 1, SS.TURN):
                    changed = True

        # Step 2b: Hairpins
        for i in range(len(raw_cfs)):
            if len(raw_cfs[i]) != 1:
                continue
            product = raw_costs[i]
            sqrt_p = int(math.sqrt(product) + 0.5)
            if sqrt_p * sqrt_p == product:
                continue
            k = 1
            while True:
                up_pos = i - k
                dn_pos = i + 1 + k
                if up_pos < 0 or dn_pos >= n:
                    break
                if locked[up_pos] or locked[dn_pos]:
                    break
                r_up = aa_ratio(seq[up_pos])
                r_dn = aa_ratio(seq[dn_pos])
                cross_product = r_up * r_dn
                cross_depth = len(to_cf(cross_product))
                if cross_depth <= INTER_GROUND_DEPTH * INTER_GROUND_DEPTH:
                    if commit(up_pos, SS.SHEET):
                        changed = True
                    if commit(dn_pos, SS.SHEET):
                        changed = True
                    k += 1
                else:
                    break

        # Step 3: COHERE
        coupled = [False] * n
        for i in range(n):
            if locked[i]:
                continue
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n:
                    if _is_coupled(self_t[i], self_t[j]):
                        coupled[i] = True
                        break

        # Step 4: TENSE
        regularity = [99] * n
        for i in range(n):
            if locked[i]:
                continue
            regularity[i] = _curvature_regularity(i, curvatures, locked)

        # Step 5: LOCK — variable CF motif window
        for i in range(n):
            if locked[i]:
                continue
            if not coupled[i]:
                continue
            if regularity[i] > INTER_GROUND_DEPTH:
                continue

            local_cfs = []
            if lock_pairs == 2:
                # Current: touching pairs only
                if i > 0 and i - 1 < len(hyd_cfs):
                    local_cfs.append(hyd_cfs[i - 1])
                if i < len(hyd_cfs):
                    local_cfs.append(hyd_cfs[i])
            elif lock_pairs == 3:
                # Symmetric: both sides
                for j in range(max(0, i - 1), min(len(hyd_cfs), i + 2)):
                    local_cfs.append(hyd_cfs[j])
            elif lock_pairs == 4:
                for j in range(max(0, i - 2), min(len(hyd_cfs), i + 2)):
                    local_cfs.append(hyd_cfs[j])
            elif lock_pairs == 5:
                for j in range(max(0, i - 2), min(len(hyd_cfs), i + 3)):
                    local_cfs.append(hyd_cfs[j])

            total_coh = 0
            total_inc = 0
            for cf in local_cfs:
                c, ic = _cf_coherent_count(cf)
                total_coh += c
                total_inc += ic

            if total_coh > total_inc:
                if commit(i, SS.HELIX):
                    changed = True
                    if verbose:
                        print(f"  [{cycle}] HELIX SEED {i+1} ({seq[i]}) "
                              f"coh={total_coh} inc={total_inc} pairs={len(local_cfs)}")

        # Step 6: ADJUST helix extension (always uses 3 pair CFs)
        for i in range(n):
            if locked[i]:
                continue
            has_helix_neighbor = False
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n and states[j] == SS.HELIX and locked[j]:
                    has_helix_neighbor = True
                    break
            if not has_helix_neighbor:
                continue
            if not coupled[i]:
                continue

            local_cfs = []
            for j in range(max(0, i - 1), min(len(hyd_cfs), i + 2)):
                local_cfs.append(hyd_cfs[j])

            total_coh = 0
            total_inc = 0
            for cf in local_cfs:
                c, ic = _cf_coherent_count(cf)
                total_coh += c
                total_inc += ic

            if total_coh > total_inc:
                if commit(i, SS.HELIX):
                    changed = True

        # Step 6b: Gap bridging
        for i in range(1, n - 1):
            if locked[i]:
                continue
            if states[i - 1] == SS.HELIX and states[i + 1] == SS.HELIX:
                if locked[i - 1] and locked[i + 1]:
                    r_prev = Fraction(max(self_t[i], self_t[i-1]),
                                      min(self_t[i], self_t[i-1]))
                    r_next = Fraction(max(self_t[i], self_t[i+1]),
                                      min(self_t[i], self_t[i+1]))
                    cf_prev = to_cf(r_prev)
                    cf_next = to_cf(r_next)
                    if (cf_prev[0] <= INTER_GROUND_DEPTH and
                            cf_next[0] <= INTER_GROUND_DEPTH):
                        if commit(i, SS.HELIX):
                            changed = True

        # Step 6c: Mediant diffusion (simultaneous, ±1)
        new_field = list(field)
        new_hyd = list(hyd_field)
        for i in range(n):
            if locked[i]:
                continue
            locked_nbrs_raw = []
            locked_nbrs_hyd = []
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n and locked[j]:
                    locked_nbrs_raw.append(field[j])
                    locked_nbrs_hyd.append(hyd_field[j])
            if locked_nbrs_raw:
                new_field[i] = mediant(field[i], *locked_nbrs_raw)
                new_hyd[i] = mediant(hyd_field[i], *locked_nbrs_hyd)
        field = new_field
        hyd_field = new_hyd

        # Step 7: OUTPUT
        if not changed:
            for i in range(n):
                if not locked[i]:
                    commit(i, SS.COIL)
            break
        if cycle > n:
            for i in range(n):
                if not locked[i]:
                    commit(i, SS.COIL)
            break

    if verbose:
        print(f"  Converged after {cycle} cycles")

    dssp_map = {
        SS.HELIX: 'H', SS.SHEET: 'E',
        SS.TURN: 'C', SS.COIL: 'C',
        SS.UNRESOLVED: 'C'
    }
    return ''.join(dssp_map[s] for s in states)


def main():
    tests = [
        ("Lysozyme", LYSOZYME_SEQ, LYSOZYME_DSSP),
        ("Ubiquitin",
         'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG',
         'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'),
    ]

    print("=" * 70)
    print("  LOCK STEP CF MOTIF WINDOW SIZE TEST")
    print("=" * 70)

    for name, seq, dssp in tests:
        n = min(len(seq), len(dssp))
        seq_t, dssp_t = seq[:n], dssp[:n]

        print(f"\n  === {name} ({n} residues) ===\n")
        print(f"  {'Config':30s} {'Q3':>6s} {'H-F1':>6s} {'E-F1':>6s} {'C-F1':>6s}  {'H-sens':>6s} {'H-prec':>7s}")
        print(f"  {'─'*30} {'─'*6} {'─'*6} {'─'*6} {'─'*6}  {'─'*6} {'─'*7}")

        # Baseline
        pred_v5 = fold_protein(seq_t)
        r_v5 = evaluate(pred_v5, dssp_t)
        print(f"  {'v5 baseline (2 pairs)':30s} {r_v5['q3']:>5.1%} "
              f"{r_v5['classes']['H']['f1']:>5.2f} "
              f"{r_v5['classes']['E']['f1']:>5.2f} "
              f"{r_v5['classes']['C']['f1']:>5.2f}  "
              f"{r_v5['classes']['H']['sensitivity']:>5.0%} "
              f"{r_v5['classes']['H']['precision']:>6.0%}")

        for pairs in [2, 3, 4, 5]:
            pred = fold_lock_window(seq_t, lock_pairs=pairs)
            r = evaluate(pred, dssp_t)
            delta = r['q3'] - r_v5['q3']
            marker = " ★" if delta > 0.005 else " ↓" if delta < -0.005 else ""
            print(f"  {'lock=' + str(pairs) + ' pairs':30s} {r['q3']:>5.1%} "
                  f"{r['classes']['H']['f1']:>5.2f} "
                  f"{r['classes']['E']['f1']:>5.2f} "
                  f"{r['classes']['C']['f1']:>5.2f}  "
                  f"{r['classes']['H']['sensitivity']:>5.0%} "
                  f"{r['classes']['H']['precision']:>6.0%}{marker}")

    # Detailed comparison
    print("\n" + "=" * 70)
    print("  DETAIL: 2 pairs (current) vs 3 pairs (symmetric)")
    print("=" * 70)

    seq = LYSOZYME_SEQ[:len(LYSOZYME_DSSP)]
    dssp = LYSOZYME_DSSP

    pred2 = fold_lock_window(seq, lock_pairs=2, verbose=False)
    pred3 = fold_lock_window(seq, lock_pairs=3, verbose=False)

    print(f"\n  SEQ:    {seq[:65]}")
    print(f"  DSSP:   {dssp[:65]}")
    print(f"  2-pair: {pred2[:65]}")
    print(f"  3-pair: {pred3[:65]}")
    diff = ''.join('·' if pred2[i] == pred3[i] else '!' for i in range(min(65, len(pred2), len(pred3))))
    print(f"  diff:   {diff}")

    print(f"\n  SEQ:    {seq[65:]}")
    print(f"  DSSP:   {dssp[65:]}")
    print(f"  2-pair: {pred2[65:]}")
    print(f"  3-pair: {pred3[65:]}")
    diff = ''.join('·' if pred2[i] == pred3[i] else '!' for i in range(65, min(len(pred2), len(pred3))))
    print(f"  diff:   {diff}")

    # Show what specific positions change
    print(f"\n  Positions that differ:")
    for i in range(min(len(pred2), len(pred3))):
        if pred2[i] != pred3[i]:
            print(f"    pos {i+1} ({seq[i]}): 2-pair={pred2[i]} 3-pair={pred3[i]} DSSP={dssp[i]}")


if __name__ == "__main__":
    main()
