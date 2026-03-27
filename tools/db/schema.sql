-- GnosisLoom Universal Database Schema
-- Consolidates all frequency data into a single queryable store

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- 1. SCALES: The measurement hierarchy (subatomic → stellar)
CREATE TABLE IF NOT EXISTS scales (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    freq_min REAL,
    freq_max REAL,
    order_index INTEGER NOT NULL
);

-- 2. ENTITIES: Everything with a frequency signature
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT,
    scale_id TEXT REFERENCES scales(id),
    domain TEXT NOT NULL,
    category TEXT,
    frequency REAL,
    freq_min REAL,
    freq_max REAL,
    phase REAL DEFAULT 0.0,
    stellar_anchor TEXT,
    element TEXT,
    formula TEXT,
    description TEXT,
    source_file TEXT,
    metadata JSON
);

-- 3. HARMONICS: Harmonic series for each entity
CREATE TABLE IF NOT EXISTS harmonics (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    harmonic_number INTEGER NOT NULL,
    frequency REAL NOT NULL,
    PRIMARY KEY (entity_id, harmonic_number)
);

-- 4. RELATIONSHIPS: Connections between entities
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES entities(id),
    target_id TEXT NOT NULL REFERENCES entities(id),
    rel_type TEXT NOT NULL,
    strength REAL,
    ratio REAL,
    description TEXT,
    metadata JSON
);

-- 5. FEEDBACK_LOOPS: Named feedback systems
CREATE TABLE IF NOT EXISTS feedback_loops (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT,
    loop_type TEXT,
    frequency REAL,
    description TEXT,
    metadata JSON
);

-- 6. LOOP_MEMBERS: Entities in feedback loops
CREATE TABLE IF NOT EXISTS loop_members (
    loop_id TEXT NOT NULL REFERENCES feedback_loops(id),
    entity_id TEXT NOT NULL REFERENCES entities(id),
    role TEXT,
    PRIMARY KEY (loop_id, entity_id)
);

-- 7. DISEASE_STATES: Disease-altered frequencies
CREATE TABLE IF NOT EXISTS disease_states (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    disease TEXT NOT NULL,
    altered_frequency REAL,
    description TEXT,
    metadata JSON,
    PRIMARY KEY (entity_id, disease)
);

-- 8. PROTOCOLS: Therapeutic/clinical protocols
CREATE TABLE IF NOT EXISTS protocols (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    protocol_type TEXT,
    target_frequency REAL,
    freq_min REAL,
    freq_max REAL,
    description TEXT,
    metadata JSON
);

-- 9. PROTOCOL_TARGETS: Protocol-entity links
CREATE TABLE IF NOT EXISTS protocol_targets (
    protocol_id TEXT NOT NULL REFERENCES protocols(id),
    entity_id TEXT NOT NULL REFERENCES entities(id),
    PRIMARY KEY (protocol_id, entity_id)
);

-- 10. GENOMIC_PROFILES: Organism-level genomic summaries
CREATE TABLE IF NOT EXISTS genomic_profiles (
    id TEXT PRIMARY KEY,
    organism TEXT NOT NULL,
    genome_id TEXT,
    genome_length INTEGER,
    gc_content REAL,
    base_frequency REAL,
    therapeutic_derivative REAL,
    metadata JSON
);

-- 11. SOURCES: Data provenance tracking
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT,
    record_count INTEGER,
    description TEXT,
    ingested_at TEXT NOT NULL
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_entities_frequency ON entities(frequency);
CREATE INDEX IF NOT EXISTS idx_entities_scale ON entities(scale_id);
CREATE INDEX IF NOT EXISTS idx_entities_domain ON entities(domain);
CREATE INDEX IF NOT EXISTS idx_entities_code ON entities(code);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_stellar ON entities(stellar_anchor);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(rel_type);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id);
CREATE INDEX IF NOT EXISTS idx_disease_states_disease ON disease_states(disease);
CREATE INDEX IF NOT EXISTS idx_harmonics_entity ON harmonics(entity_id);
CREATE INDEX IF NOT EXISTS idx_feedback_loops_code ON feedback_loops(code);
