#!/usr/bin/env python3
"""
Agent API Interface - Universal Resonance Engine Agent Integration

This module provides a clean, simple API interface that agents can use to query
the Universal Resonance Engine without needing to understand the internal complexity.

Author: Dr. Mordin Solus (custom research persona of Claude Code)
Date: 2025-09-02
Version: 1.0.0

Key Features:
- Simple function-based API for agents
- Natural language query processing
- JSON-serializable results
- Caching for performance
- Error handling and validation
- Multi-domain frequency relationship discovery
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import time
from functools import lru_cache

from universal_resonance_engine import UniversalResonanceEngine, ScientificDomain
from gnosisloom_data_integrator import GnosisLoomDataIntegrator
from resql_query_engine import ResQLQueryEngine, QueryResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UniversalResonanceAPI:
    """
    Agent-friendly API for the Universal Resonance Engine.
    Provides simple methods that agents can call without understanding internal complexity.
    """
    
    def __init__(self, auto_initialize: bool = True, gnosisloom_data_path: str = None):
        """
        Initialize the Universal Resonance API.
        
        Args:
            auto_initialize: If True, automatically loads all GnosisLoom databases
            gnosisloom_data_path: Path to GnosisLoom data directory
        """
        self.engine = None
        self.query_engine = None
        self.initialized = False
        self.stats_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        if auto_initialize:
            self.initialize(gnosisloom_data_path)
            
    def initialize(self, gnosisloom_data_path: str = None) -> Dict[str, Any]:
        """
        Initialize the Universal Resonance Engine with GnosisLoom data.
        
        Args:
            gnosisloom_data_path: Path to GnosisLoom data directory
            
        Returns:
            Integration statistics
        """
        logger.info("Initializing Universal Resonance API...")
        
        try:
            # Initialize data integrator
            integrator = GnosisLoomDataIntegrator(gnosisloom_data_path)
            
            # Integrate all databases
            logger.info("Integrating GnosisLoom databases...")
            stats = integrator.integrate_all_databases()
            
            # Get the engine
            self.engine = integrator.get_engine()
            self.query_engine = ResQLQueryEngine(self.engine)
            
            self.initialized = True
            self.stats_cache = {"integration_stats": stats, "timestamp": time.time()}
            
            logger.info(f"Universal Resonance API initialized successfully: {stats['total_entities']} entities, {stats['total_feedback_loops']} feedback loops")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to initialize Universal Resonance API: {str(e)}")
            raise
            
    def _ensure_initialized(self):
        """Ensure the API is initialized before processing requests."""
        if not self.initialized or self.engine is None:
            raise RuntimeError("Universal Resonance API not initialized. Call initialize() first.")
            
    # ===== CORE QUERY METHODS =====
    
    def query_natural_language(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return results.
        
        Args:
            query: Natural language query (e.g., "Find frequencies near 7.83 Hz")
            
        Returns:
            Dictionary with query results
        """
        self._ensure_initialized()
        
        try:
            result = self.query_engine.query(query)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {
                "query_type": "error",
                "result_count": 0,
                "confidence": 0.0,
                "execution_time_ms": 0.0,
                "metadata": {"error": str(e)},
                "results": []
            }
            
    def find_frequency_matches(self, frequency_hz: float, tolerance_percent: float = 2.0) -> List[Dict[str, Any]]:
        """
        Find entities with frequencies matching the target frequency.
        
        Args:
            frequency_hz: Target frequency in Hz
            tolerance_percent: Tolerance as percentage (default 2%)
            
        Returns:
            List of matching entities
        """
        self._ensure_initialized()
        
        tolerance = tolerance_percent / 100.0
        entities = self.engine.find_entities_by_frequency(frequency_hz, tolerance)
        
        return [self._entity_to_dict(entity) for entity in entities]
        
    def find_harmonic_relationships(self, entity_name: str, tolerance_percent: float = 2.0) -> List[Dict[str, Any]]:
        """
        Find harmonic relationships for a given entity.
        
        Args:
            entity_name: Name of entity to analyze
            tolerance_percent: Harmonic tolerance as percentage
            
        Returns:
            List of harmonic relationships
        """
        self._ensure_initialized()
        
        # Find entity by name
        target_entity = None
        for entity in self.engine.entities.values():
            if entity_name.lower() in entity.name.lower():
                target_entity = entity
                break
                
        if not target_entity:
            return []
            
        tolerance = tolerance_percent / 100.0
        harmonics = self.engine.find_harmonic_relationships(target_entity.entity_id, tolerance)
        
        results = []
        for harmonic_entity, ratio in harmonics:
            results.append({
                "target_entity": self._entity_to_dict(target_entity),
                "harmonic_entity": self._entity_to_dict(harmonic_entity),
                "harmonic_ratio": ratio,
                "relationship_type": "harmonic"
            })
            
        return results
        
    def find_cross_domain_connections(self, domain1: str, domain2: str, 
                                    frequency_tolerance_percent: float = 10.0) -> List[Dict[str, Any]]:
        """
        Find frequency correlations between two scientific domains.
        
        Args:
            domain1: First scientific domain (e.g., "biology")
            domain2: Second scientific domain (e.g., "chemistry")
            frequency_tolerance_percent: Frequency proximity tolerance
            
        Returns:
            List of cross-domain connections
        """
        self._ensure_initialized()
        
        # Convert domain strings to enums
        domain1_enum = self._string_to_domain(domain1)
        domain2_enum = self._string_to_domain(domain2)
        
        if not domain1_enum or not domain2_enum:
            return []
            
        tolerance = frequency_tolerance_percent / 100.0
        connections = self.engine.find_cross_domain_connections(domain1_enum, domain2_enum, tolerance)
        
        results = []
        for entity1, entity2, proximity in connections:
            results.append({
                f"{domain1}_entity": self._entity_to_dict(entity1),
                f"{domain2}_entity": self._entity_to_dict(entity2),
                "frequency_proximity": proximity,
                "domains": [domain1, domain2]
            })
            
        return results
        
    def get_therapeutic_frequencies(self, condition_or_entity: str) -> List[Dict[str, Any]]:
        """
        Get therapeutic frequency recommendations for a condition or entity.
        
        Args:
            condition_or_entity: Condition name or entity name
            
        Returns:
            List of therapeutic frequency protocols
        """
        self._ensure_initialized()
        
        query = f"therapeutic protocols for {condition_or_entity}"
        result = self.query_natural_language(query)
        
        # Extract therapeutic information from results
        therapeutic_protocols = []
        for item in result.get("results", []):
            if isinstance(item, dict) and "therapeutic_frequency" in item:
                therapeutic_protocols.append(item)
                
        return therapeutic_protocols
        
    def get_stellar_anchor_relationships(self, stellar_anchor: str = None) -> List[Dict[str, Any]]:
        """
        Get entities related to specific stellar anchors.
        
        Args:
            stellar_anchor: Name of stellar anchor (Sol, Arcturus, etc.) or None for all
            
        Returns:
            List of stellar anchor relationships
        """
        self._ensure_initialized()
        
        if stellar_anchor:
            query = f"stellar anchor relationships for {stellar_anchor}"
        else:
            query = "show all stellar anchor relationships"
            
        result = self.query_natural_language(query)
        return result.get("results", [])
        
    def get_feedback_loops(self, biofreq_code: str = None) -> List[Dict[str, Any]]:
        """
        Get feedback loop information.
        
        Args:
            biofreq_code: Specific BioFreq code (e.g., "FL-PPT") or None for all
            
        Returns:
            List of feedback loops
        """
        self._ensure_initialized()
        
        if biofreq_code:
            query = f"feedback loop {biofreq_code}"
        else:
            query = "show all feedback loops"
            
        result = self.query_natural_language(query)
        return result.get("results", [])
        
    # ===== DISCOVERY METHODS =====
    
    def discover_frequency_patterns(self) -> Dict[str, Any]:
        """
        Discover interesting frequency patterns across the knowledge graph.
        
        Returns:
            Dictionary of discovered patterns
        """
        self._ensure_initialized()
        
        query = "discover patterns across all domains"
        result = self.query_natural_language(query)
        return result
        
    def find_frequency_clusters(self, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
        """
        Find clusters of entities with similar frequencies.
        
        Args:
            min_cluster_size: Minimum number of entities in a cluster
            
        Returns:
            List of frequency clusters
        """
        self._ensure_initialized()
        
        # Use pattern discovery to find clusters
        patterns = self.discover_frequency_patterns()
        clusters = []
        
        for pattern in patterns.get("results", []):
            if (isinstance(pattern, dict) and 
                pattern.get("type") == "frequency_cluster" and
                pattern.get("size", 0) >= min_cluster_size):
                clusters.append(pattern)
                
        return clusters
        
    def get_disease_frequency_signatures(self, disease_name: str) -> List[Dict[str, Any]]:
        """
        Get frequency signatures associated with a disease state.
        
        Args:
            disease_name: Name of disease or condition
            
        Returns:
            List of frequency signatures for the disease
        """
        self._ensure_initialized()
        
        disease_signatures = []
        
        for entity in self.engine.entities.values():
            if (entity.domain_metadata and 
                "disease_states" in entity.domain_metadata):
                
                disease_states = entity.domain_metadata["disease_states"]
                if isinstance(disease_states, dict) and disease_name.lower() in [k.lower() for k in disease_states.keys()]:
                    
                    # Find the specific disease frequency
                    disease_freq = None
                    for k, v in disease_states.items():
                        if disease_name.lower() in k.lower():
                            disease_freq = v
                            break
                            
                    if disease_freq is not None:
                        disease_signatures.append({
                            "entity": self._entity_to_dict(entity),
                            "disease": disease_name,
                            "disease_frequency": disease_freq,
                            "normal_frequency": entity.frequency_signature.primary_frequency if entity.frequency_signature else None,
                            "frequency_disruption": self._calculate_disruption(entity.frequency_signature.primary_frequency if entity.frequency_signature else None, disease_freq)
                        })
                        
        return disease_signatures
        
    # ===== INFORMATION METHODS =====
    
    @lru_cache(maxsize=1)
    def get_system_statistics(self, include_detailed_breakdown: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive system statistics.
        
        Args:
            include_detailed_breakdown: Include detailed entity breakdowns
            
        Returns:
            System statistics
        """
        self._ensure_initialized()
        
        # Check cache
        if self.stats_cache and (time.time() - self.stats_cache.get("timestamp", 0)) < self.cache_timeout:
            base_stats = self.stats_cache["integration_stats"]
        else:
            base_stats = self.engine.get_statistics()
            self.stats_cache = {"integration_stats": base_stats, "timestamp": time.time()}
            
        if include_detailed_breakdown:
            # Add detailed breakdowns
            base_stats["frequency_ranges"] = self._analyze_frequency_ranges()
            base_stats["stellar_anchor_distribution"] = self._analyze_stellar_distribution()
            base_stats["biofreq_code_summary"] = self._analyze_biofreq_codes()
            
        return base_stats
        
    def list_available_entities(self, domain: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List available entities in the knowledge graph.
        
        Args:
            domain: Filter by domain (optional)
            limit: Maximum number of entities to return
            
        Returns:
            List of entity summaries
        """
        self._ensure_initialized()
        
        entities = []
        count = 0
        
        for entity in self.engine.entities.values():
            if count >= limit:
                break
                
            if domain is None or entity.domain.value.lower() == domain.lower():
                entities.append({
                    "name": entity.name,
                    "domain": entity.domain.value,
                    "biofreq_code": entity.biofreq_code,
                    "frequency": entity.frequency_signature.primary_frequency if entity.frequency_signature else None,
                    "stellar_anchor": entity.frequency_signature.stellar_anchor.star_name if entity.frequency_signature and entity.frequency_signature.stellar_anchor else None
                })
                count += 1
                
        return entities
        
    def get_supported_domains(self) -> List[str]:
        """Get list of supported scientific domains."""
        self._ensure_initialized()
        return [domain.value for domain in self.engine.get_statistics()["supported_domains"] if isinstance(domain, str)] + [domain for domain in self.engine.get_statistics()["supported_domains"] if isinstance(domain, ScientificDomain)]
        
    # ===== UTILITY METHODS =====
    
    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convert ResonanceEntity to dictionary."""
        return {
            "entity_id": entity.entity_id,
            "name": entity.name,
            "domain": entity.domain.value,
            "biofreq_code": entity.biofreq_code,
            "frequency": entity.frequency_signature.primary_frequency if entity.frequency_signature else None,
            "frequency_range": entity.frequency_signature.frequency_range if entity.frequency_signature else None,
            "stellar_anchor": entity.frequency_signature.stellar_anchor.star_name if entity.frequency_signature and entity.frequency_signature.stellar_anchor else None,
            "harmonics": entity.frequency_signature.harmonics if entity.frequency_signature else [],
            "phase": entity.frequency_signature.phase if entity.frequency_signature else 0.0,
            "api_source": entity.api_source
        }
        
    def _string_to_domain(self, domain_str: str) -> Optional[ScientificDomain]:
        """Convert domain string to ScientificDomain enum."""
        for domain in ScientificDomain:
            if domain_str.lower() in domain.value.lower():
                return domain
        return None
        
    def _calculate_disruption(self, normal_freq: Optional[float], disease_freq: Optional[float]) -> Optional[float]:
        """Calculate frequency disruption percentage."""
        if normal_freq is None or disease_freq is None or normal_freq == 0:
            return None
        return abs(disease_freq - normal_freq) / normal_freq * 100.0
        
    def _analyze_frequency_ranges(self) -> Dict[str, int]:
        """Analyze frequency distribution across ranges."""
        ranges = {
            "sub_hz": 0,      # < 1 Hz
            "low_hz": 0,      # 1 - 100 Hz
            "mid_hz": 0,      # 100 Hz - 1 kHz
            "high_hz": 0,     # 1 kHz - 1 MHz
            "very_high": 0,   # 1 MHz - 1 GHz
            "extreme": 0      # > 1 GHz
        }
        
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            freq = entity.frequency_signature.primary_frequency
            if freq < 1:
                ranges["sub_hz"] += 1
            elif freq < 100:
                ranges["low_hz"] += 1
            elif freq < 1000:
                ranges["mid_hz"] += 1
            elif freq < 1e6:
                ranges["high_hz"] += 1
            elif freq < 1e9:
                ranges["very_high"] += 1
            else:
                ranges["extreme"] += 1
                
        return ranges
        
    def _analyze_stellar_distribution(self) -> Dict[str, int]:
        """Analyze distribution of stellar anchors."""
        distribution = {}
        
        for entity in self.engine.entities.values():
            if (entity.frequency_signature and 
                entity.frequency_signature.stellar_anchor):
                
                anchor_name = entity.frequency_signature.stellar_anchor.star_name
                distribution[anchor_name] = distribution.get(anchor_name, 0) + 1
                
        return distribution
        
    def _analyze_biofreq_codes(self) -> Dict[str, int]:
        """Analyze distribution of BioFreq codes."""
        code_distribution = {}
        
        for entity in self.engine.entities.values():
            if entity.biofreq_code:
                prefix = entity.biofreq_code.split('-')[0]
                code_distribution[prefix] = code_distribution.get(prefix, 0) + 1
                
        return code_distribution


# ===== CONVENIENCE FUNCTIONS FOR AGENTS =====

# Global API instance
_global_api = None

def initialize_universal_resonance_api(gnosisloom_data_path: str = None) -> Dict[str, Any]:
    """Initialize the global Universal Resonance API instance."""
    global _global_api
    _global_api = UniversalResonanceAPI(auto_initialize=False)
    return _global_api.initialize(gnosisloom_data_path)

def query_frequencies(query: str) -> Dict[str, Any]:
    """Query frequencies using natural language."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.query_natural_language(query)

def find_frequency_near(frequency_hz: float, tolerance_percent: float = 2.0) -> List[Dict[str, Any]]:
    """Find entities near a specific frequency."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.find_frequency_matches(frequency_hz, tolerance_percent)

def get_harmonics(entity_name: str) -> List[Dict[str, Any]]:
    """Get harmonic relationships for an entity."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.find_harmonic_relationships(entity_name)

def cross_domain_search(domain1: str, domain2: str) -> List[Dict[str, Any]]:
    """Find connections between two scientific domains."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.find_cross_domain_connections(domain1, domain2)

def get_therapeutic_protocol(condition: str) -> List[Dict[str, Any]]:
    """Get therapeutic frequency protocols for a condition."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.get_therapeutic_frequencies(condition)

def system_stats() -> Dict[str, Any]:
    """Get system statistics."""
    if _global_api is None:
        initialize_universal_resonance_api()
    return _global_api.get_system_statistics()


if __name__ == "__main__":
    # Example usage
    print("=== Universal Resonance API Test ===")
    
    # Initialize API
    print("Initializing API...")
    stats = initialize_universal_resonance_api()
    print(f"Initialized with {stats['total_entities']} entities")
    
    # Test queries
    print("\n=== Example Queries ===")
    
    # Natural language query
    result = query_frequencies("Find frequencies near 7.83 Hz")
    print(f"Schumann resonance matches: {result['result_count']}")
    
    # Frequency search
    matches = find_frequency_near(10.0, tolerance_percent=5.0)
    print(f"10 Hz matches: {len(matches)}")
    
    # Harmonic analysis
    harmonics = get_harmonics("mitochondria")
    print(f"Mitochondria harmonics: {len(harmonics)}")
    
    # System statistics
    stats = system_stats()
    print(f"System stats: {stats['frequency_signatures']} frequency signatures")