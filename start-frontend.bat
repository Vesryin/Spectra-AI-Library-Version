@echo off
title Spectra AI - Dynamic Frontend

echo ⚛️ Starting Dynamic Spectra AI Frontend
echo ==========================================
echo.

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js 16+
    echo Download from: https://nodejs.org
    pause
    exit /b 1
)

echo 🔍 Node.js version:
node --version
echo.

echo 🔍 npm version:
npm --version
echo.

REM Navigate to frontend directory
if not exist "frontend" (
    echo ❌ Frontend directory not found!
    pause
    exit /b 1
)

cd frontend

REM Check and install/update dependencies
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
) else (
    echo � Checking dependencies...
    echo ✅ Dependencies ready
)

if errorlevel 1 (
    echo ⚠️ Some packages may have failed to install
    echo Trying npm install again...
    npm install
)

REM Check if backend is running
echo 🔗 Checking backend connection...
curl -s http://localhost:5000/api/status >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend not responding on port 5000
    echo Make sure to run start-backend.bat first
) else (
    echo ✅ Backend connection successful
)

REM Find available port
set PORT=3000
:check_port
netstat -an | findstr ":!PORT!" >nul 2>&1
if not errorlevel 1 (
    set /a PORT+=1
    if !PORT! GTR 3010 (
        echo ❌ No available ports found
        pause
        exit /b 1
    )
    goto check_port
)

echo.
echo 🚀 Starting Vite development server...
echo Frontend will be available at: http://localhost:!PORT!
echo.
echo 🎯 Spectra AI Interface Features:
echo   - Real-time chat with Spectra
echo   - Emotional intelligence responses  
echo   - Dynamic model switching
echo   - Auto-reconnection
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Vite with dynamic port
npm run dev -- --port !PORT!
