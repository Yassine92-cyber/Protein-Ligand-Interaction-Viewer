# 🚀 Quick Start Guide

Get your Protein-Ligand Interaction Viewer up and running in minutes!

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- At least 4GB RAM available

## 1. Clone and Navigate

```bash
git clone https://github.com/Yassine92-cyber/Protein-Ligand-Interaction-Viewer.git
cd Protein-Ligand-Interaction-Viewer
```

## 2. Start the Application

```bash
# Build and start all services
docker-compose up --build

# Or use the Makefile
make docker-up
```

## 3. Access Your Application

- **🌐 Frontend**: http://localhost
- **🔌 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 4. Test the Setup

```bash
# Run the test script (PowerShell on Windows)
.\test-docker.ps1

# Or test manually
curl http://localhost:8000/health
```

## 5. Stop When Done

```bash
# Stop all services
docker-compose down

# Or use the Makefile
make docker-down
```

## 🎯 What's Next?

1. **Try Sample Data**: Click "Load Sample Data" to see a pre-loaded protein-ligand complex
2. **Upload Structures**: Use the web interface to upload PDB and SDF files
3. **Analyze Interactions**: Configure parameters and analyze protein-ligand interactions
4. **View Results**: Explore the detected contacts and molecular visualizations
5. **Customize**: Modify analysis parameters and visualization options

## 📁 Sample Data

The app includes sample data to get you started:
- **Sample Protein-Ligand Complex**: A small protein with a ligand for testing
- **Public PDBs to Try**: 1A4W, 3PTB, 1HCL, 2PTC, 1TIM

## 🛠️ Development

For development with hot-reload:

```bash
# Start both backend and frontend concurrently
make dev

# Or start services separately
make dev-backend    # Backend only
cd frontend && npm run dev  # Frontend only
```

## 🆘 Need Help?

- **Docker Issues**: See [DOCKER_README.md](DOCKER_README.md)
- **Application Issues**: See [README.md](README.md)
- **API Reference**: Visit http://localhost:8000/docs

## 🧪 Sample Data

Try these sample structures to test the application:

### Simple Protein (PDB)
```
ATOM      1  N   ALA     1      27.387  14.327   5.623  1.00 20.00
ATOM      2  CA  ALA     1      26.123  14.327   6.456  1.00 20.00
ATOM      3  C   ALA     1      25.456  15.678   6.456  1.00 20.00
ATOM      4  O   ALA     1      25.456  16.234   7.456  1.00 20.00
```

### Simple Ligand (SDF)
```
benzene
 RDKit 3D

  6  6  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.3950    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.0900    1.2080    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.3950    2.4160    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    2.4160    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.6950    1.2080    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  2  3  2  0  0  0  0
  3  4  2  0  0  0  0
  4  5  2  0  0  0  0
  5  6  2  0  0  0  0
  6  1  2  0  0  0  0
M  END
```

Happy analyzing! 🧬✨ 