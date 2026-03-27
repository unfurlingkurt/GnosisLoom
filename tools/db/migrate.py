#!/usr/bin/env python3
"""GnosisLoom Universal Database - Migration script.

Reads all data files from data/ and populates gnosisloom.db.
Run: python tools/db/migrate.py
"""

import json
import sys
import os
from pathlib import Path

# Ensure imports work when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import (
    get_db, init_db, transaction, entity_id, rel_id, now_iso,
    load_json, load_csv_rows, upsert_entity, upsert_relationship,
    log_source, classify_scale, safe_float, DEFAULT_DB_PATH, DATA_DIR
)


def seed_scales(conn):
    """Seed the measurement hierarchy."""
    scales = [
        ("subatomic", "Subatomic", 1e12, 1e18, 0),
        ("atomic", "Atomic", 0.1, 10.0, 1),
        ("molecular", "Molecular", 1.0, 1e4, 2),
        ("cellular", "Cellular", 0.01, 1e3, 3),
        ("tissue", "Tissue", 0.1, 200.0, 4),
        ("organ", "Organ", 0.001, 100.0, 5),
        ("organism", "Organism", 1e-7, 10.0, 6),
        ("planetary", "Planetary", 0.001, 1e4, 7),
        ("stellar", "Stellar", 1.0, 100.0, 8),
    ]
    for sid, label, fmin, fmax, idx in scales:
        conn.execute(
            "INSERT OR IGNORE INTO scales VALUES (?,?,?,?,?)",
            (sid, label, fmin, fmax, idx),
        )
    print(f"  Seeded {len(scales)} scales")


def migrate_elements(conn):
    """periodic_table_frequencies.json → entities at atomic scale."""
    data = load_json("periodic_table_frequencies.json")
    pt = data.get("periodic_table_frequencies", data)
    count = 0
    # Walk nested structure: sol_system_primary_anchors, period_X_elements, etc.
    for group_key, group_val in pt.items():
        if group_key == "metadata":
            continue
        if isinstance(group_val, dict):
            for elem_name, elem_data in group_val.items():
                if not isinstance(elem_data, dict) or "frequency" not in elem_data:
                    continue
                freq = safe_float(elem_data["frequency"])
                eid = entity_id(elem_name, "chemistry", "atomic")
                upsert_entity(
                    conn, eid, elem_name, "chemistry", "atomic",
                    code=elem_data.get("element_code"),
                    category="element",
                    frequency=freq,
                    stellar_anchor=elem_data.get("stellar_anchor"),
                    element=elem_name,
                    description=elem_data.get("biological_role"),
                    source_file="periodic_table_frequencies.json",
                    metadata={
                        k: v for k, v in elem_data.items()
                        if k not in ("frequency", "stellar_anchor", "element_code", "biological_role")
                    },
                )
                # Add harmonic series
                for i, h in enumerate(elem_data.get("harmonic_series", []), 1):
                    conn.execute(
                        "INSERT OR IGNORE INTO harmonics VALUES (?,?,?)",
                        (eid, i, safe_float(h)),
                    )
                count += 1
    log_source(conn, "periodic_table_frequencies.json", "json", count, "Elemental frequencies")
    print(f"  Elements: {count} entities")


def migrate_stellar_anchors(conn):
    """comprehensive_stellar_anchors.json → entities at stellar/organ scale."""
    data = load_json("comprehensive_stellar_anchors.json")
    count = 0
    stellar_names = {"Sol", "Arcturus", "Sirius", "Alpha_Centauri", "Schumann", "Vega", "Betelgeuse", "Rigel", "Polaris"}
    for name, info in data.items():
        if not isinstance(info, dict) or "frequency" not in info:
            continue
        freq = safe_float(info["frequency"])
        is_stellar = name in stellar_names
        scale = "stellar" if is_stellar else "organ"
        domain = "astronomy" if is_stellar else "biology"
        eid = entity_id(name, domain, scale)
        upsert_entity(
            conn, eid, name, domain, scale,
            category="stellar_anchor" if is_stellar else "biological_system",
            frequency=freq,
            element=info.get("element"),
            description=f"Systems: {', '.join(info.get('systems', []))}",
            source_file="comprehensive_stellar_anchors.json",
            metadata={"color": info.get("color"), "systems": info.get("systems", [])},
        )
        count += 1
    log_source(conn, "comprehensive_stellar_anchors.json", "json", count, "Stellar anchors and biological systems")
    print(f"  Stellar anchors: {count} entities")


def migrate_amino_acids(conn):
    """amino_acid_frequencies.csv → entities at molecular scale."""
    rows = load_csv_rows("amino_acid_frequencies.csv")
    count = 0
    for row in rows:
        name = row.get("amino_acid_code", "").strip()
        freq = safe_float(row.get("frequency_hz"))
        if not name or freq is None:
            continue
        eid = entity_id(name, "chemistry", "molecular")
        upsert_entity(
            conn, eid, name, "chemistry", "molecular",
            code=f"AA-{name}",
            category="amino_acid",
            frequency=freq,
            formula=row.get("molecular_formula"),
            source_file="amino_acid_frequencies.csv",
            metadata={
                k: v for k, v in row.items()
                if k not in ("amino_acid_code", "frequency_hz", "molecular_formula") and v
            },
        )
        count += 1
    log_source(conn, "amino_acid_frequencies.csv", "csv", count, "Amino acid frequencies")
    print(f"  Amino acids: {count} entities")


def migrate_molecular_chemistry(conn):
    """molecular_chemistry.csv → entities at molecular scale."""
    rows = load_csv_rows("molecular_chemistry.csv")
    count = 0
    for row in rows:
        rid = row.get("record_id", "").strip()
        freq = safe_float(row.get("frequency"))
        if not rid or freq is None:
            continue
        # Extract clean name from record_id
        name = rid.replace("molecular_chemistry_resonance_", "").replace("amino_acid_frequencies_", "")
        eid = entity_id(name, "chemistry", "molecular")
        upsert_entity(
            conn, eid, name, "chemistry", "molecular",
            category="molecule",
            frequency=freq,
            formula=row.get("formula"),
            source_file="molecular_chemistry.csv",
            metadata={
                k: v for k, v in row.items()
                if k not in ("record_id", "frequency", "formula") and v
            },
        )
        count += 1
    log_source(conn, "molecular_chemistry.csv", "csv", count, "Molecular chemistry")
    print(f"  Molecules: {count} entities")


def migrate_enzymes(conn):
    """enzyme_active_sites.csv → entities at molecular scale."""
    rows = load_csv_rows("enzyme_active_sites.csv")
    count = 0
    for row in rows:
        name = row.get("enzyme_name", "").strip()
        freq = safe_float(row.get("active_site_frequency_hz"))
        if not name or freq is None:
            continue
        eid = entity_id(name, "chemistry", "molecular")
        upsert_entity(
            conn, eid, name, "chemistry", "molecular",
            code=row.get("ec_number"),
            category="enzyme",
            frequency=freq,
            source_file="enzyme_active_sites.csv",
            metadata={
                k: v for k, v in row.items()
                if k not in ("enzyme_name", "active_site_frequency_hz", "ec_number") and v
            },
        )
        count += 1
    log_source(conn, "enzyme_active_sites.csv", "csv", count, "Enzyme active sites")
    print(f"  Enzymes: {count} entities")


def migrate_dna_structural(conn):
    """dna_structural_frequencies.json → entities at molecular scale."""
    data = load_json("dna_structural_frequencies.json")
    arch = data.get("dna_frequency_architecture", data)
    bases = arch.get("nucleotide_base_frequencies", {})
    count = 0
    for name, info in bases.items():
        if not isinstance(info, dict) or "frequency" not in info:
            continue
        freq = safe_float(info["frequency"])
        eid = entity_id(name, "genomics", "molecular")
        upsert_entity(
            conn, eid, name, "genomics", "molecular",
            code=info.get("base_code"),
            category="nucleotide",
            frequency=freq,
            formula=info.get("formula"),
            description=info.get("information_code"),
            source_file="dna_structural_frequencies.json",
            metadata={
                k: v for k, v in info.items()
                if k not in ("frequency", "base_code", "formula", "information_code")
            },
        )
        count += 1
    # Also ingest base_pair_locking if present
    pairs = arch.get("base_pair_locking", {})
    for name, info in pairs.items():
        if not isinstance(info, dict):
            continue
        freq = safe_float(info.get("combined_frequency"))
        if freq is None:
            continue
        eid = entity_id(name, "genomics", "molecular")
        upsert_entity(
            conn, eid, name, "genomics", "molecular",
            category="base_pair",
            frequency=freq,
            source_file="dna_structural_frequencies.json",
            metadata=info,
        )
        count += 1
    log_source(conn, "dna_structural_frequencies.json", "json", count, "DNA structural frequencies")
    print(f"  DNA structures: {count} entities")


def migrate_comprehensive_frequencies(conn):
    """comprehensive_frequencies.json → entities + disease_states."""
    data = load_json("comprehensive_frequencies.json")
    count = 0
    disease_count = 0
    for name, info in data.items():
        if not isinstance(info, dict) or "normal_freq" not in info:
            continue
        freq = safe_float(info["normal_freq"])
        frange = info.get("range", [])
        fmin = safe_float(frange[0]) if len(frange) > 0 else None
        fmax = safe_float(frange[1]) if len(frange) > 1 else None
        scale = classify_scale(freq)
        eid = entity_id(name, "biology", scale or "organ")
        upsert_entity(
            conn, eid, name, "biology", scale or "organ",
            category="biological_system",
            frequency=freq,
            freq_min=fmin,
            freq_max=fmax,
            phase=safe_float(info.get("phase", 0.0)),
            stellar_anchor=info.get("stellar_anchor"),
            element=info.get("element"),
            source_file="comprehensive_frequencies.json",
        )
        # Harmonics
        for i, h in enumerate(info.get("harmonics", []), 1):
            hf = safe_float(h)
            if hf is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO harmonics VALUES (?,?,?)",
                    (eid, i, hf),
                )
        # Disease states
        ds = info.get("disease_states", {})
        if isinstance(ds, dict):
            for disease, altered in ds.items():
                af = safe_float(altered)
                if af is not None:
                    conn.execute(
                        "INSERT OR IGNORE INTO disease_states (entity_id, disease, altered_frequency) VALUES (?,?,?)",
                        (eid, disease, af),
                    )
                    disease_count += 1
        count += 1
    log_source(conn, "comprehensive_frequencies.json", "json", count, "Comprehensive biological frequencies")
    print(f"  Biological systems: {count} entities, {disease_count} disease states")


def migrate_feedback_loops(conn):
    """feedback_loops.json → feedback_loops table."""
    data = load_json("feedback_loops.json")
    count = 0
    for code, desc in data.items():
        if not isinstance(desc, str):
            continue
        # Try to extract frequency from description
        freq = None
        loop_type = None
        if desc in ("amplifying", "stabilizing", "rhythmic", "multi-level"):
            loop_type = desc
        lid = entity_id(code, "feedback_loop")
        conn.execute(
            "INSERT OR IGNORE INTO feedback_loops (id, code, name, loop_type, frequency, description) VALUES (?,?,?,?,?,?)",
            (lid, code, code, loop_type, freq, desc),
        )
        count += 1
    log_source(conn, "feedback_loops.json", "json", count, "Feedback loops")
    print(f"  Feedback loops: {count}")


def migrate_harmonic_relationships(conn):
    """harmonic_relationships.json → relationships table."""
    data = load_json("harmonic_relationships.json")
    count = 0
    for fundamental_name, harmonics_list in data.items():
        if not isinstance(harmonics_list, list):
            continue
        for h in harmonics_list:
            if not isinstance(h, dict):
                continue
            harmonic_name = h.get("harmonic", "")
            ratio = safe_float(h.get("ratio"))
            fund_freq = safe_float(h.get("fundamental_freq"))
            harm_freq = safe_float(h.get("harmonic_freq"))
            if not harmonic_name or ratio is None:
                continue
            # Find or create entity IDs (use biology/organ as default since these are bio systems)
            src_scale = classify_scale(fund_freq) or "organ"
            tgt_scale = classify_scale(harm_freq) or "organ"
            src_id = entity_id(fundamental_name, "biology", src_scale)
            tgt_id = entity_id(harmonic_name, "biology", tgt_scale)
            # Ensure both entities exist (create stubs if not)
            upsert_entity(conn, src_id, fundamental_name, "biology", src_scale,
                          frequency=fund_freq, source_file="harmonic_relationships.json")
            upsert_entity(conn, tgt_id, harmonic_name, "biology", tgt_scale,
                          frequency=harm_freq, source_file="harmonic_relationships.json")
            upsert_relationship(conn, src_id, tgt_id, "harmonic",
                                ratio=ratio, description=f"{ratio}:1 harmonic")
            count += 1
    log_source(conn, "harmonic_relationships.json", "json", count, "Harmonic relationships")
    print(f"  Harmonic relationships: {count}")


def migrate_environmental(conn):
    """environmental_frequencies.json → entities at planetary scale."""
    data = load_json("environmental_frequencies.json")
    freqs = data.get("environmental_frequencies", {})
    count = 0
    for code, info in freqs.items():
        if not isinstance(info, dict) or "frequency" not in info:
            continue
        freq = safe_float(info["frequency"])
        name = info.get("name", code)
        eid = entity_id(name, "geophysics", "planetary")
        stellar_coord = info.get("stellar_coordination", {})
        upsert_entity(
            conn, eid, name, "geophysics", "planetary",
            code=info.get("cell_type_code", code),
            category=info.get("shell", "environmental"),
            frequency=freq,
            stellar_anchor=stellar_coord.get("anchor") if isinstance(stellar_coord, dict) else None,
            description=info.get("generation_mechanism"),
            source_file="environmental_frequencies.json",
            metadata={k: v for k, v in info.items()
                      if k not in ("name", "frequency", "cell_type_code", "shell", "generation_mechanism", "stellar_coordination")},
        )
        count += 1
    log_source(conn, "environmental_frequencies.json", "json", count, "Environmental frequencies")
    print(f"  Environmental: {count} entities")


def migrate_plants(conn):
    """plant_kingdom_frequencies.json → entities."""
    data = load_json("plant_kingdom_frequencies.json")
    count = 0
    for section_key, section in data.items():
        if not isinstance(section, dict) or section_key == "database_info":
            continue
        for code, info in section.items():
            if not isinstance(info, dict) or "frequency" not in info:
                continue
            freq = safe_float(info["frequency"])
            name = info.get("function", code)
            eid = entity_id(code, "biology", "organism")
            upsert_entity(
                conn, eid, name, "biology", "organism",
                code=info.get("biofreq_code", code),
                category="plant",
                frequency=freq,
                stellar_anchor=info.get("stellar_anchor"),
                description=info.get("biological_process"),
                source_file="plant_kingdom_frequencies.json",
                metadata={k: v for k, v in info.items()
                          if k not in ("frequency", "function", "biofreq_code", "stellar_anchor", "biological_process")},
            )
            count += 1
    log_source(conn, "plant_kingdom_frequencies.json", "json", count, "Plant kingdom frequencies")
    print(f"  Plants: {count} entities")


def migrate_medicinal_plants(conn):
    """medicinal_plant_frequencies.json → entities."""
    try:
        data = load_json("medicinal_plant_frequencies.json")
    except FileNotFoundError:
        print("  Medicinal plants: skipped (file not found)")
        return
    count = 0
    for section_key, section in data.items():
        if not isinstance(section, dict) or section_key in ("metadata", "database_info"):
            continue
        for name, info in section.items():
            if not isinstance(info, dict):
                continue
            freq = safe_float(info.get("frequency") or info.get("primary_frequency"))
            if freq is None:
                continue
            eid = entity_id(name, "medicine", "organism")
            upsert_entity(
                conn, eid, name, "medicine", "organism",
                code=info.get("biofreq_code"),
                category="medicinal_plant",
                frequency=freq,
                stellar_anchor=info.get("stellar_anchor"),
                description=info.get("function") or info.get("therapeutic_use"),
                source_file="medicinal_plant_frequencies.json",
                metadata={k: v for k, v in info.items()
                          if k not in ("frequency", "primary_frequency", "biofreq_code", "stellar_anchor", "function", "therapeutic_use")},
            )
            count += 1
    log_source(conn, "medicinal_plant_frequencies.json", "json", count, "Medicinal plant frequencies")
    print(f"  Medicinal plants: {count} entities")


def migrate_autoimmune(conn):
    """autoimmune_frequency_confusion_matrix.json → entities + relationships (mimicry)."""
    data = load_json("autoimmune_frequency_confusion_matrix.json")
    matrix = data.get("autoimmune_frequency_confusion_matrix", data)
    pairs = matrix.get("pathogen_mimicry_frequencies", {})
    count = 0
    for pathogen_name, info in pairs.items():
        if not isinstance(info, dict):
            continue
        p_freq = safe_float(info.get("pathogen_frequency"))
        h_freq = safe_float(info.get("host_frequency"))
        target_tissue = info.get("target_tissue", "unknown")
        if p_freq is None:
            continue
        # Pathogen entity
        p_id = entity_id(pathogen_name, "biology", "cellular")
        upsert_entity(
            conn, p_id, pathogen_name, "biology", "cellular",
            code=info.get("pathogen_code"),
            category="pathogen",
            frequency=p_freq,
            source_file="autoimmune_frequency_confusion_matrix.json",
            metadata={"clinical_manifestation": info.get("clinical_manifestation"),
                       "symptoms": info.get("symptoms", [])},
        )
        # Host tissue entity
        t_id = entity_id(target_tissue, "biology", "tissue")
        upsert_entity(
            conn, t_id, target_tissue, "biology", "tissue",
            category="host_tissue",
            frequency=h_freq,
            source_file="autoimmune_frequency_confusion_matrix.json",
        )
        # Mimicry relationship
        upsert_relationship(conn, p_id, t_id, "mimicry",
                            strength=safe_float(info.get("overlap_percentage", 0)) / 100.0 if info.get("overlap_percentage") else None,
                            description=info.get("clinical_manifestation"),
                            metadata={"attack_pattern": info.get("attack_pattern"),
                                       "molecular_basis": info.get("molecular_basis")})
        count += 1
    log_source(conn, "autoimmune_frequency_confusion_matrix.json", "json", count, "Autoimmune mimicry pairs")
    print(f"  Autoimmune: {count} pathogen-host pairs")


def migrate_protocols(conn):
    """biofield_coherence_protocols.json → protocols table."""
    data = load_json("biofield_coherence_protocols.json")
    protocols_data = data.get("biofield_coherence_protocols", data)
    count = 0
    for category, protocol_list in protocols_data.items():
        if not isinstance(protocol_list, list):
            continue
        for p in protocol_list:
            if not isinstance(p, dict):
                continue
            pid = p.get("protocol_id") or entity_id(p.get("name", ""), "protocol")
            freq = safe_float(p.get("frequency"))
            conn.execute(
                "INSERT OR IGNORE INTO protocols (id, name, protocol_type, target_frequency, description, metadata) VALUES (?,?,?,?,?,?)",
                (pid, p.get("name", pid), category,
                 freq, p.get("coherence_effect"),
                 json.dumps({k: v for k, v in p.items()
                             if k not in ("protocol_id", "name", "frequency", "coherence_effect")})),
            )
            count += 1
    log_source(conn, "biofield_coherence_protocols.json", "json", count, "Biofield coherence protocols")
    print(f"  Protocols (biofield): {count}")


def migrate_delivery_systems(conn):
    """frequency_delivery_systems.json → protocols table."""
    data = load_json("frequency_delivery_systems.json")
    systems = data.get("frequency_delivery_systems", data)
    count = 0
    for sys_name, sys_data in systems.items():
        if sys_name == "metadata" or not isinstance(sys_data, dict):
            continue
        for device_name, device_data in sys_data.items():
            if not isinstance(device_data, dict):
                continue
            # Extract therapeutic protocols within each device
            tp = device_data.get("therapeutic_protocols", {})
            if isinstance(tp, dict):
                for proto_name, proto_data in tp.items():
                    if not isinstance(proto_data, dict):
                        continue
                    pid = entity_id(f"{device_name}_{proto_name}", "protocol")
                    freq_str = proto_data.get("target_frequency", "")
                    conn.execute(
                        "INSERT OR IGNORE INTO protocols (id, name, protocol_type, description, metadata) VALUES (?,?,?,?,?)",
                        (pid, f"{device_name}: {proto_name}", "delivery",
                         f"Via {sys_name}",
                         json.dumps(proto_data)),
                    )
                    count += 1
            else:
                pid = entity_id(device_name, "protocol")
                conn.execute(
                    "INSERT OR IGNORE INTO protocols (id, name, protocol_type, description, metadata) VALUES (?,?,?,?,?)",
                    (pid, device_name, "delivery", f"Via {sys_name}", json.dumps(device_data)),
                )
                count += 1
    log_source(conn, "frequency_delivery_systems.json", "json", count, "Frequency delivery systems")
    print(f"  Protocols (delivery): {count}")


def migrate_genomic_summaries(conn):
    """genomic_summary_*.json → genomic_profiles table."""
    count = 0
    for f in DATA_DIR.glob("genomic_summary_*.json"):
        data = json.loads(f.read_text())
        organism = data.get("organism", f.stem.replace("genomic_summary_", ""))
        gi = data.get("genome_info", {})
        nf = data.get("nucleotide_frequencies", {})
        gid = entity_id(organism, "genomic_profile")
        conn.execute(
            "INSERT OR IGNORE INTO genomic_profiles (id, organism, genome_id, genome_length, gc_content, base_frequency, therapeutic_derivative, metadata) VALUES (?,?,?,?,?,?,?,?)",
            (gid, organism,
             gi.get("accession"),
             gi.get("length_bp"),
             safe_float(nf.get("gc_content")),
             safe_float(nf.get("genome_base_frequency_hz")),
             safe_float(data.get("therapeutic_derivative")),
             json.dumps({k: v for k, v in data.items()
                         if k not in ("organism", "genome_info", "nucleotide_frequencies")})),
        )
        count += 1
    log_source(conn, "genomic_summary_*.json", "json", count, "Genomic profiles (summaries)")
    print(f"  Genomic profiles: {count}")


def migrate_materials(conn):
    """materials_frequencies.json → entities."""
    data = load_json("materials_frequencies.json")
    freqs = data.get("materials_frequencies", {})
    count = 0
    for code, info in freqs.items():
        if not isinstance(info, dict):
            continue
        freq = safe_float(info.get("unit_cell_frequency") or info.get("frequency"))
        if freq is None:
            continue
        name = info.get("material", code)
        eid = entity_id(name, "materials_science", "molecular")
        upsert_entity(
            conn, eid, name, "materials_science", "molecular",
            code=code,
            category="material",
            frequency=freq,
            element=info.get("base_element"),
            source_file="materials_frequencies.json",
            metadata={k: v for k, v in info.items()
                      if k not in ("material", "unit_cell_frequency", "frequency", "base_element")},
        )
        count += 1
    log_source(conn, "materials_frequencies.json", "json", count, "Materials frequencies")
    print(f"  Materials: {count} entities")


def migrate_generic_json(conn, filename, domain, scale, category,
                          name_key=None, freq_key="frequency", code_key=None,
                          data_path=None, description_key=None):
    """Generic migrator for JSON files with name→{frequency, ...} structure."""
    try:
        data = load_json(filename)
    except FileNotFoundError:
        print(f"  {filename}: skipped (not found)")
        return 0
    # Navigate to nested data if data_path specified
    if data_path:
        for key in data_path:
            if isinstance(data, dict):
                data = data.get(key, {})
    count = 0
    if isinstance(data, dict):
        for name, info in data.items():
            if not isinstance(info, dict) or name in ("metadata", "database_info"):
                continue
            freq = safe_float(info.get(freq_key))
            if freq is None:
                continue
            display_name = info.get(name_key, name) if name_key else name
            eid = entity_id(display_name, domain, scale)
            upsert_entity(
                conn, eid, display_name, domain, scale,
                code=info.get(code_key) if code_key else None,
                category=category,
                frequency=freq,
                stellar_anchor=info.get("stellar_anchor"),
                element=info.get("element"),
                description=info.get(description_key) if description_key else None,
                source_file=filename,
                metadata={k: v for k, v in info.items()
                          if k not in (freq_key, name_key, code_key, "stellar_anchor", "element", description_key) and k != "metadata"},
            )
            count += 1
    log_source(conn, filename, "json", count, f"{category} frequencies")
    print(f"  {filename}: {count} entities")
    return count


def migrate_remaining_json_files(conn):
    """Catch-all for JSON data files not handled by specific migrators."""
    handled = {
        "periodic_table_frequencies.json", "comprehensive_stellar_anchors.json",
        "comprehensive_frequencies.json", "feedback_loops.json",
        "harmonic_relationships.json", "environmental_frequencies.json",
        "plant_kingdom_frequencies.json", "medicinal_plant_frequencies.json",
        "autoimmune_frequency_confusion_matrix.json",
        "biofield_coherence_protocols.json", "frequency_delivery_systems.json",
        "materials_frequencies.json", "dna_structural_frequencies.json",
        "database_integration_bridges.json", "dataset_summary.json",
        "frequency_taxonomy_index.json", "comparative_frequency_analysis_v1.json",
        "yeast_analysis_plan.json", "gnosisloom_fhir_bundle.json",
        "molecular_chemistry_summary.json", "primordial_chemistry_summary.json",
    }
    # Skip large genomic files (raw data) and summaries already handled
    skip_prefixes = ("genomic_frequencies_", "genomic_summary_", "alphagenome_gene_",
                     "cross_kingdom_coupling_", "knowledge_graph_data_", "integration_report",
                     "frequency_compression_investigation", "observer_drift_analysis")

    count = 0
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name in handled:
            continue
        if any(f.name.startswith(p) for p in skip_prefixes):
            continue
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  {f.name}: skipped (parse error)")
            continue

        file_count = _ingest_nested_frequencies(conn, data, f.name)
        if file_count > 0:
            log_source(conn, f.name, "json", file_count, "Auto-ingested frequencies")
            print(f"  {f.name}: {file_count} entities (auto)")
        count += file_count
    return count


def _ingest_nested_frequencies(conn, data, source_file, prefix="", depth=0):
    """Recursively find frequency entries in nested JSON structures."""
    if depth > 4 or not isinstance(data, dict):
        return 0
    count = 0
    for key, val in data.items():
        if key in ("metadata", "database_info"):
            continue
        if isinstance(val, dict):
            # Check if this dict has a frequency field
            freq = safe_float(val.get("frequency") or val.get("primary_frequency") or val.get("normal_freq"))
            if freq is not None:
                name = val.get("name", key)
                domain = "biology"
                scale = classify_scale(freq) or "organ"
                eid = entity_id(f"{source_file}:{name}", domain, scale)
                upsert_entity(
                    conn, eid, name, domain, scale,
                    code=val.get("biofreq_code") or val.get("code") or val.get("cell_type_code"),
                    category=val.get("category", prefix or "auto"),
                    frequency=freq,
                    stellar_anchor=val.get("stellar_anchor"),
                    element=val.get("element"),
                    description=val.get("description") or val.get("function"),
                    source_file=source_file,
                )
                count += 1
            else:
                # Recurse deeper
                count += _ingest_nested_frequencies(conn, val, source_file, key, depth + 1)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    count += _ingest_nested_frequencies(conn, {key: item}, source_file, prefix, depth + 1)
    return count


def migrate_all():
    """Run the full migration pipeline."""
    print("=" * 60)
    print("GnosisLoom Universal Database Migration")
    print("=" * 60)

    # Remove existing DB for clean migration
    if DEFAULT_DB_PATH.exists():
        DEFAULT_DB_PATH.unlink()
        print(f"Removed existing {DEFAULT_DB_PATH.name}")

    print(f"\nInitializing database at {DEFAULT_DB_PATH}")
    init_db()
    conn = get_db()

    with transaction(conn):
        print("\n--- Phase 1: Foundation ---")
        seed_scales(conn)
        migrate_elements(conn)
        migrate_stellar_anchors(conn)

        print("\n--- Phase 2: Molecular ---")
        migrate_amino_acids(conn)
        migrate_molecular_chemistry(conn)
        migrate_enzymes(conn)
        migrate_dna_structural(conn)

        print("\n--- Phase 3: Biological Systems ---")
        migrate_comprehensive_frequencies(conn)
        migrate_feedback_loops(conn)

        print("\n--- Phase 4: Relationships ---")
        migrate_harmonic_relationships(conn)

        print("\n--- Phase 5: Environmental & Plants ---")
        migrate_environmental(conn)
        migrate_plants(conn)
        migrate_medicinal_plants(conn)

        print("\n--- Phase 6: Medical ---")
        migrate_autoimmune(conn)
        migrate_protocols(conn)
        migrate_delivery_systems(conn)

        print("\n--- Phase 7: Specialized ---")
        migrate_genomic_summaries(conn)
        migrate_materials(conn)

        print("\n--- Phase 8: Remaining files ---")
        migrate_remaining_json_files(conn)

    # Print summary
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE — Summary:")
    print("=" * 60)
    for table in ["entities", "relationships", "harmonics", "feedback_loops",
                  "disease_states", "protocols", "genomic_profiles", "sources"]:
        row = conn.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()
        print(f"  {table:25s} {row['c']:>6,}")

    db_size = DEFAULT_DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  Database size: {db_size:.1f} MB")
    print(f"  Location: {DEFAULT_DB_PATH}")

    conn.close()


if __name__ == "__main__":
    migrate_all()
