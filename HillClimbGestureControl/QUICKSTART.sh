#!/bin/bash
# Hill Climb Gesture Control - Quick Start Guide
# This script helps you get started quickly

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Hill Climb Gesture Control System - Quick Start          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ $PYTHON_VERSION found"

echo ""
echo "[2/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[4/4] Installing dependencies..."
if pip install -qq -r requirements.txt 2>/dev/null; then
    echo "✓ Dependencies installed"
else
    echo "⚠ Some packages may not have installed correctly"
    echo "Trying again with upgrade..."
    pip install --upgrade -q -r requirements.txt
    echo "✓ Dependencies installed"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Setup Complete! Ready to Go!                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run the application:"
echo "     python3 -m src.main"
echo ""
echo "  2. Test gestures on your webcam"
echo ""
echo "  3. Open Hill Climb Racing and start a level"
echo ""
echo "  4. Use hand gestures to control the game"
echo ""
echo "Controls:"
echo "  Q - Quit"
echo "  S - Settings"
echo "  R - Reset Statistics"
echo ""
echo "For more info, see:"
echo "  - README.md (overview and setup)"
echo "  - USER_GUIDE.md (detailed instructions)"
echo "  - TECHNICAL_REPORT.md (technical details)"
echo ""
