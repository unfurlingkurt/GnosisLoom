#!/usr/bin/env python3
"""
ResQL (Resonance Query Language) Engine - Natural Language Interface

This module provides a natural language query interface for the Universal Resonance Engine,
enabling agents and researchers to query frequency relationships across all scientific domains.

Author: Dr. Mordin Solus (custom research persona of Claude Code)  
Date: 2025-09-02
Version: 1.0.0

Query Examples:
- "Find frequencies near 7.83 Hz"
- "Show harmonic relationships with mitochondria"
- "Cross-domain connections between biology and physics"
- "Therapeutic protocols for fibromyalgia"
- "Stellar anchor relationships for DNA frequencies"
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum

from universal_resonance_engine import (
    UniversalResonanceEngine, ResonanceEntity, FrequencySignature,
    FeedbackLoop, ScientificDomain, StellarAnchor
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries supported by ResQL."""
    FREQUENCY_SEARCH = "frequency_search"
    HARMONIC_ANALYSIS = "harmonic_analysis"
    CROSS_DOMAIN = "cross_domain"
    ENTITY_LOOKUP = "entity_lookup"
    THERAPEUTIC_PROTOCOL = "therapeutic_protocol"
    STELLAR_RELATIONSHIP = "stellar_relationship"
    FEEDBACK_LOOP = "feedback_loop"
    PATTERN_DISCOVERY = "pattern_discovery"


@dataclass
class QueryResult:
    """Structured result from a ResQL query."""
    query_type: QueryType
    results: List[Any]
    metadata: Dict[str, Any]
    execution_time_ms: float
    result_count: int
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "query_type": self.query_type.value,
            "result_count": self.result_count,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
            "results": [self._serialize_result(r) for r in self.results]
        }
        
    def _serialize_result(self, result: Any) -> Dict[str, Any]:
        """Serialize individual result objects."""
        if isinstance(result, ResonanceEntity):
            return {
                "entity_id": result.entity_id,
                "name": result.name,
                "domain": result.domain.value,
                "biofreq_code": result.biofreq_code,
                "frequency": result.frequency_signature.primary_frequency if result.frequency_signature else None,
                "stellar_anchor": result.frequency_signature.stellar_anchor.star_name if result.frequency_signature and result.frequency_signature.stellar_anchor else None
            }
        elif isinstance(result, tuple) and len(result) >= 2:
            # Handle relationship tuples
            return {
                "primary": self._serialize_result(result[0]),
                "related": self._serialize_result(result[1]),
                "strength": result[2] if len(result) > 2 else None
            }
        else:
            return str(result)


class ResQLParser:
    """Natural language parser for ResQL queries."""
    
    def __init__(self):
        self.frequency_patterns = [
            r'(\d+\.?\d*)\s*(hz|hertz)',
            r'(\d+\.?\d*)\s*(khz|kilohertz)', 
            r'(\d+\.?\d*)\s*(mhz|megahertz)',
            r'(\d+\.?\d*)\s*(ghz|gigahertz)',
            r'(\d+\.?\d*)\s*(thz|terahertz)'
        ]
        
        self.tolerance_patterns = [
            r'within\s+(\d+\.?\d*)%',
            r'±\s*(\d+\.?\d*)%',
            r'tolerance\s+(\d+\.?\d*)%'
        ]
        
        self.stellar_anchors = [anchor.star_name.lower() for anchor in StellarAnchor]
        self.domains = [domain.value.lower() for domain in ScientificDomain]
        
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured parameters."""
        query_lower = query.lower().strip()
        
        # Determine query type
        query_type = self._identify_query_type(query_lower)
        
        # Extract parameters based on query type
        params = {
            "query_type": query_type,
            "original_query": query
        }
        
        # Extract frequencies
        frequencies = self._extract_frequencies(query_lower)
        if frequencies:
            params["frequencies"] = frequencies
            
        # Extract tolerance
        tolerance = self._extract_tolerance(query_lower)
        if tolerance:
            params["tolerance"] = tolerance
            
        # Extract domains
        domains = self._extract_domains(query_lower)
        if domains:
            params["domains"] = domains
            
        # Extract entity names/patterns
        entities = self._extract_entity_references(query_lower)
        if entities:
            params["entities"] = entities
            
        # Extract stellar anchors
        stellar_refs = self._extract_stellar_references(query_lower)
        if stellar_refs:
            params["stellar_anchors"] = stellar_refs
            
        # Extract BioFreq codes
        biofreq_codes = self._extract_biofreq_codes(query)
        if biofreq_codes:
            params["biofreq_codes"] = biofreq_codes
            
        return params
        
    def _identify_query_type(self, query: str) -> QueryType:
        """Identify the type of query from natural language."""
        if any(term in query for term in ['near', 'around', 'close to', 'frequency']):
            return QueryType.FREQUENCY_SEARCH
        elif any(term in query for term in ['harmonic', 'harmonics', 'overtone']):
            return QueryType.HARMONIC_ANALYSIS
        elif any(term in query for term in ['cross-domain', 'between domains', 'across domains']):
            return QueryType.CROSS_DOMAIN
        elif any(term in query for term in ['therapeutic', 'therapy', 'treatment', 'protocol']):
            return QueryType.THERAPEUTIC_PROTOCOL
        elif any(term in query for term in ['stellar', 'star', 'anchor']):
            return QueryType.STELLAR_RELATIONSHIP
        elif any(term in query for term in ['feedback', 'loop', 'fl-']):
            return QueryType.FEEDBACK_LOOP
        elif any(term in query for term in ['pattern', 'discover', 'find relationships']):
            return QueryType.PATTERN_DISCOVERY
        else:
            return QueryType.ENTITY_LOOKUP
            
    def _extract_frequencies(self, query: str) -> List[float]:
        """Extract frequency values from query."""
        frequencies = []
        
        for pattern in self.frequency_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                value, unit = match
                freq = float(value)
                
                # Convert to Hz
                unit_lower = unit.lower()
                if unit_lower in ['khz', 'kilohertz']:
                    freq *= 1e3
                elif unit_lower in ['mhz', 'megahertz']:
                    freq *= 1e6
                elif unit_lower in ['ghz', 'gigahertz']:
                    freq *= 1e9
                elif unit_lower in ['thz', 'terahertz']:
                    freq *= 1e12
                    
                frequencies.append(freq)
                
        return frequencies
        
    def _extract_tolerance(self, query: str) -> Optional[float]:
        """Extract tolerance percentage from query."""
        for pattern in self.tolerance_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return float(match.group(1)) / 100.0  # Convert percentage to decimal
        return None
        
    def _extract_domains(self, query: str) -> List[str]:
        """Extract scientific domains from query."""
        found_domains = []
        for domain in self.domains:
            if domain in query:
                found_domains.append(domain)
        return found_domains
        
    def _extract_entity_references(self, query: str) -> List[str]:
        """Extract potential entity names from query."""
        # Common biological/scientific terms
        entity_terms = [
            'mitochondria', 'dna', 'protein', 'neuron', 'heart', 'brain',
            'cell', 'membrane', 'enzyme', 'hormone', 'blood', 'tissue',
            'organ', 'bone', 'muscle', 'nerve', 'synapse', 'receptor'
        ]
        
        found_entities = []
        for term in entity_terms:
            if term in query:
                found_entities.append(term)
                
        return found_entities
        
    def _extract_stellar_references(self, query: str) -> List[str]:
        """Extract stellar anchor references from query."""
        found_stars = []
        for star in self.stellar_anchors:
            if star in query:
                found_stars.append(star)
        return found_stars
        
    def _extract_biofreq_codes(self, query: str) -> List[str]:
        """Extract BioFreq codes from query."""
        # Pattern for BioFreq codes (e.g., NEU-01, FL-PPT, CAR-03)
        pattern = r'\b([A-Z]{2,4}-\d{2}|[A-Z]{2,4}-[A-Z]{2,4})\b'
        matches = re.findall(pattern, query)
        return matches


class ResQLQueryEngine:
    """
    Main query engine for ResQL natural language interface.
    """
    
    def __init__(self, resonance_engine: UniversalResonanceEngine):
        self.engine = resonance_engine
        self.parser = ResQLParser()
        
        logger.info("ResQL Query Engine initialized")
        
    def query(self, natural_language_query: str) -> QueryResult:
        """Execute a natural language query and return structured results."""
        import time
        start_time = time.time()
        
        # Parse the query
        parsed_params = self.parser.parse_query(natural_language_query)
        query_type = parsed_params["query_type"]
        
        # Execute based on query type
        results = []
        metadata = {}
        confidence = 1.0
        
        try:
            if query_type == QueryType.FREQUENCY_SEARCH:
                results, metadata = self._execute_frequency_search(parsed_params)
            elif query_type == QueryType.HARMONIC_ANALYSIS:
                results, metadata = self._execute_harmonic_analysis(parsed_params)
            elif query_type == QueryType.CROSS_DOMAIN:
                results, metadata = self._execute_cross_domain_query(parsed_params)
            elif query_type == QueryType.ENTITY_LOOKUP:
                results, metadata = self._execute_entity_lookup(parsed_params)
            elif query_type == QueryType.THERAPEUTIC_PROTOCOL:
                results, metadata = self._execute_therapeutic_query(parsed_params)
            elif query_type == QueryType.STELLAR_RELATIONSHIP:
                results, metadata = self._execute_stellar_query(parsed_params)
            elif query_type == QueryType.FEEDBACK_LOOP:
                results, metadata = self._execute_feedback_loop_query(parsed_params)
            elif query_type == QueryType.PATTERN_DISCOVERY:
                results, metadata = self._execute_pattern_discovery(parsed_params)
            else:
                results = []
                metadata = {"error": f"Unsupported query type: {query_type}"}
                confidence = 0.0
                
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            results = []
            metadata = {"error": str(e)}
            confidence = 0.0
            
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResult(
            query_type=query_type,
            results=results,
            metadata=metadata,
            execution_time_ms=execution_time,
            result_count=len(results),
            confidence=confidence
        )
        
    def _execute_frequency_search(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute frequency proximity search."""
        frequencies = params.get("frequencies", [])
        tolerance = params.get("tolerance", 0.02)  # Default 2%
        
        if not frequencies:
            return [], {"error": "No frequencies specified in query"}
            
        all_results = []
        for freq in frequencies:
            entities = self.engine.find_entities_by_frequency(freq, tolerance)
            all_results.extend(entities)
            
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for entity in all_results:
            if entity.entity_id not in seen:
                unique_results.append(entity)
                seen.add(entity.entity_id)
                
        metadata = {
            "search_frequencies": frequencies,
            "tolerance": tolerance,
            "total_unique_matches": len(unique_results)
        }
        
        return unique_results, metadata
        
    def _execute_harmonic_analysis(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute harmonic relationship analysis."""
        entities = params.get("entities", [])
        tolerance = params.get("tolerance", 0.02)
        
        if not entities:
            return [], {"error": "No entities specified for harmonic analysis"}
            
        results = []
        
        # Find entities matching the specified names
        target_entities = []
        for entity_name in entities:
            for entity_id, entity in self.engine.entities.items():
                if entity_name.lower() in entity.name.lower():
                    target_entities.append(entity)
                    break
                    
        # Find harmonic relationships for each target entity
        for entity in target_entities:
            harmonics = self.engine.find_harmonic_relationships(entity.entity_id, tolerance)
            for harmonic_entity, ratio in harmonics:
                results.append((entity, harmonic_entity, ratio))
                
        metadata = {
            "target_entities": [e.name for e in target_entities],
            "tolerance": tolerance,
            "harmonic_relationships_found": len(results)
        }
        
        return results, metadata
        
    def _execute_cross_domain_query(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute cross-domain relationship query."""
        domains = params.get("domains", [])
        tolerance = params.get("tolerance", 0.1)
        
        if len(domains) < 2:
            # Default to biology and chemistry if not specified
            domains = ["biology", "chemistry"]
            
        # Convert domain strings to enums
        domain_enums = []
        for domain_str in domains:
            for domain_enum in ScientificDomain:
                if domain_str.lower() in domain_enum.value.lower():
                    domain_enums.append(domain_enum)
                    break
                    
        if len(domain_enums) < 2:
            return [], {"error": f"Need at least 2 domains, found: {domains}"}
            
        # Find connections between first two domains
        connections = self.engine.find_cross_domain_connections(
            domain_enums[0], domain_enums[1], tolerance
        )
        
        metadata = {
            "domains_analyzed": [d.value for d in domain_enums[:2]],
            "frequency_tolerance": tolerance,
            "connections_found": len(connections)
        }
        
        return connections, metadata
        
    def _execute_entity_lookup(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute entity lookup by name or BioFreq code."""
        entities = params.get("entities", [])
        biofreq_codes = params.get("biofreq_codes", [])
        
        results = []
        
        # Search by entity names
        for entity_name in entities:
            for entity in self.engine.entities.values():
                if entity_name.lower() in entity.name.lower():
                    results.append(entity)
                    
        # Search by BioFreq codes
        for code in biofreq_codes:
            if code in self.engine.biofreq_index:
                entity_ids = self.engine.biofreq_index[code]
                for entity_id in entity_ids:
                    if entity_id in self.engine.entities:
                        results.append(self.engine.entities[entity_id])
                        
        metadata = {
            "searched_names": entities,
            "searched_codes": biofreq_codes,
            "matches_found": len(results)
        }
        
        return results, metadata
        
    def _execute_therapeutic_query(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute therapeutic protocol query."""
        entities = params.get("entities", [])
        
        # Find therapeutic frequencies for specified conditions
        therapeutic_entities = []
        
        for entity_name in entities:
            for entity in self.engine.entities.values():
                if (entity_name.lower() in entity.name.lower() and 
                    entity.frequency_signature is not None):
                    
                    # Calculate therapeutic derivative
                    therapeutic_freq = entity.frequency_signature.to_therapeutic_derivative()
                    
                    therapeutic_info = {
                        "entity": entity,
                        "therapeutic_frequency": therapeutic_freq,
                        "original_frequency": entity.frequency_signature.primary_frequency,
                        "disease_states": entity.domain_metadata.get("disease_states", {})
                    }
                    therapeutic_entities.append(therapeutic_info)
                    
        metadata = {
            "conditions_searched": entities,
            "therapeutic_protocols_found": len(therapeutic_entities)
        }
        
        return therapeutic_entities, metadata
        
    def _execute_stellar_query(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute stellar anchor relationship query."""
        stellar_refs = params.get("stellar_anchors", [])
        
        results = []
        
        # If no specific stars mentioned, show all stellar relationships
        if not stellar_refs:
            for entity in self.engine.entities.values():
                if (entity.frequency_signature and 
                    entity.frequency_signature.stellar_anchor is not None):
                    results.append((entity, entity.frequency_signature.stellar_anchor))
        else:
            # Search for specific stellar anchor relationships
            for star_name in stellar_refs:
                for anchor in StellarAnchor:
                    if star_name.lower() in anchor.star_name.lower():
                        for entity in self.engine.entities.values():
                            if (entity.frequency_signature and 
                                entity.frequency_signature.stellar_anchor == anchor):
                                results.append((entity, anchor))
                                
        metadata = {
            "stellar_anchors_searched": stellar_refs,
            "relationships_found": len(results)
        }
        
        return results, metadata
        
    def _execute_feedback_loop_query(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute feedback loop query."""
        biofreq_codes = params.get("biofreq_codes", [])
        
        results = []
        
        if biofreq_codes:
            # Search for specific feedback loops
            for code in biofreq_codes:
                for loop in self.engine.feedback_loops.values():
                    if code.upper() == loop.biofreq_code.upper():
                        results.append(loop)
        else:
            # Return all feedback loops
            results = list(self.engine.feedback_loops.values())
            
        metadata = {
            "searched_codes": biofreq_codes,
            "feedback_loops_found": len(results)
        }
        
        return results, metadata
        
    def _execute_pattern_discovery(self, params: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Execute pattern discovery across the knowledge graph."""
        # Find interesting patterns and correlations
        patterns = []
        
        # Pattern 1: Frequency clusters
        frequency_clusters = self._find_frequency_clusters()
        patterns.extend(frequency_clusters)
        
        # Pattern 2: Multi-domain entities
        multi_domain_entities = [
            entity for entity in self.engine.entities.values()
            if len(entity.cross_domain_connections) > 0
        ]
        patterns.extend(multi_domain_entities)
        
        # Pattern 3: Highly connected feedback loops
        connected_loops = [
            loop for loop in self.engine.feedback_loops.values()
            if len(loop.entities) > 2
        ]
        patterns.extend(connected_loops)
        
        metadata = {
            "pattern_types": ["frequency_clusters", "multi_domain_entities", "connected_feedback_loops"],
            "total_patterns": len(patterns)
        }
        
        return patterns, metadata
        
    def _find_frequency_clusters(self) -> List[Dict[str, Any]]:
        """Find clusters of entities with similar frequencies."""
        clusters = []
        frequency_groups = {}
        
        # Group entities by rounded frequency
        for entity in self.engine.entities.values():
            if entity.frequency_signature is None:
                continue
                
            freq_key = round(math.log10(entity.frequency_signature.primary_frequency), 1)
            if freq_key not in frequency_groups:
                frequency_groups[freq_key] = []
            frequency_groups[freq_key].append(entity)
            
        # Find groups with multiple entities
        for freq_key, entities in frequency_groups.items():
            if len(entities) >= 3:  # Minimum cluster size
                cluster = {
                    "type": "frequency_cluster",
                    "frequency_range": f"10^{freq_key} Hz",
                    "entities": entities,
                    "size": len(entities)
                }
                clusters.append(cluster)
                
        return clusters


if __name__ == "__main__":
    # Example usage
    from universal_resonance_engine import UniversalResonanceEngine
    from gnosisloom_data_integrator import GnosisLoomDataIntegrator
    
    print("Initializing ResQL Query Engine...")
    
    # Create and populate the engine
    integrator = GnosisLoomDataIntegrator()
    print("Integrating GnosisLoom databases...")
    integrator.integrate_all_databases()
    
    engine = integrator.get_engine()
    query_engine = ResQLQueryEngine(engine)
    
    print("\n=== ResQL Query Examples ===")
    
    # Example queries
    test_queries = [
        "Find frequencies near 7.83 Hz",
        "Show harmonic relationships with mitochondria", 
        "Cross-domain connections between biology and chemistry",
        "Stellar anchor relationships for Sol",
        "Show feedback loops FL-PPT"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = query_engine.query(query)
        print(f"Results: {result.result_count} items in {result.execution_time_ms:.2f}ms")
        
        if result.results and result.result_count > 0:
            first_result = result.results[0]
            if hasattr(first_result, 'name'):
                print(f"First result: {first_result.name}")
            else:
                print(f"First result: {type(first_result)}")
                
        print(f"Metadata: {result.metadata}")