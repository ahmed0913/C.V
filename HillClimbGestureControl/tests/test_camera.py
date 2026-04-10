"""
Unit tests for camera module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.camera import Camera


class TestCamera(unittest.TestCase):
    """Test camera functionality."""
    
    @patch('cv2.VideoCapture')
    def test_camera_initialization(self, mock_capture):
        """Test camera initialization."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 640,  # width
            3: 480,  # height
            5: 30    # fps
        }.get(prop, 0)
        mock_capture.return_value = mock_cap
        
        camera = Camera(width=640, height=480, fps=30)
        
        self.assertTrue(camera.is_opened)
        self.assertEqual(camera.width, 640)
        self.assertEqual(camera.height, 480)
    
    @patch('cv2.VideoCapture')
    def test_frame_capture(self, mock_capture):
        """Test frame capture."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cap.get.return_value = 640
        mock_capture.return_value = mock_cap
        
        camera = Camera()
        success, frame = camera.read_frame()
        
        self.assertTrue(success)
        self.assertIsNotNone(frame)
        self.assertEqual(camera.frame_count, 1)
    
    @patch('cv2.VideoCapture')
    def test_fps_calculation(self, mock_capture):
        """Test FPS calculation."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cap.get.return_value = 640
        mock_capture.return_value = mock_cap
        
        camera = Camera()
        camera.read_frame()
        
        fps = camera.get_fps()
        # FPS should be calculated after at least 2 frames
        self.assertIsInstance(fps, float)


class TestCameraResolution(unittest.TestCase):
    """Test camera resolution settings."""
    
    @patch('cv2.VideoCapture')
    def test_resolution_change(self, mock_capture):
        """Test changing resolution."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 640
        mock_capture.return_value = mock_cap
        
        camera = Camera()
        result = camera.set_resolution(800, 600)
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
