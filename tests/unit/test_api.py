import logging
import unittest
from unittest.mock import patch

from core.api import app


class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config["TESTING"] = True
        # Disable logging for tests to avoid clutter
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_automate_task_endpoint_success(self):
        """Test the automate task endpoint with valid input."""
        with patch("core.api.automate_ai_task") as mock_automate:
            mock_automate.return_value = {"step1": "do something"}
            response = self.client.post(
                "/api/v1/automate",
                json={
                    "model_name": "test_model",
                    "task_description": "test task",
                    "context": {},
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"plan": {"step1": "do something"}})
            mock_automate.assert_called_once_with("test_model", "test task", {})

    def test_automate_task_endpoint_missing_model_name(self):
        """Test the automate task endpoint with missing model_name."""
        response = self.client.post(
            "/api/v1/automate", json={"task_description": "test task"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "model_name and task_description are required"}
        )

    def test_automate_task_endpoint_missing_task_description(self):
        """Test the automate task endpoint with missing task_description."""
        response = self.client.post(
            "/api/v1/automate", json={"model_name": "test_model"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "model_name and task_description are required"}
        )

    def test_automate_task_endpoint_missing_params(self):
        """Test the automate task endpoint with missing parameters."""
        response = self.client.post("/api/v1/automate", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "model_name and task_description are required"}
        )

    def test_automate_task_endpoint_error(self):
        """Test the automate task endpoint when an error occurs."""
        with patch("core.api.automate_ai_task") as mock_automate:
            mock_automate.side_effect = Exception("Test error")
            response = self.client.post(
                "/api/v1/automate",
                json={"model_name": "test_model", "task_description": "test task"},
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json, {"error": "Test error"})

    def test_automate_task_endpoint_invalid_json(self):
        """Test the automate task endpoint with invalid JSON."""
        response = self.client.post(
            "/api/v1/automate", data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        if response.json is not None:
            self.assertTrue(
                "error" in response.json, "Expected 'error' key in response"
            )
        else:
            self.fail("Expected JSON response but got None")

    def test_get_suggestion_endpoint_success(self):
        """Test the get suggestion endpoint with valid input."""
        with patch("core.api.get_ai_suggestion") as mock_suggestion:
            mock_suggestion.return_value = "This is a suggestion"
            response = self.client.post(
                "/api/v1/suggestion",
                json={
                    "model_name": "test_model",
                    "prompt": "test prompt",
                    "context": {},
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"suggestion": "This is a suggestion"})
            mock_suggestion.assert_called_once_with("test_model", {}, "general")

    def test_get_suggestion_endpoint_missing_model_name(self):
        """Test the get suggestion endpoint with missing model_name."""
        response = self.client.post(
            "/api/v1/suggestion", json={"prompt": "test prompt"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "model_name is required"})

    def test_get_suggestion_endpoint_missing_params(self):
        """Test the get suggestion endpoint with missing parameters."""
        response = self.client.post("/api/v1/suggestion", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "model_name is required"})

    def test_get_suggestion_endpoint_error(self):
        """Test the get suggestion endpoint when an error occurs."""
        with patch("core.api.get_ai_suggestion") as mock_suggestion:
            mock_suggestion.side_effect = Exception("Test error")
            response = self.client.post(
                "/api/v1/suggestion",
                json={"model_name": "test_model", "prompt": "test prompt"},
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json, {"error": "Test error"})

    def test_get_suggestion_endpoint_invalid_json(self):
        """Test the get suggestion endpoint with invalid JSON."""
        response = self.client.post(
            "/api/v1/suggestion", data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        if response.json is not None:
            self.assertTrue(
                "error" in response.json, "Expected 'error' key in response"
            )
        else:
            self.fail("Expected JSON response but got None")


if __name__ == "__main__":
    unittest.main()
