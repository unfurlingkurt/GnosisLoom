#!/usr/bin/env python3
"""
GnosisLoom Data Integrator - Multi-Domain Database Integration Engine

This module integrates all existing GnosisLoom databases into the Universal Resonance Engine,
preserving the BioFreq framework while enabling cross-domain frequency relationships.

Author: Dr. Mordin Solus (custom research persona of Claude Code)
Date: 2025-09-02
Version: 1.0.0

Integrates:
- 29+ JSON databases from GnosisLoom/data/
- Complete MS documentation knowledge
- BioFreq coding systems (NEU-01, CAR-03, FL-PPT, etc.)
- Stellar anchor relationships
- Cross-domain frequency mappings
"""

import json
import os
import glob
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

from universal_resonance_engine import (
    UniversalResonanceEngine, ResonanceEntity, FrequencySignature, 
    FeedbackLoop, ScientificDomain, StellarAnchor, APIDataSource
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GnosisLoomBiologyAdapter(APIDataSource):
    """Adapter for GnosisLoom biological frequency data."""
    
    def __init__(self):
        super().__init__("GnosisLoom_Biology", ScientificDomain.BIOLOGY)
        
    def extract_frequency_signatures(self, raw_data: Dict[str, Any]) -> List[FrequencySignature]:
        """Extract frequency signatures from GnosisLoom biological data."""
        signatures = []
        
        if isinstance(raw_data, dict):
            for key, data in raw_data.items():
                if isinstance(data, dict) and 'normal_freq' in data:
                    # Standard GnosisLoom frequency format
                    freq_range = data.get('range', [data['normal_freq'] * 0.9, data['normal_freq'] * 1.1])
                    harmonics = data.get('harmonics', [])
                    phase = data.get('phase', 0.0)
                    
                    # Map stellar anchor string to enum
                    stellar_anchor = None
                    if 'stellar_anchor' in data and data['stellar_anchor']:
                        stellar_name = data['stellar_anchor'].upper().replace(' ', '_')
                        try:
                            stellar_anchor = StellarAnchor[stellar_name]
                        except KeyError:
                            logger.warning(f"Unknown stellar anchor: {data['stellar_anchor']}")
                    
                    signature = FrequencySignature(
                        primary_frequency=float(data['normal_freq']),
                        frequency_range=tuple(freq_range),
                        harmonics=harmonics,
                        phase=phase,
                        stellar_anchor=stellar_anchor,
                        measurement_context={"source_key": key, "element": data.get('element')}
                    )
                    signatures.append(signature)
                    
        return signatures
        
    def create_resonance_entities(self, raw_data: Dict[str, Any]) -> List[ResonanceEntity]:
        """Create ResonanceEntity objects from GnosisLoom biological data."""
        entities = []
        
        if isinstance(raw_data, dict):
            for key, data in raw_data.items():
                if isinstance(data, dict) and 'normal_freq' in data:
                    # Extract frequency signature
                    signatures = self.extract_frequency_signatures({key: data})
                    if not signatures:
                        continue
                        
                    signature = signatures[0]
                    
                    # Determine BioFreq code from key patterns
                    biofreq_code = self._determine_biofreq_code(key, data)
                    
                    # Create entity
                    entity = ResonanceEntity(
                        name=key,
                        domain=ScientificDomain.BIOLOGY,
                        frequency_signature=signature,
                        biofreq_code=biofreq_code,
                        domain_metadata={
                            "disease_states": data.get('disease_states', {}),
                            "element": data.get('element'),
                            "original_data": data
                        },
                        api_source="GnosisLoom",
                        api_metadata={"database_key": key}
                    )
                    
                    entities.append(entity)
                    
        return entities
        
    def get_domain_specific_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract biology-specific metadata."""
        metadata = {
            "total_biological_entities": 0,
            "disease_states": set(),
            "elements": set(),
            "stellar_anchors": set()
        }
        
        if isinstance(raw_data, dict):
            for key, data in raw_data.items():
                if isinstance(data, dict) and 'normal_freq' in data:
                    metadata["total_biological_entities"] += 1
                    
                    if 'disease_states' in data:
                        metadata["disease_states"].update(data['disease_states'].keys())
                        
                    if 'element' in data and data['element']:
                        metadata["elements"].add(data['element'])
                        
                    if 'stellar_anchor' in data and data['stellar_anchor']:
                        metadata["stellar_anchors"].add(data['stellar_anchor'])
                        
        # Convert sets to lists for JSON serialization
        for key in ['disease_states', 'elements', 'stellar_anchors']:
            metadata[key] = list(metadata[key])
            
        return metadata
        
    def _determine_biofreq_code(self, key: str, data: Dict[str, Any]) -> Optional[str]:
        """Determine BioFreq code from entity key and data."""
        key_lower = key.lower()
        
        # Neural entities
        if any(term in key_lower for term in ['neural', 'neuron', 'brain', 'nerve', 'synapse']):
            return f"NEU-{hash(key) % 100:02d}"
            
        # Cardiac entities  
        elif any(term in key_lower for term in ['heart', 'cardiac', 'cardio']):
            return f"CAR-{hash(key) % 100:02d}"
            
        # Vascular entities
        elif any(term in key_lower for term in ['vascular', 'blood', 'vessel', 'artery']):
            return f"VAS-{hash(key) % 100:02d}"
            
        # Endocrine entities
        elif any(term in key_lower for term in ['hormone', 'endocrine', 'gland', 'insulin', 'thyroid']):
            return f"END-{hash(key) % 100:02d}"
            
        # Immune entities
        elif any(term in key_lower for term in ['immune', 'cytokine', 'antibody', 'lymph']):
            return f"IMM-{hash(key) % 100:02d}"
            
        # Cellular entities
        elif any(term in key_lower for term in ['cell', 'mitochondria', 'membrane', 'atp']):
            return f"CEL-{hash(key) % 100:02d}"
            
        # Default biological entity
        return f"BIO-{hash(key) % 100:02d}"


class GnosisLoomChemistryAdapter(APIDataSource):
    """Adapter for GnosisLoom chemistry and molecular data."""
    
    def __init__(self):
        super().__init__("GnosisLoom_Chemistry", ScientificDomain.CHEMISTRY)
        
    def extract_frequency_signatures(self, raw_data: Dict[str, Any]) -> List[FrequencySignature]:
        """Extract frequency signatures from chemistry data."""
        signatures = []
        
        # Handle periodic table format
        if 'elements' in raw_data or any('atomic_number' in str(v) for v in raw_data.values() if isinstance(v, dict)):
            signatures.extend(self._extract_periodic_signatures(raw_data))
            
        # Handle molecular chemistry format
        elif any(isinstance(v, dict) and ('bond_frequency' in v or 'vibrational_frequency' in v) 
                for v in raw_data.values()):
            signatures.extend(self._extract_molecular_signatures(raw_data))
            
        return signatures
        
    def _extract_periodic_signatures(self, data: Dict[str, Any]) -> List[FrequencySignature]:
        """Extract signatures from periodic table data."""
        signatures = []
        
        for element, info in data.items():
            if isinstance(info, dict) and 'frequency' in info:
                signature = FrequencySignature(
                    primary_frequency=float(info['frequency']),
                    frequency_range=(info['frequency'] * 0.95, info['frequency'] * 1.05),
                    measurement_context={
                        "element": element,
                        "atomic_number": info.get('atomic_number'),
                        "atomic_mass": info.get('atomic_mass')
                    }
                )
                signatures.append(signature)
                
        return signatures
        
    def _extract_molecular_signatures(self, data: Dict[str, Any]) -> List[FrequencySignature]:
        """Extract signatures from molecular data."""
        signatures = []
        
        for molecule, info in data.items():
            if isinstance(info, dict):
                freq = info.get('bond_frequency') or info.get('vibrational_frequency')
                if freq:
                    signature = FrequencySignature(
                        primary_frequency=float(freq),
                        frequency_range=(freq * 0.9, freq * 1.1),
                        measurement_context={
                            "molecule": molecule,
                            "bond_type": info.get('bond_type'),
                            "functional_group": info.get('functional_group')
                        }
                    )
                    signatures.append(signature)
                    
        return signatures
        
    def create_resonance_entities(self, raw_data: Dict[str, Any]) -> List[ResonanceEntity]:
        """Create chemistry ResonanceEntity objects."""
        entities = []
        signatures = self.extract_frequency_signatures(raw_data)
        
        entity_index = 0
        for key, data in raw_data.items():
            if isinstance(data, dict) and entity_index < len(signatures):
                entity = ResonanceEntity(
                    name=key,
                    domain=ScientificDomain.CHEMISTRY,
                    frequency_signature=signatures[entity_index],
                    biofreq_code=f"CHE-{hash(key) % 100:02d}",
                    domain_metadata=data,
                    api_source="GnosisLoom",
                    api_metadata={"chemistry_type": "molecular" if "bond" in str(data) else "elemental"}
                )
                entities.append(entity)
                entity_index += 1
                
        return entities
        
    def get_domain_specific_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chemistry-specific metadata."""
        return {
            "total_chemical_entities": len(raw_data),
            "data_type": "molecular" if any("bond" in str(v) for v in raw_data.values()) else "elemental"
        }


class GnosisLoomDataIntegrator:
    """
    Main integration engine for all GnosisLoom databases into the Universal Resonance Engine.
    """
    
    def __init__(self, gnosisloom_data_path: str = None):
        if gnosisloom_data_path is None:
            # Default to current directory structure
            self.data_path = Path(__file__).parent.parent / "data"
        else:
            self.data_path = Path(gnosisloom_data_path)
            
        self.engine = UniversalResonanceEngine()
        self.integration_stats = {
            "databases_processed": 0,
            "entities_created": 0,
            "feedback_loops_created": 0,
            "errors": []
        }
        
        # Register adapters
        self.engine.register_api_source(GnosisLoomBiologyAdapter())
        self.engine.register_api_source(GnosisLoomChemistryAdapter())
        
        logger.info(f"GnosisLoom Data Integrator initialized with path: {self.data_path}")
        
    def integrate_all_databases(self) -> Dict[str, Any]:
        """Integrate all JSON databases from the GnosisLoom data directory."""
        json_files = list(self.data_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON databases to integrate")
        
        for json_file in json_files:
            try:
                self._integrate_database_file(json_file)
                self.integration_stats["databases_processed"] += 1
            except Exception as e:
                error_msg = f"Error processing {json_file.name}: {str(e)}"
                logger.error(error_msg)
                self.integration_stats["errors"].append(error_msg)
                
        # Process feedback loops
        self._integrate_feedback_loops()
        
        # Generate final statistics
        final_stats = self.engine.get_statistics()
        final_stats.update(self.integration_stats)
        
        logger.info(f"Integration complete: {final_stats}")
        return final_stats
        
    def _integrate_database_file(self, json_file_path: Path):
        """Integrate a single JSON database file."""
        logger.info(f"Processing: {json_file_path.name}")
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Determine data type and appropriate adapter
        filename = json_file_path.stem.lower()
        
        if self._is_biology_database(filename):
            self.engine.ingest_api_data("GnosisLoom_Biology", data)
        elif self._is_chemistry_database(filename):
            self.engine.ingest_api_data("GnosisLoom_Chemistry", data)
        elif filename == "feedback_loops":
            # Handle feedback loops separately
            self._process_feedback_loops_data(data)
        else:
            # Generic biological processing as default
            logger.warning(f"Unknown database type for {filename}, treating as biology")
            self.engine.ingest_api_data("GnosisLoom_Biology", data)
            
        logger.debug(f"Completed processing: {json_file_path.name}")
        
    def _is_biology_database(self, filename: str) -> bool:
        """Determine if database contains biological data."""
        biology_keywords = [
            'comprehensive_frequencies', 'neural', 'biological', 'organ', 'tissue',
            'cellular', 'mitochondria', 'dna', 'protein', 'genomic'
        ]
        return any(keyword in filename for keyword in biology_keywords)
        
    def _is_chemistry_database(self, filename: str) -> bool:
        """Determine if database contains chemistry data."""
        chemistry_keywords = [
            'periodic_table', 'molecular_chemistry', 'primordial_chemistry',
            'chemical', 'atomic', 'molecular', 'bond', 'element'
        ]
        return any(keyword in filename for keyword in chemistry_keywords)
        
    def _process_feedback_loops_data(self, data: Dict[str, Any]):
        """Process feedback loops data from GnosisLoom."""
        for loop_code, description in data.items():
            if loop_code.startswith('FL-'):
                feedback_loop = FeedbackLoop(
                    biofreq_code=loop_code,
                    name=f"Feedback Loop {loop_code}",
                    description=str(description),
                    loop_type=self._determine_loop_type(loop_code, description)
                )
                self.engine.add_feedback_loop(feedback_loop)
                self.integration_stats["feedback_loops_created"] += 1
                
    def _determine_loop_type(self, code: str, description: str) -> str:
        """Determine feedback loop type from code and description."""
        desc_lower = str(description).lower()
        
        if any(term in desc_lower for term in ['amplify', 'increase', 'enhance']):
            return "amplifying"
        elif any(term in desc_lower for term in ['stabilize', 'maintain', 'balance']):
            return "stabilizing"
        elif any(term in desc_lower for term in ['oscillat', 'rhythm', 'cycle']):
            return "oscillatory"
        else:
            return "regulatory"
            
    def _integrate_feedback_loops(self):
        """Create relationships between entities and feedback loops."""
        # This is where we would implement sophisticated relationship detection
        # For now, we'll create basic connections based on BioFreq codes
        
        for loop_id, loop in self.engine.feedback_loops.items():
            # Find entities that might be related to this feedback loop
            related_entities = []
            
            # Simple matching based on description keywords
            loop_desc = loop.description.lower()
            for entity in self.engine.entities.values():
                entity_name = entity.name.lower()
                if any(word in loop_desc for word in entity_name.split('_')):
                    related_entities.append(entity)
                    
            # Add entities to the feedback loop
            for entity in related_entities[:5]:  # Limit to 5 to avoid overcrowding
                loop.add_entity(entity)
                
        logger.info(f"Processed {len(self.engine.feedback_loops)} feedback loops")
        
    def export_integration_report(self, output_path: str = None) -> str:
        """Export comprehensive integration report."""
        if output_path is None:
            output_path = self.data_path.parent / "logs" / "integration_report.json"
            
        stats = self.engine.get_statistics()
        stats.update(self.integration_stats)
        
        # Add detailed entity breakdown
        entity_details = {}
        for domain in ScientificDomain:
            domain_entities = [e for e in self.engine.entities.values() if e.domain == domain]
            entity_details[domain.value] = {
                "count": len(domain_entities),
                "with_frequency_signatures": sum(1 for e in domain_entities if e.frequency_signature is not None),
                "with_biofreq_codes": sum(1 for e in domain_entities if e.biofreq_code is not None),
                "sample_entities": [e.name for e in domain_entities[:5]]
            }
            
        stats["entity_details"] = entity_details
        
        # Write report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
            
        logger.info(f"Integration report exported to: {output_path}")
        return str(output_path)
        
    def get_engine(self) -> UniversalResonanceEngine:
        """Get the integrated Universal Resonance Engine."""
        return self.engine


if __name__ == "__main__":
    # Integration example
    integrator = GnosisLoomDataIntegrator()
    
    # Integrate all databases
    print("Starting GnosisLoom integration...")
    stats = integrator.integrate_all_databases()
    
    print("\n=== Integration Complete ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
        
    # Export report
    report_path = integrator.export_integration_report()
    print(f"\nDetailed report: {report_path}")
    
    # Test some queries
    engine = integrator.get_engine()
    
    print("\n=== Sample Queries ===")
    
    # Find entities near 7.83 Hz (Schumann resonance)
    schumann_entities = engine.find_entities_by_frequency(7.83, tolerance=0.1)
    print(f"Entities near 7.83 Hz: {len(schumann_entities)}")
    for entity in schumann_entities[:3]:
        print(f"  - {entity.name}: {entity.frequency_signature.primary_frequency} Hz")
        
    # Cross-domain connections
    if ScientificDomain.BIOLOGY in engine.domain_index and ScientificDomain.CHEMISTRY in engine.domain_index:
        connections = engine.find_cross_domain_connections(
            ScientificDomain.BIOLOGY, 
            ScientificDomain.CHEMISTRY, 
            frequency_tolerance=0.1
        )
        print(f"Biology-Chemistry frequency correlations: {len(connections)}")
        for bio_entity, chem_entity, proximity in connections[:3]:
            print(f"  - {bio_entity.name} <-> {chem_entity.name} (proximity: {proximity:.3f})")