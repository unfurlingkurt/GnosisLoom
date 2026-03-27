#!/usr/bin/env python3
"""GnosisLoom Universal Database - Ingest tool.

Add new data to the database.

Usage:
    python tools/db/ingest.py entity --name "new_thing" --freq 42.0 --domain biology --scale cellular
    python tools/db/ingest.py relationship --source mitochondria --target brain_gamma --type harmonic --ratio 4.0
    python tools/db/ingest.py file new_data.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import (
    get_db, transaction, entity_id, upsert_entity, upsert_relationship,
    log_source, classify_scale, safe_float
)


def cmd_entity(args):
    """Add a single entity."""
    conn = get_db()
    scale = args.scale or classify_scale(args.freq) or "organ"
    eid = entity_id(args.name, args.domain, scale)

    metadata = None
    if args.metadata:
        metadata = json.loads(args.metadata)

    with transaction(conn):
        upsert_entity(
            conn, eid, args.name, args.domain, scale,
            code=args.code,
            category=args.category,
            frequency=args.freq,
            stellar_anchor=args.stellar,
            element=args.element,
            formula=args.formula,
            description=args.description,
            source_file="manual_ingest",
            metadata=metadata,
        )
    print(f"  Added entity: {args.name} ({args.domain}/{scale}) @ {args.freq} Hz [id={eid}]")


def cmd_relationship(args):
    """Add a relationship between entities."""
    conn = get_db()
    # Find source and target by name
    src = conn.execute("SELECT id, name FROM entities WHERE name LIKE ? LIMIT 1",
                       (f"%{args.source}%",)).fetchone()
    tgt = conn.execute("SELECT id, name FROM entities WHERE name LIKE ? LIMIT 1",
                       (f"%{args.target}%",)).fetchone()
    if not src:
        print(f"  Source entity not found: {args.source}")
        return
    if not tgt:
        print(f"  Target entity not found: {args.target}")
        return

    with transaction(conn):
        rid = upsert_relationship(conn, src["id"], tgt["id"], args.type,
                                   strength=safe_float(args.strength),
                                   ratio=safe_float(args.ratio),
                                   description=args.description)
    print(f"  Added relationship: {src['name']} → {tgt['name']} ({args.type}, ratio={args.ratio})")


def cmd_file(args):
    """Bulk import from a JSON file."""
    filepath = Path(args.path)
    if not filepath.exists():
        print(f"  File not found: {filepath}")
        return

    data = json.loads(filepath.read_text())
    conn = get_db()
    count = 0

    with transaction(conn):
        if isinstance(data, dict):
            for name, info in data.items():
                if not isinstance(info, dict):
                    continue
                freq = safe_float(info.get("frequency") or info.get("normal_freq") or info.get("primary_frequency"))
                if freq is None:
                    continue
                domain = info.get("domain", args.domain or "biology")
                scale = info.get("scale", classify_scale(freq) or "organ")
                eid = entity_id(name, domain, scale)
                upsert_entity(
                    conn, eid, name, domain, scale,
                    code=info.get("code") or info.get("biofreq_code"),
                    category=info.get("category"),
                    frequency=freq,
                    stellar_anchor=info.get("stellar_anchor"),
                    element=info.get("element"),
                    formula=info.get("formula"),
                    description=info.get("description"),
                    source_file=filepath.name,
                    metadata={k: v for k, v in info.items()
                              if k not in ("frequency", "normal_freq", "primary_frequency",
                                           "domain", "scale", "code", "biofreq_code", "category",
                                           "stellar_anchor", "element", "formula", "description")},
                )
                count += 1
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = item.get("name", f"item_{count}")
                freq = safe_float(item.get("frequency") or item.get("normal_freq"))
                if freq is None:
                    continue
                domain = item.get("domain", args.domain or "biology")
                scale = item.get("scale", classify_scale(freq) or "organ")
                eid = entity_id(name, domain, scale)
                upsert_entity(conn, eid, name, domain, scale, frequency=freq,
                              source_file=filepath.name)
                count += 1

        log_source(conn, filepath.name, "json", count, f"Manual import from {filepath.name}")

    print(f"  Imported {count} entities from {filepath.name}")


def main():
    parser = argparse.ArgumentParser(description="GnosisLoom — Add data to the universal database")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("entity", help="Add a single entity")
    p.add_argument("--name", required=True, help="Entity name")
    p.add_argument("--freq", type=float, required=True, help="Frequency in Hz")
    p.add_argument("--domain", default="biology", help="Domain (default: biology)")
    p.add_argument("--scale", help="Scale (auto-detected if omitted)")
    p.add_argument("--code", help="BioFreq code")
    p.add_argument("--category", help="Category")
    p.add_argument("--stellar", help="Stellar anchor")
    p.add_argument("--element", help="Associated element")
    p.add_argument("--formula", help="Molecular formula")
    p.add_argument("--description", help="Description")
    p.add_argument("--metadata", help="JSON metadata string")

    p = sub.add_parser("relationship", help="Add a relationship")
    p.add_argument("--source", required=True, help="Source entity name")
    p.add_argument("--target", required=True, help="Target entity name")
    p.add_argument("--type", required=True, help="Relationship type")
    p.add_argument("--ratio", help="Harmonic ratio")
    p.add_argument("--strength", help="Strength 0.0-1.0")
    p.add_argument("--description", help="Description")

    p = sub.add_parser("file", help="Bulk import from JSON")
    p.add_argument("path", help="Path to JSON file")
    p.add_argument("--domain", help="Default domain for entries without one")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"entity": cmd_entity, "relationship": cmd_relationship, "file": cmd_file}[args.command](args)


if __name__ == "__main__":
    main()
