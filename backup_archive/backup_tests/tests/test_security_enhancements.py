"""Unit tests for Security Enhancements module."""

import os
import unittest

from flask import Flask

from enterprise.security_enhancements import SecurityEnhancements


class TestSecurityEnhancements(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.key_file = "test_encryption_key.key"
        self.audit_file = "test_audit_logs.json"
        self.security = SecurityEnhancements(self.app, self.key_file, self.audit_file)
        self.security.audit_logs = {}
        self.security.mfa_secrets = {}

    def tearDown(self):
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
        if os.path.exists(self.audit_file):
            os.remove(self.audit_file)

    def test_encrypt_and_decrypt_data(self):
        original_data = "Sensitive information"
        encrypted = self.security.encrypt_data(original_data)
        decrypted = self.security.decrypt_data(encrypted)
        self.assertEqual(decrypted, original_data)
        self.assertNotEqual(encrypted, original_data.encode())

    def test_hash_and_check_password(self):
        password = "MySecurePass123"
        hashed = self.security.hash_password(password)
        self.assertTrue(self.security.check_password(password, hashed))
        self.assertFalse(self.security.check_password("WrongPass", hashed))

    def test_setup_and_verify_mfa(self):
        user_id = "test_user"
        secret = "mfa_secret_code"
        self.assertTrue(self.security.setup_mfa(user_id, secret))
        self.assertFalse(
            self.security.setup_mfa(user_id, "another_secret")
        )  # Already setup
        self.assertTrue(self.security.verify_mfa(user_id, secret))
        self.assertFalse(self.security.verify_mfa(user_id, "wrong_code"))
        self.assertFalse(self.security.verify_mfa("unknown_user", secret))

    def test_log_and_get_audit_event(self):
        user_id = "test_user"
        event_type = "login"
        details = {"ip_address": "127.0.0.1", "device": "desktop"}

        self.security.log_audit_event(user_id, event_type, details)
        logs = self.security.get_audit_logs(user_id=user_id)
        self.assertIn(user_id, logs)
        self.assertEqual(len(logs[user_id]), 1)
        self.assertEqual(logs[user_id][0]["event_type"], event_type)
        self.assertEqual(logs[user_id][0]["details"], details)
        self.assertTrue("timestamp" in logs[user_id][0])

    def test_get_audit_logs_filtered_by_event_type(self):
        user_id = "test_user"
        self.security.log_audit_event(user_id, "login", {"ip": "127.0.0.1"})
        self.security.log_audit_event(user_id, "logout", {"ip": "127.0.0.1"})

        login_logs = self.security.get_audit_logs(user_id=user_id, event_type="login")
        self.assertIn(user_id, login_logs)
        self.assertEqual(len(login_logs[user_id]), 1)
        self.assertEqual(login_logs[user_id][0]["event_type"], "login")

        logout_logs = self.security.get_audit_logs(event_type="logout")
        self.assertIn(user_id, logout_logs)
        self.assertEqual(len(logout_logs[user_id]), 1)
        self.assertEqual(logout_logs[user_id][0]["event_type"], "logout")

    def test_get_audit_logs_empty(self):
        logs = self.security.get_audit_logs(user_id="nonexistent")
        self.assertIn("nonexistent", logs)
        self.assertEqual(len(logs["nonexistent"]), 0)


if __name__ == "__main__":
    unittest.main()
