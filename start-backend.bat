@echo off
title Spectra AI - Dynamic Backend

echo 🐍 Starting Dynamic Spectra AI Backend
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo 🔍 Python version:
python --version
echo.

REM Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo 📦 Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo 🌟 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check and install/update requirements
if exist requirements.txt (
    echo 📋 Checking Python dependencies...
    pip install -r requirements.txt --upgrade --quiet
    if errorlevel 1 (
        echo ⚠️ Some packages may have failed to install
    ) else (
        echo ✅ Dependencies ready
    )
) else (
    echo ⚠️ requirements.txt not found, installing core packages...
    pip install flask flask-cors python-dotenv ollama gunicorn uvicorn requests --upgrade --no-cache-dir
)

REM Check .env file
if not exist ".env" (
    echo ⚠️ .env file not found
    if exist ".env.example" (
        echo 📝 Copying .env.example to .env...
        copy .env.example .env >nul
    ) else (
        echo 📝 Creating basic .env file...
        echo FLASK_ENV=development > .env
        echo FLASK_DEBUG=True >> .env
        echo OLLAMA_MODEL=openhermes:7b-mistral-v2.5-q4_K_M >> .env
        echo SECRET_KEY=dynamic-spectra-key >> .env
    )
)

REM Check Ollama connection
echo 🤖 Testing Ollama connection...
python -c "import ollama; print('✅ Ollama connection successful')" 2>nul
if errorlevel 1 (
    echo ⚠️ Ollama connection failed - make sure Ollama is running
    echo Run start-ollama.bat first
)

echo.
echo 🚀 Starting Flask backend server...
echo Backend will be available at: http://localhost:5000
echo API endpoints:
echo   - GET  /api/status  (Health check)
echo   - POST /api/chat    (Chat with Spectra)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python app.py
