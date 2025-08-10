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
- Node.js 16 or higher
- npm package manager

### Option 1: Local Development (Recommended for Windows)

This option runs the application directly on your system without Docker.

### Option 2: Docker Deployment

If you prefer to use Docker containers, you'll need:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- At least 4GB RAM available

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Yassine92-cyber/Protein-Ligand-Interaction-Viewer.git
   cd Protein-Ligand-Interaction-Viewer
   ```

#### For Local Development (Windows)

2. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Test your setup**:
   ```powershell
   .\test-local.ps1
   ```

#### For Docker Deployment

2. **Install dependencies**:
   ```bash
   make install
   ```
   
   Or manually:
   ```bash
   pip install -r backend/requirements.txt
   pip install -e .[dev]
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment**:
   ```bash
   # Copy the example environment file
   cp frontend/env.example frontend/.env.local
   
   # Edit .env.local if you need to change the API URL
   ```

## 📁 Sample Data

The application includes sample data to get you started:

- **Sample Protein-Ligand Complex**: Use the "Load Sample Data" button in the interface
- **Public PDB Structures**: Try these well-known protein-ligand complexes:
  - **1A4W**: HIV-1 protease with inhibitor (small, well-studied)
  - **3PTB**: Trypsin with benzamidine (classic serine protease)
  - **1HCL**: Human carbonic anhydrase with inhibitor
  - **2PTC**: Trypsin with pancreatic trypsin inhibitor
  - **1TIM**: Triosephosphate isomerase (enzyme without ligand)

To use public PDBs:
1. Download PDB files from [RCSB PDB](https://www.rcsb.org/)
2. Upload the PDB file in the interface
3. For ligands, you can extract them from the PDB or find matching SDF files

## Usage

### Docker Deployment

```bash
# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development (No Docker Required)

#### Quick Start (Windows)

```powershell
# Test your setup first
.\test-local.ps1

# Start the application
.\start-local.ps1
```

#### Manual Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

2. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the frontend server (in a new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

#### Using Make (if available)

```bash
# Start both backend and frontend concurrently
make dev

# Or start services separately
make dev-backend    # Backend only
cd frontend && npm run dev  # Frontend only
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`

## 🚀 GitHub Deployment

### Frontend (GitHub Pages)
The frontend automatically deploys to GitHub Pages on every push to the `main` branch.

### Backend Deployment
Use the deployment scripts to deploy the backend to various platforms:

**Windows:**
```batch
.\deploy-backend.bat
```

**Linux/Mac:**
```bash
./deploy-backend.sh
```

**Supported Platforms:**
- Heroku
- Railway
- Vercel
- Render
- Docker

### GitHub Actions
The project includes automated CI/CD pipelines:
- **CI Pipeline**: Tests backend and frontend on multiple platforms
- **Deploy Pipeline**: Automatically deploys frontend to GitHub Pages
- **Docker Testing**: Builds and tests Docker containers

For detailed GitHub setup instructions, see [GITHUB_SETUP.md](GITHUB_SETUP.md).

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