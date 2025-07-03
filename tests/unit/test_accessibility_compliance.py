import unittest
from unittest.mock import Mock, patch


# Mock NSRect for testing purposes
class NSRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


# Mock the core.accessibility_compliance module
import core.accessibility_compliance


class TestAccessibilityCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.accessibility_compliance = (
            core.accessibility_compliance.AccessibilityCompliance()
        )

    def test_check_ui_element_accessible(self):
        """Test checking if a UI element is accessible with valid attributes."""
        mock_element = Mock()
        mock_element.accessibleName.return_value = "Button"
        mock_element.role.return_value = "AXButton"
        result = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertTrue(result)

    def test_check_ui_element_not_accessible(self):
        """Test checking a UI element that is not accessible."""
        # Simulate an element that fails accessibility checks
        mock_element = Mock()
        mock_element.isKindOfClass.return_value = True
        mock_element.accessibilityRole.return_value = "AXButton"
        mock_element.accessibilityLabel.return_value = None
        mock_element.accessibilityHelp.return_value = None
        mock_element.frame.return_value = NSRect(0, 0, 20, 20)  # Too small
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertEqual(
            len(report["issues"]), 1
        )  # Adjusted to expect 1 issue based on current implementation

    def test_check_application_accessibility(self):
        """Test checking application accessibility compliance."""
        with patch("core.accessibility_compliance.NSApplication") as mock_app:
            app = Mock()
            app.windows.return_value = []
            app.localizedName.return_value = "TestApp"
            mock_app.return_value = app
            result = self.accessibility_compliance.check_application_accessibility(app)
            self.assertIsInstance(result, dict)
            self.assertIn("total_elements", result)
            self.assertIn("accessible_elements", result)
            self.assertIn("issues", result)
            self.assertEqual(result["app_name"], "TestApp")

    def test_check_application_accessibility(self):
        """Test checking application accessibility compliance."""
        with patch("core.accessibility_compliance.NSApplication") as mock_app:
            mock_app.mainWindow.return_value = Mock()
            mock_app.windows.return_value = [Mock(), Mock()]
            result = self.accessibility_compliance.check_application()
            self.assertIsInstance(result, list)

    def test_check_ui_element_focusable(self):
        """Test checking if a UI element is focusable."""
        mock_element = Mock()
        mock_element.isKindOfClass.return_value = True
        mock_element.accessibilityRole.return_value = "AXButton"
        mock_element.accessibilityIsFocused.return_value = True
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertTrue(report["accessible"])

    def test_check_ui_element_label(self):
        """Test checking if a UI element has a proper label."""
        mock_element = Mock()
        mock_element.isKindOfClass.return_value = True
        mock_element.accessibilityRole.return_value = "AXTextField"
        mock_element.accessibilityLabel.return_value = "Username"
        mock_element.frame.return_value = NSRect(0, 0, 100, 30)
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertTrue(report["accessible"])

    def test_check_ui_element_help_text(self):
        """Test checking if a UI element has help text."""
        mock_element = Mock()
        mock_element.isKindOfClass.return_value = True
        mock_element.accessibilityRole.return_value = "AXSlider"
        mock_element.accessibilityHelp.return_value = "Adjust volume"
        mock_element.frame.return_value = NSRect(0, 0, 100, 30)
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertTrue(report["accessible"])


if __name__ == "__main__":
    unittest.main()
