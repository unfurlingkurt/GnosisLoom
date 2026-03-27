#!/usr/bin/env python3
"""GnosisLoom Universal Database - Explorer tool.

Interactive discovery of cross-domain frequency patterns.

Usage:
    python tools/db/explore.py cross-domain          # find entities at similar frequencies across domains
    python tools/db/explore.py anchor-clusters        # group entities by stellar anchor
    python tools/db/explore.py scale-bridge atomic stellar  # trace connections across scales
    python tools/db/explore.py frequency-spectrum     # visualize the full frequency distribution
    python tools/db/explore.py gaps                   # find frequency ranges with sparse data
    python tools/db/explore.py harmonic-chains        # find chains of harmonic relationships
    python tools/db/explore.py resonance-web 10.0     # find everything resonating near a frequency
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import get_db, safe_float


def fmt_freq(f):
    if f is None:
        return "—"
    if abs(f) >= 1e6:
        return f"{f:.2e} Hz"
    if abs(f) >= 100:
        return f"{f:.1f} Hz"
    if abs(f) >= 1:
        return f"{f:.2f} Hz"
    return f"{f:.4g} Hz"


def cmd_cross_domain(args):
    """Find entities at similar frequencies across different domains."""
    conn = get_db()
    print("\n  === Cross-Domain Frequency Matches ===\n")
    print("  Entities from different domains sharing near-identical frequencies:\n")

    tol = float(args.tol)
    rows = conn.execute("""
        SELECT a.name AS name_a, a.domain AS domain_a, a.frequency AS freq_a,
               b.name AS name_b, b.domain AS domain_b, b.frequency AS freq_b
        FROM entities a
        JOIN entities b ON a.id < b.id
            AND a.domain != b.domain
            AND a.frequency IS NOT NULL AND b.frequency IS NOT NULL
            AND a.frequency > 0 AND b.frequency > 0
            AND ABS(a.frequency - b.frequency) / a.frequency < ?
        ORDER BY a.frequency
        LIMIT 60
    """, (tol,)).fetchall()

    if rows:
        print(f"  {'Entity A':30s} {'Domain A':15s} {'Freq A':>12s}  ↔  {'Entity B':30s} {'Domain B':15s} {'Freq B':>12s}")
        print(f"  {'─'*30} {'─'*15} {'─'*12}     {'─'*30} {'─'*15} {'─'*12}")
        for r in rows:
            print(f"  {r['name_a']:30s} {r['domain_a']:15s} {fmt_freq(r['freq_a']):>12s}  ↔  {r['name_b']:30s} {r['domain_b']:15s} {fmt_freq(r['freq_b']):>12s}")
        print(f"\n  ({len(rows)} cross-domain matches within ±{tol*100:.0f}%)")
    else:
        print("  (no matches found — try increasing tolerance with --tol)")


def cmd_anchor_clusters(args):
    """Group entities by stellar anchor."""
    conn = get_db()
    print("\n  === Stellar Anchor Clusters ===\n")

    anchors = conn.execute("""
        SELECT stellar_anchor, COUNT(*) as c
        FROM entities
        WHERE stellar_anchor IS NOT NULL
        GROUP BY stellar_anchor
        ORDER BY c DESC
    """).fetchall()

    for anchor in anchors:
        name = anchor["stellar_anchor"]
        count = anchor["c"]
        print(f"  ★ {name} ({count} entities)")
        entities = conn.execute("""
            SELECT name, domain, scale_id, frequency
            FROM entities
            WHERE stellar_anchor = ?
            ORDER BY frequency
            LIMIT 15
        """, (name,)).fetchall()
        for e in entities:
            print(f"      {e['name']:35s} {e['domain']:15s} {e['scale_id'] or '—':12s} {fmt_freq(e['frequency']):>12s}")
        print()


def cmd_scale_bridge(args):
    """Trace entity connections from one scale to another."""
    conn = get_db()
    scale_a, scale_b = args.scale_from, args.scale_to
    print(f"\n  === Scale Bridge: {scale_a} → {scale_b} ===\n")

    # Find entities at each scale and look for relationships between them
    rows = conn.execute("""
        SELECT a.name AS from_name, a.frequency AS from_freq, a.scale_id AS from_scale,
               b.name AS to_name, b.frequency AS to_freq, b.scale_id AS to_scale,
               r.rel_type, r.ratio
        FROM relationships r
        JOIN entities a ON a.id = r.source_id
        JOIN entities b ON b.id = r.target_id
        WHERE a.scale_id = ? AND b.scale_id = ?
        ORDER BY a.frequency
        LIMIT 40
    """, (scale_a, scale_b)).fetchall()

    if rows:
        print(f"  {'From':25s} {'Freq':>12s} {'→':3s} {'To':25s} {'Freq':>12s} {'Type':12s} {'Ratio':>8s}")
        print(f"  {'─'*25} {'─'*12} {'─'*3} {'─'*25} {'─'*12} {'─'*12} {'─'*8}")
        for r in rows:
            ratio_str = f"{r['ratio']:.1f}" if r['ratio'] else "—"
            print(f"  {r['from_name']:25s} {fmt_freq(r['from_freq']):>12s}  →  {r['to_name']:25s} {fmt_freq(r['to_freq']):>12s} {r['rel_type']:12s} {ratio_str:>8s}")
        print(f"\n  ({len(rows)} connections)")
    else:
        print(f"  No direct connections found between {scale_a} and {scale_b}.")
        print("  Try: organ→tissue, organ→organ, tissue→organ")


def cmd_frequency_spectrum(args):
    """Show the distribution of entities across frequency ranges."""
    conn = get_db()
    print("\n  === Frequency Spectrum Distribution ===\n")

    # Define logarithmic bins
    bins = [
        ("< 0.001 Hz", "frequency > 0 AND frequency < 0.001"),
        ("0.001–0.01 Hz", "frequency >= 0.001 AND frequency < 0.01"),
        ("0.01–0.1 Hz", "frequency >= 0.01 AND frequency < 0.1"),
        ("0.1–1 Hz", "frequency >= 0.1 AND frequency < 1"),
        ("1–10 Hz", "frequency >= 1 AND frequency < 10"),
        ("10–100 Hz", "frequency >= 10 AND frequency < 100"),
        ("100–1000 Hz", "frequency >= 100 AND frequency < 1000"),
        ("1–100 kHz", "frequency >= 1000 AND frequency < 100000"),
        ("100 kHz–1 GHz", "frequency >= 100000 AND frequency < 1e9"),
        ("> 1 GHz", "frequency >= 1e9"),
    ]

    max_count = 0
    results = []
    for label, where in bins:
        row = conn.execute(f"SELECT COUNT(*) as c FROM entities WHERE {where}").fetchone()
        results.append((label, row["c"]))
        max_count = max(max_count, row["c"])

    bar_width = 50
    for label, count in results:
        bar_len = int(count / max_count * bar_width) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"  {label:20s} {bar:50s} {count:>5}")

    total = sum(c for _, c in results)
    print(f"\n  Total entities with frequency: {total}")


def cmd_gaps(args):
    """Find frequency ranges with sparse data coverage."""
    conn = get_db()
    print("\n  === Frequency Gap Analysis ===\n")
    print("  Frequency ranges with fewer than 5 entities:\n")

    # Check each octave
    freq = 0.001
    gaps = []
    while freq < 1e6:
        cnt = conn.execute(
            "SELECT COUNT(*) as c FROM entities WHERE frequency BETWEEN ? AND ?",
            (freq, freq * 2)
        ).fetchone()["c"]
        if cnt < 5:
            gaps.append((freq, freq * 2, cnt))
        freq *= 2

    if gaps:
        print(f"  {'Range':30s} {'Entities':>10s}")
        print(f"  {'─'*30} {'─'*10}")
        for low, high, cnt in gaps:
            print(f"  {fmt_freq(low):>12s} – {fmt_freq(high):>12s}      {cnt:>5}")
    else:
        print("  No gaps found — all octaves are well-populated!")


def cmd_harmonic_chains(args):
    """Find chains of harmonic relationships (A→B→C→...)."""
    conn = get_db()
    print("\n  === Harmonic Chains ===\n")
    print("  Longest chains of harmonic relationships:\n")

    # Find starting points (entities with many outgoing harmonics)
    starters = conn.execute("""
        SELECT source_id, COUNT(*) as c
        FROM relationships WHERE rel_type = 'harmonic'
        GROUP BY source_id
        ORDER BY c DESC LIMIT 10
    """).fetchall()

    for starter in starters:
        sid = starter["source_id"]
        chain = []
        visited = set()
        current = sid

        while current and current not in visited and len(chain) < 8:
            visited.add(current)
            ent = conn.execute("SELECT name, frequency FROM entities WHERE id = ?", (current,)).fetchone()
            if ent:
                chain.append((ent["name"], ent["frequency"]))
            # Follow to the next harmonic with ratio=2 (octave)
            nxt = conn.execute("""
                SELECT target_id FROM relationships
                WHERE source_id = ? AND rel_type = 'harmonic' AND ratio = 2.0
                LIMIT 1
            """, (current,)).fetchone()
            current = nxt["target_id"] if nxt else None

        if len(chain) >= 3:
            steps = " → ".join(f"{name} ({fmt_freq(f)})" for name, f in chain)
            print(f"  {steps}")

    print()


def cmd_resonance_web(args):
    """Find everything resonating near a frequency (harmonics, sub-harmonics, octaves)."""
    conn = get_db()
    target = float(args.frequency)
    print(f"\n  === Resonance Web around {fmt_freq(target)} ===\n")

    # Direct matches
    tol = 0.05
    direct = conn.execute("""
        SELECT name, domain, frequency, stellar_anchor FROM entities
        WHERE ABS(frequency - ?) / ? < ? AND frequency > 0
        ORDER BY ABS(frequency - ?)
        LIMIT 15
    """, (target, target, tol, target)).fetchall()

    if direct:
        print(f"  Direct matches (±{tol*100:.0f}%):")
        for r in direct:
            print(f"    {r['name']:35s} {r['domain']:15s} {fmt_freq(r['frequency']):>12s}  {r['stellar_anchor'] or ''}")

    # Harmonic matches
    print(f"\n  Harmonic relatives:")
    for mult in [2, 3, 4, 5, 6, 7, 8]:
        # Overtones
        hf = target * mult
        matches = conn.execute("""
            SELECT name, domain, frequency FROM entities
            WHERE ABS(frequency - ?) / ? < 0.05 AND frequency > 0
            LIMIT 5
        """, (hf, hf)).fetchall()
        for r in matches:
            print(f"    ×{mult} = {fmt_freq(hf):>12s}  {r['name']:35s} {r['domain']:15s} {fmt_freq(r['frequency']):>12s}")

    # Sub-harmonics
    print(f"\n  Sub-harmonic relatives:")
    for div in [2, 3, 4, 5, 6, 7, 8]:
        sf = target / div
        if sf > 0:
            matches = conn.execute("""
                SELECT name, domain, frequency FROM entities
                WHERE ABS(frequency - ?) / ? < 0.05 AND frequency > 0
                LIMIT 5
            """, (sf, sf)).fetchall()
            for r in matches:
                print(f"    ÷{div} = {fmt_freq(sf):>12s}  {r['name']:35s} {r['domain']:15s} {fmt_freq(r['frequency']):>12s}")


def main():
    parser = argparse.ArgumentParser(description="GnosisLoom Explorer — discover frequency patterns")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("cross-domain", help="Find cross-domain frequency matches")
    p.add_argument("--tol", default="0.02", help="Tolerance (default 0.02 = ±2%%)")

    sub.add_parser("anchor-clusters", help="Group entities by stellar anchor")

    p = sub.add_parser("scale-bridge", help="Trace connections between scales")
    p.add_argument("scale_from", help="Source scale")
    p.add_argument("scale_to", help="Target scale")

    sub.add_parser("frequency-spectrum", help="Frequency distribution histogram")
    sub.add_parser("gaps", help="Find sparse frequency ranges")
    sub.add_parser("harmonic-chains", help="Find chains of harmonic relationships")

    p = sub.add_parser("resonance-web", help="Find everything resonating near a frequency")
    p.add_argument("frequency", type=float, help="Center frequency in Hz")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "cross-domain": cmd_cross_domain,
        "anchor-clusters": cmd_anchor_clusters,
        "scale-bridge": cmd_scale_bridge,
        "frequency-spectrum": cmd_frequency_spectrum,
        "gaps": cmd_gaps,
        "harmonic-chains": cmd_harmonic_chains,
        "resonance-web": cmd_resonance_web,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
