"""
Unit tests for Workflow Execution Analytics Module
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from workflow.workflow_analytics import WorkflowAnalytics

class TestWorkflowAnalytics(unittest.TestCase):
    def setUp(self):
        self.analytics = WorkflowAnalytics()
        self.start_time = datetime.now() - timedelta(minutes=10)
        self.end_time = datetime.now() - timedelta(minutes=5)
        self.steps = [
            {'step_id': 'step1', 'step_name': 'First Step', 'start_time': self.start_time, 
             'end_time': self.start_time + timedelta(minutes=2), 'success': True},
            {'step_id': 'step2', 'step_name': 'Second Step', 'start_time': self.start_time + timedelta(minutes=2), 
             'end_time': self.end_time, 'success': True}
        ]

    def test_record_execution_success(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, True, '', self.steps)
        self.assertEqual(len(self.analytics.execution_data), 1)
        self.assertEqual(self.analytics.execution_data.iloc[0]['workflow_id'], 'wf1')
        self.assertEqual(self.analytics.execution_data.iloc[0]['success'], True)
        self.assertEqual(len(self.analytics.step_data), 2)
        self.assertEqual(self.analytics.step_data.iloc[0]['step_id'], 'step1')

    def test_record_execution_failure(self):
        self.analytics.record_execution('wf1', 'exec2', self.start_time, self.end_time, False, 'Timeout error')
        self.assertEqual(len(self.analytics.execution_data), 1)
        self.assertEqual(self.analytics.execution_data.iloc[0]['success'], False)
        self.assertEqual(self.analytics.execution_data.iloc[0]['error_message'], 'Timeout error')

    def test_get_performance_metrics(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, True, '', self.steps)
        self.analytics.record_execution('wf1', 'exec2', self.start_time - timedelta(hours=1), 
                                       self.end_time - timedelta(hours=1), False, 'Error')
        metrics = self.analytics.get_performance_metrics('wf1')
        self.assertEqual(metrics['total_executions'], 2)
        self.assertEqual(metrics['success_rate'], 50.0)
        self.assertEqual(metrics['error_count'], 1)
        self.assertGreater(metrics['average_duration'], 0)

    def test_get_performance_metrics_empty(self):
        metrics = self.analytics.get_performance_metrics('wf2')
        self.assertEqual(metrics['total_executions'], 0)
        self.assertEqual(metrics['success_rate'], 0)
        self.assertEqual(metrics['error_count'], 0)

    def test_comparative_analytics(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, True, '', self.steps)
        self.analytics.record_execution('wf2', 'exec2', self.start_time, self.end_time, False, 'Error')
        comparison = self.analytics.comparative_analytics(entity_type='workflow')
        self.assertEqual(len(comparison), 2)
        self.assertTrue('wf1' in comparison['workflow_id'].values)
        self.assertTrue('wf2' in comparison['workflow_id'].values)
        self.assertEqual(comparison[comparison['workflow_id'] == 'wf1']['success_rate'].iloc[0], 100.0)
        self.assertEqual(comparison[comparison['workflow_id'] == 'wf2']['success_rate'].iloc[0], 0.0)

    def test_comparative_analytics_empty(self):
        comparison = self.analytics.comparative_analytics(entity_type='workflow', entity_ids=['wf3'])
        self.assertTrue(comparison.empty)

    def test_train_predictive_model_insufficient_data(self):
        result = self.analytics.train_predictive_model()
        self.assertFalse(result)

    def test_predict_workflow_failure_untrained(self):
        prediction = self.analytics.predict_workflow_failure('wf1', 300.0, datetime.now().weekday())
        self.assertEqual(prediction['anomaly_score'], 0.0)
        self.assertEqual(prediction['failure_probability'], 0.0)

if __name__ == '__main__':
    unittest.main()
