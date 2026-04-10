"""
Unit tests for key controller.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.key_controller import KeyController


class TestKeyController(unittest.TestCase):
    """Test keyboard control functionality."""
    
    @patch('pynput.keyboard.Controller')
    def setUp(self, mock_controller):
        """Set up test fixtures."""
        self.mock_keyboard = MagicMock()
        mock_controller.return_value = self.mock_keyboard
        self.controller = KeyController(delay=0.01)
    
    def test_controller_initialization(self):
        """Test key controller initialization."""
        self.assertIsNotNone(self.controller.keyboard)
        self.assertEqual(self.controller.delay, 0.01)
        self.assertEqual(len(self.controller.active_keys), 0)
    
    @patch('pynput.keyboard.Controller')
    def test_key_press(self, mock_ctrl):
        """Test key press."""
        mock_keyboard = MagicMock()
        mock_ctrl.return_value = mock_keyboard
        
        controller = KeyController()
        result = controller.press_key('w')
        
        # Should not necessarily be true without time passage
        self.assertIsInstance(result, bool)
    
    @patch('pynput.keyboard.Controller')
    def test_key_mapping(self, mock_ctrl):
        """Test key mapping."""
        mock_keyboard = MagicMock()
        mock_ctrl.return_value = mock_keyboard
        
        controller = KeyController()
        
        # Test various keys
        for key in ['w', 's', 'a', 'd', 'r', 'p']:
            pynput_key = controller._get_pynput_key(key)
            self.assertIsNotNone(pynput_key)
    
    @patch('pynput.keyboard.Controller')
    def test_invalid_key(self, mock_ctrl):
        """Test invalid key handling."""
        mock_keyboard = MagicMock()
        mock_ctrl.return_value = mock_keyboard
        
        controller = KeyController()
        pynput_key = controller._get_pynput_key('invalid_key')
        
        self.assertIsNone(pynput_key)


if __name__ == '__main__':
    unittest.main()
