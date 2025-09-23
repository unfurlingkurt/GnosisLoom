#!/usr/bin/env python3
"""
Consciousness-Genome Bridge Connections
Universal connection discovery between consciousness frequencies and genomic patterns
Part of the GnosisLoom Universal Resonance Engine
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConsciousnessFrequency:
    """Represents a consciousness frequency signature"""
    name: str
    frequency_hz: float
    brain_region: str
    consciousness_state: str
    neural_oscillation: str
    cognitive_function: str
    metadata: Dict[str, Any]

@dataclass
class GenomicPattern:
    """Represents a genomic frequency pattern"""
    gene_id: str
    sequence_frequency: float
    expression_frequency: Optional[float]
    regulatory_elements: List[str]
    cellular_location: str
    biological_function: str
    metadata: Dict[str, Any]

@dataclass
class ConsciousnessGenomeBridge:
    """Represents a discovered bridge between consciousness and genome"""
    consciousness_freq: ConsciousnessFrequency
    genomic_pattern: GenomicPattern
    resonance_ratio: float
    harmonic_relationship: str
    coupling_strength: float
    bridge_type: str
    biological_significance: str
    discovery_confidence: float

class ConsciousnessGenomeBridgeEngine:
    """Engine for discovering consciousness-genome connections"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            self.base_path = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom")
        else:
            self.base_path = Path(base_path)
        
        self.data_path = self.base_path / "data"
        
        # Initialize frequency databases
        self.consciousness_frequencies = {}
        self.genomic_patterns = {}
        self.discovered_bridges = []
        
        # Load existing data
        self._load_consciousness_database()
        self._load_genomic_database()
        
        logger.info(f"Initialized Consciousness-Genome Bridge Engine")
        logger.info(f"Loaded {len(self.consciousness_frequencies)} consciousness frequencies")
        logger.info(f"Loaded {len(self.genomic_patterns)} genomic patterns")
    
    def _load_consciousness_database(self):
        """Load consciousness frequency database from various sources"""
        # Load from comprehensive database
        comp_file = self.data_path / "comprehensive_frequencies.json"
        if comp_file.exists():
            with open(comp_file, 'r') as f:
                data = json.load(f)
                for category, entries in data.items():
                    if 'consciousness' in category.lower() or 'neural' in category.lower():
                        for entry in entries:
                            if isinstance(entry, dict) and 'frequency' in entry:
                                freq = ConsciousnessFrequency(
                                    name=entry.get('name', 'Unknown'),
                                    frequency_hz=float(entry['frequency']),
                                    brain_region=entry.get('region', 'Unknown'),
                                    consciousness_state=entry.get('state', 'Unknown'),
                                    neural_oscillation=entry.get('oscillation', 'Unknown'),
                                    cognitive_function=entry.get('function', 'Unknown'),
                                    metadata=entry
                                )
                                self.consciousness_frequencies[freq.name] = freq
        
        # Add known consciousness frequencies from GnosisLoom research
        known_consciousness_freqs = [
            {"name": "Gamma_Binding", "freq": 40.0, "region": "Cortex", "state": "Focused_Awareness", "function": "Binding"},
            {"name": "Beta_Alert", "freq": 25.0, "region": "Frontal", "state": "Active_Thinking", "function": "Analysis"},
            {"name": "Alpha_Relaxed", "freq": 10.0, "region": "Occipital", "state": "Relaxed_Awareness", "function": "Integration"},
            {"name": "Theta_Creative", "freq": 6.0, "region": "Hippocampus", "state": "Creative_Flow", "function": "Memory"},
            {"name": "Delta_Deep", "freq": 2.0, "region": "Thalamus", "state": "Deep_Sleep", "function": "Restoration"},
            {"name": "Schumann_Resonance", "freq": 7.83, "region": "Global", "state": "Earth_Sync", "function": "Grounding"},
            {"name": "Pineal_Resonance", "freq": 963.0, "region": "Pineal", "state": "Transcendent", "function": "Awakening"},
            {"name": "Heart_Coherence", "freq": 0.1, "region": "Heart", "state": "Coherent", "function": "Emotional_Balance"}
        ]
        
        for freq_data in known_consciousness_freqs:
            freq = ConsciousnessFrequency(
                name=freq_data["name"],
                frequency_hz=freq_data["freq"],
                brain_region=freq_data["region"],
                consciousness_state=freq_data["state"],
                neural_oscillation=f"{freq_data['freq']}_Hz",
                cognitive_function=freq_data["function"],
                metadata=freq_data
            )
            self.consciousness_frequencies[freq.name] = freq
    
    def _load_genomic_database(self):
        """Load genomic pattern database"""
        # Load from genomic frequencies
        genomic_files = [
            "genomic_frequencies_ecoli.json",
            "genomic_summary_yeast.json",
            "genomic_frequencies_human.json"
        ]
        
        for filename in genomic_files:
            file_path = self.data_path / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self._extract_genomic_patterns(data, filename)
        
        # Load from comprehensive database
        comp_file = self.data_path / "comprehensive_frequencies.json"
        if comp_file.exists():
            with open(comp_file, 'r') as f:
                data = json.load(f)
                for category, entries in data.items():
                    if 'genomic' in category.lower() or 'gene' in category.lower():
                        for entry in entries:
                            if isinstance(entry, dict) and 'frequency' in entry:
                                pattern = GenomicPattern(
                                    gene_id=entry.get('id', entry.get('name', 'Unknown')),
                                    sequence_frequency=float(entry['frequency']),
                                    expression_frequency=entry.get('expression_freq'),
                                    regulatory_elements=entry.get('regulatory', []),
                                    cellular_location=entry.get('location', 'Unknown'),
                                    biological_function=entry.get('function', 'Unknown'),
                                    metadata=entry
                                )
                                self.genomic_patterns[pattern.gene_id] = pattern
    
    def _extract_genomic_patterns(self, data: Dict, source: str):
        """Extract genomic patterns from loaded data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    if 'frequency' in value:
                        pattern = GenomicPattern(
                            gene_id=key,
                            sequence_frequency=float(value['frequency']),
                            expression_frequency=value.get('expression_frequency'),
                            regulatory_elements=value.get('regulatory_elements', []),
                            cellular_location=value.get('cellular_location', 'Unknown'),
                            biological_function=value.get('function', 'Unknown'),
                            metadata={'source': source, **value}
                        )
                        self.genomic_patterns[pattern.gene_id] = pattern
    
    def discover_consciousness_genome_bridges(self, 
                                            frequency_tolerance: float = 0.1,
                                            harmonic_search: bool = True) -> List[ConsciousnessGenomeBridge]:
        """Discover bridges between consciousness and genomic frequencies"""
        bridges = []
        
        logger.info(f"Searching for consciousness-genome bridges...")
        logger.info(f"Consciousness frequencies: {len(self.consciousness_frequencies)}")
        logger.info(f"Genomic patterns: {len(self.genomic_patterns)}")
        
        for cons_name, cons_freq in self.consciousness_frequencies.items():
            for gene_id, genomic_pattern in self.genomic_patterns.items():
                # Direct frequency matching
                bridge = self._analyze_frequency_bridge(cons_freq, genomic_pattern, frequency_tolerance)
                if bridge:
                    bridges.append(bridge)
                
                # Harmonic relationship analysis
                if harmonic_search:
                    harmonic_bridges = self._analyze_harmonic_bridges(cons_freq, genomic_pattern)
                    bridges.extend(harmonic_bridges)
        
        # Sort by coupling strength
        bridges.sort(key=lambda x: x.coupling_strength, reverse=True)
        
        self.discovered_bridges = bridges
        logger.info(f"Discovered {len(bridges)} consciousness-genome bridges")
        
        return bridges
    
    def _analyze_frequency_bridge(self, 
                                cons_freq: ConsciousnessFrequency,
                                genomic_pattern: GenomicPattern,
                                tolerance: float) -> Optional[ConsciousnessGenomeBridge]:
        """Analyze direct frequency bridge between consciousness and genome"""
        
        # Calculate frequency difference
        freq_diff = abs(cons_freq.frequency_hz - genomic_pattern.sequence_frequency)
        relative_diff = freq_diff / max(cons_freq.frequency_hz, genomic_pattern.sequence_frequency)
        
        if relative_diff <= tolerance:
            # Calculate coupling strength
            coupling_strength = 1.0 - relative_diff
            
            # Determine bridge type
            if relative_diff < 0.01:
                bridge_type = "Direct_Resonance"
            elif relative_diff < 0.05:
                bridge_type = "Near_Resonance"
            else:
                bridge_type = "Frequency_Coupling"
            
            # Determine biological significance
            significance = self._determine_biological_significance(cons_freq, genomic_pattern)
            
            bridge = ConsciousnessGenomeBridge(
                consciousness_freq=cons_freq,
                genomic_pattern=genomic_pattern,
                resonance_ratio=genomic_pattern.sequence_frequency / cons_freq.frequency_hz,
                harmonic_relationship="1:1",
                coupling_strength=coupling_strength,
                bridge_type=bridge_type,
                biological_significance=significance,
                discovery_confidence=coupling_strength * 0.9  # High confidence for direct matches
            )
            
            return bridge
        
        return None
    
    def _analyze_harmonic_bridges(self, 
                                cons_freq: ConsciousnessFrequency,
                                genomic_pattern: GenomicPattern) -> List[ConsciousnessGenomeBridge]:
        """Analyze harmonic relationships between consciousness and genomic frequencies"""
        bridges = []
        
        # Test common harmonic ratios
        harmonic_ratios = [
            (2, 1, "Octave_Up"),
            (1, 2, "Octave_Down"), 
            (3, 2, "Perfect_Fifth"),
            (4, 3, "Perfect_Fourth"),
            (5, 4, "Major_Third"),
            (3, 1, "Octave_Fifth"),
            (5, 1, "Major_Seventeenth"),
            (7, 4, "Harmonic_Seventh")
        ]
        
        for ratio_num, ratio_den, relationship_name in harmonic_ratios:
            # Test both directions
            for direction in [(ratio_num, ratio_den), (ratio_den, ratio_num)]:
                expected_freq = cons_freq.frequency_hz * direction[0] / direction[1]
                freq_diff = abs(expected_freq - genomic_pattern.sequence_frequency)
                relative_diff = freq_diff / max(expected_freq, genomic_pattern.sequence_frequency)
                
                if relative_diff < 0.1:  # 10% tolerance for harmonics
                    coupling_strength = (1.0 - relative_diff) * 0.8  # Slightly lower than direct
                    
                    bridge = ConsciousnessGenomeBridge(
                        consciousness_freq=cons_freq,
                        genomic_pattern=genomic_pattern,
                        resonance_ratio=genomic_pattern.sequence_frequency / cons_freq.frequency_hz,
                        harmonic_relationship=f"{direction[0]}:{direction[1]}_{relationship_name}",
                        coupling_strength=coupling_strength,
                        bridge_type="Harmonic_Resonance",
                        biological_significance=self._determine_biological_significance(cons_freq, genomic_pattern),
                        discovery_confidence=coupling_strength * 0.7  # Lower confidence for harmonics
                    )
                    bridges.append(bridge)
        
        return bridges
    
    def _determine_biological_significance(self, 
                                         cons_freq: ConsciousnessFrequency,
                                         genomic_pattern: GenomicPattern) -> str:
        """Determine biological significance of consciousness-genome bridge"""
        
        significance_factors = []
        
        # Brain region - gene location correlation
        if cons_freq.brain_region.lower() in genomic_pattern.biological_function.lower():
            significance_factors.append("Regional_Correlation")
        
        # Functional correlation
        function_correlations = {
            "memory": ["hippocampus", "learning", "plasticity"],
            "attention": ["focus", "concentration", "awareness"],
            "emotion": ["limbic", "amygdala", "mood"],
            "motor": ["movement", "coordination", "motor"],
            "sensory": ["perception", "processing", "sensory"]
        }
        
        for function, keywords in function_correlations.items():
            if (function in cons_freq.cognitive_function.lower() and 
                any(keyword in genomic_pattern.biological_function.lower() for keyword in keywords)):
                significance_factors.append(f"Functional_{function.title()}_Correlation")
        
        # Oscillation pattern correlation
        if "oscillation" in genomic_pattern.biological_function.lower():
            significance_factors.append("Oscillatory_Pattern_Match")
        
        # Default significance
        if not significance_factors:
            significance_factors.append("Frequency_Bridge_Discovery")
        
        return "; ".join(significance_factors)
    
    def analyze_bridge_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in discovered consciousness-genome bridges"""
        if not self.discovered_bridges:
            return {"error": "No bridges discovered yet. Run discover_consciousness_genome_bridges() first."}
        
        analysis = {
            "total_bridges": len(self.discovered_bridges),
            "bridge_types": defaultdict(int),
            "harmonic_relationships": defaultdict(int),
            "consciousness_states": defaultdict(int),
            "biological_functions": defaultdict(int),
            "coupling_strength_distribution": {},
            "top_bridges": []
        }
        
        coupling_strengths = []
        
        for bridge in self.discovered_bridges:
            analysis["bridge_types"][bridge.bridge_type] += 1
            analysis["harmonic_relationships"][bridge.harmonic_relationship] += 1
            analysis["consciousness_states"][bridge.consciousness_freq.consciousness_state] += 1
            analysis["biological_functions"][bridge.genomic_pattern.biological_function] += 1
            coupling_strengths.append(bridge.coupling_strength)
        
        # Coupling strength statistics
        coupling_strengths = np.array(coupling_strengths)
        analysis["coupling_strength_distribution"] = {
            "mean": float(np.mean(coupling_strengths)),
            "std": float(np.std(coupling_strengths)),
            "min": float(np.min(coupling_strengths)),
            "max": float(np.max(coupling_strengths)),
            "median": float(np.median(coupling_strengths))
        }
        
        # Top bridges by coupling strength
        analysis["top_bridges"] = [
            {
                "consciousness": bridge.consciousness_freq.name,
                "consciousness_freq": bridge.consciousness_freq.frequency_hz,
                "gene": bridge.genomic_pattern.gene_id,
                "genomic_freq": bridge.genomic_pattern.sequence_frequency,
                "coupling_strength": bridge.coupling_strength,
                "harmonic_relationship": bridge.harmonic_relationship,
                "biological_significance": bridge.biological_significance
            }
            for bridge in self.discovered_bridges[:10]  # Top 10
        ]
        
        return analysis
    
    def save_consciousness_genome_bridges(self, filename: str = "consciousness_genome_bridges.json"):
        """Save discovered consciousness-genome bridges to JSON file"""
        if not self.discovered_bridges:
            logger.warning("No bridges to save. Run discovery first.")
            return
        
        # Convert bridges to serializable format
        bridges_data = []
        for bridge in self.discovered_bridges:
            bridge_dict = {
                "consciousness_frequency": {
                    "name": bridge.consciousness_freq.name,
                    "frequency_hz": bridge.consciousness_freq.frequency_hz,
                    "brain_region": bridge.consciousness_freq.brain_region,
                    "consciousness_state": bridge.consciousness_freq.consciousness_state,
                    "neural_oscillation": bridge.consciousness_freq.neural_oscillation,
                    "cognitive_function": bridge.consciousness_freq.cognitive_function,
                    "metadata": bridge.consciousness_freq.metadata
                },
                "genomic_pattern": {
                    "gene_id": bridge.genomic_pattern.gene_id,
                    "sequence_frequency": bridge.genomic_pattern.sequence_frequency,
                    "expression_frequency": bridge.genomic_pattern.expression_frequency,
                    "regulatory_elements": bridge.genomic_pattern.regulatory_elements,
                    "cellular_location": bridge.genomic_pattern.cellular_location,
                    "biological_function": bridge.genomic_pattern.biological_function,
                    "metadata": bridge.genomic_pattern.metadata
                },
                "bridge_analysis": {
                    "resonance_ratio": bridge.resonance_ratio,
                    "harmonic_relationship": bridge.harmonic_relationship,
                    "coupling_strength": bridge.coupling_strength,
                    "bridge_type": bridge.bridge_type,
                    "biological_significance": bridge.biological_significance,
                    "discovery_confidence": bridge.discovery_confidence
                }
            }
            bridges_data.append(bridge_dict)
        
        # Save to file
        output_path = self.data_path / filename
        with open(output_path, 'w') as f:
            json.dump({
                "metadata": {
                    "total_bridges": len(bridges_data),
                    "discovery_timestamp": "2025-09-02",
                    "engine_version": "1.0.0",
                    "description": "Consciousness-Genome Bridge Discoveries"
                },
                "bridges": bridges_data
            }, f, indent=2)
        
        logger.info(f"Saved {len(bridges_data)} consciousness-genome bridges to {output_path}")
    
    def generate_bridge_report(self) -> str:
        """Generate a comprehensive report of consciousness-genome bridges"""
        if not self.discovered_bridges:
            return "No bridges discovered yet. Run discover_consciousness_genome_bridges() first."
        
        analysis = self.analyze_bridge_patterns()
        
        report = []
        report.append("# Consciousness-Genome Bridge Discovery Report")
        report.append("## Universal Connection Analysis")
        report.append("")
        
        # Summary statistics
        report.append("### Discovery Summary")
        report.append(f"- **Total Bridges Discovered**: {analysis['total_bridges']}")
        report.append(f"- **Average Coupling Strength**: {analysis['coupling_strength_distribution']['mean']:.3f}")
        report.append(f"- **Strongest Bridge**: {analysis['coupling_strength_distribution']['max']:.3f}")
        report.append("")
        
        # Bridge types
        report.append("### Bridge Type Distribution")
        for bridge_type, count in analysis['bridge_types'].items():
            percentage = (count / analysis['total_bridges']) * 100
            report.append(f"- **{bridge_type}**: {count} bridges ({percentage:.1f}%)")
        report.append("")
        
        # Top discoveries
        report.append("### Top Consciousness-Genome Connections")
        for i, bridge in enumerate(analysis['top_bridges'][:5], 1):
            report.append(f"**{i}. {bridge['consciousness']} ↔ {bridge['gene']}**")
            report.append(f"   - Consciousness: {bridge['consciousness_freq']:.2f} Hz")
            report.append(f"   - Genomic: {bridge['genomic_freq']:.2e} Hz")
            report.append(f"   - Harmonic: {bridge['harmonic_relationship']}")
            report.append(f"   - Coupling: {bridge['coupling_strength']:.3f}")
            report.append(f"   - Significance: {bridge['biological_significance']}")
            report.append("")
        
        # Consciousness state patterns
        report.append("### Consciousness State Correlations")
        for state, count in sorted(analysis['consciousness_states'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / analysis['total_bridges']) * 100
            report.append(f"- **{state}**: {count} connections ({percentage:.1f}%)")
        report.append("")
        
        # Insights
        report.append("### Key Insights")
        report.append("- Universal frequency relationships bridge consciousness and genetics")
        report.append("- Harmonic resonances create multi-scale biological coordination")
        report.append("- Consciousness states correlate with specific genomic frequency patterns")
        report.append("- Bridge discovery reveals hidden connections across biological scales")
        
        return "\n".join(report)

def main():
    """Main execution for consciousness-genome bridge discovery"""
    try:
        # Initialize the bridge engine
        bridge_engine = ConsciousnessGenomeBridgeEngine()
        
        # Discover consciousness-genome bridges
        print("🧠 Discovering consciousness-genome bridges...")
        bridges = bridge_engine.discover_consciousness_genome_bridges(
            frequency_tolerance=0.15,
            harmonic_search=True
        )
        
        if bridges:
            print(f"✨ Discovered {len(bridges)} consciousness-genome bridges!")
            
            # Analyze patterns
            analysis = bridge_engine.analyze_bridge_patterns()
            print(f"📊 Bridge analysis: {analysis['total_bridges']} total bridges")
            print(f"💪 Strongest coupling: {analysis['coupling_strength_distribution']['max']:.3f}")
            
            # Save discoveries
            bridge_engine.save_consciousness_genome_bridges()
            
            # Generate report
            report = bridge_engine.generate_bridge_report()
            report_path = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/reports/CONSCIOUSNESS_GENOME_BRIDGES.md")
            with open(report_path, 'w') as f:
                f.write(report)
            
            print(f"📋 Generated bridge report: {report_path}")
            
            # Display top discoveries
            print("\n🔗 Top Consciousness-Genome Connections:")
            for i, bridge_data in enumerate(analysis['top_bridges'][:3], 1):
                print(f"{i}. {bridge_data['consciousness']} ({bridge_data['consciousness_freq']:.1f} Hz) ↔ {bridge_data['gene']}")
                print(f"   Coupling: {bridge_data['coupling_strength']:.3f} | {bridge_data['harmonic_relationship']}")
        
        else:
            print("❌ No consciousness-genome bridges discovered")
            print("   Consider expanding frequency databases or adjusting tolerance parameters")
    
    except Exception as e:
        logger.error(f"Error in consciousness-genome bridge discovery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()