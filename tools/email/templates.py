from typing import Dict, Optional, List
import logging
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

class EmailTemplateManager:
    def __init__(self, service: build):
        self.service = service
        self.logger = logging.getLogger(__name__)
        self.templates = {}

    def create_template(self, 
                       name: str, 
                       subject: str, 
                       body: str, 
                       attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new email template."""
        try:
            # Create template data
            template = {
                'name': name,
                'subject': subject,
                'body': body,
                'attachments': attachments or [],
                'created_at': datetime.utcnow().isoformat(),
                'usage_count': 0
            }
            
            # Store template
            self.templates[name] = template
            
            return {
                "success": True,
                "data": template
            }
        except Exception as e:
            self.logger.error(f"Failed to create template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_template(self, name: str) -> Dict[str, Any]:
        """Get an email template by name."""
        try:
            template = self.templates.get(name)
            if not template:
                return {
                    "success": False,
                    "error": f"Template '{name}' not found"
                }
            
            return {
                "success": True,
                "data": template
            }
        except Exception as e:
            self.logger.error(f"Failed to get template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_templates(self) -> Dict[str, Any]:
        """List all available templates."""
        try:
            return {
                "success": True,
                "data": list(self.templates.values())
            }
        except Exception as e:
            self.logger.error(f"Failed to list templates: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_template(self, name: str) -> Dict[str, Any]:
        """Delete a template by name."""
        try:
            if name in self.templates:
                del self.templates[name]
            
            return {
                "success": True,
                "data": {
                    "message": f"Template '{name}' deleted"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to delete template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_from_template(self, 
                          template_name: str, 
                          recipients: List[str],
                          context: Dict[str, str]) -> Dict[str, Any]:
        """Send an email using a template."""
        try:
            # Get template
            template = self.templates.get(template_name)
            if not template:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' not found"
                }
            
            # Apply context
            subject = template['subject'].format(**context)
            body = template['body'].format(**context)
            
            # Create message
            message = MIMEText(body)
            message['to'] = ', '.join(recipients)
            message['subject'] = subject
            
            # Add attachments
            for attachment in template['attachments']:
                # TODO: Implement attachment handling
                pass
            
            # Convert to Gmail API format
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            # Update template usage
            template['usage_count'] += 1
            template['last_used'] = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "data": {
                    "message_id": sent_message['id'],
                    "template": template_name
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to send from template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
