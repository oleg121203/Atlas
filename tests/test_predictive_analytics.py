"""
Unit Tests for Predictive Analytics Module
"""

import unittest
import os
import pandas as pd
from datetime import datetime, timedelta

from advanced_analytics.predictive_analytics import PredictiveAnalytics

class TestPredictiveAnalytics(unittest.TestCase):
    def setUp(self):
        """
        Set up test cases.
        """
        self.analytics = PredictiveAnalytics("test_data_source")
        self.start_date = datetime.now() - timedelta(days=7)
        self.end_date = datetime.now()

    def test_load_data(self):
        """
        Test loading data for predictive modeling.
        """
        data = self.analytics.load_data(self.start_date, self.end_date)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('timestamp', data.columns)
        self.assertIn('user_id', data.columns)
        self.assertIn('action_type', data.columns)
        self.assertIn('time_spent', data.columns)
        self.assertIn('will_return', data.columns)

    def test_preprocess_data(self):
        """
        Test preprocessing data for model training.
        """
        self.analytics.load_data(self.start_date, self.end_date)
        processed_data = self.analytics.preprocess_data()
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertFalse(processed_data.empty)
        self.assertIn('hour', processed_data.columns)
        self.assertIn('day_of_week', processed_data.columns)
        # Check if action_type is converted to numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_data['action_type']))

    def test_train_model(self):
        """
        Test training a predictive model.
        """
        self.analytics.load_data(self.start_date, self.end_date)
        self.analytics.preprocess_data()
        accuracy = self.analytics.train_model()
        self.assertGreater(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

    def test_predict_user_behavior(self):
        """
        Test predicting user behavior.
        """
        self.analytics.load_data(self.start_date, self.end_date)
        self.analytics.preprocess_data()
        self.analytics.train_model()
        user_data = {
            'user_id': 1,
            'action_type': 0,  # Assuming 0 is 'login' after preprocessing
            'time_spent': 300.0,
            'hour': 14,
            'day_of_week': 2
        }
        probability = self.analytics.predict_user_behavior(user_data)
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_predict_user_behavior_no_model(self):
        """
        Test predicting user behavior without a trained model.
        """
        user_data = {
            'user_id': 1,
            'action_type': 0,
            'time_spent': 300.0,
            'hour': 14,
            'day_of_week': 2
        }
        probability = self.analytics.predict_user_behavior(user_data)
        self.assertEqual(probability, 0.0)

if __name__ == '__main__':
    unittest.main()
