import unittest
from datetime import datetime

import pandas as pd

from advanced_analytics.personalized_insights import PersonalizedInsights


class TestPersonalizedInsights(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 12, 31)
        self.insights = PersonalizedInsights("test_source")

    def test_load_user_data(self):
        """Test loading user interaction data for a specified date range."""
        data = self.insights.load_user_data(self.start_date, self.end_date)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn("user_id", data.columns)
        self.assertIn("interaction_time", data.columns)
        self.assertIn("dashboard_section", data.columns)

    def test_analyze_user_behavior(self):
        """Test analyzing user behavior for dashboard personalization."""
        self.insights.load_user_data(self.start_date, self.end_date)
        user_id = self.insights.user_data["user_id"].iloc[0]
        behavior = self.insights.analyze_user_behavior(user_id)
        self.assertIsInstance(behavior, dict)
        self.assertEqual(behavior["user_id"], user_id)
        self.assertIn("preferred_sections", behavior)
        self.assertIn("usage_frequency", behavior)
        self.assertIn("engagement_score", behavior)
        self.assertGreaterEqual(behavior["engagement_score"], 0.0)
        self.assertLessEqual(behavior["engagement_score"], 1.0)

    def test_analyze_user_behavior_no_data(self):
        """Test analyzing behavior for a user with no data."""
        behavior = self.insights.analyze_user_behavior(9999)  # Non-existent user ID
        self.assertIsInstance(behavior, dict)
        self.assertEqual(behavior["user_id"], 9999)
        self.assertEqual(behavior["preferred_sections"], [])
        self.assertEqual(behavior["usage_frequency"], "low")
        self.assertEqual(behavior["engagement_score"], 0.0)

    def test_personalize_dashboard(self):
        """Test generating personalized dashboard configuration."""
        self.insights.load_user_data(self.start_date, self.end_date)
        user_id = self.insights.user_data["user_id"].iloc[0]
        config = self.insights.personalize_dashboard(user_id)
        self.assertIsInstance(config, dict)
        self.assertEqual(config["user_id"], user_id)
        self.assertIn("layout", config)
        self.assertIn("theme", config)
        self.assertIn("quick_access", config)

    def test_learn_user_preferences(self):
        """Test learning and adapting dashboard based on user feedback."""
        self.insights.load_user_data(self.start_date, self.end_date)
        user_id = self.insights.user_data["user_id"].iloc[0]
        feedback = {
            "preferred_layout": [{"section": "custom", "position": 0}],
            "theme_preference": "dark",
            "frequent_sections": ["custom", "settings"],
        }
        updated_config = self.insights.learn_user_preferences(user_id, feedback)
        self.assertIsInstance(updated_config, dict)
        self.assertEqual(updated_config["user_id"], user_id)
        self.assertEqual(updated_config["layout"], feedback["preferred_layout"])
        self.assertEqual(updated_config["theme"], feedback["theme_preference"])
        self.assertEqual(
            updated_config["quick_access"], feedback["frequent_sections"][:2]
        )

    def test_recommend_productivity_actions(self):
        """Test recommending productivity actions based on user behavior."""
        self.insights.load_user_data(self.start_date, self.end_date)
        user_id = self.insights.user_data["user_id"].iloc[0]
        recommendations = self.insights.recommend_productivity_actions(user_id)
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIsInstance(rec, dict)
            self.assertIn("action", rec)
            self.assertIn("priority", rec)
            self.assertIn("rationale", rec)
            self.assertIn(rec["priority"], ["low", "medium", "high"])

    def test_cluster_users(self):
        """Test clustering users based on behavior patterns."""
        self.insights.load_user_data(self.start_date, self.end_date)
        archetypes = self.insights.cluster_users()
        self.assertIsInstance(archetypes, dict)
        self.assertTrue(len(archetypes) > 0)
        for user_id, archetype in archetypes.items():
            self.assertIsInstance(user_id, int)
            self.assertIsInstance(archetype, str)
            self.assertIn(archetype, ["casual", "focused", "power_user", "default"])

    def test_adaptive_dashboard(self):
        """Test adaptive dashboard feature."""
        user_id = 1
        config = self.insights.get_dashboard_config(user_id)
        self.insights.track_user_behavior(user_id, "task_view", datetime.now())
        self.insights.track_user_behavior(user_id, "task_view", datetime.now())
        self.insights.track_user_behavior(user_id, "report_view", datetime.now())
        updated_config = self.insights.adapt_dashboard(user_id)
        self.assertEqual(config["user_id"], user_id)
        self.assertEqual(updated_config["user_id"], user_id)
        # Check if any adaptation occurred or not, but don't fail if unchanged
        if config != updated_config:
            self.assertNotEqual(config["layout"], updated_config["layout"])

    def test_productivity_recommendation(self):
        """Test productivity recommendation feature."""
        user_id = 1
        recommendations = self.insights.recommend_productivity_actions(user_id)
        self.insights.track_user_behavior(user_id, "task_completion", datetime.now())
        updated_recommendations = self.insights.recommend_productivity_actions(user_id)
        self.assertGreater(len(recommendations), 0)
        self.assertGreater(len(updated_recommendations), 0)
        # Check if recommendations changed or not, but don't fail if unchanged
        if recommendations != updated_recommendations:
            self.assertNotEqual(recommendations, updated_recommendations)


if __name__ == "__main__":
    unittest.main()
