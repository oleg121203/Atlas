# context_analyzer.py

"""
Context Analyzer module for Atlas.
This module implements functionality to extract and process contextual information
to inform autonomous task planning and personalized user interactions.
"""

from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime, timedelta
import logging
import calendar
import time

from utils.logger import get_logger
from utils.memory_management import MemoryManager

logger = get_logger()

class ContextAnalyzer:
    """A class to analyze and provide contextual information for Atlas AI."""

    def __init__(self, memory_manager: MemoryManager, context_path: str = "context_data"):
        """Initialize the ContextAnalyzer with memory manager for historical data.

        Args:
            memory_manager (MemoryManager): The memory manager instance for accessing user history.
            context_path (str): Path to store and load context data.
        """
        self.memory_manager = memory_manager
        self.context_path = context_path
        self.user_context: Dict[str, Dict[str, Any]] = {}
        if not os.path.exists(context_path):
            os.makedirs(context_path)
        self.load_context()
        logger.info("ContextAnalyzer initialized")

    def load_context(self) -> None:
        """Load existing user context data from storage."""
        try:
            context_file = os.path.join(self.context_path, "user_context.json")
            if os.path.exists(context_file):
                with open(context_file, 'r') as f:
                    self.user_context = json.load(f)
                    logger.info(f"Loaded context data for {len(self.user_context)} users from storage")
            else:
                logger.debug("No existing context file found, starting with empty context")
        except Exception as e:
            logger.error(f"Failed to load context data: {e}")
            self.user_context = {}

    def save_context(self) -> None:
        """Save user context data to storage."""
        try:
            context_file = os.path.join(self.context_path, "user_context.json")
            with open(context_file, 'w') as f:
                json.dump(self.user_context, f, indent=2)
            logger.debug(f"Saved context data for {len(self.user_context)} users to storage")
        except Exception as e:
            logger.error(f"Failed to save context data: {e}")

    def update_user_context(self, user_id: str, context_updates: Dict[str, Any]) -> None:
        """Update context information for a specific user.

        Args:
            user_id (str): Unique identifier for the user.
            context_updates (Dict[str, Any]): Dictionary of context data to update.
        """
        if user_id not in self.user_context:
            self.user_context[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "interaction_patterns": {},
                "preferences": {},
                "current_state": {},
                "external_data": {}
            }

        context = self.user_context[user_id]
        for key, value in context_updates.items():
            if key in context:
                if isinstance(context[key], dict) and isinstance(value, dict):
                    context[key].update(value)
                else:
                    context[key] = value
            else:
                context[key] = value

        context["last_updated"] = datetime.now().isoformat()
        self.save_context()
        logger.debug(f"Updated context for user {user_id}")

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve the full context for a specific user.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            Dict[str, Any]: The user's context data, or a default empty context if not found.
        """
        if user_id not in self.user_context:
            # Initialize with basic context if not found
            self.user_context[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "interaction_patterns": {},
                "preferences": {},
                "current_state": {},
                "external_data": {}
            }
            # Populate with data from memory manager if available
            interactions = self.memory_manager.get_user_interactions(user_id)
            if interactions:
                self.analyze_interaction_patterns(user_id, interactions)

        # Always refresh current state with real-time data
        self.refresh_current_state(user_id)
        logger.debug(f"Retrieved context for user {user_id}")
        return self.user_context[user_id]

    def refresh_current_state(self, user_id: str) -> None:
        """Refresh the current state of a user with real-time data.

        Args:
            user_id (str): Unique identifier for the user.
        """
        if user_id not in self.user_context:
            self.user_context[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "interaction_patterns": {},
                "preferences": {},
                "current_state": {},
                "external_data": {}
            }

        current_state = self.user_context[user_id]["current_state"]
        current_time = datetime.now()
        current_state.update({
            "time_of_day": current_time.hour,
            "day_of_week": current_time.weekday(),
            "date": current_time.date().isoformat(),
            "is_weekend": current_time.weekday() >= 5,
            "last_interaction": self._get_last_interaction_time(user_id)
        })

        # Placeholder for location data (would require integration with location services)
        current_state["location"] = {"status": "unknown", "last_known": None}

        # Placeholder for calendar data (would require calendar API integration)
        current_state["upcoming_events"] = []

        self.user_context[user_id]["last_updated"] = datetime.now().isoformat()
        self.save_context()
        logger.debug(f"Refreshed current state for user {user_id}")

    def _get_last_interaction_time(self, user_id: str) -> Optional[str]:
        """Get the timestamp of the user's last interaction.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            Optional[str]: ISO format timestamp of last interaction, or None if no interactions.
        """
        interactions = self.memory_manager.get_user_interactions(user_id, limit=1)
        if interactions and len(interactions) > 0:
            return interactions[-1].get("timestamp")
        return None

    def analyze_interaction_patterns(self, user_id: str, interactions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Analyze user interaction patterns to infer habits and workload.

        Args:
            user_id (str): Unique identifier for the user.
            interactions (List[Dict[str, Any]], optional): List of interactions to analyze. If None, fetch from memory. Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary of interaction patterns.
        """
        if interactions is None:
            interactions = self.memory_manager.get_user_interactions(user_id)

        if user_id not in self.user_context:
            self.user_context[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "interaction_patterns": {},
                "preferences": {},
                "current_state": {},
                "external_data": {}
            }

        patterns = self.user_context[user_id]["interaction_patterns"]
        if not interactions:
            patterns.update({
                "frequency": "none",
                "peak_hours": [],
                "average_query_length": 0,
                "task_completion_rate": 0.0,
                "last_analysis": datetime.now().isoformat()
            })
            return patterns

        # Calculate frequency and peak hours
        timestamps = [interaction.get("timestamp") for interaction in interactions if interaction.get("timestamp")]
        if timestamps:
            try:
                dates = [datetime.fromisoformat(ts) for ts in timestamps]
                hours = [dt.hour for dt in dates]
                days = [dt.weekday() for dt in dates]
                
                # Frequency: rough estimate of interactions per day
                time_span = (dates[-1] - dates[0]).total_seconds() / (60 * 60 * 24) if len(dates) > 1 else 1.0
                frequency = len(dates) / max(time_span, 1.0)
                freq_label = "daily" if frequency >= 1 else "weekly" if frequency >= 0.2 else "infrequent"

                # Peak hours: hours with most interactions
                hour_counts = {h: hours.count(h) for h in range(24)}
                peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                peak_hours = [h[0] for h in peak_hours if h[1] > 0]

                patterns["frequency"] = freq_label
                patterns["peak_hours"] = peak_hours
            except Exception as e:
                logger.error(f"Error analyzing interaction times for user {user_id}: {e}")
                patterns["frequency"] = "unknown"
                patterns["peak_hours"] = []
        else:
            patterns["frequency"] = "none"
            patterns["peak_hours"] = []

        # Average query length
        query_lengths = [len(interaction.get("query", "")) for interaction in interactions]
        patterns["average_query_length"] = sum(query_lengths) / len(query_lengths) if query_lengths else 0

        # Task completion rate (placeholder, will be updated with task data)
        ratings = [interaction.get("rating") for interaction in interactions if interaction.get("rating") is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            patterns["task_completion_rate"] = avg_rating / 5.0  # Normalize rating to 0-1 scale
        else:
            patterns["task_completion_rate"] = 0.0

        patterns["last_analysis"] = datetime.now().isoformat()
        self.user_context[user_id]["last_updated"] = datetime.now().isoformat()
        self.save_context()
        logger.debug(f"Analyzed interaction patterns for user {user_id}")
        return patterns

    def infer_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Infer user preferences based on historical data and interactions.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            Dict[str, Any]: Dictionary of inferred user preferences.
        """
        if user_id not in self.user_context:
            self.user_context[user_id] = {
                "last_updated": datetime.now().isoformat(),
                "interaction_patterns": {},
                "preferences": {},
                "current_state": {},
                "external_data": {}
            }

        preferences = self.user_context[user_id]["preferences"]
        interactions = self.memory_manager.get_user_interactions(user_id)

        if not interactions:
            preferences.update({
                "task_detail_level": "medium",
                "notification_frequency": "normal",
                "preferred_communication": "chat",
                "autonomy_level": "moderate",
                "last_updated": datetime.now().isoformat()
            })
            return preferences

        # Infer task detail level based on query length and feedback
        query_lengths = [len(interaction.get("query", "")) for interaction in interactions]
        avg_query_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0
        if avg_query_length > 100:
            preferences["task_detail_level"] = "high"
        elif avg_query_length < 30:
            preferences["task_detail_level"] = "low"
        else:
            preferences["task_detail_level"] = "medium"

        # Infer autonomy level based on feedback ratings
        ratings = [interaction.get("rating") for interaction in interactions if interaction.get("rating") is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating > 4.0:
                preferences["autonomy_level"] = "high"
            elif avg_rating < 2.5:
                preferences["autonomy_level"] = "low"
            else:
                preferences["autonomy_level"] = "moderate"
        else:
            preferences["autonomy_level"] = "moderate"

        # Placeholder for other preferences
        preferences["notification_frequency"] = "normal"
        preferences["preferred_communication"] = "chat"
        preferences["last_updated"] = datetime.now().isoformat()

        self.user_context[user_id]["last_updated"] = datetime.now().isoformat()
        self.save_context()
        logger.debug(f"Inferred preferences for user {user_id}")
        return preferences

    def get_relevant_context_for_planning(self, user_id: str, goal: str) -> Dict[str, Any]:
        """Extract relevant context for task planning based on a specific goal.

        Args:
            user_id (str): Unique identifier for the user.
            goal (str): The goal or task for which context is needed.

        Returns:
            Dict[str, Any]: Relevant context data for planning.
        """
        full_context = self.get_user_context(user_id)
        relevant_context = {
            "current_time": datetime.now().isoformat(),
            "user_state": full_context.get("current_state", {}),
            "preferences": full_context.get("preferences", {}),
            "goal_specific": {}
        }

        # Add goal-specific context
        goal_lower = goal.lower()
        if "meeting" in goal_lower or "schedule" in goal_lower:
            relevant_context["goal_specific"]["type"] = "scheduling"
            relevant_context["goal_specific"]["constraints"] = {
                "user_availability": self._infer_availability(user_id),
                "upcoming_events": full_context.get("current_state", {}).get("upcoming_events", [])
            }
        elif "research" in goal_lower or "learn" in goal_lower:
            relevant_context["goal_specific"]["type"] = "research"
            relevant_context["goal_specific"]["constraints"] = {
                "preferred_time": "peak_focus_hours",
                "focus_hours": full_context.get("interaction_patterns", {}).get("peak_hours", [9, 10, 11])
            }
        else:
            relevant_context["goal_specific"]["type"] = "general"
            relevant_context["goal_specific"]["constraints"] = {}

        logger.debug(f"Extracted relevant context for user {user_id} for goal: {goal[:50]}...")
        return relevant_context

    def _infer_availability(self, user_id: str) -> List[Dict[str, str]]:
        """Infer user availability based on current state and patterns.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            List[Dict[str, str]]: List of available time slots in ISO format.
        """
        context = self.get_user_context(user_id)
        current_state = context.get("current_state", {})
        patterns = context.get("interaction_patterns", {})

        # Default to peak hours if available
        peak_hours = patterns.get("peak_hours", [9, 10, 11])
        now = datetime.now()
        availability = []

        # Create availability slots for the next 3 days during peak hours
        for day_offset in range(3):
            target_date = now + timedelta(days=day_offset)
            for hour in peak_hours:
                slot_start = datetime(target_date.year, target_date.month, target_date.day, hour)
                slot_end = slot_start + timedelta(hours=1)
                availability.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat()
                })

        # If weekend, adjust availability (e.g., fewer slots)
        if current_state.get("is_weekend", False):
            availability = availability[:len(availability)//2]  # Reduce slots on weekends

        return availability[:5]  # Limit to 5 slots for simplicity
