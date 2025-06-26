"""Unit tests for Conflict Resolution module."""

import os
import unittest
from unittest.mock import patch
from flask import Flask

from enterprise.conflict_resolution import ConflictResolution

class TestConflictResolution(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_file = 'test_conflict_data.json'
        self.conflict_resolution = ConflictResolution(self.app, self.test_data_file)
        self.conflict_resolution.conflicts = {}
        
    def tearDown(self):
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_log_conflict(self):
        conflict = self.conflict_resolution.log_conflict('doc1', 'user1', 'User1 edit', 'Base content')
        self.assertEqual(conflict['user_id'], 'user1')
        self.assertEqual(conflict['conflicting_content'], 'User1 edit')
        self.assertEqual(conflict['base_content'], 'Base content')
        self.assertFalse(conflict['resolved'])
        self.assertIsNone(conflict['resolution'])
        self.assertTrue('timestamp' in conflict)
        self.assertIn('doc1', self.conflict_resolution.conflicts)
        self.assertEqual(len(self.conflict_resolution.conflicts['doc1']), 1)

    def test_get_conflicts(self):
        self.conflict_resolution.log_conflict('doc1', 'user1', 'User1 edit', 'Base content')
        self.conflict_resolution.log_conflict('doc1', 'user2', 'User2 edit', 'Base content')
        conflicts = self.conflict_resolution.get_conflicts('doc1')
        self.assertEqual(len(conflicts), 2)
        users = [c['user_id'] for c in conflicts]
        self.assertIn('user1', users)
        self.assertIn('user2', users)

    def test_get_conflicts_empty(self):
        conflicts = self.conflict_resolution.get_conflicts('doc2')
        self.assertEqual(len(conflicts), 0)

    def test_resolve_conflict_success(self):
        self.conflict_resolution.log_conflict('doc1', 'user1', 'User1 edit', 'Base content')
        result = self.conflict_resolution.resolve_conflict('doc1', 0, 'Merged content', 'user2')
        self.assertTrue(result)
        conflict = self.conflict_resolution.conflicts['doc1'][0]
        self.assertTrue(conflict['resolved'])
        self.assertEqual(conflict['resolution'], 'Merged content')
        self.assertEqual(conflict['resolved_by'], 'user2')
        self.assertTrue('resolved_at' in conflict)

    def test_resolve_conflict_not_found(self):
        result = self.conflict_resolution.resolve_conflict('doc1', 0, 'Merged content', 'user2')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
