#!/bin/bash

echo "🚀 Deploying Frontend to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "   npm install -g vercel"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if .env.local exists, if not create it
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    cat > .env.local << EOF
VITE_API_URL=https://your-backend-url.vercel.app
VITE_DEV_MODE=false
VITE_LOG_LEVEL=info
VITE_ENABLE_DEBUG_PANEL=false
VITE_ENABLE_PERFORMANCE_MONITORING=false
EOF
    echo ""
    echo "⚠️  Please update .env.local with your actual backend API URL"
    echo ""
fi

# Build the project
echo "🔨 Building project..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

if [ $? -eq 0 ]; then
    echo "✅ Frontend deployed to Vercel successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Set environment variables in Vercel dashboard"
    echo "2. Update VITE_API_URL to point to your backend"
    echo "3. Test the deployed application"
else
    echo "❌ Deployment failed!"
fi

echo "" 