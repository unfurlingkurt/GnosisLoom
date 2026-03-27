#!/usr/bin/env python3
"""
Extract New Molecular Frequency Signatures from Recent Databases
Systematic integration of discoveries into comprehensive frequency database
"""

import json
import os
from pathlib import Path

def extract_elemental_frequencies():
    """Extract elemental frequency anchors from periodic table data"""
    try:
        with open('data/periodic_table_frequencies.json', 'r') as f:
            periodic_data = json.load(f)
        
        elemental_frequencies = {}
        
        # Extract from sol system primary anchors
        if 'sol_system_primary_anchors' in periodic_data['periodic_table_frequencies']:
            sol_anchors = periodic_data['periodic_table_frequencies']['sol_system_primary_anchors']
            for element, data in sol_anchors.items():
                if 'frequency' in data and 'stellar_anchor' in data:
                    freq_key = f"{element.lower()}_stellar_anchor"
                    elemental_frequencies[freq_key] = {
                        "normal_freq": data['frequency'],
                        "range": [data['frequency'] * 0.9, data['frequency'] * 1.1],
                        "phase": 0.0,
                        "stellar_anchor": data['stellar_anchor'],
                        "element": element.upper(),
                        "harmonics": data.get('harmonic_series', []),
                        "disease_states": {},
                        "biofrequency_code": data.get('element_code', f"ELE-{element.upper()[:3]}-{int(data['frequency']*100):03d}"),
                        "biological_role": data.get('biological_role', ''),
                        "cell_type_code": data.get('cell_type_code', '')
                    }
        
        # Extract from other stellar anchor systems
        stellar_systems = ['sirius_system_anchors', 'polaris_system_anchors', 'betelgeuse_system_anchors', 
                          'rigel_system_anchors', 'vega_system_anchors', 'arcturus_system_anchors']
        
        for system in stellar_systems:
            if system in periodic_data['periodic_table_frequencies']:
                system_data = periodic_data['periodic_table_frequencies'][system]
                for element, data in system_data.items():
                    if 'frequency' in data and 'stellar_anchor' in data:
                        freq_key = f"{element.lower()}_stellar_anchor"
                        elemental_frequencies[freq_key] = {
                            "normal_freq": data['frequency'],
                            "range": [data['frequency'] * 0.9, data['frequency'] * 1.1],
                            "phase": 0.0,
                            "stellar_anchor": data['stellar_anchor'],
                            "element": element.upper(),
                            "harmonics": data.get('harmonic_series', []),
                            "disease_states": {},
                            "biofrequency_code": data.get('element_code', f"ELE-{element.upper()[:3]}-{int(data['frequency']*100):03d}"),
                            "biological_role": data.get('biological_role', ''),
                            "cell_type_code": data.get('cell_type_code', '')
                        }
        
        return elemental_frequencies
    except Exception as e:
        print(f"Error extracting elemental frequencies: {e}")
        return {}

def extract_molecular_assemblies():
    """Extract molecular assembly frequencies from chemistry data"""
    try:
        with open('data/molecular_assembly_pathways.json', 'r') as f:
            molecular_data = json.load(f)
        
        assembly_frequencies = {}
        
        # Extract amino acid frequencies
        if 'amino_acids' in molecular_data:
            for aa_code, data in molecular_data['amino_acids'].items():
                if 'frequency' in data:
                    freq_key = f"amino_acid_{aa_code.lower()}"
                    assembly_frequencies[freq_key] = {
                        "normal_freq": data['frequency'],
                        "range": [data['frequency'] * 0.95, data['frequency'] * 1.05],
                        "phase": 0.0,
                        "stellar_anchor": data.get('stellar_anchor_dominance'),
                        "element": data.get('primary_element'),
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": f"AA-{aa_code}-{int(data['frequency']*100):03d}",
                        "full_name": data.get('full_name', '')
                    }
        
        # Extract water structure templates
        try:
            with open('data/structured_water_templates.json', 'r') as f:
                water_data = json.load(f)
            
            if 'water_structures' in water_data:
                for structure_id, data in water_data['water_structures'].items():
                    if 'frequency' in data:
                        freq_key = f"water_{structure_id}"
                        assembly_frequencies[freq_key] = {
                            "normal_freq": data['frequency'],
                            "range": [data['frequency'] * 0.95, data['frequency'] * 1.05],
                            "phase": 0.0,
                            "stellar_anchor": "Sol-Oxygen",
                            "element": "H2O",
                            "harmonics": data.get('harmonics', []),
                            "disease_states": {},
                            "biofrequency_code": f"WAT-STR-{int(data['frequency']*100):03d}"
                        }
        except FileNotFoundError:
            pass
        
        return assembly_frequencies
    except Exception as e:
        print(f"Error extracting molecular assemblies: {e}")
        return {}

def extract_dna_frequencies():
    """Extract DNA base and structural frequencies"""
    try:
        with open('data/dna_structural_frequencies.json', 'r') as f:
            dna_data = json.load(f)
        
        dna_frequencies = {}
        
        # Extract base frequencies
        if 'dna_bases' in dna_data:
            for base_name, data in dna_data['dna_bases'].items():
                if 'frequency' in data:
                    freq_key = f"dna_base_{base_name.lower()}"
                    dna_frequencies[freq_key] = {
                        "normal_freq": data['frequency'],
                        "range": [data['frequency'] * 0.98, data['frequency'] * 1.02],
                        "phase": 0.0,
                        "stellar_anchor": data.get('stellar_anchor_dominance'),
                        "element": data.get('primary_elements'),
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": f"DNA-{base_name[0]}-{int(data['frequency']*100):03d}"
                    }
        
        # Extract base pair beat frequencies
        if 'base_pairs' in dna_data:
            for pair_name, data in dna_data['base_pairs'].items():
                if 'beat_frequency' in data:
                    freq_key = f"dna_beat_{pair_name.lower().replace('-','_')}"
                    dna_frequencies[freq_key] = {
                        "normal_freq": data['beat_frequency'],
                        "range": [data['beat_frequency'] * 0.99, data['beat_frequency'] * 1.01],
                        "phase": 0.0,
                        "stellar_anchor": None,
                        "element": "ATGC",
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": f"DNA-BP-{int(data['beat_frequency']*100):03d}"
                    }
        
        return dna_frequencies
    except Exception as e:
        print(f"Error extracting DNA frequencies: {e}")
        return {}

def extract_neural_frequencies():
    """Extract neural frequency responses from neural matrix"""
    try:
        with open('data/neural_frequency_response_matrix.json', 'r') as f:
            neural_data = json.load(f)
        
        neural_frequencies = {}
        
        # Helper function to parse frequency strings
        def parse_frequency_range(freq_str):
            # Remove _THz suffix and split on dash
            freq_clean = freq_str.replace('_THz', '').replace('THz', '')
            freq_range = freq_clean.split('-')
            if len(freq_range) == 2:
                try:
                    freq_min = float(freq_range[0])
                    freq_max = float(freq_range[1])
                    return freq_min, freq_max, (freq_min + freq_max) / 2
                except ValueError:
                    return None, None, None
            return None, None, None
        
        # Extract motor neuron responses
        motor_data = neural_data['neural_frequency_responses']['motor_neuron_responses']
        for neuron_type, data in motor_data.items():
            if 'optimal_frequency' in data:
                freq_min, freq_max, avg_freq = parse_frequency_range(data['optimal_frequency'])
                if avg_freq is not None:
                    freq_key = f"motor_neuron_{neuron_type}"
                    neural_frequencies[freq_key] = {
                        "normal_freq": avg_freq,
                        "range": [freq_min, freq_max],
                        "phase": 0.0,
                        "stellar_anchor": None,
                        "element": "Neural",
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": f"NEU-MOT-{int(avg_freq*100):03d}",
                        "frequency_units": "THz",
                        "axon_diameter": data.get('axon_diameter', ''),
                        "conduction_velocity": data.get('conduction_velocity', '')
                    }
        
        # Extract sensory neuron responses  
        sensory_data = neural_data['neural_frequency_responses']['sensory_neuron_responses']
        for neuron_type, data in sensory_data.items():
            if 'optimal_frequency' in data:
                freq_min, freq_max, avg_freq = parse_frequency_range(data['optimal_frequency'])
                if avg_freq is not None:
                    freq_key = f"sensory_neuron_{neuron_type}"
                    neural_frequencies[freq_key] = {
                        "normal_freq": avg_freq,
                        "range": [freq_min, freq_max],
                        "phase": 0.0,
                        "stellar_anchor": None,
                        "element": "Neural",
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": f"NEU-SEN-{int(avg_freq*100):03d}",
                        "frequency_units": "THz",
                        "axon_diameter": data.get('axon_diameter', ''),
                        "sensory_modality": data.get('sensory_modality', '')
                    }
        
        # Extract autonomic responses
        autonomic_data = neural_data['neural_frequency_responses']['autonomic_responses']
        for system_type, system_data in autonomic_data.items():
            for component, data in system_data.items():
                if 'frequency' in data:
                    freq_min, freq_max, avg_freq = parse_frequency_range(data['frequency'])
                    if avg_freq is not None:
                        freq_key = f"autonomic_{system_type}_{component}"
                        neural_frequencies[freq_key] = {
                            "normal_freq": avg_freq,
                            "range": [freq_min, freq_max],
                            "phase": 0.0,
                            "stellar_anchor": None,
                            "element": "Neural",
                            "harmonics": [],
                            "disease_states": {},
                            "biofrequency_code": f"NEU-AUT-{int(avg_freq*100):03d}",
                            "frequency_units": "THz"
                        }
        
        return neural_frequencies
    except Exception as e:
        print(f"Error extracting neural frequencies: {e}")
        return {}

def extract_scaffold_frequencies():
    """Extract nerve regeneration scaffold protein frequencies"""
    try:
        with open('data/nerve_regeneration_scaffolds.json', 'r') as f:
            scaffold_data = json.load(f)
        
        scaffold_frequencies = {}
        
        # Extract scaffold proteins
        if 'scaffold_protein_frequencies' in scaffold_data['nerve_regeneration_architecture']:
            proteins = scaffold_data['nerve_regeneration_architecture']['scaffold_protein_frequencies']
            for protein_name, data in proteins.items():
                if 'primary_frequency' in data:
                    freq_value = data['primary_frequency']
                    
                    freq_key = f"scaffold_{protein_name.lower()}"
                    scaffold_frequencies[freq_key] = {
                        "normal_freq": freq_value,
                        "range": [freq_value * 0.95, freq_value * 1.05],
                        "phase": 0.0,
                        "stellar_anchor": None,
                        "element": "Protein",
                        "harmonics": [],
                        "disease_states": {},
                        "biofrequency_code": data.get('protein_code', f"SCF-{protein_name.upper()[:3]}-{int(freq_value*100):03d}"),
                        "frequency_units": data.get('frequency_units', 'THz'),
                        "function": data.get('primary_function', ''),
                        "molecular_weight": data.get('molecular_weight', 0),
                        "amino_acid_residues": data.get('amino_acid_residues', 0)
                    }
        
        return scaffold_frequencies
    except Exception as e:
        print(f"Error extracting scaffold frequencies: {e}")
        return {}

def extract_q_dna_frequencies():
    """Extract Q-DNA quantum strand frequencies"""
    try:
        with open('data/q_dna_projection_dynamics.json', 'r') as f:
            q_dna_data = json.load(f)
        
        q_dna_frequencies = {}
        
        # Extract primary Q-strands
        primary_strands = q_dna_data['q_dna_framework']['quantum_strand_architecture']['primary_strands']
        for strand_name, data in primary_strands.items():
            if 'frequency' in data:
                freq_key = f"q_dna_{strand_name.lower()}"
                q_dna_frequencies[freq_key] = {
                    "normal_freq": data['frequency'],
                    "range": [data['frequency'] * 0.999, data['frequency'] * 1.001],
                    "phase": 0.0,
                    "stellar_anchor": None,
                    "element": "Quantum",
                    "harmonics": [],
                    "disease_states": {},
                    "biofrequency_code": f"Q-DNA-{strand_name[-1]}-{int(data['frequency']*100):03d}",
                    "projection_target": data.get('projection_target'),
                    "quantum_state": data.get('quantum_state')
                }
        
        return q_dna_frequencies
    except Exception as e:
        print(f"Error extracting Q-DNA frequencies: {e}")
        return {}

def main():
    """Main function to extract and integrate all new frequencies"""
    
    # Change to the correct directory
    os.chdir('/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom')
    
    print("Extracting new molecular frequency signatures...")
    
    # Extract frequencies from different sources
    elemental_freq = extract_elemental_frequencies()
    molecular_freq = extract_molecular_assemblies()
    dna_freq = extract_dna_frequencies()
    neural_freq = extract_neural_frequencies()
    scaffold_freq = extract_scaffold_frequencies()
    q_dna_freq = extract_q_dna_frequencies()
    
    # Combine all new frequencies
    new_frequencies = {}
    new_frequencies.update(elemental_freq)
    new_frequencies.update(molecular_freq)
    new_frequencies.update(dna_freq)
    new_frequencies.update(neural_freq)
    new_frequencies.update(scaffold_freq)
    new_frequencies.update(q_dna_freq)
    
    # Load existing comprehensive database
    try:
        with open('/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/data/comprehensive_frequencies.json', 'r') as f:
            existing_freq = json.load(f)
    except Exception as e:
        print(f"Error loading existing database: {e}")
        existing_freq = {}
    
    # Merge new frequencies with existing (new ones take precedence)
    existing_freq.update(new_frequencies)
    
    # Save updated comprehensive database
    try:
        with open('/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/data/comprehensive_frequencies.json', 'w') as f:
            json.dump(existing_freq, f, indent=2)
        
        print(f"Successfully integrated {len(new_frequencies)} new frequency signatures")
        print(f"Total frequency signatures: {len(existing_freq)}")
        
        # Print summary of what was added
        print("\n=== NEW FREQUENCY CATEGORIES ADDED ===")
        categories = {}
        for key in new_frequencies.keys():
            category = key.split('_')[0]
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in categories.items():
            print(f"{category.upper()}: {count} frequencies")
            
    except Exception as e:
        print(f"Error saving updated database: {e}")

if __name__ == "__main__":
    main()