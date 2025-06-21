import unittest
from unittest.mock import patch
from tools.clipboard_tool import set_clipboard_text, get_clipboard_text

class TestClipboardToolFunctions(unittest.TestCase):
    """Unit tests for the clipboard tool functions."""

    @patch('tools.clipboard_tool._APPKIT_AVAILABLE', False)
    @patch('tools.clipboard_tool.pyperclip.copy')
    def test_set_clipboard_text_success(self, mock_copy):
        """Verify set_clipboard_text calls the underlying clipboard library."""
        text_to_copy = "Hello, Atlas!"
        result = set_clipboard_text(text_to_copy)
        mock_copy.assert_called_once_with(text_to_copy)
        self.assertTrue(result.success)
        self.assertEqual(result.action, "set_text")

    @patch('tools.clipboard_tool._APPKIT_AVAILABLE', False)
    @patch('tools.clipboard_tool.pyperclip.paste')
    def test_get_clipboard_text_success(self, mock_paste):
        """Verify get_clipboard_text returns text from the clipboard."""
        expected_text = "Pasted text"
        mock_paste.return_value = expected_text
        result = get_clipboard_text()
        mock_paste.assert_called_once()
        self.assertTrue(result.success)
        self.assertEqual(result.action, "get_text")
        self.assertEqual(result.content, expected_text)

    @patch('tools.clipboard_tool._APPKIT_AVAILABLE', False)
    @patch('tools.clipboard_tool.pyperclip.copy', side_effect=Exception("Clipboard error"))
    def test_set_clipboard_text_failure(self, mock_copy):
        """Verify set_clipboard_text handles exceptions and returns a failure result."""
        result = set_clipboard_text("some text")
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIn("Clipboard error", result.error)

if __name__ == '__main__':
    unittest.main()
