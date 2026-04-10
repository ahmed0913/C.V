@echo off
REM Hill Climb Gesture Control - Quick Start Guide
REM This script helps you get started quickly

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   Hill Climb Gesture Control System - Quick Start          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

echo.
echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [4/4] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠ Some packages may not have installed correctly
    echo Trying again with upgrade...
    pip install --upgrade -r requirements.txt
)
echo ✓ Dependencies installed

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   Setup Complete! Ready to Go!                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Run the application:
echo      python -m src.main
echo.
echo   2. Test gestures on your webcam
echo.
echo   3. Open Hill Climb Racing and start a level
echo.
echo   4. Use hand gestures to control the game
echo.
echo Controls:
echo   Q - Quit
echo   S - Settings
echo   R - Reset Statistics
echo.
echo For more info, see:
echo   - README.md (overview and setup)
echo   - USER_GUIDE.md (detailed instructions)
echo   - TECHNICAL_REPORT.md (technical details)
echo.
pause
