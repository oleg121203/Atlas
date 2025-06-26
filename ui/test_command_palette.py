import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
from ui.command_palette import CommandPalette

class TestCommandPalette(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.root = tk.Tk()
        self.command_data = {
            "commands": [
                {"name": "Create Workflow", "action": "create_workflow", "category": "Workflow", "shortcut": "Ctrl+Shift+W"},
                {"name": "Open Dashboard", "action": "open_dashboard", "category": "Navigation", "shortcut": "Ctrl+D"},
                {"name": "Start Task", "action": "start_task", "category": "Task", "shortcut": "Ctrl+T"}
            ],
            "contextual": [
                {"context": "workflow_editor", "commands": ["Create Workflow"]},
                {"context": "dashboard_view", "commands": ["Open Dashboard"]}
            ]
        }
        self.palette = CommandPalette(self.root, self.command_data)
        
    def tearDown(self):
        """Clean up after each test method"""
        self.root.destroy()
        
    def test_initialization(self):
        """Test initialization of command palette"""
        self.assertEqual(self.palette.command_data, self.command_data)
        self.assertFalse(self.palette.is_visible)
        self.assertIsNone(self.palette.window)
        
    def test_load_default_commands(self):
        """Test loading default command data"""
        palette = CommandPalette(self.root)
        default_commands = palette.command_data
        self.assertTrue(len(default_commands.get("commands", [])) > 0)
        self.assertTrue(len(default_commands.get("contextual", [])) > 0)
        
    def test_show_and_hide(self):
        """Test showing and hiding the command palette"""
        self.palette.show()
        self.assertTrue(self.palette.is_visible)
        self.assertIsNotNone(self.palette.window)
        self.assertIsNotNone(self.palette.entry)
        self.assertIsNotNone(self.palette.suggestions_listbox)
        
        self.palette.hide()
        self.assertFalse(self.palette.is_visible)
        self.assertIsNone(self.palette.window)
        
    def test_update_suggestions_all(self):
        """Test updating suggestions with no filter"""
        self.palette.show()
        self.palette._update_suggestions()
        self.assertEqual(len(self.palette.filtered_commands), 3)
        self.assertEqual(self.palette.suggestions_listbox.size(), 3)
        
    def test_update_suggestions_search(self):
        """Test updating suggestions with search text"""
        self.palette.show()
        self.palette._update_suggestions(search_text="create")
        self.assertEqual(len(self.palette.filtered_commands), 1)
        self.assertEqual(self.palette.filtered_commands[0]["name"], "Create Workflow")
        self.assertEqual(self.palette.suggestions_listbox.size(), 1)
        
    def test_update_suggestions_context(self):
        """Test updating suggestions with context"""
        self.palette.show()
        self.palette._update_suggestions(context="workflow_editor")
        self.assertEqual(len(self.palette.filtered_commands), 1)
        self.assertEqual(self.palette.filtered_commands[0]["name"], "Create Workflow")
        self.assertEqual(self.palette.suggestions_listbox.size(), 1)
        
    def test_select_command(self):
        """Test selecting a command from the list"""
        self.palette.show()
        self.palette._update_suggestions()
        with patch.object(self.palette, '_execute_command') as mock_execute:
            with patch.object(self.palette, 'hide') as mock_hide:
                self.palette.suggestions_listbox.select_set(1)
                self.palette._on_select_command()
                mock_execute.assert_called_once_with(self.palette.filtered_commands[1])
                mock_hide.assert_called_once()
        
    def test_move_selection(self):
        """Test moving selection up and down"""
        self.palette.show()
        self.palette._update_suggestions()
        
        # Move down
        self.palette.suggestions_listbox.select_set(0)
        self.palette._move_selection_down(None)
        self.assertEqual(self.palette.suggestions_listbox.curselection()[0], 1)
        
        # Move down again (should stay at last item)
        self.palette._move_selection_down(None)
        self.assertEqual(self.palette.suggestions_listbox.curselection()[0], 2)
        
        # Move up
        self.palette._move_selection_up(None)
        self.assertEqual(self.palette.suggestions_listbox.curselection()[0], 1)
        
        # Move up again
        self.palette._move_selection_up(None)
        self.assertEqual(self.palette.suggestions_listbox.curselection()[0], 0)

if __name__ == '__main__':
    unittest.main()
