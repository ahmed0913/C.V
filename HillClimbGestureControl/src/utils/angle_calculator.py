"""
Angle calculation utilities using vector mathematics.

This module provides functions to calculate angles between hand landmarks
using dot product and vector mathematics for gesture recognition.
"""

import numpy as np
import math


def calculate_distance(point1: tuple, point2: tuple) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: (x, y) or (x, y, z) tuple
        point2: (x, y) or (x, y, z) tuple
        
    Returns:
        float: Distance between points
    """
    point1 = np.array(point1[:2])  # Use only x, y for 2D
    point2 = np.array(point2[:2])
    return float(np.linalg.norm(point1 - point2))


def calculate_angle(point1: tuple, vertex: tuple, point2: tuple) -> float:
    """
    Calculate angle formed by three points using dot product.
    
    The angle is calculated at the vertex point between vectors:
    - vector1: from vertex to point1
    - vector2: from vertex to point2
    
    Args:
        point1: First point (x, y, z)
        vertex: Vertex point (x, y, z)
        point2: Second point (x, y, z)
        
    Returns:
        float: Angle in degrees (0-180)
    """
    # Extract x, y coordinates
    p1 = np.array([point1[0], point1[1]])
    v = np.array([vertex[0], vertex[1]])
    p2 = np.array([point2[0], point2[1]])
    
    # Create vectors from vertex to other points
    vec1 = p1 - v
    vec2 = p2 - v
    
    # Calculate dot product and magnitudes
    dot_product = np.dot(vec1, vec2)
    magnitude1 = np.linalg.norm(vec1)
    magnitude2 = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Calculate cosine of angle
    cos_angle = dot_product / (magnitude1 * magnitude2)
    
    # Clamp to [-1, 1] to avoid numerical errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    # Convert to degrees
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    return float(angle_deg)


def calculate_finger_angle(tip: tuple, pip: tuple, mcp: tuple) -> float:
    """
    Calculate finger joint angle (TIP-PIP-MCP).
    
    Args:
        tip: Finger tip landmark (index 4, 8, 12, 16, 20)
        pip: PIP joint landmark (index 2, 6, 10, 14, 18)
        mcp: MCP joint landmark (index 1, 5, 9, 13, 17)
        
    Returns:
        float: Joint angle in degrees
    """
    return calculate_angle(tip, pip, mcp)


def calculate_hand_orientation(wrist: tuple, middle_finger_tip: tuple) -> float:
    """
    Calculate hand orientation angle (vertical tilt).
    
    Args:
        wrist: Wrist landmark position (x, y, z)
        middle_finger_tip: Middle finger tip landmark (x, y, z)
        
    Returns:
        float: Angle in degrees relative to vertical (0-180)
    """
    # Vector from wrist to middle finger tip
    dx = middle_finger_tip[0] - wrist[0]
    dy = middle_finger_tip[1] - wrist[1]
    
    # Calculate angle relative to vertical (upward)
    # atan2 returns -π to π, we'll convert to 0-180
    angle_rad = np.arctan2(dx, -dy)  # Negative dy for upward reference
    angle_deg = np.degrees(angle_rad)
    
    # Normalize to 0-180
    if angle_deg < 0:
        angle_deg += 180
    
    return float(angle_deg)


def calculate_palm_width(index_mcp: tuple, pinky_mcp: tuple) -> float:
    """
    Calculate palm width for hand size normalization.
    
    Args:
        index_mcp: Index MCP landmark (x, y, z)
        pinky_mcp: Pinky MCP landmark (x, y, z)
        
    Returns:
        float: Palm width in pixels
    """
    return calculate_distance(index_mcp, pinky_mcp)


def is_finger_extended(tip: tuple, pip: tuple, threshold: float = 0.0) -> bool:
    """
    Check if a finger is extended based on tip position relative to PIP.
    
    A finger is extended when the tip is ABOVE the PIP joint
    (lower y-coordinate in image space).
    
    Args:
        tip: Finger tip landmark (x, y, z)
        pip: PIP joint landmark (x, y, z)
        threshold: Optional y-distance threshold (in normalized coordinates)
        
    Returns:
        bool: True if finger is extended
    """
    # In image coordinates, y increases downward
    # So tip is "above" PIP if tip.y < pip.y
    return tip[1] < (pip[1] - threshold)


def count_extended_fingers(landmarks: list, threshold: float = 0.0) -> int:
    """
    Count number of extended fingers.
    
    Finger landmarks: [0: wrist, 1-4: thumb, 5-8: index, 9-12: middle,
                      13-16: ring, 17-20: pinky]
    
    Args:
        landmarks: List of 21 (x, y, z) landmark tuples
        threshold: Optional y-distance threshold
        
    Returns:
        int: Number of extended fingers (0-5)
    """
    # Finger tips and PIPs: (tip_idx, pip_idx)
    fingers = [(4, 2), (8, 6), (12, 10), (16, 14), (20, 18)]
    
    extended_count = 0
    for tip_idx, pip_idx in fingers:
        if is_finger_extended(landmarks[tip_idx], landmarks[pip_idx], threshold):
            extended_count += 1
    
    return extended_count


def normalize_coordinates(landmarks: list, width: int, height: int) -> list:
    """
    Normalize hand landmarks to 0-1 range.
    
    Args:
        landmarks: List of (x, y, z) tuples in pixel coordinates
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        list: Normalized landmarks with coordinates in 0-1 range
    """
    normalized = []
    for x, y, z in landmarks:
        norm_x = x / width if width > 0 else x
        norm_y = y / height if height > 0 else y
        normalized.append((norm_x, norm_y, z))
    
    return normalized
