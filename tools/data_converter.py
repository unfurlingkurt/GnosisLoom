#!/usr/bin/env python3
"""
GnosisLoom Data Converter
========================

Convert GnosisLoom frequency data to industry standard formats for 
seamless integration with research workflows.

Supported Output Formats:
- CSV (Excel, R, Python pandas)
- TSV (Bioinformatics tools)
- Parquet (Big data analysis)
- JSON-LD (Semantic web)
- FHIR-compatible JSON (Clinical systems)

Authors: Kurt & Claude
License: CC BY 4.0
Version: 1.0.0
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings

# Optional imports for advanced formats
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    warnings.warn("PyArrow not available. Parquet export disabled.")

class DataConverter:
    """
    Convert GnosisLoom data to multiple research-friendly formats.
    """
    
    def __init__(self, data_path: str = "../data", output_path: str = "../data-exports"):
        """
        Initialize the converter.
        
        Args:
            data_path: Path to GnosisLoom data directory
            output_path: Path for exported files
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        
    def load_json_data(self, filename: str) -> Dict:
        """Load JSON data file."""
        try:
            with open(self.data_path / filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return {}
    
    def flatten_nested_dict(self, data: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten nested dictionary structure for tabular export.
        
        Args:
            data: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self.flatten_nested_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to string representation
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def convert_frequencies_to_csv(self, output_name: str = "biological_frequencies.csv"):
        """
        Convert comprehensive frequencies to CSV format.
        
        Args:
            output_name: Output filename
        """
        print(f"🔄 Converting biological frequencies to CSV...")
        
        data = self.load_json_data("comprehensive_frequencies.json")
        if not data:
            return
        
        rows = []
        for category, category_data in data.items():
            if isinstance(category_data, dict):
                # Handle direct frequency entry (category is the frequency name)
                if 'normal_freq' in category_data or 'frequency' in category_data:
                    row = self.flatten_nested_dict(category_data)
                    row['frequency_name'] = category
                    row['category'] = 'biological_system'
                    rows.append(row)
                else:
                    # Handle nested structure 
                    for freq_id, freq_info in category_data.items():
                        if isinstance(freq_info, dict):
                            row = self.flatten_nested_dict(freq_info)
                            row['frequency_name'] = freq_id
                            row['category'] = category
                            rows.append(row)
        
        df = pd.DataFrame(rows)
        output_file = self.output_path / output_name
        df.to_csv(output_file, index=False)
        print(f"✅ Exported {len(df)} frequency records to {output_file}")
        return df
    
    def convert_stellar_anchors_to_csv(self, output_name: str = "stellar_anchors.csv"):
        """Convert stellar anchor data to CSV."""
        print(f"🔄 Converting stellar anchors to CSV...")
        
        data = self.load_json_data("comprehensive_stellar_anchors.json")
        if not data:
            return
            
        rows = []
        for anchor_name, anchor_data in data.items():
            if isinstance(anchor_data, dict):
                # Direct stellar anchor data structure
                row = self.flatten_nested_dict(anchor_data)
                row['stellar_anchor'] = anchor_name
                rows.append(row)
        
        df = pd.DataFrame(rows)
        output_file = self.output_path / output_name
        df.to_csv(output_file, index=False)
        print(f"✅ Exported {len(df)} stellar anchor records to {output_file}")
        return df
    
    def convert_specialized_datasets(self):
        """Convert all specialized JSON datasets to CSV."""
        specialized_files = [
            ("primordial_chemistry_frequencies.json", "primordial_chemistry.csv"),
            ("pineal_visual_frequencies.json", "pineal_visual_system.csv"), 
            ("molecular_chemistry_resonance.json", "molecular_chemistry.csv"),
            ("feedback_loops.json", "biological_feedback_loops.csv"),
            ("harmonic_relationships.json", "harmonic_relationships.csv")
        ]
        
        for json_file, csv_file in specialized_files:
            print(f"🔄 Converting {json_file} to CSV...")
            
            data = self.load_json_data(json_file)
            if not data:
                continue
                
            rows = []
            
            def extract_rows(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_prefix = f"{prefix}_{key}" if prefix else key
                        
                        if isinstance(value, dict) and any(isinstance(v, (int, float, str)) for v in value.values()):
                            # This looks like a record
                            row = self.flatten_nested_dict(value)
                            row['record_id'] = new_prefix
                            rows.append(row)
                        else:
                            extract_rows(value, new_prefix)
            
            extract_rows(data)
            
            if rows:
                df = pd.DataFrame(rows)
                output_file = self.output_path / csv_file
                df.to_csv(output_file, index=False)
                print(f"✅ Exported {len(df)} records to {output_file}")
    
    def create_summary_statistics(self):
        """Create summary statistics across all datasets."""
        print("📊 Generating summary statistics...")
        
        stats = {
            'generation_date': datetime.now().isoformat(),
            'total_datasets': 0,
            'total_frequency_records': 0,
            'frequency_range': {'min': float('inf'), 'max': 0},
            'categories': [],
            'stellar_anchors': [],
        }
        
        # Analyze comprehensive frequencies
        freq_data = self.load_json_data("comprehensive_frequencies.json")
        if freq_data:
            for category, category_data in freq_data.items():
                stats['categories'].append(category)
                if isinstance(category_data, dict):
                    for freq_info in category_data.values():
                        if isinstance(freq_info, dict) and 'frequency' in freq_info:
                            freq = freq_info['frequency']
                            if isinstance(freq, (int, float)):
                                stats['total_frequency_records'] += 1
                                stats['frequency_range']['min'] = min(stats['frequency_range']['min'], freq)
                                stats['frequency_range']['max'] = max(stats['frequency_range']['max'], freq)
        
        # Analyze stellar anchors
        anchor_data = self.load_json_data("comprehensive_stellar_anchors.json")
        if anchor_data:
            stats['stellar_anchors'] = list(anchor_data.keys())
        
        # Save summary
        with open(self.output_path / "dataset_summary.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Summary: {stats['total_frequency_records']} frequency records across {len(stats['categories'])} categories")
        return stats
    
    def export_to_parquet(self):
        """Export data to Parquet format for big data analysis."""
        if not PARQUET_AVAILABLE:
            print("⚠️  Parquet export requires PyArrow: pip install pyarrow")
            return
            
        print("🔄 Converting to Parquet format...")
        
        # Convert main datasets
        freq_df = self.convert_frequencies_to_csv("temp_freq.csv")
        if freq_df is not None:
            freq_df.to_parquet(self.output_path / "biological_frequencies.parquet", 
                             engine='pyarrow', compression='snappy')
            print("✅ Created biological_frequencies.parquet")
        
        anchor_df = self.convert_stellar_anchors_to_csv("temp_anchor.csv")
        if anchor_df is not None:
            anchor_df.to_parquet(self.output_path / "stellar_anchors.parquet",
                               engine='pyarrow', compression='snappy')
            print("✅ Created stellar_anchors.parquet")
        
        # Clean up temp files
        for temp_file in ["temp_freq.csv", "temp_anchor.csv"]:
            temp_path = self.output_path / temp_file
            if temp_path.exists():
                temp_path.unlink()
    
    def create_fhir_compatible_json(self):
        """Create FHIR-compatible JSON for clinical integration."""
        print("🏥 Creating FHIR-compatible format...")
        
        freq_data = self.load_json_data("comprehensive_frequencies.json")
        
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
        for category, category_data in freq_data.items():
            if isinstance(category_data, dict):
                for freq_id, freq_info in category_data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        entry = {
                            "resource": {
                                "resourceType": "Observation",
                                "id": f"freq-{freq_id}",
                                "status": "final",
                                "category": [{
                                    "coding": [{
                                        "system": "https://gnosisloom.org/categories",
                                        "code": category,
                                        "display": category.replace('_', ' ').title()
                                    }]
                                }],
                                "code": {
                                    "coding": [{
                                        "system": "https://gnosisloom.org/frequencies", 
                                        "code": freq_id,
                                        "display": f"Biological Frequency: {freq_id}"
                                    }]
                                },
                                "valueQuantity": {
                                    "value": freq_info['frequency'],
                                    "unit": "Hz",
                                    "system": "http://unitsofmeasure.org",
                                    "code": "Hz"
                                }
                            }
                        }
                        fhir_bundle["entry"].append(entry)
                        entry_count += 1
        
        with open(self.output_path / "gnosisloom_fhir_bundle.json", 'w') as f:
            json.dump(fhir_bundle, f, indent=2)
        
        print(f"✅ Created FHIR bundle with {entry_count} observations")
    
    def export_all_formats(self):
        """Export data to all supported formats."""
        print("🚀 GNOSISLOOM DATA EXPORT")
        print("=" * 40)
        
        # CSV exports
        self.convert_frequencies_to_csv()
        self.convert_stellar_anchors_to_csv() 
        self.convert_specialized_datasets()
        
        # Parquet export
        self.export_to_parquet()
        
        # FHIR export
        self.create_fhir_compatible_json()
        
        # Summary statistics
        self.create_summary_statistics()
        
        print("\n✅ Export complete! Files available in data-exports/")
        print("\n📁 Generated files:")
        for file_path in sorted(self.output_path.glob("*")):
            size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"  • {file_path.name} ({size_mb:.2f} MB)")

def main():
    """Run the data converter."""
    converter = DataConverter()
    converter.export_all_formats()

if __name__ == "__main__":
    main()