"""
Configuration management system.

Handles loading, saving, and managing application configuration from JSON files
with validation and default values.
"""

import json
import os
from typing import Any, Dict, Optional
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ConfigManager:
    """
    Manages application configuration with JSON file persistence.
    """
    
    DEFAULT_CONFIG = {
        'camera': {
            'width': 640,
            'height': 480,
            'fps': 30,
            'camera_id': 0
        },
        'detection': {
            'max_hands': 2,
            'min_detection_confidence': 0.7,
            'min_tracking_confidence': 0.5
        },
        'gesture': {
            'thumb_touch_threshold': 0.03,
            'finger_extension_threshold': 0.01,
            'peace_min_distance': 0.05
        },
        'control': {
            'key_delay': 0.05,
            'flip_frame': True
        },
        'ui': {
            'show_debug_info': True,
            'show_landmarks': True,
            'show_fps': True,
            'font_size': 1.0
        },
        'performance': {
            'frame_rate_limit': 60,
            'skip_frames': 0
        }
    }
    
    def __init__(self, config_file: str = 'config/settings.json'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration JSON file
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from JSON file.
        
        Falls back to defaults if file doesn't exist or is invalid.
        
        Returns:
            bool: True if file loaded successfully
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Merge with defaults (file config overrides defaults)
                self.config = self._deep_merge(self.DEFAULT_CONFIG.copy(), file_config)
                
                logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                logger.info(f"Config file not found, using defaults")
                self.save_config()  # Save defaults
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Config JSON error: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            return False
        except Exception as e:
            logger.error(f"Config load error: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to JSON file.
        
        Returns:
            bool: True if successful
        """
        try:
            # Create config directory if needed
            os.makedirs(os.path.dirname(self.config_file) or '.', exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Config save error: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Args:
            key_path: Path like 'camera.width' or 'gesture.thumb_touch_threshold'
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value by dot-separated path.
        
        Args:
            key_path: Path like 'camera.width'
            value: Value to set
            
        Returns:
            bool: True if successful
        """
        try:
            keys = key_path.split('.')
            config = self.config
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            logger.debug(f"Config set: {key_path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Config set error: {e}")
            return False
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            bool: True if all values are valid
        """
        try:
            # Camera settings
            width = self.get('camera.width', 640)
            height = self.get('camera.height', 480)
            fps = self.get('camera.fps', 30)
            
            if not (320 <= width <= 1920):
                logger.warning(f"Invalid camera width: {width}")
            if not (240 <= height <= 1080):
                logger.warning(f"Invalid camera height: {height}")
            if not (5 <= fps <= 60):
                logger.warning(f"Invalid FPS: {fps}")
            
            # Confidence thresholds
            det_conf = self.get('detection.min_detection_confidence', 0.7)
            track_conf = self.get('detection.min_tracking_confidence', 0.5)
            
            if not (0.0 <= det_conf <= 1.0):
                logger.warning(f"Invalid detection confidence: {det_conf}")
            if not (0.0 <= track_conf <= 1.0):
                logger.warning(f"Invalid tracking confidence: {track_conf}")
            
            return True
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False
    
    def get_all(self) -> dict:
        """
        Get entire configuration.
        
        Returns:
            dict: Full configuration
        """
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("Configuration reset to defaults")
    
    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """
        Recursively merge override config into base config.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            dict: Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
