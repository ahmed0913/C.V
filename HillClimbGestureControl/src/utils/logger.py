"""
Logging setup and utility functions.

This module configures logging for the entire application with both
file and console output for debugging and performance tracking.
"""

import logging
import os
from datetime import datetime


def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (all messages)
    log_file = f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


def log_performance(logger: logging.Logger, fps: float, latency_ms: float, 
                   gesture: str, memory_mb: float) -> None:
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance
        fps: Frames per second
        latency_ms: Gesture detection latency in milliseconds
        gesture: Currently detected gesture
        memory_mb: Memory usage in MB
    """
    logger.debug(f"Performance - FPS: {fps:.1f}, Latency: {latency_ms:.1f}ms, "
                f"Gesture: {gesture}, Memory: {memory_mb:.1f}MB")


def log_gesture_event(logger: logging.Logger, gesture: str, key: str, 
                     confidence: float) -> None:
    """
    Log when a gesture is detected and key is pressed.
    
    Args:
        logger: Logger instance
        gesture: Gesture name
        key: Key being pressed
        confidence: Confidence level (0-1)
    """
    logger.info(f"Gesture detected: {gesture} (confidence: {confidence:.2f}) "
               f"-> Key: {key}")
