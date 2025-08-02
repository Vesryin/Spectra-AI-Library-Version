@echo off
title Spectra AI - Modern Production Startup

echo 🌟 SPECTRA AI - MODERN PRODUCTION STARTUP
echo ============================================
echo FastAPI + React + Ollama
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
where node >nul 2>&1
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
echo 🚀 Starting all services with modern architecture...
echo.

echo 1️⃣ Starting Ollama service...
start "Ollama" cmd /c "ollama serve"
timeout /t 5 >nul

echo 2️⃣ Starting FastAPI Backend...
start "FastAPI Backend" cmd /c "cd /d "%~dp0" && C:/Users/PAC/Spectra-AI-Library-Version/.venv/Scripts/python.exe main.py"
timeout /t 5 >nul

echo 3️⃣ Starting React Frontend...
start "React Frontend" cmd /c "cd /d "%~dp0\frontend" && npm run dev"
timeout /t 3 >nul

echo.
echo ✅ All services starting up!
echo.
echo 🌐 Spectra AI will be available at:
echo   🤖 Ollama:        http://localhost:11434
echo   ⚡ FastAPI:       http://localhost:5000  
echo   📚 API Docs:      http://localhost:5000/docs
echo   ⚛️ React App:     http://localhost:3000
echo.
echo 💜 Spectra AI is ready for emotionally intelligent conversations!
echo    - Modern FastAPI backend with async support
echo    - Updated React frontend with latest dependencies  
echo    - Real-time AI integration with Ollama
echo.
pause
