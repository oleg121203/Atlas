"""
Unit tests for User Satisfaction Monitoring System
"""

import unittest
from datetime import datetime, timedelta

from user.user_satisfaction import UserSatisfactionMonitor


class TestUserSatisfactionMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = UserSatisfactionMonitor()

    def test_collect_nps_score_valid(self):
        self.monitor.collect_nps_score("user1", "wf1", 9)
        self.assertEqual(len(self.monitor.feedback_data), 1)
        self.assertEqual(self.monitor.feedback_data.iloc[0]["nps_score"], 9)
        self.assertEqual(self.monitor.feedback_data.iloc[0]["user_id"], "user1")
        self.assertEqual(self.monitor.feedback_data.iloc[0]["workflow_id"], "wf1")

    def test_collect_nps_score_invalid(self):
        with self.assertRaises(ValueError):
            self.monitor.collect_nps_score("user1", "wf1", 11)
        with self.assertRaises(ValueError):
            self.monitor.collect_nps_score("user1", "wf1", -1)

    def test_collect_feedback(self):
        self.monitor.collect_feedback("user2", "wf2", "Great workflow, very helpful!")
        self.assertEqual(len(self.monitor.feedback_data), 1)
        self.assertEqual(self.monitor.feedback_data.iloc[0]["user_id"], "user2")
        self.assertEqual(self.monitor.feedback_data.iloc[0]["workflow_id"], "wf2")
        self.assertNotEqual(self.monitor.feedback_data.iloc[0]["sentiment"], 0.0)

    def test_get_current_nps(self):
        self.monitor.collect_nps_score("user1", "wf1", 9)  # Promoter
        self.monitor.collect_nps_score("user2", "wf1", 7)  # Passive
        self.monitor.collect_nps_score("user3", "wf1", 6)  # Detractor
        nps = self.monitor.get_current_nps()
        self.assertAlmostEqual(
            nps, 0.0
        )  # (1 promoter - 1 detractor) / 3 total * 100 = 0

    def test_get_nps_trend(self):
        self.monitor.collect_nps_score("user1", "wf1", 9)
        trend = self.monitor.get_nps_trend(days=7)
        self.assertEqual(len(trend), 1)
        self.assertTrue(
            trend["timestamp"].iloc[0] >= datetime.now() - timedelta(days=7)
        )

    def test_get_workflow_satisfaction(self):
        self.monitor.collect_nps_score("user1", "wf1", 9)
        self.monitor.collect_nps_score("user2", "wf1", 8)
        self.monitor.collect_feedback("user3", "wf1", "Good but could be faster")
        metrics = self.monitor.get_workflow_satisfaction("wf1")
        self.assertAlmostEqual(metrics["average_nps"], 8.5)
        self.assertNotEqual(metrics["average_sentiment"], 0)
        self.assertEqual(metrics["feedback_count"], 3)
        self.assertGreaterEqual(metrics["positive_feedback"], 0)
        self.assertGreaterEqual(metrics["negative_feedback"], 0)

    def test_get_workflow_satisfaction_empty(self):
        metrics = self.monitor.get_workflow_satisfaction("wf2")
        self.assertEqual(metrics["average_nps"], 0)
        self.assertEqual(metrics["average_sentiment"], 0)
        self.assertEqual(metrics["feedback_count"], 0)
        self.assertEqual(metrics["positive_feedback"], 0)
        self.assertEqual(metrics["negative_feedback"], 0)

    def test_detailed_feedback_analysis(self):
        self.monitor.collect_feedback(
            "user1", "wf1", "Great experience with this workflow"
        )
        self.monitor.collect_feedback(
            "user2", "wf1", "Terrible performance, needs improvement"
        )
        self.monitor.collect_feedback("user3", "wf1", "Okay, nothing special")
        analysis = self.monitor.get_detailed_feedback_analysis("wf1")
        self.assertEqual(analysis["total_feedback"], 3)
        self.assertGreater(analysis["positive_percentage"], 0)
        self.assertGreater(analysis["negative_percentage"], 0)
        self.assertGreater(analysis["neutral_percentage"], 0)
        self.assertTrue(isinstance(analysis["common_themes"], list))

    def test_detailed_feedback_analysis_empty(self):
        analysis = self.monitor.get_detailed_feedback_analysis("wf2")
        self.assertEqual(analysis["total_feedback"], 0)
        self.assertEqual(analysis["positive_percentage"], 0)
        self.assertEqual(analysis["negative_percentage"], 0)
        self.assertEqual(analysis["neutral_percentage"], 0)
        self.assertEqual(analysis["common_themes"], [])


if __name__ == "__main__":
    unittest.main()
