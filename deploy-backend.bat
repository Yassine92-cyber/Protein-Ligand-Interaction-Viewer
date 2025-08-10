@echo off
setlocal enabledelayedexpansion

echo 🚀 Backend Deployment Script
echo ==============================

REM Check if we're in the right directory
if not exist "backend\app\main.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo.
echo Choose deployment option:
echo 1) Heroku
echo 2) Railway
echo 3) Vercel
echo 4) Render (instructions)
echo 5) Docker (local)
echo 6) Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto :heroku
if "%choice%"=="2" goto :railway
if "%choice%"=="3" goto :vercel
if "%choice%"=="4" goto :render
if "%choice%"=="5" goto :docker
if "%choice%"=="6" goto :exit
goto :invalid

:heroku
echo 📦 Deploying to Heroku...
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Heroku CLI not found. Please install it first:
    echo    https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Create Procfile if it doesn't exist
if not exist "backend\Procfile" (
    echo web: uvicorn app.main:app --host 0.0.0.0 --port %%PORT > backend\Procfile
    echo ✅ Created Procfile
)

REM Create runtime.txt if it doesn't exist
if not exist "backend\runtime.txt" (
    echo python-3.11.4 > backend\runtime.txt
    echo ✅ Created runtime.txt
)

REM Deploy
cd backend
heroku create protein-ligand-viewer-%random% || echo App creation skipped
git add .
git commit -m "Deploy to Heroku" || echo Commit skipped
git push heroku main

echo ✅ Backend deployed to Heroku!
heroku info -s | findstr web_url
cd ..
goto :end

:railway
echo 🚂 Deploying to Railway...
railway --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI not found. Please install it first:
    echo    npm install -g @railway/cli
    pause
    exit /b 1
)

cd backend
railway login
railway init
railway up
cd ..

echo ✅ Backend deployed to Railway!
goto :end

:vercel
echo ⚡ Deploying to Vercel...
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI not found. Please install it first:
    echo    npm install -g vercel
    pause
    exit /b 1
)

REM Create vercel.json if it doesn't exist
if not exist "backend\vercel.json" (
    echo { > backend\vercel.json
    echo   "version": 2, >> backend\vercel.json
    echo   "builds": [ >> backend\vercel.json
    echo     { >> backend\vercel.json
    echo       "src": "app/main.py", >> backend\vercel.json
    echo       "use": "@vercel/python" >> backend\vercel.json
    echo     } >> backend\vercel.json
    echo   ], >> backend\vercel.json
    echo   "routes": [ >> backend\vercel.json
    echo     { >> backend\vercel.json
    echo       "src": "/(.*)", >> backend\vercel.json
    echo       "dest": "app/main.py" >> backend\vercel.json
    echo     } >> backend\vercel.json
    echo   ] >> backend\vercel.json
    echo } >> backend\vercel.json
    echo ✅ Created vercel.json
)

cd backend
vercel --prod
cd ..

echo ✅ Backend deployed to Vercel!
goto :end

:render
echo 🎨 Deploying to Render...
echo.
echo 📝 To deploy to Render:
echo 1. Go to https://render.com
echo 2. Create a new Web Service
echo 3. Connect your GitHub repository
echo 4. Set build command: pip install -r requirements.txt
echo 5. Set start command: uvicorn app.main:app --host 0.0.0.0 --port %%PORT
echo 6. Set environment variables as needed
echo.
echo ✅ Render deployment instructions provided!
goto :end

:docker
echo 🐳 Creating Docker deployment...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found. Please install Docker Desktop first:
    echo    https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM Build the image
docker build -f Dockerfile.backend -t protein-ligand-backend .

echo ✅ Docker image built successfully!
echo 📝 To run locally: docker run -p 8000:8000 protein-ligand-backend
echo 📝 To push to registry: docker tag protein-ligand-backend your-registry/protein-ligand-backend
goto :end

:invalid
echo ❌ Invalid choice. Please run the script again.
pause
exit /b 1

:exit
echo 👋 Goodbye!
pause
exit /b 0

:end
echo.
echo 🎉 Deployment completed!
echo 📚 Check the documentation for more details:
echo    https://github.com/YOUR_USERNAME/Protein-Ligand-Interaction-Viewer
pause 