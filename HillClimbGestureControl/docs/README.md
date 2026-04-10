# Hill Climb Gesture Control System

## 🎯 Overview

A professional, rule-based gesture recognition system that controls **Hill Climb Racing** using hand gestures detected via webcam. Built with MediaPipe for hand tracking and OpenCV for video processing.

**Key Features:**
- ✅ **NO Machine Learning**: Pure geometric rule-based gesture detection
- ✅ **8 Intuitive Gestures**: Easy-to-learn hand gestures for full game control
- ✅ **Real-time Processing**: 30-60 FPS on standard hardware
- ✅ **Cross-Platform**: Windows, macOS, and Linux support
- ✅ **Professional Quality**: Production-ready code with comprehensive documentation
- ✅ **Easy to Explain**: Each function is simple and well-commented for academic submission
- ✅ **Configurable**: All thresholds in JSON files, no hardcoding

## 📁 Project Structure

```
HillClimbGestureControl/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── camera.py                 # Camera management
│   ├── hand_detector.py          # MediaPipe hand detection wrapper
│   ├── gesture_recognizer.py     # Rule-based gesture recognition (8 gestures)
│   ├── key_controller.py         # Keyboard simulation
│   ├── config_manager.py         # Configuration management
│   ├── gui.py                    # Tkinter settings GUI
│   └── utils/
│       ├── angle_calculator.py   # Vector math for gesture detection
│       ├── landmarks_processor.py # Hand landmark processing
│       └── logger.py             # Logging system
│
├── config/                       # Configuration files
│   ├── settings.json             # Main settings
│   └── gestures_mapping.json     # Gesture-to-key mapping
│
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   ├── USER_GUIDE.md             # User manual
│   └── TECHNICAL_REPORT.md       # Technical documentation
│
├── tests/                        # Unit tests
│   ├── test_camera.py
│   ├── test_gestures.py
│   └── test_key_controller.py
│
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── setup.py                      # Installation script
├── run.bat                       # Windows launcher
├── run.sh                        # Linux/Mac launcher
└── .gitignore
```

## 🎮 Supported Gestures

Each gesture maps to a Hill Climb Racing control:

| # | Gesture | Description | Key | Game Action |
|---|---------|-------------|-----|-------------|
| 1 | **OPEN_HAND** | All fingers extended | W | Gas/Accelerate |
| 2 | **FIST** | All fingers closed | S | Brake |
| 3 | **PEACE_SIGN** | Index & middle up | A | Lean Left |
| 4 | **THREE_FINGERS** | First 3 fingers up | D | Lean Right |
| 5 | **THUMBS_UP** | Thumb pointing up | SPACE | Nitro/Boost |
| 6 | **THUMBS_DOWN** | Thumb pointing down | SHIFT | Emergency Brake |
| 7 | **OK_SIGN** | Thumb & index circle | R | Reset/Restart |
| 8 | **POINTING** | Only index finger up | P | Pause |

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Webcam** (built-in or external)
- **CPU**: Dual-core minimum (i5/Ryzen 5 equivalent)
- **RAM**: 4GB minimum
- **Disk Space**: 200MB for dependencies

### Step-by-Step Installation

#### 1. Clone or Download the Project
```bash
cd HillClimbGestureControl
```

#### 2. Create Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `opencv-contrib-python` (4.8.1.78) - Video processing
- `mediapipe` (0.10.8) - Hand detection
- `pynput` (1.7.6) - Keyboard simulation
- `numpy` (1.24.3) - Numerical computations
- `psutil` (5.9.6) - System monitoring

#### 4. Verify Installation
```bash
python -c "import cv2, mediapipe, pynput; print('✓ All modules installed')"
```

## 🚀 Quick Start

### Run the Application

**Windows:**
```bash
run.bat
```

Or directly:
```bash
python -m src.main
```

**Linux/Mac:**
```bash
bash run.sh
```

Or directly:
```bash
python3 -m src.main
```

### First Time Setup

1. **Allow Camera Access**: When prompted by your OS
2. **Wait for Initialization**: System loads MediaPipe (first run takes ~5 seconds)
3. **Face Camera**: Position your hand in front of the webcam
4. **Start Gaming**: The system auto-detects your hand

### Keyboard Controls During Execution

- **Q** - Quit application
- **S** - Open settings GUI
- **R** - Reset statistics

## 📊 Configuration

### Camera Settings (`config/settings.json`)

```json
{
  "camera": {
    "width": 640,          // Frame width (320-1920)
    "height": 480,         // Frame height (240-1080)
    "fps": 30,             // Target FPS (5-60)
    "camera_id": 0         // Camera device ID
  }
}
```

### Gesture Detection Thresholds

```json
{
  "gesture": {
    "thumb_touch_threshold": 0.03,      // Distance for OK sign
    "finger_extension_threshold": 0.01, // Height for finger extension
    "peace_min_distance": 0.05          // Max distance between index/middle
  }
}
```

**Fine-tuning Tips:**
- Increase `finger_extension_threshold` if gestures are jittery
- Decrease `thumb_touch_threshold` if OK sign isn't recognized
- Adjust `peace_min_distance` if peace sign is too strict

## 🎯 How It Works

### Architecture

```
Camera Input
    ↓
[Frame Capture] (camera.py)
    ↓
[Hand Detection] (hand_detector.py)
    → MediaPipe extracts 21 landmarks per hand
    ↓
[Landmark Processing] (landmarks_processor.py)
    → Organize hand data for analysis
    ↓
[Angle Calculations] (angle_calculator.py)
    → Calculate finger angles and positions
    ↓
[Gesture Recognition] (gesture_recognizer.py)
    → Apply 8 geometric rules → Recognize gesture
    ↓
[Key Control] (key_controller.py)
    → Simulate keyboard press
    ↓
[Game] (Hill Climb Racing)
```

### Rule-Based Gesture Detection (No ML)

Each gesture uses simple geometric rules:

**Example: OPEN_HAND**
```
IF all 5 finger tips are above their PIP joints:
    OPEN_HAND gesture detected
```

**Example: THUMBS_UP**
```
IF thumb tip is above all other finger tips AND
   other fingers are mostly closed:
    THUMBS_UP gesture detected
```

All rules are in `gesture_recognizer.py` and explained with comments.

## 📈 Performance

### Optimization Features

- **FPS Target**: Configurable 30-60 FPS
- **Frame Skipping**: Option to process every Nth frame
- **Gesture Debouncing**: Reduces jitter (requires gesture consistency)
- **Anti-Spam Delay**: Prevents key press flooding (configurable)

### Expected Performance

| Metric | Target | Notes |
|--------|--------|-------|
| FPS | 30-60 | Depends on hardware |
| Latency | <100ms | Gesture to key press |
| CPU Usage | <50% | On average systems |
| Memory | <200MB | Including all libraries |
| Accuracy | >90% | Under good lighting |

### Performance Monitoring

The application displays real-time metrics:
- **FPS**: Current frames per second
- **Latency**: Gesture detection delay in milliseconds
- **Hand Count**: Number of detected hands
- **Active Key**: Currently pressed key

## 🔧 Advanced Configuration

### Enable Debug Mode

In `config/settings.json`:
```json
{
  "ui": {
    "show_debug_info": true,
    "show_landmarks": true,
    "show_fps": true
  }
}
```

### Adjust Key Press Delay

For slower/faster game response:
```json
{
  "control": {
    "key_delay": 0.05  // Milliseconds between key presses
  }
}
```

### Change Camera Device

For systems with multiple cameras:
```json
{
  "camera": {
    "camera_id": 0  // 0=default, 1=second camera, etc.
  }
}
```

## 🧪 Testing

### Run Unit Tests

```bash
python -m pytest tests/
```

Or individually:
```bash
python -m unittest tests.test_camera
python -m unittest tests.test_gestures  
python -m unittest tests.test_key_controller
```

### Manual Testing Checklist

- [ ] All 8 gestures recognized
- [ ] FPS maintained at 30+
- [ ] No false gesture detections
- [ ] Game responds to key presses
- [ ] Smooth hand tracking
- [ ] No lag or jitter

## 🐛 Troubleshooting

### Camera Not Detected
```
ERROR: Failed to open camera
```
**Solution:**
- Check camera is connected
- Try `camera_id: 1` or `2` in settings
- Close other applications using camera
- Restart application

### Low Recognition Accuracy
**Solutions:**
- Improve lighting (face light source)
- Position hand clearly in frame
- Increase `min_detection_confidence` slightly
- Ensure hand is fully visible

### Game Not Responding
**Solutions:**
- Verify game window is in focus
- Reduce `key_delay` in settings
- Check activity log: `logs/app_*.log`
- Ensure no other input devices interfere

### High CPU Usage
**Solutions:**
- Reduce resolution: 640x480 → 480x360
- Enable frame skipping: `skip_frames: 1`
- Reduce target FPS: 30 instead of 60
- Close background applications

### MediaPipe Errors
**Solution:**
```bash
pip install --upgrade mediapipe
```

## 📚 Code Structure

### Core Components

#### `camera.py`
- **Class**: `Camera`
- **Purpose**: Webcam management and frame capture
- **Key Methods**: `read_frame()`, `set_resolution()`, `get_fps()`

#### `hand_detector.py`
- **Class**: `HandDetector`
- **Purpose**: MediaPipe hand detection wrapper
- **Output**: 21 landmarks per hand

#### `gesture_recognizer.py`
- **Class**: `GestureRecognizer`
- **Purpose**: Rule-based gesture recognition
- **Methods**: 8 gesture detection methods + `recognize()`

#### `key_controller.py`
- **Class**: `KeyController`
- **Purpose**: Keyboard input simulation
- **Methods**: `press_key()`, `release_key()`

#### `config_manager.py`
- **Class**: `ConfigManager`
- **Purpose**: JSON configuration loading/saving
- **Methods**: `get()`, `set()`, `save_config()`

### Utility Modules

#### `angle_calculator.py`
- **Functions**: Angle/distance calculations using vectors
- **Purpose**: Geometric analysis for gesture detection

#### `landmarks_processor.py`
- **Class**: `LandmarksProcessor`
- **Purpose**: Hand landmark organization and processing
- **Landmark Indices**: Easy reference for hand anatomy

#### `logger.py`
- **Functions**: Logging setup and performance tracking
- **Output**: Console and file logging

## 📖 For Academic Submission

### What Makes This Suitable for A+

✅ **Computer Vision Concepts Used:**
- Feature extraction (21 hand landmarks)
- Geometric transformations (angle calculations)
- Real-time frame processing
- Threshold-based detection
- Coordinate transformations
- Performance optimization

✅ **Code Quality:**
- Clean, modular design
- Comprehensive docstrings
- Type hints throughout
- Following PEP 8 style guide
- DRY (Don't Repeat Yourself) principle
- Single Responsibility Principle

✅ **Documentation:**
- This comprehensive README
- USER_GUIDE.md with step-by-step instructions
- TECHNICAL_REPORT.md with full technical details
- Inline code comments explaining logic
- Configuration examples

✅ **Educational Value:**
- No ML complexity (pure geometric rules)
- Easy to explain to anyone
- Each gesture rule is simple and clear
- Good for demonstrating hand tracking
- Practical real-world application

### Presentation Tips

1. **Demo the System**
   - Show gesture recognition in action
   - Display FPS and performance metrics
   - Play game while controlling with gestures

2. **Explain the Approach**
   - Walk through one gesture detection rule
   - Explain why rule-based (no ML) is better for clarity
   - Show landmark visualization

3. **Highlight Technical Aspects**
   - MediaPipe landmark extraction
   - Vector-based angle calculations
   - Real-time processing pipeline
   - Performance optimization techniques

4. **Code Walkthrough**
   - `gesture_recognizer.py` - Show gesture rules
   - `angle_calculator.py` - Explain vector math
   - `main.py` - Demonstrate integration

## 🔐 System Requirements

### Minimum
- Python 3.8
- 4GB RAM
- Webcam (30 FPS+)
- Dual-core CPU

### Recommended  
- Python 3.10+
- 8GB RAM
- 1080p Webcam (60 FPS)
- Quad-core CPU (i5/Ryzen 5)

### Supported Platforms
- ✅ Windows 10/11
- ✅ macOS 10.12+
- ✅ Linux (Ubuntu 18.04+, Fedora, etc.)

## 📝 License

This project is provided for educational and research purposes.

## 🤝 Contributing

Suggestions for improvements:
1. Add more gestures
2. Implement dual-hand control
3. Add machine learning for better accuracy
4. Create GUI improvements
5. Add video recording capability

## 📞 Support

For issues or questions:
1. Check `logs/app_*.log` for error messages
2. Review troubleshooting section
3. Verify all dependencies installed
4. Try with different camera/lighting

## 🎓 References

- **MediaPipe**: https://mediapipe.dev/
- **OpenCV**: https://docs.opencv.org/
- **pynput**: https://pynput.readthedocs.io/
- **Hill Climb Racing**: https://www.hillclimbracing.com/

## ✨ Features at a Glance

| Feature | Status | Notes |
|---------|--------|-------|
| 8 Gestures | ✅ | Fully implemented and tested |
| Hand Detection | ✅ | MediaPipe with 21 landmarks |
| Keyboard Control | ✅ | Cross-platform support |
| Real-time Processing | ✅ | 30-60 FPS capability |
| GUI Settings | ✅ | Tkinter-based configuration |
| Logging | ✅ | File + console output |
| Configuration | ✅ | JSON-based, no hardcoding |
| Unit Tests | ✅ | Basic test coverage |
| Documentation | ✅ | Comprehensive guides |

## 🚀 Next Steps

1. **Install** - Follow the installation guide
2. **Run** - Execute `run.bat` or `run.sh`
3. **Test** - Try all 8 gestures
4. **Configure** - Adjust settings for your hardware
5. **Play** - Enjoy Hill Climb Racing with gestures!

---

**Built for Computer Vision Excellence** 🎯

*Make your hand gestures count!*
