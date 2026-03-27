#!/usr/bin/env python3
"""
GnosisLoom Frequency Analyzer
============================

A clean, researcher-friendly tool for analyzing biological frequency relationships
and discovering harmonic patterns in the GnosisLoom database.

Authors: Kurt & Claude
License: CC BY 4.0
Version: 1.0.0
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class FrequencyAnalyzer:
    """
    Analyze biological frequency patterns and relationships.
    
    This class provides tools for exploring the harmonic relationships
    discovered in biological systems, including:
    - Frequency correlation analysis
    - Harmonic relationship detection  
    - Stellar anchor pattern recognition
    - Octave cascade identification
    """
    
    def __init__(self, data_path: str = "../data"):
        """
        Initialize the analyzer with GnosisLoom data.
        
        Args:
            data_path: Path to GnosisLoom data directory
        """
        self.data_path = Path(data_path)
        self.frequencies = {}
        self.stellar_anchors = {}
        self.load_data()
    
    def load_data(self):
        """Load all GnosisLoom frequency databases."""
        try:
            # Load comprehensive frequencies
            with open(self.data_path / "comprehensive_frequencies.json", 'r') as f:
                self.frequencies = json.load(f)
            
            # Load stellar anchors
            with open(self.data_path / "comprehensive_stellar_anchors.json", 'r') as f:
                self.stellar_anchors = json.load(f)
                
            print(f"✅ Loaded {len(self.frequencies)} frequency categories")
            print(f"✅ Loaded {len(self.stellar_anchors)} stellar anchor relationships")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def find_harmonic_relationships(self, target_frequency: float, 
                                  tolerance: float = 0.1) -> List[Dict]:
        """
        Find harmonic relationships for a target frequency.
        
        Args:
            target_frequency: The frequency to analyze
            tolerance: Acceptable deviation for harmonic matching
            
        Returns:
            List of harmonic relationships found
        """
        relationships = []
        
        # Check all frequencies in database
        for category, data in self.frequencies.items():
            if isinstance(data, dict):
                for freq_id, freq_info in data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        freq = freq_info['frequency']
                        
                        # Check for octave relationships (2:1, 3:1, 4:1, etc.)
                        for ratio in [0.5, 2.0, 3.0, 4.0, 1.5, 2.5]:
                            expected = target_frequency * ratio
                            if abs(freq - expected) / expected < tolerance:
                                relationships.append({
                                    'type': 'harmonic',
                                    'ratio': ratio,
                                    'target_freq': target_frequency,
                                    'found_freq': freq,
                                    'frequency_id': freq_id,
                                    'category': category,
                                    'deviation': abs(freq - expected) / expected
                                })
        
        return sorted(relationships, key=lambda x: x['deviation'])
    
    def analyze_golden_ratio_relationships(self) -> List[Dict]:
        """
        Find frequency relationships that approximate the golden ratio (φ = 1.618).
        
        Returns:
            List of golden ratio relationships discovered
        """
        golden_ratio = 1.6180339887
        tolerance = 0.1
        relationships = []
        
        # Get all frequencies as a flat list
        all_frequencies = []
        for category, data in self.frequencies.items():
            if isinstance(data, dict):
                for freq_id, freq_info in data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        all_frequencies.append({
                            'frequency': freq_info['frequency'],
                            'id': freq_id,
                            'category': category
                        })
        
        # Check all pairs for golden ratio relationships
        for i, freq1 in enumerate(all_frequencies):
            for freq2 in all_frequencies[i+1:]:
                if freq1['frequency'] > 0 and freq2['frequency'] > 0:
                    ratio = max(freq1['frequency'], freq2['frequency']) / min(freq1['frequency'], freq2['frequency'])
                    
                    if abs(ratio - golden_ratio) / golden_ratio < tolerance:
                        relationships.append({
                            'freq1': freq1,
                            'freq2': freq2,
                            'ratio': ratio,
                            'deviation_from_phi': abs(ratio - golden_ratio) / golden_ratio,
                            'significance': 'golden_ratio_relationship'
                        })
        
        return sorted(relationships, key=lambda x: x['deviation_from_phi'])
    
    def find_octave_cascades(self) -> List[Dict]:
        """
        Identify octave cascade patterns (perfect 2:1 frequency relationships).
        
        Returns:
            List of octave cascade sequences found
        """
        tolerance = 0.05  # 5% tolerance for octave relationships
        cascades = []
        
        # Get all frequencies
        all_frequencies = []
        for category, data in self.frequencies.items():
            if isinstance(data, dict):
                for freq_id, freq_info in data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        all_frequencies.append({
                            'frequency': freq_info['frequency'],
                            'id': freq_id,
                            'category': category
                        })
        
        # Sort by frequency
        all_frequencies.sort(key=lambda x: x['frequency'])
        
        # Find cascade sequences
        for base_freq in all_frequencies:
            cascade = [base_freq]
            current_freq = base_freq['frequency']
            
            # Look for ascending octaves
            for multiplier in [2.0, 4.0, 8.0, 16.0]:
                target = current_freq * multiplier
                
                # Find closest match
                for candidate in all_frequencies:
                    if abs(candidate['frequency'] - target) / target < tolerance:
                        cascade.append(candidate)
                        break
            
            # Only keep cascades with at least 3 elements
            if len(cascade) >= 3:
                cascades.append({
                    'cascade': cascade,
                    'length': len(cascade),
                    'base_frequency': base_freq['frequency'],
                    'octave_pattern': [f['frequency'] for f in cascade]
                })
        
        return cascades
    
    def analyze_stellar_anchor_patterns(self) -> Dict:
        """
        Analyze patterns in stellar anchor assignments.
        
        Returns:
            Dictionary containing stellar anchor analysis
        """
        anchor_stats = {}
        
        for anchor_name, anchor_data in self.stellar_anchors.items():
            if isinstance(anchor_data, dict):
                frequencies = []
                for item_key, item_data in anchor_data.items():
                    if isinstance(item_data, dict) and 'frequency' in item_data:
                        frequencies.append(item_data['frequency'])
                
                if frequencies:
                    anchor_stats[anchor_name] = {
                        'count': len(frequencies),
                        'mean_frequency': np.mean(frequencies),
                        'std_frequency': np.std(frequencies),
                        'min_frequency': min(frequencies),
                        'max_frequency': max(frequencies),
                        'frequency_range': max(frequencies) - min(frequencies)
                    }
        
        return anchor_stats
    
    def create_frequency_report(self, target_frequency: float) -> str:
        """
        Generate a comprehensive frequency analysis report.
        
        Args:
            target_frequency: Frequency to analyze
            
        Returns:
            Formatted analysis report
        """
        report = f"🔬 FREQUENCY ANALYSIS REPORT\n"
        report += f"{'='*50}\n"
        report += f"Target Frequency: {target_frequency:.2f} Hz\n\n"
        
        # Harmonic relationships
        harmonics = self.find_harmonic_relationships(target_frequency)
        if harmonics:
            report += f"🎵 HARMONIC RELATIONSHIPS FOUND: {len(harmonics)}\n"
            for h in harmonics[:5]:  # Top 5 matches
                report += f"  • {h['ratio']}:1 ratio → {h['found_freq']:.2f} Hz "
                report += f"({h['frequency_id']}, deviation: {h['deviation']:.1%})\n"
        else:
            report += "🎵 No significant harmonic relationships found\n"
        
        report += "\n"
        
        # Golden ratio check
        golden_relationships = []
        for category, data in self.frequencies.items():
            if isinstance(data, dict):
                for freq_id, freq_info in data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        freq = freq_info['frequency']
                        if freq > 0 and target_frequency > 0:
                            ratio = max(freq, target_frequency) / min(freq, target_frequency)
                            if abs(ratio - 1.618) / 1.618 < 0.1:
                                golden_relationships.append({
                                    'freq': freq,
                                    'ratio': ratio,
                                    'id': freq_id
                                })
        
        if golden_relationships:
            report += f"✨ GOLDEN RATIO RELATIONSHIPS: {len(golden_relationships)}\n"
            for g in golden_relationships[:3]:
                report += f"  • {g['freq']:.2f} Hz (ratio: {g['ratio']:.3f} ≈ φ)\n"
        else:
            report += "✨ No golden ratio relationships found\n"
        
        return report
    
    def visualize_frequency_distribution(self, save_path: Optional[str] = None):
        """
        Create visualization of frequency distribution across categories.
        
        Args:
            save_path: Optional path to save the plot
        """
        # Collect all frequencies
        freq_data = []
        for category, data in self.frequencies.items():
            if isinstance(data, dict):
                for freq_id, freq_info in data.items():
                    if isinstance(freq_info, dict) and 'frequency' in freq_info:
                        freq_data.append({
                            'frequency': freq_info['frequency'],
                            'category': category,
                            'id': freq_id
                        })
        
        df = pd.DataFrame(freq_data)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, y='category', x='frequency')
        plt.title('Frequency Distribution Across Biological Categories')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Biological Category')
        plt.xscale('log')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Example usage of the FrequencyAnalyzer."""
    print("🧬 GnosisLoom Frequency Analyzer")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = FrequencyAnalyzer()
    
    # Analyze the consciousness interface frequency (DMT)
    print("\n🧠 ANALYZING CONSCIOUSNESS INTERFACE (13.5 Hz)")
    report = analyzer.create_frequency_report(13.5)
    print(report)
    
    # Find golden ratio relationships
    print("\n✨ SEARCHING FOR GOLDEN RATIO PATTERNS...")
    golden_ratios = analyzer.analyze_golden_ratio_relationships()
    if golden_ratios:
        print(f"Found {len(golden_ratios)} golden ratio relationships!")
        for gr in golden_ratios[:3]:
            print(f"  • {gr['freq1']['frequency']:.2f} : {gr['freq2']['frequency']:.2f} Hz "
                  f"(ratio: {gr['ratio']:.3f})")
    
    # Find octave cascades  
    print("\n🎵 SEARCHING FOR OCTAVE CASCADES...")
    cascades = analyzer.find_octave_cascades()
    if cascades:
        print(f"Found {len(cascades)} octave cascade patterns!")
        for cascade in cascades[:2]:
            freqs = [f"{f:.2f}" for f in cascade['octave_pattern']]
            print(f"  • {' → '.join(freqs)} Hz")
    
    print("\n🎉 Analysis complete! Use analyzer.visualize_frequency_distribution() to see plots.")

if __name__ == "__main__":
    main()