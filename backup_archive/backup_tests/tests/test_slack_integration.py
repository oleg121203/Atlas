"""Unit Tests for Slack Integration Module"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the parent directory is in the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration.slack.slack_integration import SlackIntegration


class TestSlackIntegration(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.route = MagicMock()
        self.slack_integration = SlackIntegration(self.app)
        self.slack_integration.client_id = "test_client_id"
        self.slack_integration.client_secret = "test_client_secret"
        self.slack_integration.redirect_uri = "http://localhost:5000/slack/callback"

    def test_setup_routes(self):
        self.assertTrue(hasattr(self.slack_integration, "app"))
        self.app.route.assert_called()

    @patch("slack_sdk.oauth.OAuthFlow.get_authorize_url")
    def test_slack_oauth_route(self, mock_get_authorize_url):
        mock_get_authorize_url.return_value = (
            "https://slack.com/oauth/authorize?client_id=test_client_id"
        )
        with self.app.test_request_context("/slack/oauth"):
            response = self.slack_integration.app.route("/slack/oauth")()
            self.assertEqual(
                response, "https://slack.com/oauth/authorize?client_id=test_client_id"
            )

    @patch("slack_sdk.oauth.OAuthFlow.fetch_token")
    @patch("slack_sdk.WebClient")
    def test_slack_callback_success(self, mock_web_client, mock_fetch_token):
        mock_fetch_token.return_value = {"access_token": "test_access_token"}
        mock_web_client.return_value = MagicMock()
        with self.app.test_request_context("/slack/callback?code=test_code"):
            response = self.slack_integration.app.route("/slack/callback")()
            self.assertIn("Slack integration successful", response)

    @patch("slack_sdk.oauth.OAuthFlow.fetch_token")
    def test_slack_callback_failure(self, mock_fetch_token):
        mock_fetch_token.side_effect = Exception("OAuth error")
        with self.app.test_request_context("/slack/callback?code=test_code"):
            response = self.slack_integration.app.route("/slack/callback")()
            self.assertIn("Error during Slack integration", response)

    def test_send_message_without_client(self):
        self.slack_integration.client = None
        result = self.slack_integration.send_message("#channel", "Hello")
        self.assertFalse(result)

    @patch("slack_sdk.WebClient.chat_postMessage")
    def test_send_message_success(self, mock_post_message):
        self.slack_integration.client = MagicMock()
        mock_post_message.return_value = {"ok": True}
        result = self.slack_integration.send_message("#channel", "Hello")
        self.assertTrue(result)

    @patch("slack_sdk.WebClient.chat_postMessage")
    def test_send_message_failure(self, mock_post_message):
        self.slack_integration.client = MagicMock()
        mock_post_message.side_effect = Exception("API error")
        result = self.slack_integration.send_message("#channel", "Hello")
        self.assertFalse(result)

    @patch("slack_integration.SlackIntegration.send_message")
    def test_create_task_from_slack(self, mock_send_message):
        mock_send_message.return_value = True
        task_id = self.slack_integration.create_task_from_slack(
            "#channel", "Create a task"
        )
        self.assertIsNotNone(task_id)
        mock_send_message.assert_called_once()

    @patch("slack_integration.SlackIntegration.send_message")
    def test_create_task_from_slack_empty_title(self, mock_send_message):
        mock_send_message.return_value = True
        task_id = self.slack_integration.create_task_from_slack("#channel", "")
        self.assertIsNone(task_id)
        mock_send_message.assert_called_once_with(
            "#channel", "Cannot create a task without a title."
        )

    @patch("slack_integration.SlackIntegration.send_message")
    @patch("slack_integration.SlackIntegration._retrieve_task")
    @patch("slack_integration.SlackIntegration._store_task")
    def test_update_task_from_slack_complete(
        self, mock_store_task, mock_retrieve_task, mock_send_message
    ):
        mock_send_message.return_value = True
        mock_retrieve_task.return_value = {
            "id": "task_123",
            "title": "Test Task",
            "status": "open",
        }
        result = self.slack_integration.update_task_from_slack(
            "#channel", "task_123", "Mark as complete"
        )
        self.assertTrue(result)
        mock_store_task.assert_called()
        mock_send_message.assert_called_once_with(
            "#channel", "Task task_123 marked as completed."
        )

    @patch("slack_integration.SlackIntegration.send_message")
    @patch("slack_integration.SlackIntegration._retrieve_task")
    @patch("slack_integration.SlackIntegration._store_task")
    def test_update_task_from_slack_note(
        self, mock_store_task, mock_retrieve_task, mock_send_message
    ):
        mock_send_message.return_value = True
        mock_retrieve_task.return_value = {
            "id": "task_123",
            "title": "Test Task",
            "status": "open",
        }
        result = self.slack_integration.update_task_from_slack(
            "#channel", "task_123", "Add a note"
        )
        self.assertTrue(result)
        mock_store_task.assert_called()
        mock_send_message.assert_called_once_with(
            "#channel", "Task task_123 updated with note: Add a note"
        )

    @patch("slack_integration.SlackIntegration.send_message")
    @patch("slack_integration.SlackIntegration._retrieve_task")
    def test_update_task_from_slack_not_found(
        self, mock_retrieve_task, mock_send_message
    ):
        mock_send_message.return_value = True
        mock_retrieve_task.return_value = None
        result = self.slack_integration.update_task_from_slack(
            "#channel", "task_123", "Update task"
        )
        self.assertFalse(result)
        mock_send_message.assert_called_once_with(
            "#channel", "Task task_123 not found."
        )

    @patch("slack_integration.SlackIntegration.send_message")
    def test_notify_task_progress(self, mock_send_message):
        mock_send_message.return_value = True
        result = self.slack_integration.notify_task_progress(
            "#channel", "task_123", "In progress"
        )
        self.assertTrue(result)
        mock_send_message.assert_called_once_with(
            "#channel", "Task task_123 progress: In progress"
        )

    @patch("slack_integration.SlackIntegration.send_message")
    def test_update_task_from_slack(self, mock_send_message):
        mock_send_message.return_value = True
        result = self.slack_integration.update_task_from_slack(
            "#channel", "task_123", "Update task"
        )
        self.assertTrue(result)
        mock_send_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()
