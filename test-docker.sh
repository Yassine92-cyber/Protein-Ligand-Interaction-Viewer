#!/bin/bash

# Test script for Docker setup
set -e

echo "🐳 Testing Docker setup for Protein-Ligand Interaction Viewer"
echo "=========================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Build images
echo "🔨 Building Docker images..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Images built successfully"
else
    echo "❌ Failed to build images"
    exit 1
fi

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
    docker-compose logs frontend
    exit 1
fi

# Test API endpoint
echo "🧪 Testing API endpoint..."
if curl -f -X POST http://localhost:8000/analyze \
    -H "Content-Type: application/json" \
    -d '{"pdb_text":"ATOM 1 N ALA 1 0.000 0.000 0.000","sdf_text":"benzene\n RDKit 3D\n\n 6 6 0 0 0 0","params":{"hbond_max_dist":3.5}}' > /dev/null 2>&1; then
    echo "✅ API endpoint is working"
else
    echo "❌ API endpoint test failed"
    docker-compose logs backend
fi

echo ""
echo "🎉 Docker setup test completed successfully!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs: make docker-logs"
echo "   Stop services: make docker-down"
echo "   Restart services: make docker-up"
echo "   Clean up: make docker-clean" 