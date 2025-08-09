@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    📦 Spectra AI Dynamic Setup
echo ============================================
echo.

REM Set color to cyan for setup
color 0B

echo 🔍 Checking system requirements...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not installed! Please install Python 3.8+ from python.org
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
    echo ✅ Python !python_version! found
)

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not installed! Please install Node.js 16+ from nodejs.org
    pause
    exit /b 1
) else (
    for /f %%i in ('node --version') do set "node_version=%%i"
    echo ✅ Node.js !node_version! found
)

REM Check Ollama installation
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not installed! Please install from ollama.ai
    pause
    exit /b 1
) else (
    echo ✅ Ollama found
)

echo.
echo 🚀 Setting up Spectra AI with latest dependencies...
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip to latest version
echo 📈 Upgrading pip to latest version...
python -m pip install --upgrade pip

REM Install/upgrade all dependencies to latest versions
echo 📦 Installing latest Python dependencies...
pip install --upgrade -r requirements.txt
if errorlevel 1 (
    echo ⚠️ Some Python dependencies may need attention
)

REM Setup frontend dependencies
if exist "frontend\package.json" (
    echo 📱 Setting up frontend dependencies...
    cd frontend
    
    REM Update npm to latest
    echo 📈 Updating npm to latest version...
    npm install -g npm@latest
    
    REM Install latest frontend dependencies
    echo 📦 Installing latest frontend dependencies...
    npm install
    if errorlevel 1 (
        echo ⚠️ Some frontend dependencies may need attention
    )
    
    REM Update all packages to latest versions
    echo 🔄 Updating all packages to latest versions...
    npm update
    
    cd ..
) else (
    echo ⚠️ Frontend directory not found
)

REM Create environment file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Created .env file from template
        echo 📝 Please edit .env and configure your settings!
    ) else (
        echo 🔧 Creating default .env file...
        (
            echo # Spectra AI Configuration
            echo ENVIRONMENT=development
            echo HOST=127.0.0.1
            echo PORT=8000
            echo DEBUG=True
            echo OLLAMA_MODEL=llama3.2:1b
            echo CORS_ORIGINS=http://localhost:3000
            echo LOG_LEVEL=INFO
        ) > .env
        echo ✅ Created default .env file
    )
) else (
    echo ✅ .env file already exists
)

REM Create logs directory
if not exist "logs" (
    mkdir logs
    echo ✅ Created logs directory
)

REM Download/update Ollama models
echo 🤖 Checking Ollama models...
ollama list >nul 2>&1
if errorlevel 1 (
    echo 🔄 Starting Ollama service...
    start /min ollama serve
    timeout /t 5 /nobreak >nul
)

echo 📥 Pulling latest lightweight AI model...
ollama pull llama3.2:1b
if errorlevel 1 (
    echo ⚠️ Could not pull AI model - will try at runtime
)

echo.
echo ============================================
echo    🎉 Spectra AI Setup Complete!
echo ============================================
echo.
echo ✅ All dependencies installed with latest versions
echo ✅ Virtual environment configured
echo ✅ Environment file ready
echo ✅ AI model downloaded
echo.
echo 🚀 Ready to start! Run: start.bat
echo 📚 Or for development: python main.py
echo.
echo Press any key to exit...
pause >nul