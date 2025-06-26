"""Unit tests for Activity Tracking module."""

import os
import unittest
from unittest.mock import patch
from flask import Flask

from enterprise.activity_tracking_module import ActivityTracking

class TestActivityTracking(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_file = 'test_activity_logs.json'
        self.activity_tracking = ActivityTracking(self.app, self.test_data_file)
        self.activity_tracking.activities = []
        
    def tearDown(self):
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_log_activity(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1', {'status': 'success'})
        self.assertEqual(len(self.activity_tracking.activities), 1)
        activity = self.activity_tracking.activities[0]
        self.assertEqual(activity['user_id'], 'user1')
        self.assertEqual(activity['action'], 'create')
        self.assertEqual(activity['resource_id'], 'doc1')
        self.assertEqual(activity['details'], {'status': 'success'})
        self.assertTrue('timestamp' in activity)

    def test_get_user_activities(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1')
        self.activity_tracking.log_activity('user2', 'update', 'doc1')
        self.activity_tracking.log_activity('user1', 'delete', 'doc2')
        user_activities = self.activity_tracking.get_user_activities('user1')
        self.assertEqual(len(user_activities), 2)
        actions = [a['action'] for a in user_activities]
        self.assertIn('create', actions)
        self.assertIn('delete', actions)

    def test_get_user_activities_no_activities(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1')
        user_activities = self.activity_tracking.get_user_activities('user2')
        self.assertEqual(len(user_activities), 0)

    def test_get_resource_activities(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1')
        self.activity_tracking.log_activity('user2', 'update', 'doc1')
        self.activity_tracking.log_activity('user1', 'delete', 'doc2')
        resource_activities = self.activity_tracking.get_resource_activities('doc1')
        self.assertEqual(len(resource_activities), 2)
        users = [a['user_id'] for a in resource_activities]
        self.assertIn('user1', users)
        self.assertIn('user2', users)

    def test_get_resource_activities_no_activities(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1')
        resource_activities = self.activity_tracking.get_resource_activities('doc3')
        self.assertEqual(len(resource_activities), 0)

    def test_get_all_activities(self):
        self.activity_tracking.log_activity('user1', 'create', 'doc1')
        self.activity_tracking.log_activity('user2', 'update', 'doc1')
        self.activity_tracking.log_activity('user1', 'delete', 'doc2')
        all_activities = self.activity_tracking.get_all_activities()
        self.assertEqual(len(all_activities), 3)

if __name__ == '__main__':
    unittest.main()
