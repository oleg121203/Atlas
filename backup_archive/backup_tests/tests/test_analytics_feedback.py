"""
Unit Tests for Analytics and Feedback Loops Module

This module contains tests for the MarketingAnalytics class, ensuring analytics functionalities work as expected.
"""

import os
import unittest

import pandas as pd
from modules.marketing.analytics_feedback import MarketingAnalytics


class TestMarketingAnalytics(unittest.TestCase):
    def setUp(self):
        self.analytics = MarketingAnalytics()
        self.data_file = self.analytics.data_file
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.analytics.campaigns = []
        self.analytics.conversion_data = []
        self.analytics.channel_metrics = {
            "Twitter": [],
            "Instagram": [],
            "LinkedIn": [],
            "Email": [],
            "Website": [],
        }
        self.analytics.save_data()

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_add_campaign(self):
        campaign = self.analytics.add_campaign(
            "TestCampaign", "2025-06-01", "2025-06-30", ["Twitter"]
        )
        self.assertEqual(len(self.analytics.campaigns), 1)
        self.assertEqual(campaign["name"], "TestCampaign")
        self.assertEqual(campaign["channels"], ["Twitter"])

    def test_record_conversion(self):
        campaign = self.analytics.add_campaign(
            "TestCampaign", "2025-06-01", "2025-06-30", ["Twitter"]
        )
        conversion = self.analytics.record_conversion(
            campaign["id"], "Twitter", "SignUp", 5
        )
        self.assertEqual(len(self.analytics.conversion_data), 1)
        self.assertEqual(conversion["campaign_id"], campaign["id"])
        self.assertEqual(conversion["channel"], "Twitter")
        self.assertEqual(conversion["type"], "SignUp")
        self.assertEqual(conversion["value"], 5)

    def test_update_channel_metrics(self):
        metric = self.analytics.update_channel_metrics("Twitter", 1000, 50, 5, 100.0)
        self.assertEqual(len(self.analytics.channel_metrics["Twitter"]), 1)
        self.assertEqual(metric["impressions"], 1000)
        self.assertEqual(metric["clicks"], 50)
        self.assertEqual(metric["conversions"], 5)
        self.assertEqual(metric["cost"], 100.0)

    def test_get_campaign_performance(self):
        campaign = self.analytics.add_campaign(
            "TestCampaign", "2025-06-01", "2025-06-30", ["Twitter", "Instagram"]
        )
        self.analytics.record_conversion(campaign["id"], "Twitter", "SignUp", 10)
        self.analytics.record_conversion(campaign["id"], "Instagram", "SignUp", 8)
        performance = self.analytics.get_campaign_performance(campaign["id"])
        self.assertIsInstance(performance, pd.DataFrame)
        self.assertEqual(performance.shape[0], 2)
        self.assertTrue((performance["channel"] == "Twitter").any())
        self.assertTrue((performance["channel"] == "Instagram").any())

    def test_get_channel_performance(self):
        self.analytics.update_channel_metrics("Twitter", 1000, 50, 5, 100.0)
        self.analytics.update_channel_metrics("Twitter", 2000, 100, 10, 180.0)
        performance = self.analytics.get_channel_performance("Twitter")
        self.assertIsInstance(performance, pd.DataFrame)
        self.assertEqual(performance.shape[0], 8)  # describe() returns 8 rows for stats
        self.assertIn("CTR", performance.columns)
        self.assertIn("CPC", performance.columns)
        self.assertIn("CPA", performance.columns)

    def test_recommend_strategy_adjustment(self):
        self.analytics.update_channel_metrics(
            "Twitter", 1000, 10, 2, 50.0
        )  # Low CTR, high CPC/CPA
        recommendations = self.analytics.recommend_strategy_adjustment(
            min_ctr=2.0, max_cpc=1.0, max_cpa=10.0
        )
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("Twitter" in rec for rec in recommendations))


if __name__ == "__main__":
    unittest.main()
