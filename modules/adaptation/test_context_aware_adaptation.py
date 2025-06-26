import unittest
from unittest.mock import MagicMock, patch
import json
import os
from datetime import datetime

from modules.adaptation.context_aware_adaptation import ContextAwareAdaptation

class TestContextAwareAdaptation(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.adaptation = ContextAwareAdaptation()
        self.test_model_path = "/tmp/test_model.json"
        self.test_training_data_path = "/tmp/test_training_data.json"
        self.user_id = "test_user_001"
        
        # Create a simple model file for testing
        os.makedirs(os.path.dirname(self.test_model_path), exist_ok=True)
        with open(self.test_model_path, 'w') as f:
            json.dump({
                "parameters": {"accuracy": 0.8, "version": "1.0"},
                "last_trained": "2023-01-01T00:00:00"
            }, f)
        
        # Create training data file for testing
        with open(self.test_training_data_path, 'w') as f:
            json.dump({
                "samples": [
                    {"user_id": self.user_id, "action": "create_workflow", "context": {"time": "morning"}},
                    {"user_id": self.user_id, "action": "start_task", "context": {"time": "afternoon"}}
                ]
            }, f)
        
    def test_initialization_without_model(self):
        """Test initialization without a model path"""
        adaptation = ContextAwareAdaptation()
        self.assertIsNone(adaptation.model_path)
        self.assertIsNone(adaptation.adaptation_model)
        self.assertEqual(len(adaptation.user_behavior_data), 0)
        self.assertEqual(len(adaptation.environment_data), 0)
        self.assertEqual(len(adaptation.adaptation_history), 0)
        
    def test_initialization_with_model(self):
        """Test initialization with a model path"""
        adaptation = ContextAwareAdaptation(model_path=self.test_model_path)
        self.assertEqual(adaptation.model_path, self.test_model_path)
        self.assertIsNotNone(adaptation.adaptation_model)
        self.assertEqual(adaptation.adaptation_model['parameters']['version'], '1.0')
        
    def test_collect_user_behavior(self):
        """Test collecting user behavior data"""
        context = {"time_of_day": "morning", "current_app": "workflow_editor"}
        self.adaptation.collect_user_behavior(self.user_id, "create_workflow", context)
        
        self.assertIn(self.user_id, self.adaptation.user_behavior_data)
        user_data = self.adaptation.user_behavior_data[self.user_id]
        self.assertEqual(len(user_data), 1)
        self.assertEqual(user_data[0]['action'], "create_workflow")
        self.assertEqual(user_data[0]['context'], context)
        self.assertTrue('timestamp' in user_data[0])
        
    def test_collect_environment_data(self):
        """Test collecting environment data"""
        env_metrics = {"time_of_day": "afternoon", "device_load": 0.75, "network_status": "connected"}
        self.adaptation.collect_environment_data(env_metrics)
        
        self.assertEqual(self.adaptation.environment_data['metrics'], env_metrics)
        self.assertTrue('timestamp' in self.adaptation.environment_data)
        
    def test_analyze_context_no_data(self):
        """Test context analysis when no user data exists"""
        analysis = self.adaptation.analyze_context("nonexistent_user")
        self.assertEqual(analysis['user_id'], "nonexistent_user")
        self.assertEqual(analysis['most_common_action'], "none")
        self.assertEqual(analysis['action_frequency'], {})
        self.assertEqual(analysis['environment'], {})
        self.assertTrue('timestamp' in analysis)
        
    def test_analyze_context_with_data(self):
        """Test context analysis with user behavior data"""
        # Add some behavior data
        self.adaptation.collect_user_behavior(self.user_id, "create_workflow", {"time": "morning"})
        self.adaptation.collect_user_behavior(self.user_id, "create_workflow", {"time": "afternoon"})
        self.adaptation.collect_user_behavior(self.user_id, "start_task", {"time": "evening"})
        # Add environment data
        env_metrics = {"time_of_day": "evening", "device_load": 0.5}
        self.adaptation.collect_environment_data(env_metrics)
        
        analysis = self.adaptation.analyze_context(self.user_id)
        self.assertEqual(analysis['user_id'], self.user_id)
        self.assertEqual(analysis['most_common_action'], "create_workflow")
        self.assertEqual(analysis['action_frequency']['create_workflow'], 2)
        self.assertEqual(analysis['action_frequency']['start_task'], 1)
        self.assertEqual(analysis['environment'], env_metrics)
        
    def test_suggest_workflow_adaptation_create_workflow(self):
        """Test adaptation suggestions for frequent workflow creation"""
        context_analysis = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "most_common_action": "create_workflow",
            "action_frequency": {"create_workflow": 5},
            "environment": {"time_of_day": "morning"}
        }
        suggestion = self.adaptation.suggest_workflow_adaptation(context_analysis)
        
        self.assertEqual(suggestion['user_id'], self.user_id)
        self.assertEqual(len(suggestion['suggested_changes']), 1)
        change = suggestion['suggested_changes'][0]
        self.assertEqual(change['target'], "workflow_editor")
        self.assertEqual(change['change_type'], "ui_optimization")
        self.assertTrue(change['parameters']['simplify_ui'])
        
    def test_suggest_workflow_adaptation_start_task_evening(self):
        """Test adaptation suggestions for frequent task starting in evening"""
        context_analysis = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "most_common_action": "start_task",
            "action_frequency": {"start_task": 3},
            "environment": {"time_of_day": "evening"}
        }
        suggestion = self.adaptation.suggest_workflow_adaptation(context_analysis)
        
        self.assertEqual(suggestion['user_id'], self.user_id)
        self.assertEqual(len(suggestion['suggested_changes']), 2)
        
        task_change = next(c for c in suggestion['suggested_changes'] if c['target'] == "task_manager")
        self.assertEqual(task_change['change_type'], "behavior_modification")
        self.assertTrue(task_change['parameters']['auto_prioritize'])
        
        theme_change = next(c for c in suggestion['suggested_changes'] if c['target'] == "global_ui")
        self.assertEqual(theme_change['change_type'], "visual_adjustment")
        self.assertEqual(theme_change['parameters']['theme'], "dark")
        
    def test_apply_adaptation_no_changes(self):
        """Test applying adaptations when there are no changes suggested"""
        suggestion = {"user_id": self.user_id, "timestamp": datetime.now().isoformat(), "suggested_changes": []}
        result = self.adaptation.apply_adaptation(suggestion)
        self.assertTrue(result)
        self.assertEqual(len(self.adaptation.adaptation_history), 0)
        
    def test_apply_adaptation_with_changes(self):
        """Test applying adaptations with suggested changes"""
        changes = [
            {"target": "workflow_editor", "change_type": "ui_optimization", "description": "Simplify UI", "parameters": {"simplify_ui": True}}
        ]
        suggestion = {"user_id": self.user_id, "timestamp": datetime.now().isoformat(), "suggested_changes": changes}
        result = self.adaptation.apply_adaptation(suggestion)
        self.assertTrue(result)
        self.assertEqual(len(self.adaptation.adaptation_history), 1)
        history_entry = self.adaptation.adaptation_history[0]
        self.assertEqual(history_entry['user_id'], self.user_id)
        self.assertEqual(history_entry['changes_applied'], changes)
        
    def test_train_adaptation_model(self):
        """Test training the adaptation model with data"""
        result = self.adaptation.train_adaptation_model(self.test_training_data_path)
        self.assertTrue(result)
        self.assertIsNotNone(self.adaptation.adaptation_model)
        self.assertTrue('last_trained' in self.adaptation.adaptation_model)
        self.assertEqual(self.adaptation.adaptation_model['parameters']['version'], '2.0')
        
    def test_save_model_no_model(self):
        """Test saving a model when none exists"""
        adaptation = ContextAwareAdaptation()
        result = adaptation.save_model("/tmp/nonexistent/path/model.json")
        self.assertFalse(result)
        
    def test_save_model_with_model(self):
        """Test saving a model when one exists"""
        adaptation = ContextAwareAdaptation()
        adaptation.adaptation_model = {"test": "data", "last_trained": datetime.now().isoformat()}
        output_path = "/tmp/test_output_model.json"
        result = adaptation.save_model(output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, adaptation.adaptation_model)

if __name__ == '__main__':
    unittest.main()
