"""
Onboarding Analytics Module for Atlas.
This module tracks user interactions during onboarding to identify drop-off points and improve the process.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class OnboardingAnalytics:
    """
    A class to track and analyze user behavior during the onboarding process.
    """

    def __init__(self, analytics_file: str = "onboarding_analytics.json"):
        """
        Initialize the OnboardingAnalytics with a file to store data.

        Args:
            analytics_file (str): Path to the JSON file for storing analytics data.
        """
        self.analytics_file = analytics_file
        self.current_session = {}
        self.load_existing_data()

    def load_existing_data(self) -> None:
        """
        Load existing analytics data from the file if it exists.
        """
        self.data = []
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, "r") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading analytics data: {e}")
                self.data = []

    def save_data(self) -> None:
        """
        Save the current analytics data to the file.
        """
        try:
            with open(self.analytics_file, "w") as f:
                json.dump(self.data, f, indent=2)
            print(f"Analytics data saved to {self.analytics_file}")
        except IOError as e:
            print(f"Error saving analytics data: {e}")

    def start_session(self, user_id: str) -> None:
        """
        Start a new onboarding session for a user.

        Args:
            user_id (str): Unique identifier for the user.
        """
        self.current_session = {
            "user_id": user_id,
            "start_time": datetime.now().isoformat(),
            "steps": [],
        }
        print(f"Started onboarding session for user {user_id}")

    def track_step(
        self,
        step_name: str,
        completed: bool = True,
        duration: Optional[float] = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Track a specific step in the onboarding process.

        Args:
            step_name (str): Name of the onboarding step.
            completed (bool): Whether the step was completed successfully.
            duration (float, optional): Time taken to complete the step in seconds.
            error (str, optional): Error message if the step failed.
        """
        if not self.current_session:
            return

        step_data = {
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "completed": completed,
            "duration": duration if duration is not None else 0.0,
            "error": error if error else "",
        }
        self.current_session["steps"].append(step_data)
        print(f"Tracked step {step_name} for user {self.current_session['user_id']}")

    def end_session(self, completed_onboarding: bool = True) -> None:
        """
        End the current onboarding session and save the data.

        Args:
            completed_onboarding (bool): Whether the user completed the entire onboarding process.
        """
        if not self.current_session:
            return

        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["completed_onboarding"] = completed_onboarding
        self.data.append(self.current_session)
        self.save_data()
        print(
            f"Ended onboarding session for user {self.current_session['user_id']}, completed: {completed_onboarding}"
        )
        self.current_session = {}

    def analyze_drop_off(self) -> Dict[str, Any]:
        """
        Analyze the analytics data to identify where users drop off during onboarding.

        Returns:
            Dict[str, Any]: Analysis results including drop-off points and completion rates.
        """
        if not self.data:
            return {"error": "No data available for analysis"}

        total_sessions = len(self.data)
        completed_sessions = sum(
            1 for session in self.data if session.get("completed_onboarding", False)
        )
        completion_rate = (
            (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        )

        # Track drop-off by step
        drop_off_points = {}
        for session in self.data:
            if not session.get("completed_onboarding", False):
                last_step = (
                    session["steps"][-1]["step_name"] if session["steps"] else "Start"
                )
                drop_off_points[last_step] = drop_off_points.get(last_step, 0) + 1

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate_percent": completion_rate,
            "drop_off_points": drop_off_points,
        }


# Example usage
if __name__ == "__main__":
    analytics = OnboardingAnalytics()

    # Simulate a user session
    analytics.start_session("user123")
    analytics.track_step("Welcome", completed=True, duration=10.5)
    analytics.track_step("Account Setup", completed=True, duration=30.2)
    analytics.track_step(
        "Feature Tour", completed=False, duration=15.0, error="User closed window"
    )
    analytics.end_session(completed_onboarding=False)

    # Analyze data
    analysis = analytics.analyze_drop_off()
    print("Onboarding Drop-Off Analysis:")
    print(f"Total Sessions: {analysis['total_sessions']}")
    print(f"Completed Sessions: {analysis['completed_sessions']}")
    print(f"Completion Rate: {analysis['completion_rate_percent']:.2f}%")
    print("Drop-Off Points:")
    for step, count in analysis["drop_off_points"].items():
        print(f"  - {step}: {count} users")
