#!/usr/bin/env python3
"""
Universal Pattern Recognition System - Q-DNA Framework Extension

This module extends the Q-DNA framework to recognize frequency patterns across
ALL scientific domains, not just genomics. It leverages the Universal Resonance Engine
to discover deep relationships between physics, chemistry, biology, astronomy, and beyond.

Author: Dr. Mordin Solus (custom research persona of Claude Code)
Date: 2025-09-02
Version: 1.0.0

Core Vision:
- Apply Q-DNA 12-strand framework to any scientific domain
- Recognize universal frequency patterns across all scales
- Generate insights spanning quantum → atomic → molecular → biological → stellar
- Enable queries like: "How do solar wind frequencies affect protein folding?"
- True universal pattern recognition engine
"""

import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
from itertools import combinations

from universal_resonance_engine import (
    UniversalResonanceEngine, ResonanceEntity, FrequencySignature,
    FeedbackLoop, ScientificDomain, StellarAnchor
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of universal patterns recognized by the system."""
    FREQUENCY_RESONANCE = "frequency_resonance"
    HARMONIC_SERIES = "harmonic_series"
    CROSS_SCALE_COUPLING = "cross_scale_coupling"
    STELLAR_GRAVITATIONAL = "stellar_gravitational"
    QUANTUM_COHERENCE = "quantum_coherence"
    GOLDEN_RATIO = "golden_ratio"
    OCTAVE_CASCADE = "octave_cascade"
    FIBONACCI_SEQUENCE = "fibonacci_sequence"
    STANDING_WAVE = "standing_wave"
    BEAT_FREQUENCY = "beat_frequency"
    PHASE_TRANSITION = "phase_transition"
    EMERGENCE_THRESHOLD = "emergence_threshold"


@dataclass
class UniversalPattern:
    """Represents a discovered pattern spanning multiple domains or scales."""
    pattern_id: str
    pattern_type: PatternType
    entities: List[ResonanceEntity]
    strength: float  # 0.0-1.0
    domains_spanned: Set[ScientificDomain]
    frequency_relationship: str
    mathematical_description: str
    
    # Pattern-specific metadata
    scale_span: Tuple[float, float]  # (min_frequency, max_frequency)
    stellar_influences: List[StellarAnchor] = field(default_factory=list)
    confidence: float = 1.0
    
    # Discovery metadata
    discovery_method: str = ""
    supporting_evidence: Dict[str, Any] = field(default_factory=dict)
    
    def is_cross_domain(self) -> bool:
        """Check if pattern spans multiple scientific domains."""
        return len(self.domains_spanned) > 1
        
    def get_scale_span_orders_of_magnitude(self) -> float:
        """Calculate how many orders of magnitude the pattern spans."""
        if self.scale_span[0] == 0 or self.scale_span[1] == 0:
            return 0.0
        return math.log10(self.scale_span[1]) - math.log10(self.scale_span[0])


class QDNAUniversalStrand:
    """
    Represents one of the 12 universal strands in the extended Q-DNA framework.
    Each strand represents a different aspect of universal frequency relationships.
    """
    
    def __init__(self, strand_id: int, domain: ScientificDomain, 
                 frequency_range: Tuple[float, float], description: str):
        self.strand_id = strand_id
        self.domain = domain
        self.frequency_range = frequency_range
        self.description = description
        self.entities: List[ResonanceEntity] = []
        self.patterns: List[UniversalPattern] = []
        
    def add_entity(self, entity: ResonanceEntity):
        """Add an entity to this strand if it fits the frequency range."""
        if entity.frequency_signature is None:
            return False
            
        freq = entity.frequency_signature.primary_frequency
        if self.frequency_range[0] <= freq <= self.frequency_range[1]:
            self.entities.append(entity)
            return True
        return False
        
    def calculate_coherence(self) -> float:
        """Calculate coherence score for entities in this strand."""
        if len(self.entities) < 2:
            return 0.0
            
        frequencies = [e.frequency_signature.primary_frequency 
                      for e in self.entities if e.frequency_signature]
        
        if not frequencies:
            return 0.0
            
        # Calculate frequency distribution coherence
        mean_freq = np.mean(frequencies)
        std_freq = np.std(frequencies)
        
        # Coherence is inverse of coefficient of variation
        if mean_freq == 0:
            return 0.0
        return 1.0 / (1.0 + (std_freq / mean_freq))


class UniversalPatternRecognizer:
    """
    Main pattern recognition engine that applies Q-DNA framework to all scientific domains.
    """
    
    def __init__(self, resonance_engine: UniversalResonanceEngine):
        self.engine = resonance_engine
        self.q_dna_strands: List[QDNAUniversalStrand] = []
        self.discovered_patterns: List[UniversalPattern] = []
        
        # Initialize 12 universal strands
        self._initialize_universal_strands()
        
        logger.info("Universal Pattern Recognizer initialized with 12-strand Q-DNA framework")
        
    def _initialize_universal_strands(self):
        """Initialize the 12 universal Q-DNA strands covering all scales."""
        
        strand_definitions = [
            # Strand 1: Quantum/Subatomic (10^12 - 10^18 Hz)
            (1, ScientificDomain.QUANTUM_PHYSICS, (1e12, 1e18), "Subatomic particles and quantum fields"),
            
            # Strand 2: Atomic/Electronic (10^9 - 10^12 Hz)
            (2, ScientificDomain.PHYSICS, (1e9, 1e12), "Atomic transitions and electron orbitals"),
            
            # Strand 3: Molecular Vibrational (10^6 - 10^9 Hz) 
            (3, ScientificDomain.CHEMISTRY, (1e6, 1e9), "Molecular vibrations and chemical bonds"),
            
            # Strand 4: Cellular/Biological High (10^3 - 10^6 Hz)
            (4, ScientificDomain.BIOLOGY, (1e3, 1e6), "Cellular processes and enzyme kinetics"),
            
            # Strand 5: Neural/Physiological (1 - 10^3 Hz)
            (5, ScientificDomain.NEUROSCIENCE, (1, 1e3), "Neural oscillations and physiological rhythms"),
            
            # Strand 6: Schumann/Geophysical (0.001 - 1 Hz)
            (6, ScientificDomain.GEOPHYSICS, (0.001, 1), "Geomagnetic and atmospheric resonances"),
            
            # Strand 7: Tidal/Gravitational (10^-6 - 0.001 Hz)
            (7, ScientificDomain.ASTRONOMY, (1e-6, 0.001), "Tidal forces and gravitational waves"),
            
            # Strand 8: Solar/Stellar (10^-9 - 10^-6 Hz)
            (8, ScientificDomain.ASTRONOMY, (1e-9, 1e-6), "Solar cycles and stellar oscillations"),
            
            # Strand 9: Galactic (10^-12 - 10^-9 Hz)
            (9, ScientificDomain.ASTRONOMY, (1e-12, 1e-9), "Galactic rotation and cosmic cycles"),
            
            # Strand 10: Cosmological (10^-15 - 10^-12 Hz)
            (10, ScientificDomain.ASTRONOMY, (1e-15, 1e-12), "Universe expansion and cosmic oscillations"),
            
            # Strand 11: Materials/Crystalline (10^6 - 10^12 Hz)
            (11, ScientificDomain.MATERIALS_SCIENCE, (1e6, 1e12), "Crystal lattice vibrations and phonons"),
            
            # Strand 12: Consciousness Interface (1 - 100 Hz)
            (12, ScientificDomain.NEUROSCIENCE, (1, 100), "Consciousness emergence frequencies")
        ]
        
        for strand_def in strand_definitions:
            strand = QDNAUniversalStrand(*strand_def)
            self.q_dna_strands.append(strand)
            
    def populate_strands(self):
        """Populate Q-DNA strands with entities from the resonance engine."""
        entity_count = 0
        
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            # Try to add entity to appropriate strands
            for strand in self.q_dna_strands:
                if strand.add_entity(entity):
                    entity_count += 1
                    break  # Entity goes to first matching strand
                    
        logger.info(f"Populated Q-DNA strands with {entity_count} entities")
        
    def recognize_universal_patterns(self) -> List[UniversalPattern]:
        """Main pattern recognition method - discovers patterns across all domains."""
        self.discovered_patterns = []
        
        # Populate strands first
        self.populate_strands()
        
        # Pattern Recognition Methods
        self._recognize_harmonic_series_patterns()
        self._recognize_cross_scale_coupling_patterns()
        self._recognize_stellar_influence_patterns()
        self._recognize_golden_ratio_patterns()
        self._recognize_octave_cascade_patterns()
        self._recognize_fibonacci_patterns()
        self._recognize_beat_frequency_patterns()
        self._recognize_emergence_thresholds()
        
        # Sort by strength
        self.discovered_patterns.sort(key=lambda p: p.strength, reverse=True)
        
        logger.info(f"Discovered {len(self.discovered_patterns)} universal patterns")
        return self.discovered_patterns
        
    def _recognize_harmonic_series_patterns(self):
        """Recognize harmonic series across all entities."""
        pattern_count = 0
        
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            # Find harmonic relationships
            harmonics = self.engine.find_harmonic_relationships(entity.entity_id, tolerance=0.02)
            
            if len(harmonics) >= 2:  # At least 2 harmonics to form a pattern
                harmonic_entities = [entity] + [h[0] for h in harmonics]
                harmonic_ratios = [1.0] + [h[1] for h in harmonics]
                
                pattern = UniversalPattern(
                    pattern_id=f"harmonic_series_{pattern_count}",
                    pattern_type=PatternType.HARMONIC_SERIES,
                    entities=harmonic_entities,
                    strength=min(1.0, len(harmonics) / 5.0),  # Strength based on harmonic count
                    domains_spanned={e.domain for e in harmonic_entities},
                    frequency_relationship=f"Harmonic series: {harmonic_ratios}",
                    mathematical_description=f"f_n = {entity.frequency_signature.primary_frequency} × n",
                    scale_span=(
                        min(e.frequency_signature.primary_frequency for e in harmonic_entities if e.frequency_signature),
                        max(e.frequency_signature.primary_frequency for e in harmonic_entities if e.frequency_signature)
                    ),
                    discovery_method="harmonic_analysis",
                    supporting_evidence={"harmonic_ratios": harmonic_ratios}
                )
                
                self.discovered_patterns.append(pattern)
                pattern_count += 1
                
    def _recognize_cross_scale_coupling_patterns(self):
        """Recognize patterns that couple across multiple frequency scales."""
        pattern_count = 0
        
        # Look for entities from different strands that have frequency relationships
        for i, strand1 in enumerate(self.q_dna_strands):
            for j, strand2 in enumerate(self.q_dna_strands):
                if i >= j:  # Avoid duplicate comparisons
                    continue
                    
                # Check if strands have frequency relationships
                coupling_entities = []
                
                for entity1 in strand1.entities[:10]:  # Limit for performance
                    for entity2 in strand2.entities[:10]:
                        if (entity1.frequency_signature and entity2.frequency_signature):
                            # Check for frequency relationships
                            freq1 = entity1.frequency_signature.primary_frequency
                            freq2 = entity2.frequency_signature.primary_frequency
                            
                            # Check for simple ratios (2:1, 3:1, 5:1, etc.)
                            ratio = max(freq1, freq2) / min(freq1, freq2)
                            for simple_ratio in [2, 3, 5, 7, 11]:  # Prime ratios
                                if abs(ratio - simple_ratio) < 0.1:
                                    coupling_entities.append((entity1, entity2, simple_ratio))
                                    
                if coupling_entities:
                    all_entities = []
                    ratios = []
                    
                    for e1, e2, ratio in coupling_entities[:5]:  # Limit to 5 strongest
                        all_entities.extend([e1, e2])
                        ratios.append(ratio)
                        
                    pattern = UniversalPattern(
                        pattern_id=f"cross_scale_coupling_{pattern_count}",
                        pattern_type=PatternType.CROSS_SCALE_COUPLING,
                        entities=all_entities,
                        strength=min(1.0, len(coupling_entities) / 10.0),
                        domains_spanned={e.domain for e in all_entities},
                        frequency_relationship=f"Cross-scale ratios: {ratios}",
                        mathematical_description=f"Coupling between {strand1.description} and {strand2.description}",
                        scale_span=(strand1.frequency_range[0], strand2.frequency_range[1]),
                        discovery_method="cross_scale_analysis"
                    )
                    
                    self.discovered_patterns.append(pattern)
                    pattern_count += 1
                    
    def _recognize_stellar_influence_patterns(self):
        """Recognize patterns influenced by stellar anchors."""
        stellar_patterns = {}
        
        # Group entities by stellar anchor
        for entity in self.engine.entities.values():
            if (entity.frequency_signature and 
                entity.frequency_signature.stellar_anchor):
                
                anchor = entity.frequency_signature.stellar_anchor
                if anchor not in stellar_patterns:
                    stellar_patterns[anchor] = []
                stellar_patterns[anchor].append(entity)
                
        # Create patterns for each stellar anchor with multiple entities
        pattern_count = 0
        for anchor, entities in stellar_patterns.items():
            if len(entities) >= 3:  # Minimum for a stellar pattern
                frequencies = [e.frequency_signature.primary_frequency 
                             for e in entities if e.frequency_signature]
                
                pattern = UniversalPattern(
                    pattern_id=f"stellar_influence_{anchor.star_name}_{pattern_count}",
                    pattern_type=PatternType.STELLAR_GRAVITATIONAL,
                    entities=entities,
                    strength=min(1.0, len(entities) / 20.0),  # Strength based on entity count
                    domains_spanned={e.domain for e in entities},
                    frequency_relationship=f"All anchored to {anchor.star_name}",
                    mathematical_description=f"Stellar gravitational influence from {anchor.star_name}",
                    scale_span=(min(frequencies), max(frequencies)) if frequencies else (0, 0),
                    stellar_influences=[anchor],
                    discovery_method="stellar_anchor_analysis",
                    supporting_evidence={"anchor_star": anchor.star_name, "entity_count": len(entities)}
                )
                
                self.discovered_patterns.append(pattern)
                pattern_count += 1
                
    def _recognize_golden_ratio_patterns(self):
        """Recognize golden ratio (φ ≈ 1.618) relationships."""
        golden_ratio = 1.618033988749
        tolerance = 0.05
        pattern_count = 0
        
        entities_list = [e for e in self.engine.entities.values() if e.frequency_signature]
        
        for i in range(len(entities_list)):
            for j in range(i + 1, len(entities_list)):
                entity1, entity2 = entities_list[i], entities_list[j]
                
                freq1 = entity1.frequency_signature.primary_frequency
                freq2 = entity2.frequency_signature.primary_frequency
                
                ratio = max(freq1, freq2) / min(freq1, freq2)
                
                if abs(ratio - golden_ratio) <= tolerance:
                    pattern = UniversalPattern(
                        pattern_id=f"golden_ratio_{pattern_count}",
                        pattern_type=PatternType.GOLDEN_RATIO,
                        entities=[entity1, entity2],
                        strength=1.0 - abs(ratio - golden_ratio) / tolerance,
                        domains_spanned={entity1.domain, entity2.domain},
                        frequency_relationship=f"Golden ratio: {ratio:.3f} ≈ φ",
                        mathematical_description=f"f₁/f₂ = φ = {golden_ratio}",
                        scale_span=(min(freq1, freq2), max(freq1, freq2)),
                        discovery_method="golden_ratio_analysis",
                        supporting_evidence={"exact_ratio": ratio, "deviation": abs(ratio - golden_ratio)}
                    )
                    
                    self.discovered_patterns.append(pattern)
                    pattern_count += 1
                    
                    if pattern_count >= 10:  # Limit to avoid too many patterns
                        break
            if pattern_count >= 10:
                break
                
    def _recognize_octave_cascade_patterns(self):
        """Recognize octave cascade patterns (powers of 2)."""
        pattern_count = 0
        entities_by_log2 = {}
        
        # Group entities by log2 of their frequency (rounded)
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            freq = entity.frequency_signature.primary_frequency
            log2_freq = round(math.log2(freq), 1)  # Round to nearest 0.1
            
            if log2_freq not in entities_by_log2:
                entities_by_log2[log2_freq] = []
            entities_by_log2[log2_freq].append(entity)
            
        # Look for octave relationships (frequencies that are powers of 2 apart)
        octave_groups = []
        log2_values = sorted(entities_by_log2.keys())
        
        for i in range(len(log2_values)):
            for j in range(i + 1, len(log2_values)):
                log_diff = abs(log2_values[j] - log2_values[i])
                
                # Check if difference is close to an integer (octave relationship)
                if abs(log_diff - round(log_diff)) < 0.2:  # Within 0.2 log2 units
                    octave_entities = entities_by_log2[log2_values[i]] + entities_by_log2[log2_values[j]]
                    
                    if len(octave_entities) >= 2:
                        frequencies = [e.frequency_signature.primary_frequency 
                                     for e in octave_entities if e.frequency_signature]
                        
                        pattern = UniversalPattern(
                            pattern_id=f"octave_cascade_{pattern_count}",
                            pattern_type=PatternType.OCTAVE_CASCADE,
                            entities=octave_entities,
                            strength=min(1.0, len(octave_entities) / 10.0),
                            domains_spanned={e.domain for e in octave_entities},
                            frequency_relationship=f"Octave separation: 2^{round(log_diff)} = {2**round(log_diff)}",
                            mathematical_description=f"f₂ = f₁ × 2^{round(log_diff)}",
                            scale_span=(min(frequencies), max(frequencies)),
                            discovery_method="octave_cascade_analysis",
                            supporting_evidence={"log2_difference": log_diff, "octave_multiplier": 2**round(log_diff)}
                        )
                        
                        self.discovered_patterns.append(pattern)
                        pattern_count += 1
                        
                        if pattern_count >= 5:  # Limit octave patterns
                            return
                            
    def _recognize_fibonacci_patterns(self):
        """Recognize Fibonacci sequence relationships."""
        fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        pattern_count = 0
        tolerance = 0.1
        
        entities_list = [e for e in self.engine.entities.values() if e.frequency_signature]
        
        # Look for frequency ratios that match Fibonacci ratios
        for i in range(len(entities_list)):
            for j in range(i + 1, len(entities_list)):
                entity1, entity2 = entities_list[i], entities_list[j]
                
                freq1 = entity1.frequency_signature.primary_frequency
                freq2 = entity2.frequency_signature.primary_frequency
                
                ratio = max(freq1, freq2) / min(freq1, freq2)
                
                # Check against Fibonacci ratios
                for k in range(len(fibonacci_sequence) - 1):
                    fib_ratio = fibonacci_sequence[k + 1] / fibonacci_sequence[k]
                    
                    if abs(ratio - fib_ratio) <= tolerance:
                        pattern = UniversalPattern(
                            pattern_id=f"fibonacci_{pattern_count}",
                            pattern_type=PatternType.FIBONACCI_SEQUENCE,
                            entities=[entity1, entity2],
                            strength=1.0 - abs(ratio - fib_ratio) / tolerance,
                            domains_spanned={entity1.domain, entity2.domain},
                            frequency_relationship=f"Fibonacci ratio: {ratio:.3f} ≈ {fib_ratio:.3f}",
                            mathematical_description=f"f₁/f₂ = F_{k+1}/F_{k} = {fibonacci_sequence[k+1]}/{fibonacci_sequence[k]}",
                            scale_span=(min(freq1, freq2), max(freq1, freq2)),
                            discovery_method="fibonacci_analysis",
                            supporting_evidence={"fibonacci_numbers": [fibonacci_sequence[k], fibonacci_sequence[k+1]]}
                        )
                        
                        self.discovered_patterns.append(pattern)
                        pattern_count += 1
                        
                        if pattern_count >= 5:  # Limit Fibonacci patterns
                            return
                            
    def _recognize_beat_frequency_patterns(self):
        """Recognize beat frequency patterns between close frequencies."""
        pattern_count = 0
        entities_list = [e for e in self.engine.entities.values() if e.frequency_signature]
        
        for i in range(len(entities_list)):
            for j in range(i + 1, len(entities_list)):
                entity1, entity2 = entities_list[i], entities_list[j]
                
                freq1 = entity1.frequency_signature.primary_frequency
                freq2 = entity2.frequency_signature.primary_frequency
                
                # Beat frequency is the difference between close frequencies
                freq_diff = abs(freq1 - freq2)
                avg_freq = (freq1 + freq2) / 2
                
                # Check if frequencies are close enough to create meaningful beats
                if freq_diff / avg_freq < 0.1 and freq_diff > 0.1:  # 10% difference, minimum 0.1 Hz beat
                    
                    # Look for other entities that might resonate at the beat frequency
                    beat_freq_entities = []
                    for entity3 in entities_list:
                        if entity3 in [entity1, entity2]:
                            continue
                        freq3 = entity3.frequency_signature.primary_frequency
                        if abs(freq3 - freq_diff) / max(freq3, freq_diff) < 0.1:  # Within 10%
                            beat_freq_entities.append(entity3)
                            
                    if beat_freq_entities:  # Found entities at beat frequency
                        all_entities = [entity1, entity2] + beat_freq_entities
                        
                        pattern = UniversalPattern(
                            pattern_id=f"beat_frequency_{pattern_count}",
                            pattern_type=PatternType.BEAT_FREQUENCY,
                            entities=all_entities,
                            strength=min(1.0, len(beat_freq_entities) / 3.0),
                            domains_spanned={e.domain for e in all_entities},
                            frequency_relationship=f"Beat frequency: |{freq1:.2f} - {freq2:.2f}| = {freq_diff:.2f} Hz",
                            mathematical_description=f"f_beat = |f₁ - f₂| = {freq_diff:.2f} Hz",
                            scale_span=(min(freq_diff, min(freq1, freq2)), max(freq1, freq2)),
                            discovery_method="beat_frequency_analysis",
                            supporting_evidence={"beat_frequency": freq_diff, "source_frequencies": [freq1, freq2]}
                        )
                        
                        self.discovered_patterns.append(pattern)
                        pattern_count += 1
                        
                        if pattern_count >= 5:  # Limit beat frequency patterns
                            return
                            
    def _recognize_emergence_thresholds(self):
        """Recognize emergence thresholds where new properties appear."""
        pattern_count = 0
        
        # Group entities by orders of magnitude
        magnitude_groups = {}
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            freq = entity.frequency_signature.primary_frequency
            magnitude = round(math.log10(freq))
            
            if magnitude not in magnitude_groups:
                magnitude_groups[magnitude] = []
            magnitude_groups[magnitude].append(entity)
            
        # Look for magnitude boundaries with significant entity clusters
        for magnitude, entities in magnitude_groups.items():
            if len(entities) >= 5:  # Minimum cluster size for emergence
                
                # Check if this represents a known emergence threshold
                threshold_description = self._identify_emergence_threshold(magnitude)
                
                if threshold_description:
                    frequencies = [e.frequency_signature.primary_frequency 
                                 for e in entities if e.frequency_signature]
                    
                    pattern = UniversalPattern(
                        pattern_id=f"emergence_threshold_{pattern_count}",
                        pattern_type=PatternType.EMERGENCE_THRESHOLD,
                        entities=entities,
                        strength=min(1.0, len(entities) / 20.0),
                        domains_spanned={e.domain for e in entities},
                        frequency_relationship=f"Emergence at ~10^{magnitude} Hz",
                        mathematical_description=f"Threshold emergence: {threshold_description}",
                        scale_span=(min(frequencies), max(frequencies)),
                        discovery_method="emergence_threshold_analysis",
                        supporting_evidence={"magnitude": magnitude, "entity_count": len(entities)}
                    )
                    
                    self.discovered_patterns.append(pattern)
                    pattern_count += 1
                    
    def _identify_emergence_threshold(self, magnitude: int) -> Optional[str]:
        """Identify known emergence thresholds by frequency magnitude."""
        thresholds = {
            15: "Quantum field fluctuations",
            12: "Molecular bond formation",
            9: "Atomic transitions",
            6: "Cellular processes",
            3: "Neural networks",
            0: "Physiological rhythms",
            -3: "Ecological cycles",
            -6: "Geological processes",
            -9: "Stellar oscillations",
            -12: "Galactic dynamics"
        }
        return thresholds.get(magnitude)
        
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all discovered patterns."""
        if not self.discovered_patterns:
            self.recognize_universal_patterns()
            
        summary = {
            "total_patterns": len(self.discovered_patterns),
            "patterns_by_type": {},
            "cross_domain_patterns": 0,
            "strongest_patterns": [],
            "scale_span_analysis": {},
            "strand_coherence": {}
        }
        
        # Analyze patterns by type
        for pattern in self.discovered_patterns:
            pattern_type = pattern.pattern_type.value
            if pattern_type not in summary["patterns_by_type"]:
                summary["patterns_by_type"][pattern_type] = 0
            summary["patterns_by_type"][pattern_type] += 1
            
            if pattern.is_cross_domain():
                summary["cross_domain_patterns"] += 1
                
        # Get strongest patterns
        summary["strongest_patterns"] = [
            {
                "pattern_id": p.pattern_id,
                "type": p.pattern_type.value,
                "strength": p.strength,
                "domains": [d.value for d in p.domains_spanned],
                "scale_span_orders": p.get_scale_span_orders_of_magnitude()
            }
            for p in self.discovered_patterns[:10]
        ]
        
        # Analyze scale spans
        scale_spans = [p.get_scale_span_orders_of_magnitude() for p in self.discovered_patterns]
        if scale_spans:
            summary["scale_span_analysis"] = {
                "max_span": max(scale_spans),
                "avg_span": np.mean(scale_spans),
                "patterns_spanning_10plus_orders": sum(1 for span in scale_spans if span >= 10)
            }
            
        # Analyze strand coherence
        for strand in self.q_dna_strands:
            summary["strand_coherence"][f"strand_{strand.strand_id}_{strand.domain.value}"] = {
                "entity_count": len(strand.entities),
                "coherence_score": strand.calculate_coherence(),
                "frequency_range": strand.frequency_range
            }
            
        return summary
        
    def export_patterns(self, filename: str = "universal_patterns.json"):
        """Export discovered patterns to JSON file."""
        if not self.discovered_patterns:
            self.recognize_universal_patterns()
            
        export_data = {
            "metadata": {
                "total_patterns": len(self.discovered_patterns),
                "generation_timestamp": "2025-09-02",
                "q_dna_strands": len(self.q_dna_strands)
            },
            "patterns": []
        }
        
        for pattern in self.discovered_patterns:
            pattern_data = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type.value,
                "strength": pattern.strength,
                "confidence": pattern.confidence,
                "domains_spanned": [d.value for d in pattern.domains_spanned],
                "entity_count": len(pattern.entities),
                "frequency_relationship": pattern.frequency_relationship,
                "mathematical_description": pattern.mathematical_description,
                "scale_span": pattern.scale_span,
                "scale_span_orders": pattern.get_scale_span_orders_of_magnitude(),
                "stellar_influences": [s.star_name for s in pattern.stellar_influences],
                "discovery_method": pattern.discovery_method,
                "supporting_evidence": pattern.supporting_evidence
            }
            export_data["patterns"].append(pattern_data)
            
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
            
        logger.info(f"Exported {len(self.discovered_patterns)} patterns to {filename}")
        return filename


if __name__ == "__main__":
    # Example usage
    from universal_resonance_engine import UniversalResonanceEngine
    from gnosisloom_data_integrator import GnosisLoomDataIntegrator
    
    print("=== Universal Pattern Recognition System ===")
    
    # Initialize the system
    print("Initializing Universal Resonance Engine...")
    integrator = GnosisLoomDataIntegrator()
    integrator.integrate_all_databases()
    
    engine = integrator.get_engine()
    
    print("Initializing Pattern Recognizer...")
    recognizer = UniversalPatternRecognizer(engine)
    
    # Recognize patterns
    print("Recognizing universal patterns...")
    patterns = recognizer.recognize_universal_patterns()
    
    print(f"\n=== Pattern Recognition Results ===")
    print(f"Total patterns discovered: {len(patterns)}")
    
    # Show top patterns
    print("\nTop 5 Strongest Patterns:")
    for i, pattern in enumerate(patterns[:5]):
        print(f"{i+1}. {pattern.pattern_id}")
        print(f"   Type: {pattern.pattern_type.value}")
        print(f"   Strength: {pattern.strength:.3f}")
        print(f"   Domains: {[d.value for d in pattern.domains_spanned]}")
        print(f"   Scale span: {pattern.get_scale_span_orders_of_magnitude():.1f} orders of magnitude")
        print(f"   Description: {pattern.mathematical_description}")
        print()
        
    # Get summary
    summary = recognizer.get_pattern_summary()
    print("Pattern Summary:")
    for key, value in summary.items():
        if key not in ["strongest_patterns", "strand_coherence"]:
            print(f"  {key}: {value}")
            
    # Export patterns
    export_file = recognizer.export_patterns("discovered_universal_patterns.json")
    print(f"\nPatterns exported to: {export_file}")