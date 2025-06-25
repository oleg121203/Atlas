# self_learning_test.py

"""
Test suite for self-learning algorithms and feedback integration in Atlas.
This module tests the functionality of the SelfLearningAgent class, including
feedback collection, model updating, and response adaptation.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import numpy as np

# Ensure the parent directory is in the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.self_learning_agent import SelfLearningAgent
from utils.memory_management import MemoryManager

class TestSelfLearningAgent(unittest.TestCase):
    """Test cases for SelfLearningAgent class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.memory_manager = MemoryManager()
        self.agent = SelfLearningAgent(memory_manager=self.memory_manager, model_path="test_models")

    def test_initialization(self):
        """Test that the SelfLearningAgent initializes correctly."""
        self.assertIsInstance(self.agent, SelfLearningAgent)
        self.assertEqual(self.agent.memory_manager, self.memory_manager)
        self.assertTrue(os.path.exists("test_models"))
        self.assertIn("general", self.agent.models)
        self.assertIn("general", self.agent.scalers)

    def test_collect_feedback(self):
        """Test collecting feedback from user interactions."""
        user_id = "test_user"
        query = "How are you?"
        response = "I'm fine, thank you!"
        rating = 4.5

        self.agent.collect_feedback(user_id, query, response, rating)
        
        self.assertIn(user_id, self.agent.user_profiles)
        self.assertEqual(self.agent.user_profiles[user_id]["interaction_count"], 1)
        self.assertEqual(self.agent.user_profiles[user_id]["avg_rating"], 4.5)
        self.assertEqual(len(self.agent.feedback_data["queries"]), 1)
        self.assertEqual(self.agent.feedback_data["queries"][0], query)
        self.assertEqual(self.agent.feedback_data["responses"][0], response)
        self.assertEqual(self.agent.feedback_data["ratings"][0], rating)

        # Check if interaction is stored in memory manager
        interactions = self.memory_manager.get_user_interactions(user_id)
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0]["query"], query)
        self.assertEqual(interactions[0]["response"], response)
        self.assertEqual(interactions[0]["rating"], rating)

    def test_update_learning_model_insufficient_data(self):
        """Test updating the learning model with insufficient data."""
        result = self.agent.update_learning_model()
        self.assertFalse(result, "Model update should fail with insufficient data")

    @patch('agents.self_learning_agent.SGDRegressor')
    @patch('agents.self_learning_agent.StandardScaler')
    def test_update_learning_model_with_data(self, mock_scaler, mock_regressor):
        """Test updating the learning model with sufficient feedback data."""
        # Mock the model and scaler
        mock_model_instance = MagicMock()
        mock_regressor.return_value = mock_model_instance
        mock_scaler_instance = MagicMock()
        mock_scaler.return_value = mock_scaler_instance
        self.agent.models["general"] = mock_model_instance
        self.agent.scalers["general"] = mock_scaler_instance

        # Add sufficient feedback data
        for i in range(15):
            self.agent.feedback_data["queries"].append(f"Query {i}")
            self.agent.feedback_data["responses"].append(f"Response {i}")
            self.agent.feedback_data["ratings"].append(float(i % 5 + 1))
            self.agent.feedback_data["timestamps"].append("2023-10-01T00:00:00")

        result = self.agent.update_learning_model()
        self.assertTrue(result, "Model update should succeed with sufficient data")
        mock_scaler_instance.fit_transform.assert_called()
        mock_model_instance.partial_fit.assert_called()

    def test_adapt_response_no_data(self):
        """Test response adaptation when no model or data is available."""
        user_id = "test_user"
        query = "What's the weather?"
        candidates = ["It's sunny.", "It's raining."]

        result = self.agent.adapt_response(user_id, query, candidates)
        self.assertEqual(result["response"], candidates[0])
        self.assertEqual(result["confidence"], 0.5)
        self.assertEqual(result["source"], "default")

    @patch('agents.self_learning_agent.SGDRegressor')
    @patch('agents.self_learning_agent.StandardScaler')
    def test_adapt_response_with_model(self, mock_scaler, mock_regressor):
        """Test response adaptation using a trained model."""
        # Mock the model and scaler
        mock_model_instance = MagicMock()
        mock_model_instance.predict.return_value = np.array([2.0, 4.0])
        mock_regressor.return_value = mock_model_instance
        mock_scaler_instance = MagicMock()
        mock_scaler.return_value = mock_scaler_instance
        self.agent.models["general"] = mock_model_instance
        self.agent.scalers["general"] = mock_scaler_instance

        # Add some feedback data to simulate a trained model
        self.agent.feedback_data["queries"].append("Previous query")
        self.agent.feedback_data["responses"].append("Previous response")
        self.agent.feedback_data["ratings"].append(4.0)

        user_id = "test_user"
        query = "What's the weather?"
        candidates = ["It's sunny.", "It's raining."]

        result = self.agent.adapt_response(user_id, query, candidates)
        self.assertEqual(result["response"], candidates[1], "Should select the response with higher predicted reward")
        self.assertGreater(result["confidence"], 0.5)
        self.assertEqual(result["source"], "self_learning")

    def test_get_user_learning_profile(self):
        """Test retrieving a user's learning profile."""
        user_id = "test_user"
        profile = self.agent.get_user_learning_profile(user_id)
        self.assertEqual(profile["interaction_count"], 0)
        self.assertEqual(profile["avg_rating"], 0.0)
        self.assertEqual(profile["preferences"], {})

        # Add some feedback to update profile
        self.agent.collect_feedback(user_id, "Test query", "Test response", 4.0)
        profile = self.agent.get_user_learning_profile(user_id)
        self.assertEqual(profile["interaction_count"], 1)
        self.assertEqual(profile["avg_rating"], 4.0)

    def test_reset_learning_data(self):
        """Test resetting learning data for a user or all users."""
        user_id = "test_user"
        self.agent.collect_feedback(user_id, "Test query", "Test response", 4.0)
        self.agent.collect_feedback("another_user", "Another query", "Another response", 3.0)

        # Reset data for specific user
        self.agent.reset_learning_data(user_id)
        self.assertNotIn(user_id, self.agent.user_profiles)
        self.assertIn("another_user", self.agent.user_profiles)

        # Reset all data
        self.agent.reset_learning_data()
        self.assertEqual(len(self.agent.user_profiles), 0)
        self.assertEqual(len(self.agent.feedback_data["queries"]), 0)

if __name__ == "__main__":
    unittest.main()
