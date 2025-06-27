"""
Test cases for Atlas Application core.
"""

import unittest
from unittest.mock import patch

from core.atlas_application import AtlasApplication


class TestAtlasApplication(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app_name = "test_atlas"

    @patch("PySide6.QtWidgets.QApplication")
    @patch("core.atlas_application.setup_logging")
    @patch("core.atlas_application.check_environment_security")
    @patch("core.atlas_application.initialize_security")
    @patch("core.atlas_application.initialize_alerting")
    @patch("core.atlas_application.start_monitoring")
    def test_application_initialization(
        self,
        mock_monitoring,
        mock_alerting,
        mock_security_init,
        mock_security_check,
        mock_logging,
        mock_qapp,
    ):
        """Test if the application initializes correctly."""
        # Setup mocks
        mock_security_check.return_value = True
        mock_security_init.return_value = True
        mock_alerting.return_value = True

        # Initialize application
        app = AtlasApplication(self.app_name)

        # Verify initialization
        self.assertIsNotNone(app)
        mock_logging.assert_called_once()
        mock_security_check.assert_called_once()
        mock_security_init.assert_called_once()
        mock_alerting.assert_called_once()
        mock_monitoring.assert_called_once()


if __name__ == "__main__":
    unittest.main()
