"""Slack Integration Module for Atlas

This module handles the integration with Slack for task creation, updates, and notifications.
"""

import os
import json
import requests
from slack_sdk import WebClient
from slack_sdk.oauth import OAuthFlow
from flask import Flask, request, redirect, url_for
import time

from core.config import Config

class SlackIntegration:
    def __init__(self, app):
        self.app = app
        self.client_id = Config.SLACK_CLIENT_ID
        self.client_secret = Config.SLACK_CLIENT_SECRET
        self.redirect_uri = Config.SLACK_REDIRECT_URI
        self.scopes = ['chat:write', 'channels:read', 'groups:read', 'users:read']
        self.oauth_flow = OAuthFlow(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes
        )
        self.client = None
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/slack/oauth')
        def slack_oauth():
            return self.oauth_flow.get_authorize_url()

        @self.app.route('/slack/callback')
        def slack_callback():
            code = request.args.get('code')
            if code:
                try:
                    token_response = self.oauth_flow.fetch_token(code=code)
                    access_token = token_response.get('access_token')
                    self.client = WebClient(token=access_token)
                    # Save the token for future use
                    with open('slack_token.json', 'w') as f:
                        json.dump(token_response, f)
                    return 'Slack integration successful. You can close this window.'
                except Exception as e:
                    return f'Error during Slack integration: {str(e)}'
            return 'No code provided for Slack integration.'

    def send_message(self, channel, text):
        if not self.client:
            self._load_token()
        if self.client:
            try:
                response = self.client.chat_postMessage(channel=channel, text=text)
                return response['ok']
            except Exception as e:
                print(f"Error sending Slack message: {e}")
                return False
        return False

    def _load_token(self):
        try:
            with open('slack_token.json', 'r') as f:
                token_data = json.load(f)
                access_token = token_data.get('access_token')
                if access_token:
                    self.client = WebClient(token=access_token)
        except Exception as e:
            print(f"Error loading Slack token: {e}")

    def create_task_from_slack(self, channel, text):
        """Create a task from a Slack message."""
        # Extract task details from the message text
        task_title = text.strip()
        if not task_title:
            self.send_message(channel, "Cannot create a task without a title.")
            return None
        
        # Placeholder for actual task creation logic in Atlas
        task_id = f"task_{hash(task_title)}_{int(time.time())}"
        task_data = {
            "id": task_id,
            "title": task_title,
            "status": "open",
            "created": time.time()
        }
        
        # Store task data (placeholder for database storage)
        self._store_task(task_data)
        
        self.send_message(channel, f"Task created with ID: {task_id} - {task_title}")
        return task_id

    def update_task_from_slack(self, channel, task_id, update_text):
        """Update a task based on Slack message."""
        # Placeholder for task update logic in Atlas
        task_data = self._retrieve_task(task_id)
        if not task_data:
            self.send_message(channel, f"Task {task_id} not found.")
            return False
        
        if "complete" in update_text.lower() or "done" in update_text.lower():
            task_data["status"] = "completed"
            self._store_task(task_data)
            self.send_message(channel, f"Task {task_id} marked as completed.")
        else:
            task_data["notes"] = update_text
            self._store_task(task_data)
            self.send_message(channel, f"Task {task_id} updated with note: {update_text}")
        return True

    def notify_task_progress(self, channel, task_id, progress_message):
        """Notify Slack channel about task progress."""
        return self.send_message(channel, f"Task {task_id} progress: {progress_message}")

    def _store_task(self, task_data):
        """Placeholder for storing task data in Atlas database."""
        # This should interact with Atlas's actual task management system
        try:
            with open('tasks.json', 'r') as f:
                tasks = json.load(f)
        except FileNotFoundError:
            tasks = {}
        
        tasks[task_data["id"]] = task_data
        with open('tasks.json', 'w') as f:
            json.dump(tasks, f)

    def _retrieve_task(self, task_id):
        """Placeholder for retrieving task data from Atlas database."""
        try:
            with open('tasks.json', 'r') as f:
                tasks = json.load(f)
            return tasks.get(task_id)
        except FileNotFoundError:
            return None
