# Test script for Docker setup (PowerShell)
param(
    [switch]$SkipBuild
)

Write-Host "🐳 Testing Docker setup for Protein-Ligand Interaction Viewer" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose is not installed. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Build images (unless skipped)
if (-not $SkipBuild) {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
    docker-compose build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Images built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build images" -ForegroundColor Red
        exit 1
    }
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow

# Check backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
        docker-compose logs backend
        exit 1
    }
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
    docker-compose logs backend
    exit 1
}

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend is not accessible" -ForegroundColor Red
        docker-compose logs frontend
        exit 1
    }
} catch {
    Write-Host "❌ Frontend is not accessible" -ForegroundColor Red
    docker-compose logs frontend
    exit 1
}

# Test API endpoint
Write-Host "🧪 Testing API endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        pdb_text = "ATOM 1 N ALA 1 0.000 0.000 0.000"
        sdf_text = "benzene`n RDKit 3D`n`n 6 6 0 0 0 0"
        params = @{
            hbond_max_dist = 3.5
        }
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/analyze" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API endpoint is working" -ForegroundColor Green
    } else {
        Write-Host "❌ API endpoint test failed" -ForegroundColor Red
        docker-compose logs backend
    }
} catch {
    Write-Host "❌ API endpoint test failed" -ForegroundColor Red
    docker-compose logs backend
}

Write-Host ""
Write-Host "🎉 Docker setup test completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: make docker-logs" -ForegroundColor White
Write-Host "   Stop services: make docker-down" -ForegroundColor White
Write-Host "   Restart services: make docker-up" -ForegroundColor White
Write-Host "   Clean up: make docker-clean" -ForegroundColor White 