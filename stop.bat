@echo off
echo.
echo ============================================
echo    🛑 Graceful Spectra AI Shutdown
echo ============================================
echo.

REM Set color to cyan for status messages
color 0B

echo 🔍 Checking running services...
echo.

REM Check and kill Vite/Node.js processes (Frontend)
echo 📱 Shutting down Frontend (Vite/Node.js)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq node.exe" /fo csv ^| find "node.exe"') do (
    echo    Stopping Node.js process %%i
    taskkill /PID %%i /F >nul 2>&1
)

REM Check and kill Python/Flask processes (Backend)
echo 🐍 Shutting down Backend (Flask/Python)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    echo    Stopping Python process %%i
    taskkill /PID %%i /F >nul 2>&1
)

REM Check and kill Ollama processes (AI Service)
echo 🤖 Shutting down AI Service (Ollama)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq ollama.exe" /fo csv ^| find "ollama.exe"') do (
    echo    Stopping Ollama process %%i
    taskkill /PID %%i /F >nul 2>&1
)

REM Additional cleanup for any lingering processes on our ports
echo 🧹 Cleaning up network connections...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":5000"') do (
    echo    Freeing port 5000 (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":3000"') do (
    echo    Freeing port 3000 (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":3001"') do (
    echo    Freeing port 3001 (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":11434"') do (
    echo    Freeing port 11434 (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

REM Give processes time to shut down gracefully
echo.
echo ⏳ Waiting for processes to terminate gracefully...
timeout /t 3 /nobreak >nul

REM Verify shutdown
echo.
echo 🔍 Verifying shutdown status...
echo.

set "processes_found=false"

REM Check if any processes are still running
tasklist /fi "imagename eq node.exe" 2>nul | find "node.exe" >nul
if not errorlevel 1 (
    echo    ⚠️  Some Node.js processes may still be running
    set "processes_found=true"
)

tasklist /fi "imagename eq python.exe" 2>nul | find "python.exe" >nul
if not errorlevel 1 (
    echo    ⚠️  Some Python processes may still be running
    set "processes_found=true"
)

tasklist /fi "imagename eq ollama.exe" 2>nul | find "ollama.exe" >nul
if not errorlevel 1 (
    echo    ⚠️  Some Ollama processes may still be running
    set "processes_found=true"
)

if "%processes_found%"=="false" (
    echo    ✅ All Spectra AI services stopped successfully!
) else (
    echo    ℹ️  Some processes may still be running (could be system processes)
)

echo.
echo ============================================
echo    🎉 Spectra AI Shutdown Complete
echo ============================================
echo.
echo Press any key to exit...
pause >nul
