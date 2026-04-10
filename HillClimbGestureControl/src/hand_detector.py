"""
MediaPipe hand detection wrapper.

Wraps MediaPipe Hands for hand detection and landmark extraction
with configurable detection thresholds.
"""

import mediapipe as mp
from typing import List, Optional, Tuple
from src.utils.logger import setup_logger
from src.utils.landmarks_processor import LandmarksProcessor


logger = setup_logger(__name__)


class HandDetector:
    """
    Hand detection using MediaPipe.
    
    Detects hands and extracts 21 landmarks per hand using MediaPipe Hands.
    """
    
    def __init__(self, max_num_hands: int = 2, 
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize hand detector.
        
        Args:
            max_num_hands: Maximum number of hands to detect (1 or 2)
            min_detection_confidence: Minimum confidence for hand detection (0-1)
            min_tracking_confidence: Minimum confidence for hand tracking (0-1)
        """
        self.max_num_hands = max(1, min(max_num_hands, 2))
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        logger.info(f"Hand detector initialized - max_hands: {self.max_num_hands}, "
                   f"detection_conf: {self.min_detection_confidence}")
    
    def detect_hands(self, frame) -> Tuple[List, bool]:
        """
        Detect hands and extract landmarks from frame.
        
        Args:
            frame: Input frame (BGR format from OpenCV)
            
        Returns:
            Tuple[hands_data, success]: hands_data is list of hand dictionaries:
                [
                    {
                        'landmarks': [(x, y, z), ...],  # 21 landmarks
                        'handedness': 'Left' or 'Right',
                        'confidence': float (0-1)
                    },
                    ...
                ]
                
                success: True if detection successful
        """
        try:
            # Convert BGR to RGB
            import cv2
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run detection
            results = self.hands.process(frame_rgb)
            
            hands_data = []
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for landmarks_proto, handedness_proto in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):
                    # Extract landmarks
                    landmarks = LandmarksProcessor.extract_hand_data(landmarks_proto)
                    
                    # Get hand label and confidence
                    label = handedness_proto.classification[0].label
                    confidence = handedness_proto.classification[0].score
                    
                    hands_data.append({
                        'landmarks': landmarks,
                        'handedness': label,
                        'confidence': confidence,
                        'landmarks_proto': landmarks_proto  # For drawing
                    })
            
            return hands_data, True
            
        except Exception as e:
            logger.error(f"Hand detection error: {e}")
            return [], False
    
    def check_hand_visibility(self, landmarks: List) -> float:
        """
        Check hand visibility quality based on landmarks spread.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            float: Visibility score (0-1)
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
        Draw hand landmarks and skeleton on frame.
        
        Args:
            frame: Input frame to draw on
            hands_data: Hand data from detect_hands()
        """
        try:
            for hand in hands_data:
                if 'landmarks_proto' in hand:
                    # Draw landmarks and skeleton
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand['landmarks_proto'],
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(
                            color=(0, 255, 0),
                            thickness=2,
                            circle_radius=2
                        ),
                        self.mp_drawing.DrawingSpec(
                            color=(255, 0, 0),
                            thickness=2
                        )
                    )
        except Exception as e:
            logger.error(f"Drawing error: {e}")
    
    def get_hand_center_in_frame(self, frame, landmarks: List) -> Tuple[int, int]:
        """
        Get hand center position in frame coordinates.
        
        Args:
            frame: Input frame
            landmarks: Hand landmarks
            
        Returns:
            Tuple[int, int]: (x, y) pixel coordinates
        """
        height, width = frame.shape[:2]
        center = LandmarksProcessor.get_hand_center(landmarks)
        
        x = int(center[0] * width)
        y = int(center[1] * height)
        
        return (x, y)
    
    def set_max_hands(self, max_num_hands: int) -> None:
        """
        Change maximum number of hands to detect.
        
        Requires re-initialization of MediaPipe.
        
        Args:
            max_num_hands: New maximum (1 or 2)
        """
        max_num_hands = max(1, min(max_num_hands, 2))
        
        if max_num_hands != self.max_num_hands:
            self.max_num_hands = max_num_hands
            self.hands.close()
            
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self.max_num_hands,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            
            logger.info(f"Max hands changed to {self.max_num_hands}")
    
    def release(self) -> None:
        """Release MediaPipe resources."""
        if self.hands is not None:
            self.hands.close()
            logger.info("Hand detector released")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.release()
