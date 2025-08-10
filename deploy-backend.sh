#!/bin/bash

# Backend Deployment Script
# This script helps deploy the backend to various hosting platforms

set -e

echo "🚀 Backend Deployment Script"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first:"
        echo "   https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Procfile if it doesn't exist
    if [ ! -f "backend/Procfile" ]; then
        echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile
        echo "✅ Created Procfile"
    fi
    
    # Create runtime.txt if it doesn't exist
    if [ ! -f "backend/runtime.txt" ]; then
        echo "python-3.11.4" > backend/runtime.txt
        echo "✅ Created runtime.txt"
    fi
    
    # Deploy
    cd backend
    heroku create protein-ligand-viewer-$(date +%s) || true
    git add .
    git commit -m "Deploy to Heroku" || true
    git push heroku main
    
    echo "✅ Backend deployed to Heroku!"
    echo "🌐 URL: https://$(heroku info -s | grep web_url | cut -d= -f2)"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Please install it first:"
        echo "   npm install -g @railway/cli"
        exit 1
    fi
    
    # Deploy
    cd backend
    railway login
    railway init
    railway up
    
    echo "✅ Backend deployed to Railway!"
}

# Function to deploy to Vercel
deploy_vercel() {
    echo "⚡ Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI not found. Please install it first:"
        echo "   npm install -g vercel"
        exit 1
    fi
    
    # Create vercel.json if it doesn't exist
    if [ ! -f "backend/vercel.json" ]; then
        cat > backend/vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
EOF
        echo "✅ Created vercel.json"
    fi
    
    # Deploy
    cd backend
    vercel --prod
    
    echo "✅ Backend deployed to Vercel!"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    
    echo "📝 To deploy to Render:"
    echo "1. Go to https://render.com"
    echo "2. Create a new Web Service"
    echo "3. Connect your GitHub repository"
    echo "4. Set build command: pip install -r requirements.txt"
    echo "5. Set start command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Set environment variables as needed"
    echo ""
    echo "✅ Render deployment instructions provided!"
}

# Function to create Docker deployment
deploy_docker() {
    echo "🐳 Creating Docker deployment..."
    
    # Build the image
    docker build -f Dockerfile.backend -t protein-ligand-backend .
    
    echo "✅ Docker image built successfully!"
    echo "📝 To run locally: docker run -p 8000:8000 protein-ligand-backend"
    echo "📝 To push to registry: docker tag protein-ligand-backend your-registry/protein-ligand-backend"
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1) Heroku"
echo "2) Railway"
echo "3) Vercel"
echo "4) Render (instructions)"
echo "5) Docker (local)"
echo "6) Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        deploy_heroku
        ;;
    2)
        deploy_railway
        ;;
    3)
        deploy_vercel
        ;;
    4)
        deploy_render
        ;;
    5)
        deploy_docker
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo "📚 Check the documentation for more details:"
echo "   https://github.com/YOUR_USERNAME/Protein-Ligand-Interaction-Viewer" 