@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo    🛑 Graceful Spectra AI Shutdown
echo ============================================
echo.

REM Set color to cyan for status messages
color 0B

echo 🔍 Checking running services...
echo.

REM Function to kill processes by name with better error handling
call :kill_process_by_name "node.exe" "📱 Frontend (Node.js/Vite)"
call :kill_process_by_name "python.exe" "🐍 Backend (Python/Flask)"
call :kill_process_by_name "ollama.exe" "🤖 AI Service (Ollama)"

REM Clean up ports more efficiently
echo.
echo 🧹 Cleaning up network connections...
call :kill_process_by_port "5000" "Backend"
call :kill_process_by_port "3000" "Frontend"
call :kill_process_by_port "3001" "Frontend Dev"
call :kill_process_by_port "11434" "Ollama"

REM Give processes time to shut down gracefully
echo.
echo ⏳ Waiting for graceful shutdown...
timeout /t 3 /nobreak >nul

REM Verify shutdown
call :verify_shutdown

echo.
echo ============================================
echo    🎉 Spectra AI Shutdown Complete
echo ============================================
echo.
echo Press any key to exit...
pause >nul
goto :eof

:kill_process_by_name
set "process_name=%~1"
set "service_name=%~2"
echo %service_name%...
set "found_processes=false"
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq %process_name%" /fo csv 2^>nul ^| find "%process_name%"') do (
    set "found_processes=true"
    echo    Stopping process %%i
    taskkill /PID %%i /F >nul 2>&1
)
if "!found_processes!"=="false" (
    echo    No %process_name% processes found
)
goto :eof

:kill_process_by_port
set "port=%~1"
set "service_name=%~2"
for /f "tokens=5" %%i in ('netstat -ano 2^>nul ^| findstr ":%port%"') do (
    if "%%i" neq "" (
        echo    Freeing port %port% (%service_name% - PID: %%i)
        taskkill /PID %%i /F >nul 2>&1
    )
)
goto :eof

:verify_shutdown
echo 🔍 Verifying shutdown status...
echo.
set "processes_found=false"

for %%p in (node.exe python.exe ollama.exe) do (
    tasklist /fi "imagename eq %%p" 2>nul | find "%%p" >nul
    if not errorlevel 1 (
        echo    ⚠️  Some %%p processes may still be running
        set "processes_found=true"
    )
)

if "!processes_found!"=="false" (
    echo    ✅ All Spectra AI services stopped successfully!
) else (
    echo    ℹ️  Some processes may still be running (could be system processes)
)
goto :eof