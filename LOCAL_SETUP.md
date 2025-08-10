# 🚀 Local Setup Guide (No Docker Required)

This guide will help you run the Protein-Ligand Interaction Viewer directly on your Windows system without Docker.

## ✅ Prerequisites

- **Python 3.8+** (You have Python 3.11.4 ✓)
- **Node.js 16+** (You have Node.js v24.5.0 ✓)
- **Git** (for cloning the repository)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Yassine92-cyber/Protein-Ligand-Interaction-Viewer.git
cd Protein-Ligand-Interaction-Viewer
```

### 2. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Install Node.js Dependencies
```bash
cd frontend
npm install
cd ..
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```powershell
# Test your setup first
.\test-local.ps1

# Start the application
.\start-local.ps1
```

### Option 2: Manual Startup

1. **Start Backend Server** (Terminal 1):
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend Server** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

## 🌐 Access Your Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

### Test Your Setup
```powershell
.\test-local.ps1
```

This script will:
- Verify Python dependencies
- Check Node.js dependencies
- Test backend startup
- Validate the health endpoint

### Test the API
```bash
curl http://localhost:8000/health
```

Expected response: `{"ok": true}`

## 📁 Project Structure

```
docker/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   └── requirements.txt
├── frontend/          # React frontend
│   ├── src/          # Source code
│   └── package.json
├── start-local.ps1   # PowerShell startup script
├── start-local.bat   # Batch startup script
└── test-local.ps1    # Setup test script
```

## 🔧 Troubleshooting

### Python Import Errors
- Ensure you're in the correct directory
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r backend/requirements.txt`

### Node.js Issues
- Check Node.js version: `node --version`
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `cd frontend && npm install`

### Port Conflicts
- Backend port 8000 already in use: Change port in `backend/app/main.py`
- Frontend port 5173 already in use: Vite will automatically find another port

### RDKit Issues
- RDKit can be tricky on Windows. The current setup uses `rdkit-pypi==2023.3.1b1`
- If you encounter issues, try: `pip install rdkit-pypi==2023.3.1b1`

## 🎯 Next Steps

1. **Load Sample Data**: Use the "Load Sample Data" button in the interface
2. **Upload Structures**: Try uploading PDB and SDF files
3. **Analyze Interactions**: Configure parameters and analyze protein-ligand interactions
4. **Customize**: Modify analysis parameters and visualization options

## 📚 Additional Resources

- [Main README](README.md) - Complete project documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [DOCKER_README.md](DOCKER_README.md) - Docker setup guide

## 🆘 Need Help?

- Check the troubleshooting section above
- Review the main [README.md](README.md)
- Open an issue on GitHub
- Check the API documentation at http://localhost:8000/docs

Happy analyzing! 🧬✨ 