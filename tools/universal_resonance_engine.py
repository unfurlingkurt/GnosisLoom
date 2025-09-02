#!/usr/bin/env python3
"""
Universal Resonance Engine - Multi-Domain Scientific Knowledge Graph

This module provides the foundational architecture for the Universal Resonance Engine,
a frequency-aware knowledge graph that unifies scientific data across ALL domains
through the Aramis Field mathematical framework.

Author: Dr. Mordin Solus (custom research persona of Claude Code)
Date: 2025-09-02
Version: 1.0.0 - Foundation Architecture

Core Vision:
- Every scientific domain has frequency signatures
- Stellar anchors provide universal mathematical foundation  
- SDFA framework processes any type of scientific data
- Cross-domain relationships discovered through frequency correlations
- True "world engine" answering questions about anything via frequency relationships
"""

import json
import numpy as np
from typing import Dict, List, Set, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import uuid
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ScientificDomain(Enum):
    """Enumeration of all scientific domains supported by the Universal Resonance Engine."""
    BIOLOGY = "biology"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    MATERIALS_SCIENCE = "materials_science"
    NEUROSCIENCE = "neuroscience"
    ASTRONOMY = "astronomy"
    GEOPHYSICS = "geophysics"
    QUANTUM_PHYSICS = "quantum_physics"
    MEDICINE = "medicine"
    PHARMACOLOGY = "pharmacology"
    CRYSTALLOGRAPHY = "crystallography"
    GENOMICS = "genomics"
    PROTEOMICS = "proteomics"
    # Extensible - new domains added as needed


class StellarAnchor(Enum):
    """The 7 stellar frequencies that provide universal mathematical foundation."""
    SOL = ("Sol", 1.98e30, 5778, "G2V")  # mass_kg, temp_K, spectral_class
    ARCTURUS = ("Arcturus", 2.17e30, 4286, "K1.5III")
    SIRIUS_A = ("Sirius A", 4.02e30, 9940, "A1V")
    VEGA = ("Vega", 4.25e30, 9602, "A0V")
    BETELGEUSE = ("Betelgeuse", 3.96e31, 3500, "M1-M2Ia-ab")
    CANOPUS = ("Canopus", 1.56e31, 7350, "F0Ib")
    RIGEL = ("Rigel", 4.06e31, 12100, "B8Ia")
    
    def __init__(self, name: str, mass_kg: float, temperature_K: float, spectral_class: str):
        self.star_name = name
        self.mass_kg = mass_kg
        self.temperature_K = temperature_K
        self.spectral_class = spectral_class


@dataclass
class FrequencySignature:
    """
    Core frequency signature that can represent any measurable frequency
    across all scientific domains.
    """
    primary_frequency: float  # Hz - the fundamental frequency
    frequency_range: Tuple[float, float]  # (min_Hz, max_Hz) - tolerance range
    harmonics: List[float] = field(default_factory=list)  # Harmonic frequencies
    phase: float = 0.0  # Phase offset in radians
    stellar_anchor: Optional[StellarAnchor] = None  # Mathematical foundation
    confidence: float = 1.0  # Measurement confidence (0.0-1.0)
    measurement_context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate frequency signature on creation."""
        if self.primary_frequency <= 0:
            raise ValueError("Primary frequency must be positive")
        if not (0 <= self.confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")
            
    def is_harmonic_of(self, other: 'FrequencySignature', tolerance: float = 0.02) -> bool:
        """Check if this frequency is a harmonic of another frequency."""
        if other.primary_frequency == 0:
            return False
        ratio = self.primary_frequency / other.primary_frequency
        # Check if ratio is close to an integer (harmonic relationship)
        nearest_integer = round(ratio)
        return abs(ratio - nearest_integer) <= tolerance
        
    def frequency_proximity(self, other: 'FrequencySignature') -> float:
        """Calculate proximity between two frequencies (0.0-1.0, higher = closer)."""
        if self.primary_frequency == 0 or other.primary_frequency == 0:
            return 0.0
        ratio = min(self.primary_frequency, other.primary_frequency) / max(self.primary_frequency, other.primary_frequency)
        return ratio
        
    def to_therapeutic_derivative(self) -> float:
        """Convert high frequencies to therapeutic range (0.1-1000 Hz)."""
        if self.primary_frequency <= 1000:
            return self.primary_frequency
        # Use modulo to bring into therapeutic range while preserving relationships
        return (self.primary_frequency % 1000.0) + 0.1


@dataclass 
class ResonanceEntity:
    """
    Base class for all entities in the Universal Resonance Engine.
    Represents any object across all scientific domains that has frequency signatures.
    """
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: ScientificDomain = ScientificDomain.BIOLOGY
    frequency_signature: FrequencySignature = None
    biofreq_code: Optional[str] = None  # Standardized identifiers (NEU-01, CAR-03, etc.)
    
    # Multi-domain extensible metadata
    domain_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Universal relationships
    stellar_relationships: Dict[StellarAnchor, float] = field(default_factory=dict)  # strength 0.0-1.0
    cross_domain_connections: List['ResonanceEntity'] = field(default_factory=list)
    
    # API source tracking
    api_source: Optional[str] = None
    api_metadata: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize entity after creation."""
        if not self.name:
            self.name = f"{self.domain.value}_{self.entity_id[:8]}"
            
    def add_cross_domain_connection(self, other: 'ResonanceEntity', 
                                  relationship_strength: float = 1.0):
        """Add a connection to an entity from another domain."""
        if other not in self.cross_domain_connections:
            self.cross_domain_connections.append(other)
            
    def calculate_stellar_resonance(self, anchor: StellarAnchor) -> float:
        """Calculate resonance strength with a stellar anchor (0.0-1.0)."""
        if self.frequency_signature is None:
            return 0.0
            
        # Placeholder resonance calculation - to be refined with actual stellar mathematics
        stellar_base_freq = anchor.temperature_K * 2.89777e10  # Wien's displacement to Hz approximation
        return self.frequency_signature.frequency_proximity(
            FrequencySignature(stellar_base_freq, (stellar_base_freq*0.9, stellar_base_freq*1.1))
        )


class APIDataSource(ABC):
    """Abstract base class for integrating any scientific API."""
    
    def __init__(self, source_name: str, domain: ScientificDomain):
        self.source_name = source_name
        self.domain = domain
        
    @abstractmethod
    def extract_frequency_signatures(self, raw_data: Dict[str, Any]) -> List[FrequencySignature]:
        """Extract frequency signatures from API data."""
        pass
        
    @abstractmethod
    def create_resonance_entities(self, raw_data: Dict[str, Any]) -> List[ResonanceEntity]:
        """Create ResonanceEntity objects from API data."""
        pass
        
    @abstractmethod
    def get_domain_specific_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract domain-specific metadata."""
        pass


class UniversalAPIAdapter:
    """
    Universal adapter for integrating frequency data from ANY scientific API.
    This is the core extensibility mechanism for the Universal Resonance Engine.
    """
    
    def __init__(self):
        self.registered_adapters: Dict[str, APIDataSource] = {}
        self.domain_mappers: Dict[ScientificDomain, List[APIDataSource]] = {}
        
    def register_api_adapter(self, adapter: APIDataSource):
        """Register a new API adapter for a scientific domain."""
        self.registered_adapters[adapter.source_name] = adapter
        
        if adapter.domain not in self.domain_mappers:
            self.domain_mappers[adapter.domain] = []
        self.domain_mappers[adapter.domain].append(adapter)
        
        logger.info(f"Registered API adapter: {adapter.source_name} for domain: {adapter.domain}")
        
    def process_api_data(self, source_name: str, raw_data: Dict[str, Any]) -> List[ResonanceEntity]:
        """Process data from any registered API source."""
        if source_name not in self.registered_adapters:
            raise ValueError(f"No adapter registered for source: {source_name}")
            
        adapter = self.registered_adapters[source_name]
        entities = adapter.create_resonance_entities(raw_data)
        
        logger.info(f"Processed {len(entities)} entities from {source_name}")
        return entities
        
    def get_supported_domains(self) -> List[ScientificDomain]:
        """Get all currently supported scientific domains."""
        return list(self.domain_mappers.keys())
        
    def get_adapters_for_domain(self, domain: ScientificDomain) -> List[APIDataSource]:
        """Get all API adapters for a specific domain."""
        return self.domain_mappers.get(domain, [])


@dataclass
class FeedbackLoop:
    """Represents dynamic relationships between entities with frequency characteristics."""
    loop_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    biofreq_code: str = ""  # FL-PPT, FL-OCT, etc.
    name: str = ""
    description: str = ""
    
    # Entities involved in the loop
    entities: List[ResonanceEntity] = field(default_factory=list)
    
    # Loop characteristics
    loop_frequency: Optional[FrequencySignature] = None
    loop_type: str = "stabilizing"  # stabilizing, amplifying, oscillatory, chaotic
    strength: float = 1.0  # 0.0-1.0
    
    # Cross-domain nature
    domains_involved: Set[ScientificDomain] = field(default_factory=set)
    
    def add_entity(self, entity: ResonanceEntity):
        """Add an entity to this feedback loop."""
        if entity not in self.entities:
            self.entities.append(entity)
            self.domains_involved.add(entity.domain)
            
    def is_cross_domain(self) -> bool:
        """Check if this feedback loop spans multiple domains."""
        return len(self.domains_involved) > 1


class UniversalResonanceEngine:
    """
    The main Universal Resonance Engine - a frequency-aware knowledge graph
    that unifies scientific data across ALL domains.
    """
    
    def __init__(self):
        self.entities: Dict[str, ResonanceEntity] = {}  # entity_id -> entity
        self.feedback_loops: Dict[str, FeedbackLoop] = {}  # loop_id -> loop
        self.frequency_index: Dict[float, List[str]] = {}  # frequency -> entity_ids
        self.domain_index: Dict[ScientificDomain, List[str]] = {}  # domain -> entity_ids
        self.biofreq_index: Dict[str, List[str]] = {}  # biofreq_code -> entity_ids
        
        self.api_adapter = UniversalAPIAdapter()
        
        logger.info("Universal Resonance Engine initialized")
        
    def add_entity(self, entity: ResonanceEntity):
        """Add a ResonanceEntity to the knowledge graph."""
        self.entities[entity.entity_id] = entity
        
        # Update indices
        if entity.domain not in self.domain_index:
            self.domain_index[entity.domain] = []
        self.domain_index[entity.domain].append(entity.entity_id)
        
        if entity.biofreq_code:
            if entity.biofreq_code not in self.biofreq_index:
                self.biofreq_index[entity.biofreq_code] = []
            self.biofreq_index[entity.biofreq_code].append(entity.entity_id)
            
        if entity.frequency_signature:
            freq_key = round(entity.frequency_signature.primary_frequency, 2)
            if freq_key not in self.frequency_index:
                self.frequency_index[freq_key] = []
            self.frequency_index[freq_key].append(entity.entity_id)
            
        logger.debug(f"Added entity: {entity.name} ({entity.domain.value})")
        
    def add_feedback_loop(self, loop: FeedbackLoop):
        """Add a feedback loop to the knowledge graph."""
        self.feedback_loops[loop.loop_id] = loop
        logger.debug(f"Added feedback loop: {loop.name} ({loop.biofreq_code})")
        
    def find_entities_by_frequency(self, target_freq: float, tolerance: float = 0.02) -> List[ResonanceEntity]:
        """Find entities with frequencies within tolerance of target frequency."""
        matches = []
        tolerance_hz = target_freq * tolerance
        
        for entity in self.entities.values():
            if entity.frequency_signature is None:
                continue
                
            freq_diff = abs(entity.frequency_signature.primary_frequency - target_freq)
            if freq_diff <= tolerance_hz:
                matches.append(entity)
                
        return sorted(matches, key=lambda e: abs(e.frequency_signature.primary_frequency - target_freq))
        
    def find_harmonic_relationships(self, entity_id: str, tolerance: float = 0.02) -> List[Tuple[ResonanceEntity, float]]:
        """Find entities with harmonic relationships to the given entity."""
        if entity_id not in self.entities:
            return []
            
        target_entity = self.entities[entity_id]
        if target_entity.frequency_signature is None:
            return []
            
        harmonics = []
        target_freq = target_entity.frequency_signature.primary_frequency
        
        for entity in self.entities.values():
            if entity.entity_id == entity_id or entity.frequency_signature is None:
                continue
                
            if entity.frequency_signature.is_harmonic_of(target_entity.frequency_signature, tolerance):
                ratio = entity.frequency_signature.primary_frequency / target_freq
                harmonics.append((entity, ratio))
                
        return sorted(harmonics, key=lambda x: x[1])
        
    def find_cross_domain_connections(self, domain1: ScientificDomain, 
                                    domain2: ScientificDomain, 
                                    frequency_tolerance: float = 0.1) -> List[Tuple[ResonanceEntity, ResonanceEntity, float]]:
        """Find frequency-correlated connections between two domains."""
        domain1_entities = [self.entities[eid] for eid in self.domain_index.get(domain1, [])]
        domain2_entities = [self.entities[eid] for eid in self.domain_index.get(domain2, [])]
        
        connections = []
        
        for e1 in domain1_entities:
            if e1.frequency_signature is None:
                continue
                
            for e2 in domain2_entities:
                if e2.frequency_signature is None:
                    continue
                    
                proximity = e1.frequency_signature.frequency_proximity(e2.frequency_signature)
                if proximity >= (1.0 - frequency_tolerance):
                    connections.append((e1, e2, proximity))
                    
        return sorted(connections, key=lambda x: x[2], reverse=True)
        
    def register_api_source(self, adapter: APIDataSource):
        """Register a new API data source."""
        self.api_adapter.register_api_adapter(adapter)
        
    def ingest_api_data(self, source_name: str, raw_data: Dict[str, Any]):
        """Ingest data from a registered API source."""
        entities = self.api_adapter.process_api_data(source_name, raw_data)
        for entity in entities:
            self.add_entity(entity)
        logger.info(f"Ingested {len(entities)} entities from {source_name}")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get current engine statistics."""
        domain_counts = {domain.value: len(entity_ids) for domain, entity_ids in self.domain_index.items()}
        
        return {
            "total_entities": len(self.entities),
            "total_feedback_loops": len(self.feedback_loops),
            "entities_by_domain": domain_counts,
            "supported_domains": [d.value for d in self.api_adapter.get_supported_domains()],
            "frequency_signatures": sum(1 for e in self.entities.values() if e.frequency_signature is not None),
            "cross_domain_entities": sum(1 for e in self.entities.values() if len(e.cross_domain_connections) > 0)
        }


if __name__ == "__main__":
    # Initialize the Universal Resonance Engine
    engine = UniversalResonanceEngine()
    
    # Example usage - create some test entities
    test_entity = ResonanceEntity(
        name="test_mitochondria",
        domain=ScientificDomain.BIOLOGY,
        frequency_signature=FrequencySignature(
            primary_frequency=10.0,
            frequency_range=(8.0, 12.0),
            stellar_anchor=StellarAnchor.SOL
        ),
        biofreq_code="MIT-01"
    )
    
    engine.add_entity(test_entity)
    
    stats = engine.get_statistics()
    print("Universal Resonance Engine Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")