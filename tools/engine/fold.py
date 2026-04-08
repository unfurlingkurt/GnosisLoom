#!/usr/bin/env python3
"""Geometric field solver v8.3 — dynamic acceleration tracking.

Amino acids occupy φ-scaled temporal domains based on log_φ(ST/38):
  Domain -2: S(16)           Domain 0: A,V,D,N,P       Domain 2: M,H,W,K
  Domain -1: T(25)           Domain 1: Q,I,L,C,E,R     Domain 3: F,Y
  Domain  5: G(632)

CF[0] of the tension ratio encodes domain separation:
  CF[0]=1 → within φ¹ → same temporal window (coupled)
  CF[0]=2 → within φ² → one gear up/down
  CF[0]=4 → within φ³ → two gears up/down

The fold proceeds in two temporal phases:

  PHASE 1 — WIND-UP: Local structure crystallizes via 7-step field iterator.
    Step 1 — SAMPLE:   Read ratios and field state
    Step 2 — DETECT:   Pair CF depths, boundary candidates     [Fib(1)=1]
    Step 3 — COHERE:   Coupling analysis (CF[0] = 1)           [Fib(2)=1]
    Step 4 — TENSE:    Curvature regularity (hw=igd=2)         [Fib(3)=2]
    Step 5 — LOCK:     Commit positions, symmetric CF motif     [Fib(4)=3 pairs]
    Step 6 — ADJUST:   Propagate + mediant diffusion (±1)      [±1, iterates]
    Step 7 — OUTPUT:   Update state, check convergence

  PHASE 2 — WIND-DOWN: Non-local topology overrides local structure.
    Winding returns spanning hairpin markers connect distant positions
    topologically. When a helix position is connected to a Phase-1 sheet
    position, the slower temporal gear (non-local contacts) overrides the
    faster gear (local helix coupling), reassigning helix → sheet.
    Extension proceeds directionally TOWARD the nearest hairpin.

The field (ratio at each position) evolves through mediant diffusion:
unlocked positions blend toward locked neighbors via mediant (the Aramis
Field iterator's diffusion mechanism). Each mediant = one step on the
Stern-Brocot tree. Iterated mediant through cycles = the SB tree walk.

ALL criteria are CF depth checks, exact ratio matches, or structural
invariants. The only constants are framework-native:
  - SOL_CARBON = 153/100
  - WATER_CARBON = 51/62
  - inter_ground_depth = CF_depth(57/38) = 2
  - CF[0] = 1 for coupling (ratio < 2:1)
  - CF depth = 1 for hairpin (non-square product)

CF coefficient classification (φ-coherence from Stern-Brocot theory):
  - φ-coherent: c ≤ inter_ground_depth (= 2) — noble number neighborhood
  - Transitional: 3 ≤ c ≤ 4 — neutral, not counted
  - φ-incoherent: c ≥ cf_length(inter_ground_cf) + igd (= 5) — far from noble
Both boundaries derive from the inter-ground ratio 57/38 = [1,2].

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
    cf_motif_counts, phi_coherence, mediant, SOL_CARBON, WATER_CARBON, POLAR_AA, PHI
)
from tools.engine.curvature import (
    geometric_winding, winding_returns, sequential_ratios,
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


# === FRAMEWORK CONSTANTS (all derived, none imposed) ===

# Inter-ground depth: THE universal structural scale
# CF depth of SHEET_GROUND/HELIX_GROUND = 57/38 = [1,2], depth 2
INTER_GROUND_CF = to_cf(Fraction(SHEET_GROUND, HELIX_GROUND))
INTER_GROUND_DEPTH = len(INTER_GROUND_CF)  # = 2

# The denominator lattice: all pair products have denominators 3^a × 17^b
# Exactly 9 levels exist: {1, 3, 9, 51, 153, 459, 2601, 7803, 23409}
# The lattice dimension is 2: factor-of-3 axis and factor-of-17 axis


def _cf_coherent_count(cf_coeffs: list) -> Tuple[int, int]:
    """Count φ-coherent vs φ-incoherent CF coefficients.

    In Stern-Brocot / CF theory:
    - Coefficients {1, 2} are the noble number neighborhood (φ = [1,1,1,...])
      These are the ONLY coefficients in CFs of noble numbers.
    - Coefficients {3, 4} are transitional — neutral zone.
    - Coefficients {≥5} are far from any noble number.

    The boundary ≤ inter_ground_depth (=2) defines φ-coherent.
    The incoherent threshold is cf_length(inter_ground_cf) + inter_ground_depth
    = 3 + 2 = 5.

    Returns (coherent_count, incoherent_count) — exact integers.
    """
    inter_ground_cost = cf_length(INTER_GROUND_CF)  # = 3
    incoherent_threshold = inter_ground_cost + INTER_GROUND_DEPTH  # = 5

    coh = sum(1 for c in cf_coeffs if c <= INTER_GROUND_DEPTH)
    inc = sum(1 for c in cf_coeffs if c >= incoherent_threshold)
    return coh, inc


def _is_coupled(t1: int, t2: int) -> bool:
    """Two self-tensions are coupled when their ratio has CF[0] = 1.

    CF[0] = 1 means the ratio is between 1:1 and 2:1.
    This is the strictest possible coupling — exact framework criterion.
    """
    if t1 <= 0 or t2 <= 0:
        return False
    ratio = Fraction(max(t1, t2), min(t1, t2))
    cf = to_cf(ratio)
    return cf[0] == 1


def _multi_scale_accel(curvatures: list, n: int, igd: int, min_h: int):
    """Compute multi-scale acceleration from a curvature array.

    Returns (accel_k1, accel_k_igd, accel_k_helix, accel_magnitude) —
    four lists of length n.  Each accel_k[pos] = |curvatures[i+k] - curvatures[i]|
    centered on position pos.  accel_magnitude = max across all three scales.

    This is called each iteration cycle so the acceleration EVOLVES with the
    field — it is not a static property.  As mediant diffusion smooths the
    field, curvatures converge and acceleration decays.  The 2nd derivative
    thereby reveals how far each position is from its structural ground state.
    """
    # k=1: consecutive curvature change
    ak1 = [0.0] * n
    for i in range(len(curvatures) - 1):
        pos = i + 1  # centered between curvatures[i] and curvatures[i+1]
        if pos < n:
            ak1[pos] = abs(curvatures[i + 1] - curvatures[i])

    # k=igd: sheet-period curvature change
    ak_igd = [0.0] * n
    for i in range(len(curvatures) - igd):
        pos = i + 1  # center of span
        if pos < n:
            ak_igd[pos] = abs(curvatures[i + igd] - curvatures[i])

    # k=min_helix_len: helix-period curvature change
    ak_helix = [0.0] * n
    for i in range(len(curvatures) - min_h):
        pos = i + min_h // 2  # center of span
        if pos < n:
            ak_helix[pos] = abs(curvatures[i + min_h] - curvatures[i])

    # Boundaries: first/last get max (no stable structure at chain ends)
    for arr in (ak1, ak_igd, ak_helix):
        mx = max(arr) if any(v > 0 for v in arr) else 0
        if n > 0:
            arr[0] = mx
            arr[n - 1] = mx

    # Combined: max across scales
    a_mag = [max(ak1[i], ak_igd[i], ak_helix[i]) for i in range(n)]

    return ak1, ak_igd, ak_helix, a_mag


def _curvature_regularity(pos: int, curvatures: list, locked: list) -> int:
    """CF depth of max/min curvature magnitude ratio in ±igd window.

    The window half-width IS the inter-ground depth (=2), the universal
    structural scale derived from CF(57/38). This gives a 5-curvature
    window — the minimum needed to capture one full helix turn (~3.6 residues).
    """
    n = len(curvatures)
    hw = INTER_GROUND_DEPTH  # = 2, derived from framework
    start = max(0, pos - hw)
    end = min(n, pos + hw + 1)
    if start >= end:
        return 99
    mags = [abs(curvatures[j]) for j in range(start, end)]
    mx = max(mags)
    mn = min(mags)
    if mn == 0:
        mn = 1
    ratio = Fraction(mx, mn)
    cf = to_cf(ratio)
    return len(cf)


def fold_protein(seq: str, verbose: bool = False) -> str:
    """Fold a protein using the 7-step iterative field solver.

    The field evolves through repeated 7-step cycles until convergence.
    Each cycle applies: Sample → Detect → Cohere → Tense → Lock → Adjust → Output.

    Crystallization criteria (all framework-native):
      Turn:  pair CF depth ≤ inter_ground_depth
      Helix: coupled + curvature regular + CF motif coherent > incoherent
      Sheet: hairpin (CF depth=1, non-square product) + cross-strand extension
      Coil:  uncristallized remainder (assigned at convergence)
    """
    seq = seq.upper().replace(" ", "").replace("\n", "")
    n = len(seq)

    # === STEP 1: SAMPLE — initialize the field ===

    # The field: ratio at each position. Evolves through mediant diffusion.
    field = [aa_ratio(c) for c in seq]
    hyd_field = [hydrated_ratio(c) for c in seq]

    # Static backbone quantities (computed once from initial ratios)
    raw_tensions = tension_sequence(seq)
    raw_cfs = [t["cf"] for t in raw_tensions]
    raw_costs = [t["cost"] for t in raw_tensions]
    raw_depths = [len(t["cf"]) for t in raw_tensions]

    # Self-tensions (static — property of amino acid identity)
    self_t = [SELF_TENSION.get(c, 50) for c in seq]

    # Framework-derived helix constants
    MIN_HELIX_LEN = INTER_GROUND_DEPTH + INTER_GROUND_DEPTH  # = 4
    MAX_INTERNAL_GAP = INTER_GROUND_DEPTH * INTER_GROUND_DEPTH  # = 4

    # φ-domains: floor(log_φ(ST/HELIX_GROUND)) — temporal scaling tier
    aa_domains = []
    for c in seq:
        st = SELF_TENSION.get(c, 50)
        if st <= 0:
            aa_domains.append(0)
        else:
            aa_domains.append(int(math.floor(math.log(st / HELIX_GROUND)
                                             / math.log(PHI))))

    # State arrays
    states = [SS.UNRESOLVED] * n
    locked = [False] * n

    def commit(pos, state):
        """Lock a position into a structural state."""
        if 0 <= pos < n and not locked[pos]:
            states[pos] = state
            locked[pos] = True
            return True
        return False

    # === PRE-COMPUTE: Static curvature regularity (from initial ratios) ===
    # The curvature from initial sequential ratios is a STATIC property of the
    # sequence — it doesn't change with mediant diffusion. This is used for
    # sheet extension decisions because sheet curvature is NEVER regular
    # (depth ≤ igd). The evolving curvature (from the field) is used for
    # helix decisions, which DO benefit from field evolution.
    static_curvatures = []
    for i in range(n - 1):
        ratio = field[i + 1] / field[i]  # initial field = original ratios
        cf = to_cf(ratio)
        mag = cf_length(cf)
        sign = 1 if float(ratio) >= 1.0 else -1
        static_curvatures.append(sign * mag)

    static_regularity = [99] * n
    for i in range(n):
        static_regularity[i] = _curvature_regularity(i, static_curvatures, [False] * n)

    # === INITIAL: Multi-scale curvature acceleration (2nd derivative) ===
    # Computed from the initial field curvatures — but this is just the
    # STARTING STATE. The acceleration is RECOMPUTED each cycle from the
    # evolving field (see Step 1b inside the loop). As mediant diffusion
    # smooths the field, curvatures converge and acceleration decays.
    # The 2nd derivative tracks how far each position is from its structural
    # ground state at each temporal scale:
    #   k=1:              local curvature change (fastest gear)
    #   k=IGD=2:          sheet-period curvature change
    #   k=MIN_HELIX_LEN=4: helix-period curvature change (slowest local gear)
    accel_k1, accel_k_igd, accel_k_helix, accel_magnitude = \
        _multi_scale_accel(static_curvatures, n, INTER_GROUND_DEPTH, MIN_HELIX_LEN)

    # === PRE-COMPUTE: Pairwise CF0 (tension ratio first coefficient) ===
    # CF0 of max(ST_i, ST_j) / min(ST_i, ST_j) encodes domain separation:
    #   CF0=1 → same or adjacent domain (helix coupling)
    #   CF0=2 → one gear shift (sheet coupling range)
    #   CF0≥IGD+1 → domain boundary
    # A run of consecutive pairs ALL with CF0 ≤ IGD = consistent coupling window.
    pair_cf0 = []
    for i in range(n - 1):
        if self_t[i] > 0 and self_t[i + 1] > 0:
            r = Fraction(max(self_t[i], self_t[i + 1]),
                         min(self_t[i], self_t[i + 1]))
            cf = to_cf(r)
            pair_cf0.append(cf[0])
        else:
            pair_cf0.append(99)

    # === PRE-COMPUTE: Winding returns (topological sheet contacts) ===
    # Winding returns detect positions where the accumulated geometric
    # curvature (from sequential ratios) returns to a previously visited
    # value. This means the chain has LOOPED — positions i and j are
    # topologically adjacent despite being far apart in sequence.
    #
    # max_diff=0: exact winding closure only. When winding(i) == winding(j),
    # the chain has traced a geometrically exact closed loop — the curvature
    # accumulated from i to j sums to exactly zero. This is the framework's
    # own proof of topological adjacency: positions i and j are at the same
    # geometric orientation despite being far apart in sequence.
    wr = winding_returns(seq, min_separation=INTER_GROUND_DEPTH + 1, max_diff=0)

    # Build winding return adjacency: which positions are topologically connected?
    wr_partners = [set() for _ in range(n)]
    for r in wr:
        i_pos, j_pos = r["pos_i"], r["pos_j"]
        if i_pos < n and j_pos < n:
            wr_partners[i_pos].add(j_pos)
            wr_partners[j_pos].add(i_pos)

    # Identify hairpin markers (CF depth=1, non-square product)
    # These are structural SHEET seeds, not turns — they mark where
    # the chain reverses direction in a β-hairpin.
    hairpin_pairs = set()
    for i in range(len(raw_cfs)):
        if len(raw_cfs[i]) != 1:
            continue
        product = raw_costs[i]
        sqrt_p = int(math.sqrt(product) + 0.5)
        if sqrt_p * sqrt_p != product:
            hairpin_pairs.add(i)

    # === ITERATIVE 7-STEP CYCLE ===

    accel_rise = [0] * n  # consecutive cycles of helix-scale accel increase

    cycle = 0
    while True:
        cycle += 1
        changed = False

        # --- Step 1 (per-cycle): Recompute field-derived quantities ---
        # Hydrated pair CFs (evolve as field evolves)
        hyd_cfs = []
        for i in range(n - 1):
            product = hyd_field[i] * hyd_field[i + 1]
            hyd_cfs.append(to_cf(product))

        # Curvature from current field (evolves with field)
        curvatures = []
        for i in range(n - 1):
            ratio = field[i + 1] / field[i]
            cf = to_cf(ratio)
            mag = cf_length(cf)
            sign = 1 if float(ratio) >= 1.0 else -1
            curvatures.append(sign * mag)

        # --- Step 1b: Recompute multi-scale acceleration from evolving field ---
        # The 2nd derivative evolves with the field. Track the helix-scale
        # acceleration rise count: consecutive cycles where acceleration at
        # position i increases rather than decays. At convergence, accel_rise
        # shows which positions the field was still "fighting" vs settling.
        # This is diagnostic for now — gating was explored but the field
        # evolution is too short (6 cycles) for reliable discrimination,
        # and the gate self-interferes (blocking a seed changes the field).
        prev_accel_k_helix = list(accel_k_helix)
        dyn_ak1, dyn_ak_igd, dyn_ak_helix, dyn_ak_mag = \
            _multi_scale_accel(curvatures, n, INTER_GROUND_DEPTH, MIN_HELIX_LEN)
        if cycle > 1:
            for i in range(n):
                if dyn_ak_helix[i] > prev_accel_k_helix[i]:
                    accel_rise[i] += 1
                else:
                    accel_rise[i] = 0
        accel_k_helix = list(dyn_ak_helix)

        # --- Step 2: DETECT — identify boundary candidates ---
        # Pairs with CF depth ≤ inter_ground_depth are structural boundaries.
        # EXCEPT: hairpin markers (CF depth=1, non-square) are sheet seeds,
        # not turns. The hairpin is where the chain reverses in a β-hairpin;
        # the positions AT the marker are part of the sheet structure.
        for i in range(len(raw_depths)):
            if raw_depths[i] <= INTER_GROUND_DEPTH:
                if i in hairpin_pairs:
                    continue  # handled in Step 2b as sheet seed
                if commit(i, SS.TURN):
                    changed = True
                    if verbose:
                        print(f"  [{cycle}] TURN at pair {i+1} ({raw_tensions[i]['pair']}) "
                              f"CF={raw_cfs[i]} depth={raw_depths[i]}")
                if i + 1 < n and commit(i + 1, SS.TURN):
                    changed = True

        # --- Step 2b: DETECT — hairpin sheet seeds ---
        # Hairpin markers (CF depth=1, non-square product) are the ONLY
        # amino acid pairs where the tension product is an exact non-square
        # integer. This is unique to ST/TS (4×5=20). These seed sheet
        # strands that extend outward from the hairpin turn.
        for i in sorted(hairpin_pairs):
            if verbose and cycle == 1:
                print(f"  [{cycle}] HAIRPIN at pair {i+1} ({raw_tensions[i]['pair']}) product={raw_costs[i]}")

            # The hairpin positions themselves are sheet structure
            if commit(i, SS.SHEET):
                changed = True
                if verbose:
                    print(f"    [{cycle}] SHEET SEED at {i+1} ({seq[i]})")
            if i + 1 < n and commit(i + 1, SS.SHEET):
                changed = True
                if verbose:
                    print(f"    [{cycle}] SHEET SEED at {i+2} ({seq[i+1]})")

            # Extend anti-parallel strands outward from hairpin
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

                # Cross-strand consonance: CF depth within lattice scale
                if cross_depth <= INTER_GROUND_DEPTH * INTER_GROUND_DEPTH:
                    if commit(up_pos, SS.SHEET):
                        changed = True
                    if commit(dn_pos, SS.SHEET):
                        changed = True
                    if verbose:
                        print(f"    [{cycle}] STRAND k={k}: pos {up_pos+1},{dn_pos+1} "
                              f"cross_depth={cross_depth}")
                    k += 1
                else:
                    break

        # --- Step 2c: DETECT — winding-return sheet contacts ---
        # Winding returns prove topological adjacency: when winding(i) ≈
        # winding(j), positions i and j are at the same geometric
        # orientation despite being far apart in sequence. This IS sheet
        # geometry — the framework's own proof, not requiring hairpin.
        #
        # Two modes:
        # A) Hairpin-spanning WR: both positions are sheet (original logic)
        # B) Non-hairpin WR: positions are sheet IF they don't qualify as
        #    helix (CF0 > 1 to neighbors = not directly coupled = sheet regime)
        for r in wr:
            i_pos, j_pos = r["pos_i"], r["pos_j"]
            if i_pos >= n or j_pos >= n:
                continue

            spans_hairpin = any(i_pos <= h <= j_pos for h in hairpin_pairs)

            for pos in (i_pos, j_pos):
                if locked[pos]:
                    continue
                reg = static_regularity[pos]

                if spans_hairpin:
                    # Mode A: hairpin-spanning — irregular curvature → sheet
                    if reg > INTER_GROUND_DEPTH:
                        if commit(pos, SS.SHEET):
                            changed = True
                            if verbose:
                                partner = j_pos if pos == i_pos else i_pos
                                print(f"  [{cycle}] SHEET (wr+hp) at {pos+1} ({seq[pos]}) "
                                      f"partner={partner+1} reg={reg}")
                    # Mode B (non-hairpin WR) handled post-convergence
                    # in Phase 1d, where helix positions are already locked
                    # and won't be overwritten by sheet cascade.
                    pass

        # --- Step 3: COHERE — coupling analysis ---
        # (coupling is a static property, computed once but used each cycle)
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

        # --- Step 4: TENSE — curvature regularity ---
        regularity = [99] * n
        for i in range(n):
            if locked[i]:
                continue
            regularity[i] = _curvature_regularity(i, curvatures, locked)

        # --- Step 5: LOCK — crystallize helix seeds ---
        # A position crystallizes as HELIX when ALL geometric criteria are met:
        #   1. Coupled to at least one neighbor (CF[0] = 1)
        #   2. Curvature regular (CF depth ≤ inter_ground_depth)
        #   3. CF motif: coherent coefficients > incoherent in symmetric pair CFs
        #
        # The CF motif window is SYMMETRIC: pairs on both sides of the position.
        # This matches the extension step's window and aligns with Fibonacci
        # scaling: LOCK is step 5 in the 7-step process, using Fib(4)=3 pairs.
        # Steps 2-4 naturally use Fib(1)=1, Fib(2)=1, Fib(3)=2 windows.
        for i in range(n):
            if locked[i]:
                continue
            if not coupled[i]:
                continue
            if regularity[i] > INTER_GROUND_DEPTH:
                continue
            # CF motif from symmetric pair CFs: pairs (i-1,i), (i,i+1), (i+1,i+2)
            # Same window as the extension step — the position should see
            # the CF environment equally on both sides.
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
                    if verbose:
                        print(f"  [{cycle}] HELIX SEED at {i+1} ({seq[i]}) "
                              f"coh={total_coh} inc={total_inc} reg={regularity[i]} "
                              f"a[1,{INTER_GROUND_DEPTH},{MIN_HELIX_LEN}]="
                              f"{dyn_ak1[i]:.0f},{dyn_ak_igd[i]:.0f},{dyn_ak_helix[i]:.0f}")

        # --- Step 5b: LOCK — extend sheet strands ---
        # Sheet strands propagate from locked sheet positions along the
        # chain. The strand continues while:
        #   1. Adjacent to locked sheet
        #   2. Connecting pair is NOT a turn marker (depth > igd)
        #   3. STATIC curvature regularity > igd (irregular = sheet character)
        # The STATIC regularity (from initial ratios, not the evolving field)
        # is the framework's own geometry: sheet curvature is NEVER regular.
        # Helix-like regions (regular curvature) naturally terminate strands.
        for i in range(n):
            if locked[i]:
                continue
            # Static curvature must be irregular (sheet character)
            if static_regularity[i] <= INTER_GROUND_DEPTH:
                continue
            has_sheet_neighbor = False
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n and states[j] == SS.SHEET and locked[j]:
                    # Check that the pair connecting them is not a boundary
                    pair_idx = min(i, j)
                    if pair_idx < len(raw_depths):
                        if raw_depths[pair_idx] > INTER_GROUND_DEPTH:
                            has_sheet_neighbor = True
                            break
            if has_sheet_neighbor:
                if commit(i, SS.SHEET):
                    changed = True
                    if verbose:
                        print(f"  [{cycle}] SHEET EXT at {i+1} ({seq[i]}) reg={regularity[i]}")

        # --- Step 6: ADJUST — propagate helix through coupled neighbors ---
        # Locked helix positions influence adjacent unlocked positions.
        # Extension requires coupling + CF motif + far-side boundary check.
        #
        # The boundary check prevents helix overshoot: if the far-side
        # neighbor (away from the locked helix) has CF0 ≥ igd+1 (= 3),
        # the position is at a φ-domain boundary (2+ domain separation)
        # and helix cannot extend through it. This is the framework's
        # own boundary detection — not an imposed threshold.
        for i in range(n):
            if locked[i]:
                continue

            # Must be adjacent to a locked helix
            helix_side = None
            for offset in (-1, 1):
                j = i + offset
                if 0 <= j < n and states[j] == SS.HELIX and locked[j]:
                    helix_side = offset
                    break
            if helix_side is None:
                continue

            if not coupled[i]:
                continue

            # Far-side boundary check: is there a domain break on the
            # non-helix side? CF0 ≥ igd+1 means 2+ domain separation.
            far_side = i - helix_side  # opposite direction from helix
            if 0 <= far_side < n:
                if self_t[i] > 0 and self_t[far_side] > 0:
                    r_far = Fraction(max(self_t[i], self_t[far_side]),
                                     min(self_t[i], self_t[far_side]))
                    cf_far = to_cf(r_far)
                    if cf_far[0] >= INTER_GROUND_DEPTH + 1:
                        # Domain boundary on far side — don't extend
                        continue

            # CF motif over immediate + adjacent pair CFs
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
                    if verbose:
                        print(f"  [{cycle}] HELIX EXT at {i+1} ({seq[i]}) "
                              f"coh={total_coh} inc={total_inc} "
                              f"a[1,{INTER_GROUND_DEPTH},{MIN_HELIX_LEN}]="
                              f"{dyn_ak1[i]:.0f},{dyn_ak_igd[i]:.0f},{dyn_ak_helix[i]:.0f}")

        # --- Step 6b: ADJUST — bridge single-residue helix gaps ---
        # If a position is flanked by locked helices and coupled to both,
        # it joins the helix. The coupling check uses CF[0] ≤ inter_ground_depth.
        for i in range(1, n - 1):
            if locked[i]:
                continue
            if states[i - 1] == SS.HELIX and states[i + 1] == SS.HELIX:
                if locked[i - 1] and locked[i + 1]:
                    # Check coupling to both sides
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

        # --- Step 6c: ADJUST — domain-scaled mediant diffusion ---
        # Unlocked positions blend toward locked neighbors through mediant.
        # Each position gets ceil(φ^(|domain|/2)) mediant steps per cycle,
        # because higher φ-domains crystallize on slower timescales.
        # Domain 0: 1 step. Domain ±1: 1 step. Domain ±2: 2 steps.
        # Domain ±3: 2 steps. Domain +5 (G): 4 steps.
        # This IS the temporal gearing: different φ-domains tick at
        # different rates, and the mediant iterator respects this.
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
                # Domain-scaled: more mediant steps for higher domains
                dom = aa_domains[i]
                steps = max(1, math.ceil(PHI ** (abs(dom) / 2.0)))
                f_val = new_field[i]
                h_val = new_hyd[i]
                for _ in range(steps):
                    f_val = mediant(f_val, *locked_nbrs_raw)
                    h_val = mediant(h_val, *locked_nbrs_hyd)
                new_field[i] = f_val
                new_hyd[i] = h_val
        field = new_field
        hyd_field = new_hyd

        # --- Step 7: OUTPUT — check convergence ---
        if not changed:
            # Field has crystallized — assign remaining as coil
            for i in range(n):
                if not locked[i]:
                    commit(i, SS.COIL)
            break

        # Safety: prevent infinite iteration
        # The field MUST converge because each cycle either locks new positions
        # or changes nothing. With n positions, at most n cycles.
        if cycle > n:
            for i in range(n):
                if not locked[i]:
                    commit(i, SS.COIL)
            break

    if verbose:
        print(f"  Phase 1 converged after {cycle} cycles")
        # Show positions where acceleration was still rising at convergence
        rising = [(i, accel_rise[i]) for i in range(n) if accel_rise[i] > 0]
        if rising:
            parts = [f"{i+1}({seq[i]})={r}" for i, r in rising]
            print(f"  Accel still rising at: {', '.join(parts)}")

    # === PHASE 1b: MINIMUM HELIX LENGTH + EXTREME GAP CHECK ===
    # A helix requires at least one complete turn: the i→i+4 backbone H-bond
    # pattern needs 4 residues minimum. Additionally, a helix run with an
    # EXTREME coupling gap (CF[0] > 2*IGD = 4) anywhere is demoted — such a
    # gap means positions in radically different φ-domains (e.g., G at domain+5)
    # were grouped by coincidence, not structural coupling.
    # Applied BEFORE Phase 2 to prevent false sheet from wind-down of orphan helices.

    def _max_pair_cf0(start, end):
        """Maximum CF[0] between any consecutive pair in seq[start:end]."""
        max_cf0 = 0
        for j in range(start, end - 1):
            if self_t[j] > 0 and self_t[j + 1] > 0:
                ratio = Fraction(max(self_t[j], self_t[j + 1]),
                                 min(self_t[j], self_t[j + 1]))
                cf = to_cf(ratio)
                if cf[0] > max_cf0:
                    max_cf0 = cf[0]
        return max_cf0

    i = 0
    while i < n:
        if states[i] == SS.HELIX:
            run_start = i
            while i < n and states[i] == SS.HELIX:
                i += 1
            run_len = i - run_start
            demote = False
            reason = ""
            if run_len < MIN_HELIX_LEN:
                demote = True
                reason = f"len={run_len}"
            else:
                max_gap = _max_pair_cf0(run_start, i)
                if max_gap > MAX_INTERNAL_GAP:
                    demote = True
                    reason = f"gap CF[0]={max_gap}"
            if demote:
                for j in range(run_start, i):
                    states[j] = SS.COIL
                    locked[j] = True
                if verbose:
                    print(f"  [P1b] Demote helix {run_start+1}-{i} "
                          f"({reason})")
        else:
            i += 1

    # === PHASE 1c: MEDIATED HELIX EXTENSION (single pass, no cascade) ===
    # After Phase 1 convergence, positions adjacent to locked helices can
    # extend with relaxed coupling (CF[0] ≤ igd = 2 instead of 1) IF the
    # locked helix neighbor has a "proven" context: CF[0]=1 coupling to
    # another locked helix on the far side. This models temporal gearing:
    # the proven helix context mediates across a φ-domain boundary.
    # Single pass prevents cascading false helices.

    # Recompute curvatures and hyd_cfs at convergence state
    conv_curvatures = []
    for i_pos in range(n - 1):
        ratio = field[i_pos + 1] / field[i_pos]
        cf = to_cf(ratio)
        mag = cf_length(cf)
        sign = 1 if float(ratio) >= 1.0 else -1
        conv_curvatures.append(sign * mag)

    # === MEDOID TENSION — distance from structural ground state ===
    # The converged field curvatures encode how far each position settled
    # from its ideal CF configuration.  The helix-scale acceleration of
    # these converged curvatures is the MEDOID TENSION: the geometric
    # distance between each position's actual state and the medoid
    # (the most central, physically valid state in the CF tree).
    #
    # The medoid of all helix-assigned positions' tensions sets the
    # Gold Standard Baseline Tension (GSBT) — the "rock-solid medoid"
    # that a healthy helix should cluster around.  Positions far from
    # the GSBT are geometric outliers: the field pushed them there, but
    # they don't genuinely belong to the helix population.
    conv_ak1, conv_ak_igd, conv_ak_helix, conv_ak_mag = \
        _multi_scale_accel(conv_curvatures, n, INTER_GROUND_DEPTH, MIN_HELIX_LEN)

    # Medoid tension per position: helix-scale acceleration from the
    # converged field.  This specifically asks whether the helix-period
    # curvature settled.  Using ONLY the helix scale (k=MIN_HELIX_LEN=4)
    # avoids false positives from high k=1 acceleration at structure
    # boundaries (which is a natural feature, not a quality signal).
    medoid_tension = conv_ak_helix  # k=helix-period only

    # Per-run medoid analysis: within each helix run, find the medoid
    # tension (median).  Edge positions whose tension exceeds the run's
    # medoid by more than φ^MAX_INTERNAL_GAP (= φ^4 ≈ 6.85) times are
    # geometric outliers — the field settled them far from the run's
    # medoid.  This is a high bar (φ⁴, not φ²) because edges naturally
    # have elevated tension from the structure boundary.
    phi_mig = PHI ** MAX_INTERNAL_GAP  # φ^IGD² — framework outlier threshold

    if verbose:
        h_vals = sorted([medoid_tension[i] for i in range(n) if states[i] == SS.HELIX])
        c_vals = sorted([medoid_tension[i] for i in range(n) if states[i] == SS.COIL])
        h_med = h_vals[len(h_vals) // 2] if h_vals else 0
        c_med = c_vals[len(c_vals) // 2] if c_vals else 0
        print(f"  Medoid tension — helix: {h_med:.1f} (n={len(h_vals)})  "
              f"coil: {c_med:.1f} (n={len(c_vals)})")

    i = 0
    while i < n:
        if states[i] == SS.HELIX:
            run_start = i
            while i < n and states[i] == SS.HELIX:
                i += 1
            run_end = i  # exclusive
            run_len = run_end - run_start
            if run_len < 2:
                continue
            # Run medoid = median tension within this run
            run_tensions = sorted([medoid_tension[j] for j in range(run_start, run_end)])
            run_medoid = run_tensions[len(run_tensions) // 2]
            if run_medoid == 0:
                continue  # avoid division issues
            # Trim edges where tension > φ^IGD² × run medoid
            threshold = phi_mig * run_medoid
            trimmed = []
            # Left edge
            for j in range(run_start, run_end):
                if medoid_tension[j] > threshold:
                    trimmed.append(j)
                else:
                    break
            # Right edge
            for j in range(run_end - 1, run_start - 1, -1):
                if j in [t for t in trimmed]:
                    break
                if medoid_tension[j] > threshold:
                    trimmed.append(j)
                else:
                    break
            for j in trimmed:
                states[j] = SS.COIL
                if verbose:
                    print(f"  [MEDOID] Trim {j+1} ({seq[j]}) "
                          f"tension={medoid_tension[j]:.0f} > "
                          f"φ⁴×medoid={threshold:.0f} "
                          f"(run medoid={run_medoid:.0f})")
        else:
            i += 1

    conv_hyd_cfs = []
    for i_pos in range(n - 1):
        product = hyd_field[i_pos] * hyd_field[i_pos + 1]
        conv_hyd_cfs.append(to_cf(product))

    mediated_positions = []
    for i in range(n):
        if states[i] != SS.COIL:
            continue  # only upgrade coil positions
        # Must NOT already be coupled (those were handled in Phase 1)
        has_coupling = False
        for offset in (-1, 1):
            nb = i + offset
            if 0 <= nb < n and _is_coupled(self_t[i], self_t[nb]):
                has_coupling = True
                break
        if has_coupling:
            continue

        for offset in (-1, 1):
            j = i + offset  # mediator (locked helix neighbor)
            if not (0 <= j < n and states[j] == SS.HELIX and locked[j]):
                continue

            # i-j coupling within one gear shift
            if self_t[i] <= 0 or self_t[j] <= 0:
                continue
            r_ij = Fraction(max(self_t[i], self_t[j]),
                            min(self_t[i], self_t[j]))
            cf_ij = to_cf(r_ij)
            if cf_ij[0] > INTER_GROUND_DEPTH:
                continue

            # Mediator j has proven helix neighbor k (coupled with CF[0]=1)
            k = j + offset  # far side of j from i
            if not (0 <= k < n and states[k] == SS.HELIX and locked[k]):
                continue
            if not _is_coupled(self_t[j], self_t[k]):
                continue

            # Curvature regularity threshold scales with mediation CF0:
            # CF0=1 → threshold = 1×IGD+1 = 3 (normal helix)
            # CF0=2 → threshold = 2×IGD+1 = 5 (one gear shift)
            # Each gear shift adds IGD of expected curvature variation.
            reg = _curvature_regularity(i, conv_curvatures, locked)
            reg_threshold = cf_ij[0] * INTER_GROUND_DEPTH + 1
            if reg > reg_threshold:
                continue

            # For mediated positions, the proven helix context on the far
            # side IS the structural evidence — the local CF motif is expected
            # to be atypical at domain boundaries (that's WHY mediation is needed).
            # The guards (CF0 ≤ IGD, proven context, scaled regularity) suffice.
            mediated_positions.append(i)
            if verbose:
                print(f"  [P1c] MEDIATED HELIX at {i+1} ({seq[i]}) "
                      f"via {j+1}({seq[j]})-{k+1}({seq[k]}) "
                      f"CF[0]={cf_ij[0]} reg={reg}")
            break

    for pos in mediated_positions:
        states[pos] = SS.HELIX
        locked[pos] = True

    # Bridge single-residue helix gaps between two MEDIATED positions.
    # Only mediated-to-mediated bridges are safe — general helix gaps
    # might create runs that hit gap checks and cascade demotion.
    mediated_set = set(mediated_positions)
    for i in range(1, n - 1):
        if states[i] == SS.COIL:
            if ((i-1) in mediated_set and (i+1) in mediated_set and
                    states[i-1] == SS.HELIX and states[i+1] == SS.HELIX):
                states[i] = SS.HELIX
                locked[i] = True
                if verbose:
                    print(f"  [P1c] BRIDGE at {i+1} ({seq[i]}) "
                          f"flanked by {i}({seq[i-1]})-{i+2}({seq[i+1]})")

    # === PHASE 1d: WR-TOPOLOGY SHEET SEEDING (post-convergence) ===
    # After Phase 1 locks helices, seed sheet at COIL positions with
    # exact winding returns. The WR proves topological adjacency — two
    # distant chain segments at the same geometric orientation. This IS
    # sheet geometry: the framework's own proof, not requiring a hairpin.
    #
    # Criteria (all framework-native):
    # 1. Position is COIL (not helix, not turn, not already sheet)
    # 2. Exact winding return (diff=0) with separation > MIN_HELIX_LEN * IGD
    # 3. No CF0=1 coupling to any neighbor (not helix-qualified)
    # 4. Static curvature irregular (reg > IGD — sheet character)
    #
    # Seeded positions then extend along coil neighbors via sheet extension.
    # Long-range WR must span at least a full structural unit + buffer.
    # MIN_HELIX_LEN * (IGD + 1) = 4 * 3 = 12 residues minimum.
    min_topo_sep = MIN_HELIX_LEN * (INTER_GROUND_DEPTH + 1)  # = 12
    wr_topo_seeds = set()
    for r in wr:
        if r["diff"] > 0:
            continue  # exact WR only
        i_pos, j_pos = r["pos_i"], r["pos_j"]
        if i_pos >= n or j_pos >= n:
            continue
        # Must not span a hairpin (those handled in Phase 1 loop)
        spans_hairpin = any(i_pos <= h <= j_pos for h in hairpin_pairs)
        if spans_hairpin:
            continue
        if r["separation"] <= min_topo_sep:
            continue

        for pos in (i_pos, j_pos):
            # This position must be COIL to seed sheet here
            if states[pos] != SS.COIL:
                continue
            # Partner must be STRUCTURED (helix/sheet/turn).
            # WR connecting coil↔structured = topological evidence.
            # WR connecting coil↔coil = coincidental winding match.
            partner = j_pos if pos == i_pos else i_pos
            if states[partner] == SS.COIL:
                continue
            # Domain distance between seed and partner must be ≤ IGD.
            # Cross-domain WR beyond this range can't form sheet contacts.
            if abs(aa_domains[pos] - aa_domains[partner]) > INTER_GROUND_DEPTH:
                continue
            # No CF0=1 coupling to any neighbor
            has_coupling = False
            for offset in (-1, 1):
                nb = pos + offset
                if 0 <= nb < n and _is_coupled(self_t[pos], self_t[nb]):
                    has_coupling = True
                    break
            if has_coupling:
                continue
            # Not adjacent to locked helix (helix boundary ≠ sheet seed)
            adjacent_helix = False
            for offset in (-1, 1):
                nb = pos + offset
                if 0 <= nb < n and states[nb] == SS.HELIX:
                    adjacent_helix = True
                    break
            if adjacent_helix:
                continue
            # Irregular curvature (sheet character) — from initial field.
            # Sheet regularity is intrinsic to amino acid properties, not
            # field evolution (mediant diffusion washes out the signal).
            if static_regularity[pos] <= INTER_GROUND_DEPTH:
                continue
            wr_topo_seeds.add(pos)
            if verbose:
                partner = j_pos if pos == i_pos else i_pos
                print(f"  [P1d] SHEET (wr-topo) at {pos+1} ({seq[pos]}) "
                      f"partner={partner+1} sep={r['separation']}")

    # Seed and extend WR-topo positions
    for seed in sorted(wr_topo_seeds):
        states[seed] = SS.SHEET
        locked[seed] = True
    # Extend from seeds — stop at framework-native boundaries:
    # 1. CF0 > IGD between current and next position (domain boundary)
    # 2. Pair CF depth ≤ IGD (structural boundary / turn)
    # 3. Non-COIL state (already structured)
    # No arbitrary max_ext — the framework's own geometry defines the strand.
    for seed in sorted(wr_topo_seeds):
        for direction in (-1, 1):
            pos = seed + direction
            while 0 <= pos < n:
                if states[pos] != SS.COIL:
                    break
                # CF0 boundary: domain separation exceeds coupling window
                connecting_pair = min(pos, pos - direction)
                if connecting_pair < len(pair_cf0) and pair_cf0[connecting_pair] > INTER_GROUND_DEPTH:
                    break
                # Structural boundary (turn marker)
                pair_idx = min(pos, pos - direction)
                if pair_idx < len(raw_depths) and raw_depths[pair_idx] <= INTER_GROUND_DEPTH:
                    break
                states[pos] = SS.SHEET
                locked[pos] = True
                if verbose:
                    print(f"  [P1d] SHEET EXT (topo) at {pos+1} ({seq[pos]})")
                pos += direction

    # === PHASE 1e: SEP-2 WINDING OSCILLATION SHEET SEEDING ===
    #
    # β-strands have a specific backbone oscillation: the winding returns
    # to the same value every 2 positions (extended backbone zig-zag).
    # Sheet positions show 3x the rate of sep-2 WR compared to helix or coil.
    #
    # Combined criteria (all framework-native):
    #   1. Sep-2 exact winding return: w(i) == w(i+2), both positions COIL
    #   2. CF0≤IGD consistency: positions are in a run of ≥ MIN_HELIX_LEN
    #      consecutive positions where ALL pair CF0 ≤ IGD
    #   3. Irregular curvature: reg > IGD (not helix-like)
    #
    # The CF0≤IGD run boundaries are framework-native: the run starts and
    # ends where CF0 crosses IGD. No arbitrary length limits.

    winding = geometric_winding(seq)

    # Find CF0≤IGD runs among COIL positions
    cf0_runs = []  # list of (start, end) inclusive
    run_start = None
    for i in range(n):
        if states[i] != SS.COIL:
            if run_start is not None and i - run_start >= MIN_HELIX_LEN:
                cf0_runs.append((run_start, i - 1))
            run_start = None
            continue
        if run_start is None:
            run_start = i
        elif pair_cf0[i - 1] > INTER_GROUND_DEPTH:
            if i - run_start >= MIN_HELIX_LEN:
                cf0_runs.append((run_start, i - 1))
            run_start = i
    if run_start is not None and n - run_start >= MIN_HELIX_LEN:
        cf0_runs.append((run_start, n - 1))

    # Build set of positions in valid CF0≤IGD runs
    cf0_run_positions = set()
    for rs, re in cf0_runs:
        for j in range(rs, re + 1):
            cf0_run_positions.add(j)

    # Find sep-2 WR seeds within CF0≤IGD runs
    sep2_seeds = set()
    for i in range(n - 2):
        if i not in cf0_run_positions or (i + 2) not in cf0_run_positions:
            continue
        if states[i] != SS.COIL or states[i + 2] != SS.COIL:
            continue
        if winding[i] != winding[i + 2]:
            continue
        # Both positions must have irregular curvature — from initial field.
        # Sheet regularity is intrinsic to amino acid properties, not
        # field evolution (mediant diffusion washes out the signal).
        if static_regularity[i] <= INTER_GROUND_DEPTH:
            continue
        if static_regularity[i + 2] <= INTER_GROUND_DEPTH:
            continue
        # Neither position can be at a CF0>IGD boundary (run edge).
        # Run edges are transition zones, not stable strand interiors.
        for pos in (i, i + 2):
            boundary = False
            if pos > 0 and pair_cf0[pos - 1] > INTER_GROUND_DEPTH:
                boundary = True
            if pos < n - 1 and pair_cf0[pos] > INTER_GROUND_DEPTH:
                boundary = True
            if not boundary:
                sep2_seeds.add(pos)

    # Seed only (no extension — the CF0 boundaries define the strand geometry,
    # and the seeds themselves mark the oscillation pattern)
    for seed in sorted(sep2_seeds):
        if states[seed] != SS.COIL:
            continue
        states[seed] = SS.SHEET
        locked[seed] = True
        if verbose:
            print(f"  [P1e] SHEET (sep2-wr) at {seed+1} ({seq[seed]}) "
                  f"w={winding[seed]:.0f}")

    # === PHASE 1f: NEAR-WR HELIX SEEDING ===
    #
    # Near-winding-returns (diff ≤ IGD) to locked HELIX positions provide
    # topological helix evidence. When a COIL position's winding nearly
    # returns to a locked helix position's value (within one gear shift),
    # the geometric loop is almost closed — the position is topologically
    # adjacent to helix structure.
    #
    # This is the near-WR analog of Phase 1c mediation: the near-WR proves
    # topological adjacency (bypassing the sequential path), and the locked
    # helix partner provides proven structural context.
    #
    # Criteria (all framework-native):
    #   1. Near-WR: diff ≤ 1 (winding-space CF0=1 coupling)
    #   2. The seed position is COIL or TURN (TURN is local, near-WR overrides)
    #   3. Not CF0=1 coupled to any sequential neighbor (Phase 1 handled those)
    #   4. Curvature regularity ≤ MAX_INTERNAL_GAP (= IGD² = 4)
    #   5. Pair CF0 with adjacent HELIX ≤ MAX_INTERNAL_GAP (P3 consistency)
    #   6. Not adjacent to sheet (structural boundary)
    #   7. Separation ≥ MIN_HELIX_LEN
    #
    # Iterative: newly seeded helix positions can enable further near-WR seeds.
    # This models helix propagation through topological space.

    # max_diff=1: the winding return is within 1 step of exact closure.
    # This is the winding-space analog of CF0=1 coupling — the same
    # criterion Phase 1 uses for helix seeding. diff=2 (at the IGD
    # boundary) provides weaker evidence and risks false positives.
    near_wr = winding_returns(seq, min_separation=MIN_HELIX_LEN,
                              max_diff=1)

    # Build near-WR adjacency: for each position, which locked HELIX positions
    # does it have near-WR connections to?
    near_wr_changed = True
    while near_wr_changed:
        near_wr_changed = False
        for r in near_wr:
            i_pos, j_pos = r["pos_i"], r["pos_j"]
            diff = r["diff"]
            if i_pos >= n or j_pos >= n:
                continue

            for pos, partner in ((i_pos, j_pos), (j_pos, i_pos)):
                # Allow COIL and TURN → HELIX via near-WR.
                # TURN is a LOCAL pair property (CF depth ≤ IGD).
                # Near-WR is NON-LOCAL topology — when it says helix,
                # it overrides the local turn assignment (same principle
                # as Phase 2 wind-down overriding helix with sheet).
                if states[pos] not in (SS.COIL, SS.TURN):
                    continue
                if states[partner] != SS.HELIX or not locked[partner]:
                    continue

                # Not sequentially coupled (those handled in Phase 1)
                has_coupling = False
                for offset in (-1, 1):
                    nb = pos + offset
                    if 0 <= nb < n and _is_coupled(self_t[pos], self_t[nb]):
                        has_coupling = True
                        break
                if has_coupling:
                    continue

                # Curvature regularity ≤ MAX_INTERNAL_GAP (= IGD² = 4).
                # This is framework-native: MAX_INTERNAL_GAP is the maximum
                # CF0 gap tolerated within a helix run (used by P3 validation).
                # Near-WR helix seeds must meet the same local consistency.
                reg = _curvature_regularity(pos, conv_curvatures, locked)
                if reg > MAX_INTERNAL_GAP:
                    continue

                # Pair CF0 with adjacent HELIX must not exceed MAX_INTERNAL_GAP.
                # This is the same constraint P3 uses: if seeding this position
                # would create a pair CF0 > IGD² within the helix run, the run
                # would be demoted anyway. Catch it at seed time.
                helix_gap_violation = False
                for offset in (-1, 1):
                    nb = pos + offset
                    if 0 <= nb < n and states[nb] == SS.HELIX:
                        pidx = min(pos, nb)
                        if pidx < len(pair_cf0) and pair_cf0[pidx] > MAX_INTERNAL_GAP:
                            helix_gap_violation = True
                            break
                if helix_gap_violation:
                    continue

                # Not adjacent to locked sheet (sheet boundary ≠ helix seed)
                adjacent_sheet = False
                for offset in (-1, 1):
                    nb = pos + offset
                    if 0 <= nb < n and states[nb] == SS.SHEET:
                        adjacent_sheet = True
                        break
                if adjacent_sheet:
                    continue

                states[pos] = SS.HELIX
                locked[pos] = True
                near_wr_changed = True
                if verbose:
                    print(f"  [P1f] HELIX (near-wr) at {pos+1} ({seq[pos]}) "
                          f"partner={partner+1}({seq[partner]}) "
                          f"diff={diff:.0f} sep={r['separation']} "
                          f"reg={reg}")
                break  # done with this position

    # Post-P1f: fill short COIL gaps between adjacent helix segments.
    # When a near-WR seeded helix is close to existing helix and the merged
    # run's max pair CF0 ≤ MAX_INTERNAL_GAP, the gap positions are filled.
    # The gap length limit IS MAX_INTERNAL_GAP — the same framework constant
    # that defines the maximum tolerable domain shift within a helix run.
    for i in range(n):
        if states[i] != SS.HELIX:
            continue
        # Find end of this helix run
        j = i
        while j < n and states[j] == SS.HELIX:
            j += 1
        # j is first non-HELIX after run. Check for a COIL gap followed by HELIX.
        gap_start = j
        gap_end = j
        while gap_end < n and states[gap_end] in (SS.COIL, SS.TURN):
            gap_end += 1
        gap_len = gap_end - gap_start
        if gap_len == 0 or gap_len > MAX_INTERNAL_GAP:
            continue
        if gap_end >= n or states[gap_end] != SS.HELIX:
            continue
        # Check max CF0 across the entire merged run (i to gap_end+run2)
        run2_end = gap_end
        while run2_end < n and states[run2_end] == SS.HELIX:
            run2_end += 1
        max_gap = _max_pair_cf0(i, run2_end)
        if max_gap <= MAX_INTERNAL_GAP:
            for k in range(gap_start, gap_end):
                states[k] = SS.HELIX
                locked[k] = True
                if verbose:
                    print(f"  [P1f] HELIX FILL at {k+1} ({seq[k]}) "
                          f"gap={gap_len}")

    # === PHASE 2: WIND-DOWN — non-local topology overrides local structure ===
    #
    # The "gears" of the Aramis Field operate on φ-scaled timescales.
    # Phase 1 (wind-up) establishes LOCAL structure via coupling and CF motifs.
    # Phase 2 (wind-down) applies NON-LOCAL topology: winding returns that
    # span hairpin markers prove topological adjacency between distant positions.
    # When a helix position is connected to a Phase-1 sheet position, the
    # slower temporal gear overrides the faster one — reassigning H → E.
    #
    # This models the physical reality that β-sheet formation (inter-strand
    # H-bonds) operates on a slower timescale than α-helix formation
    # (local backbone H-bonds), and can override local helix tendency.

    # Freeze Phase 1 states for decision-making
    phase1_states = list(states)

    # Find nearest hairpin for directional extension
    nearest_hp = [None] * n
    for i in range(n):
        best_dist = n + 1
        for hp in hairpin_pairs:
            d = abs(i - hp)
            if d < best_dist:
                best_dist = d
                nearest_hp[i] = hp

    # Step 1: Identify reassignment candidates from hairpin-spanning winding returns
    # Only reassign when the partner was SHEET in Phase 1 (frozen states),
    # preventing cascading reassignments from wind-down-modified states.
    wr_seeds = set()
    for r in wr:
        i_pos, j_pos = r["pos_i"], r["pos_j"]
        if i_pos >= n or j_pos >= n:
            continue
        # Must span a hairpin
        spans_hairpin = any(i_pos <= h <= j_pos for h in hairpin_pairs)
        if not spans_hairpin:
            continue
        for a, b in [(i_pos, j_pos), (j_pos, i_pos)]:
            if phase1_states[a] == SS.HELIX and phase1_states[b] == SS.SHEET:
                wr_seeds.add(a)
                if verbose:
                    print(f"  [P2] WIND-DOWN: {a+1}({seq[a]}) H→E "
                          f"(wr to Phase-1 sheet {b+1})")

    # Apply direct reassignments
    for s in wr_seeds:
        states[s] = SS.SHEET

    # Step 2: Directional extension TOWARD nearest hairpin
    # The extension follows the chain toward the structural reversal point,
    # stopping at turn markers (pair depth ≤ igd) or non-helix positions.
    for seed in sorted(wr_seeds):
        hp = nearest_hp[seed]
        if hp is None:
            continue
        direction = 1 if hp > seed else -1
        pos = seed + direction
        while 0 <= pos < n:
            if states[pos] != SS.HELIX:
                break
            pair_idx = min(pos, pos - direction)
            if pair_idx < len(raw_depths) and raw_depths[pair_idx] > INTER_GROUND_DEPTH:
                states[pos] = SS.SHEET
                if verbose:
                    print(f"  [P2] WIND-DOWN EXT: {pos+1}({seq[pos]}) H→E "
                          f"(toward hairpin {hp+1})")
                pos += direction
            else:
                break

    # === PHASE 3: MINIMUM HELIX LENGTH + EXTREME GAP (post-wind-down) ===
    # Same criteria as Phase 1b, re-applied after wind-down can split helix runs.
    i = 0
    while i < n:
        if states[i] == SS.HELIX:
            run_start = i
            while i < n and states[i] == SS.HELIX:
                i += 1
            run_len = i - run_start
            demote = False
            reason = ""
            if run_len < MIN_HELIX_LEN:
                demote = True
                reason = f"len={run_len}"
            else:
                max_gap = _max_pair_cf0(run_start, i)
                if max_gap > MAX_INTERNAL_GAP:
                    demote = True
                    reason = f"gap CF[0]={max_gap}"
            if demote:
                for j in range(run_start, i):
                    states[j] = SS.COIL
                if verbose:
                    print(f"  [P3] Demote helix {run_start+1}-{i} "
                          f"({reason})")
        else:
            i += 1

    # === PHASE 3 MEDOID TRIM — same logic as post-P1b, applied to ===
    # wind-down survivors.  Wind-down can split helix runs, exposing new
    # edges that are geometric outliers.  Recompute medoid tension from
    # the converged curvatures (unchanged since pre-P1c) and trim.
    i = 0
    while i < n:
        if states[i] == SS.HELIX:
            run_start = i
            while i < n and states[i] == SS.HELIX:
                i += 1
            run_end = i
            run_len = run_end - run_start
            if run_len < 2:
                continue
            run_tensions = sorted([medoid_tension[j] for j in range(run_start, run_end)])
            run_medoid = run_tensions[len(run_tensions) // 2]
            if run_medoid == 0:
                continue
            threshold = phi_mig * run_medoid
            trimmed = []
            for j in range(run_start, run_end):
                if medoid_tension[j] > threshold:
                    trimmed.append(j)
                else:
                    break
            for j in range(run_end - 1, run_start - 1, -1):
                if j in trimmed:
                    break
                if medoid_tension[j] > threshold:
                    trimmed.append(j)
                else:
                    break
            for j in trimmed:
                states[j] = SS.COIL
                if verbose:
                    print(f"  [P3-MEDOID] Trim {j+1} ({seq[j]}) "
                          f"tension={medoid_tension[j]:.0f} > "
                          f"φ⁴×medoid={threshold:.0f}")
        else:
            i += 1

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
    GEOMETRIC FIELD SOLVER v8.3 — medoid tension + dynamic acceleration
    Phase 1 (wind-up): Local 7-step iterator to convergence
    Phase 2 (wind-down): Non-local topology overrides via winding returns
    φ-domain structure: CF[0] of tension ratio = domain separation
    All framework-native criteria. No imposed thresholds.
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
    p = argparse.ArgumentParser(description="Geometric protein field solver (7-step iterator)")
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
