#!/usr/bin/env python3
"""GnosisLoom Universal Database - Export tool.

Generate outputs from the universal database.

Usage:
    python tools/db/export.py json                    # full DB as JSON
    python tools/db/export.py json --domain biology   # filtered export
    python tools/db/export.py csv                     # full DB as CSV
    python tools/db/export.py csv --domain chemistry  # filtered CSV
    python tools/db/export.py report mitochondria     # markdown report for entity
    python tools/db/export.py summary                 # summary statistics as JSON
"""

import argparse
import csv
import json
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import get_db, DEFAULT_DB_PATH


def cmd_json(args):
    """Export database as JSON."""
    conn = get_db()
    where = ""
    params = ()
    if args.domain:
        where = "WHERE domain = ?"
        params = (args.domain,)

    entities = conn.execute(f"""
        SELECT id, name, code, scale_id, domain, category,
               frequency, freq_min, freq_max, phase,
               stellar_anchor, element, formula, description, metadata
        FROM entities {where}
        ORDER BY frequency
    """, params).fetchall()

    result = {}
    for e in entities:
        entry = {
            "name": e["name"],
            "code": e["code"],
            "scale": e["scale_id"],
            "domain": e["domain"],
            "category": e["category"],
            "frequency": e["frequency"],
            "freq_range": [e["freq_min"], e["freq_max"]],
            "stellar_anchor": e["stellar_anchor"],
            "element": e["element"],
            "formula": e["formula"],
            "description": e["description"],
        }
        if e["metadata"]:
            try:
                entry["metadata"] = json.loads(e["metadata"])
            except (json.JSONDecodeError, TypeError):
                pass

        # Disease states
        diseases = conn.execute(
            "SELECT disease, altered_frequency FROM disease_states WHERE entity_id = ?",
            (e["id"],)
        ).fetchall()
        if diseases:
            entry["disease_states"] = {d["disease"]: d["altered_frequency"] for d in diseases}

        # Harmonics
        harmonics = conn.execute(
            "SELECT harmonic_number, frequency FROM harmonics WHERE entity_id = ? ORDER BY harmonic_number",
            (e["id"],)
        ).fetchall()
        if harmonics:
            entry["harmonics"] = {h["harmonic_number"]: h["frequency"] for h in harmonics}

        result[e["id"]] = entry

    output = args.output or sys.stdout
    if isinstance(output, str):
        Path(output).write_text(json.dumps(result, indent=2))
        print(f"  Exported {len(result)} entities to {output}")
    else:
        json.dump(result, output, indent=2)
        print(f"\n  ({len(result)} entities)", file=sys.stderr)


def cmd_csv(args):
    """Export database as CSV."""
    conn = get_db()
    where = ""
    params = ()
    if args.domain:
        where = "WHERE domain = ?"
        params = (args.domain,)

    entities = conn.execute(f"""
        SELECT name, code, scale_id, domain, category,
               frequency, freq_min, freq_max,
               stellar_anchor, element, formula, description
        FROM entities {where}
        ORDER BY frequency
    """, params).fetchall()

    fields = ["name", "code", "scale_id", "domain", "category",
              "frequency", "freq_min", "freq_max",
              "stellar_anchor", "element", "formula", "description"]

    output = args.output
    if output:
        f = open(output, "w", newline="")
    else:
        f = sys.stdout

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for e in entities:
        writer.writerow({k: e[k] for k in fields})

    if output:
        f.close()
        print(f"  Exported {len(entities)} entities to {output}")
    else:
        print(f"\n  ({len(entities)} entities)", file=sys.stderr)


def cmd_report(args):
    """Generate a markdown report for an entity."""
    conn = get_db()
    entity = conn.execute("""
        SELECT * FROM entities WHERE name LIKE ? OR code LIKE ?
        ORDER BY name LIMIT 1
    """, (f"%{args.name}%", f"%{args.name}%")).fetchone()

    if not entity:
        print(f"  No entity found matching '{args.name}'")
        return

    eid = entity["id"]
    lines = []
    lines.append(f"# {entity['name']}")
    lines.append("")
    lines.append(f"**Domain**: {entity['domain']}  ")
    lines.append(f"**Scale**: {entity['scale_id']}  ")
    if entity["code"]:
        lines.append(f"**Code**: {entity['code']}  ")
    lines.append(f"**Frequency**: {entity['frequency']} Hz  ")
    if entity["freq_min"] and entity["freq_max"]:
        lines.append(f"**Range**: {entity['freq_min']}–{entity['freq_max']} Hz  ")
    if entity["stellar_anchor"]:
        lines.append(f"**Stellar Anchor**: {entity['stellar_anchor']}  ")
    if entity["element"]:
        lines.append(f"**Element**: {entity['element']}  ")
    if entity["formula"]:
        lines.append(f"**Formula**: {entity['formula']}  ")
    if entity["description"]:
        lines.append(f"\n{entity['description']}")

    # Disease states
    diseases = conn.execute(
        "SELECT disease, altered_frequency FROM disease_states WHERE entity_id = ?", (eid,)
    ).fetchall()
    if diseases:
        lines.append("\n## Disease States\n")
        lines.append("| Disease | Normal | Altered | Shift |")
        lines.append("|---------|--------|---------|-------|")
        nf = entity["frequency"]
        for d in diseases:
            af = d["altered_frequency"]
            shift = f"{((af - nf) / nf * 100):+.0f}%" if nf and af else "—"
            lines.append(f"| {d['disease']} | {nf} Hz | {af} Hz | {shift} |")

    # Relationships
    out_rels = conn.execute("""
        SELECT e.name, r.rel_type, r.ratio, e.frequency
        FROM relationships r JOIN entities e ON e.id = r.target_id
        WHERE r.source_id = ?
        ORDER BY r.ratio LIMIT 20
    """, (eid,)).fetchall()
    if out_rels:
        lines.append("\n## Harmonic Relationships\n")
        lines.append("| Target | Type | Ratio | Frequency |")
        lines.append("|--------|------|-------|-----------|")
        for r in out_rels:
            ratio = f"{r['ratio']:.1f}" if r["ratio"] else "—"
            lines.append(f"| {r['name']} | {r['rel_type']} | {ratio} | {r['frequency']} Hz |")

    # Harmonics
    harmonics = conn.execute(
        "SELECT harmonic_number, frequency FROM harmonics WHERE entity_id = ? ORDER BY harmonic_number",
        (eid,)
    ).fetchall()
    if harmonics:
        lines.append("\n## Harmonic Series\n")
        for h in harmonics:
            lines.append(f"- Harmonic {h['harmonic_number']}: {h['frequency']} Hz")

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report)
        print(f"  Report written to {args.output}")
    else:
        print(report)


def cmd_summary(args):
    """Export summary statistics as JSON."""
    conn = get_db()
    stats = {}

    stats["total_entities"] = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    stats["total_relationships"] = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    stats["total_feedback_loops"] = conn.execute("SELECT COUNT(*) FROM feedback_loops").fetchone()[0]
    stats["total_protocols"] = conn.execute("SELECT COUNT(*) FROM protocols").fetchone()[0]

    stats["by_domain"] = {}
    for r in conn.execute("SELECT domain, COUNT(*) as c FROM entities GROUP BY domain ORDER BY c DESC"):
        stats["by_domain"][r["domain"]] = r["c"]

    stats["by_scale"] = {}
    for r in conn.execute("SELECT scale_id, COUNT(*) as c FROM entities GROUP BY scale_id ORDER BY c DESC"):
        stats["by_scale"][r["scale_id"] or "unclassified"] = r["c"]

    freq_stats = conn.execute(
        "SELECT MIN(frequency) as mn, MAX(frequency) as mx, AVG(frequency) as avg FROM entities WHERE frequency IS NOT NULL"
    ).fetchone()
    stats["frequency_range"] = {"min": freq_stats["mn"], "max": freq_stats["mx"], "avg": freq_stats["avg"]}

    stats["stellar_anchors"] = {}
    for r in conn.execute("SELECT stellar_anchor, COUNT(*) as c FROM entities WHERE stellar_anchor IS NOT NULL GROUP BY stellar_anchor ORDER BY c DESC"):
        stats["stellar_anchors"][r["stellar_anchor"]] = r["c"]

    stats["sources"] = {}
    for r in conn.execute("SELECT filename, record_count FROM sources ORDER BY record_count DESC"):
        stats["sources"][r["filename"]] = r["record_count"]

    print(json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description="GnosisLoom — Export data from the universal database")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("json", help="Export as JSON")
    p.add_argument("--domain", help="Filter by domain")
    p.add_argument("--output", "-o", help="Output file (default: stdout)")

    p = sub.add_parser("csv", help="Export as CSV")
    p.add_argument("--domain", help="Filter by domain")
    p.add_argument("--output", "-o", help="Output file (default: stdout)")

    p = sub.add_parser("report", help="Markdown report for an entity")
    p.add_argument("name", help="Entity name")
    p.add_argument("--output", "-o", help="Output file (default: stdout)")

    sub.add_parser("summary", help="Summary statistics as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"json": cmd_json, "csv": cmd_csv, "report": cmd_report, "summary": cmd_summary}[args.command](args)


if __name__ == "__main__":
    main()
