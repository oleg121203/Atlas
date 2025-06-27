"""Unit tests for Real-Time Collaboration module."""

import os
import unittest

from flask import Flask

from enterprise.real_time_collaboration import RealTimeCollaboration


class TestRealTimeCollaboration(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_file = "test_collaboration_data.json"
        self.collaboration = RealTimeCollaboration(self.app, self.test_data_file)
        self.collaboration.chats = {}
        self.collaboration.documents = {}
        self.collaboration.tasks = {}

    def tearDown(self):
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_send_chat_message(self):
        message = self.collaboration.send_chat_message("ws1", "user1", "Hello, team!")
        self.assertEqual(message["user_id"], "user1")
        self.assertEqual(message["message"], "Hello, team!")
        self.assertTrue("timestamp" in message)
        self.assertIn("ws1", self.collaboration.chats)
        self.assertEqual(len(self.collaboration.chats["ws1"]), 1)
        self.assertEqual(self.collaboration.chats["ws1"][0]["message"], "Hello, team!")

    def test_get_chat_history(self):
        self.collaboration.send_chat_message("ws1", "user1", "Message 1")
        self.collaboration.send_chat_message("ws1", "user2", "Message 2")
        history = self.collaboration.get_chat_history("ws1")
        self.assertEqual(len(history), 2)
        messages = [m["message"] for m in history]
        self.assertIn("Message 1", messages)
        self.assertIn("Message 2", messages)

    def test_get_chat_history_empty(self):
        history = self.collaboration.get_chat_history("ws2")
        self.assertEqual(len(history), 0)

    def test_update_document_new(self):
        doc = self.collaboration.update_document("doc1", "Initial content", "user1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["content"], "Initial content")
        self.assertEqual(doc["last_updated_by"], "user1")
        self.assertTrue("last_updated_at" in doc)
        self.assertEqual(len(doc["history"]), 0)

    def test_update_document_existing(self):
        self.collaboration.update_document("doc1", "Initial content", "user1")
        doc = self.collaboration.update_document("doc1", "Updated content", "user2")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["content"], "Updated content")
        self.assertEqual(doc["last_updated_by"], "user2")
        self.assertTrue("last_updated_at" in doc)
        self.assertEqual(len(doc["history"]), 1)
        self.assertEqual(doc["history"][0]["content"], "Initial content")
        self.assertEqual(doc["history"][0]["updated_by"], "user1")

    def test_get_document(self):
        self.collaboration.update_document("doc1", "Some content", "user1")
        doc = self.collaboration.get_document("doc1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["content"], "Some content")

    def test_get_document_not_found(self):
        doc = self.collaboration.get_document("doc2")
        self.assertIsNone(doc)

    def test_create_task_success(self):
        result = self.collaboration.create_task(
            "ws1", "task1", "Test Task", "Do something", ["user1", "user2"], "user1"
        )
        self.assertTrue(result)
        self.assertIn("ws1", self.collaboration.tasks)
        self.assertIn("task1", self.collaboration.tasks["ws1"])
        task = self.collaboration.tasks["ws1"]["task1"]
        self.assertEqual(task["title"], "Test Task")
        self.assertEqual(task["description"], "Do something")
        self.assertEqual(task["assigned_to"], ["user1", "user2"])
        self.assertEqual(task["created_by"], "user1")
        self.assertEqual(task["status"], "open")
        self.assertTrue("created_at" in task)

    def test_create_task_duplicate(self):
        self.collaboration.create_task(
            "ws1", "task1", "Test Task", "Do something", ["user1"], "user1"
        )
        result = self.collaboration.create_task(
            "ws1", "task1", "Duplicate Task", "Do something else", ["user2"], "user2"
        )
        self.assertFalse(result)
        task = self.collaboration.tasks["ws1"]["task1"]
        self.assertEqual(task["title"], "Test Task")
        self.assertEqual(task["created_by"], "user1")

    def test_update_task_status_success(self):
        self.collaboration.create_task(
            "ws1", "task1", "Test Task", "Do something", ["user1"], "user1"
        )
        result = self.collaboration.update_task_status(
            "ws1", "task1", "in_progress", "user1"
        )
        self.assertTrue(result)
        task = self.collaboration.tasks["ws1"]["task1"]
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(len(task["updates"]), 1)
        self.assertEqual(task["updates"][0]["status"], "in_progress")
        self.assertEqual(task["updates"][0]["updated_by"], "user1")
        self.assertTrue("updated_at" in task["updates"][0])

    def test_update_task_status_not_found(self):
        result = self.collaboration.update_task_status(
            "ws1", "task2", "in_progress", "user1"
        )
        self.assertFalse(result)

    def test_get_tasks(self):
        self.collaboration.create_task(
            "ws1", "task1", "Task 1", "Do something", ["user1"], "user1"
        )
        self.collaboration.create_task(
            "ws1", "task2", "Task 2", "Do something else", ["user2"], "user1"
        )
        tasks = self.collaboration.get_tasks("ws1")
        self.assertEqual(len(tasks), 2)
        self.assertIn("task1", tasks)
        self.assertIn("task2", tasks)

    def test_get_tasks_empty(self):
        tasks = self.collaboration.get_tasks("ws2")
        self.assertEqual(len(tasks), 0)


if __name__ == "__main__":
    unittest.main()
