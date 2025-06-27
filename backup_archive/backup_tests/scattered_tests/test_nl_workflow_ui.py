import tkinter as tk
import unittest
from unittest.mock import MagicMock

from ui.nl_workflow_ui import NLWorkflowUI
from workflow.natural_language_workflow import NLWorkflowGenerator


class TestNLWorkflowUI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.root = tk.Tk()
        self.generator = MagicMock(spec=NLWorkflowGenerator)
        self.ui = NLWorkflowUI(self.root, self.generator)

    def tearDown(self):
        """Clean up after each test method"""
        self.root.destroy()

    def test_initialization(self):
        """Test that the UI initializes correctly"""
        self.assertIsNotNone(self.ui.root)
        self.assertEqual(self.ui.generator, self.generator)
        self.assertEqual(
            self.ui.root.title(), "Atlas Natural Language Workflow Generator"
        )

    def test_generate_workflow_empty_input(self):
        """Test generate_workflow with empty input"""
        # Mock messagebox to avoid actual UI popups during test
        with unittest.mock.patch("tkinter.messagebox.showwarning") as mock_warning:
            self.ui.generate_workflow()
            mock_warning.assert_called_once_with(
                "Input Required",
                "Please enter a description of the workflow you want to create.",
            )

    def test_generate_workflow_valid_input(self):
        """Test generate_workflow with valid input"""
        test_input = "Create a data processing workflow"
        test_workflow = {"name": "Test Workflow", "steps": []}
        self.generator.generate_workflow.return_value = test_workflow

        self.ui.input_text.insert("1.0", test_input)
        self.ui.generate_workflow()

        self.generator.generate_workflow.assert_called_once_with(test_input)
        self.assertTrue(hasattr(self.ui, "current_workflow"))
        self.assertEqual(self.ui.current_workflow, test_workflow)

        # Check if output text was updated (we can't check content directly due to state)
        self.assertEqual(
            self.ui.output_text.get("1.0", "1.1"), "{"
        )  # First char should be opening brace of JSON

    def test_generate_workflow_error(self):
        """Test generate_workflow when generator raises exception"""
        test_input = "Create a workflow"
        self.generator.generate_workflow.side_effect = Exception("Test error")

        self.ui.input_text.insert("1.0", test_input)
        with unittest.mock.patch("tkinter.messagebox.showerror") as mock_error:
            self.ui.generate_workflow()
            mock_error.assert_called_once()

    def test_save_workflow_no_workflow(self):
        """Test save_workflow when no workflow has been generated"""
        with unittest.mock.patch("tkinter.messagebox.showwarning") as mock_warning:
            self.ui.save_workflow()
            mock_warning.assert_called_once_with(
                "No Workflow", "Generate a workflow first before saving."
            )

    def test_save_workflow_success(self):
        """Test save_workflow with a generated workflow"""
        test_workflow = {"name": "Test Workflow"}
        self.ui.current_workflow = test_workflow

        with unittest.mock.patch("tkinter.messagebox.showinfo") as mock_info:
            self.ui.save_workflow()
            mock_info.assert_called_once_with(
                "Save Successful", "Workflow saved successfully! (Placeholder action)"
            )

    def test_edit_workflow_no_workflow(self):
        """Test edit_workflow when no workflow has been generated"""
        with unittest.mock.patch("tkinter.messagebox.showwarning") as mock_warning:
            self.ui.edit_workflow()
            mock_warning.assert_called_once_with(
                "No Workflow", "Generate a workflow first before editing."
            )

    def test_edit_workflow_success(self):
        """Test edit_workflow with a generated workflow"""
        test_workflow = {"name": "Test Workflow"}
        self.ui.current_workflow = test_workflow

        with unittest.mock.patch("tkinter.messagebox.showinfo") as mock_info:
            self.ui.edit_workflow()
            mock_info.assert_called_once_with(
                "Editor", "Opening workflow editor... (Placeholder action)"
            )


if __name__ == "__main__":
    unittest.main()
