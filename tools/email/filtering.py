from typing import Dict, List, Optional, Tuple, Any
import logging
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build

class EmailFilter:
    def __init__(self, service: build):
        self.service = service
        self.logger = logging.getLogger(__name__)

    def search_emails(self, 
                     query: str,
                     max_results: int = 50,
                     include_spam_trash: bool = False,
                     categories: Optional[List[str]] = None,
                     importance: Optional[str] = None,
                     attachment_types: Optional[List[str]] = None,
                     thread_length: Optional[Tuple[int, int]] = None,
                     response_time: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """Search emails with advanced filtering."""
        try:
            # Build search query
            search_query = query
            if not include_spam_trash:
                search_query += " -in:spam -in:trash"
            
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            detailed_messages = []
            for message in messages:
                email = self._get_email_content(message['id'])
                headers = email['payload'].get('headers', [])
                
                # Get thread details
                thread = self._get_thread(message['threadId'])
                
                # Analyze email
                analysis = self._analyze_email(email, headers, thread)
                
                # Apply filters
                if categories and analysis['category'] not in categories:
                    continue
                
                if importance and analysis['importance'] != importance:
                    continue
                
                if attachment_types:
                    attachment_mimes = [p.get('mimeType', 'unknown') for p in email['payload'].get('parts', []) 
                                      if p.get('filename')]
                    if not any(mime in attachment_types for mime in attachment_mimes):
                        continue
                
                if thread_length:
                    thread_len = len(thread['messages']) if thread else 0
                    if thread_len < thread_length[0] or thread_len > thread_length[1]:
                        continue
                
                if response_time:
                    if thread and len(thread['messages']) > 1:
                        messages = sorted(thread['messages'], 
                                        key=lambda m: m['internalDate'])
                        if len(messages) > 1:
                            response_time_minutes = (int(messages[1]['internalDate']) - 
                                                  int(messages[0]['internalDate'])) / (1000 * 60)
                            if response_time_minutes < response_time[0] or response_time_minutes > response_time[1]:
                                continue
                    else:
                        continue
                
                detailed_messages.append({
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'snippet': email.get('snippet', ''),
                    'headers': headers,
                    'labels': email.get('labelIds', []),
                    'attachments': len([p for p in email['payload'].get('parts', []) 
                                     if p.get('filename')]),
                    'analysis': analysis
                })
            
            return {
                "success": True,
                "data": {
                    "total_results": len(messages),
                    "filtered_results": len(detailed_messages),
                    "messages": detailed_messages
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to search emails: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_email(self, email: Dict[str, Any], headers: List[Dict[str, str]], 
                      thread: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze email content and metadata."""
        analysis = {
            'category': self._determine_category(email),
            'importance': self._determine_importance(email),
            'sentiment': self._analyze_sentiment(email),
            'attachment_types': [p.get('mimeType', 'unknown') for p in email['payload'].get('parts', []) 
                              if p.get('filename')],
            'thread_length': len(thread['messages']) if thread else 1,
            'response_time': self._calculate_response_time(thread) if thread else None,
            'read_status': 'INBOX' in email.get('labelIds', []),
            'has_attachments': any(p.get('filename') for p in email['payload'].get('parts', [])),
            'is_forwarded': self._is_forwarded(email),
            'is_reply': self._is_reply(email),
            'has_signature': self._detect_signature(email),
            'priority': self._calculate_priority(email)
        }
        
        return analysis

    def _determine_category(self, email: Dict[str, Any]) -> str:
        """Determine email category."""
        headers = email['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()
        
        categories = {
            'meeting': ['meeting', 'conference', 'call', 'zoom', 'teams'],
            'invoice': ['invoice', 'bill', 'payment', 'charge'],
            'notification': ['notification', 'alert', 'reminder'],
            'personal': ['personal', 'family', 'friend'],
            'work': ['work', 'job', 'project', 'task'],
            'promotion': ['promotion', 'offer', 'discount', 'sale'],
            'update': ['update', 'status', 'report', 'summary'],
            'social': ['social', 'network', 'linkedin', 'facebook'],
            'travel': ['travel', 'flight', 'hotel', 'booking'],
            'default': 'other'
        }
        
        for category, keywords in categories.items():
            if any(keyword in subject for keyword in keywords):
                return category
        
        return 'other'

    def _determine_importance(self, email: Dict[str, Any]) -> str:
        """Determine email importance level."""
        importance = 'normal'
        headers = email['payload'].get('headers', [])
        
        if any(h['value'].lower() == 'high' for h in headers if h['name'] == 'Importance'):
            importance = 'high'
        
        if any(h['value'].lower() == 'urgent' for h in headers if h['name'] == 'Priority'):
            importance = 'urgent'
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()
        if any(word in subject for word in ['urgent', 'immediate', 'asap', 'today']):
            importance = 'high'
        
        return importance

    def _analyze_sentiment(self, email: Dict[str, Any]) -> str:
        """Analyze email sentiment."""
        headers = email['payload'].get('headers', [])
        body = next((h['value'] for h in headers if h['name'] == 'Body'), '').lower()
        
        positive_words = ['thank', 'great', 'good', 'appreciate', 'helpful', 'satisfied']
        negative_words = ['problem', 'issue', 'concern', 'disappointed', 'frustrated', 'unsatisfied']
        
        positive_count = sum(1 for word in positive_words if word in body)
        negative_count = sum(1 for word in negative_words if word in body)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _calculate_response_time(self, thread: Dict[str, Any]) -> Optional[float]:
        """Calculate average response time in minutes."""
        if len(thread['messages']) < 2:
            return None
            
        messages = sorted(thread['messages'], key=lambda m: m['internalDate'])
        response_time = (int(messages[1]['internalDate']) - 
                       int(messages[0]['internalDate'])) / (1000 * 60)
        
        return response_time

    def _detect_signature(self, email: Dict[str, Any]) -> bool:
        """Detect if email contains a signature."""
        headers = email['payload'].get('headers', [])
        body = next((h['value'] for h in headers if h['name'] == 'Body'), '').lower()
        
        signature_patterns = [
            r'--\s*$',
            r'\s*regards?\s*$',
            r'\s*best\s*$',
            r'\s*sincerely\s*$',
            r'\s*thank\s*$',
            r'\s*from:\s*$',
            r'\s*signature\s*$',
            r'\s*\[\s*signature\s*\]\s*$',
            r'\s*\[\s*sig\s*\]\s*$'
        ]
        
        return any(re.search(pattern, body, re.IGNORECASE) for pattern in signature_patterns)

    def _is_forwarded(self, email: Dict[str, Any]) -> bool:
        """Check if email is forwarded."""
        headers = email['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()
        return 'fwd:' in subject

    def _is_reply(self, email: Dict[str, Any]) -> bool:
        """Check if email is a reply."""
        headers = email['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()
        return 're:' in subject

    def _calculate_priority(self, email: Dict[str, Any]) -> int:
        """Calculate email priority score."""
        score = 0
        headers = email['payload'].get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()
        if any(word in subject for word in ['urgent', 'immediate', 'asap', 'today']):
            score += 3
        
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '').lower()
        if '@google.com' in sender:
            score += 2
        
        if any(p.get('filename') for p in email['payload'].get('parts', [])):
            score += 1
        
        to = next((h['value'] for h in headers if h['name'] == 'To'), '')
        cc = next((h['value'] for h in headers if h['name'] == 'Cc'), '')
        if to and len(to.split(',')) > 1:
            score += 1
        if cc:
            score += 1
        
        return score

    def _get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get complete thread details."""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            return thread
        except Exception as e:
            self.logger.error(f"Failed to get thread: {e}")
            raise

    def _get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get detailed email content."""
        try:
            email = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            return email
        except Exception as e:
            self.logger.error(f"Failed to get email content: {e}")
            raise
