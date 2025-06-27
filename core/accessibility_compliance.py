from typing import Any, Dict, List

# Import specific macOS accessibility frameworks
from AppKit import NSAccessibilityElement, NSApplication


class AccessibilityCompliance:
    """Class to ensure macOS accessibility compliance for Atlas UI components"""

    def __init__(self):
        """Initialize accessibility compliance checker"""
        self.accessibility_issues: List[Dict[str, Any]] = []
        self.supported_roles = {
            "AXButton",
            "AXMenu",
            "AXMenuItem",
            "AXWindow",
            "AXTextField",
            "AXTextArea",
            "AXStaticText",
            "AXGroup",
            "AXRadioButton",
            "AXCheckBox",
            "AXPopUpButton",
            "AXTabGroup",
            "AXTable",
            "AXRow",
            "AXColumn",
            "AXCell",
            "AXSlider",
            "AXValueIndicator",
            "AXImage",
            "AXScrollArea",
            "AXScrollBar",
        }

    def check_ui_element(self, element: Any) -> Dict[str, Any]:
        """Check accessibility compliance for a UI element

        Args:
            element: UI element to check (expected to conform to NSAccessibilityProtocol)

        Returns:
            Dict[str, Any]: Report of accessibility status and issues if any
        """
        report = {
            "element": str(element),
            "accessible": False,
            "issues": [],
            "role": "Unknown",
            "description": "",
        }

        try:
            if not isinstance(element, NSAccessibilityElement):
                report["issues"].append(
                    "Element does not conform to accessibility protocol"
                )
                self.accessibility_issues.append(report)
                return report

            # Get accessibility role
            role = element.accessibilityRole()
            report["role"] = role if role else "Unknown"

            if role not in self.supported_roles:
                report["issues"].append(f"Unsupported accessibility role: {role}")

            # Check for role description
            role_description = element.accessibilityRoleDescription()
            if not role_description:
                report["issues"].append("Missing accessibility role description")

            # Check for label/help text
            label = element.accessibilityLabel()
            if not label:
                report["issues"].append("Missing accessibility label")

            # Check if element is enabled
            if not element.accessibilityEnabled():
                report["issues"].append("Accessibility is not enabled for this element")

            # Check for focusability if applicable
            if (
                role
                in {
                    "AXButton",
                    "AXTextField",
                    "AXTextArea",
                    "AXMenuItem",
                    "AXRadioButton",
                    "AXCheckBox",
                    "AXPopUpButton",
                    "AXSlider",
                }
                and not element.accessibilityFocused()
                and not hasattr(element, "accessibilityPerformPress")
                and not hasattr(element, "accessibilityPerformShowMenu")
            ):
                report["issues"].append("Element is not focusable")

            # Check for parent/child relationships
            children = element.accessibilityChildren()
            if children:
                for child in children:
                    child_report = self.check_ui_element(child)
                    if not child_report["accessible"]:
                        report["issues"].extend(
                            [
                                f"Child element issue: {issue}"
                                for issue in child_report["issues"]
                            ]
                        )

            # Check for minimum size (for touch targets)
            frame = element.accessibilityFrame()
            if (
                frame.size.width < 44
                or frame.size.height < 44
                and role in {"AXButton", "AXMenuItem", "AXRadioButton", "AXCheckBox"}
            ):
                report["issues"].append(
                    "Touch target is too small (should be at least 44x44 points)"
                )

            # If no issues found, mark as accessible
            report["accessible"] = len(report["issues"]) == 0
            report["description"] = (
                role_description if role_description else "No description"
            )

            if not report["accessible"]:
                self.accessibility_issues.append(report)

        except Exception as e:
            report["issues"].append(f"Error checking accessibility: {str(e)}")
            self.accessibility_issues.append(report)

        return report

    def check_application_accessibility(self, app: NSApplication) -> Dict[str, Any]:
        """Check accessibility compliance for the entire application

        Args:
            app: NSApplication instance to check

        Returns:
            Dict[str, Any]: Comprehensive accessibility report
        """
        self.accessibility_issues = []
        report = {
            "app_name": app.localizedName()
            if hasattr(app, "localizedName")
            else "Unknown",
            "accessible": False,
            "total_elements": 0,
            "accessible_elements": 0,
            "issues": [],
        }

        try:
            # Get main window or all windows
            windows = app.windows() if hasattr(app, "windows") else []
            report["total_windows"] = len(windows)

            for window in windows:
                window_report = self.check_ui_element(window)
                report["total_elements"] += 1
                if window_report["accessible"]:
                    report["accessible_elements"] += 1
                else:
                    report["issues"].extend(
                        [f"Window issue: {issue}" for issue in window_report["issues"]]
                    )

                # Check window-specific accessibility features
                if not window.isAccessibilityElement():
                    report["issues"].append(
                        "Window is not marked as accessibility element"
                    )

            # Check for VoiceOver cursor support
            if not app.isAccessibilityFocused():
                # This is a general check - not always an issue, depends on context
                report["issues"].append(
                    "Application does not have VoiceOver cursor focus"
                )

            # Finalize report
            report["accessible"] = (
                len(report["issues"]) == 0
                and report["accessible_elements"] == report["total_elements"]
            )
            report["issues"].extend(list(self.accessibility_issues))

        except Exception as e:
            report["issues"].append(
                f"Error checking application accessibility: {str(e)}"
            )

        return report

    def fix_accessibility_issue(self, element: Any, issue: Dict[str, Any]) -> bool:
        """Attempt to fix an accessibility issue for an element

        Args:
            element: UI element with accessibility issue
            issue: Dict describing the issue to fix

        Returns:
            bool: True if issue was fixed, False otherwise
        """
        try:
            if not isinstance(element, NSAccessibilityElement):
                return False

            issues = issue.get("issues", [])
            for problem in issues:
                if "Missing accessibility label" in problem:
                    element.setAccessibilityLabel("Untitled Element")
                    return True
                elif "Missing accessibility role description" in problem:
                    element.setAccessibilityRoleDescription(
                        f"{issue.get('role', 'Element')} description"
                    )
                    return True
                elif "Accessibility is not enabled" in problem:
                    element.setAccessibilityEnabled(True)
                    return True
                # Add more fixable issues as needed

            return False
        except Exception as e:
            print(f"Error fixing accessibility issue: {str(e)}")
            return False

    def get_accessibility_report(self) -> List[Dict[str, Any]]:
        """Get the current list of accessibility issues

        Returns:
            List[Dict[str, Any]]: List of accessibility issue reports
        """
        return self.accessibility_issues
