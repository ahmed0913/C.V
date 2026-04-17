@echo off
REM Hill Climb Gesture Control System - Windows Launcher

REM Check if Python 3.11 is available via py launcher
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    REM Fallback: check if python is in PATH
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.8+ from https://www.python.org/
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py -3.11
)

echo Using: %PYTHON_CMD%

REM Check if required packages are installed
%PYTHON_CMD% -c "import cv2; import mediapipe; import pynput" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting Hill Climb Gesture Control System...
echo Press 'q' to quit, 'm' to toggle mode (Keyboard/Swipe), 'r' to reset stats
%PYTHON_CMD% -m src.main %*

pause
