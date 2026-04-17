"""
Pinch-based swipe gesture recognizer for Subway Surfers control.

Detects when thumb and index finger are pinched together, then tracks
hand movement direction to determine swipe gestures (up/down/left/right).

This module works ALONGSIDE the existing GestureRecognizer — it does NOT
replace it.
"""

import time
from typing import Tuple, Optional
from src.utils.logger import setup_logger
from src.utils.angle_calculator import calculate_distance
from src.utils.landmarks_processor import LandmarksProcessor


logger = setup_logger(__name__)


class PinchSwipeRecognizer:
    """
    Recognizes pinch + directional swipe gestures.
    
    Logic:
    1. Detect pinch (thumb tip touches index tip)
    2. Record starting hand position when pinch begins
    3. Track hand movement while pinched
    4. When movement exceeds threshold → trigger swipe
    5. Cooldown prevents repeated triggers
    6. When pinch is released → reset state
    """
    
    # Swipe direction constants
    SWIPE_NONE = 'NONE'
    SWIPE_UP = 'SWIPE_UP'
    SWIPE_DOWN = 'SWIPE_DOWN'
    SWIPE_LEFT = 'SWIPE_LEFT'
    SWIPE_RIGHT = 'SWIPE_RIGHT'
    PINCH_HOLD = 'PINCH_HOLD'  # Pinching but not swiping yet
    
    def __init__(self, config: dict = None):
        """
        Initialize pinch swipe recognizer.
        
        Args:
            config: Configuration dictionary with thresholds
        """
        config = config or {}
        
        # Thresholds
        self.pinch_threshold = config.get('pinch_threshold', 0.05)
        self.swipe_threshold = config.get('swipe_threshold', 0.08)
        self.swipe_cooldown = config.get('swipe_cooldown', 0.4)
        
        # State tracking
        self.is_pinching = False
        self.pinch_start_pos = None      # (x, y) when pinch started
        self.last_swipe_time = 0          # Timestamp of last swipe
        self.last_swipe_direction = self.SWIPE_NONE
        self.swipe_executed = False       # Whether a swipe was triggered in current pinch
        
        logger.info(f"PinchSwipeRecognizer initialized (pinch_thresh: {self.pinch_threshold}, "
                     f"swipe_thresh: {self.swipe_threshold}, cooldown: {self.swipe_cooldown}s)")
    
    def recognize(self, landmarks: list) -> Tuple[str, float, dict]:
        """
        Recognize pinch + swipe gesture from hand landmarks.
        
        Args:
            landmarks: List of 21 (x, y, z) landmark tuples
            
        Returns:
            Tuple[swipe_direction, confidence, debug_info]:
                - swipe_direction: SWIPE_UP/DOWN/LEFT/RIGHT/PINCH_HOLD/NONE
                - confidence: 0.0 to 1.0
                - debug_info: dict with pinch state details for UI overlay
        """
        try:
            # Get thumb and index tip positions
            thumb_tip = landmarks[LandmarksProcessor.THUMB_TIP]
            index_tip = landmarks[LandmarksProcessor.INDEX_TIP]
            
            # Calculate pinch distance
            pinch_distance = calculate_distance(thumb_tip, index_tip)
            
            # Get hand center for position tracking (use wrist for stability)
            hand_pos = landmarks[LandmarksProcessor.WRIST]
            current_pos = (hand_pos[0], hand_pos[1])
            
            # Debug info for UI
            debug_info = {
                'pinch_distance': pinch_distance,
                'is_pinching': False,
                'hand_pos': current_pos,
                'start_pos': self.pinch_start_pos,
                'dx': 0,
                'dy': 0,
            }
            
            # Check if pinching
            is_currently_pinching = pinch_distance < self.pinch_threshold
            
            if is_currently_pinching:
                debug_info['is_pinching'] = True
                
                if not self.is_pinching:
                    # Pinch just started — record starting position
                    self.is_pinching = True
                    self.pinch_start_pos = current_pos
                    self.swipe_executed = False
                    logger.debug(f"Pinch started at ({current_pos[0]:.3f}, {current_pos[1]:.3f})")
                    return self.PINCH_HOLD, 0.8, debug_info
                
                # Already pinching — check for swipe direction
                if self.pinch_start_pos is not None and not self.swipe_executed:
                    dx = current_pos[0] - self.pinch_start_pos[0]
                    dy = current_pos[1] - self.pinch_start_pos[1]
                    
                    debug_info['dx'] = dx
                    debug_info['dy'] = dy
                    debug_info['start_pos'] = self.pinch_start_pos
                    
                    # Check cooldown
                    now = time.time()
                    if (now - self.last_swipe_time) < self.swipe_cooldown:
                        return self.PINCH_HOLD, 0.7, debug_info
                    
                    # Determine swipe direction (check which axis has larger movement)
                    abs_dx = abs(dx)
                    abs_dy = abs(dy)
                    
                    if abs_dx > self.swipe_threshold or abs_dy > self.swipe_threshold:
                        if abs_dx > abs_dy:
                            # Horizontal swipe
                            if dx > 0:
                                direction = self.SWIPE_RIGHT
                            else:
                                direction = self.SWIPE_LEFT
                        else:
                            # Vertical swipe
                            if dy > 0:
                                direction = self.SWIPE_DOWN
                            else:
                                direction = self.SWIPE_UP
                        
                        # Trigger swipe
                        self.last_swipe_time = now
                        self.last_swipe_direction = direction
                        self.swipe_executed = True
                        
                        logger.info(f"Swipe detected: {direction} (dx={dx:.3f}, dy={dy:.3f})")
                        return direction, 0.95, debug_info
                
                return self.PINCH_HOLD, 0.7, debug_info
            
            else:
                # Not pinching
                if self.is_pinching:
                    # Pinch just released — reset
                    logger.debug("Pinch released")
                    self.is_pinching = False
                    self.pinch_start_pos = None
                    self.swipe_executed = False
                
                return self.SWIPE_NONE, 0.0, debug_info
                
        except Exception as e:
            logger.error(f"PinchSwipe recognition error: {e}")
            return self.SWIPE_NONE, 0.0, {}
    
    def reset(self) -> None:
        """Reset all state."""
        self.is_pinching = False
        self.pinch_start_pos = None
        self.swipe_executed = False
        self.last_swipe_direction = self.SWIPE_NONE
    
    def update_thresholds(self, config: dict) -> None:
        """
        Update recognition thresholds.
        
        Args:
            config: Configuration dictionary
        """
        self.pinch_threshold = config.get('pinch_threshold', self.pinch_threshold)
        self.swipe_threshold = config.get('swipe_threshold', self.swipe_threshold)
        self.swipe_cooldown = config.get('swipe_cooldown', self.swipe_cooldown)
        
        logger.info("PinchSwipe thresholds updated")
