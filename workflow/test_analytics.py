"""
Unit Tests for Workflow Analytics

This module tests the functionality of the WorkflowAnalytics class,
including monitoring, performance metrics, and optimization suggestions.
"""

import unittest
import time
from datetime import datetime, timedelta
import os
from workflow.analytics import WorkflowAnalytics

class TestWorkflowAnalytics(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.db_path = "test_workflow_analytics.db"
        self.analytics = WorkflowAnalytics(self.db_path)
        self.execution_id = "test_execution_1"
        self.workflow_id = "test_workflow_1"

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_start_and_end_execution(self):
        """Test starting and ending a workflow execution."""
        self.analytics.start_execution(self.execution_id, self.workflow_id)
        time.sleep(1)  # Simulate some duration
        self.analytics.end_execution(self.execution_id, "completed", "All actions successful")
        
        performance_data = self.analytics.get_workflow_performance(self.workflow_id)
        self.assertEqual(len(performance_data), 1)
        self.assertEqual(performance_data[0]['execution_id'], self.execution_id)
        self.assertEqual(performance_data[0]['status'], "completed")
        self.assertGreater(performance_data[0]['duration_seconds'], 0.0)

    def test_record_action(self):
        """Test recording individual action executions within a workflow."""
        self.analytics.start_execution(self.execution_id, self.workflow_id)
        start_time = datetime.now()
        time.sleep(0.5)
        end_time = datetime.now()
        self.analytics.record_action(self.execution_id, "action1", start_time, end_time, "success")
        self.analytics.end_execution(self.execution_id, "completed")
        
        action_data = self.analytics.get_action_performance(self.execution_id)
        self.assertEqual(len(action_data), 1)
        self.assertEqual(action_data[0]['action_name'], "action1")
        self.assertEqual(action_data[0]['status'], "success")
        self.assertGreater(action_data[0]['duration_seconds'], 0)

    def test_record_failed_action(self):
        """Test recording a failed action within a workflow."""
        self.analytics.start_execution(self.execution_id, self.workflow_id)
        start_time = datetime.now()
        time.sleep(0.5)
        end_time = datetime.now()
        self.analytics.record_action(self.execution_id, "action1", start_time, end_time, "failed", "Timeout error")
        self.analytics.end_execution(self.execution_id, "failed", "Workflow failed due to action timeout")
        
        action_data = self.analytics.get_action_performance(self.execution_id)
        self.assertEqual(len(action_data), 1)
        self.assertEqual(action_data[0]['action_name'], "action1")
        self.assertEqual(action_data[0]['status'], "failed")
        self.assertEqual(action_data[0]['error_message'], "Timeout error")
        
        performance_data = self.analytics.get_workflow_performance(self.workflow_id)
        self.assertEqual(performance_data[0]['failed_actions_count'], 1)

    def test_analyze_failures(self):
        """Test failure analysis for a workflow with multiple failed executions."""
        for i in range(3):
            exec_id = f"test_execution_{i+1}"
            self.analytics.start_execution(exec_id, self.workflow_id)
            start_time = datetime.now()
            time.sleep(0.1)
            end_time = datetime.now()
            error_msg = "Connection timeout"
            self.analytics.record_action(exec_id, "connect_action", start_time, end_time, "failed", error_msg)
            self.analytics.end_execution(exec_id, "failed", f"Failed due to {error_msg}")
        
        analysis = self.analytics.analyze_failures(self.workflow_id)
        self.assertEqual(analysis['total_failed_executions'], 3)
        self.assertGreaterEqual(len(analysis['failed_actions']), 1)
        self.assertEqual(analysis['failed_actions'][0]['action_name'], "connect_action")
        self.assertEqual(analysis['failed_actions'][0]['count'], 3)
        self.assertGreaterEqual(len(analysis['recommendations']), 1)
        self.assertTrue(any("timeout" in rec for rec in analysis['recommendations']))

    def test_optimize_workflow(self):
        """Test optimization suggestions for a workflow based on performance data."""
        # Simulate multiple successful executions with varying action durations
        for i in range(3):
            exec_id = f"test_execution_{i+1}"
            self.analytics.start_execution(exec_id, self.workflow_id)
            start_time = datetime.now()
            time.sleep(0.5)  # Long-running action
            end_time = datetime.now()
            self.analytics.record_action(exec_id, "long_action", start_time, end_time, "success")
            start_time = datetime.now()
            time.sleep(0.1)  # Short action
            end_time = datetime.now()
            self.analytics.record_action(exec_id, "short_action", start_time, end_time, "success")
            self.analytics.end_execution(exec_id, "completed")
        
        suggestions = self.analytics.optimize_workflow(self.workflow_id)
        self.assertGreaterEqual(len(suggestions['bottlenecks']), 1)
        self.assertTrue(any("long_action" in bottleneck for bottleneck in suggestions['bottlenecks']))
        self.assertGreaterEqual(len(suggestions['parallelization_opportunities']), 1)
        self.assertTrue(any("long_action" in opportunity for opportunity in suggestions['parallelization_opportunities']))

if __name__ == '__main__':
    unittest.main()
