"""
Hand landmarks processor for MediaPipe hand detection.

This module extracts and processes the 21 hand landmarks from MediaPipe
Hands, organizing them into an easy-to-use structure for gesture recognition.

Hand Landmark Indices:
  0: Wrist
  
  Thumb: 1-4 (MCP, PIP, DIP, TIP)
  Index: 5-8 (MCP, PIP, DIP, TIP)
  Middle: 9-12 (MCP, PIP, DIP, TIP)
  Ring: 13-16 (MCP, PIP, DIP, TIP)
  Pinky: 17-20 (MCP, PIP, DIP, TIP)
"""


class LandmarksProcessor:
    """Process and organize hand landmarks."""
    
    # Landmark indices for easy access
    WRIST = 0
    
    # Thumb
    THUMB_MCP = 1
    THUMB_PIP = 2
    THUMB_DIP = 3
    THUMB_TIP = 4
    
    # Index
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    
    # Middle
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    
    # Ring
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    
    # Pinky
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20
    
    # Finger groups (tip, pip, mcp indices)
    FINGERS = {
        'thumb': (THUMB_TIP, THUMB_PIP, THUMB_MCP),
        'index': (INDEX_TIP, INDEX_PIP, INDEX_MCP),
        'middle': (MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP),
        'ring': (RING_TIP, RING_PIP, RING_MCP),
        'pinky': (PINKY_TIP, PINKY_PIP, PINKY_MCP),
    }
    
    @staticmethod
    def extract_hand_data(landmarks_proto) -> list:
        """
        Extract landmarks from MediaPipe hand detection.
        
        Args:
            landmarks_proto: MediaPipe hand landmarks object
            
        Returns:
            list: List of 21 (x, y, z) tuples
        """
        landmarks = []
        for landmark in landmarks_proto.landmark:
            landmarks.append((landmark.x, landmark.y, landmark.z))
        return landmarks
    
    @staticmethod
    def get_finger_landmarks(landmarks: list, finger_name: str) -> dict:
        """
        Get landmarks for a specific finger.
        
        Args:
            landmarks: List of 21 landmarks
            finger_name: 'thumb', 'index', 'middle', 'ring', or 'pinky'
            
        Returns:
            dict: Finger landmarks with keys 'tip', 'pip', 'mcp'
        """
        if finger_name not in LandmarksProcessor.FINGERS:
            return {}
        
        tip_idx, pip_idx, mcp_idx = LandmarksProcessor.FINGERS[finger_name]
        
        return {
            'tip': landmarks[tip_idx],
            'pip': landmarks[pip_idx],
            'mcp': landmarks[mcp_idx],
            'dip': landmarks[tip_idx - 1]  # DIP is between PIP and TIP
        }
    
    @staticmethod
    def get_all_finger_tips(landmarks: list) -> list:
        """
        Get all five finger tips.
        
        Returns order: [thumb, index, middle, ring, pinky]
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            list: 5 finger tip landmarks
        """
        return [
            landmarks[LandmarksProcessor.THUMB_TIP],
            landmarks[LandmarksProcessor.INDEX_TIP],
            landmarks[LandmarksProcessor.MIDDLE_TIP],
            landmarks[LandmarksProcessor.RING_TIP],
            landmarks[LandmarksProcessor.PINKY_TIP],
        ]
    
    @staticmethod
    def get_hand_center(landmarks: list) -> tuple:
        """
        Calculate hand center (average of all landmarks).
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            tuple: (x, y, z) center position
        """
        x_coords = [l[0] for l in landmarks]
        y_coords = [l[1] for l in landmarks]
        z_coords = [l[2] for l in landmarks]
        
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        center_z = sum(z_coords) / len(z_coords)
        
        return (center_x, center_y, center_z)
    
    @staticmethod
    def get_hand_bounding_box(landmarks: list) -> dict:
        """
        Get bounding box of hand.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            dict: {'x_min', 'x_max', 'y_min', 'y_max', 'width', 'height'}
        """
        x_coords = [l[0] for l in landmarks]
        y_coords = [l[1] for l in landmarks]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return {
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max,
            'width': x_max - x_min,
            'height': y_max - y_min,
            'center_x': (x_min + x_max) / 2,
            'center_y': (y_min + y_max) / 2,
        }
    
    @staticmethod
    def get_wrist_and_middle(landmarks: list) -> tuple:
        """
        Get wrist and middle finger tip for orientation calculation.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            tuple: (wrist, middle_tip) landmarks
        """
        return (
            landmarks[LandmarksProcessor.WRIST],
            landmarks[LandmarksProcessor.MIDDLE_TIP]
        )
    
    @staticmethod
    def is_palm_facing_camera(landmarks: list) -> bool:
        """
        Check if palm is facing the camera (not rotated away).
        
        Heuristic: If landmarks are spread out (not compressed), palm faces camera.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            bool: True if palm is facing camera
        """
        bbox = LandmarksProcessor.get_hand_bounding_box(landmarks)
        
        # Calculate aspect ratio
        aspect_ratio = bbox['width'] / bbox['height'] if bbox['height'] > 0 else 1
        
        # Palm roughly square-ish when facing camera
        return 0.3 < aspect_ratio < 3.0
    
    @staticmethod
    def get_finger_distances_from_center(landmarks: list) -> dict:
        """
        Get distances of all finger tips from hand center.
        
        Useful for gesture recognition and hand size normalization.
        
        Args:
            landmarks: List of 21 landmarks
            
        Returns:
            dict: Distances for each finger
        """
        import math
        center = LandmarksProcessor.get_hand_center(landmarks)
        tips = LandmarksProcessor.get_all_finger_tips(landmarks)
        
        fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
        distances = {}
        
        for finger_name, tip in zip(fingers, tips):
            dist = math.sqrt(
                (tip[0] - center[0])**2 + (tip[1] - center[1])**2
            )
            distances[finger_name] = dist
        
        return distances
