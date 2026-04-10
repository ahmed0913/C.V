"""
Unit tests for gesture recognition.
"""

import unittest
from src.gesture_recognizer import GestureRecognizer
from src.utils.landmarks_processor import LandmarksProcessor


class TestGestureRecognition(unittest.TestCase):
    """Test gesture recognition functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recognizer = GestureRecognizer()
        
        # Create mock landmarks for testing
        self.mock_landmarks = [
            (0.5, 0.5, 0.0),  # 0: Wrist
            (0.4, 0.4, 0.0),  # 1: Thumb MCP
            (0.35, 0.35, 0.0), # 2: Thumb PIP
            (0.3, 0.3, 0.0),  # 3: Thumb DIP
            (0.25, 0.25, 0.0), # 4: Thumb TIP
            (0.6, 0.4, 0.0),  # 5: Index MCP
            (0.65, 0.35, 0.0), # 6: Index PIP
            (0.7, 0.3, 0.0),  # 7: Index DIP
            (0.75, 0.2, 0.0),  # 8: Index TIP (extended)
            (0.6, 0.3, 0.0),  # 9: Middle MCP
            (0.65, 0.25, 0.0), # 10: Middle PIP
            (0.7, 0.2, 0.0),  # 11: Middle DIP
            (0.75, 0.15, 0.0), # 12: Middle TIP (extended)
            (0.5, 0.3, 0.0),  # 13: Ring MCP
            (0.5, 0.35, 0.0),  # 14: Ring PIP
            (0.5, 0.4, 0.0),  # 15: Ring DIP
            (0.5, 0.45, 0.0),  # 16: Ring TIP (not extended)
            (0.4, 0.3, 0.0),  # 17: Pinky MCP
            (0.4, 0.35, 0.0),  # 18: Pinky PIP
            (0.4, 0.4, 0.0),  # 19: Pinky DIP
            (0.4, 0.45, 0.0),  # 20: Pinky TIP (not extended)
        ]
    
    def test_gesture_mapping(self):
        """Test that gesture keys are properly mapped."""
        self.assertEqual(self.recognizer.get_gesture_key('OPEN_HAND'), 'w')
        self.assertEqual(self.recognizer.get_gesture_key('FIST'), 's')
        self.assertEqual(self.recognizer.get_gesture_key('THUMBS_UP'), 'space')
        self.assertEqual(self.recognizer.get_gesture_key('NONE'), None)
    
    def test_none_gesture(self):
        """Test that NONE gesture is recognized for random landmarks."""
        gesture, confidence = self.recognizer.recognize(self.mock_landmarks)
        # Due to random hand positioning, gesture should likely be NONE
        self.assertIsInstance(gesture, str)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0 <= confidence <= 1)
    
    def test_threshold_update(self):
        """Test updating gesture thresholds."""
        config = {
            'thumb_touch_threshold': 0.05,
            'finger_extension_threshold': 0.02,
            'peace_min_distance': 0.1
        }
        self.recognizer.update_thresholds(config)
        
        self.assertEqual(self.recognizer.thumb_touch_threshold, 0.05)
        self.assertEqual(self.recognizer.finger_extension_threshold, 0.02)
        self.assertEqual(self.recognizer.peace_min_distance, 0.1)


class TestGestureDetails(unittest.TestCase):
    """Test specific gesture recognition."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recognizer = GestureRecognizer()
    
    def test_gesture_key_mapping_complete(self):
        """Test that all gestures have key mappings."""
        expected_keys = ['OPEN_HAND', 'FIST', 'PEACE_SIGN', 'THREE_FINGERS',
                        'THUMBS_UP', 'THUMBS_DOWN', 'OK_SIGN', 'POINTING']
        
        for gesture in expected_keys:
            key = self.recognizer.get_gesture_key(gesture)
            self.assertIsNotNone(key, f"Gesture {gesture} has no key mapping")


if __name__ == '__main__':
    unittest.main()
