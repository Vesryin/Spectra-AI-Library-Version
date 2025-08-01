@echo off
title Spectra AI - Complete Dynamic Startup

echo 🌟 SPECTRA AI - COMPLETE DYNAMIC STARTUP
echo ==========================================
echo.

echo 🔍 System Check...
echo.

REM Check all prerequisites
set "all_good=true"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not installed
    set "all_good=false"
) else (
    echo ✅ Python installed
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not installed
    set "all_good=false"
) else (
    echo ✅ Node.js installed
)

REM Check Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not installed
    set "all_good=false"
) else (
    echo ✅ Ollama installed
)

if "%all_good%"=="false" (
    echo.
    echo ❌ Missing prerequisites! Please install:
    echo   - Python 3.8+ from python.org
    echo   - Node.js 16+ from nodejs.org  
    echo   - Ollama from ollama.ai
    pause
    exit /b 1
)

echo.
echo 🚀 Starting all services dynamically...
echo.

echo 1️⃣ Starting Ollama service...
start "Ollama" cmd /c "start-ollama.bat"
timeout /t 5 >nul

echo 2️⃣ Starting Backend API...
start "Backend" cmd /c "start-backend.bat"
timeout /t 5 >nul

echo 3️⃣ Starting Frontend UI...
start "Frontend" cmd /c "start-frontend.bat"
timeout /t 3 >nul

echo.
echo ✅ All services starting up!
echo.
echo 🌐 Spectra AI will be available at:
echo   🤖 Ollama:   http://localhost:11434
echo   🐍 Backend:  http://localhost:5000  
echo   ⚛️ Frontend: http://localhost:3000+ (auto-port)
echo.
echo 💜 Spectra AI is ready for emotionally intelligent conversations!
echo.
pause
