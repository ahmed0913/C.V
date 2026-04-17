"""
Mouse control simulation using pynput for Subway Surfers swipe mode.

Handles mouse click and swipe simulation to control games that use
touch/swipe input (like Subway Surfers on PC via BlueStacks or browser).
"""

from pynput.mouse import Controller as MouseController_pynput, Button
import time
import ctypes
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


def get_screen_size():
    """Get the screen resolution."""
    try:
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080  # Fallback


class MouseController:
    """
    Simulates mouse swipe input for games like Subway Surfers.
    
    Performs swipe gestures by:
    1. Moving mouse to center of screen
    2. Pressing left click
    3. Dragging in the desired direction
    4. Releasing click
    """
    
    def __init__(self, swipe_distance: int = 300, swipe_duration: float = 0.05):
        """
        Initialize mouse controller.
        
        Args:
            swipe_distance: How far to drag the mouse in pixels
            swipe_duration: How long the swipe takes in seconds
        """
        self.mouse = MouseController_pynput()
        self.swipe_distance = swipe_distance
        self.swipe_duration = swipe_duration
        self.is_pressed = False
        
        # Get screen center
        self.screen_w, self.screen_h = get_screen_size()
        self.center_x = self.screen_w // 2
        self.center_y = self.screen_h // 2
        
        logger.info(f"Mouse controller initialized (screen: {self.screen_w}x{self.screen_h}, "
                     f"swipe_distance: {swipe_distance}px)")
    
    def swipe_up(self) -> bool:
        """Perform an upward swipe."""
        return self._do_swipe(0, -self.swipe_distance, "UP")
    
    def swipe_down(self) -> bool:
        """Perform a downward swipe."""
        return self._do_swipe(0, self.swipe_distance, "DOWN")
    
    def swipe_left(self) -> bool:
        """Perform a left swipe."""
        return self._do_swipe(-self.swipe_distance, 0, "LEFT")
    
    def swipe_right(self) -> bool:
        """Perform a right swipe."""
        return self._do_swipe(self.swipe_distance, 0, "RIGHT")
    
    def _do_swipe(self, dx: int, dy: int, direction: str) -> bool:
        """
        Execute a mouse swipe gesture.
        
        Steps:
        1. Move to screen center
        2. Press left button
        3. Drag to target position (smooth movement)
        4. Release left button
        5. Return to center
        
        Args:
            dx: Horizontal pixel offset (positive = right)
            dy: Vertical pixel offset (positive = down)
            direction: Direction name for logging
            
        Returns:
            bool: True if swipe was executed
        """
        try:
            # Move to center first
            self.mouse.position = (self.center_x, self.center_y)
            time.sleep(0.01)
            
            # Press
            self.mouse.press(Button.left)
            time.sleep(0.01)
            
            # Smooth drag in steps
            steps = 5
            for i in range(1, steps + 1):
                target_x = self.center_x + int(dx * i / steps)
                target_y = self.center_y + int(dy * i / steps)
                self.mouse.position = (target_x, target_y)
                time.sleep(self.swipe_duration / steps)
            
            # Release
            self.mouse.release(Button.left)
            
            # Return to center
            time.sleep(0.01)
            self.mouse.position = (self.center_x, self.center_y)
            
            logger.debug(f"Swipe {direction} executed")
            return True
            
        except Exception as e:
            logger.error(f"Swipe error ({direction}): {e}")
            # Safety: release if pressed
            try:
                self.mouse.release(Button.left)
            except:
                pass
            return False
    
    def click(self) -> bool:
        """Perform a single left click at screen center."""
        try:
            self.mouse.position = (self.center_x, self.center_y)
            self.mouse.click(Button.left)
            logger.debug("Click executed")
            return True
        except Exception as e:
            logger.error(f"Click error: {e}")
            return False
    
    def set_swipe_distance(self, distance: int) -> None:
        """
        Change swipe distance.
        
        Args:
            distance: New swipe distance in pixels
        """
        self.swipe_distance = max(50, distance)
        logger.info(f"Swipe distance set to {self.swipe_distance}px")
    
    def release_all(self) -> None:
        """Release mouse button if pressed."""
        try:
            self.mouse.release(Button.left)
        except:
            pass
    
    def __del__(self):
        """Destructor to clean up."""
        self.release_all()
