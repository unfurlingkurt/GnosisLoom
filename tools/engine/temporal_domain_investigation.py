#!/usr/bin/env python3
"""Temporal domain analysis of amino acid φ-scaling.

Investigation: The 20 amino acids partition into φ-domains based on
log_φ(self_tension / helix_ground). CF[0] of the tension ratio between
two amino acids encodes their domain separation — this IS the number
of temporal "gear shifts" needed for coupling.

Key findings:
  1. AAs partition into 7 φ-domains: {-2, -1, 0, 1, 2, 3, 5}
  2. CF[0] ≈ ceil(φ^|domain_separation|) for inter-domain pairs
  3. The K-A coupling gap (CF[0]=4) corresponds to a 2-domain
     separation: K is domain 2, A is domain 0, φ² ≈ 2.62
  4. The folding process needs TWO temporal phases:
     - Wind-up: local coupling (fast gear, same domain)
     - Wind-down: non-local topology overrides (slow gear, cross-domain)

Run: python tools/engine/temporal_domain_investigation.py
"""

import math
import sys
from pathlib import Path
from fractions import Fraction

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.engine.rscode import (
    aa_ratio, to_cf, cf_length, PHI, SOL_CARBON
)
from tools.engine.predict import (
    SELF_TENSION, HELIX_GROUND, SHEET_GROUND,
    LYSOZYME_SEQ, LYSOZYME_DSSP,
)


def aa_domain(aa):
    """φ-domain of an amino acid: floor(log_φ(ST/helix_ground))."""
    st = SELF_TENSION.get(aa, 50)
    if st <= 0:
        return 0
    return int(math.floor(math.log(st / HELIX_GROUND) / math.log(PHI)))


def investigate_domain_structure():
    """Map all amino acids to their φ-domains."""
    print("=" * 70)
    print("  AMINO ACID φ-DOMAIN STRUCTURE")
    print("=" * 70)
    print()
    print(f"  Helix ground state: A = {HELIX_GROUND}")
    print(f"  Sheet ground state: V/D = {SHEET_GROUND}")
    print(f"  φ = {PHI:.6f}")
    print()

    domains = {}
    for aa in sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a]):
        st = SELF_TENSION[aa]
        d = aa_domain(aa)
        if d not in domains:
            domains[d] = []
        domains[d].append(aa)
        log_phi = math.log(st / HELIX_GROUND) / math.log(PHI)
        print(f"  {aa}: ST={st:>4d}  log_φ(ST/38) = {log_phi:>+6.3f}  → domain {d:+d}")

    print()
    print("  Domain summary:")
    for d in sorted(domains.keys()):
        aas = domains[d]
        sts = [SELF_TENSION[a] for a in aas]
        print(f"    Domain {d:+d}: {', '.join(f'{a}({SELF_TENSION[a]})' for a in aas)}")
        freq_lo = HELIX_GROUND * PHI ** d
        freq_hi = HELIX_GROUND * PHI ** (d + 1)
        print(f"      ST range: [{freq_lo:.1f}, {freq_hi:.1f})")

    return domains


def investigate_inter_domain_coupling():
    """Analyze how CF[0] encodes domain separation."""
    print()
    print("=" * 70)
    print("  CF[0] AS DOMAIN SEPARATION ENCODER")
    print("=" * 70)
    print()
    print("  φ-power vs CF[0] (theoretical):")
    for k in range(6):
        ratio = PHI ** k
        cf0 = int(ratio)
        print(f"    φ^{k} = {ratio:>7.3f}  →  CF[0] would be {cf0}")

    print()
    print("  Actual inter-domain CF[0] values:")
    print(f"  {'Pair':>6s} {'Dom':>5s} {'Sep':>4s} {'Ratio':>7s} {'CF[0]':>6s} "
          f"{'φ^sep':>7s} {'Match':>6s}")

    # Representative pairs from each domain combination
    all_aas = sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a])
    seen_pairs = set()
    for aa1 in all_aas:
        for aa2 in all_aas:
            d1 = aa_domain(aa1)
            d2 = aa_domain(aa2)
            d_sep = abs(d1 - d2)
            pair_key = (min(d1, d2), max(d1, d2))
            if pair_key in seen_pairs or d_sep == 0:
                continue
            if d_sep > 4:
                continue
            seen_pairs.add(pair_key)
            t1 = SELF_TENSION[aa1]
            t2 = SELF_TENSION[aa2]
            ratio = Fraction(max(t1, t2), min(t1, t2))
            cf = to_cf(ratio)
            phi_sep = PHI ** d_sep
            match = "~" if abs(cf[0] - round(phi_sep)) <= 1 else "X"
            print(f"  {aa1}-{aa2:>2s} {d1:+d}/{d2:+d} {d_sep:>4d} {float(ratio):>7.3f} "
                  f"{cf[0]:>6d} {phi_sep:>7.3f} {match:>6s}")


def investigate_coupling_chains():
    """Analyze coupling chain connectivity for key protein helices."""
    print()
    print("=" * 70)
    print("  COUPLING CHAIN ANALYSIS")
    print("=" * 70)

    # Ubiquitin helix: positions 24-34 (1-indexed)
    ubq = 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'
    ubq_d = 'EEEEEECCCCCCEEEECCCCCCCHHHHHHHHHHHCCCCEEEEEECCCCCCCCHHHHHHHHHHCCCCEEEEEECCCC'

    for name, seq, start, end in [
        ("Ubiquitin helix", ubq, 23, 34),
        ("Ubiquitin sheet 39-44", ubq, 38, 44),
    ]:
        print(f"\n  --- {name} (positions {start+1}-{end+1}) ---")
        print(f"  Sequence: {''.join(seq[i] for i in range(start, end+1))}")
        print(f"  DSSP:     {''.join(ubq_d[i] for i in range(start, end+1))}")
        print()
        print(f"  {'Pair':>8s} {'ST ratio':>10s} {'CF':>15s} {'CF[0]':>6s} "
              f"{'Dom':>5s} {'Coupled':>8s}")
        for i in range(start, end):
            aa1, aa2 = seq[i], seq[i + 1]
            t1, t2 = SELF_TENSION[aa1], SELF_TENSION[aa2]
            ratio = Fraction(max(t1, t2), min(t1, t2))
            cf = to_cf(ratio)
            d1 = aa_domain(aa1)
            d2 = aa_domain(aa2)
            coupled = "YES" if cf[0] == 1 else f"NO ({cf[0]})"
            print(f"  {aa1}({t1:>3d})-{aa2}({t2:>3d}) {float(ratio):>10.3f} "
                  f"{str(cf[:4]):>15s} {cf[0]:>6d} {d1:+d}/{d2:+d} {coupled:>8s}")


def investigate_temporal_frequencies():
    """Map temporal domains to physical frequencies."""
    print()
    print("=" * 70)
    print("  TEMPORAL DOMAIN FREQUENCIES")
    print("=" * 70)
    print()
    print(f"  Anchor: Sol-Carbon = {float(SOL_CARBON):.2f} Hz")
    print()
    print(f"  {'Domain':>7s} {'φ-scale':>10s} {'Freq (Hz)':>12s} {'Period':>12s}")
    print(f"  {'------':>7s} {'-------':>10s} {'---------':>12s} {'------':>12s}")
    for k in range(-3, 7):
        freq = float(SOL_CARBON) * PHI ** k
        period = 1.0 / freq
        if period > 1:
            p_str = f"{period:.3f} s"
        elif period > 0.001:
            p_str = f"{period * 1000:.3f} ms"
        elif period > 1e-6:
            p_str = f"{period * 1e6:.3f} μs"
        else:
            p_str = f"{period * 1e9:.3f} ns"
        print(f"  {k:>+7d} {'φ^' + str(k):>10s} {freq:>12.4f} {p_str:>12s}")

    print()
    print("  Amino acid temporal periods (relative to Sol-Carbon):")
    for aa in sorted(SELF_TENSION.keys(), key=lambda a: SELF_TENSION[a]):
        st = SELF_TENSION[aa]
        d = aa_domain(aa)
        # Effective period scales as φ^domain
        eff_period = (1.0 / float(SOL_CARBON)) * PHI ** (-d)
        print(f"    {aa}(ST={st:>3d}, dom={d:+d}): effective period ~ "
              f"{eff_period * 1000:.0f} ms")


def investigate_wind_down_mechanism():
    """Document the wind-down temporal phase mechanism."""
    print()
    print("=" * 70)
    print("  WIND-DOWN MECHANISM: NON-LOCAL OVERRIDES LOCAL")
    print("=" * 70)
    print()
    print("  Phase 1 (Wind-Up): Fast temporal gears")
    print("    - Local coupling (CF[0]=1, same domain)")
    print("    - 7-step iterator: Detect → Cohere → Tense → Lock → Adjust")
    print("    - Establishes helix + local sheet (hairpin + cross-strand)")
    print()
    print("  Phase 2 (Wind-Down): Slow temporal gears")
    print("    - Non-local topology via winding returns")
    print("    - Only hairpin-spanning returns (structural proof of sheet)")
    print("    - Uses frozen Phase 1 states (no cascading)")
    print("    - Extension toward nearest hairpin (directional)")
    print()
    print("  Physical basis:")
    print("    - Helix formation: LOCAL backbone H-bonds (i → i+4)")
    print("    - Sheet formation: NON-LOCAL inter-strand H-bonds")
    print("    - Sheet H-bonds are stronger but slower to form")
    print("    - The 'gear winding down' is the slow establishment of")
    print("      non-local contacts that override fast local structure")
    print()
    print("  Key result on ubiquitin:")
    print("    - Positions 39-44 (DQQRLI) have PERFECT local helix coupling")
    print("    - All pairs have CF[0]=1, curvature is regular, CF motif coherent")
    print("    - Phase 1 correctly identifies them as locally helix-like")
    print("    - But winding return 39↔72 spans hairpin 65")
    print("    - Phase 2 overrides: these positions are sheet in the 3D structure")
    print("    - The non-local topology (slower gear) wins over local coupling")


def main():
    domains = investigate_domain_structure()
    investigate_inter_domain_coupling()
    investigate_coupling_chains()
    investigate_temporal_frequencies()
    investigate_wind_down_mechanism()


if __name__ == "__main__":
    main()
