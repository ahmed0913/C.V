"""
MediaPipe hand detection wrapper using Tasks API.

Wraps MediaPipe Hands for hand detection and landmark extraction
with configurable detection thresholds.
"""

import os
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import List, Optional, Tuple
from src.utils.logger import setup_logger
from src.utils.landmarks_processor import LandmarksProcessor
import cv2

logger = setup_logger(__name__)

# Verify model path (assumes hand_landmarker.task is in the project root)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hand_landmarker.task')

class HandDetector:
    """
    Hand detection using MediaPipe Tasks API.
    
    Detects hands and extracts 21 landmarks per hand using MediaPipe Hands.
    """
    
    def __init__(self, max_num_hands: int = 2, 
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize hand detector.
        """
        self.max_num_hands = max(1, min(max_num_hands, 2))
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        try:
            # Initialize MediaPipe Tasks
            base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=self.max_num_hands,
                min_hand_detection_confidence=self.min_detection_confidence,
                min_hand_presence_confidence=self.min_tracking_confidence,
                min_tracking_confidence=self.min_tracking_confidence,
                running_mode=vision.RunningMode.VIDEO
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            
            # Hardcoded hand connections since mp.solutions is missing
            self.HAND_CONNECTIONS = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (5, 9), (9, 10), (10, 11), (11, 12),
                (9, 13), (13, 14), (14, 15), (15, 16),
                (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
            ]
            
            logger.info(f"Hand detector initialized (Tasks API) - max_hands: {self.max_num_hands}, "
                       f"detection_conf: {self.min_detection_confidence}")
        except Exception as e:
            logger.error(f"Failed to initialize HandDetector tasks API: {e}")
            self.detector = None
    
    def detect_hands(self, frame) -> Tuple[List, bool]:
        """
        Detect hands and extract landmarks from frame.
        """
        if self.detector is None:
            return [], False

        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Run detection (use current time in milliseconds)
            timestamp_ms = int(time.time() * 1000)
            results = self.detector.detect_for_video(mp_image, timestamp_ms)
            
            hands_data = []
            
            if results and results.hand_landmarks:
                for i in range(len(results.hand_landmarks)):
                    landmarks_list = results.hand_landmarks[i]
                    handedness_cat = results.handedness[i][0]
                    
                    # Extract landmarks directly as tuple
                    landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks_list]
                    
                    # Get hand label and confidence
                    label = handedness_cat.category_name
                    confidence = handedness_cat.score
                    
                    hands_data.append({
                        'landmarks': landmarks,
                        'handedness': label,
                        'confidence': confidence,
                        'landmarks_raw': landmarks_list  # For drawing
                    })
            
            return hands_data, True
            
        except Exception as e:
            logger.error(f"Hand detection error: {e}")
            return [], False
    
    def check_hand_visibility(self, landmarks: List) -> float:
        """
        Check hand visibility quality based on landmarks spread.
        """
        try:
            bbox = LandmarksProcessor.get_hand_bounding_box(landmarks)
            
            # Calculate spread metric
            spread = (bbox['width'] * bbox['height'])
            
            # Normalize (empirical values for typical camera distance)
            visibility = min(spread / 0.3, 1.0)  # Normalize to 0-1
            
            return visibility
            
        except Exception as e:
            logger.error(f"Visibility check error: {e}")
            return 0.0
    
    def draw_hands(self, frame, hands_data) -> None:
        """
        Draw hand landmarks and skeleton on frame using OpenCV directly.
        """
        try:
            height, width = frame.shape[:2]
            
            for hand in hands_data:
                if 'landmarks_raw' in hand:
                    landmarks_raw = hand['landmarks_raw']
                    
                    # Store pixel coordinates
                    pixel_landmarks = []
                    for lm in landmarks_raw:
                        x_px = min(int(lm.x * width), width - 1)
                        y_px = min(int(lm.y * height), height - 1)
                        pixel_landmarks.append((x_px, y_px))
                        
                        # Draw circle for landmark
                        cv2.circle(frame, (x_px, y_px), 3, (0, 255, 0), -1)
                        
                    # Draw connections
                    for connection in self.HAND_CONNECTIONS:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        
                        start_point = pixel_landmarks[start_idx]
                        end_point = pixel_landmarks[end_idx]
                        
                        cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
                        
        except Exception as e:
            logger.error(f"Drawing error: {e}")
    
    def get_hand_center_in_frame(self, frame, landmarks: List) -> Tuple[int, int]:
        """
        Get hand center position in frame coordinates.
        """
        height, width = frame.shape[:2]
        center = LandmarksProcessor.get_hand_center(landmarks)
        
        x = int(center[0] * width)
        y = int(center[1] * height)
        
        return (x, y)
    
    def set_max_hands(self, max_num_hands: int) -> None:
        """
        Change maximum number of hands to detect.
        """
        max_num_hands = max(1, min(max_num_hands, 2))
        
        if max_num_hands != self.max_num_hands:
            self.max_num_hands = max_num_hands
            
            if hasattr(self, 'detector') and self.detector is not None:
                self.detector.close()
            
            base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=self.max_num_hands,
                min_hand_detection_confidence=self.min_detection_confidence,
                min_hand_presence_confidence=self.min_tracking_confidence,
                min_tracking_confidence=self.min_tracking_confidence,
                running_mode=vision.RunningMode.VIDEO
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            
            logger.info(f"Max hands changed to {self.max_num_hands}")
    
    def release(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, 'detector') and self.detector is not None:
            self.detector.close()
            logger.info("Hand detector released")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.release()
