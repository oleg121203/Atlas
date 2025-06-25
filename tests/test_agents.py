"""
Test cases for the agents module of Atlas application.
"""

import unittest
from modules.agents.agent_manager import AgentManager
from core.application import AtlasApplication

class TestAgentsModule(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])
        self.agent_manager = AgentManager()

    def test_agent_manager_initialization(self):
        """Test if the agent manager initializes correctly."""
        self.assertIsNotNone(self.agent_manager)
        self.assertTrue(hasattr(self.agent_manager, 'create_agent'))

    def test_agent_creation(self):
        """Test if an agent can be created successfully."""
        agent_name = "Test Agent"
        agent_id = self.agent_manager.create_agent(agent_name)
        self.assertIsNotNone(agent_id)
        self.assertIsInstance(agent_id, str)

if __name__ == '__main__':
    unittest.main()
