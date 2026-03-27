# GnosisLoom REST API

A simple REST API for programmatic access to the biological frequency database.

## Quick Start

```bash
cd api/
pip install -r requirements.txt
python3 frequency_api.py --port 8080
```

## API Endpoints

### Core Data Access
- `GET /` - API information and endpoint documentation
- `GET /health` - Health check and data loading status
- `GET /frequencies` - List all biological frequencies (paginated)
- `GET /frequencies/{name}` - Get specific frequency by name
- `GET /stellar-anchors` - List all stellar anchor systems
- `GET /stellar-anchors/{name}` - Get specific stellar anchor data

### Analysis & Search
- `GET /harmonics/{frequency}?tolerance=0.1` - Find harmonic relationships
- `GET /search?q={query}` - Search frequencies by keyword
- `GET /golden-ratio?tolerance=0.1` - Find golden ratio relationships
- `GET /feedback-loops` - List all documented feedback loops

## Example Usage

### Python
```python
import requests

# Get all frequencies
response = requests.get('http://localhost:8080/frequencies')
frequencies = response.json()

# Find harmonics of 13.5 Hz (DMT consciousness interface)
response = requests.get('http://localhost:8080/harmonics/13.5')
harmonics = response.json()

# Search for heart-related frequencies
response = requests.get('http://localhost:8080/search?q=heart')
results = response.json()
```

### JavaScript
```javascript
// Get stellar anchors
fetch('http://localhost:8080/stellar-anchors')
  .then(response => response.json())
  .then(data => console.log(data));

// Find golden ratio relationships
fetch('http://localhost:8080/golden-ratio')
  .then(response => response.json())
  .then(data => console.log(data));
```

### curl
```bash
# API health check
curl http://localhost:8080/health

# Get frequency data
curl http://localhost:8080/frequencies/mitochondria

# Search frequencies
curl "http://localhost:8080/search?q=brain"
```

## Response Format

All endpoints return JSON with consistent structure:

```json
{
  "data": {},
  "count": 42,
  "status": "success"
}
```

## Configuration

```bash
python3 frequency_api.py --help

Options:
  --host HOST      Host to bind to (default: localhost)
  --port PORT      Port to bind to (default: 8080)
  --debug         Enable debug mode
```

## CORS Support

The API includes CORS headers for web application integration.