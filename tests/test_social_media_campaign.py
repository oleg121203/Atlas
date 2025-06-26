"""
Unit Tests for Social Media Campaign Module

This module contains tests for the SocialMediaCampaign class, ensuring that campaign management functionalities
work as expected.
"""

import unittest
import os
import pandas as pd
from datetime import datetime, timedelta
from modules.marketing.social_media_campaign import SocialMediaCampaign

class TestSocialMediaCampaign(unittest.TestCase):
    def setUp(self):
        self.campaign = SocialMediaCampaign("TestCampaign")
        # Clear any existing data file for a clean test environment
        self.data_file = self.campaign.data_file
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.campaign.content_plan = []
        self.campaign.scheduled_posts = []
        self.campaign.engagement_metrics = {'Twitter': [], 'Instagram': [], 'LinkedIn': []}
        self.campaign.save_data()

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_add_content_to_plan(self):
        content = self.campaign.add_content_to_plan("Test Content", ['Twitter'], "Test Visual")
        self.assertEqual(len(self.campaign.content_plan), 1)
        self.assertEqual(content['idea'], "Test Content")
        self.assertEqual(content['platforms'], ['Twitter'])
        self.assertEqual(content['visual_description'], "Test Visual")
        self.assertEqual(content['status'], "Draft")

    def test_schedule_post(self):
        self.campaign.add_content_to_plan("Test Content", ['Twitter'])
        post_time = datetime.now() + timedelta(days=1)
        scheduled_post = self.campaign.schedule_post(0, post_time, ['Twitter'])
        self.assertEqual(len(self.campaign.scheduled_posts), 1)
        self.assertEqual(scheduled_post['content_index'], 0)
        self.assertEqual(scheduled_post['platforms'], ['Twitter'])
        self.assertEqual(scheduled_post['status'], "Scheduled")
        self.assertEqual(self.campaign.content_plan[0]['status'], "Scheduled")

    def test_simulate_posting(self):
        self.campaign.add_content_to_plan("Test Content", ['Twitter'])
        post_time = datetime.now() + timedelta(hours=1)
        self.campaign.schedule_post(0, post_time)
        post = self.campaign.simulate_posting(0)
        self.assertEqual(post['status'], "Posted")
        self.assertEqual(self.campaign.content_plan[0]['status'], "Posted")
        self.assertEqual(len(self.campaign.engagement_metrics['Twitter']), 1)
        self.assertEqual(len(self.campaign.engagement_metrics['Instagram']), 0)
        self.assertEqual(len(self.campaign.engagement_metrics['LinkedIn']), 0)

    def test_get_engagement_report_single_platform(self):
        self.campaign.add_content_to_plan("Test Content", ['Twitter'])
        self.campaign.schedule_post(0)
        self.campaign.simulate_posting(0)
        report = self.campaign.get_engagement_report('Twitter')
        self.assertIsInstance(report, pd.DataFrame)
        self.assertEqual(report.shape[0], 1)
        self.assertIn('likes', report.columns)
        self.assertIn('shares', report.columns)
        self.assertIn('comments', report.columns)
        self.assertIn('reach', report.columns)

    def test_get_engagement_report_all_platforms(self):
        self.campaign.add_content_to_plan("Test Content", ['Twitter', 'Instagram'])
        self.campaign.schedule_post(0)
        self.campaign.simulate_posting(0)
        report = self.campaign.get_engagement_report()
        self.assertIsInstance(report, dict)
        self.assertIn('Twitter', report)
        self.assertIn('Instagram', report)
        self.assertIn('LinkedIn', report)
        self.assertIsInstance(report['Twitter'], pd.DataFrame)
        self.assertIsInstance(report['Instagram'], pd.DataFrame)

    def test_get_scheduled_posts_upcoming_only(self):
        self.campaign.add_content_to_plan("Test Content", ['Twitter'])
        post_time_future = datetime.now() + timedelta(days=1)
        post_time_past = datetime.now() - timedelta(days=1)
        self.campaign.schedule_post(0, post_time_future)
        self.campaign.schedule_post(0, post_time_past)
        upcoming_posts = self.campaign.get_scheduled_posts(upcoming_only=True)
        self.assertEqual(len(upcoming_posts), 1)
        self.assertGreater(upcoming_posts[0]['post_time'], datetime.now().isoformat())

    def test_get_content_plan_by_status(self):
        self.campaign.add_content_to_plan("Draft Content", ['Twitter'])
        self.campaign.add_content_to_plan("Scheduled Content", ['Twitter'])
        self.campaign.schedule_post(1)
        draft_content = self.campaign.get_content_plan(status="Draft")
        scheduled_content = self.campaign.get_content_plan(status="Scheduled")
        self.assertEqual(len(draft_content), 1)
        self.assertEqual(len(scheduled_content), 1)
        self.assertEqual(draft_content[0]['status'], "Draft")
        self.assertEqual(scheduled_content[0]['status'], "Scheduled")

if __name__ == '__main__':
    unittest.main()
