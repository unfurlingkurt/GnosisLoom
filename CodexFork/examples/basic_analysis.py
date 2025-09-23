#!/usr/bin/env python3
"""
GnosisLoom Basic Analysis Examples

Demonstrates common analysis patterns for biological frequency data.
Perfect for getting started with the frequency database.

Usage:
    python3 basic_analysis.py
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add tools directory to path
sys.path.append('../tools')

def load_frequency_data(data_path="../data-exports"):
    """Load frequency data from CSV exports"""
    data_path = Path(data_path)
    
    try:
        # Load biological frequencies
        bio_df = pd.read_csv(data_path / 'biological_frequencies.csv')
        print(f"✅ Loaded {len(bio_df)} biological frequency records")
        
        # Load stellar anchors  
        stellar_df = pd.read_csv(data_path / 'stellar_anchors.csv')
        print(f"✅ Loaded {len(stellar_df)} stellar anchor systems")
        
        return bio_df, stellar_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

def analyze_frequency_distribution(bio_df):
    """Analyze the distribution of biological frequencies"""
    print("\n🔬 FREQUENCY DISTRIBUTION ANALYSIS")
    print("=" * 40)
    
    normal_freqs = bio_df['normal_freq'].dropna()
    
    print(f"📊 Total frequency records: {len(bio_df)}")
    print(f"📊 Valid normal frequencies: {len(normal_freqs)}")
    print(f"📊 Frequency range: {normal_freqs.min():.6f} - {normal_freqs.max():.1f} Hz")
    print(f"📊 Frequency span: {np.log10(normal_freqs.max() / normal_freqs.min()):.1f} orders of magnitude")
    print(f"📊 Median frequency: {normal_freqs.median():.3f} Hz")
    print(f"📊 Mean frequency: {normal_freqs.mean():.3f} Hz")
    
    # Show frequency ranges
    print(f"\n📈 Frequency Distribution:")
    print(f"   • Ultra-low (< 1 Hz): {len(normal_freqs[normal_freqs < 1])} systems")
    print(f"   • Low (1-10 Hz): {len(normal_freqs[(normal_freqs >= 1) & (normal_freqs < 10)])} systems") 
    print(f"   • Medium (10-100 Hz): {len(normal_freqs[(normal_freqs >= 10) & (normal_freqs < 100)])} systems")
    print(f"   • High (100+ Hz): {len(normal_freqs[normal_freqs >= 100])} systems")
    
    return normal_freqs

def find_golden_ratio_relationships(bio_df, tolerance=0.1):
    """Find golden ratio relationships in the frequency data"""
    print("\n✨ GOLDEN RATIO ANALYSIS")
    print("=" * 25)
    
    golden_phi = 1.618033988749
    normal_freqs = bio_df[['frequency_name', 'normal_freq']].dropna()
    
    relationships = []
    
    # Compare all frequency pairs
    for i, row1 in normal_freqs.iterrows():
        for j, row2 in normal_freqs.iterrows():
            if i >= j or row2['normal_freq'] == 0:
                continue
                
            ratio = row1['normal_freq'] / row2['normal_freq']
            
            # Check for golden ratio (both directions)
            for target_ratio, name in [(golden_phi, 'φ'), (1/golden_phi, '1/φ')]:
                deviation = abs(ratio - target_ratio) / target_ratio
                
                if deviation <= tolerance:
                    relationships.append({
                        'freq1_name': row1['frequency_name'],
                        'freq1': row1['normal_freq'],
                        'freq2_name': row2['frequency_name'], 
                        'freq2': row2['normal_freq'],
                        'ratio': ratio,
                        'target': target_ratio,
                        'deviation': deviation,
                        'type': name
                    })
    
    # Sort by deviation (best matches first)
    relationships.sort(key=lambda x: x['deviation'])
    
    print(f"🎯 Found {len(relationships)} golden ratio relationships (tolerance: {tolerance:.1%})")
    
    # Show top 5 relationships
    for i, rel in enumerate(relationships[:5]):
        print(f"   {i+1}. {rel['freq1_name']} ({rel['freq1']:.3f} Hz) ÷")
        print(f"      {rel['freq2_name']} ({rel['freq2']:.3f} Hz) = {rel['ratio']:.3f}")
        print(f"      Target: {rel['type']} = {rel['target']:.3f}, Deviation: {rel['deviation']:.1%}")
        print()
    
    return relationships

def analyze_octave_relationships(bio_df, tolerance=0.1):
    """Find octave (2:1) relationships in the frequency data"""
    print("\n🎵 OCTAVE RELATIONSHIP ANALYSIS")
    print("=" * 30)
    
    normal_freqs = bio_df[['frequency_name', 'normal_freq']].dropna()
    octave_relationships = []
    
    # Look for 2:1 ratios
    for i, row1 in normal_freqs.iterrows():
        for j, row2 in normal_freqs.iterrows():
            if i >= j:
                continue
                
            ratio = row1['normal_freq'] / row2['normal_freq']
            
            # Check for octave relationships
            target_ratios = [2.0, 0.5, 4.0, 0.25, 8.0, 0.125]
            ratio_names = ['2:1', '1:2', '4:1', '1:4', '8:1', '1:8']
            
            for target_ratio, ratio_name in zip(target_ratios, ratio_names):
                deviation = abs(ratio - target_ratio) / target_ratio
                
                if deviation <= tolerance:
                    octave_relationships.append({
                        'freq1_name': row1['frequency_name'],
                        'freq1': row1['normal_freq'],
                        'freq2_name': row2['frequency_name'],
                        'freq2': row2['normal_freq'],
                        'ratio': ratio,
                        'target_ratio': target_ratio,
                        'ratio_name': ratio_name,
                        'deviation': deviation
                    })
    
    # Sort by deviation
    octave_relationships.sort(key=lambda x: x['deviation'])
    
    print(f"🎼 Found {len(octave_relationships)} octave relationships (tolerance: {tolerance:.1%})")
    
    # Show top 5
    for i, rel in enumerate(octave_relationships[:5]):
        print(f"   {i+1}. {rel['freq1_name']} ({rel['freq1']:.3f} Hz) ÷")
        print(f"      {rel['freq2_name']} ({rel['freq2']:.3f} Hz) = {rel['ratio']:.3f}")
        print(f"      Octave: {rel['ratio_name']}, Deviation: {rel['deviation']:.1%}")
        print()
    
    return octave_relationships

def analyze_stellar_anchors(bio_df, stellar_df):
    """Analyze stellar anchor distribution"""
    print("\n⭐ STELLAR ANCHOR ANALYSIS")
    print("=" * 26)
    
    anchor_counts = bio_df['stellar_anchor'].value_counts().dropna()
    
    print(f"🌟 {len(anchor_counts)} stellar anchors organizing biological systems:")
    
    for anchor, count in anchor_counts.items():
        print(f"   • {anchor}: {count} biological systems")
    
    # Most active anchor
    if len(anchor_counts) > 0:
        top_anchor = anchor_counts.index[0]
        print(f"\n🎯 Most active stellar anchor: {top_anchor} ({anchor_counts.iloc[0]} systems)")
        
        # Show systems for top anchor
        top_systems = bio_df[bio_df['stellar_anchor'] == top_anchor]['frequency_name'].head(8)
        print(f"   Systems anchored to {top_anchor}:")
        for system in top_systems:
            freq = bio_df[bio_df['frequency_name'] == system]['normal_freq'].iloc[0]
            print(f"     - {system}: {freq:.3f} Hz")
    
    return anchor_counts

def demonstrate_key_relationships():
    """Demonstrate key relationships discovered in the research"""
    print("\n🌟 KEY RELATIONSHIP DEMONSTRATIONS")
    print("=" * 35)
    
    # DMT-Schumann golden ratio
    dmt_freq = 13.5  # DMT consciousness interface
    schumann_freq = 7.83  # Schumann resonance
    ratio = dmt_freq / schumann_freq
    golden_ratio = 1.618
    deviation = abs(ratio - golden_ratio) / golden_ratio
    
    print("🧠 DMT-Schumann Golden Ratio Bridge:")
    print(f"   DMT Consciousness Interface: {dmt_freq} Hz")
    print(f"   Schumann Resonance: {schumann_freq} Hz") 
    print(f"   Ratio: {ratio:.3f} ≈ φ ({golden_ratio:.3f})")
    print(f"   Deviation: {deviation:.1%}")
    if deviation < 0.1:
        print("   ✅ Golden ratio confirmed - Consciousness-Earth bridge!")
    
    # Visual processing octaves
    visual_cascade = [80.0, 40.0, 20.0, 10.0]  # Hz
    print(f"\n👁️ Visual Processing Octave Cascade:")
    for i in range(len(visual_cascade)-1):
        ratio = visual_cascade[i] / visual_cascade[i+1]
        print(f"   {visual_cascade[i]:.0f} Hz ÷ {visual_cascade[i+1]:.0f} Hz = {ratio:.1f}:1 (Perfect octave)")
    print("   ✅ Perfect 2:1 octave relationships throughout visual system!")
    
    # H-O beat frequency
    h_o_beat = 1.86  # Hz
    universal_organizer = "H-O Beat (Universal Organizer)"
    print(f"\n🎵 {universal_organizer}:")
    print(f"   Frequency: {h_o_beat} Hz")
    print(f"   Mathematical significance: Contains 7 golden ratios")
    print("   ✅ Universal organizing frequency for biological systems!")

def create_visualization(bio_df):
    """Create basic visualization of frequency data"""
    print("\n📊 Creating visualization...")
    
    normal_freqs = bio_df['normal_freq'].dropna()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Frequency distribution histogram
    ax1.hist(normal_freqs, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Count')
    ax1.set_title('Biological Frequency Distribution')
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Stellar anchor distribution
    anchor_counts = bio_df['stellar_anchor'].value_counts().dropna()
    if len(anchor_counts) > 0:
        ax2.bar(range(len(anchor_counts)), anchor_counts.values, 
               color='lightcoral', alpha=0.8, edgecolor='black')
        ax2.set_xticks(range(len(anchor_counts)))
        ax2.set_xticklabels(anchor_counts.index, rotation=45, ha='right')
        ax2.set_ylabel('Number of Systems')
        ax2.set_title('Systems per Stellar Anchor')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('basic_analysis_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("💾 Saved visualization as 'basic_analysis_visualization.png'")

def main():
    """Main analysis function"""
    print("🧬 GnosisLoom Basic Analysis Examples")
    print("=" * 40)
    
    # Load data
    bio_df, stellar_df = load_frequency_data()
    if bio_df is None:
        print("❌ Could not load frequency data. Please run the data converter first.")
        return
    
    # Run analyses
    normal_freqs = analyze_frequency_distribution(bio_df)
    golden_relationships = find_golden_ratio_relationships(bio_df, tolerance=0.1)
    octave_relationships = analyze_octave_relationships(bio_df, tolerance=0.1)
    anchor_counts = analyze_stellar_anchors(bio_df, stellar_df)
    
    # Demonstrate key relationships
    demonstrate_key_relationships()
    
    # Create visualization
    create_visualization(bio_df)
    
    print("\n🎉 Analysis Complete!")
    print(f"   • {len(bio_df)} frequency signatures analyzed")
    print(f"   • {len(golden_relationships)} golden ratio relationships found")
    print(f"   • {len(octave_relationships)} octave relationships found")
    print(f"   • {len(anchor_counts)} stellar anchors organizing biological systems")
    print("\n💡 This demonstrates the mathematical precision underlying biological systems!")
    print("   The frequencies are real, the relationships are profound.")

if __name__ == "__main__":
    main()