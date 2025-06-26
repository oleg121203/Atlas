"""
Unit Tests for Workflow Integration

This module tests the functionality of the WorkflowIntegrator and adapters
for connecting workflows with enterprise systems.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from workflow.integration import IntegrationAdapter, RESTApiAdapter, WorkflowIntegrator

class TestIntegrationAdapter(unittest.TestCase):
    def test_abstract_adapter(self):
        """Test that the abstract IntegrationAdapter cannot be instantiated directly."""
        config = {'base_url': 'http://example.com'}
        with self.assertRaises(TypeError):
            IntegrationAdapter(config)

class TestRESTApiAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test_key_123'
        }
        self.adapter = RESTApiAdapter(self.config)

    @patch('requests.Session.get')
    def test_connect_success(self, mock_get):
        """Test successful connection to REST API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.adapter.connect()
        self.assertTrue(result)
        self.assertTrue(self.adapter.is_connected)
        mock_get.assert_called_once_with('http://api.example.com/health', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_key_123'}, timeout=5)

    @patch('requests.Session.get')
    def test_connect_failure(self, mock_get):
        """Test failed connection to REST API."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        result = self.adapter.connect()
        self.assertFalse(result)
        self.assertFalse(self.adapter.is_connected)
        mock_get.assert_called_once_with('http://api.example.com/health', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_key_123'}, timeout=5)

    def test_disconnect(self):
        """Test disconnecting from REST API."""
        self.adapter.is_connected = True
        self.adapter.disconnect()
        self.assertFalse(self.adapter.is_connected)

    @patch('requests.Session.post')
    def test_send_data_success(self, mock_post):
        """Test sending data to REST API successfully."""
        self.adapter.is_connected = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        data = {'key': 'value'}
        endpoint = 'data_endpoint'
        response = self.adapter.send_data(data, endpoint)
        self.assertEqual(response, {'status': 'success'})
        mock_post.assert_called_once_with('http://api.example.com/data_endpoint', json=data, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_key_123'}, timeout=10)

    @patch('requests.Session.get')
    def test_receive_data_success(self, mock_get):
        """Test receiving data from REST API successfully."""
        self.adapter.is_connected = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test_data'}
        mock_get.return_value = mock_response

        endpoint = 'fetch_endpoint'
        query = 'id=123'
        response = self.adapter.receive_data(query, endpoint)
        self.assertEqual(response, {'data': 'test_data'})
        mock_get.assert_called_once_with('http://api.example.com/fetch_endpoint?id=123', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_key_123'}, timeout=10)

class TestWorkflowIntegrator(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.integrator = WorkflowIntegrator()
        self.config = {
            'base_url': 'http://api.example.com',
            'api_key': 'test_key_123'
        }
        self.adapter = RESTApiAdapter(self.config)
        self.system_id = 'test_system'

    def test_register_adapter(self):
        """Test registering an integration adapter."""
        self.integrator.register_adapter(self.system_id, self.adapter)
        self.assertIn(self.system_id, self.integrator.adapters)
        self.assertEqual(self.integrator.adapters[self.system_id], self.adapter)

    @patch.object(RESTApiAdapter, 'connect')
    def test_connect_to_system_success(self, mock_connect):
        """Test successful connection to a system via adapter."""
        mock_connect.return_value = True
        self.integrator.register_adapter(self.system_id, self.adapter)
        result = self.integrator.connect_to_system(self.system_id)
        self.assertTrue(result)
        mock_connect.assert_called_once()

    @patch.object(RESTApiAdapter, 'connect')
    def test_connect_to_system_failure(self, mock_connect):
        """Test failed connection to a system via adapter."""
        mock_connect.return_value = False
        self.integrator.register_adapter(self.system_id, self.adapter)
        result = self.integrator.connect_to_system(self.system_id)
        self.assertFalse(result)
        mock_connect.assert_called_once()

    def test_connect_to_nonexistent_system(self):
        """Test attempting to connect to a system with no registered adapter."""
        result = self.integrator.connect_to_system('nonexistent_system')
        self.assertFalse(result)

    @patch.object(RESTApiAdapter, 'disconnect')
    def test_disconnect_from_system(self, mock_disconnect):
        """Test disconnecting from a system via adapter."""
        self.integrator.register_adapter(self.system_id, self.adapter)
        self.integrator.disconnect_from_system(self.system_id)
        mock_disconnect.assert_called_once()

    @patch.object(RESTApiAdapter, 'send_data')
    def test_send_to_system(self, mock_send_data):
        """Test sending data to a system via adapter."""
        mock_send_data.return_value = {'status': 'success'}
        self.integrator.register_adapter(self.system_id, self.adapter)
        data = {'key': 'value'}
        endpoint = 'data_endpoint'
        response = self.integrator.send_to_system(self.system_id, data, endpoint)
        self.assertEqual(response, {'status': 'success'})
        mock_send_data.assert_called_once_with(data, endpoint)

    @patch.object(RESTApiAdapter, 'receive_data')
    def test_receive_from_system(self, mock_receive_data):
        """Test receiving data from a system via adapter."""
        mock_receive_data.return_value = {'data': 'test_data'}
        self.integrator.register_adapter(self.system_id, self.adapter)
        query = 'id=123'
        endpoint = 'fetch_endpoint'
        response = self.integrator.receive_from_system(self.system_id, query, endpoint)
        self.assertEqual(response, {'data': 'test_data'})
        mock_receive_data.assert_called_once_with(query, endpoint)

    def test_send_to_nonexistent_system(self):
        """Test attempting to send data to a system with no registered adapter."""
        data = {'key': 'value'}
        with self.assertRaises(ValueError):
            self.integrator.send_to_system('nonexistent_system', data)

    def test_receive_from_nonexistent_system(self):
        """Test attempting to receive data from a system with no registered adapter."""
        with self.assertRaises(ValueError):
            self.integrator.receive_from_system('nonexistent_system')

if __name__ == '__main__':
    unittest.main()
