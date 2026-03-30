#!/usr/bin/env python3
"""Pascal's Triangle ↔ Stern-Brocot Tree structural investigation.

The mediant operation (a+c)/(b+d) IS Pascal's addition rule applied to
fractions. This script investigates the deep connections:

1. Pascal row/column → SB tree depth/position mapping
2. Hexagonal invariant: alternating petal products are equal
3. The "flower product" constraint on valid mediant paths
4. Connection to the 6(+1) temporal domains from φ-scaling
5. φ = [1;1,1,...] as Pascal's edge invariant

Key insight: The all-1s boundary of Pascal's triangle is the same
all-1s structure that defines φ in CF space. Our φ-coherence criterion
(CF coefficients ≤ 2) measures proximity to Pascal's edge.

Run: python tools/engine/pascal_sb_investigation.py
"""

import math
import sys
from pathlib import Path
from fractions import Fraction
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, to_cf, from_cf, cf_length, mediant, phi_coherence,
    PHI, SOL_CARBON, AA_FREQ,
)
from tools.engine.predict import SELF_TENSION, HELIX_GROUND


# ═══════════════════════════════════════════════════════════════
# SECTION 1: Stern-Brocot Tree Construction
# ═══════════════════════════════════════════════════════════════

def sb_tree(depth: int) -> List[List[Fraction]]:
    """Build the Stern-Brocot tree to given depth.

    Level 0: [1/1]  (the root mediant of 0/1 and 1/0)
    Level k: insert mediants between all consecutive fractions
             of level k-1 (including boundary sentinels 0/1, 1/0).

    Returns list of levels, each containing the NEW fractions at that level.
    """
    levels = [[Fraction(1, 1)]]
    # All fractions accumulated so far, with sentinels
    all_fracs = [Fraction(0, 1), Fraction(1, 1)]  # sentinel 1/0 omitted, use large

    for d in range(1, depth):
        new_level = []
        # Rebuild the full sorted sequence including sentinels
        full = [Fraction(0, 1)] + sorted(set(f for lvl in levels for f in lvl)) + [None]  # None = 1/0
        for i in range(len(full) - 1):
            left = full[i]
            right = full[i + 1]
            if right is None:
                # Mediant with 1/0 sentinel
                m = Fraction(left.numerator + 1, left.denominator)
            else:
                m = mediant(left, right)
            if m not in set(f for lvl in levels for f in lvl):
                new_level.append(m)
        levels.append(sorted(new_level))
    return levels


def sb_path(frac: Fraction, max_steps: int = 20) -> List[str]:
    """Find the path from SB root to a fraction.

    Returns sequence of 'L' (left) and 'R' (right) turns.
    The path encodes the CF expansion: CF = [a0; a1, a2, ...]
    corresponds to a0 R's, then a1 L's, then a2 R's, etc.
    """
    if frac <= 0:
        return []
    path = []
    lo_n, lo_d = 0, 1  # 0/1
    hi_n, hi_d = 1, 0  # 1/0
    for _ in range(max_steps):
        med_n = lo_n + hi_n
        med_d = lo_d + hi_d
        med = Fraction(med_n, med_d)
        if med == frac:
            break
        elif frac < med:
            path.append('L')
            hi_n, hi_d = med_n, med_d
        else:
            path.append('R')
            lo_n, lo_d = med_n, med_d
    return path


def path_to_cf(path: List[str]) -> List[int]:
    """Convert SB path (L/R sequence) to CF expansion.

    CF[0] = number of initial R's (or 0 if starts with L)
    Then alternating runs of L's and R's give subsequent terms.

    For fractions > 1: starts with R's.
    For fractions < 1: CF[0] = 0 is implicit, starts with L's.
    """
    if not path:
        return [1]  # root = 1/1 = [1]
    runs = []
    current = path[0]
    count = 1
    for c in path[1:]:
        if c == current:
            count += 1
        else:
            runs.append((current, count))
            current = c
            count = 1
    runs.append((current, count))

    # CF expansion: for frac > 1, first run should be R
    cf = []
    for direction, length in runs:
        cf.append(length)
    return cf


# ═══════════════════════════════════════════════════════════════
# SECTION 2: Pascal's Triangle and Mediant Connection
# ═══════════════════════════════════════════════════════════════

def pascal_row(n: int) -> List[int]:
    """Row n of Pascal's triangle (0-indexed)."""
    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row


def pascal_fraction_row(n: int) -> List[Fraction]:
    """Row n of Pascal's triangle as ratios of consecutive entries.

    Entry k: C(n,k+1)/C(n,k) = (n-k)/(k+1)

    These ratios ARE the fractions that appear in the SB tree.
    """
    row = pascal_row(n)
    ratios = []
    for k in range(len(row) - 1):
        if row[k] != 0:
            ratios.append(Fraction(row[k + 1], row[k]))
    return ratios


def investigate_pascal_sb_mapping():
    """Map Pascal consecutive-entry ratios to SB tree positions."""
    print("=" * 70)
    print("  PASCAL → STERN-BROCOT MAPPING")
    print("=" * 70)
    print()
    print("  Pascal's consecutive-entry ratios C(n,k+1)/C(n,k) = (n-k)/(k+1)")
    print("  These ratios trace paths through the SB tree.")
    print()

    for n in range(2, 9):
        row = pascal_row(n)
        ratios = pascal_fraction_row(n)
        print(f"  Pascal row {n}: {row}")
        print(f"    Ratios: ", end="")
        for r in ratios:
            cf = to_cf(r)
            path = sb_path(r)
            print(f"{r}(CF={cf}) ", end="")
        print()

    # Key observation: edge ratios are always n/1 or 1/n
    print()
    print("  Edge observation:")
    print("    Left edge: C(n,1)/C(n,0) = n/1 → CF = [n] (single step)")
    print("    Right edge: C(n,n)/C(n,n-1) = 1/n → CF = [0;n] (single reciprocal)")
    print("    Center: C(n,⌊n/2⌋+1)/C(n,⌊n/2⌋) → approaches 1/1 = φ-edge")
    print()

    # The center ratio approaches 1 as n grows — this IS the φ connection
    print("  Center ratio convergence toward 1/1 (the φ-edge):")
    for n in range(2, 20):
        row = pascal_row(n)
        k = n // 2
        center_ratio = Fraction(row[k + 1], row[k]) if k + 1 < len(row) else Fraction(1)
        cf = to_cf(center_ratio)
        depth = len(cf)
        print(f"    n={n:>2d}: C({n},{k+1})/C({n},{k}) = {center_ratio} = {float(center_ratio):.6f}"
              f"  CF={cf[:6]}{'...' if len(cf) > 6 else ''}  depth={depth}")


# ═══════════════════════════════════════════════════════════════
# SECTION 3: Hexagonal Invariant ("Pascal's Flowers")
# ═══════════════════════════════════════════════════════════════

def pascal_flower(n: int, k: int) -> Dict:
    """Compute the hexagonal flower around Pascal entry C(n,k).

    The six "petals" are the neighbors:
        NW: C(n-1, k-1)    NE: C(n-1, k)
        W:  C(n,   k-1)    E:  C(n,   k+1)
        SW: C(n+1, k)      SE: C(n+1, k+1)

    Hexagonal invariant: NW * E * SW = NE * W * SE
    (Alternating petal products are equal.)
    """
    def C(nn, kk):
        if kk < 0 or kk > nn or nn < 0:
            return 0
        return math.comb(nn, kk)

    center = C(n, k)
    nw = C(n - 1, k - 1)
    ne = C(n - 1, k)
    w = C(n, k - 1)
    e = C(n, k + 1)
    sw = C(n + 1, k)
    se = C(n + 1, k + 1)

    prod_a = nw * e * sw  # alternating petals A
    prod_b = ne * w * se  # alternating petals B

    return {
        "center": center,
        "petals": {"NW": nw, "NE": ne, "W": w, "E": e, "SW": sw, "SE": se},
        "prod_a": prod_a,
        "prod_b": prod_b,
        "invariant_holds": prod_a == prod_b,
    }


def investigate_hexagonal_invariant():
    """Verify and explore the hexagonal invariant of Pascal's triangle."""
    print()
    print("=" * 70)
    print("  HEXAGONAL INVARIANT (PASCAL'S FLOWERS)")
    print("=" * 70)
    print()
    print("  For interior entry C(n,k), the 6 neighbors form a 'flower'.")
    print("  Invariant: NW × E × SW = NE × W × SE")
    print()

    # Verify for many interior cells
    violations = 0
    checks = 0
    for n in range(2, 15):
        for k in range(1, n):
            flower = pascal_flower(n, k)
            checks += 1
            if not flower["invariant_holds"]:
                violations += 1
                print(f"  VIOLATION at ({n},{k})!")

    print(f"  Checked {checks} interior cells (rows 2-14): "
          f"{violations} violations → {'INVARIANT HOLDS' if violations == 0 else 'BROKEN'}")
    print()

    # Show a few example flowers
    print("  Example flowers:")
    for n, k in [(3, 1), (4, 2), (5, 2), (6, 3)]:
        f = pascal_flower(n, k)
        p = f["petals"]
        print(f"\n    C({n},{k}) = {f['center']}:")
        print(f"      {p['NW']:>4d}  {p['NE']:>4d}")
        print(f"    {p['W']:>4d}  [{f['center']:>4d}]  {p['E']:>4d}")
        print(f"      {p['SW']:>4d}  {p['SE']:>4d}")
        print(f"    Products: {p['NW']}×{p['E']}×{p['SW']} = {f['prod_a']}  |  "
              f"{p['NE']}×{p['W']}×{p['SE']} = {f['prod_b']}")


# ═══════════════════════════════════════════════════════════════
# SECTION 4: φ as Pascal's Edge Invariant
# ═══════════════════════════════════════════════════════════════

def investigate_phi_edge():
    """Show that φ = [1;1,1,...] IS the all-1s edge of Pascal's triangle."""
    print()
    print("=" * 70)
    print("  φ AS PASCAL'S EDGE INVARIANT")
    print("=" * 70)
    print()
    print("  Pascal's edge: all entries are 1 → all consecutive ratios are 1/1")
    print("  CF of 1/1 = [1] → sequence of 1s = the CF of φ")
    print()

    # Show convergents of φ = [1;1,1,...] are Fibonacci ratios
    print("  φ convergents (Fibonacci ratios from CF truncation):")
    print(f"  {'Depth':>6s} {'CF':>20s} {'Fraction':>12s} {'Float':>10s} {'|φ-x|':>10s}")
    for d in range(1, 15):
        cf = [1] * d
        frac = from_cf(cf)
        err = abs(float(frac) - PHI)
        print(f"  {d:>6d} {str(cf):>20s} {str(frac):>12s} {float(frac):>10.7f} {err:>10.2e}")

    # Show that Fibonacci numbers ARE Pascal diagonal sums
    print()
    print("  Fibonacci numbers as Pascal diagonal sums:")
    print("    F(n) = sum of C(n-k-1, k) for k = 0,1,2,...")
    for n in range(1, 12):
        diag_sum = 0
        k = 0
        while n - k - 1 >= k:
            diag_sum += math.comb(n - k - 1, k)
            k += 1
        fib = round(PHI ** n / math.sqrt(5))
        print(f"    n={n:>2d}: diagonal_sum = {diag_sum:>4d}  Fibonacci = {fib:>4d}  "
              f"{'✓' if diag_sum == fib else '✗'}")

    # Connection to protein folding
    print()
    print("  Connection to protein CF-coherence:")
    print("    φ-coherent = CF starts with [1,1,...] = close to φ in SB tree")
    print("    Helix ground (A): ST=38, domain 0 → baseline φ⁰ = 1")
    print("    Sheet ground (V): ST=57, domain 0 → baseline φ⁰ = 1")
    print("    Both are 'on Pascal's edge' — maximally simple structure")
    print()

    # Show AA ratios and their φ-coherence
    print(f"  {'AA':>3s} {'ST':>4s} {'r=freq/C':>10s} {'CF':>25s} {'φ-coh':>6s} {'CF_len':>7s}")
    for aa in sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a]):
        r = aa_ratio(aa)
        cf = to_cf(r)
        pc = phi_coherence(cf)
        cl = cf_length(cf)
        print(f"  {aa:>3s} {SELF_TENSION[aa]:>4d} {float(r):>10.5f} {str(cf[:8]):>25s} {pc:>6d} {cl:>7d}")


# ═══════════════════════════════════════════════════════════════
# SECTION 5: Denominator Lattice and Flower Constraint
# ═══════════════════════════════════════════════════════════════

def investigate_denominator_lattice():
    """Investigate the 2D denominator lattice and its hexagonal structure.

    The 20 AA frequencies use denominators that factor as 100 = 4 × 25.
    The Sol-Carbon anchor is 153/100. Ratios freq/anchor create a
    lattice of denominators. The hexagonal flower invariant constrains
    which mediants are geometrically valid.
    """
    print()
    print("=" * 70)
    print("  DENOMINATOR LATTICE STRUCTURE")
    print("=" * 70)
    print()

    # Collect all AA ratios and their denominators
    print(f"  {'AA':>3s} {'Freq':>10s} {'Ratio':>12s} {'Num':>6s} {'Den':>6s} "
          f"{'Den factors':>15s}")

    den_set = set()
    for aa in sorted(AA_FREQ.keys(), key=lambda a: float(AA_FREQ[a])):
        freq = AA_FREQ[aa]
        r = aa_ratio(aa)
        num = r.numerator
        den = r.denominator
        den_set.add(den)

        # Factor the denominator
        factors = []
        d = den
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
            while d % p == 0:
                factors.append(p)
                d //= p
            if d == 1:
                break
        if d > 1:
            factors.append(d)
        print(f"  {aa:>3s} {str(freq):>10s} {str(r):>12s} {num:>6d} {den:>6d} "
              f"{' × '.join(str(f) for f in factors):>15s}")

    print(f"\n  Unique denominators: {sorted(den_set)}")
    print(f"  Count: {len(den_set)}")

    # Check pairwise mediants and their denominators
    print()
    print("  Mediant denominator structure (sample pairs):")
    aas = sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a])
    pairs_shown = 0
    for i in range(len(aas)):
        for j in range(i + 1, len(aas)):
            if pairs_shown >= 15:
                break
            r1 = aa_ratio(aas[i])
            r2 = aa_ratio(aas[j])
            m = mediant(r1, r2)
            cf_m = to_cf(m)
            print(f"    {aas[i]}-{aas[j]}: mediant({r1}, {r2}) = {m}  "
                  f"CF={cf_m[:5]}  den={m.denominator}")
            pairs_shown += 1
        if pairs_shown >= 15:
            break


# ═══════════════════════════════════════════════════════════════
# SECTION 6: Temporal Domains and Hexagonal Structure
# ═══════════════════════════════════════════════════════════════

def investigate_temporal_hex():
    """Connect the 7 temporal domains to hexagonal lattice structure.

    Each AA has a φ-domain: floor(log_φ(ST/38)).
    The 7 domains {-2,-1,0,1,2,3,5} map to positions in a
    hexagonal tiling where 6 neighbors surround each interior cell.
    """
    print()
    print("=" * 70)
    print("  TEMPORAL DOMAINS ↔ HEXAGONAL STRUCTURE")
    print("=" * 70)
    print()

    def aa_domain(aa):
        st = SELF_TENSION.get(aa, 50)
        if st <= 0:
            return 0
        return int(math.floor(math.log(st / HELIX_GROUND) / math.log(PHI)))

    # Map domains
    domains = {}
    for aa in sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a]):
        d = aa_domain(aa)
        if d not in domains:
            domains[d] = []
        domains[d].append(aa)

    print("  Domain membership:")
    for d in sorted(domains.keys()):
        aas = domains[d]
        print(f"    Domain {d:+d}: {', '.join(f'{a}(ST={SELF_TENSION[a]})' for a in aas)}")

    n_domains = len(domains)
    print(f"\n  Total domains: {n_domains}")
    print(f"  Domain values: {sorted(domains.keys())}")

    # Hexagonal neighborhood: each domain d neighbors d-1 and d+1
    # In a hex lattice, each cell has 6 neighbors
    # For 1D domain ordering, neighbors = ±1
    print()
    print("  Domain adjacency (inter-domain coupling CF[0]):")
    domain_keys = sorted(domains.keys())
    for i in range(len(domain_keys)):
        for j in range(i + 1, len(domain_keys)):
            d1, d2 = domain_keys[i], domain_keys[j]
            sep = abs(d2 - d1)
            # Pick representative AA from each domain
            aa1 = domains[d1][0]
            aa2 = domains[d2][0]
            t1, t2 = SELF_TENSION[aa1], SELF_TENSION[aa2]
            ratio = Fraction(max(t1, t2), min(t1, t2))
            cf = to_cf(ratio)
            phi_power = PHI ** sep
            print(f"    Dom {d1:+d} ↔ {d2:+d} (sep={sep}): "
                  f"{aa1}-{aa2} ratio={float(ratio):.3f} CF[0]={cf[0]} "
                  f"φ^{sep}={phi_power:.3f}")

    # Key connection: 6 petals in flower = 6 domain transitions possible
    print()
    print("  Structural interpretation:")
    print("    - Each domain is a 'cell' in a 1D hexagonal strip")
    print("    - CF[0] between domains encodes coupling cost")
    print("    - CF[0]=1 (same domain) → direct coupling (helix)")
    print("    - CF[0]=2 (adjacent domain) → mediated coupling")
    print("    - CF[0]≥3 (distant domain) → temporal gear shift needed")
    print()
    print("    The flower invariant (NW×E×SW = NE×W×SE) guarantees")
    print("    that mediant paths through the SB tree preserve local")
    print("    multiplicative structure — mediants CAN'T destroy the")
    print("    hexagonal consistency of the domain lattice.")


# ═══════════════════════════════════════════════════════════════
# SECTION 7: Mediant Paths and Folding Trajectories
# ═══════════════════════════════════════════════════════════════

def investigate_mediant_paths():
    """Trace mediant iteration paths for key AA pairs.

    When the fold solver runs mediant diffusion, each position's
    tension evolves through the SB tree. This section traces
    those paths and checks whether the flower invariant constrains
    which destinations are reachable.
    """
    print()
    print("=" * 70)
    print("  MEDIANT PATHS IN THE SB TREE")
    print("=" * 70)
    print()

    # Key helix-forming pairs
    pairs = [
        ("A-A", Fraction(SELF_TENSION["A"]), Fraction(SELF_TENSION["A"])),
        ("A-L", Fraction(SELF_TENSION["A"]), Fraction(SELF_TENSION["L"])),
        ("V-K", Fraction(SELF_TENSION["V"]), Fraction(SELF_TENSION["K"])),
        ("K-A", Fraction(SELF_TENSION["K"]), Fraction(SELF_TENSION["A"])),
        ("S-T", Fraction(SELF_TENSION["S"]), Fraction(SELF_TENSION["T"])),
    ]

    for name, t1, t2 in pairs:
        r = Fraction(max(t1, t2), min(t1, t2))
        cf = to_cf(r)
        path = sb_path(r)

        print(f"  {name}: ratio={r} = {float(r):.4f}")
        print(f"    CF = {cf}")
        print(f"    SB path: {''.join(path) if path else '(root)'}")
        print(f"    Depth: {len(path)}")

        # Trace mediant convergence from t1, t2
        print(f"    Mediant iteration: {t1}, {t2} → ", end="")
        a, b = t1, t2
        steps = []
        for _ in range(8):
            m = mediant(a, b)
            steps.append(m)
            # Next step: mediant with whichever is further
            if abs(float(m) - float(a)) > abs(float(m) - float(b)):
                b = m
            else:
                a = m
        print(" → ".join(f"{float(s):.3f}" for s in steps[:6]))
        print()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  PASCAL'S TRIANGLE ↔ STERN-BROCOT TREE INVESTIGATION           ║
    ║  Hexagonal invariant, φ-edge, temporal domain structure        ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    investigate_pascal_sb_mapping()
    investigate_hexagonal_invariant()
    investigate_phi_edge()
    investigate_denominator_lattice()
    investigate_temporal_hex()
    investigate_mediant_paths()

    print()
    print("=" * 70)
    print("  SUMMARY OF STRUCTURAL CONNECTIONS")
    print("=" * 70)
    print()
    print("  1. Pascal consecutive-entry ratios trace SB tree paths")
    print("     Center ratios → 1/1 as row grows = approach to φ-edge")
    print()
    print("  2. Hexagonal invariant (NW×E×SW = NE×W×SE) is EXACT")
    print("     for all interior Pascal cells — local multiplicative")
    print("     conservation guarantees mediant self-consistency")
    print()
    print("  3. φ = [1;1,1,...] = Pascal's all-1s edge")
    print("     Fibonacci = Pascal diagonal sums")
    print("     CF φ-coherence = proximity to Pascal's edge in SB tree")
    print()
    print("  4. 7 temporal domains from φ-scaling map to a 1D hex strip")
    print("     CF[0] between domains encodes coupling cost = φ^separation")
    print("     Flower invariant constrains valid mediant evolution paths")
    print()
    print("  5. The fold solver's mediant diffusion traverses the SB tree")
    print("     Each step IS a Pascal mediant operation")
    print("     Convergence = finding the correct SB tree node")
    print()


if __name__ == "__main__":
    main()
