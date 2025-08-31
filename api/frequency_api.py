#!/usr/bin/env python3
"""
GnosisLoom Frequency API

A simple REST API for programmatic access to the biological frequency database.
Provides endpoints for querying frequency signatures, stellar anchors, and 
harmonic relationships.

Usage:
    python3 frequency_api.py [--port 8080] [--host localhost]

API Endpoints:
    GET /frequencies - List all biological frequencies
    GET /frequencies/{name} - Get specific frequency by name
    GET /stellar-anchors - List all stellar anchors
    GET /stellar-anchors/{name} - Get specific stellar anchor
    GET /harmonics/{frequency} - Find harmonic relationships
    GET /search?q={query} - Search frequencies by keyword
    GET /golden-ratio - Find golden ratio relationships
    GET /health - API health check
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GnosisLoomAPI:
    def __init__(self, data_path: str = "../data"):
        self.data_path = Path(data_path)
        self.frequencies = {}
        self.stellar_anchors = {}
        self.feedback_loops = {}
        self.load_data()
        
    def load_data(self):
        """Load all data files into memory"""
        try:
            # Load biological frequencies
            freq_file = self.data_path / "comprehensive_frequencies.json"
            if freq_file.exists():
                with open(freq_file, 'r') as f:
                    self.frequencies = json.load(f)
                logger.info(f"Loaded {len(self.frequencies)} frequency entries")
            
            # Load stellar anchors
            anchor_file = self.data_path / "comprehensive_stellar_anchors.json"
            if anchor_file.exists():
                with open(anchor_file, 'r') as f:
                    self.stellar_anchors = json.load(f)
                logger.info(f"Loaded {len(self.stellar_anchors)} stellar anchors")
            
            # Load feedback loops
            loops_file = self.data_path / "feedback_loops.json"
            if loops_file.exists():
                with open(loops_file, 'r') as f:
                    self.feedback_loops = json.load(f)
                logger.info(f"Loaded {len(self.feedback_loops)} feedback loops")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def find_harmonic_relationships(self, target_freq: float, tolerance: float = 0.1) -> List[Dict]:
        """Find harmonic relationships for a target frequency"""
        relationships = []
        
        for name, data in self.frequencies.items():
            if not isinstance(data, dict):
                continue
                
            freq = data.get('normal_freq') or data.get('frequency')
            if not freq or not isinstance(freq, (int, float)):
                continue
            
            # Check harmonic ratios
            for ratio in [0.5, 2.0, 3.0, 4.0, 1.5, 2.5, 1.618, 0.618]:  # Include golden ratio
                expected = target_freq * ratio
                deviation = abs(freq - expected) / expected
                
                if deviation <= tolerance:
                    relationships.append({
                        'frequency_name': name,
                        'frequency': freq,
                        'ratio': ratio,
                        'expected': expected,
                        'deviation': deviation,
                        'relationship_type': self._classify_relationship(ratio)
                    })
        
        # Sort by deviation (closest matches first)
        return sorted(relationships, key=lambda x: x['deviation'])
    
    def _classify_relationship(self, ratio: float) -> str:
        """Classify the type of harmonic relationship"""
        if abs(ratio - 2.0) < 0.1:
            return "octave"
        elif abs(ratio - 0.5) < 0.1:
            return "sub-octave"
        elif abs(ratio - 1.618) < 0.1:
            return "golden_ratio"
        elif abs(ratio - 0.618) < 0.1:
            return "inverse_golden_ratio"
        elif abs(ratio - 3.0) < 0.1:
            return "perfect_fifth"
        elif abs(ratio - 1.5) < 0.1:
            return "perfect_fourth"
        else:
            return "harmonic_series"
    
    def find_golden_ratio_relationships(self, tolerance: float = 0.1) -> List[Dict]:
        """Find all golden ratio relationships in the database"""
        golden_phi = 1.618033988749
        relationships = []
        
        freq_list = []
        for name, data in self.frequencies.items():
            if isinstance(data, dict):
                freq = data.get('normal_freq') or data.get('frequency')
                if freq and isinstance(freq, (int, float)):
                    freq_list.append({'name': name, 'frequency': freq})
        
        # Compare all pairs
        for i, freq1 in enumerate(freq_list):
            for freq2 in freq_list[i+1:]:
                if freq2['frequency'] > 0:
                    ratio = freq1['frequency'] / freq2['frequency']
                    
                    # Check both directions for golden ratio
                    for target_ratio, name in [(golden_phi, 'golden_ratio'), (1/golden_phi, 'inverse_golden_ratio')]:
                        deviation = abs(ratio - target_ratio) / target_ratio
                        if deviation <= tolerance:
                            relationships.append({
                                'frequency1': freq1,
                                'frequency2': freq2,
                                'ratio': ratio,
                                'target_ratio': target_ratio,
                                'deviation': deviation,
                                'relationship_type': name
                            })
        
        return sorted(relationships, key=lambda x: x['deviation'])
    
    def search_frequencies(self, query: str) -> List[Dict]:
        """Search frequencies by keyword"""
        query = query.lower()
        results = []
        
        for name, data in self.frequencies.items():
            if isinstance(data, dict):
                # Search in frequency name
                if query in name.lower():
                    result = {'name': name, 'data': data, 'match_type': 'name'}
                    results.append(result)
                    continue
                
                # Search in stellar anchor
                anchor = data.get('stellar_anchor', '')
                if isinstance(anchor, str) and query in anchor.lower():
                    result = {'name': name, 'data': data, 'match_type': 'stellar_anchor'}
                    results.append(result)
                    continue
                
                # Search in tags or categories if they exist
                for key, value in data.items():
                    if isinstance(value, str) and query in value.lower():
                        result = {'name': name, 'data': data, 'match_type': key}
                        results.append(result)
                        break
        
        return results

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web applications

# Initialize API
try:
    api = GnosisLoomAPI()
except Exception as e:
    logger.error(f"Failed to initialize API: {e}")
    api = None

@app.route('/health')
def health_check():
    """API health check"""
    status = {
        'status': 'healthy' if api else 'error',
        'data_loaded': {
            'frequencies': len(api.frequencies) if api else 0,
            'stellar_anchors': len(api.stellar_anchors) if api else 0,
            'feedback_loops': len(api.feedback_loops) if api else 0
        }
    }
    return jsonify(status)

@app.route('/frequencies')
def get_frequencies():
    """Get all biological frequencies"""
    if not api:
        abort(500, description="API not initialized")
    
    # Return summary with pagination support
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    freq_list = []
    for name, data in api.frequencies.items():
        if isinstance(data, dict):
            freq = data.get('normal_freq') or data.get('frequency')
            summary = {
                'name': name,
                'frequency': freq,
                'stellar_anchor': data.get('stellar_anchor'),
                'category': data.get('category', 'biological_system')
            }
            freq_list.append(summary)
    
    # Simple pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = freq_list[start:end]
    
    return jsonify({
        'frequencies': paginated,
        'total': len(freq_list),
        'page': page,
        'per_page': per_page,
        'pages': math.ceil(len(freq_list) / per_page)
    })

@app.route('/frequencies/<name>')
def get_frequency(name):
    """Get specific frequency by name"""
    if not api:
        abort(500, description="API not initialized")
    
    if name not in api.frequencies:
        abort(404, description="Frequency not found")
    
    return jsonify({
        'name': name,
        'data': api.frequencies[name]
    })

@app.route('/stellar-anchors')
def get_stellar_anchors():
    """Get all stellar anchors"""
    if not api:
        abort(500, description="API not initialized")
    
    return jsonify({
        'stellar_anchors': api.stellar_anchors,
        'count': len(api.stellar_anchors)
    })

@app.route('/stellar-anchors/<name>')
def get_stellar_anchor(name):
    """Get specific stellar anchor by name"""
    if not api:
        abort(500, description="API not initialized")
    
    if name not in api.stellar_anchors:
        abort(404, description="Stellar anchor not found")
    
    return jsonify({
        'name': name,
        'data': api.stellar_anchors[name]
    })

@app.route('/harmonics/<float:frequency>')
def get_harmonics(frequency):
    """Find harmonic relationships for a frequency"""
    if not api:
        abort(500, description="API not initialized")
    
    tolerance = request.args.get('tolerance', 0.1, type=float)
    relationships = api.find_harmonic_relationships(frequency, tolerance)
    
    return jsonify({
        'target_frequency': frequency,
        'tolerance': tolerance,
        'relationships': relationships,
        'count': len(relationships)
    })

@app.route('/search')
def search_frequencies():
    """Search frequencies by keyword"""
    if not api:
        abort(500, description="API not initialized")
    
    query = request.args.get('q', '')
    if not query:
        abort(400, description="Query parameter 'q' is required")
    
    results = api.search_frequencies(query)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/golden-ratio')
def get_golden_ratio():
    """Find all golden ratio relationships"""
    if not api:
        abort(500, description="API not initialized")
    
    tolerance = request.args.get('tolerance', 0.1, type=float)
    relationships = api.find_golden_ratio_relationships(tolerance)
    
    return jsonify({
        'golden_ratio': 1.618033988749,
        'tolerance': tolerance,
        'relationships': relationships,
        'count': len(relationships)
    })

@app.route('/feedback-loops')
def get_feedback_loops():
    """Get all feedback loops"""
    if not api:
        abort(500, description="API not initialized")
    
    return jsonify({
        'feedback_loops': api.feedback_loops,
        'count': len(api.feedback_loops)
    })

@app.route('/')
def api_info():
    """API information and documentation"""
    return jsonify({
        'name': 'GnosisLoom Frequency API',
        'version': '1.0.0',
        'description': 'REST API for biological frequency database',
        'endpoints': {
            'GET /frequencies': 'List all biological frequencies (paginated)',
            'GET /frequencies/{name}': 'Get specific frequency by name',
            'GET /stellar-anchors': 'List all stellar anchors',
            'GET /stellar-anchors/{name}': 'Get specific stellar anchor',
            'GET /harmonics/{frequency}': 'Find harmonic relationships (tolerance param)',
            'GET /search?q={query}': 'Search frequencies by keyword',
            'GET /golden-ratio': 'Find golden ratio relationships (tolerance param)',
            'GET /feedback-loops': 'List all feedback loops',
            'GET /health': 'API health check'
        },
        'data_summary': {
            'frequencies': len(api.frequencies) if api else 0,
            'stellar_anchors': len(api.stellar_anchors) if api else 0,
            'feedback_loops': len(api.feedback_loops) if api else 0
        }
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GnosisLoom Frequency API Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    logger.info(f"Starting GnosisLoom API on {args.host}:{args.port}")
    logger.info("API Endpoints available:")
    logger.info("  GET / - API information")
    logger.info("  GET /frequencies - List frequencies")
    logger.info("  GET /harmonics/{freq} - Find harmonics")
    logger.info("  GET /search?q={query} - Search frequencies")
    logger.info("  GET /golden-ratio - Golden ratio analysis")
    
    app.run(host=args.host, port=args.port, debug=args.debug)