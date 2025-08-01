@echo off
echo 🛑 Quick Shutdown - Spectra AI Services
echo.

REM Kill all Node.js processes (Frontend)
taskkill /im node.exe /f >nul 2>&1

REM Kill all Python processes (Backend) 
taskkill /im python.exe /f >nul 2>&1

REM Kill all Ollama processes (AI Service)
taskkill /im ollama.exe /f >nul 2>&1

echo ✅ All services terminated
timeout /t 2 /nobreak >nul
