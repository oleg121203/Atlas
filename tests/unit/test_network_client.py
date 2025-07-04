"""
Tests for the NetworkClient class in core/network_client.py
"""

import unittest
from unittest.mock import MagicMock, patch

from core.network_client import NetworkClient


class TestNetworkClient(unittest.TestCase):
    """Test cases for the NetworkClient class."""

    def setUp(self):
        """Set up test fixtures."""
        # Patch the required functions and classes
        self.mock_configure_session = patch(
            "core.network_client.configure_secure_session"
        ).start()
        self.mock_make_secure_request = patch(
            "core.network_client.make_secure_request"
        ).start()
        self.mock_validate_ssl = patch(
            "core.network_client.validate_ssl_certificate"
        ).start()
        self.mock_logger = patch("core.network_client.logger").start()
        self.mock_requests = patch("core.network_client.requests").start()

        # Create a mock session
        self.mock_session = MagicMock()
        self.mock_configure_session.return_value = self.mock_session

        # Create a mock response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.text = "Test response"
        self.mock_make_secure_request.return_value = self.mock_response
        self.mock_validate_ssl.return_value = (True, "Valid certificate")

        # Create the client instance
        self.client = NetworkClient()

        # Set up the mock session to return our mock response
        self.mock_session.request.return_value = self.mock_response

        self.ssl_patcher = patch("core.network_client.validate_ssl_certificate")
        self.mock_validate_ssl = self.ssl_patcher.start()
        self.mock_validate_ssl.return_value = (True, "Valid certificate")

        # Mock make_secure_request
        self.secure_req_patcher = patch("core.network_client.make_secure_request")
        self.mock_make_secure_request = self.secure_req_patcher.start()
        self.mock_make_secure_request.return_value = self.mock_response

    def tearDown(self):
        """Clean up after each test method."""
        patch.stopall()  # Stop all active patches

    def test_init_creates_secure_session(self):
        """Test that __init__ creates a secure session."""
        # Reset the mock to clear any previous calls
        self.mock_configure_session.reset_mock()
        self.mock_logger.reset_mock()

        # Create a new instance to trigger __init__
        _ = NetworkClient()  # Store in _ to indicate we're intentionally not using it

        # Verify the session was configured and logged
        self.mock_configure_session.assert_called_once()
        self.mock_logger.info.assert_called_with(
            "Network client initialized with secure session"
        )

    def test_validate_url_success(self):
        """Test URL validation with valid URL."""
        test_url = "https://example.com"
        self.client.validate_url(test_url)
        self.mock_validate_ssl.assert_called_once_with(test_url, 10)

    def test_validate_url_with_custom_timeout(self):
        """Test URL validation with custom timeout."""
        test_url = "https://example.com"
        custom_timeout = 30
        self.client.validate_url(test_url, custom_timeout)
        self.mock_validate_ssl.assert_called_once_with(test_url, custom_timeout)

    def test_get_success(self):
        """Test successful GET request."""
        test_url = "https://example.com"
        response = self.client.get(test_url)

        # Verify make_secure_request was called with correct arguments
        self.mock_make_secure_request.assert_called_once()
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs.get("timeout"), 10)
        self.assertEqual(response, self.mock_response)

    def test_get_with_ssl_validation_failure(self):
        """Test GET request with SSL validation failure."""
        test_url = "https://example.com"
        self.mock_validate_ssl.return_value = (False, "Invalid certificate")

        response = self.client.get(test_url, validate_ssl=True)

        self.assertIsNone(response)
        self.mock_validate_ssl.assert_called_once_with(test_url, 10)
        self.mock_make_secure_request.assert_not_called()

    def test_get_with_ssl_validation_disabled(self):
        """Test GET request with SSL validation disabled."""
        test_url = "https://example.com"
        response = self.client.get(test_url, validate_ssl=False)

        self.mock_validate_ssl.assert_not_called()
        self.mock_make_secure_request.assert_called_once()
        self.assertEqual(response, self.mock_response)

    def test_post_success(self):
        """Test successful POST request."""
        test_url = "https://example.com"
        test_data = {"key": "value"}
        response = self.client.post(test_url, data=test_data)

        # Verify make_secure_request was called with correct arguments
        self.mock_make_secure_request.assert_called_once()
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs.get("data"), test_data)
        self.assertEqual(kwargs.get("timeout"), 10)
        self.assertEqual(response, self.mock_response)

    def test_request_success(self):
        """Test successful generic request."""
        test_url = "https://example.com"
        test_data = {"key": "value"}
        test_headers = {"Content-Type": "application/json"}

        response = self.client.request(
            "PUT", test_url, data=test_data, headers=test_headers, timeout=30
        )

        # Verify make_secure_request was called with correct arguments
        self.mock_make_secure_request.assert_called_once()
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "PUT")
        self.assertEqual(kwargs.get("data"), test_data)
        self.assertEqual(kwargs.get("headers"), test_headers)
        self.assertEqual(kwargs.get("timeout"), 30)
        self.assertEqual(response, self.mock_response)

    def test_request_with_ssl_error(self):
        """Test handling of SSL errors."""
        test_url = "https://example.com"
        # Configure the mock to raise an SSL error
        self.mock_validate_ssl.return_value = (
            False,
            "SSL certificate verification failed",
        )

        response = self.client.get(test_url)

        self.assertIsNone(response)
        # Verify the error was logged
        self.mock_logger.error.assert_called_with(
            "SSL validation failed for GET request to %s: %s",
            test_url,
            "SSL certificate verification failed",
        )

    def test_request_with_timeout(self):
        """Test handling of request timeouts."""
        test_url = "https://example.com"
        # Configure the mock to return None to simulate a timeout
        self.mock_make_secure_request.return_value = None
        # Make the request
        response = self.client.get(test_url)
        # Verify the response is None
        self.assertIsNone(response)
        # Verify make_secure_request was called with the correct arguments
        self.mock_make_secure_request.assert_called_once()
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)  # First positional argument is URL
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["timeout"], 10)

    def test_request_with_generic_exception(self):
        """Test handling of generic exceptions."""
        test_url = "https://example.com"
        # Configure the mock to return None to simulate a generic error
        self.mock_make_secure_request.return_value = None
        # Make the request
        response = self.client.get(test_url)
        # Verify the response is None
        self.assertIsNone(response)
        # Verify make_secure_request was called with the correct arguments
        self.mock_make_secure_request.assert_called_once()
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)  # First positional argument is URL
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["timeout"], 10)

    def test_close(self):
        """Test closing the network client."""
        self.client.close()
        self.mock_session.close.assert_called_once()

    def test_post_request(self):
        """Test making a POST request."""
        test_url = "https://example.com/api"
        test_data = {"key": "value"}
        test_headers = {"Content-Type": "application/json"}

        # Configure the mock to return a successful response
        self.mock_make_secure_request.return_value = self.mock_response

        # Make the POST request
        response = self.client.post(test_url, data=test_data, headers=test_headers)

        # Verify the response
        self.assertEqual(response, self.mock_response)
        # Verify the call was made with the correct arguments
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)  # First positional arg is URL
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["data"], test_data)
        self.assertEqual(kwargs["headers"], test_headers)
        self.assertEqual(kwargs["timeout"], 10)

    def test_validate_url(self):
        """Test URL validation."""
        # Test with a valid URL
        is_valid, message = self.client.validate_url("https://example.com")
        self.assertTrue(is_valid)
        # Check that validate_ssl_certificate was called with correct arguments
        args, kwargs = self.mock_validate_ssl.call_args
        self.assertEqual(args[0], "https://example.com")
        self.assertEqual(args[1], 10)  # Default timeout

        # Test with a different timeout
        self.mock_validate_ssl.reset_mock()
        self.client.validate_url("https://example.com", timeout=5)
        args, kwargs = self.mock_validate_ssl.call_args
        self.assertEqual(args[0], "https://example.com")
        self.assertEqual(args[1], 5)  # Custom timeout

    def test_request_with_custom_timeout(self):
        """Test making a request with a custom timeout."""
        test_url = "https://example.com"
        self.mock_make_secure_request.return_value = self.mock_response

        response = self.client.get(test_url, timeout=15)

        self.assertEqual(response, self.mock_response)
        # Verify the call was made with the correct arguments
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["timeout"], 15)

    def test_request_with_ssl_verification_disabled(self):
        """Test making a request with SSL verification disabled."""
        test_url = "https://example.com"
        self.mock_make_secure_request.return_value = self.mock_response

        response = self.client.get(test_url, validate_ssl=False)

        self.assertEqual(response, self.mock_response)
        # Should skip validation
        self.mock_validate_ssl.assert_not_called()
        # Verify the call was made with the correct arguments
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["timeout"], 10)

    def test_request_with_custom_headers(self):
        """Test making a request with custom headers."""
        test_url = "https://example.com"
        test_headers = {"Authorization": "Bearer token"}
        self.mock_make_secure_request.return_value = self.mock_response

        response = self.client.get(test_url, headers=test_headers)

        self.assertEqual(response, self.mock_response)
        # Verify the call was made with the correct arguments
        args, kwargs = self.mock_make_secure_request.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["headers"], test_headers)
        self.assertEqual(kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
