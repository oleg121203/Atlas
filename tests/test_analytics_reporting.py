"""
Unit Tests for Enterprise Analytics and Reporting Module
"""

import unittest
import os
import pandas as pd
from datetime import datetime, timedelta

from enterprise.analytics_reporting import AnalyticsReporting

class TestAnalyticsReporting(unittest.TestCase):
    def setUp(self):
        """
        Set up test cases.
        """
        self.analytics = AnalyticsReporting("test_data_source")
        self.start_date = datetime.now() - timedelta(days=7)
        self.end_date = datetime.now()

    def test_collect_usage_data(self):
        """
        Test collecting usage data.
        """
        usage_data = self.analytics.collect_usage_data(self.start_date, self.end_date)
        self.assertIsInstance(usage_data, pd.DataFrame)
        self.assertFalse(usage_data.empty)
        self.assertIn('timestamp', usage_data.columns)
        self.assertIn('user_count', usage_data.columns)
        self.assertIn('action_count', usage_data.columns)
        self.assertIn('login_count', usage_data.columns)
        self.assertIn('document_edits', usage_data.columns)
        self.assertIn('task_updates', usage_data.columns)

    def test_aggregate_data(self):
        """
        Test aggregating data by different frequencies.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        agg_data_daily = self.analytics.aggregate_data(frequency='D')
        self.assertIsInstance(agg_data_daily, pd.DataFrame)
        self.assertFalse(agg_data_daily.empty)
        self.assertIn('user_count', agg_data_daily.columns)

        agg_data_weekly = self.analytics.aggregate_data(frequency='W')
        self.assertIsInstance(agg_data_weekly, pd.DataFrame)
        self.assertFalse(agg_data_weekly.empty)
        self.assertTrue(len(agg_data_weekly) <= len(agg_data_daily))

    def test_generate_dashboard(self):
        """
        Test generating a customizable dashboard.
        """
        config = {"title": "Test Dashboard", "metrics": ["user_count", "action_count", "login_count"]}
        dashboard_path = self.analytics.generate_dashboard(config)
        self.assertTrue(os.path.exists(dashboard_path))
        with open(dashboard_path, 'r') as f:
            content = f.read()
            self.assertIn("Test Dashboard", content)
            self.assertIn("user_count", content)
            self.assertIn("action_count", content)
            self.assertIn("login_count", content)
        os.remove(dashboard_path)  # Clean up after test

    def test_generate_interactive_dashboard(self):
        """
        Test generating an interactive dashboard.
        """
        config = {"title": "Interactive Dashboard", "metrics": ["user_count", "action_count"], "interactive": True}
        dashboard_path = self.analytics.generate_dashboard(config)
        self.assertTrue(os.path.exists(dashboard_path))
        with open(dashboard_path, 'r') as f:
            content = f.read()
            self.assertIn("Interactive Dashboard", content)
            self.assertIn("interactive", content)
            self.assertIn("alert", content)
        os.remove(dashboard_path)  # Clean up after test

    def test_export_report_csv(self):
        """
        Test exporting report in CSV format.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        report_path = self.analytics.export_report(format='csv')
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('.csv'))
        os.remove(report_path)  # Clean up after test

    def test_export_report_pdf(self):
        """
        Test exporting report in PDF format.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        report_path = self.analytics.export_report(format='pdf')
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('.pdf'))
        os.remove(report_path)  # Clean up after test

    def test_visualize_data_line(self):
        """
        Test visualizing data with line plot.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        plot_path = self.analytics.visualize_data(plot_type='line', metrics=['user_count', 'action_count', 'login_count'])
        self.assertTrue(os.path.exists(plot_path))
        self.assertTrue(plot_path.endswith('.png'))
        os.remove(plot_path)  # Clean up after test

    def test_visualize_data_bar(self):
        """
        Test visualizing data with bar plot.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        plot_path = self.analytics.visualize_data(plot_type='bar', metrics=['user_count', 'document_edits'])
        self.assertTrue(os.path.exists(plot_path))
        self.assertTrue(plot_path.endswith('.png'))
        os.remove(plot_path)  # Clean up after test

    def test_visualize_data_area(self):
        """
        Test visualizing data with area plot.
        """
        self.analytics.collect_usage_data(self.start_date, self.end_date)
        plot_path = self.analytics.visualize_data(plot_type='area', metrics=['action_count', 'task_updates'])
        self.assertTrue(os.path.exists(plot_path))
        self.assertTrue(plot_path.endswith('.png'))
        os.remove(plot_path)  # Clean up after test

    def test_export_report_no_data(self):
        """
        Test exporting report with no data.
        """
        result = self.analytics.export_report()
        self.assertEqual(result, "No data to export.")

    def test_visualize_data_no_data(self):
        """
        Test visualizing data with no data.
        """
        result = self.analytics.visualize_data()
        self.assertEqual(result, "No data to visualize.")

if __name__ == '__main__':
    unittest.main()
