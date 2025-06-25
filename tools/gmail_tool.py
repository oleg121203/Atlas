"""
Gmail API Tool for Atlas

This tool provides real Gmail integration using the Gmail API.
It can search emails, read email content, and extract email metadata.
"""

import os
import json
import base64
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import re

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logging.warning("Gmail API libraries not available. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailTool:
    """Gmail API integration tool for Atlas."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.is_authenticated = False
        
    def authenticate(self, credentials_path: str = None) -> Dict[str, Any]:
        """
        Authenticate with Gmail API.
        
        Args:
            credentials_path: Path to credentials.json file
            
        Returns:
            Dict with authentication status and message
        """
        if not GMAIL_AVAILABLE:
            return {
                "success": False,
                "error": "Gmail API libraries not available. Install required packages.",
                "message": "Please install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            }
        
        try:
            # Look for credentials in common locations
            if not credentials_path:
                possible_paths = [
                    "credentials.json",
                    "gmail_credentials.json", 
                    "config/credentials.json",
                    os.path.expanduser("~/.atlas/gmail_credentials.json")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        credentials_path = path
                        break
            
            if not credentials_path or not os.path.exists(credentials_path):
                return {
                    "success": False,
                    "error": "Gmail credentials not found",
                    "message": "Please provide a valid credentials.json file from Google Cloud Console"
                }
            
            # Load credentials
            creds = None
            token_path = "token.json"
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.credentials = creds
            self.is_authenticated = True
            
            return {
                "success": True,
                "message": "Successfully authenticated with Gmail API",
                "service": "Gmail API v1"
            }
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to authenticate with Gmail API"
            }
    
    def search_emails(self, query: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search emails using Gmail API.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict with search results
        """
        if not self.is_authenticated or not self.service:
            auth_result = self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
        try:
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return {
                    "success": True,
                    "results": [],
                    "count": 0,
                    "query": query,
                    "message": f"No emails found for query: {query}"
                }
            
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
                except ValueError:
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
            
            return {
                "success": True,
                "results": email_details,
                "count": len(email_details),
                "query": query,
                "message": f"Found {len(email_details)} emails for query: {query}"
            }
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                "success": False,
                "error": str(error),
                "message": "Gmail API request failed"
            }
        except Exception as e:
            logger.error(f"Email search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to search emails"
            }
    
    def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """
        Get full content of an email.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            Dict with email content
        """
        if not self.is_authenticated or not self.service:
            auth_result = self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
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
            
            return {
                "success": True,
                "id": email_id,
                "subject": subject,
                "from": sender,
                "date": date,
                "body": body,
                "message": "Email content retrieved successfully"
            }
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                "success": False,
                "error": str(error),
                "message": "Gmail API request failed"
            }
        except Exception as e:
            logger.error(f"Email content retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get email content"
            }
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
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
    
    def search_security_emails(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Search for security-related emails.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dict with security email results
        """
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
            result = self.search_emails(query, max_results=20)
            if result["success"] and result["results"]:
                all_results.extend(result["results"])
        
        # Remove duplicates based on email ID
        unique_emails = {}
        for email in all_results:
            if email['id'] not in unique_emails:
                unique_emails[email['id']] = email
        
        unique_results = list(unique_emails.values())
        unique_results.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "success": True,
            "results": unique_results,
            "count": len(unique_results),
            "query": "Security-related emails",
            "message": f"Found {len(unique_results)} security-related emails from the last {days_back} days"
        }

# Global Gmail tool instance
_gmail_tool = None

def get_gmail_tool() -> GmailTool:
    """Get or create Gmail tool instance."""
    global _gmail_tool
    if _gmail_tool is None:
        _gmail_tool = GmailTool()
    return _gmail_tool

def authenticate_gmail(credentials_path: str = None) -> str:
    """Authenticate with Gmail API."""
    tool = get_gmail_tool()
    result = tool.authenticate(credentials_path)
    return json.dumps(result, indent=2)

def search_gmail_emails(query: str, max_results: int = 50) -> str:
    """Search emails in Gmail."""
    tool = get_gmail_tool()
    result = tool.search_emails(query, max_results)
    return json.dumps(result, indent=2)

def get_gmail_email_content(email_id: str) -> str:
    """Get content of a specific email."""
    tool = get_gmail_tool()
    result = tool.get_email_content(email_id)
    return json.dumps(result, indent=2)

def search_gmail_security_emails(days_back: int = 30) -> str:
    """Search for security-related emails in Gmail."""
    tool = get_gmail_tool()
    result = tool.search_security_emails(days_back)
    return json.dumps(result, indent=2)

def list_gmail_labels() -> str:
    """List all Gmail labels."""
    tool = get_gmail_tool()
    if not tool.is_authenticated or not tool.service:
        auth_result = tool.authenticate()
        if not auth_result["success"]:
            return json.dumps(auth_result, indent=2)
    
    try:
        results = tool.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        return json.dumps({
            "success": True,
            "labels": [label['name'] for label in labels],
            "count": len(labels),
            "message": f"Found {len(labels)} Gmail labels"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to list Gmail labels"
        }, indent=2)

if __name__ == "__main__":
    # Test the Gmail tool
    print("Testing Gmail Tool...")
    
    tool = GmailTool()
    
    # Test authentication
    print("\n1. Testing authentication...")
    auth_result = tool.authenticate()
    print(json.dumps(auth_result, indent=2))
    
    if auth_result["success"]:
        # Test security email search
        print("\n2. Testing security email search...")
        security_result = tool.search_security_emails(days_back=7)
        print(json.dumps(security_result, indent=2))
        
        # Test general search
        print("\n3. Testing general email search...")
        search_result = tool.search_emails("is:important", max_results=5)
        print(json.dumps(search_result, indent=2)) 