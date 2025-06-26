"""Unit tests for Workspace Sharing module."""

import os
import unittest
from unittest.mock import patch
from flask import Flask

from enterprise.workspace_sharing import WorkspaceSharing

class TestWorkspaceSharing(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_file = 'test_workspace_data.json'
        self.workspace_sharing = WorkspaceSharing(self.app, self.test_data_file)
        self.workspace_sharing.workspaces = {}
        
    def tearDown(self):
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_create_workspace_success(self):
        result = self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.assertTrue(result)
        self.assertIn('ws1', self.workspace_sharing.workspaces)
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['name'], 'Test Workspace')
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['owner_id'], 'user1')
        self.assertIn('user1', self.workspace_sharing.workspaces['ws1']['members'])
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['members']['user1'], 'owner')

    def test_create_workspace_duplicate(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.create_workspace('ws1', 'Duplicate Workspace', 'user2')
        self.assertFalse(result)
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['name'], 'Test Workspace')
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['owner_id'], 'user1')

    def test_add_member_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.add_member('ws1', 'user2', 'editor')
        self.assertTrue(result)
        self.assertIn('user2', self.workspace_sharing.workspaces['ws1']['members'])
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['members']['user2'], 'editor')

    def test_add_member_workspace_not_found(self):
        result = self.workspace_sharing.add_member('ws2', 'user2', 'editor')
        self.assertFalse(result)

    def test_remove_member_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.workspace_sharing.add_member('ws1', 'user2', 'editor')
        result = self.workspace_sharing.remove_member('ws1', 'user2')
        self.assertTrue(result)
        self.assertNotIn('user2', self.workspace_sharing.workspaces['ws1']['members'])

    def test_remove_member_owner(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.remove_member('ws1', 'user1')
        self.assertFalse(result)
        self.assertIn('user1', self.workspace_sharing.workspaces['ws1']['members'])

    def test_remove_member_not_found(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.remove_member('ws1', 'user3')
        self.assertFalse(result)

    def test_update_member_role_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.workspace_sharing.add_member('ws1', 'user2', 'editor')
        result = self.workspace_sharing.update_member_role('ws1', 'user2', 'manager')
        self.assertTrue(result)
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['members']['user2'], 'manager')

    def test_update_member_role_owner(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.update_member_role('ws1', 'user1', 'editor')
        self.assertFalse(result)
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['members']['user1'], 'owner')

    def test_update_member_role_not_found(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        result = self.workspace_sharing.update_member_role('ws1', 'user3', 'editor')
        self.assertFalse(result)

    def test_add_resource_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        permissions = {
            'owner': ['read', 'write', 'delete'],
            'editor': ['read', 'write'],
            'member': ['read']
        }
        result = self.workspace_sharing.add_resource('ws1', 'res1', 'document', permissions)
        self.assertTrue(result)
        self.assertIn('res1', self.workspace_sharing.workspaces['ws1']['resources'])
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['resources']['res1']['type'], 'document')
        self.assertEqual(self.workspace_sharing.workspaces['ws1']['resources']['res1']['permissions'], permissions)

    def test_add_resource_workspace_not_found(self):
        permissions = {
            'owner': ['read', 'write', 'delete']
        }
        result = self.workspace_sharing.add_resource('ws2', 'res1', 'document', permissions)
        self.assertFalse(result)

    def test_check_access_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.workspace_sharing.add_member('ws1', 'user2', 'editor')
        permissions = {
            'owner': ['read', 'write', 'delete'],
            'editor': ['read', 'write'],
            'member': ['read']
        }
        self.workspace_sharing.add_resource('ws1', 'res1', 'document', permissions)
        self.assertTrue(self.workspace_sharing.check_access('ws1', 'user2', 'res1', 'read'))
        self.assertTrue(self.workspace_sharing.check_access('ws1', 'user2', 'res1', 'write'))
        self.assertFalse(self.workspace_sharing.check_access('ws1', 'user2', 'res1', 'delete'))

    def test_check_access_no_permission(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.workspace_sharing.add_member('ws1', 'user2', 'member')
        permissions = {
            'owner': ['read', 'write', 'delete'],
            'editor': ['read', 'write'],
            'member': ['read']
        }
        self.workspace_sharing.add_resource('ws1', 'res1', 'document', permissions)
        self.assertFalse(self.workspace_sharing.check_access('ws1', 'user2', 'res1', 'write'))

    def test_check_access_user_not_member(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        permissions = {
            'owner': ['read', 'write', 'delete']
        }
        self.workspace_sharing.add_resource('ws1', 'res1', 'document', permissions)
        self.assertFalse(self.workspace_sharing.check_access('ws1', 'user3', 'res1', 'read'))

    def test_check_access_resource_not_found(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        self.assertFalse(self.workspace_sharing.check_access('ws1', 'user1', 'res2', 'read'))

    def test_get_workspace_success(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace', 'user1')
        workspace = self.workspace_sharing.get_workspace('ws1')
        self.assertIsNotNone(workspace)
        self.assertEqual(workspace['name'], 'Test Workspace')

    def test_get_workspace_not_found(self):
        workspace = self.workspace_sharing.get_workspace('ws2')
        self.assertIsNone(workspace)

    def test_get_user_workspaces(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace 1', 'user1')
        self.workspace_sharing.create_workspace('ws2', 'Test Workspace 2', 'user2')
        self.workspace_sharing.add_member('ws2', 'user1', 'editor')
        user_workspaces = self.workspace_sharing.get_user_workspaces('user1')
        self.assertEqual(len(user_workspaces), 2)
        workspace_ids = [w['id'] for w in user_workspaces]
        self.assertIn('ws1', workspace_ids)
        self.assertIn('ws2', workspace_ids)
        for w in user_workspaces:
            if w['id'] == 'ws1':
                self.assertEqual(w['role'], 'owner')
            elif w['id'] == 'ws2':
                self.assertEqual(w['role'], 'editor')

    def test_get_user_workspaces_no_membership(self):
        self.workspace_sharing.create_workspace('ws1', 'Test Workspace 1', 'user1')
        user_workspaces = self.workspace_sharing.get_user_workspaces('user2')
        self.assertEqual(len(user_workspaces), 0)

if __name__ == '__main__':
    unittest.main()
