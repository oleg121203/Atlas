"""
Unit tests for Workflow Optimization Module
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from workflow_analytics import WorkflowAnalytics
from workflow_optimization import WorkflowOptimizer

class TestWorkflowOptimizer(unittest.TestCase):
    def setUp(self):
        self.analytics = WorkflowAnalytics()
        self.optimizer = WorkflowOptimizer(self.analytics)
        self.start_time = datetime.now() - timedelta(minutes=10)
        self.end_time = datetime.now() - timedelta(minutes=5)
        self.steps = [
            {'step_id': 'step1', 'step_name': 'First Step', 'start_time': self.start_time, 
             'end_time': self.start_time + timedelta(minutes=2), 'success': True},
            {'step_id': 'step2', 'step_name': 'Second Step', 'start_time': self.start_time + timedelta(minutes=2), 
             'end_time': self.end_time, 'success': True}
        ]

    def test_build_workflow_graph_empty(self):
        graph = self.optimizer.build_workflow_graph('wf1')
        self.assertEqual(len(graph.nodes), 0)
        self.assertEqual(len(graph.edges), 0)

    def test_build_workflow_graph_with_data(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, True, '', self.steps)
        graph = self.optimizer.build_workflow_graph('wf1')
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
        self.assertTrue(graph.has_edge('step1', 'step2'))

    def test_identify_critical_path_empty(self):
        path = self.optimizer.identify_critical_path('wf1')
        self.assertEqual(len(path), 0)

    def test_identify_critical_path_with_data(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, True, '', self.steps)
        path = self.optimizer.identify_critical_path('wf1')
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], 'step1')
        self.assertEqual(path[1], 'step2')

    def test_cluster_executions_insufficient_data(self):
        result = self.optimizer.cluster_executions('wf1')
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['centers'], [])
        self.assertEqual(result['execution_ids'], [])

    def test_recommend_optimizations_no_data(self):
        recommendations = self.optimizer.recommend_optimizations('wf1')
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['type'], 'data_insufficient')

    def test_recommend_optimizations_with_data(self):
        self.analytics.record_execution('wf1', 'exec1', self.start_time, self.end_time, False, 'Error', self.steps)
        recommendations = self.optimizer.recommend_optimizations('wf1')
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any(rec['type'] == 'reliability' for rec in recommendations))

    def test_evaluate_optimization_impact_no_data(self):
        impact = self.optimizer.evaluate_optimization_impact('wf1', 'opt1')
        self.assertEqual(impact['before']['total_executions'], 0)
        self.assertEqual(impact['after']['total_executions'], 0)

if __name__ == '__main__':
    unittest.main()
