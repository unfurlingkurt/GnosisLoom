#!/usr/bin/env python3
"""GnosisLoom Universal Database - Query CLI.

Usage:
    python tools/db/query.py freq 10.0              # entities near 10 Hz
    python tools/db/query.py freq 10.0 --tol 0.5    # wider tolerance
    python tools/db/query.py entity mitochondria     # search by name
    python tools/db/query.py code NEU-01             # search by BioFreq code
    python tools/db/query.py harmonics mitochondria  # harmonic relatives
    python tools/db/query.py domain biology          # list domain entities
    python tools/db/query.py scale cellular          # list by scale
    python tools/db/query.py connections heart        # show relationships
    python tools/db/query.py loops                   # list feedback loops
    python tools/db/query.py diseases CFS            # disease frequency shifts
    python tools/db/query.py protocols               # list therapeutic protocols
    python tools/db/query.py stats                   # database statistics
    python tools/db/query.py sql "SELECT ..."        # raw SQL
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import get_db, safe_float


def fmt_freq(f):
    """Format a frequency for display."""
    if f is None:
        return "—"
    if abs(f) >= 1e6:
        return f"{f:.2e} Hz"
    if abs(f) >= 100:
        return f"{f:.1f} Hz"
    if abs(f) >= 1:
        return f"{f:.2f} Hz"
    return f"{f:.4g} Hz"


def fmt_row(row, fields):
    """Format a database row for display."""
    parts = []
    for f in fields:
        val = row[f] if f in row.keys() else None
        if f in ("frequency", "altered_frequency", "freq_min", "freq_max", "base_frequency"):
            parts.append(fmt_freq(val))
        elif val is None:
            parts.append("—")
        else:
            parts.append(str(val))
    return " | ".join(parts)


def print_table(rows, fields, headers=None):
    """Print rows as a formatted table."""
    if not rows:
        print("  (no results)")
        return
    headers = headers or fields
    widths = [len(h) for h in headers]
    str_rows = []
    for row in rows:
        vals = []
        for i, f in enumerate(fields):
            val = row[f] if f in row.keys() else None
            if f in ("frequency", "altered_frequency", "freq_min", "freq_max",
                     "base_frequency", "target_frequency"):
                s = fmt_freq(val)
            elif val is None:
                s = "—"
            else:
                s = str(val)[:60]
            vals.append(s)
            widths[i] = max(widths[i], len(s))
        str_rows.append(vals)

    # Header
    hdr = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(f"  {hdr}")
    print(f"  {'  '.join('─' * w for w in widths)}")
    for vals in str_rows:
        line = "  ".join(vals[i].ljust(widths[i]) for i in range(len(vals)))
        print(f"  {line}")
    print(f"\n  ({len(rows)} results)")


def cmd_freq(args):
    """Find entities near a frequency."""
    conn = get_db()
    target = float(args.target)
    tol = float(args.tol)
    low, high = target * (1 - tol), target * (1 + tol)
    rows = conn.execute("""
        SELECT name, code, domain, scale_id, frequency, stellar_anchor
        FROM entities
        WHERE frequency BETWEEN ? AND ?
        ORDER BY ABS(frequency - ?) ASC
        LIMIT 50
    """, (low, high, target)).fetchall()
    print(f"\n  Entities near {fmt_freq(target)} (±{tol*100:.0f}%):\n")
    print_table(rows, ["name", "code", "domain", "scale_id", "frequency", "stellar_anchor"],
                ["Name", "Code", "Domain", "Scale", "Frequency", "Stellar Anchor"])


def cmd_entity(args):
    """Search entities by name."""
    conn = get_db()
    pattern = f"%{args.name}%"
    rows = conn.execute("""
        SELECT name, code, domain, scale_id, frequency, stellar_anchor, element
        FROM entities
        WHERE name LIKE ? OR code LIKE ?
        ORDER BY name
        LIMIT 50
    """, (pattern, pattern)).fetchall()
    print(f"\n  Entities matching '{args.name}':\n")
    print_table(rows, ["name", "code", "domain", "scale_id", "frequency", "stellar_anchor"],
                ["Name", "Code", "Domain", "Scale", "Frequency", "Stellar Anchor"])


def cmd_code(args):
    """Search entities by BioFreq code."""
    conn = get_db()
    pattern = f"%{args.code}%"
    rows = conn.execute("""
        SELECT name, code, domain, scale_id, frequency, stellar_anchor
        FROM entities WHERE code LIKE ?
        ORDER BY code LIMIT 50
    """, (pattern,)).fetchall()
    print(f"\n  Entities with code matching '{args.code}':\n")
    print_table(rows, ["name", "code", "domain", "scale_id", "frequency", "stellar_anchor"],
                ["Name", "Code", "Domain", "Scale", "Frequency", "Stellar Anchor"])


def cmd_harmonics(args):
    """Find harmonic relatives of an entity."""
    conn = get_db()
    # First find the entity
    pattern = f"%{args.name}%"
    entity = conn.execute("""
        SELECT id, name, frequency FROM entities
        WHERE name LIKE ? OR code LIKE ?
        ORDER BY name LIMIT 1
    """, (pattern, pattern)).fetchone()
    if not entity:
        print(f"  No entity found matching '{args.name}'")
        return
    eid = entity["id"]
    freq = entity["frequency"]
    print(f"\n  Harmonics of {entity['name']} ({fmt_freq(freq)}):\n")

    # Direct relationships from relationships table
    rows = conn.execute("""
        SELECT e.name, e.frequency, r.ratio, r.description, e.domain, e.scale_id
        FROM relationships r
        JOIN entities e ON e.id = r.target_id
        WHERE r.source_id = ? AND r.rel_type = 'harmonic'
        ORDER BY r.ratio
        LIMIT 30
    """, (eid,)).fetchall()
    if rows:
        print_table(rows, ["name", "frequency", "ratio", "domain", "scale_id"],
                    ["Name", "Frequency", "Ratio", "Domain", "Scale"])
    else:
        # Fall back to frequency-based harmonic search
        print("  (no stored harmonics — searching by frequency ratio)")
        if freq and freq > 0:
            results = []
            for mult in [2, 3, 4, 5, 6, 7, 8]:
                hf = freq * mult
                near = conn.execute("""
                    SELECT name, frequency, domain, scale_id FROM entities
                    WHERE ABS(frequency - ?) / ? < 0.05 AND name != ?
                    LIMIT 5
                """, (hf, hf, entity["name"])).fetchall()
                for r in near:
                    results.append(dict(r) | {"ratio": mult})
            if results:
                for r in results:
                    print(f"  {r['name']:30s} {fmt_freq(r['frequency']):>14s}  {r['ratio']}:1  ({r['domain']})")
            else:
                print("  (no harmonic matches found)")


def cmd_domain(args):
    """List entities in a domain."""
    conn = get_db()
    rows = conn.execute("""
        SELECT name, code, scale_id, frequency, stellar_anchor
        FROM entities WHERE domain = ?
        ORDER BY frequency DESC
        LIMIT 80
    """, (args.domain,)).fetchall()
    print(f"\n  Entities in domain '{args.domain}':\n")
    print_table(rows, ["name", "code", "scale_id", "frequency", "stellar_anchor"],
                ["Name", "Code", "Scale", "Frequency", "Stellar Anchor"])


def cmd_scale(args):
    """List entities at a scale."""
    conn = get_db()
    rows = conn.execute("""
        SELECT name, code, domain, frequency, stellar_anchor
        FROM entities WHERE scale_id = ?
        ORDER BY frequency DESC
        LIMIT 80
    """, (args.scale,)).fetchall()
    print(f"\n  Entities at scale '{args.scale}':\n")
    print_table(rows, ["name", "code", "domain", "frequency", "stellar_anchor"],
                ["Name", "Code", "Domain", "Frequency", "Stellar Anchor"])


def cmd_connections(args):
    """Show all relationships for an entity."""
    conn = get_db()
    pattern = f"%{args.name}%"
    entity = conn.execute("""
        SELECT id, name, frequency, domain, scale_id FROM entities
        WHERE name LIKE ? OR code LIKE ?
        ORDER BY name LIMIT 1
    """, (pattern, pattern)).fetchone()
    if not entity:
        print(f"  No entity found matching '{args.name}'")
        return
    eid = entity["id"]
    print(f"\n  Connections for {entity['name']} ({fmt_freq(entity['frequency'])}, {entity['domain']}/{entity['scale_id']}):\n")

    # Outgoing
    out_rows = conn.execute("""
        SELECT e.name AS target, r.rel_type, r.strength, r.ratio, r.description, e.frequency
        FROM relationships r JOIN entities e ON e.id = r.target_id
        WHERE r.source_id = ?
        ORDER BY r.rel_type, e.name
        LIMIT 30
    """, (eid,)).fetchall()
    if out_rows:
        print(f"  → Outgoing ({len(out_rows)}):")
        print_table(out_rows, ["target", "rel_type", "ratio", "frequency", "description"],
                    ["Target", "Type", "Ratio", "Frequency", "Description"])

    # Incoming
    in_rows = conn.execute("""
        SELECT e.name AS source, r.rel_type, r.strength, r.ratio, r.description, e.frequency
        FROM relationships r JOIN entities e ON e.id = r.source_id
        WHERE r.target_id = ?
        ORDER BY r.rel_type, e.name
        LIMIT 30
    """, (eid,)).fetchall()
    if in_rows:
        print(f"\n  ← Incoming ({len(in_rows)}):")
        print_table(in_rows, ["source", "rel_type", "ratio", "frequency", "description"],
                    ["Source", "Type", "Ratio", "Frequency", "Description"])

    if not out_rows and not in_rows:
        print("  (no relationships found)")


def cmd_loops(args):
    """List feedback loops."""
    conn = get_db()
    rows = conn.execute("""
        SELECT code, name, loop_type, frequency, description
        FROM feedback_loops ORDER BY code LIMIT 80
    """).fetchall()
    print(f"\n  Feedback Loops:\n")
    print_table(rows, ["code", "loop_type", "description"],
                ["Code", "Type", "Description"])


def cmd_diseases(args):
    """Show disease frequency alterations."""
    conn = get_db()
    rows = conn.execute("""
        SELECT e.name, e.frequency AS normal_freq, d.disease, d.altered_frequency
        FROM disease_states d
        JOIN entities e ON e.id = d.entity_id
        WHERE d.disease LIKE ?
        ORDER BY e.name
    """, (f"%{args.disease}%",)).fetchall()
    print(f"\n  Disease states matching '{args.disease}':\n")
    if rows:
        print(f"  {'Entity':30s} {'Normal':>14s} {'Disease':15s} {'Altered':>14s} {'Shift':>10s}")
        print(f"  {'─'*30}  {'─'*14} {'─'*15} {'─'*14} {'─'*10}")
        for r in rows:
            nf = r["normal_freq"]
            af = r["altered_frequency"]
            shift = f"{((af - nf) / nf * 100):+.0f}%" if nf and af and nf != 0 else "—"
            print(f"  {r['name']:30s} {fmt_freq(nf):>14s} {r['disease']:15s} {fmt_freq(af):>14s} {shift:>10s}")
        print(f"\n  ({len(rows)} results)")
    else:
        print("  (no results)")


def cmd_protocols(args):
    """List therapeutic protocols."""
    conn = get_db()
    rows = conn.execute("""
        SELECT name, protocol_type, target_frequency, description
        FROM protocols ORDER BY protocol_type, name LIMIT 50
    """).fetchall()
    print(f"\n  Therapeutic Protocols:\n")
    print_table(rows, ["name", "protocol_type", "target_frequency", "description"],
                ["Name", "Type", "Target Freq", "Description"])


def cmd_stats(args):
    """Show database statistics."""
    conn = get_db()
    print("\n  === GnosisLoom Universal Database ===\n")

    for table in ["entities", "relationships", "harmonics", "feedback_loops",
                  "disease_states", "protocols", "genomic_profiles", "sources"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {cnt:>6,}")

    print(f"\n  --- Entities by Domain ---")
    for r in conn.execute("SELECT domain, COUNT(*) as c FROM entities GROUP BY domain ORDER BY c DESC"):
        print(f"  {r['domain']:25s} {r['c']:>6,}")

    print(f"\n  --- Entities by Scale ---")
    for r in conn.execute("SELECT scale_id, COUNT(*) as c FROM entities GROUP BY scale_id ORDER BY c DESC"):
        print(f"  {str(r['scale_id']):25s} {r['c']:>6,}")

    print(f"\n  --- Frequency Range ---")
    r = conn.execute("SELECT MIN(frequency) as mn, MAX(frequency) as mx, AVG(frequency) as avg FROM entities WHERE frequency IS NOT NULL").fetchone()
    print(f"  Min: {fmt_freq(r['mn'])}")
    print(f"  Max: {fmt_freq(r['mx'])}")
    print(f"  Avg: {fmt_freq(r['avg'])}")

    print(f"\n  --- Stellar Anchors ---")
    for r in conn.execute("SELECT stellar_anchor, COUNT(*) as c FROM entities WHERE stellar_anchor IS NOT NULL GROUP BY stellar_anchor ORDER BY c DESC"):
        print(f"  {str(r['stellar_anchor']):25s} {r['c']:>6,}")

    # DB file size
    from core import DEFAULT_DB_PATH
    if DEFAULT_DB_PATH.exists():
        size_mb = DEFAULT_DB_PATH.stat().st_size / (1024 * 1024)
        print(f"\n  Database: {DEFAULT_DB_PATH} ({size_mb:.1f} MB)")


def cmd_sql(args):
    """Execute raw SQL."""
    conn = get_db()
    try:
        rows = conn.execute(args.query).fetchall()
        if rows:
            fields = rows[0].keys()
            print_table(rows[:100], list(fields))
        else:
            print("  (no results)")
    except Exception as e:
        print(f"  SQL error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="GnosisLoom Universal Database Query Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s freq 10.0              Find entities near 10 Hz
  %(prog)s entity mitochondria    Search by name
  %(prog)s harmonics heart        Find harmonic relatives
  %(prog)s domain biology         List biology entities
  %(prog)s diseases CFS           Show CFS frequency shifts
  %(prog)s stats                  Database overview
  %(prog)s sql "SELECT ..."       Raw SQL query
        """,
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("freq", help="Find entities near a frequency")
    p.add_argument("target", type=float, help="Target frequency in Hz")
    p.add_argument("--tol", type=float, default=0.1, help="Tolerance (0.1 = ±10%%)")

    p = sub.add_parser("entity", help="Search entities by name")
    p.add_argument("name", help="Name pattern to search")

    p = sub.add_parser("code", help="Search entities by BioFreq code")
    p.add_argument("code", help="Code pattern to search")

    p = sub.add_parser("harmonics", help="Find harmonic relatives")
    p.add_argument("name", help="Entity name to find harmonics for")

    p = sub.add_parser("domain", help="List entities in a domain")
    p.add_argument("domain", help="Domain name (biology, chemistry, etc.)")

    p = sub.add_parser("scale", help="List entities at a scale")
    p.add_argument("scale", help="Scale (subatomic, atomic, molecular, cellular, tissue, organ, organism, planetary, stellar)")

    p = sub.add_parser("connections", help="Show entity relationships")
    p.add_argument("name", help="Entity name")

    p = sub.add_parser("loops", help="List feedback loops")

    p = sub.add_parser("diseases", help="Show disease frequency shifts")
    p.add_argument("disease", help="Disease name pattern")

    p = sub.add_parser("protocols", help="List therapeutic protocols")

    p = sub.add_parser("stats", help="Database statistics")

    p = sub.add_parser("sql", help="Execute raw SQL query")
    p.add_argument("query", help="SQL query string")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "freq": cmd_freq, "entity": cmd_entity, "code": cmd_code,
        "harmonics": cmd_harmonics, "domain": cmd_domain, "scale": cmd_scale,
        "connections": cmd_connections, "loops": cmd_loops,
        "diseases": cmd_diseases, "protocols": cmd_protocols,
        "stats": cmd_stats, "sql": cmd_sql,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
