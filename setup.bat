@echo off
echo 🌟 Setting up Spectra AI - DYNAMIC LATEST VERSIONS
echo ===================================================
echo.

echo 🐍 Creating/updating Python virtual environment...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo 📦 Installing Python dependencies (LATEST versions)...
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --upgrade --force-reinstall --no-cache-dir
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo 📱 Setting up frontend (LATEST versions)...
cd frontend
echo 🔄 Clearing npm cache...
npm cache clean --force
echo 📦 Installing latest Node.js dependencies...
npm install --save-exact=false --force
echo 🛡️ Running security audit and fixes...
npm audit fix --force
if errorlevel 1 (
    echo ⚠️ Some frontend dependencies may need attention
)

cd ..
echo.
echo ⚙️ Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file from template
    echo 📝 Please edit .env and add your API keys!
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Spectra AI setup complete!
echo.
echo 🤖 Installing Ollama (required for AI):
echo    Visit: https://ollama.ai/download
echo    Or run: winget install Ollama.Ollama
echo.
echo 📥 Pull required models:
echo    ollama pull openhermes2.5-mistral
echo    ollama pull mistral:7b
echo.
echo 🚀 To start Spectra:
echo    1. Start Ollama: ollama serve
echo    2. Run: python app.py
echo    3. In another terminal: cd frontend ^&^& npm run dev
echo    4. Open http://localhost:3000
echo.
pause
