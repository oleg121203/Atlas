import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from tools.image_recognition_tool import find_template_in_image, find_object_in_image

class TestImageRecognitionTool(unittest.TestCase):
    """Unit tests for the image recognition tool."""

    @patch('tools.image_recognition_tool.cv2.imread')
    @patch('tools.image_recognition_tool.cv2.matchTemplate')
    @patch('tools.image_recognition_tool.cv2.minMaxLoc')
    def test_find_template_success(self, mock_minMaxLoc, mock_matchTemplate, mock_imread):
        """Test find_template_in_image finds a match successfully."""
        mock_imread.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_minMaxLoc.return_value = (0, 0.9, (0, 0), (50, 50)) #min_val, max_val, min_loc, max_loc
        
        result = find_template_in_image('template.png', 'image.png', threshold=0.8)
        
        self.assertEqual(result, (50, 50))

    @patch('tools.image_recognition_tool.cv2.imread')
    @patch('tools.image_recognition_tool.cv2.matchTemplate')
    @patch('tools.image_recognition_tool.cv2.minMaxLoc')
    def test_find_template_no_match(self, mock_minMaxLoc, mock_matchTemplate, mock_imread):
        """Test find_template_in_image returns None when no match is found."""
        mock_imread.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_minMaxLoc.return_value = (0, 0.7, (0, 0), (50, 50))
        
        result = find_template_in_image('template.png', 'image.png', threshold=0.8)
        
        self.assertIsNone(result)

    @patch('tools.image_recognition_tool.cv2.imread', return_value=None)
    def test_find_template_load_error(self, mock_imread):
        """Test find_template_in_image handles image loading failure."""
        result = find_template_in_image('template.png', 'image.png')
        self.assertIsNone(result)

    @patch('tools.image_recognition_tool.cv2.imread')
    @patch('tools.image_recognition_tool.cv2.cvtColor')
    @patch('tools.image_recognition_tool.cv2.CascadeClassifier')
    def test_find_object_success(self, mock_CascadeClassifier, mock_cvtColor, mock_imread):
        """Test find_object_in_image detects objects successfully."""
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cascade_instance = MagicMock()
        mock_cascade_instance.empty.return_value = False
        mock_cascade_instance.detectMultiScale.return_value = np.array([[10, 20, 30, 40]])
        mock_CascadeClassifier.return_value = mock_cascade_instance
        
        result = find_object_in_image('image.png', 'cascade.xml')
        
        self.assertEqual(result, [[10, 20, 30, 40]])

    @patch('tools.image_recognition_tool.cv2.imread', return_value=None)
    def test_find_object_image_load_error(self, mock_imread):
        """Test find_object_in_image handles image loading failure."""
        result = find_object_in_image('image.png', 'cascade.xml')
        self.assertEqual(result, [])

    @patch('tools.image_recognition_tool.cv2.imread')
    @patch('tools.image_recognition_tool.cv2.CascadeClassifier')
    def test_find_object_cascade_load_error(self, mock_CascadeClassifier, mock_imread):
        """Test find_object_in_image handles cascade loading failure."""
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cascade_instance = MagicMock()
        mock_cascade_instance.empty.return_value = True
        mock_CascadeClassifier.return_value = mock_cascade_instance
        
        result = find_object_in_image('image.png', 'cascade.xml')
        
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
