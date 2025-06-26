import unittest
from workflow.workflow_validator import WorkflowValidator

class TestWorkflowValidator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.validator = WorkflowValidator()
        
    def test_valid_workflow(self):
        """Test validation of a correctly structured workflow"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "initialize",
                    "parameters": {"input": "data"},
                    "dependencies": []
                },
                {
                    "id": "step2",
                    "action": "process",
                    "parameters": {"method": "analyze"},
                    "dependencies": ["step1"]
                }
            ],
            "metadata": {
                "version": "1.0"
            }
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
    def test_missing_required_fields(self):
        """Test validation of workflow missing required top-level fields"""
        workflow = {
            "steps": []
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)  # Missing name and metadata
        self.assertIn("Missing required field: name", errors)
        self.assertIn("Missing required field: metadata", errors)
        
    def test_empty_steps(self):
        """Test validation of workflow with empty steps list"""
        workflow = {
            "name": "Test Workflow",
            "steps": [],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Workflow must have at least one step", errors)
        
    def test_invalid_step_structure(self):
        """Test validation of workflow with invalid step structure"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1"
                    # Missing action, parameters, dependencies
                }
            ],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)  # Missing required step fields
        self.assertIn("Step 1 (step1): Missing required field: action", errors)
        
    def test_duplicate_step_ids(self):
        """Test validation of workflow with duplicate step IDs"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "initialize",
                    "parameters": {},
                    "dependencies": []
                },
                {
                    "id": "step1",  # Duplicate ID
                    "action": "process",
                    "parameters": {},
                    "dependencies": ["step1"]
                }
            ],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)
        self.assertIn("Step 2 (step1): Duplicate step ID: step1", errors)
        self.assertIn("Self-dependency detected in step step1", errors)
        self.assertIn("Dependency 'step1' in step step1 is invalid", errors)
        
    def test_invalid_dependency(self):
        """Test validation of workflow with invalid dependency ID"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "initialize",
                    "parameters": {},
                    "dependencies": []
                },
                {
                    "id": "step2",
                    "action": "process",
                    "parameters": {},
                    "dependencies": ["nonexistent"]  # Invalid dependency
                }
            ],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid dependency ID 'nonexistent' in step step2", errors)
        
    def test_circular_dependency(self):
        """Test validation of workflow with circular dependencies"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "initialize",
                    "parameters": {},
                    "dependencies": ["step2"]  # Circular dependency
                },
                {
                    "id": "step2",
                    "action": "process",
                    "parameters": {},
                    "dependencies": ["step1"]  # Circular dependency
                }
            ],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Circular dependency detected involving step step1", errors)
        
    def test_self_dependency(self):
        """Test validation of workflow with self-dependency"""
        workflow = {
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step1",
                    "action": "initialize",
                    "parameters": {},
                    "dependencies": ["step1"]  # Self-dependency
                }
            ],
            "metadata": {}
        }
        is_valid, errors = self.validator.validate_workflow(workflow)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Self-dependency detected in step step1", errors)

if __name__ == '__main__':
    unittest.main()
