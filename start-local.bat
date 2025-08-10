@echo off
echo Starting Protein-Ligand Interaction Viewer locally...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Services are starting up...
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo The application will open in your browser shortly...
timeout /t 3 /nobreak > nul
start http://localhost:5173 