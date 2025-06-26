import unittest
from unittest.mock import MagicMock, patch
from input.gesture_hotkey_mapper import GestureHotkeyMapper

class TestGestureHotkeyMapper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mapper = GestureHotkeyMapper()
        
    def test_initialization(self):
        """Test initialization of gesture hotkey mapper"""
        self.assertEqual(len(self.mapper.hotkey_mappings), 0)
        self.assertFalse(self.mapper.is_listening)
        
    def test_register_hotkey(self):
        """Test registering a hotkey mapping"""
        hotkey = "ctrl+shift+w"
        action = {"action": "create_workflow", "parameters": {"name": "quick workflow"}}
        self.mapper.register_hotkey(hotkey, action)
        self.assertIn(hotkey, self.mapper.hotkey_mappings)
        self.assertEqual(self.mapper.hotkey_mappings[hotkey], action)
        
    @patch('keyboard.add_hotkey')
    def test_start_listening(self, mock_keyboard_hotkey):
        """Test starting to listen for hotkeys"""
        hotkey = "ctrl+alt+t"
        action = {"action": "start_task", "parameters": {}}
        self.mapper.register_hotkey(hotkey, action)
        
        self.mapper.start_listening()
        self.assertTrue(self.mapper.is_listening)
        mock_keyboard_hotkey.assert_called()
        
        # Test calling start_listening again (should do nothing)
        with patch.object(self.mapper, '_handle_hotkey', return_value=None) as mock_handle:
            self.mapper.start_listening()
            mock_handle.assert_not_called()
        
    @patch('keyboard.clear_all_hotkeys')
    def test_stop_listening(self, mock_keyboard_clear):
        """Test stopping listening for hotkeys"""
        self.mapper.is_listening = True
        self.mapper.stop_listening()
        self.assertFalse(self.mapper.is_listening)
        mock_keyboard_clear.assert_called_once()
        
        # Test calling stop_listening again (should do nothing)
        with patch.object(self.mapper, '_handle_hotkey', return_value=None) as mock_handle:
            self.mapper.stop_listening()
            mock_handle.assert_not_called()
        
    def test_handle_hotkey(self):
        """Test handling a hotkey event"""
        hotkey = "ctrl+shift+p"
        action = {"action": "publish_workflow", "parameters": {}}
        self.mapper.hotkey_mappings[hotkey] = action
        
        with patch.object(self.mapper, '_execute_action') as mock_execute:
            self.mapper._handle_hotkey(hotkey)
            mock_execute.assert_called_once_with(action)
        
    def test_execute_action(self):
        """Test executing an action"""
        action = {"action": "test_action", "parameters": {"param1": "value1"}}
        # Just verify it doesn't crash - actual execution would be tested in integration
        try:
            self.mapper._execute_action(action)
            self.assertTrue(True)  # If we get here, no exception was raised
        except Exception:
            self.assertTrue(False, "Executing action raised an exception")

if __name__ == '__main__':
    unittest.main()
