# User Guide - Hill Climb Gesture Control System

## 📖 Complete User Manual

This guide walks you through setup, usage, and troubleshooting for the Hill Climb Gesture Control System.

### Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [First-Time Setup](#first-time-setup)
4. [Learning the Gestures](#learning-the-gestures)
5. [Game Controls](#game-controls)
6. [Settings Guide](#settings-guide)
7. [Tips & Tricks](#tips--tricks)
8. [FAQ](#faq)
9. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 7+, macOS 10.12+, or Linux
- **Python**: 3.8+ (check with `python --version`)
- **Webcam**: Any USB webcam (30+ FPS)
- **RAM**: 4GB
- **CPU**: Intel i3 / AMD Ryzen 3 equivalent

### Recommended Specifications
- **Python**: 3.10+
- **Webcam**: 1080p, 60 FPS
- **RAM**: 8GB+
- **CPU**: Intel i5 / AMD Ryzen 5 equivalent

### Supported Platforms
- ✅ **Windows**: 10, 11
- ✅ **macOS**: Catalina (10.15) and later
- ✅ **Linux**: Ubuntu 18.04+, Fedora, Debian, etc.

---

## Installation Steps

### Step 1: Download/Clone Project

**Option A: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder
3. Open terminal/command prompt in that folder

**Option B: Git Clone**
```bash
git clone <repository-url>
cd HillClimbGestureControl
```

### Step 2: Set Up Python Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**What gets installed:**
- OpenCV (video processing)
- MediaPipe (hand detection)
- pynput (keyboard control)
- NumPy (math operations)
- psutil (system monitoring)

### Step 4: Verify Installation

```bash
# Test if all modules import correctly
python -c "import cv2, mediapipe, pynput; print('✓ Ready to go!')"
```

If you see `✓ Ready to go!` - you're all set!

### Step 5: Run Application

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
bash run.sh
```

**Direct Python:**
```bash
python -m src.main
```

---

## First-Time Setup

### Initial Configuration

1. **Camera Check**
   - Application automatically detects webcam
   - Ensure camera is connected and functional
   - Allow camera access when prompted by OS

2. **Initialization**
   - First run takes 5-10 seconds (loading MediaPipe)
   - Subsequent runs are faster

3. **Hand Detection**
   - Position hand on front of camera
   - Ensure good lighting
   - Move hand slowly to let system calibrate

### Adjusting for Your Setup

If you have multiple cameras:
1. Edit `config/settings.json`
2. Change `"camera_id"` from `0` to `1`, `2`, etc.
3. Restart application

If camera image is too small/large:
```json
{
  "camera": {
    "width": 1280,
    "height": 720
  }
}
```

---

## Learning the Gestures

### Quick Reference Table

| Gesture | Hand Shape | Game Action | Key |
|---------|-----------|-------------|-----|
| **OPEN_HAND** | All fingers spread | Gas/Accelerate | W |
| **FIST** | Closed hand | Brake | S |
| **PEACE_SIGN** | ✌ two fingers up | Lean Left | A |
| **THREE_FINGERS** | Three fingers up | Lean Right | D |
| **THUMBS_UP** | 👍 thumb up | Nitro Boost | SPACE |
| **THUMBS_DOWN** | 👎 thumb down | Emergency Brake | SHIFT |
| **OK_SIGN** | 👌 thumb-index circle | Reset Game | R |
| **POINTING** | ☝️ index finger only | Pause | P |

### Learning Method

#### Method 1: Trial and Error
1. Make a gesture
2. Watch display to see if it's recognized
3. Adjust until recognized

#### Method 2: Guided Practice

```
1. Start application
2. Show OPEN_HAND → Wait for "Gesture: OPEN_HAND"
3. Show FIST → Wait for "Gesture: FIST"
4. Try others → Check feedback on screen
```

#### Method 3: Slow Practice

1. Make gesture slowly
2. Hold for 2 seconds
3. Watch recognition on screen
4. Adjust hand position until recognized

### Why Gestures Get Missed

| Issue | Solution |
|-------|----------|
| Not extended enough | Spread fingers wider |
| Hand out of frame | Move hand to center |
| Poor lighting | Face light source |
| Partially hidden | Show all fingers clearly |
| Too fast | Hold gesture for 1+ second |

---

## Game Controls

### Full Hill Climb Control Mapping

```
┌─────────────────────────────────────────┐
│     Hill Climb Racing Controls          │
├─────────────────────────────────────────┤
│ OPEN_HAND (W)     → Press Gas           │
│ FIST (S)          → Apply Brake         │
│ PEACE_SIGN (A)    → Lean Left           │
│ THREE_FINGERS (D) → Lean Right          │
│ THUMBS_UP (SPACE) → Activate Nitro      │
│ THUMBS_DOWN (SHIFT)→ Emergency Brake    │
│ OK_SIGN (R)       → Restart Level       │
│ POINTING (P)      → Pause Game          │
└─────────────────────────────────────────┘
```

### Application Controls

| Key | Action |
|-----|--------|
| **Q** | Quit application |
| **S** | Open settings menu |
| **R** | Reset statistics |
| **C** | Calibrate (future) |

### Application Display

**Top-Left Corner:**
- FPS: Frames per second
- Latency: Detection speed in ms

**Top-Right Corner:**
- Current gesture name (large text)
- Green if recognized, gray if none

**Bottom-Left Corner:**
- Active key being pressed/sent to game

**Bottom-Right Corner:**
- Hand count detection

---

## Settings Guide

### Opening Settings GUI

```bash
# While application is running, press 'S'
```

Or modify `config/settings.json` directly with a text editor.

### Camera Settings Tab

**Resolution**
- `Width`: 320-1920 pixels (default: 640)
- `Height`: 240-1080 pixels (default: 480)

*Note: Higher values = slower processing*

**FPS Target**
- Range: 5-60 FPS (default: 30)
- Higher = smoother but more CPU usage

**Camera ID**
- `0`: Default/built-in camera
- `1`, `2`, etc.: External cameras

### Detection Settings Tab

**Max Hands**
- `1` or `2` hands to detect
- Detecting 2 hands uses more CPU

**Detection Confidence**
- Scale: 0.3 - 1.0 (default: 0.7)
- Higher = stricter hand recognition
- Lower = more false positives

**Tracking Confidence**
- Scale: 0.3 - 1.0 (default: 0.5)
- Controls hand tracking smoothness

### Control Settings Tab

**Key Press Delay**
- Range: 0.01 - 0.5 seconds
- Prevents key flooding
- Adjust if game feels laggy

**Flip Frame**
- Toggle: True/False
- Use True for mirror mode

### UI Settings Tab

**Debug Info**
- Show/hide debug panel

**Hand Landmarks**
- Show/hide landmark points

**FPS Counter**
- Show/hide FPS display

**Font Size**
- Adjust text size on screen (0.5x - 2.0x)

---

## Tips & Tricks

### For Better Recognition

1. **Lighting**
   - Face well-lit area
   - Avoid backlighting (shadows on hands)
   - Natural window light works great

2. **Camera Angle**
   - Position camera at face level
   - 60-90cm away from camera
   - Keep hand in frame center

3. **Hand Position**
   - Keep palm facing camera (mostly)
   - Fingers clearly visible
   - Avoid covering fingers

4. **Gesture Timing**
   - Hold each gesture 0.5+ seconds
   - Don't jitter hands
   - Smooth transitions between gestures

### For Better Performance

**Increase FPS:**
```json
{
  "camera": {
    "width": 480,
    "height": 360,
    "fps": 60
  }
}
```

**Reduce Latency:**
```json
{
  "control": {
    "key_delay": 0.01
  }
}
```

**Lower CPU Usage:**
```json
{
  "performance": {
    "skip_frames": 1
  }
}
```

### Gesture Fine-Tuning

If gesture isn't recognized properly:

1. Check threshold values in `config/settings.json`
2. Adjust incrementally (10% changes)
3. Test with hand gesture
4. Repeat until satisfied

**Adjustment Example:**
```json
{
  "gesture": {
    "finger_extension_threshold": 0.015
  }
}
```

---

## FAQ

### Q: My gestures aren't recognized
**A:** 
1. Check lighting - ensure good brightness
2. Keep hand fully in view
3. Hold gesture for 1+ second
4. Check webcam is working (open Camera app)
5. Adjust detection confidence down slightly

### Q: Game isn't responding to my gestures
**A:**
1. Ensure game window is in focus
2. Check if key is being pressed (see bottom-left)
3. Reduce `key_delay` value
4. Try pressing gesture key manually to verify game

### Q: Application is slow/laggy
**A:**
1. Reduce resolution to 480x360
2. Lower FPS target to 30
3. Enable frame skipping
4. Close other applications
5. Check CPU temperature

### Q: Too many false positives
**A:**
1. Increase detection confidence (0.8+)
2. Increase threshold values
3. Ensure stable lighting
4. Avoid hand tremors

### Q: Which version of Python do I need?
**A:** Python 3.8+ (3.10+ recommended)
```bash
python --version
```

### Q: Can I use with a USB camera?
**A:** Yes! Any USB webcam works.
```json
{
  "camera": {
    "camera_id": 1
  }
}
```

### Q: Does it work on Mac/Linux?
**A:** Yes! Fully cross-platform.
```bash
bash run.sh
```

### Q: How do I reset settings?
**A:** In GUI settings:
1. Click "Reset" button
2. Confirm when asked
3. Settings return to defaults

Or delete `config/settings.json` to reset:
```bash
rm config/settings.json
```

### Q: Can I add more gestures?
**A:** Yes! Edit `gesture_recognizer.py` and add new detection methods.

### Q: Where are error logs?
**A:** In `logs/` folder
```bash
logs/app_20240101_120000.log
```

---

## Troubleshooting

### Issue: "Failed to open camera"

**Cause:** Camera not detected or in use

**Solutions:**
1. Close other camera applications
2. Check Settings → Volume → Microphone
3. Try different `camera_id` in config
4. Unplug and reconnect camera
5. Restart computer

### Issue: "Import Error: No module named 'mediapipe'"

**Cause:** Missing dependencies

**Solution:**
```bash
pip install -r requirements.txt
```

If still fails:
```bash
pip install --upgrade mediapipe
```

### Issue: Game not responding

**Cause:** Keys not being sent

**Solutions:**
1. Check game is in focus (active window)
2. Verify key displays in bottom-left corner
3. Try pressing gesture key manually
4. Check keyboard isn't locked (Capslock, etc.)
5. Restart application

### Issue: "Permission Denied" on run.sh

**Solution:**
```bash
chmod +x run.sh
bash run.sh
```

### Issue: Low FPS (below 20)

**Cause:** System too slow

**Solutions:**
1. Lower resolution:
```json
{
  "camera": {
    "width": 320,
    "height": 240
  }
}
```

2. Reduce FPS target:
```json
{
  "camera": {
    "fps": 20
  }
}
```

3. Close other applications
4. Check CPU temperature
5. Disable debug displays

### Issue: Gesture randomly changes

**Cause:** Jittery tracking or low threshold

**Solution:**
```json
{
  "gesture": {
    "finger_extension_threshold": 0.015
  }
}
```

### Issue: System crashes

**Solution:**
1. Check `logs/app_*.log` for error
2. Reduce resolution and FPS
3. Disable all debug displays
4. Update Python and libraries:
```bash
pip install --upgrade -r requirements.txt
```

---

## Getting Help

### Check These First

1. Read troubleshooting section above
2. Review log files in `logs/` folder
3. Check README.md for technical details
4. Verify all dependencies installed

### Documentation Files

- **README.md** - Setup, features, API reference
- **TECHNICAL_REPORT.md** - Detailed technical explanation
- **USER_GUIDE.md** - This file

---

## Next Steps

✅ **You're ready!**

1. Start the application
2. Learn one gesture at a time
3. Practice until comfortable
4. Load Hill Climb Racing
5. Enjoy gesture-based game control!

---

**Happy Gaming! 🎮**

*Control Hill Climb Racing with your hands!*
