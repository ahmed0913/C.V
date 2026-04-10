#!/bin/bash
# Hill Climb Gesture Control System - Linux/Mac Launcher

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check if required packages are installed
python3 -c "import cv2; import mediapipe; import pynput" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install packages"
        exit 1
    fi
fi

# Run the application
echo "Starting Hill Climb Gesture Control System..."
python3 -m src.main "$@"
