"""
Main application entry point for Hill Climb Gesture Control System.

Supports two control modes:
1. KEYBOARD MODE (Hill Climb Racing): Uses hand gestures → keyboard arrow keys
2. SWIPE MODE (Subway Surfers): Uses pinch + hand movement → mouse swipes

Press 'm' to toggle between modes during runtime.

Integrates all components:
- Camera capture
- Hand detection
- Gesture recognition (keyboard mode)
- Pinch swipe recognition (swipe mode)
- Keyboard control / Mouse control
- Real-time display with overlays
"""

import cv2
import time
import psutil
import os
from typing import Tuple, Optional
from src.camera import Camera
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.key_controller import KeyController
from src.mouse_controller import MouseController
from src.pinch_swipe_recognizer import PinchSwipeRecognizer
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class GestureControlSystem:
    """
    Main gesture control system integrating all components.
    
    Supports two modes:
    - 'keyboard': Original Hill Climb Racing controls (gestures → arrow keys)
    - 'mouse_swipe': Subway Surfers controls (pinch + swipe → mouse drag)
    """
    
    # Control modes
    MODE_KEYBOARD = 'keyboard'
    MODE_SWIPE = 'mouse_swipe'
    
    def __init__(self, config_file: str = 'config/settings.json'):
        """
        Initialize the gesture control system.
        
        Args:
            config_file: Path to configuration file
        """
        logger.info("=" * 60)
        logger.info("Hill Climb Gesture Control System Starting")
        logger.info("=" * 60)
        
        # Load configuration
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_all()
        
        # Initialize components
        self.camera = Camera(
            camera_id=self.config['camera']['camera_id'],
            width=self.config['camera']['width'],
            height=self.config['camera']['height'],
            fps=self.config['camera']['fps']
        )
        
        self.hand_detector = HandDetector(
            max_num_hands=self.config['detection']['max_hands'],
            min_detection_confidence=self.config['detection']['min_detection_confidence'],
            min_tracking_confidence=self.config['detection']['min_tracking_confidence']
        )
        
        # --- Keyboard mode components (original) ---
        self.gesture_recognizer = GestureRecognizer(self.config['gesture'])
        
        self.key_controller = KeyController(
            delay=self.config['control']['key_delay']
        )
        
        # --- Swipe mode components (new) ---
        swipe_config = self.config.get('swipe', {})
        self.pinch_swipe_recognizer = PinchSwipeRecognizer(swipe_config)
        
        self.mouse_controller = MouseController(
            swipe_distance=swipe_config.get('swipe_distance_pixels', 300),
            swipe_duration=0.05
        )
        
        # --- Control mode ---
        self.control_mode = self.MODE_KEYBOARD  # Default: keyboard mode
        
        # Performance tracking
        self.frame_count = 0
        self.gesture_count = {}
        self.start_time = time.time()
        self.last_gesture = 'NONE'
        self.gesture_hold_time = 0
        self.gesture_hold_counter = 0
        
        # Gesture debouncing (require gesture for N frames before pressing)
        self.gesture_debounce_frames = 2
        self.gesture_buffer = []
        
        logger.info(f"System initialized successfully (mode: {self.control_mode})")
    
    def toggle_mode(self) -> str:
        """
        Toggle between keyboard and swipe mode.
        
        Returns:
            str: New mode name
        """
        # Release everything before switching
        self.key_controller.release_all()
        self.mouse_controller.release_all()
        self.pinch_swipe_recognizer.reset()
        self.gesture_buffer.clear()
        self.last_gesture = 'NONE'
        
        if self.control_mode == self.MODE_KEYBOARD:
            self.control_mode = self.MODE_SWIPE
        else:
            self.control_mode = self.MODE_KEYBOARD
        
        logger.info(f"Control mode switched to: {self.control_mode}")
        return self.control_mode
    
    def _update_frame_metrics(self) -> Tuple[float, float]:
        """
        Calculate FPS and memory usage.
        
        Returns:
            Tuple[fps, memory_mb]: Current FPS and memory usage
        """
        fps = self.camera.get_fps()
        
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
        except:
            memory_mb = 0.0
        
        return fps, memory_mb
    
    def _draw_info_overlay(self, frame, gesture: str, key: Optional[str], 
                          fps: float, latency: float, hand_count: int) -> None:
        """
        Draw information overlay on frame.
        
        Args:
            frame: Frame to draw on
            gesture: Current gesture name
            key: Current key being pressed
            fps: Current FPS
            latency: Gesture detection latency
            hand_count: Number of hands detected
        """
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self.config['ui']['font_size']
        thickness = 2
        color_text = (255, 255, 255)
        color_bg = (0, 0, 0)
        
        # Top-left: FPS and latency
        if self.config['ui']['show_fps']:
            cv2.rectangle(frame, (5, 5), (300, 95), color_bg, -1)
            cv2.putText(frame, f"FPS: {fps:.1f}", (15, 35), font, font_scale, color_text, thickness)
            cv2.putText(frame, f"Latency: {latency:.1f}ms", (15, 65), font, font_scale, color_text, thickness)
        
        # Top-right: Gesture name (large)
        gesture_color = (0, 255, 0) if gesture != 'NONE' else (100, 100, 100)
        cv2.rectangle(frame, (width - 350, 5), (width - 5, 80), color_bg, -1)
        cv2.putText(frame, f"Gesture: {gesture}", (width - 340, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale * 1.2, gesture_color, thickness + 1)
        
        # Bottom-left: Active key / swipe info
        if key and key != 'None':
            cv2.rectangle(frame, (5, height - 70), (200, height - 5), color_bg, -1)
            cv2.putText(frame, f"Key: {key.upper()}", (15, height - 30), font, 
                       font_scale, (0, 255, 255), thickness)
        
        # Bottom-right: Hand count
        cv2.rectangle(frame, (width - 200, height - 70), (width - 5, height - 5), color_bg, -1)
        cv2.putText(frame, f"Hands: {hand_count}", (width - 190, height - 30), font,
                   font_scale, (255, 0, 255), thickness)
        
        # Top-center: Current mode indicator
        mode_text = "KEYBOARD (Hill Climb)" if self.control_mode == self.MODE_KEYBOARD else "SWIPE (Subway Surfers)"
        mode_color = (255, 200, 0) if self.control_mode == self.MODE_KEYBOARD else (0, 200, 255)
        text_size = cv2.getTextSize(mode_text, font, font_scale * 0.7, thickness)[0]
        text_x = (width - text_size[0]) // 2
        cv2.rectangle(frame, (text_x - 10, 85), (text_x + text_size[0] + 10, 120), color_bg, -1)
        cv2.putText(frame, mode_text, (text_x, 110), font, 
                   font_scale * 0.7, mode_color, thickness)
    
    def _draw_swipe_overlay(self, frame, debug_info: dict) -> None:
        """
        Draw pinch/swipe debug information on frame (swipe mode only).
        
        Args:
            frame: Frame to draw on
            debug_info: Debug info from PinchSwipeRecognizer
        """
        if not debug_info:
            return
            
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Pinch indicator
        is_pinching = debug_info.get('is_pinching', False)
        pinch_dist = debug_info.get('pinch_distance', 0)
        
        # Draw pinch status box
        pinch_color = (0, 255, 0) if is_pinching else (0, 0, 255)
        pinch_text = "PINCH: ON" if is_pinching else "PINCH: OFF"
        cv2.rectangle(frame, (5, height - 140), (250, height - 75), (0, 0, 0), -1)
        cv2.putText(frame, pinch_text, (15, height - 115), font, font_scale, pinch_color, thickness)
        cv2.putText(frame, f"Dist: {pinch_dist:.3f}", (15, height - 90), font, font_scale, (200, 200, 200), 1)
        
        # Draw movement arrows if pinching
        if is_pinching:
            dx = debug_info.get('dx', 0)
            dy = debug_info.get('dy', 0)
            
            # Draw direction indicator in center
            center_x, center_y = width // 2, height // 2
            arrow_len = 60
            
            # Draw crosshair
            cv2.circle(frame, (center_x, center_y), 30, (100, 100, 100), 1)
            
            # Draw movement vector
            end_x = center_x + int(dx * 500)
            end_y = center_y + int(dy * 500)
            # Clamp
            end_x = max(center_x - arrow_len, min(center_x + arrow_len, end_x))
            end_y = max(center_y - arrow_len, min(center_y + arrow_len, end_y))
            
            cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), (0, 255, 255), 3)
    
    def _draw_debug_overlay(self, frame, landmarks: list, gesture_details: dict) -> None:
        """
        Draw debug information overlay.
        
        Args:
            frame: Frame to draw on
            landmarks: Hand landmarks
            gesture_details: Details about current gesture
        """
        if not self.config['ui']['show_landmarks']:
            return
        
        height, width = frame.shape[:2]
        
        # Draw landmarks as circles
        for i, (x, y, z) in enumerate(landmarks):
            px = int(x * width)
            py = int(y * height)
            cv2.circle(frame, (px, py), 3, (0, 255, 0), -1)
            
            # Draw landmark index for first few
            if i < 5:
                cv2.putText(frame, str(i), (px + 5, py + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    def process_frame_keyboard(self, frame, hands_data) -> Tuple[str, Optional[str]]:
        """
        Process frame in KEYBOARD mode (original Hill Climb logic).
        
        Args:
            frame: Input frame
            hands_data: Detected hands data
            
        Returns:
            Tuple[gesture, key]: Detected gesture and corresponding key
        """
        gesture = 'NONE'
        key = None
        
        if len(hands_data) > 0:
            landmarks = hands_data[0]['landmarks']
            
            # Recognize gesture
            gesture, confidence = self.gesture_recognizer.recognize(landmarks)
            
            # Debounce gesture
            self.gesture_buffer.append(gesture)
            if len(self.gesture_buffer) > self.gesture_debounce_frames:
                self.gesture_buffer.pop(0)
            
            # Check if gesture is consistent
            if len(self.gesture_buffer) >= self.gesture_debounce_frames:
                most_common = max(set(self.gesture_buffer), key=self.gesture_buffer.count)
                if self.gesture_buffer.count(most_common) >= self.gesture_debounce_frames - 1:
                    gesture = most_common
            
            # Get key for gesture
            if gesture != 'NONE':
                key = self.gesture_recognizer.get_gesture_key(gesture)
                
                if gesture != self.last_gesture:
                    logger.info(f"Gesture: {gesture} -> Key: {key}")
                    self.last_gesture = gesture
                    self.gesture_count[gesture] = self.gesture_count.get(gesture, 0) + 1
        
        # Control keys
        if key and gesture != 'NONE':
            for active_key in list(self.key_controller.get_active_keys()):
                if active_key != key:
                    self.key_controller.release_key(active_key)
            self.key_controller.press_key(key)
        else:
            self.key_controller.release_all()
        
        return gesture, key
    
    def process_frame_swipe(self, frame, hands_data) -> Tuple[str, Optional[str], dict]:
        """
        Process frame in SWIPE mode (Subway Surfers logic).
        
        Args:
            frame: Input frame
            hands_data: Detected hands data
            
        Returns:
            Tuple[gesture, action, debug_info]: Detected swipe and action taken
        """
        gesture = 'NONE'
        action = None
        debug_info = {}
        
        if len(hands_data) > 0:
            landmarks = hands_data[0]['landmarks']
            
            # Recognize pinch + swipe
            gesture, confidence, debug_info = self.pinch_swipe_recognizer.recognize(landmarks)
            
            # Execute swipe if detected
            if gesture == PinchSwipeRecognizer.SWIPE_UP:
                self.mouse_controller.swipe_up()
                action = 'SWIPE UP'
                self.gesture_count['SWIPE_UP'] = self.gesture_count.get('SWIPE_UP', 0) + 1
                
            elif gesture == PinchSwipeRecognizer.SWIPE_DOWN:
                self.mouse_controller.swipe_down()
                action = 'SWIPE DOWN'
                self.gesture_count['SWIPE_DOWN'] = self.gesture_count.get('SWIPE_DOWN', 0) + 1
                
            elif gesture == PinchSwipeRecognizer.SWIPE_LEFT:
                self.mouse_controller.swipe_left()
                action = 'SWIPE LEFT'
                self.gesture_count['SWIPE_LEFT'] = self.gesture_count.get('SWIPE_LEFT', 0) + 1
                
            elif gesture == PinchSwipeRecognizer.SWIPE_RIGHT:
                self.mouse_controller.swipe_right()
                action = 'SWIPE RIGHT'
                self.gesture_count['SWIPE_RIGHT'] = self.gesture_count.get('SWIPE_RIGHT', 0) + 1
            
            if gesture != self.last_gesture and gesture != PinchSwipeRecognizer.PINCH_HOLD:
                self.last_gesture = gesture
        
        return gesture, action, debug_info
    
    def run(self) -> None:
        """
        Main application loop.
        
        Captures frames, processes gestures, and handles game control.
        Press 'q' to quit, 'm' to toggle mode, 'r' to reset statistics.
        """
        logger.info("Starting main loop")
        logger.info("Press 'q' to quit, 'm' to toggle mode, 'r' to reset stats")
        
        skip_frames = self.config['performance']['skip_frames']
        frame_skip_counter = 0
        
        try:
            while True:
                # Capture frame
                success, frame = self.camera.read_frame()
                
                if not success or frame is None:
                    logger.warning("Failed to capture frame")
                    continue
                
                # Skip frames if configured
                frame_skip_counter += 1
                if frame_skip_counter < (skip_frames + 1):
                    continue
                frame_skip_counter = 0
                
                latency_start = time.time()
                
                # Flip if configured
                if self.config['control']['flip_frame']:
                    frame = self.camera.flip_frame(frame)
                
                # Detect hands
                hands_data, detect_success = self.hand_detector.detect_hands(frame)
                
                # Process based on current mode
                gesture = 'NONE'
                key_or_action = None
                swipe_debug = {}
                
                if detect_success:
                    if self.control_mode == self.MODE_KEYBOARD:
                        gesture, key_or_action = self.process_frame_keyboard(frame, hands_data)
                    else:
                        gesture, key_or_action, swipe_debug = self.process_frame_swipe(frame, hands_data)
                
                # Calculate latency
                latency_ms = (time.time() - latency_start) * 1000
                
                # Update metrics
                fps, memory = self._update_frame_metrics()
                self.frame_count += 1
                
                # Draw overlays
                self.hand_detector.draw_hands(frame, hands_data)
                hand_count = len(hands_data)
                
                self._draw_info_overlay(frame, gesture, key_or_action, fps, latency_ms, hand_count)
                
                if len(hands_data) > 0:
                    self._draw_debug_overlay(frame, hands_data[0]['landmarks'], {})
                
                # Draw swipe-specific overlay in swipe mode
                if self.control_mode == self.MODE_SWIPE:
                    self._draw_swipe_overlay(frame, swipe_debug)
                
                # Display frame
                cv2.imshow('Hill Climb Gesture Control', frame)
                
                # Handle keyboard input
                key_press = cv2.waitKey(1) & 0xFF
                
                if key_press == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key_press == ord('m'):
                    new_mode = self.toggle_mode()
                    logger.info(f"Mode toggled to: {new_mode}")
                elif key_press == ord('r'):
                    logger.info("Statistics reset")
                    self.gesture_count = {}
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Main loop error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Clean up resources and display statistics."""
        logger.info("Shutting down...")
        
        # Release key presses and mouse
        self.key_controller.release_all()
        self.mouse_controller.release_all()
        
        # Close camera
        self.camera.release()
        self.hand_detector.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        # Log statistics
        runtime = time.time() - self.start_time
        logger.info("=" * 60)
        logger.info("STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total runtime: {runtime:.1f} seconds")
        logger.info(f"Frames processed: {self.frame_count}")
        logger.info(f"Average FPS: {self.frame_count / runtime:.1f}")
        
        if self.gesture_count:
            logger.info("Gestures detected:")
            for gesture, count in sorted(self.gesture_count.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {gesture}: {count} times")
        
        logger.info("=" * 60)
        logger.info("System shutdown complete")


def main():
    """Application entry point."""
    import sys
    
    # Determine config file
    config_file = 'config/settings.json'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # Create and run system
    system = GestureControlSystem(config_file)
    system.run()


if __name__ == '__main__':
    main()
