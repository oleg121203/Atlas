import unittest
from unittest.mock import Mock, patch

import core.accessibility_compliance


# Mock NSRect for testing purposes
class NSRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = (
            self  # Mocking size attribute to return self for width and height access
        )


# Mock NSAccessibilityElement class for isinstance checks
class MockNSAccessibilityElement:
    def __init__(self):
        self.accessibilityRole = Mock(return_value="AXButton")
        self.accessibilityRoleDescription = Mock(return_value="Button Description")
        self.accessibilityLabel = Mock(return_value="Button")
        self.accessibilityEnabled = Mock(return_value=True)
        self.accessibilityFocused = Mock(return_value=True)
        self.accessibilityFrame = Mock(return_value=NSRect(10, 10, 50, 50))
        self.accessibilityChildren = Mock(return_value=[])
        self.accessibilityPerformPress = Mock()
        self.accessibilityPerformShowMenu = Mock()
        self.isAccessibilityElement = Mock(return_value=True)
        # Initialize attributes to fix lint errors
        self.setAccessibilityLabel = Mock(side_effect=self._set_label)
        self.setAccessibilityEnabled = Mock(side_effect=self._set_enabled)
        self.setAccessibilityRoleDescription = Mock(side_effect=self._set_description)

    def _set_label(self, value):
        self.accessibilityLabel.return_value = value

    def _set_enabled(self, value):
        self.accessibilityEnabled.return_value = value

    def _set_description(self, value):
        self.accessibilityRoleDescription.return_value = value


class TestAccessibilityCompliance(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.accessibility_compliance = (
            core.accessibility_compliance.AccessibilityCompliance()
        )
        # Patch isinstance to recognize MockNSAccessibilityElement as NSAccessibilityElement
        self.isinstance_patcher = patch(
            "core.accessibility_compliance.isinstance",
            side_effect=lambda obj, cls: (
                True
                if isinstance(obj, MockNSAccessibilityElement)
                and cls == core.accessibility_compliance.NSAccessibilityElement
                else isinstance(obj, cls)
            ),
        )
        self.isinstance_patcher.start()

    def tearDown(self):
        """Clean up after each test method."""
        self.isinstance_patcher.stop()

    def test_check_ui_element_accessible(self):
        """Test checking if a UI element is accessible with valid attributes."""
        mock_element = MockNSAccessibilityElement()
        result = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertTrue(result["accessible"])
        self.assertEqual(result["role"], "AXButton")
        self.assertEqual(result["description"], "Button Description")
        self.assertEqual(result["issues"], [])

    def test_check_ui_element_not_accessible(self):
        """Test checking a UI element that is not accessible."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityRoleDescription.return_value = None
        mock_element.accessibilityLabel.return_value = None
        mock_element.accessibilityEnabled.return_value = False
        mock_element.accessibilityFocused.return_value = False
        mock_element.accessibilityFrame.return_value = NSRect(0, 0, 20, 20)
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertGreaterEqual(len(report["issues"]), 4)
        self.assertIn("Missing accessibility role description", report["issues"])
        self.assertIn("Missing accessibility label", report["issues"])
        self.assertIn("Accessibility is not enabled for this element", report["issues"])
        self.assertIn(
            "Touch target is too small (should be at least 44x44 points)",
            report["issues"],
        )

    def test_check_ui_element_unsupported_role(self):
        """Test checking a UI element with an unsupported role."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityRole.return_value = "UnsupportedRole"
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertIn(
            "Unsupported accessibility role: UnsupportedRole", report["issues"]
        )

    def test_check_ui_element_with_children(self):
        """Test checking a UI element with child elements."""
        mock_child = MockNSAccessibilityElement()
        mock_child.accessibilityRoleDescription.return_value = None
        mock_child.accessibilityLabel.return_value = None
        mock_child.accessibilityEnabled.return_value = False
        mock_child.accessibilityFrame.return_value = NSRect(0, 0, 20, 20)
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityRole.return_value = "AXGroup"
        mock_element.accessibilityChildren.return_value = [mock_child]
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertIn(
            "Child element issue: Missing accessibility role description",
            report["issues"],
        )
        self.assertIn(
            "Child element issue: Missing accessibility label", report["issues"]
        )
        self.assertIn(
            "Child element issue: Accessibility is not enabled for this element",
            report["issues"],
        )
        self.assertIn(
            "Child element issue: Touch target is too small "
            "(should be at least 44x44 points)",
            report["issues"],
        )

    def test_check_ui_element_small_touch_target(self):
        """Test checking a UI element with a touch target smaller than 44x44."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityFrame.return_value = NSRect(10, 10, 20, 20)
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertIn(
            "Touch target is too small (should be at least 44x44 points)",
            report["issues"],
        )

    def test_check_ui_element_not_focusable(self):
        """Test checking a UI element that should be focusable but isn't."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityFocused.return_value = False
        delattr(mock_element, "accessibilityPerformPress")
        delattr(mock_element, "accessibilityPerformShowMenu")
        report = self.accessibility_compliance.check_ui_element(mock_element)
        self.assertFalse(report["accessible"])
        self.assertIn("Element is not focusable", report["issues"])

    def test_check_application_accessibility_compliance(self):
        """Test checking application accessibility compliance."""
        if not hasattr(
            self.accessibility_compliance, "check_application_accessibility_compliance"
        ):
            self.skipTest(
                "check_application_accessibility_compliance method not implemented"
            )
        with patch("core.accessibility_compliance.NSApplication") as mock_app:
            mock_window = MockNSAccessibilityElement()
            mock_window.accessibilityRole.return_value = "AXWindow"
            mock_window.accessibilityFrame.return_value = NSRect(10, 10, 500, 400)
            mock_app.mainWindow.return_value = mock_window
            mock_app.windows.return_value = [mock_window]
            mock_app.localizedName.return_value = "Atlas App"
            mock_app.isAccessibilityFocused.return_value = True
            report = self.accessibility_compliance.check_application_accessibility(
                mock_app
            )
            self.assertFalse(report["accessible"])
            self.assertEqual(report["app_name"], "Atlas App")
            self.assertEqual(report["total_elements"], 1)
            self.assertEqual(report["accessible_elements"], 1)

    def test_check_application_accessibility_non_accessible_window(self):
        """Test checking application with non-accessible window."""
        with patch("core.accessibility_compliance.NSApplication") as mock_app:
            mock_window = Mock()
            mock_window.isAccessibilityElement.return_value = False
            mock_window.accessibilityRole.return_value = "AXWindow"
            mock_window.accessibilityLabel.return_value = None
            mock_window.accessibilityEnabled.return_value = False
            mock_window.accessibilityFrame.return_value = NSRect(0, 0, 100, 100)
            mock_app.mainWindow.return_value = mock_window
            mock_app.windows.return_value = [mock_window]
            mock_app.localizedName.return_value = "Atlas App"
            mock_app.isAccessibilityFocused.return_value = False
            report = self.accessibility_compliance.check_application_accessibility(
                mock_app
            )
            self.assertFalse(report["accessible"])
            self.assertGreaterEqual(len(report["issues"]), 2)
            self.assertIn(
                "Window is not marked as accessibility element", report["issues"]
            )
            self.assertIn(
                "Application does not have VoiceOver cursor focus", report["issues"]
            )

    def test_fix_accessibility_issue_label(self):
        """Test fixing a missing accessibility label issue."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityLabel.return_value = None
        issue = {
            "element": str(mock_element),
            "issues": ["Missing accessibility label"],
            "accessible": False,
        }
        result = self.accessibility_compliance.fix_accessibility_issue(
            mock_element, issue
        )
        self.assertTrue(result)
        self.assertEqual(mock_element.accessibilityLabel(), "Untitled Element")

    def test_fix_accessibility_issue_enabled(self):
        """Test fixing an accessibility not enabled issue."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityEnabled.return_value = False
        issue = {
            "element": str(mock_element),
            "issues": ["Accessibility is not enabled for this element"],
            "accessible": False,
        }
        result = self.accessibility_compliance.fix_accessibility_issue(
            mock_element, issue
        )
        self.assertTrue(result)
        self.assertTrue(mock_element.accessibilityEnabled())

    def test_fix_accessibility_issue_role_description(self):
        """Test fixing a missing accessibility role description issue."""
        mock_element = MockNSAccessibilityElement()
        mock_element.accessibilityRoleDescription.return_value = None
        mock_element.accessibilityRole.return_value = "AXButton"
        issue = {
            "element": str(mock_element),
            "issues": ["Missing accessibility role description"],
            "accessible": False,
        }
        result = self.accessibility_compliance.fix_accessibility_issue(
            mock_element, issue
        )
        self.assertTrue(result)
        self.assertEqual(
            mock_element.accessibilityRoleDescription(), "Element description"
        )

    def test_get_accessibility_report(self):
        """Test retrieving the current list of accessibility issues."""
        issue1 = {"element": "Element1", "issues": ["Issue1"], "accessible": False}
        issue2 = {
            "element": "Element2",
            "issues": ["Issue2", "Issue3"],
            "accessible": False,
        }
        self.accessibility_compliance.accessibility_issues = [issue1, issue2]
        report = self.accessibility_compliance.get_accessibility_report()
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0], issue1)
        self.assertEqual(report[1], issue2)

    def test_check_application_accessibility_multiple_windows(self):
        """Test checking application accessibility with multiple windows."""
        with patch("core.accessibility_compliance.NSApplication") as mock_app:
            mock_window1 = MockNSAccessibilityElement()
            mock_window1.accessibilityRole.return_value = "AXWindow"
            mock_window1.accessibilityFrame.return_value = NSRect(10, 10, 500, 400)
            mock_window2 = MockNSAccessibilityElement()
            mock_window2.accessibilityRole.return_value = "AXWindow"
            mock_window2.accessibilityFrame.return_value = NSRect(100, 100, 500, 400)
            mock_window2.accessibilityLabel.return_value = None
            mock_app.mainWindow.return_value = mock_window1
            mock_app.windows.return_value = [mock_window1, mock_window2]
            mock_app.localizedName.return_value = "Atlas App"
            mock_app.isAccessibilityFocused.return_value = True
            report = self.accessibility_compliance.check_application_accessibility(
                mock_app
            )
            self.assertFalse(report["accessible"])
            self.assertEqual(report["app_name"], "Atlas App")
            self.assertEqual(report["total_elements"], 2)
            self.assertEqual(report["accessible_elements"], 1)
            self.assertIn("Window issue: Missing accessibility label", report["issues"])


if __name__ == "__main__":
    unittest.main()
