import unittest
from unittest.mock import patch, MagicMock
import os
import sys

#Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from tools.notification_tool import NotificationManager

class TestNotificationManager(unittest.TestCase):
    """Unit tests for the NotificationManager."""

    @patch('tools.notification_tool.get_logger')
    def test_send_email(self, mock_get_logger):
        """Verify that send_email logs the correct information."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        manager = NotificationManager()
        manager.send_email("Test Subject", "Test Body", "test@example.com")
        
        self.assertEqual(mock_logger.info.call_count, 3)
        mock_logger.info.assert_any_call("SIMULATING EMAIL NOTIFICATION to test@example.com:")
        mock_logger.info.assert_any_call("  Subject: Test Subject")
        mock_logger.info.assert_any_call("  Body: Test Body")

    @patch('tools.notification_tool.get_logger')
    def test_send_telegram(self, mock_get_logger):
        """Verify that send_telegram logs the correct information."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        manager = NotificationManager()
        manager.send_telegram("Test Message", "12345")
        
        self.assertEqual(mock_logger.info.call_count, 2)
        mock_logger.info.assert_any_call("SIMULATING TELEGRAM NOTIFICATION to chat_id 12345:")
        mock_logger.info.assert_any_call("  Message: Test Message")

    @patch('tools.notification_tool.get_logger')
    def test_send_sms(self, mock_get_logger):
        """Verify that send_sms logs the correct information."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        manager = NotificationManager()
        manager.send_sms("Test SMS", "+15551234567")
        
        self.assertEqual(mock_logger.info.call_count, 2)
        mock_logger.info.assert_any_call("SIMULATING SMS NOTIFICATION to +15551234567:")
        mock_logger.info.assert_any_call("  Message: Test SMS")

if __name__ == '__main__':
    unittest.main()
