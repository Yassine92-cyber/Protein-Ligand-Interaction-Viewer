# Protein-Ligand Interaction Viewer

A FastAPI-based web service for analyzing protein-ligand interactions using RDKit. This application provides comprehensive analysis of molecular interactions including hydrogen bonds, hydrophobic contacts, π-π stacking, salt bridges, and metal coordination.

## Features

- **Multiple Interaction Types**: Detect hydrogen bonds, hydrophobic contacts, π-π stacking, salt bridges, and metal coordination
- **Configurable Parameters**: Adjustable distance and angle thresholds for each interaction type
- **RDKit Integration**: Robust molecular parsing and analysis using RDKit
- **RESTful API**: Clean FastAPI endpoints for easy integration
- **Comprehensive Testing**: Full test suite with realistic molecular data

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Yassine92-cyber/Protein-Ligand-Interaction-Viewer.git
   cd Protein-Ligand-Interaction-Viewer
   ```

2. **Install dependencies**:
   ```bash
   make install
   ```
   
   Or manually:
   ```bash
   pip install -r backend/requirements.txt
   pip install -e .[dev]
   ```

## Usage

### Starting the Development Server

```bash
make dev
```

Or manually:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```
Returns: `{"ok": true}`

#### Analyze Interactions
```bash
POST /analyze
```

**Request Body**:
```json
{
  "pdb_text": "ATOM 1 N ALA 1 27.387 14.327 5.623...",
  "sdf_text": "benzene\n RDKit 3D\n\n 6 6 0 0 0 0...",
  "params": {
    "hbond_max_dist": 3.5,
    "hbond_min_angle": 120.0,
    "hydrophobic_max_dist": 4.0,
    "pi_stack": true,
    "salt_bridge_max_dist": 4.0,
    "metal_max_dist": 2.8
  }
}
```

**Response**:
```json
{
  "contacts": [
    {
      "type": "HBOND",
      "ligand_atom": 0,
      "protein_resi": 1,
      "protein_resn": "ALA",
      "protein_atom": "N",
      "distance": 3.2,
      "angle": 150.0
    }
  ],
  "ligand_summary": {
    "atoms": 6,
    "bonds": 6
  },
  "protein_summary": {
    "chains": 1,
    "residues": 3
  },
  "warnings": []
}
```

### Parameter Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hbond_max_dist` | 3.5 Å | Maximum distance for hydrogen bonds |
| `hbond_min_angle` | 120.0° | Minimum D-H-A angle for hydrogen bonds |
| `hydrophobic_max_dist` | 4.0 Å | Maximum distance for hydrophobic contacts |
| `pi_stack` | true | Enable π-π stacking detection |
| `salt_bridge_max_dist` | 4.0 Å | Maximum distance for salt bridges |
| `metal_max_dist` | 2.8 Å | Maximum distance for metal coordination |

## Development

### Running Tests

```bash
make test
```

### Code Formatting

```bash
make format
```

### Linting

```bash
make lint
```

### All Checks

```bash
make check
```

### Cleanup

```bash
make clean
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── schemas.py       # Pydantic data models
│   └── contacts.py      # Core interaction analysis logic
├── tests/
│   └── test_contacts.py # Test suite
└── requirements.txt      # Python dependencies

pyproject.toml           # Project configuration and dev tools
Makefile                 # Development commands
README.md               # This file
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`

## Example Usage

### Python Client

```python
import requests

# Analyze protein-ligand interactions
response = requests.post("http://localhost:8000/analyze", json={
    "pdb_text": "ATOM 1 N ALA 1 27.387 14.327 5.623...",
    "sdf_text": "benzene\n RDKit 3D\n\n 6 6 0 0 0 0...",
    "params": {
        "hbond_max_dist": 4.0,
        "pi_stack": True
    }
})

results = response.json()
print(f"Found {len(results['contacts'])} interactions")
```

### cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "pdb_text": "ATOM 1 N ALA 1 27.387 14.327 5.623...",
    "sdf_text": "benzene\n RDKit 3D\n\n 6 6 0 0 0 0...",
    "params": {
      "hbond_max_dist": 4.0,
      "pi_stack": true
    }
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `make test`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [RDKit](https://www.rdkit.org/) for molecular informatics capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## Support

For questions or issues, please open a GitHub issue or contact the maintainers. 