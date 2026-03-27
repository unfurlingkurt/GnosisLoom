#!/usr/bin/env python3
"""
Fix GnosisLoom Data Exports

Fixes issues with data export generation to ensure complete, accurate exports.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_json_safe(filepath: Path) -> Dict:
    """Safely load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return {}

def fix_fhir_bundle():
    """Create proper FHIR bundle with actual data"""
    print("🏥 Fixing FHIR bundle...")
    
    data_path = Path("../data")
    output_path = Path("../data-exports")
    
    # Load the actual frequency data
    freq_data = load_json_safe(data_path / "comprehensive_frequencies.json")
    
    fhir_bundle = {
        "resourceType": "Bundle",
        "id": "gnosisloom-frequencies",
        "meta": {
            "lastUpdated": datetime.now().isoformat(),
            "profile": ["http://hl7.org/fhir/StructureDefinition/Bundle"]
        },
        "identifier": {
            "system": "https://gnosisloom.org/frequency-database",
            "value": "v1.0.0"
        },
        "type": "collection",
        "entry": []
    }
    
    entry_count = 0
    for freq_name, freq_info in freq_data.items():
        if isinstance(freq_info, dict) and freq_info.get('normal_freq'):
            entry = {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"freq-{freq_name}",
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "https://gnosisloom.org/categories",
                            "code": "biological_frequency",
                            "display": "Biological Frequency"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "https://gnosisloom.org/frequencies",
                            "code": freq_name,
                            "display": f"Frequency: {freq_name.replace('_', ' ').title()}"
                        }]
                    },
                    "valueQuantity": {
                        "value": freq_info['normal_freq'],
                        "unit": "Hz",
                        "system": "http://unitsofmeasure.org",
                        "code": "Hz"
                    }
                }
            }
            
            # Add stellar anchor if available
            if freq_info.get('stellar_anchor'):
                entry["resource"]["component"] = [{
                    "code": {
                        "coding": [{
                            "system": "https://gnosisloom.org/stellar-anchors",
                            "code": freq_info['stellar_anchor'],
                            "display": f"Stellar Anchor: {freq_info['stellar_anchor']}"
                        }]
                    },
                    "valueString": freq_info['stellar_anchor']
                }]
            
            fhir_bundle["entry"].append(entry)
            entry_count += 1
    
    # Save fixed FHIR bundle
    with open(output_path / "gnosisloom_fhir_bundle.json", 'w') as f:
        json.dump(fhir_bundle, f, indent=2)
    
    print(f"✅ Created FHIR bundle with {entry_count} frequency observations")
    return entry_count

def fix_dataset_summary():
    """Generate proper dataset summary with actual statistics"""
    print("📊 Fixing dataset summary...")
    
    data_path = Path("../data")
    output_path = Path("../data-exports")
    
    # Load all data files
    freq_data = load_json_safe(data_path / "comprehensive_frequencies.json")
    anchor_data = load_json_safe(data_path / "comprehensive_stellar_anchors.json")
    
    # Calculate actual statistics
    frequencies = []
    categories = []
    stellar_anchors = []
    
    for name, data in freq_data.items():
        if isinstance(data, dict) and data.get('normal_freq'):
            frequencies.append(data['normal_freq'])
            categories.append(name)
            if data.get('stellar_anchor'):
                stellar_anchors.append(data['stellar_anchor'])
    
    # Generate summary
    summary = {
        "generation_date": datetime.now().isoformat(),
        "total_datasets": len(freq_data),
        "total_frequency_records": len(frequencies),
        "frequency_range": {
            "min": float(min(frequencies)) if frequencies else 0,
            "max": float(max(frequencies)) if frequencies else 0,
            "mean": float(np.mean(frequencies)) if frequencies else 0,
            "median": float(np.median(frequencies)) if frequencies else 0
        },
        "frequency_span_orders_of_magnitude": float(np.log10(max(frequencies) / min(frequencies))) if frequencies and min(frequencies) > 0 else 0,
        "categories": categories,
        "stellar_anchors": list(set(stellar_anchors)),
        "stellar_anchor_counts": {k: int(v) for k, v in pd.Series(stellar_anchors).value_counts().items()} if stellar_anchors else {},
        "data_files": {
            "biological_frequencies": len(freq_data),
            "stellar_anchors": len(anchor_data),
        }
    }
    
    # Save fixed summary
    with open(output_path / "dataset_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Generated summary for {len(frequencies)} frequency records")
    print(f"   • Frequency range: {summary['frequency_range']['min']:.6f} - {summary['frequency_range']['max']:.1f} Hz")
    print(f"   • Span: {summary['frequency_span_orders_of_magnitude']:.1f} orders of magnitude")
    
    return summary

def verify_csv_exports():
    """Verify CSV exports are complete and correct"""
    print("📋 Verifying CSV exports...")
    
    output_path = Path("../data-exports")
    
    files_to_check = [
        "biological_frequencies.csv",
        "stellar_anchors.csv", 
        "molecular_chemistry.csv",
        "pineal_visual_system.csv",
        "primordial_chemistry.csv"
    ]
    
    for filename in files_to_check:
        filepath = output_path / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"✅ {filename}: {len(df)} records")
            
            # Check for key columns
            if filename == "biological_frequencies.csv":
                required_cols = ['frequency_name', 'normal_freq']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    print(f"⚠️  Missing columns in {filename}: {missing_cols}")
                else:
                    valid_freqs = df['normal_freq'].dropna()
                    print(f"   • Valid frequencies: {len(valid_freqs)}")
                    if len(valid_freqs) > 0:
                        print(f"   • Range: {valid_freqs.min():.6f} - {valid_freqs.max():.1f} Hz")
        else:
            print(f"❌ Missing: {filename}")

def main():
    """Fix all data export issues"""
    print("🔧 FIXING GNOSISLOOM DATA EXPORTS")
    print("=" * 40)
    
    # Fix individual components
    fhir_entries = fix_fhir_bundle()
    summary = fix_dataset_summary()
    verify_csv_exports()
    
    print("\n🎉 Data export fixes complete!")
    print(f"   • FHIR bundle: {fhir_entries} observations")
    print(f"   • Dataset summary: {summary['total_frequency_records']} frequency records")
    print(f"   • Frequency span: {summary['frequency_span_orders_of_magnitude']:.1f} orders of magnitude")

if __name__ == "__main__":
    main()