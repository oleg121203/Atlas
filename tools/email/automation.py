from typing import Dict, Optional, List, Any
import logging
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json

class EmailAutomation:
    def __init__(self, service: Any):
        self.service = service
        self.logger = logging.getLogger(__name__)
        self.workflows = {}
        self.templates = {}
        self.scheduled_emails = {}

    def create_workflow(self, 
                       name: str, 
                       triggers: List[Dict[str, Any]], 
                       actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new email workflow."""
        try:
            # Validate triggers and actions
            if not self._validate_workflow(triggers, actions):
                return {
                    "success": False,
                    "error": "Invalid workflow structure"
                }

            # Create workflow
            workflow = {
                'id': f"wf_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                'name': name,
                'triggers': triggers,
                'actions': actions,
                'created_at': datetime.utcnow().isoformat(),
                'last_run': None,
                'run_count': 0,
                'status': 'active'
            }
            
            # Store workflow
            self.workflows[workflow['id']] = workflow
            
            return {
                "success": True,
                "data": workflow
            }
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_workflows(self) -> Dict[str, Any]:
        """List all available workflows."""
        try:
            workflows = list(self.workflows.values())
            return {
                "success": True,
                "data": {
                    "total": len(workflows),
                    "workflows": workflows
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to list workflows: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_template(self, 
                       name: str, 
                       subject: str, 
                       body: str, 
                       placeholders: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new email template."""
        try:
            template_id = f"tmpl_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            template = {
                'id': template_id,
                'name': name,
                'subject': subject,
                'body': body,
                'placeholders': placeholders or {},
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.templates[template_id] = template
            
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

    def send_email_from_template(self, 
                               template_id: str, 
                               recipients: List[str], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using a saved template."""
        try:
            template = self.templates.get(template_id)
            if not template:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found"
                }

            # Replace placeholders
            subject = template['subject']
            body = template['body']
            
            for placeholder, value in context.items():
                subject = subject.replace(f"{{{{{placeholder}}}}}", str(value))
                body = body.replace(f"{{{{{placeholder}}}}}", str(value))

            # Create email
            message = MIMEMultipart()
            message['to'] = ", ".join(recipients)
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Send email
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            self.logger.error(f"Failed to send email from template: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _validate_workflow(self, triggers: List[Dict[str, Any]], actions: List[Dict[str, Any]]) -> bool:
        """Validate workflow structure."""
        try:
            # Validate triggers
            for trigger in triggers:
                if not all(key in trigger for key in ['type', 'conditions']):
                    return False
                    
            # Validate actions
            for action in actions:
                if not 'type' in action:
                    return False
                    
                if action['type'] == 'auto_reply':
                    if not all(key in action for key in ['to', 'subject', 'body']):
                        return False
                elif action['type'] == 'forward':
                    if not all(key in action for key in ['to', 'email_id']):
                        return False
                elif action['type'] == 'label':
                    if not 'label_name' in action:
                        return False
                    
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate workflow: {e}")
            return False

    def delete_workflow(self, name: str) -> Dict[str, Any]:
        """Delete a workflow by name."""
        try:
            if name in self.workflows:
                del self.workflows[name]
            
            return {
                "success": True,
                "data": {
                    "message": f"Workflow '{name}' deleted"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to delete workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_workflow(self, name: str) -> Dict[str, Any]:
        """Run a workflow."""
        try:
            workflow = self.workflows.get(name)
            if not workflow:
                return {
                    "success": False,
                    "error": f"Workflow '{name}' not found"
                }
            
            # Check triggers
            for trigger in workflow['triggers']:
                if not self._check_trigger(trigger):
                    return {
                        "success": False,
                        "error": "Trigger conditions not met"
                    }
            
            # Execute actions
            results = []
            for action in workflow['actions']:
                result = self._execute_action(action)
                results.append(result)
            
            # Update workflow stats
            workflow['last_run'] = datetime.utcnow().isoformat()
            workflow['run_count'] += 1
            
            return {
                "success": True,
                "data": {
                    "results": results,
                    "workflow": workflow
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to run workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def schedule_email(self, 
                      email_data: Dict[str, Any], 
                      schedule_time: str, 
                      timezone: str = "UTC") -> Dict[str, Any]:
        """Schedule an email to be sent at a specific time."""
        try:
            # Create scheduled email
            scheduled_email = {
                'email': email_data,
                'schedule_time': schedule_time,
                'timezone': timezone,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Store scheduled email
            self.scheduled_emails[scheduled_email['id']] = scheduled_email
            
            return {
                "success": True,
                "data": scheduled_email
            }
        except Exception as e:
            self.logger.error(f"Failed to schedule email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _check_trigger(self, trigger: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met."""
        try:
            # Check time-based triggers
            if trigger.get('type') == 'time':
                current_time = datetime.utcnow()
                trigger_time = datetime.fromisoformat(trigger['time'])
                return current_time >= trigger_time
                
            # Check email-based triggers
            if trigger.get('type') == 'email':
                # Check for new emails matching criteria
                results = self.service.users().messages().list(
                    userId='me',
                    q=trigger['query']
                ).execute()
                return bool(results.get('messages', []))
                
            return False
        except Exception as e:
            self.logger.error(f"Failed to check trigger: {e}")
            return False

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action."""
        try:
            if action.get('type') == 'send_email':
                return self._send_email(action['data'])
            
            if action.get('type') == 'label_email':
                return self._label_email(action['data'])
            
            if action.get('type') == 'forward_email':
                return self._forward_email(action['data'])
            
            return {
                "success": False,
                "error": f"Unknown action type: {action.get('type')}"
            }
        except Exception as e:
            self.logger.error(f"Failed to execute action: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email."""
        try:
            # Create message
            message = MIMEText(email_data['body'])
            message['to'] = email_data['to']
            message['subject'] = email_data['subject']
            
            # Convert to Gmail API format
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {
                "success": True,
                "data": {
                    "message_id": sent_message['id']
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _label_email(self, label_data: Dict[str, Any]) -> Dict[str, Any]:
        """Label an email."""
        try:
            # Get email
            email = self.service.users().messages().get(
                userId='me',
                id=label_data['email_id']
            ).execute()
            
            # Add label
            labels = email.get('labelIds', [])
            if label_data['label_id'] not in labels:
                labels.append(label_data['label_id'])
                
                # Update email
                self.service.users().messages().modify(
                    userId='me',
                    id=label_data['email_id'],
                    body={'addLabelIds': [label_data['label_id']]}
                ).execute()
            
            return {
                "success": True,
                "data": {
                    "email_id": label_data['email_id'],
                    "label_id": label_data['label_id']
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to label email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _forward_email(self, forward_data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward an email."""
        try:
            # Get email
            email = self.service.users().messages().get(
                userId='me',
                id=forward_data['email_id']
            ).execute()
            
            # Create forward message
            message = MIMEText(f"Forwarded message:\n\n{email['snippet']}")
            message['to'] = forward_data['to']
            message['subject'] = f"FW: {email['payload'].get('headers', [])[0].get('value', '')}"
            
            # Convert to Gmail API format
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send forwarded email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {
                "success": True,
                "data": {
                    "message_id": sent_message['id']
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to forward email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
