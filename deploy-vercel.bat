@echo off
echo 🚀 Deploying Frontend to Vercel...

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI not found. Please install it first:
    echo    npm install -g vercel
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

REM Check if .env.local exists, if not create it
if not exist ".env.local" (
    echo 📝 Creating .env.local file...
    echo VITE_API_URL=https://your-backend-url.vercel.app > .env.local
    echo VITE_DEV_MODE=false >> .env.local
    echo VITE_LOG_LEVEL=info >> .env.local
    echo VITE_ENABLE_DEBUG_PANEL=false >> .env.local
    echo VITE_ENABLE_PERFORMANCE_MONITORING=false >> .env.local
    echo.
    echo ⚠️  Please update .env.local with your actual backend API URL
    echo.
)

REM Build the project
echo 🔨 Building project...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Deploy to Vercel
echo 🚀 Deploying to Vercel...
vercel --prod

if %errorlevel% equ 0 (
    echo ✅ Frontend deployed to Vercel successfully!
    echo.
    echo 📋 Next steps:
    echo 1. Set environment variables in Vercel dashboard
    echo 2. Update VITE_API_URL to point to your backend
    echo 3. Test the deployed application
) else (
    echo ❌ Deployment failed!
)

echo.
pause 