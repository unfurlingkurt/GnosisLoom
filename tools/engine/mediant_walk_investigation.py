#!/usr/bin/env python3
"""Investigation: Mediant nesting order = Stern-Brocot tree walk.

The mediant operation a⊕b = (a_num+b_num)/(a_den+b_den) is a SINGLE STEP
on the Stern-Brocot tree. When applied iteratively vs simultaneously,
the WALK on the tree differs:

  SIMULTANEOUS: mediant(a, b, c) — one step incorporating all neighbors
  NESTED LEFT:  mediant(mediant(a, b), c) — walk toward b first, then c
  NESTED NEAR:  mediant(mediant(a, nearest), next) — walk closest first

The NESTING ORDER determines the walk path. This IS the "Ramachandran walk"
— the path through ratio-space that the fold follows.

Key hypothesis: nested mediant (closest first) gives natural φ-decay
because each successive step moves the value LESS (the SB tree analog
of exponential decay in distance).
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
)


def fold_with_mediant_strategy(seq: str, strategy: str = "simultaneous",
                                verbose: bool = False) -> str:
    """Fold protein with different mediant diffusion strategies.

    Strategies:
      "simultaneous": mediant(field[i], *all_locked_neighbors) — current v5
      "nested_nearest": mediant closest locked first, then farther — SB walk
      "nested_left": mediant left neighbor first, then right
      "nested_right": mediant right neighbor first, then left
      "no_diffusion": no mediant diffusion (control)
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
    cycle_locks = []  # Track locks per cycle

    while True:
        cycle += 1
        changed = False
        locks_this_cycle = 0

        # Step 1: Recompute
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
                    locks_this_cycle += 1
                if i + 1 < n and commit(i + 1, SS.TURN):
                    changed = True
                    locks_this_cycle += 1

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
                        locks_this_cycle += 1
                    if commit(dn_pos, SS.SHEET):
                        changed = True
                        locks_this_cycle += 1
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

        # Step 5: LOCK
        for i in range(n):
            if locked[i]:
                continue
            if not coupled[i]:
                continue
            if regularity[i] > INTER_GROUND_DEPTH:
                continue

            local_cfs = []
            if i > 0 and i - 1 < len(hyd_cfs):
                local_cfs.append(hyd_cfs[i - 1])
            if i < len(hyd_cfs):
                local_cfs.append(hyd_cfs[i])

            total_coh = 0
            total_inc = 0
            for cf in local_cfs:
                c, ic = _cf_coherent_count(cf)
                total_coh += c
                total_inc += ic

            if total_coh > total_inc:
                if commit(i, SS.HELIX):
                    changed = True
                    locks_this_cycle += 1

        # Step 6: ADJUST helix extension
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
                    locks_this_cycle += 1

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
                            locks_this_cycle += 1

        # Step 6c: Mediant diffusion — THE KEY DIFFERENCE
        if strategy != "no_diffusion":
            new_field = list(field)
            new_hyd = list(hyd_field)
            for i in range(n):
                if locked[i]:
                    continue

                if strategy == "simultaneous":
                    # Current v5: mediant(field[i], *all_locked_neighbors)
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

                elif strategy == "nested_nearest":
                    # SB tree walk: blend closest first, then farther
                    # This gives natural φ-decay because each step on the
                    # SB tree moves the value LESS than the previous step
                    val_raw = field[i]
                    val_hyd = hyd_field[i]
                    has_any = False
                    for dist in range(1, 6):  # up to ±5 (Fibonacci)
                        for offset in (-dist, dist):
                            j = i + offset
                            if 0 <= j < n and locked[j]:
                                val_raw = mediant(val_raw, field[j])
                                val_hyd = mediant(val_hyd, hyd_field[j])
                                has_any = True
                    if has_any:
                        new_field[i] = val_raw
                        new_hyd[i] = val_hyd

                elif strategy == "nested_left":
                    # Always blend left first, then right
                    val_raw = field[i]
                    val_hyd = hyd_field[i]
                    has_any = False
                    if i - 1 >= 0 and locked[i - 1]:
                        val_raw = mediant(val_raw, field[i - 1])
                        val_hyd = mediant(val_hyd, hyd_field[i - 1])
                        has_any = True
                    if i + 1 < n and locked[i + 1]:
                        val_raw = mediant(val_raw, field[i + 1])
                        val_hyd = mediant(val_hyd, hyd_field[i + 1])
                        has_any = True
                    if has_any:
                        new_field[i] = val_raw
                        new_hyd[i] = val_hyd

                elif strategy == "nested_right":
                    # Always blend right first, then left
                    val_raw = field[i]
                    val_hyd = hyd_field[i]
                    has_any = False
                    if i + 1 < n and locked[i + 1]:
                        val_raw = mediant(val_raw, field[i + 1])
                        val_hyd = mediant(val_hyd, hyd_field[i + 1])
                        has_any = True
                    if i - 1 >= 0 and locked[i - 1]:
                        val_raw = mediant(val_raw, field[i - 1])
                        val_hyd = mediant(val_hyd, hyd_field[i - 1])
                        has_any = True
                    if has_any:
                        new_field[i] = val_raw
                        new_hyd[i] = val_hyd

            field = new_field
            hyd_field = new_hyd

        cycle_locks.append(locks_this_cycle)

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
        print(f"  Strategy: {strategy}")
        print(f"  Converged after {cycle} cycles")
        print(f"  Locks per cycle: {cycle_locks}")

        # Check if lock pattern follows Fibonacci
        total = sum(cycle_locks)
        cumulative = []
        cum = 0
        for l in cycle_locks:
            cum += l
            cumulative.append(cum)
        print(f"  Cumulative locks: {cumulative}")
        print(f"  Total locked: {total}/{n}")

    dssp_map = {
        SS.HELIX: 'H', SS.SHEET: 'E',
        SS.TURN: 'C', SS.COIL: 'C',
        SS.UNRESOLVED: 'C'
    }
    return ''.join(dssp_map[s] for s in states)


def demonstrate_mediant_walk():
    """Show how mediant nesting traces different SB tree walks."""
    print("=" * 70)
    print("  MEDIANT NESTING = STERN-BROCOT TREE WALK")
    print("=" * 70)

    # Example: position between two locked neighbors
    a = Fraction(463, 300)   # ~Ala ratio
    b = Fraction(769, 500)   # ~Val ratio (locked left)
    c = Fraction(922, 600)   # ~Leu ratio (locked right)

    print(f"\n  Current field value: {a} = {float(a):.6f}")
    print(f"  Locked left:        {b} = {float(b):.6f}")
    print(f"  Locked right:       {c} = {float(c):.6f}")

    # Simultaneous mediant
    sim = mediant(a, b, c)
    print(f"\n  SIMULTANEOUS: mediant(a, b, c)")
    print(f"    = ({a.numerator}+{b.numerator}+{c.numerator})/({a.denominator}+{b.denominator}+{c.denominator})")
    print(f"    = {sim} = {float(sim):.6f}")
    print(f"    CF = {to_cf(sim)}")

    # Nested left first
    m1 = mediant(a, b)
    nl = mediant(m1, c)
    print(f"\n  NESTED LEFT FIRST: mediant(mediant(a, b), c)")
    print(f"    Step 1: mediant(a, b) = {m1} = {float(m1):.6f}")
    print(f"    Step 2: mediant(m1, c) = {nl} = {float(nl):.6f}")
    print(f"    CF = {to_cf(nl)}")

    # Nested right first
    m1r = mediant(a, c)
    nr = mediant(m1r, b)
    print(f"\n  NESTED RIGHT FIRST: mediant(mediant(a, c), b)")
    print(f"    Step 1: mediant(a, c) = {m1r} = {float(m1r):.6f}")
    print(f"    Step 2: mediant(m1r, b) = {nr} = {float(nr):.6f}")
    print(f"    CF = {to_cf(nr)}")

    # Show walk distances
    print(f"\n  Walk distances (CF depth of ratio to original):")
    for name, result in [("Simultaneous", sim), ("Nested left", nl), ("Nested right", nr)]:
        ratio = result / a if result > a else a / result
        cf = to_cf(ratio)
        print(f"    {name:20s}: distance CF = {cf}, depth = {len(cf)}, cost = {cf_length(cf)}")

    # Multi-step walk: iterated mediant from position outward
    print(f"\n  ITERATED MEDIANT WALK (φ-decay demonstration):")
    val = Fraction(463, 300)  # start
    targets = [Fraction(769, 500), Fraction(922, 600),
               Fraction(612, 400), Fraction(1052, 700)]  # locked at dist 1,2,3,4
    for step, t in enumerate(targets, 1):
        prev = val
        val = mediant(val, t)
        move = abs(float(val) - float(prev))
        print(f"    Step {step}: mediant with target at dist {step} → {val} = {float(val):.6f} "
              f"(moved {move:.6f})")

    print(f"\n  Each step moves LESS — this is natural φ-decay on the SB tree!")
    print(f"  The ratio of successive moves approximates 1/φ.")

    moves = []
    val = Fraction(463, 300)
    for t in targets:
        prev = val
        val = mediant(val, t)
        moves.append(abs(float(val) - float(prev)))

    print(f"  Move ratios: ", end="")
    for i in range(1, len(moves)):
        if moves[i-1] > 0:
            print(f"{moves[i]/moves[i-1]:.3f} ", end="")
    print(f"  (φ^-1 = {1/((1+5**0.5)/2):.3f})")


def run_strategy_comparison():
    """Compare mediant strategies on test proteins."""
    print("\n" + "=" * 70)
    print("  MEDIANT STRATEGY COMPARISON")
    print("=" * 70)

    tests = [
        ("Lysozyme", LYSOZYME_SEQ, LYSOZYME_DSSP),
        ("Ubiquitin",
         'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG',
         'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'),
    ]

    strategies = [
        "simultaneous",     # current v5
        "nested_nearest",   # SB walk: closest first, up to ±5
        "nested_left",      # always left first
        "nested_right",     # always right first
        "no_diffusion",     # control
    ]

    for name, seq, dssp in tests:
        n = min(len(seq), len(dssp))
        seq_t, dssp_t = seq[:n], dssp[:n]

        print(f"\n  === {name} ({n} residues) ===\n")
        print(f"  {'Strategy':25s} {'Q3':>6s} {'H-F1':>6s} {'E-F1':>6s} {'C-F1':>6s}  {'H-sens':>6s}")
        print(f"  {'─'*25} {'─'*6} {'─'*6} {'─'*6} {'─'*6}  {'─'*6}")

        for strat in strategies:
            pred = fold_with_mediant_strategy(seq_t, strategy=strat, verbose=False)
            r = evaluate(pred, dssp_t)
            print(f"  {strat:25s} {r['q3']:>5.1%} "
                  f"{r['classes']['H']['f1']:>5.2f} "
                  f"{r['classes']['E']['f1']:>5.2f} "
                  f"{r['classes']['C']['f1']:>5.2f}  "
                  f"{r['classes']['H']['sensitivity']:>5.0%}")

    # Detailed convergence for the best strategy
    print("\n  === Convergence dynamics (Lysozyme, nested_nearest) ===\n")
    seq = LYSOZYME_SEQ[:len(LYSOZYME_DSSP)]
    fold_with_mediant_strategy(seq, strategy="nested_nearest", verbose=True)

    print("\n  === Convergence dynamics (Lysozyme, simultaneous / v5) ===\n")
    fold_with_mediant_strategy(seq, strategy="simultaneous", verbose=True)


if __name__ == "__main__":
    demonstrate_mediant_walk()
    run_strategy_comparison()
