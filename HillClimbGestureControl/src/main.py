"""
Main application entry point for Hill Climb Gesture Control System.

Integrates all components:
- Camera capture
- Hand detection
- Gesture recognition
- Keyboard control
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
from src.config_manager import ConfigManager
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class GestureControlSystem:
    """
    Main gesture control system integrating all components.
    """
    
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
        
        self.gesture_recognizer = GestureRecognizer(self.config['gesture'])
        
        self.key_controller = KeyController(
            delay=self.config['control']['key_delay']
        )
        
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
        
        logger.info("System initialized successfully")
    
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
        
        # Bottom-left: Active key
        if key and key != 'None':
            cv2.rectangle(frame, (5, height - 70), (150, height - 5), color_bg, -1)
            cv2.putText(frame, f"Key: {key.upper()}", (15, height - 30), font, 
                       font_scale, (0, 255, 255), thickness)
        
        # Bottom-right: Hand count
        cv2.rectangle(frame, (width - 200, height - 70), (width - 5, height - 5), color_bg, -1)
        cv2.putText(frame, f"Hands: {hand_count}", (width - 190, height - 30), font,
                   font_scale, (255, 0, 255), thickness)
    
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
    
    def process_frame(self, frame) -> Tuple[str, Optional[str]]:
        """
        Process single frame for gesture recognition and key control.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Tuple[gesture, key]: Detected gesture and corresponding key
        """
        latency_start = time.time()
        
        # Flip if configured
        if self.config['control']['flip_frame']:
            frame = self.camera.flip_frame(frame)
        
        # Detect hands
        hands_data, success = self.hand_detector.detect_hands(frame)
        
        gesture = 'NONE'
        key = None
        
        if success and len(hands_data) > 0:
            # Process first hand (primary)
            landmarks = hands_data[0]['landmarks']
            
            # Recognize gesture
            gesture, confidence = self.gesture_recognizer.recognize(landmarks)
            
            # Debounce gesture (require consistency)
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
                
                # Only press if gesture changed
                if gesture != self.last_gesture:
                    logger.info(f"Gesture: {gesture} -> Key: {key}")
                    self.last_gesture = gesture
                    
                    # Update statistics
                    self.gesture_count[gesture] = self.gesture_count.get(gesture, 0) + 1
        
        # Calculate latency
        latency_ms = (time.time() - latency_start) * 1000
        
        # Update metrics
        fps, memory = self._update_frame_metrics()
        self.frame_count += 1
        
        return gesture, key, hands_data, frame, fps, latency_ms, memory
    
    def run(self) -> None:
        """
        Main application loop.
        
        Captures frames, processes gestures, and handles game control.
        Press 'q' to quit, 's' for settings, 'r' to reset statistics.
        """
        logger.info("Starting main loop")
        logger.info("Press 'q' to quit, 's' for settings, 'r' to reset stats")
        
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
                
                # Process gesture
                gesture, key, hands_data, frame, fps, latency, memory = self.process_frame(frame)
                
                # Draw overlays
                self.hand_detector.draw_hands(frame, hands_data)
                hand_count = len(hands_data)
                
                self._draw_info_overlay(frame, gesture, key, fps, latency, hand_count)
                
                if len(hands_data) > 0:
                    self._draw_debug_overlay(frame, hands_data[0]['landmarks'], {})
                
                # Press key if gesture detected
                if key and gesture != 'NONE':
                    self.key_controller.press_key(key)
                else:
                    # Release all keys if no gesture
                    self.key_controller.release_all()
                
                # Display frame
                cv2.imshow('Hill Climb Gesture Control', frame)
                
                # Handle keyboard input
                key_press = cv2.waitKey(1) & 0xFF
                
                if key_press == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key_press == ord('s'):
                    logger.info("Settings requested")
                    # Settings would open in separate thread
                    # For now, just log it
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
        
        # Release key presses
        self.key_controller.release_all()
        
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
