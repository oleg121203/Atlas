import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock the pyaudio availability before importing the module
try:
    import pyaudio
    import speech_recognition as sr
    PY_AUDIO_AVAILABLE = True
except ImportError:
    PY_AUDIO_AVAILABLE = False
    print("PyAudio or speech_recognition not available. Voice command functionality will be disabled.")

# Import after setting up mocks
with patch.dict('sys.modules', {'pyaudio': None if not PY_AUDIO_AVAILABLE else MagicMock(), 'speech_recognition': None if not PY_AUDIO_AVAILABLE else MagicMock()}) as mocked_modules:
    if not PY_AUDIO_AVAILABLE:
        mocked_modules['speech_recognition'] = MagicMock()
        mocked_modules['pyaudio'] = MagicMock()
    from input.voice_command_parser import VoiceCommandParser

class TestVoiceCommandParser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = VoiceCommandParser()
        
    def test_initialization(self):
        """Test initialization of voice command parser"""
        if PY_AUDIO_AVAILABLE:
            self.assertIsNotNone(self.parser.recognizer)
            self.assertIsNotNone(self.parser.microphone)
        else:
            self.assertIsNone(self.parser.recognizer)
            self.assertIsNone(self.parser.microphone)
        self.assertFalse(self.parser.is_calibrated)
        
    @patch('input.voice_command_parser.PY_AUDIO_AVAILABLE', False)
    def test_calibrate_microphone_pyaudio_unavailable(self):
        """Test microphone calibration when pyaudio is not available"""
        self.parser.calibrate_microphone(duration=1)
        self.assertFalse(self.parser.is_calibrated)
        
    @patch('input.voice_command_parser.PY_AUDIO_AVAILABLE', False)
    def test_listen_for_command_pyaudio_unavailable(self):
        """Test listening for command when pyaudio is not available"""
        result = self.parser.listen_for_command(timeout=1)
        self.assertIsNone(result)
        
    def test_parse_command_create_workflow(self):
        """Test parsing a 'create workflow' command"""
        command_text = "create workflow test flow"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "create_workflow")
        self.assertEqual(action['parameters']['name'], "test flow")
        
    def test_parse_command_create_workflow_no_name(self):
        """Test parsing a 'create workflow' command with no specific name"""
        command_text = "create workflow"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "create_workflow")
        self.assertTrue("Workflow_" in action['parameters']['name'])
        
    def test_parse_command_start_task(self):
        """Test parsing a 'start task' command"""
        command_text = "start task urgent task"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "start_task")
        self.assertEqual(action['parameters']['name'], "urgent task")
        
    def test_parse_command_open_dashboard(self):
        """Test parsing an 'open dashboard' command"""
        command_text = "open dashboard"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "open_dashboard")
        self.assertEqual(action['parameters']['name'], "main dashboard")
        
    def test_parse_command_stop_listening(self):
        """Test parsing a 'stop listening' command"""
        command_text = "stop listening"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "stop_listening")
        self.assertEqual(action['parameters'], {})
        
    def test_parse_command_unknown(self):
        """Test parsing an unknown command"""
        command_text = "do something weird"
        action = self.parser.parse_command(command_text)
        self.assertEqual(action['action'], "unknown_command")
        self.assertEqual(action['parameters']['text'], "do something weird")

if __name__ == '__main__':
    unittest.main()
