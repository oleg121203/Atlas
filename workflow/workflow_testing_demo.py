"""
Demo script for WorkflowTestFramework class

This script demonstrates the usage of WorkflowTestFramework with sample workflow test cases.
"""

import unittest
import random
from datetime import datetime, timedelta
from workflow_testing import WorkflowTestFramework, framework

from unittest.mock import Mock, patch

# Initialize test framework
wf_test_framework = WorkflowTestFramework()

# Define a more complex test suite for demonstration
def create_workflow_test_suite():
    """
    Create a comprehensive test suite for workflow testing.
    """
    class WorkflowStepTests(unittest.TestCase):
        def setUp(self):
            self.test_executions = framework.generate_test_data('workflow_execution', count=10)
            self.test_users = framework.generate_test_data('user', count=5)
            # Mock an external API call
            self.mock_api = wf_test_framework.mock_dependency(
                'external_api.service.get_data', 
                return_value={'status': 'success', 'data': [1, 2, 3]}
            )

        def test_step_execution_success_rate(self):
            success_count = len([exe for exe in self.test_executions if exe['success']])
            success_rate = success_count / len(self.test_executions)
            self.assertGreaterEqual(success_rate, 0.7, "Workflow success rate below 70%")

        def test_step_execution_duration(self):
            for exe in self.test_executions:
                self.assertGreater(exe['duration'], 0, "Duration must be positive")
                self.assertLess(exe['duration'], 1000, "Duration unreasonably high")

        def test_user_roles(self):
            valid_roles = ['Admin', 'Editor', 'Viewer']
            for user in self.test_users:
                self.assertIn(user['role'], valid_roles, f"Invalid role for user {user['user_id']}")

        def test_external_api_call(self):
            from external_api.service import get_data  # This would normally be a real import
            response = get_data()
            self.assertEqual(response['status'], 'success')
            self.assertEqual(len(response['data']), 3)
            self.mock_api.assert_called_once()

    class WorkflowIntegrationTests(unittest.TestCase):
        def setUp(self):
            self.test_feedback = framework.generate_test_data('feedback', count=20)

        def test_workflow_feedback_distribution(self):
            nps_scores = [fb['nps_score'] for fb in self.test_feedback]
            avg_nps = sum(nps_scores) / len(nps_scores)
            self.assertGreaterEqual(avg_nps, 5.0, "Average NPS score below acceptable threshold")

        def test_feedback_text_presence(self):
            with_text = len([fb for fb in self.test_feedback if fb['feedback_text']])
            self.assertGreater(with_text, 0, "No feedback entries have text content")

    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WorkflowStepTests))
    suite.addTest(unittest.makeSuite(WorkflowIntegrationTests))
    return suite

# Register the test suite
wf_test_framework.register_test_suite('complex_workflow', create_workflow_test_suite())

# Record some dummy coverage data for demonstration
wf_test_framework.record_coverage('complex_workflow', 'step_1_init', 92.5)
wf_test_framework.record_coverage('complex_workflow', 'step_2_process', 88.0)
wf_test_framework.record_coverage('complex_workflow', 'step_3_complete', 95.0)

if __name__ == "__main__":
    print("Running comprehensive workflow tests...")
    # Run the tests with detailed output
    result = wf_test_framework.run_tests('complex_workflow', verbosity=2)
    
    print("\nGenerating detailed test report...")
    report = wf_test_framework.generate_test_report('complex_workflow')
    
    print("\nTest Report Summary:")
    print(f"Workflow: {report['workflow_id']}")
    print(f"Status: {report['status']}")
    print(f"Tests Run: {report['tests_run']}")
    print(f"Tests Passed: {report['tests_passed']}")
    print(f"Tests Failed: {report['tests_failed']}")
    print(f"Tests Skipped: {report['tests_skipped']}")
    print("Coverage Report:")
    for step, coverage in report['coverage'].items():
        print(f"  {step}: {coverage}%")
    
    if report['tests_failed'] > 0:
        print("\nFailed Tests Details:")
        for test, message in report['details']['failures']:
            print(f"  Test: {test}")
            print(f"  Reason: {message[:100]}...")
    
    if report['details']['errors']:
        print("\nError Details:")
        for test, message in report['details']['errors']:
            print(f"  Test: {test}")
            print(f"  Error: {message[:100]}...")
