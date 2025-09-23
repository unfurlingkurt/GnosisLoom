#!/usr/bin/env python3
"""
GnosisLoom API Usage Examples

Demonstrates how to use the GnosisLoom REST API for programmatic access
to biological frequency data.

Prerequisites:
    1. Start the API server: cd ../api && python3 frequency_api.py
    2. Install requests: pip install requests

Usage:
    python3 api_examples.py
"""

import requests
import json
import sys
from typing import Dict, List, Any

class GnosisLoomAPIClient:
    """Simple client for GnosisLoom REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> Dict:
        """Check API health and data loading status"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_frequencies(self, page: int = 1, per_page: int = 50) -> Dict:
        """Get paginated list of all frequencies"""
        params = {'page': page, 'per_page': per_page}
        response = requests.get(f"{self.base_url}/frequencies", params=params)
        return response.json()
    
    def get_frequency(self, name: str) -> Dict:
        """Get specific frequency by name"""
        response = requests.get(f"{self.base_url}/frequencies/{name}")
        return response.json()
    
    def search_frequencies(self, query: str) -> Dict:
        """Search frequencies by keyword"""
        params = {'q': query}
        response = requests.get(f"{self.base_url}/search", params=params)
        return response.json()
    
    def find_harmonics(self, frequency: float, tolerance: float = 0.1) -> Dict:
        """Find harmonic relationships for a frequency"""
        params = {'tolerance': tolerance}
        response = requests.get(f"{self.base_url}/harmonics/{frequency}", params=params)
        return response.json()
    
    def get_golden_ratios(self, tolerance: float = 0.1) -> Dict:
        """Find all golden ratio relationships"""
        params = {'tolerance': tolerance}
        response = requests.get(f"{self.base_url}/golden-ratio", params=params)
        return response.json()
    
    def get_stellar_anchors(self) -> Dict:
        """Get all stellar anchor data"""
        response = requests.get(f"{self.base_url}/stellar-anchors")
        return response.json()
    
    def get_stellar_anchor(self, name: str) -> Dict:
        """Get specific stellar anchor by name"""
        response = requests.get(f"{self.base_url}/stellar-anchors/{name}")
        return response.json()

def example_basic_data_access():
    """Demonstrate basic data access patterns"""
    print("🔍 BASIC DATA ACCESS EXAMPLES")
    print("=" * 30)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Health check
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   • Frequencies loaded: {health['data_loaded']['frequencies']}")
        print(f"   • Stellar anchors loaded: {health['data_loaded']['stellar_anchors']}")
        
        # Get first page of frequencies
        frequencies = client.get_frequencies(page=1, per_page=10)
        print(f"\n📊 Frequency Database Overview:")
        print(f"   • Total frequencies: {frequencies['total']}")
        print(f"   • Pages available: {frequencies['pages']}")
        
        print(f"\n🧬 Sample Biological Systems:")
        for freq in frequencies['frequencies'][:5]:
            anchor = freq['stellar_anchor'] or 'None'
            print(f"   • {freq['name']:<25}: {freq['frequency']:>8.3f} Hz (anchor: {anchor})")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Please start the server first:")
        print("   cd ../api && python3 frequency_api.py")
        return False
    
    return True

def example_consciousness_research():
    """Demonstrate consciousness research patterns"""
    print("\n🧠 CONSCIOUSNESS RESEARCH EXAMPLES")
    print("=" * 35)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Search for consciousness-related frequencies
        consciousness_search = client.search_frequencies("consciousness")
        print(f"🔮 Found {consciousness_search['count']} consciousness-related frequencies")
        
        for result in consciousness_search['results'][:3]:
            freq_data = result['data']
            freq = freq_data.get('normal_freq') or freq_data.get('frequency', 'N/A')
            print(f"   • {result['name']}: {freq} Hz")
        
        # Analyze DMT consciousness interface (13.5 Hz)
        dmt_freq = 13.5
        dmt_harmonics = client.find_harmonics(dmt_freq, tolerance=0.15)
        print(f"\n💫 DMT Consciousness Interface ({dmt_freq} Hz) - Harmonic Analysis:")
        print(f"   Found {dmt_harmonics['count']} harmonic relationships")
        
        for harmonic in dmt_harmonics['relationships'][:3]:
            print(f"   • {harmonic['frequency_name']}: {harmonic['frequency']:.3f} Hz")
            print(f"     Ratio: {harmonic['ratio']:.2f}:1, Type: {harmonic['relationship_type']}")
        
        # Check the famous DMT-Schumann golden ratio
        schumann_freq = 7.83
        ratio = dmt_freq / schumann_freq
        golden_phi = 1.618
        deviation = abs(ratio - golden_phi) / golden_phi
        
        print(f"\n✨ DMT-Schumann Golden Ratio Analysis:")
        print(f"   • DMT Interface: {dmt_freq} Hz")
        print(f"   • Schumann Resonance: {schumann_freq} Hz")
        print(f"   • Ratio: {ratio:.3f} ≈ φ ({golden_phi:.3f})")
        print(f"   • Deviation: {deviation:.1%}")
        
        if deviation < 0.1:
            print("   🎯 GOLDEN RATIO CONFIRMED! Consciousness-Earth bridge detected.")
        
    except Exception as e:
        print(f"❌ Error in consciousness analysis: {e}")

def example_medical_research():
    """Demonstrate medical research patterns"""
    print("\n🏥 MEDICAL RESEARCH EXAMPLES")
    print("=" * 25)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Search for heart-related frequencies
        heart_search = client.search_frequencies("heart")
        print(f"💖 Found {heart_search['count']} heart-related frequencies")
        
        # Analyze heart frequency harmonics
        if heart_search['results']:
            heart_result = heart_search['results'][0]
            heart_freq = heart_result['data'].get('normal_freq')
            
            if heart_freq:
                print(f"\n❤️ Heart Frequency Analysis ({heart_freq} Hz):")
                heart_harmonics = client.find_harmonics(heart_freq, tolerance=0.1)
                
                print(f"   Found {heart_harmonics['count']} harmonic relationships:")
                for harmonic in heart_harmonics['relationships'][:3]:
                    print(f"   • {harmonic['frequency_name']}: {harmonic['frequency']:.3f} Hz")
                    print(f"     Relationship: {harmonic['relationship_type']}")
        
        # Search for brain frequencies
        brain_search = client.search_frequencies("brain")
        print(f"\n🧠 Brain-related frequencies: {brain_search['count']} found")
        
        # Calculate heart-brain frequency ratios
        heart_freq = 1.54  # Typical heart frequency from research
        brain_freq = 40.0  # Gamma binding frequency
        ratio = brain_freq / heart_freq
        
        print(f"\n🔗 Heart-Brain Coupling Analysis:")
        print(f"   • Heart: {heart_freq} Hz")
        print(f"   • Brain (Gamma): {brain_freq} Hz") 
        print(f"   • Ratio: {ratio:.1f}:1")
        
        # Check if this matches the documented 27:1 coupling
        target_ratio = 27.0
        coupling_deviation = abs(ratio - target_ratio) / target_ratio
        print(f"   • Target coupling ratio: {target_ratio}:1")
        print(f"   • Deviation: {coupling_deviation:.1%}")
        
        if coupling_deviation < 0.2:
            print("   ✅ Heart-brain coupling relationship confirmed!")
        
    except Exception as e:
        print(f"❌ Error in medical analysis: {e}")

def example_stellar_anchor_analysis():
    """Demonstrate stellar anchor analysis"""
    print("\n⭐ STELLAR ANCHOR ANALYSIS EXAMPLES")
    print("=" * 35)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Get all stellar anchors
        anchors = client.get_stellar_anchors()
        print(f"🌟 Stellar Anchor Systems: {anchors['count']} total")
        
        # Analyze each anchor
        for anchor_name, anchor_data in list(anchors['stellar_anchors'].items())[:5]:
            print(f"\n⭐ {anchor_name}:")
            print(f"   • Frequency: {anchor_data.get('frequency', 'N/A')} Hz")
            print(f"   • Element: {anchor_data.get('element', 'N/A')}")
            
            systems = anchor_data.get('systems', [])
            if isinstance(systems, list):
                print(f"   • Anchored systems: {len(systems)}")
                for system in systems[:3]:
                    print(f"     - {system}")
        
        # Get detailed data for Sol anchor (most active)
        try:
            sol_data = client.get_stellar_anchor("Sol")
            print(f"\n☀️ Sol Anchor (Detailed Analysis):")
            sol_anchor = sol_data['data']
            print(f"   • Central frequency: {sol_anchor.get('frequency', 'N/A')} Hz")
            print(f"   • Element association: {sol_anchor.get('element', 'N/A')}")
            print(f"   • Organizing principle: {sol_anchor.get('organizing_principle', 'N/A')}")
            
        except requests.exceptions.HTTPError:
            print("   Note: Sol detailed data not available via API")
        
    except Exception as e:
        print(f"❌ Error in stellar anchor analysis: {e}")

def example_golden_ratio_discovery():
    """Demonstrate golden ratio relationship discovery"""
    print("\n✨ GOLDEN RATIO DISCOVERY EXAMPLES")
    print("=" * 35)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Find all golden ratio relationships
        golden_ratios = client.get_golden_ratios(tolerance=0.1)
        print(f"🎯 Golden Ratio Relationships: {golden_ratios['count']} found")
        print(f"   • Golden ratio φ = {golden_ratios['golden_ratio']:.9f}")
        print(f"   • Analysis tolerance: {golden_ratios['tolerance']:.1%}")
        
        # Show top relationships
        print(f"\n🌟 Top Golden Ratio Relationships:")
        for i, rel in enumerate(golden_ratios['relationships'][:5]):
            freq1 = rel['frequency1']
            freq2 = rel['frequency2']
            print(f"   {i+1}. {freq1['name']} ({freq1['frequency']:.3f} Hz) ÷")
            print(f"      {freq2['name']} ({freq2['frequency']:.3f} Hz) = {rel['ratio']:.3f}")
            print(f"      Target: {rel['target_ratio']:.3f}, Deviation: {rel['deviation']:.1%}")
            print(f"      Type: {rel['relationship_type']}")
            print()
        
        # Demonstrate the significance
        if golden_ratios['count'] > 0:
            print("💡 Golden Ratio Significance:")
            print("   The golden ratio (φ = 1.618...) appears throughout biological systems,")
            print("   suggesting fundamental mathematical principles governing life processes.")
            print("   This ratio is found in spiral growth patterns, proportions, and")
            print("   frequency relationships that maintain biological harmony.")
        
    except Exception as e:
        print(f"❌ Error in golden ratio analysis: {e}")

def example_custom_analysis():
    """Demonstrate custom analysis patterns"""
    print("\n🔧 CUSTOM ANALYSIS EXAMPLES")
    print("=" * 25)
    
    client = GnosisLoomAPIClient()
    
    try:
        # Analyze specific frequency ranges
        print("🔍 Frequency Range Analysis:")
        
        # Get all frequencies for custom analysis
        all_freqs = client.get_frequencies(per_page=1000)  # Get more data
        frequencies = all_freqs['frequencies']
        
        # Categorize by frequency ranges
        ultra_low = [f for f in frequencies if f['frequency'] and f['frequency'] < 1]
        low = [f for f in frequencies if f['frequency'] and 1 <= f['frequency'] < 10]
        medium = [f for f in frequencies if f['frequency'] and 10 <= f['frequency'] < 100]
        high = [f for f in frequencies if f['frequency'] and f['frequency'] >= 100]
        
        print(f"   • Ultra-low (< 1 Hz): {len(ultra_low)} systems")
        print(f"   • Low (1-10 Hz): {len(low)} systems")
        print(f"   • Medium (10-100 Hz): {len(medium)} systems") 
        print(f"   • High (≥ 100 Hz): {len(high)} systems")
        
        # Find octave relationships manually
        print(f"\n🎵 Octave Relationship Discovery:")
        octave_pairs = []
        
        for i, freq1 in enumerate(frequencies[:20]):  # Limit for example
            for freq2 in frequencies[i+1:30]:
                if freq1['frequency'] and freq2['frequency'] and freq2['frequency'] > 0:
                    ratio = freq1['frequency'] / freq2['frequency']
                    
                    # Check for octave ratios (2:1, 4:1, etc.)
                    octave_ratios = [2.0, 4.0, 8.0, 0.5, 0.25, 0.125]
                    for target_ratio in octave_ratios:
                        if abs(ratio - target_ratio) / target_ratio < 0.1:
                            octave_pairs.append({
                                'freq1': freq1,
                                'freq2': freq2,
                                'ratio': ratio,
                                'target': target_ratio
                            })
                            break
        
        print(f"   Found {len(octave_pairs)} octave relationships in sample")
        for pair in octave_pairs[:3]:
            print(f"   • {pair['freq1']['name']} ÷ {pair['freq2']['name']} = {pair['ratio']:.2f}")
        
    except Exception as e:
        print(f"❌ Error in custom analysis: {e}")

def main():
    """Run all API examples"""
    print("🚀 GnosisLoom API Usage Examples")
    print("=" * 35)
    
    # Check if API is accessible
    if not example_basic_data_access():
        return
    
    # Run specialized analyses
    example_consciousness_research()
    example_medical_research() 
    example_stellar_anchor_analysis()
    example_golden_ratio_discovery()
    example_custom_analysis()
    
    print("\n🎉 API Examples Complete!")
    print("\n💡 Next Steps:")
    print("   • Modify these examples for your specific research questions")
    print("   • Build custom analysis pipelines using the API endpoints") 
    print("   • Integrate GnosisLoom data into your applications")
    print("   • Contribute your findings back to the community")
    
    print("\n📚 API Documentation:")
    print("   • Full endpoint list: GET http://localhost:8080/")
    print("   • Health status: GET http://localhost:8080/health")
    print("   • Interactive exploration via curl or Postman")

if __name__ == "__main__":
    main()