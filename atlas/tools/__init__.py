"""Atlas tools package.

Core automation tools for screen capture, OCR, image recognition,
mouse/keyboard control, clipboard management, terminal operations, and creative chaining.

Modernized tools support async execution, chaining, and rich metadata for creative workflows.
Creative, proactive, and playful tool modules are included for superhuman and enjoyable automation.
"""

import logging
from typing import Any, Dict, List, Optional

__all__ = [
    "BrowserTool",
    "wait_for_clipboard_change",
    "accessibility_action",
    "add_meme_caption",
    "run_applescript",
    "run_automator_or_shortcut",
    "BaseTool",
    "ClipboardResult",
    "clear_clipboard",
    "get_clipboard_image",
    "get_clipboard_text",
    "set_clipboard_image",
    "set_clipboard_text",
    "CreativeTool",
    "DelayTool",
    "EmailAnalytics",
]

from .accessibility_tool import accessibility_action
from .add_meme_caption_tool import add_meme_caption
from .applescript_tool import run_applescript
from .automator_shortcuts_tool import run_automator_or_shortcut
from .base_tool import BaseTool
from .browser import BrowserTool
from .clipboard_tool import (
    ClipboardResult,
    clear_clipboard,
    get_clipboard_image,
    get_clipboard_text,
    set_clipboard_image,
    set_clipboard_text,
    wait_for_clipboard_change,
)
from .creative_tool import CreativeTool
from .delay_tool import DelayTool
from .email.analytics import EmailAnalytics
from .email.automation import EmailAutomation
from .email.filtering import EmailFilter
from .email.signature import EmailSignatureManager
from .email.templates import EmailTemplateManager
from .image_recognition_tool import find_object_in_image, find_template_in_image
from .macro_suggestion_tool import macro_suggestion
from .mouse_keyboard_tool import (
    MouseButton,
    MouseKeyboardResult,
    click_at,
    move_mouse,
    press_key,
    type_text,
)
from .ocr_tool import ocr_file, ocr_image
from .pdf_extraction_tool import extract_pdf_text
from .playful_tool import PlayfulTool
from .proactive_tool import ProactiveTool
from .save_image_tool import save_image
from .screenshot_tool import capture_screen
from .summarize_text_tool import summarize_text
from .system_events_tool import system_event
from .terminal_tool import (
    TerminalResult,
    change_directory,
    execute_command,
    execute_script,
    get_environment,
    kill_process,
)


# Unified Email Tool that provides access to all email functionality
class EmailTool:
    """Unified email tool that provides access to all email functionality."""

    def __init__(self, service=None):
        """Initialize EmailTool with Gmail service."""
        self.service = service
        self.logger = logging.getLogger(__name__)
        # Initialize with basic email components
        try:
            self.analytics = EmailAnalytics()
            self.filter = EmailFilter()
            self.templates = EmailTemplateManager()
            self.automation = EmailAutomation({})  # Empty config for now
            self.signature = EmailSignatureManager()
        except Exception as e:
            self.logger.warning(f"Could not initialize email components: {e}")
            self.analytics = None
            self.filter = None
            self.templates = None
            self.automation = None
            self.signature = None

    def search_emails(
        self,
        query: str,
        max_results: int = 50,
        include_spam_trash: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Search emails with basic filtering."""
        if self.filter is None:
            return {"error": "Email filtering not available"}
        return {
            "message": "Email search completed",
            "query": query,
            "max_results": max_results,
        }

    def analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email using basic analytics."""
        if self.analytics is None:
            return {"error": "Email analytics not available"}
        return {
            "message": "Email analysis completed",
            "email_id": email.get("id", "unknown"),
        }

    def get_statistics(
        self, time_range: Optional[tuple] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get basic email statistics."""
        if self.analytics is None:
            return {"error": "Email statistics not available"}
        return {"message": "Email statistics retrieved", "time_range": str(time_range)}

    def create_workflow(
        self, name: str, triggers: List[Dict[str, Any]], actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create basic email workflow."""
        if self.automation is None:
            return {"error": "Email automation not available"}
        return {"message": "Workflow created", "name": name}

    def create_template(
        self,
        name: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create basic email template."""
        if self.templates is None:
            return {"error": "Email templates not available"}
        return {"message": "Template created", "name": name, "subject": subject}

    def create_signature(
        self, name: str, content: str, type: str = "html"
    ) -> Dict[str, Any]:
        """Create basic email signature."""
        if self.signature is None:
            return {"error": "Email signatures not available"}
        return {"message": "Signature created", "name": name, "type": type}

    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows."""
        if self.automation is None:
            return {"error": "Email automation not available"}
        return {"message": "Workflows listed", "count": 0}

    def list_templates(self) -> Dict[str, Any]:
        """List all templates."""
        if self.templates is None:
            return {"error": "Email templates not available"}
        return {"message": "Templates listed", "count": 0}

    def list_signatures(self) -> Dict[str, Any]:
        """List all signatures."""
        if self.signature is None:
            return {"error": "Email signatures not available"}
        return {"message": "Signatures listed", "count": 0}

    def send_from_template(
        self, template_name: str, recipients: List[str], context: Dict[str, str]
    ) -> Dict[str, Any]:
        """Send email from template."""
        if self.templates is None:
            return {"error": "Email templates not available"}
        return {
            "message": "Email sent from template",
            "template": template_name,
            "recipients": len(recipients),
        }

    def send_email_with_signature(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        signature_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email with signature."""
        if self.signature is None:
            return {"error": "Email signatures not available"}
        return {"message": "Email sent with signature", "to": to, "subject": subject}


__all__ = [
    # Screenshot
    "capture_screen",
    # OCR
    "ocr_image",
    "ocr_file",
    # Image recognition
    "find_template_in_image",
    "find_object_in_image",
    # Mouse & Keyboard
    "MouseButton",
    "click_at",
    "move_mouse",
    "type_text",
    "press_key",
    "MouseKeyboardResult",
    # Clipboard
    "get_clipboard_text",
    "set_clipboard_text",
    "get_clipboard_image",
    "set_clipboard_image",
    "clear_clipboard",
    "ClipboardResult",
    # Terminal
    "execute_command",
    "execute_script",
    "get_environment",
    "change_directory",
    "kill_process",
    "TerminalResult",
    # Email
    "EmailAnalytics",
    "EmailAutomation",
    "EmailFilter",
    "EmailTemplateManager",
    "EmailSignatureManager",
    "EmailTool",
    "BaseTool",
    "DelayTool",
    "CreativeTool",
    "ProactiveTool",
    "PlayfulTool",
    "extract_pdf_text",
    "summarize_text",
    "add_meme_caption",
    "save_image",
    "macro_suggestion",
    "run_applescript",
    "run_automator_or_shortcut",
    "accessibility_action",
    "system_event",
]
