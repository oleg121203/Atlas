import unittest

from core.events import (
    CHAT_MESSAGE_RECEIVED,
    CHAT_MESSAGE_SENT,
    CONTEXT_UPDATED,
    MEMORY_UPDATED,
    NEW_TOOL_REGISTERED,
    SHOW_NOTIFICATION,
    TASK_COMPLETED,
    TASK_CREATED,
    TASK_UPDATED,
    THEME_CHANGED,
    TOOL_ERROR,
    TOOL_EXECUTED,
    USER_ACTION,
    WORKFLOW_EXECUTED,
)


class TestEvents(unittest.TestCase):
    def test_task_completed_constant(self):
        """Test TASK_COMPLETED constant value."""
        self.assertEqual(TASK_COMPLETED, "TaskCompleted")

    def test_task_created_constant(self):
        """Test TASK_CREATED constant value."""
        self.assertEqual(TASK_CREATED, "TaskCreated")

    def test_task_updated_constant(self):
        """Test TASK_UPDATED constant value."""
        self.assertEqual(TASK_UPDATED, "TaskUpdated")

    def test_new_tool_registered_constant(self):
        """Test NEW_TOOL_REGISTERED constant value."""
        self.assertEqual(NEW_TOOL_REGISTERED, "NewToolRegistered")

    def test_tool_executed_constant(self):
        """Test TOOL_EXECUTED constant value."""
        self.assertEqual(TOOL_EXECUTED, "ToolExecuted")

    def test_tool_error_constant(self):
        """Test TOOL_ERROR constant value."""
        self.assertEqual(TOOL_ERROR, "ToolError")

    def test_context_updated_constant(self):
        """Test CONTEXT_UPDATED constant value."""
        self.assertEqual(CONTEXT_UPDATED, "ContextUpdated")

    def test_memory_updated_constant(self):
        """Test MEMORY_UPDATED constant value."""
        self.assertEqual(MEMORY_UPDATED, "MemoryUpdated")

    def test_show_notification_constant(self):
        """Test SHOW_NOTIFICATION constant value."""
        self.assertEqual(SHOW_NOTIFICATION, "ShowNotification")

    def test_user_action_constant(self):
        """Test USER_ACTION constant value."""
        self.assertEqual(USER_ACTION, "UserAction")

    def test_theme_changed_constant(self):
        """Test THEME_CHANGED constant value."""
        self.assertEqual(THEME_CHANGED, "ThemeChanged")

    def test_chat_message_sent_constant(self):
        """Test CHAT_MESSAGE_SENT constant value."""
        self.assertEqual(CHAT_MESSAGE_SENT, "ChatMessageSent")

    def test_chat_message_received_constant(self):
        """Test CHAT_MESSAGE_RECEIVED constant value."""
        self.assertEqual(CHAT_MESSAGE_RECEIVED, "ChatMessageReceived")

    def test_workflow_executed_constant(self):
        """Test WORKFLOW_EXECUTED constant value."""
        self.assertEqual(WORKFLOW_EXECUTED, "WorkflowExecuted")


if __name__ == "__main__":
    unittest.main()
