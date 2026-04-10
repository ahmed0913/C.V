@echo off
REM Hill Climb Gesture Control System - Windows Launcher

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import cv2; import mediapipe; import pynput" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting Hill Climb Gesture Control System...
python -m src.main %*

pause
