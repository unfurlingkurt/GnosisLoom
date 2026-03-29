#!/usr/bin/env python3
"""Investigation: φ-scaled step windows in the 7-step fold process.

The Aramis Field has 6 temporal domains with φ-based scaling:
  {φ, 1, 1/φ, 1/φ², 1/φ³, 1/φ⁴}

In protein folding, "temporal domain" maps to "spatial scale."
Each of the 7 steps should operate at a DIFFERENT scale, increasing
as Fibonacci numbers (the integer approximation of φ^n):

  Step 2 (DETECT):  Fib(1) = 1  (bond pairs)           ← already correct
  Step 3 (COHERE):  Fib(2) = 1  (nearest coupling)     ← already correct
  Step 4 (TENSE):   Fib(3) = 2  (curvature window)     ← already correct!
  Step 5 (LOCK):    Fib(4) = 3  (CF motif window)      ← currently 1
  Step 6 (ADJUST):  Fib(5) = 5  (diffusion range)      ← currently 1

This script tests the impact of correcting Steps 5 and 6 to their
natural Fibonacci-scaled windows.
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from typing import List, Tuple
from enum import Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, hydrated_ratio, to_cf, cf_length, tension_sequence,
    mediant, SOL_CARBON, WATER_CARBON, POLAR_AA
)
from tools.engine.curvature import sequential_ratios
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
    evaluate, LYSOZYME_SEQ, LYSOZYME_DSSP,
)
from tools.engine.fold import (
    SS, INTER_GROUND_CF, INTER_GROUND_DEPTH,
    _cf_coherent_count, _is_coupled, _curvature_regularity,
    fold_protein,
)

# Fibonacci sequence (integer approximation of φ^n)
# φ^0=1, φ^1≈1.618→2, φ^2≈2.618→3, φ^3≈4.236→4, φ^4≈6.854→7, φ^5≈11.09→11
# But Fibonacci itself: 1, 1, 2, 3, 5, 8, 13...
# Stern-Brocot tree: each level adds a mediant between existing fractions
FIB = [1, 1, 2, 3, 5, 8, 13]

# Step-to-Fibonacci mapping
STEP_SCALES = {
    'detect': FIB[0],   # 1 — bond pairs
    'cohere': FIB[1],   # 1 — nearest coupling
    'tense':  FIB[2],   # 2 — curvature window (ALREADY CORRECT)
    'lock':   FIB[3],   # 3 — CF motif window (CURRENTLY 1)
    'adjust': FIB[4],   # 5 — diffusion range (CURRENTLY 1)
}


def fold_protein_phi(seq: str, lock_hw: int = 3, adjust_hw: int = 5,
                      verbose: bool = False) -> str:
    """Fold with φ-scaled step windows.

    Same as fold_protein but with Fibonacci-scaled half-windows:
    - LOCK step: CF motif window hw=lock_hw (default 3 = Fib(4))
    - ADJUST step: mediant diffusion via iterative nesting up to adjust_hw
    """
    seq = seq.upper().replace(" ", "").replace("\n", "")
    n = len(seq)

    # === STEP 1: SAMPLE ===
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

        # --- Step 1 (per-cycle): Recompute field-derived quantities ---
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

        # --- Step 2: DETECT --- (scale = Fib(1) = 1, unchanged)
        for i in range(len(raw_depths)):
            if raw_depths[i] <= INTER_GROUND_DEPTH:
                if commit(i, SS.TURN):
                    changed = True
                if i + 1 < n and commit(i + 1, SS.TURN):
                    changed = True

        # --- Step 2b: DETECT hairpins --- (same)
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
                cross_cf = to_cf(cross_product)
                cross_depth = len(cross_cf)
                if cross_depth <= INTER_GROUND_DEPTH * INTER_GROUND_DEPTH:
                    if commit(up_pos, SS.SHEET):
                        changed = True
                    if commit(dn_pos, SS.SHEET):
                        changed = True
                    k += 1
                else:
                    break

        # --- Step 3: COHERE --- (scale = Fib(2) = 1, unchanged)
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

        # --- Step 4: TENSE --- (scale = Fib(3) = 2, ALREADY CORRECT)
        regularity = [99] * n
        for i in range(n):
            if locked[i]:
                continue
            regularity[i] = _curvature_regularity(i, curvatures, locked)

        # --- Step 5: LOCK with φ-scaled CF motif window ---
        # Current: hw=1 (only pairs touching position i)
        # φ-scaled: hw=lock_hw=3 (pairs from i-3 to i+3)
        for i in range(n):
            if locked[i]:
                continue
            if not coupled[i]:
                continue
            if regularity[i] > INTER_GROUND_DEPTH:
                continue

            # CF motif from φ-scaled window of pair CFs
            local_cfs = []
            for j in range(max(0, i - lock_hw), min(len(hyd_cfs), i + lock_hw + 1)):
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
                        print(f"  [{cycle}] HELIX SEED at {i+1} ({seq[i]}) "
                              f"coh={total_coh} inc={total_inc} reg={regularity[i]} hw={lock_hw}")

        # --- Step 6: ADJUST helix extension with φ-scaled reach ---
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

            # Extension uses same φ-scaled CF motif window
            local_cfs = []
            for j in range(max(0, i - lock_hw), min(len(hyd_cfs), i + lock_hw + 1)):
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

        # --- Step 6b: Gap bridging --- (same)
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

        # --- Step 6c: Mediant diffusion with φ-scaled reach ---
        # Iterative nesting: blend closest locked positions first,
        # then progressively farther. This gives natural φ-decay
        # because each successive mediant moves the result less.
        new_field = list(field)
        new_hyd = list(hyd_field)
        for i in range(n):
            if locked[i]:
                continue
            val_raw = field[i]
            val_hyd = hyd_field[i]
            has_locked = False
            # Iterate from closest to farthest (SB tree walk pattern)
            for dist in range(1, adjust_hw + 1):
                for offset in (-dist, dist):
                    j = i + offset
                    if 0 <= j < n and locked[j]:
                        val_raw = mediant(val_raw, field[j])
                        val_hyd = mediant(val_hyd, hyd_field[j])
                        has_locked = True
            if has_locked:
                new_field[i] = val_raw
                new_hyd[i] = val_hyd
        field = new_field
        hyd_field = new_hyd

        # --- Step 7: OUTPUT ---
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


def run_comparison():
    """Compare current (linear-scale) vs φ-scaled step windows."""
    print("=" * 70)
    print("  φ-SCALING INVESTIGATION: Step Window Sizes")
    print("=" * 70)

    # Show the Fibonacci mapping
    print("\n  Step-to-Fibonacci mapping:")
    print(f"    Step 2 (DETECT):  hw = {STEP_SCALES['detect']}  (bond pairs)")
    print(f"    Step 3 (COHERE):  hw = {STEP_SCALES['cohere']}  (nearest coupling)")
    print(f"    Step 4 (TENSE):   hw = {STEP_SCALES['tense']}  (curvature window) ← already Fib(3)")
    print(f"    Step 5 (LOCK):    hw = {STEP_SCALES['lock']}  (CF motif window) ← currently 1")
    print(f"    Step 6 (ADJUST):  hw = {STEP_SCALES['adjust']}  (diffusion range) ← currently 1")

    # Test proteins
    tests = [
        ("Lysozyme", LYSOZYME_SEQ, LYSOZYME_DSSP),
        ("Ubiquitin",
         'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG',
         'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'),
    ]

    # Test different window combinations
    configs = [
        ("v5 current (hw=1,1)", 1, 1),
        ("lock=2, adj=1", 2, 1),
        ("lock=3, adj=1 (Fib lock only)", 3, 1),
        ("lock=1, adj=2", 1, 2),
        ("lock=1, adj=3", 1, 3),
        ("lock=1, adj=5", 1, 5),
        ("lock=2, adj=3", 2, 3),
        ("lock=3, adj=5 (full Fibonacci)", 3, 5),
        ("lock=3, adj=3", 3, 3),
        ("lock=2, adj=2", 2, 2),
    ]

    for name, seq, dssp in tests:
        n = min(len(seq), len(dssp))
        seq_t, dssp_t = seq[:n], dssp[:n]

        print(f"\n  === {name} ({n} residues) ===\n")
        print(f"  {'Config':35s} {'Q3':>6s} {'H-F1':>6s} {'E-F1':>6s} {'C-F1':>6s}  {'H-sens':>6s} {'H-prec':>7s}")
        print(f"  {'─'*35} {'─'*6} {'─'*6} {'─'*6} {'─'*6}  {'─'*6} {'─'*7}")

        # Current v5 baseline
        pred_v5 = fold_protein(seq_t)
        r_v5 = evaluate(pred_v5, dssp_t)
        print(f"  {'v5 baseline':35s} {r_v5['q3']:>5.1%} "
              f"{r_v5['classes']['H']['f1']:>5.2f} "
              f"{r_v5['classes']['E']['f1']:>5.2f} "
              f"{r_v5['classes']['C']['f1']:>5.2f}  "
              f"{r_v5['classes']['H']['sensitivity']:>5.0%} "
              f"{r_v5['classes']['H']['precision']:>6.0%}")

        for config_name, lock_hw, adj_hw in configs:
            pred = fold_protein_phi(seq_t, lock_hw=lock_hw, adjust_hw=adj_hw)
            r = evaluate(pred, dssp_t)
            # Mark improvements
            q3_delta = r['q3'] - r_v5['q3']
            marker = " ★" if q3_delta > 0.005 else " ↓" if q3_delta < -0.005 else ""
            print(f"  {config_name:35s} {r['q3']:>5.1%} "
                  f"{r['classes']['H']['f1']:>5.2f} "
                  f"{r['classes']['E']['f1']:>5.2f} "
                  f"{r['classes']['C']['f1']:>5.2f}  "
                  f"{r['classes']['H']['sensitivity']:>5.0%} "
                  f"{r['classes']['H']['precision']:>6.0%}{marker}")

    # Detailed comparison of best config
    print("\n" + "=" * 70)
    print("  DETAILED: v5 baseline vs best φ-scaled config")
    print("=" * 70)

    seq, dssp = LYSOZYME_SEQ[:len(LYSOZYME_DSSP)], LYSOZYME_DSSP
    pred_v5 = fold_protein(seq)
    pred_phi = fold_protein_phi(seq, lock_hw=3, adjust_hw=5, verbose=False)

    print(f"\n  SEQ:    {seq[:65]}")
    print(f"  DSSP:   {dssp[:65]}")
    print(f"  v5:     {pred_v5[:65]}")
    print(f"  φ-scl:  {pred_phi[:65]}")
    diff = ''.join('·' if pred_v5[i] == pred_phi[i] else '!' for i in range(65))
    print(f"  diff:   {diff}")

    print(f"\n  SEQ:    {seq[65:]}")
    print(f"  DSSP:   {dssp[65:]}")
    print(f"  v5:     {pred_v5[65:]}")
    print(f"  φ-scl:  {pred_phi[65:]}")
    diff = ''.join('·' if pred_v5[i] == pred_phi[i] else '!' for i in range(65, len(seq)))
    print(f"  diff:   {diff}")

    # SB tree walk analysis
    print("\n" + "=" * 70)
    print("  STERN-BROCOT WALK ANALYSIS")
    print("  CF expansion of sequential ratios = walk on SB tree")
    print("=" * 70)

    ratios = [aa_ratio(c) for c in seq]
    for region_name, start, end, ss_type in [
        ("Helix (5-15)", 4, 15, "H"),
        ("Sheet region (41-52)", 40, 52, "E"),
        ("Coil (16-30)", 15, 30, "C"),
    ]:
        print(f"\n  {region_name}:")
        print(f"    Seq:  {seq[start:end]}")
        print(f"    DSSP: {dssp[start:end]}")
        for i in range(start, min(end - 1, len(ratios) - 1)):
            r = ratios[i + 1] / ratios[i]
            cf = to_cf(r)
            depth = len(cf)
            cost = cf_length(cf)
            # Walk pattern: L=left (subtract), R=right (add) on SB tree
            walk = ''.join('R' * c if idx % 2 == 0 else 'L' * c
                          for idx, c in enumerate(cf))
            print(f"    {seq[i]}→{seq[i+1]}: CF={cf!s:20s} depth={depth} cost={cost:3d} "
                  f"walk={walk[:20]}")


if __name__ == "__main__":
    run_comparison()
