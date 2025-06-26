import unittest
from workflow_documentation import WorkflowDocumentation

class TestWorkflowDocumentation(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.documentation = WorkflowDocumentation()
        self.template_name = "test_template"
        self.template_content = {
            "name": "Test Workflow",
            "description": "A test workflow description.",
            "steps": [
                {"id": 1, "action": "Step 1", "expected": "Result 1"},
                {"id": 2, "action": "Step 2", "expected": "Result 2"}
            ]
        }

    def test_register_template(self):
        """Test registering a documentation template."""
        self.documentation.register_template(self.template_name, self.template_content)
        self.assertIn(self.template_name, self.documentation.templates)
        self.assertEqual(self.documentation.templates[self.template_name], self.template_content)

    def test_extract_documentation_from_code(self):
        """Test extracting documentation from code comments."""
        code_snippet = """
        # Workflow: Test Workflow
        # Description: This is a test workflow.
        def test_workflow():
            # Step 1: Perform action
            pass
            # Step 2: Verify result
            pass
        """
        extracted = self.documentation.extract_documentation_from_code(code_snippet)
        self.assertIsNotNone(extracted)
        self.assertIn("name", extracted)
        self.assertEqual(extracted["name"], "Test Workflow")

    def test_generate_visual_diagram(self):
        """Test generating a visual workflow diagram."""
        self.documentation.register_template(self.template_name, self.template_content)
        diagram = self.documentation.generate_visual_diagram(self.template_name)
        self.assertIsNotNone(diagram)
        self.assertTrue(isinstance(diagram, str))
        self.assertIn("Step 1", diagram)
        self.assertIn("Step 2", diagram)

    def test_version_documentation(self):
        """Test versioning of workflow documentation."""
        self.documentation.register_template(self.template_name, self.template_content)
        version_info = {"version": "1.0.0", "date": "2023-10-01"}
        self.documentation.version_documentation(self.template_name, version_info)
        self.assertIn(self.template_name, self.documentation.version_history)
        self.assertEqual(self.documentation.version_history[self.template_name][-1], version_info)

    def test_generate_inline_help(self):
        """Test generating inline help for UI integration."""
        self.documentation.register_template(self.template_name, self.template_content)
        inline_help = self.documentation.generate_inline_help(self.template_name)
        self.assertIsNotNone(inline_help)
        self.assertTrue(isinstance(inline_help, dict))
        self.assertIn("steps", inline_help)
        self.assertEqual(len(inline_help["steps"]), 2)

    def test_error_handling_missing_template(self):
        """Test error handling for missing template."""
        with self.assertRaises(KeyError):
            self.documentation.generate_visual_diagram("nonexistent_template")

if __name__ == '__main__':
    unittest.main()
