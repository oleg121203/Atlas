"""
Integration test cases for the Atlas application.

These tests verify the interactions between different modules like chat, tasks, and agents.
"""

import unittest
from core.application import AtlasApplication
from modules.chat.chat_logic import ChatProcessor
from modules.tasks.task_manager import TaskManager
from modules.agents.agent_manager import AgentManager

class TestModuleIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])
        self.chat_processor = ChatProcessor()
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()

    def test_chat_to_task_integration(self):
        """Test if a chat message can trigger a task creation."""
        chat_message = "Create a new task: Test Task from Chat"
        chat_response = self.chat_processor.process_message(chat_message)
        self.assertIsNotNone(chat_response)
        self.assertIn("task created", chat_response.lower())
        
        # Extract task ID from response if possible, or create a task directly for verification
        task_id = self.task_manager.create_task("Test Task from Chat")
        self.assertIsNotNone(task_id)

    def test_task_to_agent_integration(self):
        """Test if a task can be assigned to an agent."""
        task_id = self.task_manager.create_task("Test Task for Agent")
        self.assertIsNotNone(task_id)
        
        agent_id = self.agent_manager.create_agent("Test Agent for Task")
        self.assertIsNotNone(agent_id)
        
        assignment_result = self.task_manager.assign_task_to_agent(task_id, agent_id)
        self.assertTrue(assignment_result)

    def test_chat_to_agent_integration(self):
        """Test if a chat message can trigger an agent action."""
        chat_message = "Ask agent to perform a task"
        chat_response = self.chat_processor.process_message(chat_message)
        self.assertIsNotNone(chat_response)
        self.assertIn("agent", chat_response.lower())
        
        agent_id = self.agent_manager.create_agent("Test Agent from Chat")
        self.assertIsNotNone(agent_id)

if __name__ == '__main__':
    unittest.main()
