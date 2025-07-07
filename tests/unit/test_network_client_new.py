"""
Tests for the NetworkClient class in core/network_client.py
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.exceptions import RequestException, SSLError, Timeout

from core.network_client import NetworkClient

# Test data
TEST_URL = "https://example.com"
TEST_SSL_ERROR = "SSL certificate verification failed"
TEST_TIMEOUT = 10


# Fixtures
@pytest.fixture
def mock_secure_request():
    """Fixture to mock make_secure_request function."""
    with patch("core.network_client.make_secure_request") as mock_request:
        # Create a mock response with status code 200 by default
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        yield mock_request


@pytest.fixture
def network_client():
    """Fixture to create a NetworkClient instance for testing."""
    with (
        patch("core.network_client.configure_secure_session") as mock_session,
        patch("core.network_client.validate_ssl_certificate") as mock_validate_ssl,
        patch("core.network_client.make_secure_request") as mock_secure_request,
    ):
        # Setup mock session
        mock_session.return_value = MagicMock(spec=requests.Session)
        mock_session.return_value.request = MagicMock(
            return_value=MagicMock(status_code=200)
        )
        # Setup mock SSL validation
        mock_validate_ssl.return_value = (True, "Valid certificate")
        # Setup mock secure request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_secure_request.return_value = mock_response
        # Create client
        client = NetworkClient()
        yield client, mock_secure_request, mock_validate_ssl


# Test cases
class TestNetworkClientInit:
    """Tests for NetworkClient initialization."""

    def test_init_creates_secure_session(self):
        """Test that __init__ creates a secure session."""
        with patch("core.network_client.configure_secure_session") as mock_session:
            mock_session.return_value = MagicMock(spec=requests.Session)
            client = NetworkClient()
            mock_session.assert_called_once()
            assert hasattr(client, "session")
            assert isinstance(client.session, requests.Session)


class TestNetworkClientGet:
    """Tests for the get method."""

    def test_get_success(self, network_client):
        """Test successful GET request."""
        client, mock_secure_request, _ = network_client

        # Execute
        response = client.get(TEST_URL, timeout=TEST_TIMEOUT)

        # Assert
        # Check that make_secure_request was called with the expected arguments
        mock_secure_request.assert_called_once()
        # Check positional arguments
        assert mock_secure_request.call_args[0] == (TEST_URL,)
        # Check keyword arguments
        kwargs = mock_secure_request.call_args[1]
        assert kwargs.get("method") == "GET"
        assert kwargs.get("timeout") == TEST_TIMEOUT
        # validate_ssl is not passed by default, so we don't check for it
        assert response.status_code == 200

    def test_get_ssl_validation_failure(self, network_client):
        """Test GET with SSL validation failure."""
        client, mock_secure_request, mock_validate_ssl = network_client

        # Setup mock to fail SSL validation
        mock_validate_ssl.return_value = (False, TEST_SSL_ERROR)

        # Execute
        response = client.get(TEST_URL, timeout=TEST_TIMEOUT)

        # Assert
        mock_validate_ssl.assert_called_once_with(TEST_URL, TEST_TIMEOUT)
        assert response is None

    def test_get_request_exception(self, network_client):
        """Test GET with request exception."""
        client, mock_secure_request, _ = network_client

        # Make the mock raise RequestException directly
        mock_secure_request.side_effect = RequestException("Request failed")

        # Execute and assert that RequestException is raised
        with pytest.raises(RequestException):
            client.get(TEST_URL, timeout=TEST_TIMEOUT)


class TestNetworkClientPost:
    """Tests for the post method."""

    def test_post_success(self, network_client):
        """Test successful POST request."""
        client, mock_secure_request, _ = network_client
        test_data = {"key": "value"}

        # Execute
        response = client.post(TEST_URL, json=test_data, timeout=TEST_TIMEOUT)

        # Assert
        # Check that make_secure_request was called with the expected arguments
        mock_secure_request.assert_called_once()
        # Check positional arguments
        assert mock_secure_request.call_args[0] == (TEST_URL,)
        # Check keyword arguments
        kwargs = mock_secure_request.call_args[1]
        assert kwargs.get("method") == "POST"
        assert kwargs.get("json") == test_data
        assert kwargs.get("timeout") == TEST_TIMEOUT
        # validate_ssl is not passed by default, so we don't check for it
        assert response.status_code == 200

    def test_post_with_data(self, network_client):
        """Test POST with form data."""
        client, mock_secure_request, _ = network_client
        form_data = {"key": "value"}

        # Execute
        response = client.post(TEST_URL, data=form_data, timeout=TEST_TIMEOUT)

        # Assert
        # Check that make_secure_request was called with the expected arguments
        mock_secure_request.assert_called_once()
        # Check positional arguments
        assert mock_secure_request.call_args[0] == (TEST_URL,)
        # Check keyword arguments
        kwargs = mock_secure_request.call_args[1]
        assert kwargs.get("method") == "POST"
        assert kwargs.get("data") == form_data
        assert kwargs.get("timeout") == TEST_TIMEOUT
        # validate_ssl is not passed by default, so we don't check for it
        assert response.status_code == 200


class TestNetworkClientRequest:
    """Tests for the generic request method."""

    def test_request_success(self, network_client):
        """Test successful request with custom method."""
        client, mock_secure_request, _ = network_client

        # Execute
        response = client.request("PUT", TEST_URL, timeout=TEST_TIMEOUT)

        # Assert
        # Check that make_secure_request was called with the expected arguments
        mock_secure_request.assert_called_once()
        # Check positional arguments
        assert mock_secure_request.call_args[0] == (TEST_URL,)
        # Check keyword arguments
        kwargs = mock_secure_request.call_args[1]
        assert kwargs.get("method") == "PUT"
        assert kwargs.get("timeout") == TEST_TIMEOUT
        # validate_ssl is not passed by default, so we don't check for it
        assert response.status_code == 200

    def test_request_ssl_error(self, network_client):
        """Test request with SSL error."""
        client, mock_secure_request, _ = network_client
        mock_secure_request.side_effect = SSLError("SSL error")

        # Execute / Assert
        with pytest.raises(SSLError):
            client.request("GET", TEST_URL, timeout=TEST_TIMEOUT, validate_ssl=False)

    def test_request_timeout(self, network_client):
        """Test request timeout."""
        client, mock_secure_request, _ = network_client

        # Make the mock raise Timeout directly
        mock_secure_request.side_effect = Timeout("Request timed out")

        # Execute and assert that Timeout is raised
        with pytest.raises(Timeout):
            client.request("GET", TEST_URL, timeout=1)


class TestNetworkClientClose:
    """Tests for the close method."""

    def test_close(self, network_client):
        """Test that close calls session.close()."""
        client, _, _ = network_client

        # Execute
        client.close()

        # Assert
        client.session.close.assert_called_once()


class TestNetworkClientValidateURL:
    """Tests for URL validation."""

    def test_validate_url_success(self, network_client):
        """Test successful URL validation."""
        client, _, mock_validate_ssl = network_client
        mock_validate_ssl.return_value = (True, "Valid certificate")

        # Execute
        is_valid, message = client.validate_url(TEST_URL)

        # Assert
        mock_validate_ssl.assert_called_once_with(TEST_URL, 10)
        assert is_valid is True
        assert "Valid" in message

    def test_validate_url_failure(self, network_client):
        """Test failed URL validation."""
        client, _, mock_validate_ssl = network_client
        mock_validate_ssl.return_value = (False, TEST_SSL_ERROR)

        # Execute
        is_valid, message = client.validate_url(TEST_URL)

        # Assert
        mock_validate_ssl.assert_called_once_with(TEST_URL, 10)
        assert is_valid is False
        assert TEST_SSL_ERROR in message
