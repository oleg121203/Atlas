# self_learning_agent.py

"""
Self-Learning Agent module for Atlas.
This module implements the core functionality for self-learning algorithms,
enabling the AI to improve responses based on user interactions and feedback.
"""

from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

from utils.logger import get_logger
from utils.memory_management import MemoryManager

logger = get_logger()

class SelfLearningAgent:
    """A class to manage self-learning capabilities for Atlas AI."""

    def __init__(self, memory_manager: MemoryManager, model_path: str = "models/self_learning"):
        """Initialize the SelfLearningAgent with a memory manager and model storage path.

        Args:
            memory_manager (MemoryManager): The memory manager instance for storing feedback and context.
            model_path (str): Path to store and load learning models.
        """
        self.memory_manager = memory_manager
        self.model_path = model_path
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feedback_data: Dict[str, list] = {'queries': [], 'responses': [], 'ratings': [], 'timestamps': []}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self._initialize_models()
        logger.info("SelfLearningAgent initialized")

    def _initialize_models(self) -> None:
        """Initialize or load learning models for response improvement.
        Currently uses a simple SGDRegressor for contextual bandit learning.
        """
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        # Initialize or load a model for general response selection
        general_model_path = os.path.join(self.model_path, "general_model.json")
        if os.path.exists(general_model_path):
            self._load_model("general", general_model_path)
        else:
            self.models["general"] = SGDRegressor(loss="squared_loss", penalty="l2", alpha=0.01, learning_rate="adaptive")
            self.scalers["general"] = StandardScaler()
            logger.debug("Initialized general SGDRegressor model")

    def _load_model(self, model_name: str, path: str) -> None:
        """Load a saved model and scaler from the specified path.

        Args:
            model_name (str): The name/key of the model to load.
            path (str): The file path to load the model data from.
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Placeholder for actual model loading logic
                self.models[model_name] = SGDRegressor(loss="squared_loss", penalty="l2", alpha=0.01, learning_rate="adaptive")
                self.scalers[model_name] = StandardScaler()
                logger.info(f"Loaded model {model_name} from {path}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            self.models[model_name] = SGDRegressor(loss="squared_loss", penalty="l2", alpha=0.01, learning_rate="adaptive")
            self.scalers[model_name] = StandardScaler()

    def _save_model(self, model_name: str, path: str) -> None:
        """Save a model and scaler to the specified path.

        Args:
            model_name (str): The name/key of the model to save.
            path (str): The file path to save the model data to.
        """
        try:
            # Placeholder for actual model saving logic
            data = {"placeholder": "Model data would be saved here"}
            with open(path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved model {model_name} to {path}")
        except Exception as e:
            logger.error(f"Failed to save model {model_name}: {e}")

    def collect_feedback(self, user_id: str, query: str, response: str, rating: Optional[float] = None,
                         engagement_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Collect feedback from user interactions for learning.

        Args:
            user_id (str): Unique identifier for the user.
            query (str): The user's query or input.
            response (str): The AI's response to the query.
            rating (float, optional): Explicit user rating (e.g., 1-5). Defaults to None.
            engagement_metrics (dict, optional): Implicit feedback like time spent or clicks. Defaults to None.
        """
        timestamp = datetime.now().isoformat()
        self.feedback_data['queries'].append(query)
        self.feedback_data['responses'].append(response)
        self.feedback_data['ratings'].append(rating if rating is not None else 3.0)  # Default neutral rating
        self.feedback_data['timestamps'].append(timestamp)

        # Update user profile with feedback
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {'interaction_count': 0, 'avg_rating': 0.0, 'preferences': {}}
        profile = self.user_profiles[user_id]
        profile['interaction_count'] += 1
        profile['avg_rating'] = (profile['avg_rating'] * (profile['interaction_count'] - 1) + (rating or 3.0)) / profile['interaction_count']

        # Log engagement metrics if provided
        if engagement_metrics:
            logger.debug(f"Engagement metrics for user {user_id}: {engagement_metrics}")

        logger.info(f"Collected feedback for user {user_id} on query: {query[:50]}...")
        self.memory_manager.store_interaction(user_id, query, response, rating, timestamp)

    def update_learning_model(self, model_name: str = "general") -> bool:
        """Update the learning model with recent feedback data.

        Args:
            model_name (str): The name of the model to update. Defaults to 'general'.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        if len(self.feedback_data['queries']) < 10:  # Minimum data threshold for update
            logger.warning("Insufficient feedback data for model update")
            return False

        try:
            # Extract features (placeholder for actual feature extraction)
            X = np.array([self._extract_features(q, r) for q, r in
                          zip(self.feedback_data['queries'], self.feedback_data['responses'])])
            y = np.array(self.feedback_data['ratings'])

            if X.shape[0] == 0 or y.shape[0] == 0:
                logger.error("Empty feature or target data for model update")
                return False

            # Scale features
            scaler = self.scalers.get(model_name, StandardScaler())
            X_scaled = scaler.fit_transform(X) if len(X) > 1 else scaler.transform(X)
            self.scalers[model_name] = scaler

            # Update model incrementally
            model = self.models.get(model_name)
            if model:
                model.partial_fit(X_scaled, y)
                self.models[model_name] = model
                logger.info(f"Updated {model_name} model with {len(y)} new data points")

                # Save updated model
                model_path = os.path.join(self.model_path, f"{model_name}_model.json")
                self._save_model(model_name, model_path)

                # Clear some feedback data to manage memory
                self._trim_feedback_data()
                return True
            else:
                logger.error(f"Model {model_name} not found for update")
                return False
        except Exception as e:
            logger.error(f"Failed to update learning model {model_name}: {e}", exc_info=True)
            return False

    def _extract_features(self, query: str, response: str) -> list:
        """Extract features from query and response for learning.
        Currently a placeholder returning dummy features.

        Args:
            query (str): The user's query.
            response (str): The AI's response.

        Returns:
            list: Extracted feature vector.
        """
        # Placeholder for actual feature extraction (e.g., embeddings, sentiment analysis)
        return [len(query), len(response), query.count(' '), response.count(' ')]

    def _trim_feedback_data(self) -> None:
        """Trim feedback data to prevent memory bloat, keeping recent interactions."""
        max_items = 1000
        if len(self.feedback_data['queries']) > max_items:
            for key in self.feedback_data:
                self.feedback_data[key] = self.feedback_data[key][-max_items:]
            logger.debug(f"Trimmed feedback data to last {max_items} items")

    def adapt_response(self, user_id: str, query: str, candidate_responses: list) -> Dict[str, Any]:
        """Select or adapt a response from candidates based on learned model and user profile.

        Args:
            user_id (str): Unique identifier for the user.
            query (str): The user's query.
            candidate_responses (list): List of possible responses to choose from.

        Returns:
            dict: Selected response with metadata (e.g., confidence score).
        """
        if not candidate_responses:
            logger.warning("No candidate responses provided for adaptation")
            return {"response": "", "confidence": 0.0, "source": "default"}

        # Default to first response if no learning model or data
        if "general" not in self.models or not self.feedback_data['queries']:
            logger.debug("Using default response selection (no model or data)")
            return {"response": candidate_responses[0], "confidence": 0.5, "source": "default"}

        try:
            # Extract features for the query and each candidate response
            features = [self._extract_features(query, resp) for resp in candidate_responses]
            scaler = self.scalers.get("general")
            features_scaled = scaler.transform(features) if scaler else features

            # Predict reward (quality) for each response
            model = self.models.get("general")
            predicted_rewards = model.predict(features_scaled) if model else [0.5] * len(candidate_responses)

            # Select response with highest predicted reward
            best_idx = np.argmax(predicted_rewards)
            selected_response = candidate_responses[best_idx]
            confidence = float(predicted_rewards[best_idx]) / 5.0  # Normalize to 0-1 scale assuming max rating is 5

            # Adjust confidence based on user profile if available
            user_profile = self.user_profiles.get(user_id, {})
            adjustment_factor = user_profile.get("avg_rating", 3.0) / 5.0
            confidence = confidence * 0.8 + adjustment_factor * 0.2

            logger.info(f"Adapted response for user {user_id} with confidence {confidence:.2f}")
            return {
                "response": selected_response,
                "confidence": max(0.1, min(1.0, confidence)),  # Bound confidence between 0.1 and 1.0
                "source": "self_learning"
            }
        except Exception as e:
            logger.error(f"Error adapting response for user {user_id}: {e}", exc_info=True)
            return {"response": candidate_responses[0], "confidence": 0.5, "source": "error_fallback"}

    def get_user_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve the learning profile for a specific user.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            dict: User profile data related to learning.
        """
        return self.user_profiles.get(user_id, {
            "interaction_count": 0,
            "avg_rating": 0.0,
            "preferences": {}
        })

    def reset_learning_data(self, user_id: Optional[str] = None) -> None:
        """Reset learning data for a specific user or all users.

        Args:
            user_id (str, optional): Unique identifier for the user. If None, reset all data. Defaults to None.
        """
        if user_id is None:
            self.feedback_data = {'queries': [], 'responses': [], 'ratings': [], 'timestamps': []}
            self.user_profiles = {}
            logger.info("Reset all learning data")
        else:
            if user_id in self.user_profiles:
                del self.user_profiles[user_id]
            # Remove user-specific feedback data (if identifiable)
            logger.info(f"Reset learning data for user {user_id}")
