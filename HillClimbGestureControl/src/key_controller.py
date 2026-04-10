"""
Keyboard control simulation using pynput.

Handles keyboard input simulation for controlling Hill Climb Racing game
with support for key press/release and key combinations.
"""

from pynput.keyboard import Controller, Key
import time
from typing import Optional
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class KeyController:
    """
    Simulates keyboard input for game control.
    
    Uses pynput for cross-platform keyboard simulation.
    """
    
    # Map gesture keys to pynput Key objects
    KEY_MAP = {
        'w': 'w',                  # Gas
        's': 's',                  # Brake
        'a': 'a',                  # Lean Left
        'd': 'd',                  # Lean Right
        'space': Key.space,        # Nitro
        'shift': Key.shift,        # Emergency Brake
        'r': 'r',                  # Reset
        'p': 'p',                  # Pause
    }
    
    def __init__(self, delay: float = 0.05):
        """
        Initialize key controller.
        
        Args:
            delay: Delay between key presses in seconds (anti-spam)
        """
        self.keyboard = Controller()
        self.delay = delay  # Minimum time between key presses
        
        self.key_press_times = {}  # Track last press time for each key
        self.active_keys = set()   # Currently pressed keys
        
        logger.info(f"Key controller initialized (delay: {delay}s)")
    
    def _get_pynput_key(self, key_name: str):
        """
        Convert key name to pynput Key object.
        
        Args:
            key_name: Key name (e.g., 'w', 'space', 'shift')
            
        Returns:
            pynput Key object or None
        """
        if key_name in self.KEY_MAP:
            return self.KEY_MAP[key_name]
        return None
    
    def _can_press_key(self, key_name: str) -> bool:
        """
        Check if enough time has passed since last key press (anti-spam).
        
        Args:
            key_name: Key name
            
        Returns:
            bool: True if key can be pressed
        """
        current_time = time.time()
        last_press_time = self.key_press_times.get(key_name, 0)
        
        return (current_time - last_press_time) >= self.delay
    
    def press_key(self, key_name: str) -> bool:
        """
        Simulate pressing a key.
        
        Implements anti-spam delay and tracks active keys.
        
        Args:
            key_name: Key to press ('w', 's', 'space', etc.)
            
        Returns:
            bool: True if key press was simulated
        """
        try:
            # Sanitize key name
            key_name = key_name.lower().strip()
            
            # Check anti-spam delay
            if not self._can_press_key(key_name):
                return False
            
            pynput_key = self._get_pynput_key(key_name)
            
            if pynput_key is None:
                logger.warning(f"Unknown key: {key_name}")
                return False
            
            # Press key
            self.keyboard.press(pynput_key)
            self.active_keys.add(key_name)
            self.key_press_times[key_name] = time.time()
            
            logger.debug(f"Key pressed: {key_name}")
            return True
            
        except Exception as e:
            logger.error(f"Key press error for '{key_name}': {e}")
            return False
    
    def release_key(self, key_name: str) -> bool:
        """
        Simulate releasing a key.
        
        Args:
            key_name: Key to release
            
        Returns:
            bool: True if key release was simulated
        """
        try:
            # Sanitize key name
            key_name = key_name.lower().strip()
            
            pynput_key = self._get_pynput_key(key_name)
            
            if pynput_key is None:
                logger.warning(f"Unknown key: {key_name}")
                return False
            
            # Release key only if it's currently pressed
            if key_name in self.active_keys:
                self.keyboard.release(pynput_key)
                self.active_keys.discard(key_name)
                
                logger.debug(f"Key released: {key_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Key release error for '{key_name}': {e}")
            return False
    
    def press_and_hold(self, key_name: str, duration: float = 0.1) -> bool:
        """
        Press a key for specified duration.
        
        Args:
            key_name: Key to press
            duration: How long to hold in seconds
            
        Returns:
            bool: True if successful
        """
        if self.press_key(key_name):
            time.sleep(duration)
            return self.release_key(key_name)
        return False
    
    def release_all(self) -> None:
        """Release all currently active keys."""
        for key_name in list(self.active_keys):
            self.release_key(key_name)
        
        logger.info("All keys released")
    
    def get_active_keys(self) -> set:
        """
        Get set of currently pressed keys.
        
        Returns:
            set: Active key names
        """
        return self.active_keys.copy()
    
    def set_delay(self, delay: float) -> None:
        """
        Change anti-spam delay.
        
        Args:
            delay: New delay in seconds
        """
        self.delay = max(0.01, delay)  # Minimum 10ms
        logger.info(f"Key delay set to {self.delay}s")
    
    def __del__(self):
        """Destructor to clean up."""
        self.release_all()
