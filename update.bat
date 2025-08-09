@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    🔄 Spectra AI Dynamic Update
echo ============================================
echo.

color 0E

echo 🔄 Updating all components to latest versions...
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️ Virtual environment not found - run setup.bat first
    pause
    exit /b 1
)

REM Update pip itself
echo 📈 Updating pip to latest...
python -m pip install --upgrade pip

REM Update all Python packages to latest
echo 🐍 Updating Python dependencies to latest versions...
pip install --upgrade -r requirements.txt

REM Show what was updated
echo 📋 Current Python package versions:
pip list --format=columns

REM Update frontend dependencies
if exist "frontend\package.json" (
    echo.
    echo 📱 Updating frontend dependencies...
    cd frontend
    
    REM Update npm itself
    npm install -g npm@latest
    
    REM Update all packages
    npm update
    
    REM Show outdated packages (if any)
    echo 📋 Checking for any remaining outdated packages...
    npm outdated
    
    cd ..
) else (
    echo ⚠️ Frontend directory not found
)

REM Update Ollama models
echo.
echo 🤖 Updating AI models...
ollama list | findstr "llama3.2:1b" >nul
if not errorlevel 1 (
    echo 🔄 Updating llama3.2:1b model...
    ollama pull llama3.2:1b
) else (
    echo 📥 Installing llama3.2:1b model...
    ollama pull llama3.2:1b
)

REM Check for other available models
echo 📋 Available models:
ollama list

echo.
echo ============================================
echo    ✅ Update Complete!
echo ============================================
echo.
echo 🎉 All components updated to latest versions
echo 🚀 Ready to run with: start.bat
echo.
pause