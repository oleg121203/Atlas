"""
Unit tests for Workflow Testing Framework Module
"""

import unittest
import random
from datetime import datetime, timedelta
from workflow_testing import WorkflowTestFramework, framework

from unittest.mock import Mock

class TestWorkflowTestFramework(unittest.TestCase):
    def setUp(self):
        self.framework = WorkflowTestFramework()

    def test_register_and_run_test_suite(self):
        # Create a simple test case
        class DummyTest(unittest.TestCase):
            def test_dummy(self):
                self.assertTrue(True)

        # Create and register suite
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(DummyTest))
        self.framework.register_test_suite('dummy_workflow', suite)

        # Run tests
        result = self.framework.run_tests('dummy_workflow', verbosity=0)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(self.framework.test_results['dummy_workflow'], result)

    def test_run_tests_nonexistent_workflow(self):
        with self.assertRaises(ValueError):
            self.framework.run_tests('nonexistent_workflow')

    def test_mock_dependency(self):
        mock_obj = self.framework.mock_dependency('some.module.function', return_value=42)
        self.assertEqual(mock_obj(), 42)
        self.assertIn('some.module.function', self.framework.mocked_dependencies)

    def test_register_and_generate_test_data(self):
        def custom_generator(**kwargs):
            return {'value': kwargs.get('value', 100)}

        self.framework.register_test_data_generator('custom_type', custom_generator)
        data = self.framework.generate_test_data('custom_type', value=200)
        self.assertEqual(data['value'], 200)

        data_list = self.framework.generate_test_data('custom_type', count=3, value=300)
        self.assertEqual(len(data_list), 3)
        self.assertEqual(data_list[0]['value'], 300)

    def test_generate_test_data_nonexistent_type(self):
        with self.assertRaises(ValueError):
            self.framework.generate_test_data('nonexistent_type')

    def test_record_and_get_coverage(self):
        self.framework.record_coverage('wf1', 'step1', 85.5)
        self.framework.record_coverage('wf1', 'step2', 92.0)
        coverage_report = self.framework.get_coverage_report('wf1')
        self.assertEqual(coverage_report['step1'], 85.5)
        self.assertEqual(coverage_report['step2'], 92.0)
        self.assertEqual(self.framework.get_coverage_report('wf2'), {})

    def test_generate_test_report_not_tested(self):
        report = self.framework.generate_test_report('untested_workflow')
        self.assertEqual(report['status'], 'Not Tested')
        self.assertEqual(report['tests_run'], 0)

    def test_default_data_generators(self):
        user_data = framework.generate_test_data('user')
        self.assertIn('user_id', user_data)
        self.assertIn('name', user_data)

        wf_data = framework.generate_test_data('workflow_execution')
        self.assertIn('workflow_id', wf_data)
        self.assertIn('duration', wf_data)
        self.assertGreater(wf_data['duration'], 0)

        feedback_data = framework.generate_test_data('feedback')
        self.assertIn('nps_score', feedback_data)
        self.assertGreaterEqual(feedback_data['nps_score'], 0)
        self.assertLessEqual(feedback_data['nps_score'], 10)

if __name__ == '__main__':
    unittest.main()
