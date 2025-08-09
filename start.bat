@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    🚀 Spectra AI Production Startup
echo ============================================
echo.

REM Set color to green for startup
color 0A

REM Check if we're using FastAPI or Flask
if exist "main.py" (
    set "backend_cmd=python main.py"
    set "backend_name=FastAPI Backend"
) else (
    set "backend_cmd=python app.py"
    set "backend_name=Flask Backend (Legacy)"
)

REM Initialize variables
set "all_good=true"

echo 🔍 Checking prerequisites...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not installed
    set "all_good=false"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
    echo ✅ Python !python_version! found
)

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not installed
    set "all_good=false"
) else (
    for /f %%i in ('node --version') do set "node_version=%%i"
    echo ✅ Node.js !node_version! found
)

REM Check Ollama installation
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not installed
    set "all_good=false"
) else (
    echo ✅ Ollama found
)

if "%all_good%"=="false" (
    echo.
    echo ❌ Missing prerequisites! Please run setup.bat first
    pause
    exit /b 1
)

echo.
echo ✅ All prerequisites satisfied!
echo.

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo 🚀 Starting services...
echo.

REM Start Ollama service first
echo 🤖 Starting Ollama AI service...
start "Ollama Service" cmd /c "ollama serve"
timeout /t 5 /nobreak >nul

REM Start backend
echo 🐍 Starting %backend_name%...
start "Spectra Backend" cmd /c "%backend_cmd%"
timeout /t 5 /nobreak >nul

REM Start frontend
echo 📱 Starting frontend...
if exist "frontend\package.json" (
    cd frontend
    start "Spectra Frontend" cmd /c "npm run dev"
    cd ..
) else (
    echo ⚠️  Frontend not found
)

echo.
echo ============================================
echo    🎉 Spectra AI Started Successfully!
echo ============================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000 (FastAPI) or :5000 (Flask)
echo 🤖 Ollama:   http://localhost:11434
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit (services will continue running)...
pause >nul