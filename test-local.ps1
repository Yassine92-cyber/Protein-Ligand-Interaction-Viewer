# Test local setup
Write-Host "Testing local setup..." -ForegroundColor Green
Write-Host ""

# Test Python imports
Write-Host "Testing Python dependencies..." -ForegroundColor Yellow
try {
    cd backend
    python -c "import fastapi, uvicorn, rdkit, numpy, scipy, pandas; print('✓ All Python dependencies imported successfully')"
    cd ..
} catch {
    Write-Host "✗ Python dependencies test failed" -ForegroundColor Red
    exit 1
}

# Test Node.js dependencies
Write-Host "Testing Node.js dependencies..." -ForegroundColor Yellow
try {
    cd frontend
    if (Test-Path "node_modules") {
        Write-Host "✓ Node.js dependencies found" -ForegroundColor Green
    } else {
        Write-Host "✗ Node.js dependencies not found. Run 'npm install' first" -ForegroundColor Red
        exit 1
    }
    cd ..
} catch {
    Write-Host "✗ Node.js dependencies test failed" -ForegroundColor Red
    exit 1
}

# Test backend startup
Write-Host "Testing backend startup..." -ForegroundColor Yellow
try {
    cd backend
    $process = Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -PassThru
    Start-Sleep -Seconds 5
    
    # Test health endpoint
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        if ($response.ok -eq $true) {
            Write-Host "✓ Backend health check passed" -ForegroundColor Green
        } else {
            Write-Host "✗ Backend health check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Backend health check failed: $_" -ForegroundColor Red
    }
    
    # Stop the backend
    Stop-Process -Id $process.Id -Force
    cd ..
} catch {
    Write-Host "✗ Backend startup test failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Local setup test completed!" -ForegroundColor Green
Write-Host "You can now run 'start-local.ps1' to start the application" -ForegroundColor Cyan 