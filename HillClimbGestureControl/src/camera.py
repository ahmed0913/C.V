"""
Camera management and frame capture.

Handles webcam initialization, frame capture, and release with proper
error handling and performance monitoring.
"""

import cv2
import time
from typing import Tuple, Optional, Any
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Camera:
    """
    Manages webcam input and frame capture.
    
    Provides interface for:
    - Webcam initialization
    - Frame capture
    - FPS calculation
    - Resource cleanup
    """
    
    def __init__(self, camera_id: int = 0, width: int = 640, 
                 height: int = 480, fps: int = 30):
        """
        Initialize camera.
        
        Args:
            camera_id: Camera device ID (0 for default)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.target_fps = fps
        self.frame_time = 1.0 / fps
        
        self.cap = None
        self.is_opened = False
        self.current_fps = 0
        self.previous_frame_time = 0
        self.frame_count = 0
        
        self._open_camera()
    
    def _open_camera(self) -> bool:
        """
        Open and configure camera.
        
        Returns:
            bool: True if successful
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            # Set auto-focus and exposure for better hand visibility
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            
            # Get actual properties
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps")
            self.is_opened = True
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[Any]]:
        """
        Capture and return a frame.
        
        Includes FPS calculation and frame timing.
        
        Returns:
            Tuple[bool, frame]: (success, frame) where frame is None on failure
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        try:
            success, frame = self.cap.read()
            
            if success:
                self.frame_count += 1
                self._update_fps()
                
            return success, frame
            
        except Exception as e:
            logger.error(f"Frame capture error: {e}")
            return False, None
    
    def _update_fps(self) -> None:
        """Update FPS calculation."""
        current_time = time.time()
        
        if self.previous_frame_time > 0:
            delta_time = current_time - self.previous_frame_time
            if delta_time > 0:
                self.current_fps = 0.9 * self.current_fps + 0.1 * (1.0 / delta_time)
        
        self.previous_frame_time = current_time
    
    def get_fps(self) -> float:
        """
        Get current FPS.
        
        Returns:
            float: Frames per second
        """
        return self.current_fps
    
    def get_frame_count(self) -> int:
        """
        Get total frames captured.
        
        Returns:
            int: Frame count
        """
        return self.frame_count
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Change camera resolution.
        
        Args:
            width: New frame width
            height: New frame height
            
        Returns:
            bool: True if successful
        """
        if not self.is_opened or self.cap is None:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if actual_width == width and actual_height == height:
                self.width = width
                self.height = height
                logger.info(f"Resolution changed to {width}x{height}")
                return True
            else:
                logger.warning(f"Resolution set to {actual_width}x{actual_height}")
                return True
                
        except Exception as e:
            logger.error(f"Resolution change error: {e}")
            return False
    
    def get_resolution(self) -> Tuple[int, int]:
        """
        Get current resolution.
        
        Returns:
            Tuple[int, int]: (width, height)
        """
        return (self.width, self.height)
    
    def flip_frame(self, frame) -> None:
        """
        Horizontally flip frame (for mirror effect).
        
        Args:
            frame: Input frame
            
        Returns:
            Flipped frame
        """
        return cv2.flip(frame, 1)
    
    def release(self) -> None:
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            logger.info(f"Camera released. Total frames captured: {self.frame_count}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.release()
