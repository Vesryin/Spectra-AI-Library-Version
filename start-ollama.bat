@echo off
setlocal enabledelayedexpansion
title Spectra AI - Dynamic Ollama Service

echo 🤖 Starting Dynamic Ollama Service for Spectra AI
echo =====================================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not found! Please install Ollama first.
    echo Download from: https://ollama.ai
    pause
    exit /b 1
)

echo 🔍 Ollama version:
ollama --version
echo.

REM Check if already running
netstat -an | findstr ":11434" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Ollama already running on port 11434
    echo.
    echo 📋 Current models:
    ollama list
    echo.
    echo 🧠 Testing Spectra's preferred model...
    set PREFERRED_MODEL=openhermes:7b-mistral-v2.5-q4_K_M
    ollama list | findstr "!PREFERRED_MODEL!" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Preferred model available: !PREFERRED_MODEL!
        echo 🧪 Testing model connection...
        echo test | ollama run !PREFERRED_MODEL! --verbose 2>nul >nul
        if not errorlevel 1 (
            echo ✅ Model test successful!
        ) else (
            echo ⚠️ Model loaded but may need warming up
        )
    ) else (
        echo ⚠️ Preferred model not found, will auto-download
        echo 📥 Pulling !PREFERRED_MODEL!...
        ollama pull !PREFERRED_MODEL!
        if not errorlevel 1 (
            echo ✅ Model downloaded successfully!
        ) else (
            echo ❌ Failed to download model
        )
    )
    pause
    exit /b 0
)

echo 🚀 Starting Ollama service...
echo Service will be available at: http://localhost:11434
echo.

REM Start Ollama in background
start "Ollama Service" ollama serve

REM Wait for service to start
echo ⏳ Waiting for Ollama to start...
:wait_loop
timeout /t 2 /nobreak >nul
netstat -an | findstr ":11434" >nul 2>&1
if errorlevel 1 (
    echo Still waiting...
    goto wait_loop
)

echo ✅ Ollama service started successfully!
echo.

REM Auto-download preferred model if not exists
echo 🧠 Checking for Spectra's AI model...
set PREFERRED_MODEL=openhermes:7b-mistral-v2.5-q4_K_M
ollama list | findstr "!PREFERRED_MODEL!" >nul 2>&1
if errorlevel 1 (
    echo 📥 Downloading Spectra's AI model: !PREFERRED_MODEL!
    echo This may take several minutes...
    ollama pull !PREFERRED_MODEL!
    if not errorlevel 1 (
        echo ✅ Model downloaded successfully!
    ) else (
        echo ⚠️ Model download failed, will use available models
    )
) else (
    echo ✅ Preferred model already available!
)

echo.
echo 📋 Available models:
ollama list
echo.
echo 🔬 Final model verification...
echo Testing | ollama run !PREFERRED_MODEL! "Respond with just: READY" 2>nul | findstr "READY" >nul
if not errorlevel 1 (
    echo ✅ !PREFERRED_MODEL! is fully operational!
) else (
    echo ⚠️ Model may need a moment to warm up
)
echo.
echo 🌟 Ollama service ready for Spectra AI!
echo.
pause
