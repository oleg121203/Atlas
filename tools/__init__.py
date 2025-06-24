"""Atlas tools package.

Core automation tools for screen capture, OCR, image recognition,
mouse/keyboard control, clipboard management, terminal operations, and creative chaining.

Modernized tools support async execution, chaining, and rich metadata for creative workflows.
Creative, proactive, and playful tool modules are included for superhuman and enjoyable automation.
"""

from typing import Optional, List, Dict, Any, Tuple
import logging

from .clipboard_tool import (
    ClipboardResult,
    clear_clipboard,
    get_clipboard_image,
    get_clipboard_text,
    set_clipboard_image,
    set_clipboard_text,
    wait_for_clipboard_change,
)
from .email.analytics import EmailAnalytics
from .email.automation import EmailAutomation
from .email.filtering import EmailFilter
from .email.templates import EmailTemplateManager
from .email.signature import EmailSignatureManager
from .browser import BrowserTool
from .image_recognition_tool import find_object_in_image, find_template_in_image
from .mouse_keyboard_tool import (
    MouseButton,
    MouseKeyboardResult,
    click_at,
    move_mouse,
    press_key,
    type_text,
)
from .ocr_tool import ocr_file, ocr_image
from .screenshot_tool import capture_screen
from .terminal_tool import (
    TerminalResult,
    change_directory,
    execute_command,
    execute_script,
    get_environment,
    kill_process,
)
from .base_tool import BaseTool
from .delay_tool import DelayTool
from .creative_tool import CreativeTool
from .proactive_tool import ProactiveTool
from .playful_tool import PlayfulTool
from .pdf_extraction_tool import extract_pdf_text
from .summarize_text_tool import summarize_text
from .add_meme_caption_tool import add_meme_caption
from .save_image_tool import save_image
from .macro_suggestion_tool import macro_suggestion
from .applescript_tool import run_applescript
from .automator_shortcuts_tool import run_automator_or_shortcut
from .accessibility_tool import accessibility_action
from .system_events_tool import system_event

# Unified Email Tool that provides access to all email functionality
class EmailTool:
    """Unified email tool that provides access to all email functionality."""
    
    def __init__(self, service):
        """Initialize EmailTool with Gmail service."""
        # Import build only if needed for Gmail service
        try:
            from googleapiclient.discovery import build
        except ImportError:
            build = None  # Not needed unless using Gmail features
        self.service = service
        self.logger = logging.getLogger(__name__)
        self.analytics = EmailAnalytics(service)
        self.filter = EmailFilter(service)
        self.templates = EmailTemplateManager(service)
        self.automation = EmailAutomation(service)
        self.signature = EmailSignatureManager(service)

    def search_emails(self, 
                     query: str,
                     max_results: int = 50,
                     include_spam_trash: bool = False,
                     categories: Optional[List[str]] = None,
                     importance: Optional[str] = None,
                     attachment_types: Optional[List[str]] = None,
                     thread_length: Optional[Tuple[int, int]] = None,
                     response_time: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """Search emails with advanced filtering using the filter tool."""
        return self.filter.search_emails(
            query=query,
            max_results=max_results,
            include_spam_trash=include_spam_trash,
            categories=categories,
            importance=importance,
            attachment_types=attachment_types,
            thread_length=thread_length,
            response_time=response_time
        )

    def analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email using the analytics tool."""
        return self.analytics.analyze_email(email)

    def get_statistics(self, time_range: Optional[tuple] = None, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get email statistics using the analytics tool."""
        return self.analytics.get_email_statistics(time_range, categories)

    def create_workflow(self, name: str, triggers: List[Dict[str, Any]], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create email workflow using the automation tool."""
        return self.automation.create_workflow(name, triggers, actions)

    def create_template(self, name: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create email template using the templates tool."""
        return self.templates.create_template(name, subject, body, attachments)

    def create_signature(self, name: str, content: str, type: str = 'html') -> Dict[str, Any]:
        """Create email signature using the signature tool."""
        return self.signature.create_signature(name, content, type)

    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows using the automation tool."""
        return self.automation.list_workflows()

    def list_templates(self) -> Dict[str, Any]:
        """List all templates using the templates tool."""
        return self.templates.list_templates()

    def list_signatures(self) -> Dict[str, Any]:
        """List all signatures using the signature tool."""
        return self.signature.list_signatures()

    def send_from_template(self, template_name: str, recipients: List[str], context: Dict[str, str]) -> Dict[str, Any]:
        """Send email from template using the templates tool."""
        return self.templates.send_from_template(template_name, recipients, context)

    def send_email_with_signature(self, to: str, subject: str, body: str, attachments: Optional[List[str]] = None, signature_id: Optional[str] = None) -> Dict[str, Any]:
        """Send email with signature using the signature tool."""
        return self.signature.create_email_with_signature(to, subject, body, attachments, signature_id)

__all__ = [
    #Screenshot
    "capture_screen",
    #OCR
    "ocr_image", "ocr_file",
    #Image recognition
    "find_template_in_image", "find_object_in_image",
    #Mouse & Keyboard
    "MouseButton", "click_at", "move_mouse", "type_text", "press_key", "MouseKeyboardResult",
    #Clipboard
    "get_clipboard_text", "set_clipboard_text", "get_clipboard_image",
    "set_clipboard_image", "clear_clipboard", "ClipboardResult",
    #Terminal
    "execute_command", "execute_script", "get_environment",
    "change_directory", "kill_process", "TerminalResult",
    #Email
    "EmailAnalytics", "EmailAutomation", "EmailFilter", "EmailTemplateManager", "EmailSignatureManager", "EmailTool",
    "BaseTool", "DelayTool", "CreativeTool", "ProactiveTool", "PlayfulTool",
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