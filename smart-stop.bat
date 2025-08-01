@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    🔄 Smart Spectra AI Shutdown
echo ============================================
echo.

REM Try graceful shutdown first
echo 🤝 Attempting graceful shutdown...

REM Send Ctrl+C to running terminals (graceful)
echo    Sending interrupt signals to running services...

REM Give a moment for graceful shutdown
timeout /t 3 /nobreak >nul

REM Check if processes are still running
set "need_force=false"

tasklist /fi "imagename eq node.exe" 2>nul | find "node.exe" >nul
if not errorlevel 1 set "need_force=true"

tasklist /fi "imagename eq python.exe" 2>nul | find "python.exe" >nul  
if not errorlevel 1 set "need_force=true"

tasklist /fi "imagename eq ollama.exe" 2>nul | find "ollama.exe" >nul
if not errorlevel 1 set "need_force=true"

if "!need_force!"=="true" (
    echo.
    echo 💪 Graceful shutdown incomplete, using force termination...
    echo.
    
    REM Force kill remaining processes
    echo 📱 Force stopping Frontend processes...
    taskkill /im node.exe /f >nul 2>&1
    
    echo 🐍 Force stopping Backend processes...
    taskkill /im python.exe /f >nul 2>&1
    
    echo 🤖 Force stopping AI Service processes...
    taskkill /im ollama.exe /f >nul 2>&1
    
    echo.
    echo ⏳ Finalizing shutdown...
    timeout /t 2 /nobreak >nul
) else (
    echo ✅ Graceful shutdown successful!
)

echo.
echo ============================================
echo    ✨ Shutdown Complete
echo ============================================
echo.

REM Optional: Clear any lingering port locks
netsh int ip reset >nul 2>&1

echo Press any key to exit...
pause >nul
