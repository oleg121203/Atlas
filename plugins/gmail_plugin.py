"""
Gmail Plugin for Atlas

This plugin provides Gmail integration using the active provider in the chat system.
It can search emails, read email content, and extract email metadata.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base_plugin import BasePlugin, PluginMetadata, PluginResult

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class GmailPlugin(BasePlugin):
    """Gmail integration plugin for Atlas."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.service = None
        self.credentials = None
        self.is_authenticated = False
        
        # Gmail API scopes
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="gmail",
            version="1.0.0",
            description="Gmail integration for email search and analysis",
            author="Atlas Team",
            category="email",
            tags=["gmail", "email", "search", "security"],
            dependencies=["google-auth-oauthlib", "google-auth-httplib2", "google-api-python-client"],
            config_schema={
                "credentials_path": {"type": "string", "default": "credentials.json"},
                "token_path": {"type": "string", "default": "token.json"},
                "max_results": {"type": "integer", "default": 50},
                "days_back": {"type": "integer", "default": 30}
            }
        )
    
    def initialize(self, provider: Any) -> bool:
        """Initialize the plugin with the active provider."""
        try:
            if not GMAIL_AVAILABLE:
                self.logger.error("Gmail API libraries not available")
                return False
            
            # Store the provider for potential use
            self.active_provider = provider
            
            # Try to authenticate
            auth_result = self._authenticate()
            if auth_result["success"]:
                self.is_authenticated = True
                self.logger.info("Gmail plugin initialized successfully")
                return True
            else:
                self.logger.error(f"Gmail authentication failed: {auth_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail plugin: {e}")
            return False
    
    def execute(self, command: str, **kwargs) -> PluginResult:
        """Execute a Gmail plugin command."""
        if not self.is_authenticated:
            return PluginResult(
                success=False,
                error="Gmail plugin not authenticated"
            )
        
        try:
            if command == "search_emails":
                return self._search_emails(**kwargs)
            elif command == "search_security_emails":
                return self._search_security_emails(**kwargs)
            elif command == "get_email_content":
                return self._get_email_content(**kwargs)
            elif command == "list_labels":
                return self._list_labels(**kwargs)
            elif command == "authenticate":
                return self._authenticate_result()
            else:
                return PluginResult(
                    success=False,
                    error=f"Unknown command: {command}"
                )
                
        except Exception as e:
            self.logger.error(f"Error executing Gmail command {command}: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def get_commands(self) -> List[str]:
        """Get list of available commands."""
        return [
            "search_emails",
            "search_security_emails", 
            "get_email_content",
            "list_labels",
            "authenticate"
        ]
    
    def get_help(self) -> str:
        """Get help information for the plugin."""
        help_text = f"""
Gmail Plugin Help
=================

Description: {self.metadata.description}

Available Commands:
- search_emails: Search for emails with a specific query
- search_security_emails: Search for security-related emails
- get_email_content: Get the content of a specific email
- list_labels: List all Gmail labels
- authenticate: Check authentication status

Usage Examples:
- search_emails(query="is:important", max_results=10)
- search_security_emails(days_back=7)
- get_email_content(email_id="12345")
- list_labels()

Authentication: {self.is_authenticated}
        """
        return help_text.strip()
    
    def _authenticate(self) -> Dict[str, Any]:
        """Authenticate with Gmail API."""
        if not GMAIL_AVAILABLE:
            return {
                "success": False,
                "error": "Gmail API libraries not available"
            }
        
        try:
            # Look for credentials
            credentials_path = self.config.get("credentials_path", "credentials.json")
            possible_paths = [
                credentials_path,
                "gmail_credentials.json",
                "config/credentials.json",
                os.path.expanduser("~/.atlas/gmail_credentials.json")
            ]
            
            creds_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    creds_path = path
                    break
            
            if not creds_path:
                return {
                    "success": False,
                    "error": "Gmail credentials not found"
                }
            
            # Load credentials
            creds = None
            token_path = self.config.get("token_path", "token.json")
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.credentials = creds
            
            return {
                "success": True,
                "message": "Successfully authenticated with Gmail API"
            }
            
        except Exception as e:
            self.logger.error(f"Gmail authentication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _authenticate_result(self) -> PluginResult:
        """Return authentication status."""
        return PluginResult(
            success=self.is_authenticated,
            data={
                "authenticated": self.is_authenticated,
                "service_available": self.service is not None
            }
        )
    
    def _search_emails(self, query: str, max_results: int = 50) -> PluginResult:
        """Search emails using Gmail API."""
        try:
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return PluginResult(
                    success=True,
                    data={
                        "emails": [],
                        "count": 0,
                        "query": query
                    },
                    metadata={"message": f"No emails found for query: {query}"}
                )
            
            # Get detailed information for each email
            email_details = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date', 'To']
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Parse date
                try:
                    parsed_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = date
                
                email_details.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'date': formatted_date,
                    'snippet': msg.get('snippet', ''),
                    'threadId': msg.get('threadId', '')
                })
            
            # Sort by date (newest first)
            email_details.sort(key=lambda x: x['date'], reverse=True)
            
            return PluginResult(
                success=True,
                data={
                    "emails": email_details,
                    "count": len(email_details),
                    "query": query
                },
                metadata={"message": f"Found {len(email_details)} emails for query: {query}"}
            )
            
        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            return PluginResult(
                success=False,
                error=f"Gmail API request failed: {error}"
            )
        except Exception as e:
            self.logger.error(f"Email search failed: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def _search_security_emails(self, days_back: int = 30) -> PluginResult:
        """Search for security-related emails."""
        try:
            # Create security-focused search query
            date_filter = f"after:{(datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')}"
            
            security_queries = [
                f"{date_filter} (security OR password OR login OR account OR verification OR 2fa OR two-factor)",
                f"{date_filter} from:(noreply@accounts.google.com OR security@google.com)",
                f"{date_filter} subject:(security OR password OR login OR account)",
                f"{date_filter} (Google Account OR Gmail security OR account security)"
            ]
            
            all_results = []
            
            for query in security_queries:
                result = self._search_emails(query, max_results=20)
                if result.success and result.data["emails"]:
                    all_results.extend(result.data["emails"])
            
            # Remove duplicates based on email ID
            unique_emails = {}
            for email in all_results:
                if email['id'] not in unique_emails:
                    unique_emails[email['id']] = email
            
            unique_results = list(unique_emails.values())
            unique_results.sort(key=lambda x: x['date'], reverse=True)
            
            return PluginResult(
                success=True,
                data={
                    "emails": unique_results,
                    "count": len(unique_results),
                    "query": "Security-related emails"
                },
                metadata={"message": f"Found {len(unique_results)} security-related emails from the last {days_back} days"}
            )
            
        except Exception as e:
            self.logger.error(f"Security email search failed: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def _get_email_content(self, email_id: str) -> PluginResult:
        """Get full content of an email."""
        try:
            # Get full message
            message = self.service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract body content
            body = self._extract_email_body(message['payload'])
            
            return PluginResult(
                success=True,
                data={
                    "id": email_id,
                    "subject": subject,
                    "from": sender,
                    "date": date,
                    "body": body
                },
                metadata={"message": "Email content retrieved successfully"}
            )
            
        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            return PluginResult(
                success=False,
                error=f"Gmail API request failed: {error}"
            )
        except Exception as e:
            self.logger.error(f"Email content retrieval failed: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        import base64
        import re
        
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        # Simple HTML to text conversion
                        text_content = re.sub(r'<[^>]+>', '', html_content)
                        return text_content
        
        return "No readable content found"
    
    def _list_labels(self) -> PluginResult:
        """List all Gmail labels."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            return PluginResult(
                success=True,
                data={
                    "labels": [label['name'] for label in labels],
                    "count": len(labels)
                },
                metadata={"message": f"Found {len(labels)} Gmail labels"}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to list Gmail labels: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )

# Plugin registration function
def register_gmail_plugin(config: Optional[Dict[str, Any]] = None) -> bool:
    """Register the Gmail plugin."""
    from .base_plugin import register_plugin
    
    plugin = GmailPlugin(config)
    return register_plugin(plugin) 