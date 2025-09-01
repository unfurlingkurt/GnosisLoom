#!/usr/bin/env python3
"""
Improve Chemistry Data Exports

Creates focused, complete CSV files for molecular chemistry and primordial chemistry
data instead of sparse, overly wide tables.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

def load_json_data(filepath: Path) -> Dict:
    """Load JSON data safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return {}

def create_focused_molecular_chemistry_csv():
    """Create focused molecular chemistry CSV with complete data"""
    print("🧪 Creating focused molecular chemistry export...")
    
    data_path = Path("../data")
    output_path = Path("../data-exports")
    
    # Load the molecular chemistry data
    mol_data = load_json_data(data_path / "molecular_chemistry_resonance.json")
    
    if not mol_data or 'molecular_chemistry_resonance' not in mol_data:
        print("❌ No molecular chemistry data found")
        return
    
    chemistry_data = mol_data['molecular_chemistry_resonance']
    
    # Create focused datasets
    amino_acids = []
    enzymes = []
    
    # Process amino acid frequencies
    if 'amino_acid_frequencies' in chemistry_data:
        for aa_code, aa_data in chemistry_data['amino_acid_frequencies'].items():
            if isinstance(aa_data, dict):
                row = {
                    'amino_acid_code': aa_code,
                    'frequency_hz': aa_data.get('frequency', 0),
                    'molecular_formula': aa_data.get('formula', ''),
                    'carbon_count': aa_data.get('composition', {}).get('C', 0),
                    'hydrogen_count': aa_data.get('composition', {}).get('H', 0),
                    'nitrogen_count': aa_data.get('composition', {}).get('N', 0),
                    'oxygen_count': aa_data.get('composition', {}).get('O', 0),
                    'sulfur_count': aa_data.get('composition', {}).get('S', 0),
                    'calculation_method': aa_data.get('calculation', ''),
                    'hydrophobic': aa_data.get('properties', {}).get('hydrophobic', False),
                    'polar': aa_data.get('properties', {}).get('polar', False),
                    'charged': aa_data.get('properties', {}).get('charged', 0),
                    'aromatic': aa_data.get('properties', {}).get('aromatic', False),
                    'branched': aa_data.get('properties', {}).get('branched', False),
                    'size_category': aa_data.get('size', ''),
                    'helix_propensity': aa_data.get('helix_propensity', ''),
                    'beta_sheet_propensity': aa_data.get('beta_sheet_propensity', ''),
                    'special_function': aa_data.get('special_function', ''),
                    'pk_a': aa_data.get('pk_a', None),
                    'start_codon': aa_data.get('start_codon', ''),
                    'disulfide_bonding': aa_data.get('disulfide_bonding', False),
                    'fluorescence': aa_data.get('fluorescence', False),
                    'indole_ring': aa_data.get('indole_ring', False)
                }
                amino_acids.append(row)
    
    # Process enzyme active sites
    if 'enzyme_active_sites' in chemistry_data:
        for enzyme_name, enzyme_data in chemistry_data['enzyme_active_sites'].items():
            if isinstance(enzyme_data, dict):
                row = {
                    'enzyme_name': enzyme_name,
                    'ec_number': enzyme_data.get('ec_number', ''),
                    'active_site_frequency_hz': enzyme_data.get('active_site_frequency', 0),
                    'active_site_residues': ', '.join(enzyme_data.get('active_site_residues', [])),
                    'residue_frequencies': ', '.join([str(f) for f in enzyme_data.get('frequencies', [])]),
                    'geometry_factor': enzyme_data.get('geometry_factor', 0),
                    'substrate': enzyme_data.get('substrate', ''),
                    'substrate_frequency_hz': enzyme_data.get('substrate_frequency', 0),
                    'catalysis_efficiency': enzyme_data.get('catalysis_efficiency', 0),
                    'reaction': enzyme_data.get('reaction', ''),
                    'optimal_ph': enzyme_data.get('optimal_ph', None),
                    'cofactor': enzyme_data.get('cofactor', ''),
                    'kcat': enzyme_data.get('kcat', None),
                    'optimal_temperature': enzyme_data.get('optimal_temperature', None)
                }
                enzymes.append(row)
    
    # Save focused CSV files
    if amino_acids:
        aa_df = pd.DataFrame(amino_acids)
        aa_df.to_csv(output_path / "amino_acid_frequencies.csv", index=False)
        print(f"✅ Created amino_acid_frequencies.csv with {len(aa_df)} records")
    
    if enzymes:
        enzyme_df = pd.DataFrame(enzymes)
        enzyme_df.to_csv(output_path / "enzyme_active_sites.csv", index=False)
        print(f"✅ Created enzyme_active_sites.csv with {len(enzyme_df)} records")
    
    # Create combined molecular chemistry summary
    if amino_acids or enzymes:
        summary = {
            'amino_acids': len(amino_acids),
            'enzymes': len(enzymes),
            'total_molecular_signatures': len(amino_acids) + len(enzymes)
        }
        
        with open(output_path / "molecular_chemistry_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Molecular chemistry: {summary['amino_acids']} amino acids, {summary['enzymes']} enzymes")

def create_focused_primordial_chemistry_csv():
    """Create focused primordial chemistry CSV with complete data"""
    print("🌊 Creating focused primordial chemistry export...")
    
    data_path = Path("../data")
    output_path = Path("../data-exports")
    
    # Load the primordial chemistry data
    prim_data = load_json_data(data_path / "primordial_chemistry_frequencies.json")
    
    if not prim_data or 'primordial_chemistry_frequencies' not in prim_data:
        print("❌ No primordial chemistry data found")
        return
    
    chemistry_data = prim_data['primordial_chemistry_frequencies']
    
    # Create focused datasets
    water_patterns = []
    lipid_formations = []
    
    # Process structured water patterns
    if 'structured_water_patterns' in chemistry_data:
        for pattern_id, pattern_data in chemistry_data['structured_water_patterns'].items():
            if isinstance(pattern_data, dict):
                row = {
                    'pattern_id': pattern_id,
                    'frequency_hz': pattern_data.get('frequency', 0),
                    'pattern_type': pattern_data.get('pattern', ''),
                    'formation_mechanism': pattern_data.get('formation_mechanism', ''),
                    'temperature_optimal_k': pattern_data.get('temperature_optimal', 0),
                    'crystallization_type': pattern_data.get('crystallization', ''),
                    'cymatic_nodes': pattern_data.get('cymatic_nodes', 0),
                    'golden_ratio_factor': pattern_data.get('golden_ratio_factor', 0),
                    'symmetry': pattern_data.get('symmetry', ''),
                    'bond_angle_degrees': pattern_data.get('bond_angle', 0),
                    'frequencies_list': str(pattern_data.get('frequencies', [])),
                    'primary_beat': pattern_data.get('primary_beat', 0),
                    'secondary_beats': str(pattern_data.get('secondary_beats', [])),
                    'complexity': pattern_data.get('complexity', ''),
                    'ratio_relationships': str(pattern_data.get('ratio_relationships', []))
                }
                water_patterns.append(row)
    
    # Process lipid barrier formations
    if 'lipid_barrier_formations' in chemistry_data:
        for lipid_id, lipid_data in chemistry_data['lipid_barrier_formations'].items():
            if isinstance(lipid_data, dict):
                row = {
                    'lipid_id': lipid_id,
                    'frequency_hz': lipid_data.get('frequency', 0),
                    'component': lipid_data.get('component', ''),
                    'stellar_anchor': lipid_data.get('anchor', ''),
                    'formation_temperature_k': lipid_data.get('formation_temperature', 0),
                    'stability_range_k': lipid_data.get('stability_range', ''),
                    'chain_length': lipid_data.get('chain_length', ''),
                    'bond_strength': lipid_data.get('bond_strength', ''),
                    'stability_function': lipid_data.get('stability_function', ''),
                    'calculation_method': lipid_data.get('calculation', ''),
                    'mechanism': lipid_data.get('mechanism', ''),
                    'membrane_function': lipid_data.get('function', '')
                }
                lipid_formations.append(row)
    
    # Save focused CSV files
    if water_patterns:
        water_df = pd.DataFrame(water_patterns)
        water_df.to_csv(output_path / "structured_water_patterns.csv", index=False)
        print(f"✅ Created structured_water_patterns.csv with {len(water_df)} records")
    
    if lipid_formations:
        lipid_df = pd.DataFrame(lipid_formations)
        lipid_df.to_csv(output_path / "lipid_barrier_formations.csv", index=False)
        print(f"✅ Created lipid_barrier_formations.csv with {len(lipid_df)} records")
    
    # Create combined primordial chemistry summary
    if water_patterns or lipid_formations:
        summary = {
            'water_patterns': len(water_patterns),
            'lipid_formations': len(lipid_formations),
            'total_primordial_signatures': len(water_patterns) + len(lipid_formations),
            'frequency_range_hz': {
                'min': min([p.get('frequency_hz', 0) for p in water_patterns + lipid_formations if p.get('frequency_hz', 0) > 0] or [0]),
                'max': max([p.get('frequency_hz', 0) for p in water_patterns + lipid_formations] or [0])
            }
        }
        
        with open(output_path / "primordial_chemistry_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Primordial chemistry: {summary['water_patterns']} water patterns, {summary['lipid_formations']} lipid formations")

def verify_focused_exports():
    """Verify the new focused exports are complete"""
    print("\n📋 Verifying focused chemistry exports...")
    
    output_path = Path("../data-exports")
    
    focused_files = {
        'amino_acid_frequencies.csv': 'amino acids',
        'enzyme_active_sites.csv': 'enzymes', 
        'structured_water_patterns.csv': 'water patterns',
        'lipid_barrier_formations.csv': 'lipid formations'
    }
    
    for filename, description in focused_files.items():
        filepath = output_path / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"✅ {filename}: {len(df)} {description}")
            
            # Show sample data
            if len(df) > 0:
                print(f"   Sample columns: {list(df.columns)[:5]}...")
                if 'frequency_hz' in df.columns:
                    freq_col = df['frequency_hz'].dropna()
                    if len(freq_col) > 0:
                        print(f"   Frequency range: {freq_col.min():.3f} - {freq_col.max():.3f} Hz")
        else:
            print(f"❌ Missing: {filename}")

def main():
    """Create improved, focused chemistry data exports"""
    print("🔬 IMPROVING CHEMISTRY DATA EXPORTS")
    print("=" * 40)
    
    create_focused_molecular_chemistry_csv()
    create_focused_primordial_chemistry_csv()
    verify_focused_exports()
    
    print("\n🎉 Improved chemistry exports complete!")
    print("   • Replaced sparse wide tables with focused, complete datasets")
    print("   • Each CSV now contains relevant columns with minimal empty cells")
    print("   • Data is properly structured for analysis and research")

if __name__ == "__main__":
    main()