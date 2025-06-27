import os
import sys
import tkinter as tk

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.chat_history_view import ChatHistoryView


@pytest.fixture
def root_window():
    """Create a root Tk window for the tests."""
    root = tk.Tk()
    # Hide the window during tests
    root.withdraw()
    yield root
    root.destroy()


def test_chat_history_view_initialization(root_window):
    """Test that the ChatHistoryView can be initialized successfully."""
    try:
        view = ChatHistoryView(root_window)
        assert view is not None
        assert isinstance(view.history, list)
        assert len(view.history) == 0
    except Exception as e:
        pytest.fail(f"ChatHistoryView initialization failed: {e}")


def test_add_and_clear_messages(root_window):
    """Test adding messages of different roles and clearing the history."""
    view = ChatHistoryView(root_window)

    # Add a user message
    view.add_message("user", "Hello, Atlas!")
    assert len(view.history) == 1
    assert view.history[0] == {"role": "user", "text": "Hello, Atlas!"}

    # Add an agent message
    view.add_message("agent", "Hello! How can I help you?")
    assert len(view.history) == 2
    assert view.history[1] == {"role": "agent", "text": "Hello! How can I help you?"}

    # Add a system message
    view.add_message("system", "System is now online.")
    assert len(view.history) == 3
    assert view.history[2] == {"role": "system", "text": "System is now online."}

    # Verify text is in the textbox (simple check)
    text_content = view.textbox.get("1.0", "end-1c")
    assert "Hello, Atlas!" in text_content
    assert "Hello! How can I help you?" in text_content
    assert "System is now online." in text_content

    # Test the clear method
    view.clear()
    assert len(view.history) == 0
    cleared_text_content = view.textbox.get("1.0", "end-1c")
    assert cleared_text_content == ""
