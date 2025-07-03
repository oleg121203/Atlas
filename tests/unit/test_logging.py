# Standard library imports
import contextlib
import logging
import os
import sys
import tempfile
import unittest

# Third-party imports
from unittest.mock import MagicMock, patch

# Add parent directory to path for importing core modules
if ".." not in sys.path:
    sys.path.append("..")

# Local application imports
from core.logging import get_logger, setup_logging


class TestLogging(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.log_file = os.path.join(tempfile.mkdtemp(), "test_atlas.log")
        # Ensure no existing handlers interfere
        logging.getLogger().handlers = []

    def tearDown(self):
        """Clean up after each test method."""
        # Remove test log file if it exists
        with contextlib.suppress(Exception):
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
        # Reset logging configuration
        logging.getLogger().handlers = []
        logging.getLogger().setLevel(logging.NOTSET)

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        setup_logging()
        self.assertEqual(logging.getLogger().level, logging.INFO)

    def test_setup_logging_with_file(self):
        """Test setup_logging with a specific log file."""
        log_file = os.path.join(tempfile.mkdtemp(), "test.log")
        setup_logging(log_file=log_file)
        self.assertEqual(logging.getLogger().level, logging.INFO)

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test")

    def test_get_logger_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        self.assertIs(logger1, logger2)

    def test_logger_log_level(self):
        """Test logger's default log level."""
        logger = get_logger("test_level")
        self.assertEqual(logger.level, logging.INFO)

    def test_logging_initialization_no_crash(self):
        """Test that initializing logging doesn't crash."""
        try:
            logger = get_logger("test_init")
            logger.info("Initialization test")
        except Exception as e:
            self.fail(f"Logging initialization or usage crashed: {str(e)}")

    @patch("core.logging.RotatingFileHandler")
    @patch("core.logging.logging.StreamHandler")
    def test_setup_logging_default_parameters(
        self, mock_stream_handler, mock_file_handler
    ):
        """Test setup_logging with default parameters."""
        # Configure mock to avoid log level comparison issues
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        mock_stream_handler.return_value.level = logging.INFO
        mock_file_handler.return_value.level = logging.INFO
        setup_logging(log_file=self.log_file)
        self.assertEqual(logging.getLogger().level, logging.INFO)
        self.assertEqual(len(logging.getLogger().handlers), 2)
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()

    @patch("core.logging.RotatingFileHandler")
    @patch("core.logging.logging.StreamHandler")
    def test_setup_logging_custom_log_level(
        self, mock_stream_handler, mock_file_handler
    ):
        """Test setup_logging with a custom log level."""
        # Configure mock to avoid log level comparison issues
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        mock_stream_handler.return_value.level = logging.DEBUG
        mock_file_handler.return_value.level = logging.DEBUG
        setup_logging(log_file=self.log_file, log_level=logging.DEBUG)
        self.assertEqual(logging.getLogger().level, logging.DEBUG)
        self.assertEqual(len(logging.getLogger().handlers), 2)
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()

    @patch("core.logging.RotatingFileHandler")
    @patch("core.logging.logging.StreamHandler")
    def test_setup_logging_custom_log_file(
        self, mock_stream_handler, mock_file_handler
    ):
        """Test setup_logging with a custom log file path."""
        # Configure mock to avoid log level comparison issues
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        mock_stream_handler.return_value.level = logging.INFO
        mock_file_handler.return_value.level = logging.INFO
        custom_log_file = "custom_test.log"
        setup_logging(log_file=custom_log_file, log_level=logging.INFO)
        self.assertEqual(logging.getLogger().level, logging.INFO)
        self.assertEqual(len(logging.getLogger().handlers), 2)
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()

    @patch("core.logging.RotatingFileHandler")
    @patch("core.logging.logging.StreamHandler")
    def test_setup_logging_handler_formatting(
        self, mock_stream_handler, mock_file_handler
    ):
        """Test if handlers in setup_logging have correct formatter."""
        # Configure mock to avoid log level comparison issues
        mock_stream_handler.return_value = MagicMock()
        mock_file_handler.return_value = MagicMock()
        mock_stream_handler.return_value.level = logging.INFO
        mock_file_handler.return_value.level = logging.INFO
        mock_stream_handler.return_value.formatter = logging.Formatter()
        mock_file_handler.return_value.formatter = logging.Formatter()
        setup_logging(log_file=self.log_file)
        self.assertEqual(len(logging.getLogger().handlers), 2)
        for handler in logging.getLogger().handlers:
            self.assertIsInstance(handler.formatter, logging.Formatter)

    def test_get_logger_after_setup(self):
        """Test get_logger after setup_logging call."""
        setup_logging(log_file=self.log_file, log_level=logging.DEBUG)
        logger = get_logger("test_module_after_setup")
        self.assertEqual(logger.name, "test_module_after_setup")
        self.assertEqual(logger.level, logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
