"""Unit tests for User Management module."""

import os
import unittest

import jwt
from flask import Flask

from enterprise.user_management import UserManager


class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_file = "test_user_data.json"
        self.user_manager = UserManager(self.app, self.test_data_file)
        self.user_manager.users = {}

    def tearDown(self):
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_create_user_success(self):
        result = self.user_manager.create_user(
            "testuser", "password123", "test@example.com", "user"
        )
        self.assertTrue(result)
        self.assertIn("testuser", self.user_manager.users)
        self.assertEqual(
            self.user_manager.users["testuser"]["email"], "test@example.com"
        )
        self.assertEqual(self.user_manager.users["testuser"]["role"], "user")
        self.assertNotEqual(
            self.user_manager.users["testuser"]["password"], "password123"
        )  # Should be hashed

    def test_create_user_duplicate(self):
        self.user_manager.create_user("testuser", "password123", "test@example.com")
        result = self.user_manager.create_user(
            "testuser", "password456", "test2@example.com"
        )
        self.assertFalse(result)
        self.assertEqual(
            self.user_manager.users["testuser"]["email"], "test@example.com"
        )  # Original unchanged

    def test_authenticate_user_success(self):
        self.user_manager.create_user("testuser", "password123", "test@example.com")
        token = self.user_manager.authenticate_user("testuser", "password123")
        self.assertIsNotNone(token)
        decoded = jwt.decode(token, self.user_manager.secret_key, algorithms=["HS256"])
        self.assertEqual(decoded["user"], "testuser")
        self.assertEqual(decoded["role"], "user")
        self.assertIsNotNone(self.user_manager.users["testuser"]["last_login"])

    def test_authenticate_user_wrong_password(self):
        self.user_manager.create_user("testuser", "password123", "test@example.com")
        token = self.user_manager.authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(token)

    def test_authenticate_user_nonexistent(self):
        token = self.user_manager.authenticate_user("nonexistent", "password123")
        self.assertIsNone(token)

    def test_get_user(self):
        self.user_manager.create_user(
            "testuser", "password123", "test@example.com", "admin"
        )
        user = self.user_manager.get_user("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "admin")
        self.assertEqual(user["email"], "test@example.com")

    def test_update_user_role(self):
        self.user_manager.create_user(
            "testuser", "password123", "test@example.com", "user"
        )
        result = self.user_manager.update_user_role("testuser", "admin")
        self.assertTrue(result)
        self.assertEqual(self.user_manager.users["testuser"]["role"], "admin")

    def test_delete_user(self):
        self.user_manager.create_user("testuser", "password123", "test@example.com")
        result = self.user_manager.delete_user("testuser")
        self.assertTrue(result)
        self.assertNotIn("testuser", self.user_manager.users)

    def test_get_all_users(self):
        self.user_manager.create_user("user1", "pass1", "user1@example.com", "user")
        self.user_manager.create_user("user2", "pass2", "user2@example.com", "admin")
        users = self.user_manager.get_all_users()
        self.assertEqual(len(users), 2)
        self.assertTrue(
            all("password" not in user for user in users)
        )  # Passwords should be excluded

    def test_register_endpoint_success(self):
        with self.app.test_client() as client:
            response = client.post(
                "/api/users/register",
                json={
                    "username": "newuser",
                    "password": "password123",
                    "email": "newuser@example.com",
                    "role": "user",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("newuser", self.user_manager.users)

    def test_login_endpoint_success(self):
        self.user_manager.create_user("testuser", "password123", "test@example.com")
        with self.app.test_client() as client:
            response = client.post(
                "/api/users/login",
                json={"username": "testuser", "password": "password123"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("token", response.get_json())

    def test_get_users_endpoint_admin_access(self):
        self.user_manager.create_user(
            "adminuser", "password123", "admin@example.com", "admin"
        )
        token = self.user_manager.authenticate_user("adminuser", "password123")
        with self.app.test_client() as client:
            response = client.get(
                "/api/users", headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.get_json(), list)


if __name__ == "__main__":
    unittest.main()
