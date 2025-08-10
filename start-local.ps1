# Start Protein-Ligand Interaction Viewer locally
Write-Host "Starting Protein-Ligand Interaction Viewer locally..." -ForegroundColor Green
Write-Host ""

# Check if Python and Node.js are available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Start Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Services are starting up..." -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Wait for user input
Write-Host "Press any key to open the frontend in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open frontend in browser
Start-Process "http://localhost:5173"
Write-Host "Frontend opened in browser!" -ForegroundColor Green 