"""
Unit Tests for Workflow Security

This module tests the functionality of the WorkflowSecurity class,
including access control, encryption, and audit logging.
"""

import unittest
import os
import json
from datetime import datetime, timedelta
from workflow.security import AccessControl, EncryptionManager, AuditLogger, WorkflowSecurity

class TestAccessControl(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.access_control = AccessControl()
        self.user_id = "test_user"

    def test_default_roles(self):
        """Test default roles and permissions."""
        self.access_control.assign_role(self.user_id, "admin")
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_start"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_stop"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_edit"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_view"))

        self.access_control.assign_role(self.user_id, "editor")
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_start"))
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_stop"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_edit"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_view"))

        self.access_control.assign_role(self.user_id, "viewer")
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_start"))
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_stop"))
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_edit"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_view"))

    def test_unknown_user(self):
        """Test permission check for unknown user."""
        self.assertFalse(self.access_control.check_permission("unknown_user", "can_start"))

    def test_add_role(self):
        """Test adding a new role with custom permissions."""
        new_role = "manager"
        permissions = {"can_start": True, "can_stop": True, "can_edit": False, "can_view": True}
        self.access_control.add_role(new_role, permissions)
        self.access_control.assign_role(self.user_id, new_role)
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_start"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_stop"))
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_edit"))
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_view"))

    def test_update_role_permissions(self):
        """Test updating permissions for an existing role."""
        self.access_control.assign_role(self.user_id, "editor")
        self.assertFalse(self.access_control.check_permission(self.user_id, "can_stop"))
        updated_permissions = {"can_start": True, "can_stop": True, "can_edit": True, "can_view": True}
        self.access_control.update_role_permissions("editor", updated_permissions)
        self.assertTrue(self.access_control.check_permission(self.user_id, "can_stop"))

    def test_assign_unknown_role(self):
        """Test assigning an unknown role raises ValueError."""
        with self.assertRaises(ValueError):
            self.access_control.assign_role(self.user_id, "unknown_role")

class TestEncryptionManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.key = b'test_key_32_bytes_long_1234567890'
        self.encryption = EncryptionManager(self.key)
        self.test_data = "sensitive data"

    def test_encrypt_decrypt_data(self):
        """Test encrypting and decrypting data."""
        encrypted = self.encryption.encrypt_data(self.test_data)
        decrypted = self.encryption.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.test_data)

    def test_hash_sensitive_data(self):
        """Test hashing sensitive data."""
        hash1 = self.encryption.hash_sensitive_data(self.test_data)
        hash2 = self.encryption.hash_sensitive_data(self.test_data)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, self.test_data)

    def test_hmac_generation_verification(self):
        """Test generating and verifying HMAC for data integrity."""
        hmac_sig = self.encryption.generate_hmac(self.test_data)
        self.assertTrue(self.encryption.verify_hmac(self.test_data, hmac_sig))
        self.assertFalse(self.encryption.verify_hmac("different data", hmac_sig))

class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.log_file = "test_audit_log.json"
        self.audit_logger = AuditLogger(self.log_file)
        self.user_id = "test_user"
        self.event_type = "workflow_start"
        self.details = {"workflow_id": "wf_123"}

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_event(self):
        """Test logging an event and retrieving it."""
        self.audit_logger.log_event(self.event_type, self.user_id, self.details)
        logs = self.audit_logger.get_logs(event_type=self.event_type)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['event_type'], self.event_type)
        self.assertEqual(logs[0]['user_id'], self.user_id)
        self.assertEqual(logs[0]['details'], self.details)

    def test_filter_logs(self):
        """Test filtering logs by event type and user ID."""
        self.audit_logger.log_event("workflow_start", "user1", {"workflow_id": "wf_1"})
        self.audit_logger.log_event("workflow_stop", "user1", {"workflow_id": "wf_1"})
        self.audit_logger.log_event("workflow_start", "user2", {"workflow_id": "wf_2"})

        logs_start = self.audit_logger.get_logs(event_type="workflow_start")
        self.assertEqual(len(logs_start), 2)

        logs_user1 = self.audit_logger.get_logs(user_id="user1")
        self.assertEqual(len(logs_user1), 2)

        logs_start_user1 = self.audit_logger.get_logs(event_type="workflow_start", user_id="user1")
        self.assertEqual(len(logs_start_user1), 1)

    def test_clear_old_logs(self):
        """Test clearing logs older than a specified number of days."""
        # Simulate old logs by manually setting timestamps
        current_time = datetime.now()
        old_log = {
            'timestamp': (current_time - timedelta(days=10)).isoformat(),
            'event_type': 'old_event',
            'user_id': 'user1',
            'details': {}
        }
        recent_log = {
            'timestamp': current_time.isoformat(),
            'event_type': 'recent_event',
            'user_id': 'user2',
            'details': {}
        }
        self.audit_logger.logs = [old_log, recent_log]
        self.audit_logger.save_logs()

        self.audit_logger.clear_old_logs(days_old=5)
        logs = self.audit_logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['event_type'], 'recent_event')

class TestWorkflowSecurity(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.access_control = AccessControl()
        self.encryption = EncryptionManager()
        self.audit_logger = AuditLogger("test_security_audit_log.json")
        self.security = WorkflowSecurity(self.access_control, self.encryption, self.audit_logger)
        self.user_id = "test_user"

    def tearDown(self):
        """Clean up test environment after each test."""
        log_file = "test_security_audit_log.json"
        if os.path.exists(log_file):
            os.remove(log_file)

    def test_secure_workflow_action_success(self):
        """Test executing a workflow action with proper permissions."""
        self.access_control.assign_role(self.user_id, "admin")
        action_result = "Action completed"
        result = self.security.secure_workflow_action(self.user_id, "can_start", lambda: action_result)
        self.assertEqual(result, action_result)

        logs = self.audit_logger.get_logs(event_type="action_can_start_success", user_id=self.user_id)
        self.assertEqual(len(logs), 1)

    def test_secure_workflow_action_access_denied(self):
        """Test executing a workflow action without proper permissions."""
        self.access_control.assign_role(self.user_id, "viewer")
        with self.assertRaises(PermissionError):
            self.security.secure_workflow_action(self.user_id, "can_start", lambda: "Action completed")

        logs = self.audit_logger.get_logs(event_type="access_denied_can_start", user_id=self.user_id)
        self.assertEqual(len(logs), 1)

    def test_secure_workflow_action_with_encryption(self):
        """Test executing a workflow action with sensitive data encryption."""
        self.access_control.assign_role(self.user_id, "admin")
        sensitive_data = "sensitive info"
        action_result = "Action completed"
        result = self.security.secure_workflow_action(self.user_id, "can_start", lambda: action_result, sensitive_data)
        self.assertEqual(result, action_result)

        logs_encrypted = self.audit_logger.get_logs(event_type="data_encrypted", user_id=self.user_id)
        self.assertEqual(len(logs_encrypted), 1)
        logs_success = self.audit_logger.get_logs(event_type="action_can_start_success", user_id=self.user_id)
        self.assertEqual(len(logs_success), 1)

    def test_secure_workflow_action_failure(self):
        """Test executing a workflow action that fails with an exception."""
        self.access_control.assign_role(self.user_id, "admin")
        def failing_action():
            raise ValueError("Action failed")
        with self.assertRaises(ValueError):
            self.security.secure_workflow_action(self.user_id, "can_start", failing_action)

        logs_failed = self.audit_logger.get_logs(event_type="action_can_start_failed", user_id=self.user_id)
        self.assertEqual(len(logs_failed), 1)

if __name__ == '__main__':
    unittest.main()
