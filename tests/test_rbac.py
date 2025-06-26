"""Unit tests for Role-Based Access Control (RBAC) module."""

import os
import unittest
from unittest.mock import patch
from flask import Flask

from enterprise.rbac import RBACManager

class TestRBACManager(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_policy_file = 'test_rbac_policies.json'
        self.rbac_manager = RBACManager(self.app, self.test_policy_file)
        self.rbac_manager.policies = {}
        
    def tearDown(self):
        if os.path.exists(self.test_policy_file):
            os.remove(self.test_policy_file)

    def test_check_permission_admin(self):
        self.assertTrue(self.rbac_manager.check_permission('admin', 'read'))
        self.assertTrue(self.rbac_manager.check_permission('admin', 'write'))
        self.assertTrue(self.rbac_manager.check_permission('admin', 'delete'))
        self.assertTrue(self.rbac_manager.check_permission('admin', 'manage_users'))
        self.assertTrue(self.rbac_manager.check_permission('admin', 'manage_roles'))

    def test_check_permission_user(self):
        self.assertTrue(self.rbac_manager.check_permission('user', 'read'))
        self.assertTrue(self.rbac_manager.check_permission('user', 'write'))
        self.assertFalse(self.rbac_manager.check_permission('user', 'delete'))
        self.assertFalse(self.rbac_manager.check_permission('user', 'manage_users'))

    def test_check_permission_guest(self):
        self.assertTrue(self.rbac_manager.check_permission('guest', 'read'))
        self.assertFalse(self.rbac_manager.check_permission('guest', 'write'))
        self.assertFalse(self.rbac_manager.check_permission('guest', 'delete'))

    def test_add_role_success(self):
        result = self.rbac_manager.add_role('tester', {'test', 'read'})
        self.assertTrue(result)
        self.assertIn('tester', self.rbac_manager.roles)
        self.assertEqual(self.rbac_manager.roles['tester']['permissions'], {'test', 'read'})

    def test_add_role_duplicate(self):
        result = self.rbac_manager.add_role('user', {'read', 'write'})
        self.assertFalse(result)
        self.assertEqual(self.rbac_manager.roles['user']['permissions'], {'read', 'write'})

    def test_update_role_permissions_success(self):
        result = self.rbac_manager.update_role_permissions('user', {'read', 'comment'})
        self.assertTrue(result)
        self.assertEqual(self.rbac_manager.roles['user']['permissions'], {'read', 'comment'})

    def test_update_role_permissions_nonexistent(self):
        result = self.rbac_manager.update_role_permissions('nonexistent', {'read'})
        self.assertFalse(result)
        self.assertNotIn('nonexistent', self.rbac_manager.roles)

    def test_add_policy(self):
        self.rbac_manager.add_policy('user123', 'project1', ['read', 'write'])
        self.assertIn('user123', self.rbac_manager.policies)
        self.assertIn('project1', self.rbac_manager.policies['user123'])
        self.assertEqual(self.rbac_manager.policies['user123']['project1'], ['read', 'write'])

    def test_check_policy_with_permission(self):
        self.rbac_manager.add_policy('user123', 'project1', ['read', 'write'])
        self.assertTrue(self.rbac_manager.check_policy('user123', 'project1', 'read'))
        self.assertTrue(self.rbac_manager.check_policy('user123', 'project1', 'write'))
        self.assertFalse(self.rbac_manager.check_policy('user123', 'project1', 'delete'))

    def test_check_policy_without_permission(self):
        self.rbac_manager.add_policy('user123', 'project1', ['read'])
        self.assertFalse(self.rbac_manager.check_policy('user123', 'project1', 'write'))

    def test_remove_policy_success(self):
        self.rbac_manager.add_policy('user123', 'project1', ['read', 'write'])
        result = self.rbac_manager.remove_policy('user123', 'project1')
        self.assertTrue(result)
        self.assertNotIn('project1', self.rbac_manager.policies.get('user123', {}))

    def test_remove_policy_nonexistent(self):
        result = self.rbac_manager.remove_policy('user123', 'nonexistent')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
