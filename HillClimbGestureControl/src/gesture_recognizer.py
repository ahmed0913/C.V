"""
Rule-based gesture recognition system.

Recognizes 8 hand gestures using geometric rules and hand landmark positions.
NO Machine Learning - pure geometric calculations.

Gestures:
1. OPEN_HAND - All fingers extended → 'W' (Gas)
2. FIST - All fingers closed → 'S' (Brake)
3. PEACE_SIGN - Index + middle up → 'A' (Lean Left)
4. THREE_FINGERS - First 3 fingers up → 'D' (Lean Right)
5. THUMBS_UP - Thumb highest → 'SPACE' (Nitro)
6. THUMBS_DOWN - Thumb lowest → 'SHIFT' (Emergency Brake)
7. OK_SIGN - Thumb + index circle → 'R' (Reset)
8. POINTING - Only index up → 'P' (Pause)
"""

from typing import Tuple, Optional
from src.utils.logger import setup_logger
from src.utils.angle_calculator import (
    calculate_distance, calculate_angle, is_finger_extended,
    count_extended_fingers
)
from src.utils.landmarks_processor import LandmarksProcessor


logger = setup_logger(__name__)


class GestureRecognizer:
    """
    Rule-based gesture recognition using hand landmarks.
    
    Each gesture is defined by clear geometric rules that are easy to
    understand and explain.
    """
    
    # Gesture names and their corresponding game keys
    GESTURE_MAP = {
        'OPEN_HAND': 'w',           # Gas
        'FIST': 's',                # Brake
        'PEACE_SIGN': 'a',          # Lean Left
        'THREE_FINGERS': 'd',       # Lean Right
        'THUMBS_UP': 'space',       # Nitro/Boost
        'THUMBS_DOWN': 'shift',     # Emergency Brake
        'OK_SIGN': 'r',             # Reset/Restart
        'POINTING': 'p',            # Pause
        'NONE': None                # No gesture
    }
    
    def __init__(self, config: dict = None):
        """
        Initialize gesture recognizer.
        
        Args:
            config: Configuration dictionary with thresholds
        """
        # Default thresholds (can be tuned)
        self.config = config or {}
        
        self.thumb_touch_threshold = self.config.get('thumb_touch_threshold', 0.03)
        self.finger_extension_threshold = self.config.get('finger_extension_threshold', 0.01)
        self.peace_min_distance = self.config.get('peace_min_distance', 0.05)
        
        self.current_gesture = 'NONE'
        self.confidence = 0.0
        
        logger.info("Gesture recognizer initialized")
    
    def recognize(self, landmarks: list, handedness: str = 'Right') -> Tuple[str, float]:
        """
        Recognize gesture from hand landmarks.
        
        Args:
            landmarks: List of 21 (x, y, z) landmark tuples
            handedness: 'Left' or 'Right' hand
            
        Returns:
            Tuple[gesture_name, confidence]: Gesture name and confidence (0-1)
        """
        try:
            # Check gestures in specific order
            # Order matters: check similar gestures in sequence
            
            if self._is_ok_sign(landmarks):
                return 'OK_SIGN', 0.95
            
            if self._is_thumbs_up(landmarks):
                return 'THUMBS_UP', 0.95
            
            if self._is_thumbs_down(landmarks):
                return 'THUMBS_DOWN', 0.95
            
            if self._is_pointing(landmarks):
                return 'POINTING', 0.90
            
            if self._is_three_fingers(landmarks):
                return 'THREE_FINGERS', 0.90
            
            if self._is_peace_sign(landmarks):
                return 'PEACE_SIGN', 0.90
            
            if self._is_open_hand(landmarks):
                return 'OPEN_HAND', 0.90
            
            if self._is_fist(landmarks):
                return 'FIST', 0.90
            
            return 'NONE', 0.0
            
        except Exception as e:
            logger.error(f"Gesture recognition error: {e}")
            return 'NONE', 0.0
    
    def _is_open_hand(self, landmarks: list) -> bool:
        """
        Check if hand is OPEN (all fingers extended).
        
        Rule: All 5 finger tips must be above their PIP joints.
        This indicates all fingers are extended/straightened.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if open hand gesture detected
        """
        extended_count = count_extended_fingers(landmarks, self.finger_extension_threshold)
        
        # All 5 fingers must be extended
        return extended_count >= 5
    
    def _is_fist(self, landmarks: list) -> bool:
        """
        Check if hand is in FIST (all fingers closed).
        
        Rule: All 5 finger tips must be below their PIP joints.
        This indicates all fingers are folded/closed.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if fist gesture detected
        """
        extended_count = count_extended_fingers(landmarks, self.finger_extension_threshold)
        
        # None or very few fingers extended
        return extended_count <= 1
    
    def _is_peace_sign(self, landmarks: list) -> bool:
        """
        Check if hand is making PEACE_SIGN (index and middle finger up).
        
        Rule: Index and middle finger tips above PIP,
               others (ring, pinky, thumb) below PIP.
        Distance between index and middle should be reasonable.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if peace sign detected
        """
        # Index and middle up
        index_extended = is_finger_extended(
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.INDEX_PIP],
            self.finger_extension_threshold
        )
        middle_extended = is_finger_extended(
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.MIDDLE_PIP],
            self.finger_extension_threshold
        )
        
        # Ring and pinky down
        ring_extended = is_finger_extended(
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.RING_PIP],
            -self.finger_extension_threshold
        )
        pinky_extended = is_finger_extended(
            landmarks[LandmarksProcessor.PINKY_TIP],
            landmarks[LandmarksProcessor.PINKY_PIP],
            -self.finger_extension_threshold
        )
        
        # Index and middle closer to each other (not spread wide)
        index_middle_distance = calculate_distance(
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.MIDDLE_TIP]
        )
        
        return (index_extended and middle_extended and 
                not ring_extended and not pinky_extended and
                index_middle_distance < self.peace_min_distance)
    
    def _is_three_fingers(self, landmarks: list) -> bool:
        """
        Check if THREE_FINGERS are extended (index, middle, ring up).
        
        Rule: First 3 fingers (index, middle, ring) extended,
               thumb and pinky folded.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if three fingers gesture detected
        """
        # Index, middle, ring up
        index_extended = is_finger_extended(
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.INDEX_PIP],
            self.finger_extension_threshold
        )
        middle_extended = is_finger_extended(
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.MIDDLE_PIP],
            self.finger_extension_threshold
        )
        ring_extended = is_finger_extended(
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.RING_PIP],
            self.finger_extension_threshold
        )
        
        # Pinky down
        pinky_extended = is_finger_extended(
            landmarks[LandmarksProcessor.PINKY_TIP],
            landmarks[LandmarksProcessor.PINKY_PIP],
            -self.finger_extension_threshold
        )
        
        return (index_extended and middle_extended and ring_extended 
                and not pinky_extended)
    
    def _is_thumbs_up(self, landmarks: list) -> bool:
        """
        Check if hand is showing THUMBS_UP.
        
        Rule: Thumb tip is ABOVE (higher than) all other finger tips.
        Palm generally closed (other fingers not all extended).
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if thumbs up detected
        """
        thumb_tip = landmarks[LandmarksProcessor.THUMB_TIP]
        finger_tips = [
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.PINKY_TIP]
        ]
        
        # Thumb y-coordinate should be less (higher in image)
        y_positions = [tip[1] for tip in finger_tips]
        
        # Thumb must be above all other fingers
        thumbs_up = thumb_tip[1] < min(y_positions) - 0.02
        
        # Other fingers not too extended (palm quasi-closed)
        extended_count = count_extended_fingers(landmarks, self.finger_extension_threshold)
        palm_quasi_closed = extended_count <= 2
        
        return thumbs_up and palm_quasi_closed
    
    def _is_thumbs_down(self, landmarks: list) -> bool:
        """
        Check if hand is showing THUMBS_DOWN.
        
        Rule: Thumb tip is BELOW (lower than) all other finger tips.
        Palm generally closed.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if thumbs down detected
        """
        thumb_tip = landmarks[LandmarksProcessor.THUMB_TIP]
        finger_tips = [
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.PINKY_TIP]
        ]
        
        # Thumb y-coordinate should be more (lower in image)
        y_positions = [tip[1] for tip in finger_tips]
        
        # Thumb must be below all other fingers
        thumbs_down = thumb_tip[1] > max(y_positions) + 0.02
        
        # Other fingers not too extended (palm quasi-closed)
        extended_count = count_extended_fingers(landmarks, self.finger_extension_threshold)
        palm_quasi_closed = extended_count <= 2
        
        return thumbs_down and palm_quasi_closed
    
    def _is_ok_sign(self, landmarks: list) -> bool:
        """
        Check if hand is making OK_SIGN (thumb and index form circle).
        
        Rule: Distance between thumb tip and index tip is very small (<30px).
        Other fingers extended (showing the circle).
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if ok sign detected
        """
        thumb_tip = landmarks[LandmarksProcessor.THUMB_TIP]
        index_tip = landmarks[LandmarksProcessor.INDEX_TIP]
        
        # Distance between thumb and index should be very small
        thumb_index_distance = calculate_distance(thumb_tip, index_tip)
        
        touch = thumb_index_distance < self.thumb_touch_threshold
        
        # Other fingers should be extended to show the circle
        middle_extended = is_finger_extended(
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.MIDDLE_PIP],
            0.005
        )
        
        return touch and middle_extended
    
    def _is_pointing(self, landmarks: list) -> bool:
        """
        Check if hand is POINTING (only index finger extended).
        
        Rule: Only index finger tip is above PIP,
               all other fingers below PIP.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if pointing gesture detected
        """
        # Index extended
        index_extended = is_finger_extended(
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.INDEX_PIP],
            self.finger_extension_threshold
        )
        
        # All others folded
        thumb_extended = is_finger_extended(
            landmarks[LandmarksProcessor.THUMB_TIP],
            landmarks[LandmarksProcessor.THUMB_PIP],
            -self.finger_extension_threshold
        )
        middle_extended = is_finger_extended(
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.MIDDLE_PIP],
            -self.finger_extension_threshold
        )
        ring_extended = is_finger_extended(
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.RING_PIP],
            -self.finger_extension_threshold
        )
        pinky_extended = is_finger_extended(
            landmarks[LandmarksProcessor.PINKY_TIP],
            landmarks[LandmarksProcessor.PINKY_PIP],
            -self.finger_extension_threshold
        )
        
        return (index_extended and not thumb_extended and 
                not middle_extended and not ring_extended and not pinky_extended)
    
    def get_gesture_key(self, gesture_name: str) -> Optional[str]:
        """
        Get keyboard key for a gesture.
        
        Args:
            gesture_name: Gesture name
            
        Returns:
            str: Key name or None
        """
        return self.GESTURE_MAP.get(gesture_name, None)
    
    def update_thresholds(self, config: dict) -> None:
        """
        Update recognition thresholds.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.thumb_touch_threshold = config.get('thumb_touch_threshold', self.thumb_touch_threshold)
        self.finger_extension_threshold = config.get('finger_extension_threshold', 
                                                     self.finger_extension_threshold)
        self.peace_min_distance = config.get('peace_min_distance', self.peace_min_distance)
        
        logger.info("Gesture thresholds updated")
