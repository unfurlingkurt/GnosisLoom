#!/usr/bin/env python3
"""GnosisLoom Universal Database - Core module.

Provides connection management, schema initialization, and common helpers.
"""

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

# Default database location: project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "gnosisloom.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DATA_DIR = PROJECT_ROOT / "data"


def get_db(db_path=None):
    """Open a connection to the GnosisLoom database."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def transaction(conn):
    """Context manager for atomic transactions."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db(db_path=None):
    """Create the database schema from schema.sql."""
    conn = get_db(db_path)
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.close()
    return db_path or DEFAULT_DB_PATH


def entity_id(name, domain, scale_id=""):
    """Generate a deterministic entity ID from name+domain+scale."""
    key = f"{name}|{domain}|{scale_id}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def rel_id(source_id, target_id, rel_type):
    """Generate a deterministic relationship ID."""
    key = f"{source_id}|{target_id}|{rel_type}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def now_iso():
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def load_json(filename):
    """Load a JSON file from the data directory."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path) as f:
        return json.load(f)


def load_csv_rows(filename):
    """Load a CSV file from the data directory as list of dicts."""
    import csv
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def upsert_entity(conn, eid, name, domain, scale_id=None, code=None,
                   category=None, frequency=None, freq_min=None, freq_max=None,
                   phase=0.0, stellar_anchor=None, element=None, formula=None,
                   description=None, source_file=None, metadata=None):
    """Insert or update an entity."""
    meta_json = json.dumps(metadata) if metadata else None
    conn.execute("""
        INSERT INTO entities (id, name, code, scale_id, domain, category,
                              frequency, freq_min, freq_max, phase,
                              stellar_anchor, element, formula,
                              description, source_file, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            code=COALESCE(excluded.code, code),
            category=COALESCE(excluded.category, category),
            frequency=COALESCE(excluded.frequency, frequency),
            freq_min=COALESCE(excluded.freq_min, freq_min),
            freq_max=COALESCE(excluded.freq_max, freq_max),
            stellar_anchor=COALESCE(excluded.stellar_anchor, stellar_anchor),
            element=COALESCE(excluded.element, element),
            formula=COALESCE(excluded.formula, formula),
            description=COALESCE(excluded.description, description),
            metadata=COALESCE(excluded.metadata, metadata)
    """, (eid, name, code, scale_id, domain, category,
          frequency, freq_min, freq_max, phase,
          stellar_anchor, element, formula,
          description, source_file, meta_json))
    return eid


def upsert_relationship(conn, source_id, target_id, rtype,
                         strength=None, ratio=None, description=None, metadata=None):
    """Insert or ignore a relationship."""
    rid = rel_id(source_id, target_id, rtype)
    meta_json = json.dumps(metadata) if metadata else None
    conn.execute("""
        INSERT OR IGNORE INTO relationships (id, source_id, target_id, rel_type,
                                             strength, ratio, description, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (rid, source_id, target_id, rtype, strength, ratio, description, meta_json))
    return rid


def log_source(conn, filename, file_type, record_count, description=""):
    """Record a source file in the provenance table."""
    sid = entity_id(filename, "source")
    conn.execute("""
        INSERT OR REPLACE INTO sources (id, filename, file_type, record_count, description, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sid, filename, file_type, record_count, description, now_iso()))


def classify_scale(frequency):
    """Infer scale from frequency value (Hz)."""
    if frequency is None:
        return None
    f = abs(frequency)
    if f >= 1e12:
        return "subatomic"
    if f >= 1e4:
        return "cellular"
    if f >= 100:
        return "tissue"
    if f >= 1:
        return "organ"
    if f >= 0.001:
        return "organism"
    return "planetary"


def safe_float(val):
    """Convert a value to float, returning None on failure."""
    if val is None or val == "" or val == "null":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
