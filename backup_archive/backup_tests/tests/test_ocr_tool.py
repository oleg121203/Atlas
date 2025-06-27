import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from tools.ocr_tool import ocr_file, ocr_image


class TestOcrTool(unittest.TestCase):
    """Unit tests for the OCR tool."""

    def setUp(self):
        """Create a dummy image for testing."""
        self.mock_image = Image.new("RGB", (100, 50), color="red")

    @patch("tools.ocr_tool._VISION_AVAILABLE", True)
    @patch("tools.ocr_tool._vision_ocr")
    def test_ocr_image_with_vision_success(self, mock_vision_ocr):
        """Test ocr_image uses Vision framework when available."""
        expected_text = "Vision OCR Text"
        mock_vision_ocr.return_value = expected_text

        result = ocr_image(self.mock_image)

        mock_vision_ocr.assert_called_once_with(self.mock_image)
        self.assertEqual(result, expected_text)

    @patch("tools.ocr_tool._VISION_AVAILABLE", True)
    @patch("tools.ocr_tool._vision_ocr", side_effect=Exception("Vision failed"))
    @patch("tools.ocr_tool.pytesseract.image_to_string")
    def test_ocr_image_with_vision_fallback(self, mock_pytesseract, mock_vision_ocr):
        """Test ocr_image falls back to pytesseract when Vision fails."""
        expected_text = "Pytesseract Fallback Text"
        mock_pytesseract.return_value = expected_text

        result = ocr_image(self.mock_image)

        mock_vision_ocr.assert_called_once_with(self.mock_image)
        mock_pytesseract.assert_called_once_with(self.mock_image)
        self.assertEqual(result, expected_text)

    @patch("tools.ocr_tool._VISION_AVAILABLE", False)
    @patch("tools.ocr_tool.pytesseract.image_to_string")
    def test_ocr_image_without_vision(self, mock_pytesseract):
        """Test ocr_image uses pytesseract when Vision is not available."""
        expected_text = "Pytesseract Only Text"
        mock_pytesseract.return_value = expected_text

        result = ocr_image(self.mock_image)

        mock_pytesseract.assert_called_once_with(self.mock_image)
        self.assertEqual(result, expected_text)

    @patch("tools.ocr_tool.Image.open")
    @patch("tools.ocr_tool.ocr_image")
    def test_ocr_file_without_lang(self, mock_ocr_image, mock_image_open):
        """Test ocr_file calls ocr_image when no language is specified."""
        mock_image_open.return_value = self.mock_image
        expected_text = "File OCR Text"
        mock_ocr_image.return_value = expected_text

        result = ocr_file("dummy_path.png")

        mock_image_open.assert_called_once_with(Path("dummy_path.png"))
        mock_ocr_image.assert_called_once_with(self.mock_image)
        self.assertEqual(result, expected_text)

    @patch("tools.ocr_tool.Image.open")
    @patch("tools.ocr_tool.pytesseract.image_to_string")
    def test_ocr_file_with_lang(self, mock_pytesseract, mock_image_open):
        """Test ocr_file calls pytesseract directly when language is specified."""
        mock_image_open.return_value = self.mock_image
        expected_text = "File OCR Text with Lang"
        mock_pytesseract.return_value = expected_text

        result = ocr_file("dummy_path.png", lang="eng")

        mock_image_open.assert_called_once_with(Path("dummy_path.png"))
        mock_pytesseract.assert_called_once_with(self.mock_image, lang="eng")
        self.assertEqual(result, expected_text)


if __name__ == "__main__":
    unittest.main()
