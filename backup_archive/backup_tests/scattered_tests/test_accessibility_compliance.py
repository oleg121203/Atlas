import unittest
from unittest.mock import MagicMock

from core.accessibility_compliance import AccessibilityCompliance


class TestAccessibilityCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.accessibility = AccessibilityCompliance()
        self.mock_element = MagicMock()
        self.mock_app = MagicMock()

    def test_initialization(self):
        """Test initialization of accessibility compliance checker"""
        self.assertTrue(len(self.accessibility.supported_roles) > 0)
        self.assertEqual(len(self.accessibility.accessibility_issues), 0)

    def test_check_ui_element_accessible(self):
        """Test checking an accessible UI element"""
        self.mock_element.accessibilityRole.return_value = "AXButton"
        self.mock_element.accessibilityRoleDescription.return_value = "Button"
        self.mock_element.accessibilityLabel.return_value = "Click Me"
        self.mock_element.accessibilityEnabled.return_value = True
        self.mock_element.accessibilityFocused.return_value = False
        self.mock_element.accessibilityFrame.return_value = type(
            "Frame", (), {"size": type("Size", (), {"width": 50, "height": 50})}
        )()
        self.mock_element.accessibilityChildren.return_value = []
        self.mock_element.accessibilityPerformPress = MagicMock()

        report = self.accessibility.check_ui_element(self.mock_element)
        self.assertTrue(report["accessible"])
        self.assertEqual(len(report["issues"]), 0)
        self.assertEqual(report["role"], "AXButton")

    def test_check_ui_element_inaccessible(self):
        """Test checking an inaccessible UI element"""
        self.mock_element.accessibilityRole.return_value = "AXUnknown"
        self.mock_element.accessibilityRoleDescription.return_value = ""
        self.mock_element.accessibilityLabel.return_value = ""
        self.mock_element.accessibilityEnabled.return_value = False
        self.mock_element.accessibilityFocused.return_value = False
        self.mock_element.accessibilityFrame.return_value = type(
            "Frame", (), {"size": type("Size", (), {"width": 20, "height": 20})}
        )()
        self.mock_element.accessibilityChildren.return_value = []

        report = self.accessibility.check_ui_element(self.mock_element)
        self.assertFalse(report["accessible"])
        self.assertTrue(len(report["issues"]) > 0)
        self.assertEqual(report["role"], "AXUnknown")

    def test_check_application_accessibility(self):
        """Test checking application-wide accessibility"""
        self.mock_app.localizedName.return_value = "Test App"
        mock_window = MagicMock()
        mock_window.isAccessibilityElement.return_value = True
        mock_window.accessibilityRole.return_value = "AXWindow"
        mock_window.accessibilityRoleDescription.return_value = "Window"
        mock_window.accessibilityLabel.return_value = "Main Window"
        mock_window.accessibilityEnabled.return_value = True
        mock_window.accessibilityFrame.return_value = type(
            "Frame", (), {"size": type("Size", (), {"width": 800, "height": 600})}
        )()
        mock_window.accessibilityChildren.return_value = []
        self.mock_app.windows.return_value = [mock_window]
        self.mock_app.isAccessibilityFocused.return_value = False

        report = self.accessibility.check_application_accessibility(self.mock_app)
        self.assertEqual(report["app_name"], "Test App")
        self.assertEqual(report["total_elements"], 1)
        self.assertTrue(report["accessible_elements"] > 0)
        self.assertTrue(len(report["issues"]) > 0)  # Due to VoiceOver focus issue

    def test_fix_accessibility_issue_label(self):
        """Test fixing a missing accessibility label"""
        issue = {"issues": ["Missing accessibility label"], "role": "AXButton"}
        self.mock_element.setAccessibilityLabel = MagicMock()

        result = self.accessibility.fix_accessibility_issue(self.mock_element, issue)
        self.assertTrue(result)
        self.mock_element.setAccessibilityLabel.assert_called_once_with(
            "Untitled Element"
        )

    def test_fix_accessibility_issue_enabled(self):
        """Test fixing accessibility not enabled"""
        issue = {
            "issues": ["Accessibility is not enabled for this element"],
            "role": "AXButton",
        }
        self.mock_element.setAccessibilityEnabled = MagicMock()

        result = self.accessibility.fix_accessibility_issue(self.mock_element, issue)
        self.assertTrue(result)
        self.mock_element.setAccessibilityEnabled.assert_called_once_with(True)

    def test_get_accessibility_report(self):
        """Test getting accessibility report"""
        self.mock_element.accessibilityRole.return_value = "AXUnknown"
        self.mock_element.accessibilityRoleDescription.return_value = ""
        self.mock_element.accessibilityLabel.return_value = ""
        self.mock_element.accessibilityEnabled.return_value = False
        self.mock_element.accessibilityFrame.return_value = type(
            "Frame", (), {"size": type("Size", (), {"width": 20, "height": 20})}
        )()

        self.accessibility.check_ui_element(self.mock_element)
        report = self.accessibility.get_accessibility_report()
        self.assertEqual(len(report), 1)
        self.assertFalse(report[0]["accessible"])
        self.assertTrue(len(report[0]["issues"]) > 0)


if __name__ == "__main__":
    unittest.main()
