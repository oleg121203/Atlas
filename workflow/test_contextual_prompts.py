import unittest
import os
import json
from workflow.contextual_prompts import ContextualPromptGenerator

class TestContextualPromptGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_data_dir = "/tmp/test_contextual_prompts"
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Create test user roles
        roles_data = {
            "test_user": {
                "name": "Data Analyst",
                "permissions": ["create_workflow", "edit_workflow", "analyze_data"],
                "preferences": {
                    "style": "concise",
                    "complexity": "intermediate",
                    "domain": "data processing"
                }
            },
            "default_role": {
                "name": "User",
                "permissions": ["create_workflow", "edit_workflow"],
                "preferences": {}
            }
        }
        with open(os.path.join(self.test_data_dir, "user_roles.json"), 'w') as f:
            json.dump(roles_data, f)
            
        # Create test user history
        history_data = [
            {
                "user_id": "test_user",
                "workflow": {
                    "name": "Data Pipeline",
                    "steps": [
                        {"action": "extract_data", "parameters": {}},
                        {"action": "transform_data", "parameters": {}},
                        {"action": "load_data", "parameters": {}}
                    ]
                }
            },
            {
                "user_id": "test_user",
                "workflow": {
                    "name": "Analysis Flow",
                    "steps": [
                        {"action": "extract_data", "parameters": {}},
                        {"action": "analyze_data", "parameters": {}}
                    ]
                }
            },
            {
                "user_id": "other_user",
                "workflow": {
                    "name": "Other Flow",
                    "steps": []
                }
            }
        ]
        with open(os.path.join(self.test_data_dir, "user_history.json"), 'w') as f:
            json.dump(history_data, f)
            
        # Create test dashboard configs
        dashboard_data = {
            "active_dashboards": ["Sales Dashboard", "Performance Metrics"],
            "metrics": {
                "data_points": 1500,
                "last_updated": "2023-05-10"
            }
        }
        with open(os.path.join(self.test_data_dir, "dashboard_configs.json"), 'w') as f:
            json.dump(dashboard_data, f)
            
        self.generator = ContextualPromptGenerator(self.test_data_dir)
        
    def tearDown(self):
        """Clean up after each test method"""
        for file in os.listdir(self.test_data_dir):
            os.remove(os.path.join(self.test_data_dir, file))
        os.rmdir(self.test_data_dir)
        
    def test_load_user_roles(self):
        """Test loading user role information"""
        self.assertIn("test_user", self.generator.user_roles)
        self.assertEqual(self.generator.user_roles["test_user"]["name"], "Data Analyst")
        self.assertIn("default_role", self.generator.user_roles)
        
    def test_load_user_history(self):
        """Test loading user history data"""
        self.assertEqual(len(self.generator.user_history), 3)
        test_user_history = [h for h in self.generator.user_history if h["user_id"] == "test_user"]
        self.assertEqual(len(test_user_history), 2)
        
    def test_load_dashboard_configs(self):
        """Test loading dashboard configuration data"""
        self.assertEqual(len(self.generator.dashboard_configs["active_dashboards"]), 2)
        self.assertEqual(self.generator.dashboard_configs["active_dashboards"][0], "Sales Dashboard")
        
    def test_generate_contextual_prompt_default_user(self):
        """Test generating contextual prompt for default user"""
        base_prompt = "Create a workflow for data analysis"
        enhanced_prompt = self.generator.generate_contextual_prompt(base_prompt)
        
        self.assertIn("You are assisting a User with workflow creation", enhanced_prompt)
        self.assertIn("User request: Create a workflow for data analysis", enhanced_prompt)
        
    def test_generate_contextual_prompt_test_user(self):
        """Test generating contextual prompt for specific test user"""
        base_prompt = "Create a workflow for data analysis"
        enhanced_prompt = self.generator.generate_contextual_prompt(base_prompt, user_id="test_user")
        
        self.assertIn("You are assisting a Data Analyst with workflow creation", enhanced_prompt)
        self.assertIn("User preferences: style=concise, complexity=intermediate, domain=data processing", enhanced_prompt)
        self.assertIn("Frequently used actions: extract_data", enhanced_prompt)
        self.assertIn("Active dashboards: Sales Dashboard, Performance Metrics", enhanced_prompt)
        self.assertIn("User request: Create a workflow for data analysis", enhanced_prompt)
        
    def test_generate_contextual_prompt_with_context_data(self):
        """Test generating contextual prompt with additional context data"""
        base_prompt = "Create a workflow"
        context_data = {"current_task": "Monthly Sales Report"}
        enhanced_prompt = self.generator.generate_contextual_prompt(base_prompt, user_id="test_user", context_data=context_data)
        
        self.assertIn("Current user task: Monthly Sales Report", enhanced_prompt)
        self.assertIn("User request: Create a workflow", enhanced_prompt)

if __name__ == '__main__':
    unittest.main()
