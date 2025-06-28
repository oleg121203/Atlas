"""
Tests for the OnboardingAnalytics class in analytics/onboarding_analytics.py
"""

import json
import os

import pytest

from analytics.onboarding_analytics import OnboardingAnalytics


@pytest.fixture
def analytics_file(tmp_path):
    """Create a temporary file for analytics data."""
    return str(tmp_path / "test_analytics.json")


@pytest.fixture
def analytics(analytics_file):
    """Create an instance of OnboardingAnalytics for testing."""
    return OnboardingAnalytics(analytics_file=analytics_file)


def test_initialize(analytics):
    """Test that the initialize method sets up the data structure."""
    # Reset data to test initialization
    analytics.data = None

    # Call initialize
    analytics.initialize()

    # Verify data is now an empty list
    assert analytics.data == []


def test_start_session(analytics):
    """Test starting a new session."""
    user_id = "test_user_123"
    analytics.start_session(user_id)

    # Check that current_session is properly initialized
    assert analytics.current_session["user_id"] == user_id
    assert "start_time" in analytics.current_session
    assert analytics.current_session["steps"] == []


def test_track_step(analytics):
    """Test tracking a step in the onboarding process."""
    # Setup session
    analytics.start_session("test_user_123")

    # Track a step
    analytics.track_step("Welcome Screen", completed=True, duration=10.5)

    # Verify the step was tracked
    assert len(analytics.current_session["steps"]) == 1
    step = analytics.current_session["steps"][0]
    assert step["step_name"] == "Welcome Screen"
    assert step["completed"] is True
    assert step["duration"] == 10.5
    assert step["error"] == ""


def test_track_step_with_error(analytics):
    """Test tracking a step that fails."""
    # Setup session
    analytics.start_session("test_user_123")

    # Track a failed step
    error_msg = "User closed the app"
    analytics.track_step("Feature Tour", completed=False, error=error_msg)

    # Verify the step was tracked with error
    assert len(analytics.current_session["steps"]) == 1
    step = analytics.current_session["steps"][0]
    assert step["step_name"] == "Feature Tour"
    assert step["completed"] is False
    assert step["error"] == error_msg


def test_end_session(analytics):
    """Test ending a session."""
    # Setup session with steps
    analytics.start_session("test_user_123")
    analytics.track_step("Welcome", completed=True)

    # End session
    analytics.end_session(completed_onboarding=True)

    # Verify session was ended and saved
    assert analytics.current_session == {}
    assert len(analytics.data) == 1
    saved_session = analytics.data[0]
    assert saved_session["user_id"] == "test_user_123"
    assert saved_session["completed_onboarding"] is True
    assert "end_time" in saved_session

    # Verify file was saved
    assert os.path.exists(analytics.analytics_file)
    with open(analytics.analytics_file, "r") as f:
        loaded_data = json.load(f)
    assert len(loaded_data) == 1


def test_analyze_drop_off(analytics):
    """Test analyzing drop-off points."""
    # Add multiple sessions with different outcomes
    analytics.data = []

    # Completed session
    analytics.data.append(
        {
            "user_id": "user1",
            "completed_onboarding": True,
            "steps": [
                {"step_name": "Welcome", "completed": True},
                {"step_name": "Setup", "completed": True},
            ],
        }
    )

    # Dropped at Setup step
    analytics.data.append(
        {
            "user_id": "user2",
            "completed_onboarding": False,
            "steps": [
                {"step_name": "Welcome", "completed": True},
                {"step_name": "Setup", "completed": False},
            ],
        }
    )

    # Dropped at Tutorial step
    analytics.data.append(
        {
            "user_id": "user3",
            "completed_onboarding": False,
            "steps": [
                {"step_name": "Welcome", "completed": True},
                {"step_name": "Setup", "completed": True},
                {"step_name": "Tutorial", "completed": False},
            ],
        }
    )

    # Run analysis
    results = analytics.analyze_drop_off()

    # Verify analysis results
    assert results["total_sessions"] == 3
    assert results["completed_sessions"] == 1
    assert results["completion_rate_percent"] == pytest.approx(33.33, 0.01)
    assert "Setup" in results["drop_off_points"]
    assert "Tutorial" in results["drop_off_points"]
    assert results["drop_off_points"]["Setup"] == 1
    assert results["drop_off_points"]["Tutorial"] == 1


def test_load_existing_data(analytics, analytics_file):
    """Test loading existing analytics data."""
    # Create test data
    test_data = [{"user_id": "test1", "completed_onboarding": True, "steps": []}]

    # Write test data to file
    with open(analytics_file, "w") as f:
        json.dump(test_data, f)

    # Create new instance to load data
    new_analytics = OnboardingAnalytics(analytics_file=analytics_file)

    # Verify data was loaded
    assert len(new_analytics.data) == 1
    assert new_analytics.data[0]["user_id"] == "test1"


def test_no_session_tracking(analytics):
    """Test tracking when no session is active."""
    # Attempt to track without an active session
    analytics.track_step("Welcome")

    # Verify nothing happened (no exception)
    assert True


def test_no_session_ending(analytics):
    """Test ending when no session is active."""
    # Attempt to end without an active session
    analytics.end_session()

    # Verify nothing happened (no exception)
    assert True


def test_load_nonexistent_file(analytics):
    """Test loading from a nonexistent file."""
    # Point to nonexistent file
    analytics.analytics_file = "nonexistent_file.json"

    # Load data (should initialize empty)
    analytics.load_existing_data()

    # Verify data is empty
    assert analytics.data == []
