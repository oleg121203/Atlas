import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from tools.screenshot_tool import capture_screen


class TestScreenshotTool(unittest.TestCase):
    """Unit tests for the screenshot tool."""

    def setUp(self):
        """Create a dummy image for testing."""
        self.mock_image = Image.new("RGB", (100, 50), color="blue")
        #Mock the save method on the image instance itself
        self.mock_image.save = MagicMock()

    @patch("tools.screenshot_tool._QUARTZ_AVAILABLE", True)
    @patch("tools.screenshot_tool._capture_quartz")
    def test_capture_screen_with_quartz(self, mock_capture_quartz):
        """Test capture_screen uses Quartz when available."""
        mock_capture_quartz.return_value = self.mock_image

        img = capture_screen()

        mock_capture_quartz.assert_called_once()
        self.assertEqual(img, self.mock_image)

    @patch("tools.screenshot_tool._QUARTZ_AVAILABLE", False)
    @patch("tools.screenshot_tool.pyautogui.screenshot")
    def test_capture_screen_with_pyautogui_fallback(self, mock_pyautogui_screenshot):
        """Test capture_screen falls back to pyautogui."""
        mock_pyautogui_screenshot.return_value = self.mock_image

        img = capture_screen()

        mock_pyautogui_screenshot.assert_called_once()
        self.assertEqual(img, self.mock_image)

    @patch("tools.screenshot_tool._QUARTZ_AVAILABLE", True)
    @patch("tools.screenshot_tool._capture_quartz")
    @patch("pathlib.Path.mkdir")
    @patch("tools.screenshot_tool.datetime")
    def test_capture_screen_and_save(self, mock_datetime, mock_mkdir, mock_capture_quartz):
        """Test capture_screen saves the image when a path is provided."""
        mock_capture_quartz.return_value = self.mock_image

        #Mock the strftime call to return a fixed timestamp
        mock_datetime.datetime.now.return_value.strftime.return_value = "20250617T153000"

        save_path = Path("/tmp/screenshot.png")
        capture_screen(save_to=save_path)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        expected_filename = Path("/tmp/screenshot_20250617T153000.png")
        self.mock_image.save.assert_called_once_with(expected_filename)

    @patch("tools.screenshot_tool._QUARTZ_AVAILABLE", True)
    @patch("tools.screenshot_tool._capture_quartz")
    def test_capture_screen_without_saving(self, mock_capture_quartz):
        """Test capture_screen does not save when no path is provided."""
        mock_capture_quartz.return_value = self.mock_image

        capture_screen()

        self.mock_image.save.assert_not_called()

if __name__ == "__main__":
    unittest.main()
