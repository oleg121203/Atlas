"""
Workflow Testing Framework Module

This module provides a comprehensive framework for testing complex workflows,
including unit tests for individual steps, integration tests for entire workflows,
mock external dependencies, test data generation, and coverage analysis.
"""

import unittest
import random
import json
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

class WorkflowTestFramework:
    def __init__(self):
        self.test_suites: Dict[str, unittest.TestSuite] = {}
        self.test_results: Dict[str, unittest.TestResult] = {}
        self.mocked_dependencies: Dict[str, Mock] = {}
        self.test_data_generators: Dict[str, Callable] = {}
        self.coverage_data: Dict[str, Dict[str, float]] = {}

    def register_test_suite(self, workflow_id: str, test_suite: unittest.TestSuite):
        """
        Register a test suite for a specific workflow.
        """
        self.test_suites[workflow_id] = test_suite

    def run_tests(self, workflow_id: str, verbosity: int = 1) -> unittest.TestResult:
        """
        Run the test suite for a specific workflow and store the results.
        """
        if workflow_id not in self.test_suites:
            raise ValueError(f"No test suite registered for workflow {workflow_id}")

        result = unittest.TextTestRunner(verbosity=verbosity).run(self.test_suites[workflow_id])
        self.test_results[workflow_id] = result
        return result

    def mock_dependency(self, dependency_path: str, return_value: Any = None, side_effect: Optional[Callable] = None):
        """
        Create a mock for an external dependency.
        """
        mock_obj = Mock()
        if return_value is not None:
            mock_obj.return_value = return_value
        if side_effect is not None:
            mock_obj.side_effect = side_effect
        self.mocked_dependencies[dependency_path] = mock_obj
        return mock_obj

    def apply_mocks(self):
        """
        Apply all registered mocks to the testing environment.
        """
        for dependency_path, mock_obj in self.mocked_dependencies.items():
            patch(dependency_path, mock_obj).__enter__()

    def register_test_data_generator(self, data_type: str, generator_func: Callable):
        """
        Register a function to generate test data for a specific type.
        """
        self.test_data_generators[data_type] = generator_func

    def generate_test_data(self, data_type: str, count: int = 1, **kwargs) -> Any:
        """
        Generate test data using the registered generator for the specified type.
        """
        if data_type not in self.test_data_generators:
            raise ValueError(f"No test data generator registered for type {data_type}")
        if count == 1:
            return self.test_data_generators[data_type](**kwargs)
        return [self.test_data_generators[data_type](**kwargs) for _ in range(count)]

    def record_coverage(self, workflow_id: str, step_id: str, coverage_percentage: float):
        """
        Record test coverage data for a specific workflow step.
        """
        if workflow_id not in self.coverage_data:
            self.coverage_data[workflow_id] = {}
        self.coverage_data[workflow_id][step_id] = coverage_percentage

    def get_coverage_report(self, workflow_id: str) -> Dict[str, float]:
        """
        Get the test coverage report for a specific workflow.
        """
        return self.coverage_data.get(workflow_id, {})

    def generate_test_report(self, workflow_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive test report including results and coverage.
        """
        if workflow_id not in self.test_results:
            return {
                'workflow_id': workflow_id,
                'status': 'Not Tested',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'tests_skipped': 0,
                'coverage': {}
            }

        result = self.test_results[workflow_id]
        return {
            'workflow_id': workflow_id,
            'status': 'Pass' if result.wasSuccessful() else 'Fail',
            'tests_run': result.testsRun,
            'tests_passed': result.testsRun - len(result.failures) - len(result.errors),
            'tests_failed': len(result.failures),
            'tests_skipped': len(result.skipped),
            'coverage': self.get_coverage_report(workflow_id),
            'details': {
                'failures': [(str(test), msg) for test, msg in result.failures],
                'errors': [(str(test), msg) for test, msg in result.errors]
            }
        }

# Example usage and built-in test data generators
def generate_sample_user_data(**kwargs) -> Dict[str, Any]:
    """
    Generate sample user data for testing.
    """
    return {
        'user_id': kwargs.get('user_id', f"user_{random.randint(1000, 9999)}"),
        'name': kwargs.get('name', random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Eve'])),
        'role': kwargs.get('role', random.choice(['Admin', 'Editor', 'Viewer'])),
        'created_at': kwargs.get('created_at', datetime.now() - timedelta(days=random.randint(1, 365)))
    }

def generate_sample_workflow_execution(**kwargs) -> Dict[str, Any]:
    """
    Generate sample workflow execution data for testing.
    """
    start_time = kwargs.get('start_time', datetime.now() - timedelta(minutes=random.randint(10, 1000)))
    duration = kwargs.get('duration', random.randint(60, 600))
    end_time = kwargs.get('end_time', start_time + timedelta(seconds=duration))
    success = kwargs.get('success', random.random() < 0.85)
    return {
        'workflow_id': kwargs.get('workflow_id', f"wf_{random.randint(100, 999)}"),
        'execution_id': kwargs.get('execution_id', f"exec_{random.randint(1000, 9999)}"),
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'success': success,
        'error_message': '' if success else random.choice(['Timeout', 'ValidationError', 'ResourceLimit'])
    }

def generate_sample_feedback_data(**kwargs) -> Dict[str, Any]:
    """
    Generate sample user feedback data for testing.
    """
    return {
        'user_id': kwargs.get('user_id', f"user_{random.randint(1000, 9999)}"),
        'workflow_id': kwargs.get('workflow_id', f"wf_{random.randint(100, 999)}"),
        'nps_score': kwargs.get('nps_score', random.randint(0, 10)),
        'feedback_text': kwargs.get('feedback_text', random.choice([
            'Great experience!', 'Needs improvement.', 'Very efficient.', 'Too complicated.', 'Works well!'
        ])),
        'timestamp': kwargs.get('timestamp', datetime.now() - timedelta(minutes=random.randint(1, 1440)))
    }

# Initialize framework with default generators
framework = WorkflowTestFramework()
framework.register_test_data_generator('user', generate_sample_user_data)
framework.register_test_data_generator('workflow_execution', generate_sample_workflow_execution)
framework.register_test_data_generator('feedback', generate_sample_feedback_data)

if __name__ == '__main__':
    # Example test case for a workflow
    class SampleWorkflowTests(unittest.TestCase):
        def setUp(self):
            self.test_data = framework.generate_test_data('workflow_execution', count=5)

        def test_workflow_execution_success(self):
            successful_executions = [data for data in self.test_data if data['success']]
            self.assertTrue(len(successful_executions) > 0, "No successful executions in test data")

        def test_workflow_duration(self):
            for data in self.test_data:
                self.assertGreater(data['duration'], 0, "Duration should be positive")

    # Create and register test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SampleWorkflowTests))
    framework.register_test_suite('sample_workflow', suite)

    # Run tests
    result = framework.run_tests('sample_workflow', verbosity=2)
    report = framework.generate_test_report('sample_workflow')
    print("\nTest Report:")
    print(json.dumps(report, indent=2, default=str))
