import unittest

from workflow.natural_language_workflow import NLWorkflowGenerator


class TestNLWorkflowGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.generator = NLWorkflowGenerator()

    def test_initialization(self):
        """Test that the generator initializes correctly"""
        self.assertIsNotNone(self.generator.llm)
        self.assertIsInstance(self.generator.workflow_patterns, dict)
        self.assertIsInstance(self.generator.user_history, list)

    def test_load_workflow_patterns(self):
        """Test loading of workflow patterns"""
        patterns = self.generator._load_workflow_patterns()
        self.assertIsInstance(patterns, dict)
        # Check if some expected patterns are loaded
        self.assertTrue(len(patterns) > 0, "Workflow patterns should not be empty")

    def test_load_user_history(self):
        """Test loading of user history"""
        history = self.generator._load_user_history()
        self.assertIsInstance(history, list)
        # Even if empty, should return a list
        self.assertTrue(isinstance(history, list))

    def test_prepare_training_data(self):
        """Test preparation of training data for fine-tuning"""
        training_data = self.generator._prepare_training_data()
        self.assertIsInstance(training_data, list)
        self.assertTrue(len(training_data) > 0, "Training data should not be empty")
        for item in training_data:
            self.assertIn("prompt", item)
            self.assertIn("completion", item)
            self.assertIsInstance(item["prompt"], str)
            self.assertIsInstance(item["completion"], str)

    def test_construct_prompt(self):
        """Test construction of prompt for LLM"""
        nl_input = "Create a workflow for processing customer feedback"
        prompt = self.generator._construct_prompt(nl_input)
        self.assertIsInstance(prompt, str)
        self.assertIn(nl_input, prompt)
        self.assertIn("JSON", prompt)

    def test_fine_tune_model(self):
        """Test fine-tuning process (mocked response)"""
        # Since we can't actually fine-tune in test, just check if method executes
        result = self.generator.fine_tune_model()
        # Should return boolean indicating success/failure
        self.assertIsInstance(result, bool)

    def test_generate_workflow(self):
        """Test workflow generation from natural language (mocked response)"""
        nl_input = "Create a simple data processing pipeline"
        workflow = self.generator.generate_workflow(nl_input)
        self.assertIsInstance(workflow, dict)
        # Even if empty due to mock, should return dict
        self.assertTrue(isinstance(workflow, dict))


if __name__ == "__main__":
    unittest.main()
