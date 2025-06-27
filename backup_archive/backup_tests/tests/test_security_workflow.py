"""End-to-end test for the SecurityAgent's blocking and notification workflow."""

import multiprocessing
import os

# Add project root to path to allow direct imports
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.agents.security_agent import SecurityAgent

from utils.logger import LOG_FILE_PATH


class TestSecurityWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up the SecurityAgent process and communication pipe for each test."""
        # Clean up log file before test
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        self.security_agent = SecurityAgent(self.child_conn)
        self.security_agent.start()
        # Allow time for the process to start
        time.sleep(0.5)

    def tearDown(self):
        """Clean up by stopping the SecurityAgent process."""
        self.security_agent.stop()
        self.security_agent.join(timeout=1)
        if self.security_agent.is_alive():
            self.security_agent.terminate()  # Force terminate if it doesn't stop gracefully
        self.parent_conn.close()
        self.child_conn.close()
        # Clean up log file after test
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

    def test_block_malicious_goal_and_notify(self):
        """Verify that a malicious goal is blocked and a notification is triggered."""
        # 1. Send rule and notification settings to the agent
        rules = ["DENY, goal, rm -rf"]
        notification_channels = {"email": True, "telegram": False, "sms": False}

        self.parent_conn.send({"type": "UPDATE_RULES", "details": {"rules": rules}})
        self.parent_conn.send(
            {
                "type": "UPDATE_NOTIFICATION_SETTINGS",
                "details": {"channels": notification_channels},
            }
        )

        # 2. Send a malicious goal
        malicious_goal = "Use the terminal to delete all files with rm -rf /"
        event = {"type": "GOAL_EXECUTION_REQUEST", "details": {"goal": malicious_goal}}

        self.parent_conn.send(event)

        # 3. Wait for and check the response
        self.assertTrue(
            self.parent_conn.poll(timeout=2), "Agent did not respond in time."
        )
        response = self.parent_conn.recv()

        # 4. Assert the action was blocked
        self.assertEqual(response.get("action"), "BLOCK")
        self.assertIn("Execution blocked by rule: 'rm -rf'", response.get("reason", ""))

        # 5. Assert that the notification was logged
        # Give the logger time to flush
        time.sleep(0.2)
        with open(LOG_FILE_PATH) as f:
            log_content = f.read()

        self.assertIn("SIMULATING EMAIL NOTIFICATION", log_content)
        self.assertIn("Reason: Execution blocked by rule: 'rm -rf'", log_content)

    def test_allow_safe_goal(self):
        """Verify that a safe goal is allowed to proceed."""
        # 1. Send a safe goal
        safe_goal = "Use the terminal to list files with ls"
        event = {"type": "GOAL_EXECUTION_REQUEST", "details": {"goal": safe_goal}}
        self.parent_conn.send(event)

        # 2. Wait for and check the response
        self.assertTrue(
            self.parent_conn.poll(timeout=2), "Agent did not respond in time."
        )
        response = self.parent_conn.recv()

        # 3. Assert the action was allowed
        self.assertEqual(response.get("action"), "ALLOW")

    def test_performance_of_security_check(self):
        """Measures the latency of the security check to ensure it's performant."""
        num_requests = 100
        event = {"type": "GOAL_EXECUTION_REQUEST", "details": {"goal": "A safe goal"}}

        start_time = time.perf_counter()

        for _ in range(num_requests):
            self.parent_conn.send(event)
            # Wait for the response to ensure we're measuring the round trip
            self.assertTrue(
                self.parent_conn.poll(timeout=1), "Agent did not respond in time."
            )
            self.parent_conn.recv()

        end_time = time.perf_counter()

        total_duration = end_time - start_time
        avg_latency = total_duration / num_requests

        print(
            f"\nAverage security check latency: {avg_latency * 1000:.2f} ms over {num_requests} requests."
        )
        self.assertLess(
            avg_latency, 0.1, "Security check latency is above the 100ms threshold."
        )


if __name__ == "__main__":
    unittest.main()
