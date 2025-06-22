from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import base64

class EmailAnalytics:
    def __init__(self, service: Any):
        """Initialize EmailAnalytics with Gmail service."""
        self.service = service
        self.logger = logging.getLogger(__name__)
        self.category_patterns = {
            'security': [
                r'password reset',
                r'security alert',
                r'account verification',
                r'login attempt',
                r'suspicious activity',
                r'account update',
                r'security update',
                r'2fa',
                r'two-factor'
            ],
            'promotion': [
                r'discount',
                r'offer',
                r'promotion',
                r'sale',
                r'newsletter',
                r'update',
                r'news',
                r'event'
            ],
            'transaction': [
                r'purchase confirmation',
                r'order confirmation',
                r'receipt',
                r'invoice',
                r'payment',
                r'billing',
                r'charge',
                r'refund'
            ],
            'notification': [
                r'notification',
                r'alert',
                r'update',
                r'reminder'
            ],
            'other': [
                r'general',
                r'information',
                r'other'
            ]
        }

    def analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email content and extract metadata.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Dictionary with email analysis results
        """
        try:
            thread = self._get_thread(email)
            analysis = {
                'category': self._determine_category(email),
                'sentiment': self._analyze_sentiment(email),
                'priority': self._determine_priority(email),
                'thread': thread,
                'response_time': self._calculate_response_time(thread),
                'is_forwarded': self._is_forwarded(email),
                'is_reply': self._is_reply(email),
                'has_signature': self._detect_signature(email)
            }
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing email: {e}")
            return {'error': str(e)}

    def _determine_category(self, email: Dict[str, Any]) -> str:
        """Determine email category based on content.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Category string
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            body = email.get('snippet', '')
            
            content = f"{subject} {body}".lower()
            
            for category, patterns in self.category_patterns.items():
                if any(re.search(pattern, content) for pattern in patterns):
                    return category
            
            return 'other'
        except Exception as e:
            self.logger.error(f"Error determining category: {e}")
            return 'other'

    def _analyze_sentiment(self, email: Dict[str, Any]) -> str:
        """Analyze email sentiment.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Sentiment string ('positive', 'negative', or 'neutral')
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            body = email.get('snippet', '')
            
            content = f"{subject} {body}".lower()
            
            positive_words = ['great', 'good', 'excellent', 'happy', 'satisfied', 'thank', 'appreciate']
            negative_words = ['bad', 'poor', 'unsatisfactory', 'disappointed', 'complaint', 'issue', 'problem']
            
            pos_count = sum(1 for word in positive_words if word in content)
            neg_count = sum(1 for word in negative_words if word in content)
            
            if pos_count > neg_count:
                return 'positive'
            elif neg_count > pos_count:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return 'neutral'

    def _determine_priority(self, email: Dict[str, Any]) -> str:
        """Determine email priority.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Priority string ('high', 'normal', or 'low')
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '').lower()
            
            if any(word in subject for word in [
                'urgent', 'important', 'immediate', 
                'high priority', 'critical', 'emergency',
                'action required', 'response needed'
            ]):
                return 'high'
            elif any(word in subject for word in [
                'normal', 'regular', 'standard',
                'information', 'update', 'notification'
            ]):
                return 'normal'
            else:
                return 'low'
        except Exception as e:
            self.logger.error(f"Error determining priority: {e}")
            return 'normal'

    def _get_thread(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Get email thread history.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Thread dictionary with messages and metadata
        """
        try:
            thread_id = email.get('threadId')
            if not thread_id:
                return {'messages': []}
            
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = sorted(thread.get('messages', []), 
                            key=lambda x: x.get('internalDate', 0))
            
            return {
                'messages': messages,
                'length': len(messages),
                'last_message_date': messages[-1].get('internalDate') if messages else None
            }
        except Exception as e:
            self.logger.error(f"Error getting thread: {e}")
            return {'messages': []}

    def _calculate_response_time(self, thread: Dict[str, Any]) -> Optional[int]:
        """Calculate response time in minutes.
        
        Args:
            thread: Thread dictionary
            
        Returns:
            Response time in minutes or None if not calculable
        """
        try:
            messages = thread.get('messages', [])
            if len(messages) < 2:
                return None
            
            first_msg = messages[0]
            last_msg = messages[-1]
            
            if not first_msg.get('internalDate') or not last_msg.get('internalDate'):
                return None
            
            time_diff = (int(last_msg['internalDate']) - 
                        int(first_msg['internalDate'])) / (1000 * 60)
            return int(time_diff)
        except Exception as e:
            self.logger.error(f"Error calculating response time: {e}")
            return None

    def _is_forwarded(self, email: Dict[str, Any]) -> bool:
        """Check if email is forwarded.
        
        Args:
            email: Email message dictionary
            
        Returns:
            True if email is forwarded, False otherwise
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            return any(h['name'].lower() == 'x-forwarded-for' for h in headers)
        except Exception as e:
            self.logger.error(f"Error checking forwarded status: {e}")
            return False

    def _is_reply(self, email: Dict[str, Any]) -> bool:
        """Check if email is a reply.
        
        Args:
            email: Email message dictionary
            
        Returns:
            True if email is a reply, False otherwise
        """
        try:
            headers = email.get('payload', {}).get('headers', [])
            return any(h['name'].lower() == 'in-reply-to' for h in headers)
        except Exception as e:
            self.logger.error(f"Error checking reply status: {e}")
            return False

    def _detect_signature(self, email: Dict[str, Any]) -> bool:
        """Detect email signature.
        
        Args:
            email: Email message dictionary
            
        Returns:
            True if signature is detected, False otherwise
        """
        try:
            body = email.get('snippet', '').lower()
            signature_keywords = ['regards', 'sincerely', 'best regards', 'thanks', 'signature']
            return any(keyword in body for keyword in signature_keywords)
        except Exception as e:
            self.logger.error(f"Error detecting signature: {e}")
            return False

    def _get_thread_by_id(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get complete thread details by thread ID."""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            return thread
        except Exception as e:
            self.logger.error(f"Failed to get thread: {e}")
            return None

    def _get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get detailed email content."""
        try:
            email = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            return email
        except Exception as e:
            self.logger.error(f"Error getting email content: {e}")
            raise

    def get_email_statistics(self, 
                           time_range: Optional[tuple] = None,
                           categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive email statistics."""
        try:
            # Build query
            query = ""
            if time_range:
                start_date = datetime.fromisoformat(time_range[0])
                end_date = datetime.fromisoformat(time_range[1])
                query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"

            # Get emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=1000
            ).execute()

            messages = results.get('messages', [])
            
            # Analyze emails
            stats = {
                'total_emails': len(messages),
                'categories': {},
                'senders': {},
                'recipients': {},
                'attachments': {},
                'time_distribution': {},
                'response_times': [],
                'conversation_lengths': [],
                'engagement_metrics': {
                    'unique_contacts': set(),
                    'attachments_sent': 0,
                    'attachments_received': 0,
                    'emails_sent': 0,
                    'emails_received': 0
                }
            }

            for message in messages:
                email = self._get_email_content(message['id'])
                headers = email['payload'].get('headers', [])
                
                # Get thread details
                thread = self._get_thread(email)
                
                # Analyze email
                analysis = self.analyze_email(email)
                
                # Update statistics
                if analysis['category'] not in stats['categories']:
                    stats['categories'][analysis['category']] = 0
                stats['categories'][analysis['category']] += 1

                # Update engagement metrics
                if analysis['priority'] == 'high':
                    stats['engagement_metrics']['emails_received'] += 1
                else:
                    stats['engagement_metrics']['emails_sent'] += 1

                if analysis.get('attachments'):
                    if analysis['priority'] == 'high':
                        stats['engagement_metrics']['attachments_received'] += 1
                    else:
                        stats['engagement_metrics']['attachments_sent'] += 1

                # Update time distribution
                date = datetime.fromtimestamp(int(email['internalDate'])/1000)
                hour = date.hour
                if hour not in stats['time_distribution']:
                    stats['time_distribution'][hour] = 0
                stats['time_distribution'][hour] += 1

                # Update response times
                if thread and len(thread.get('messages', [])) > 1:
                    response_time = analysis['response_time']
                    if response_time:
                        stats['response_times'].append(response_time)

            # Calculate additional metrics
            stats['average_response_time'] = (sum(stats['response_times']) / 
                                            len(stats['response_times'])) if stats['response_times'] else 0
            stats['average_conversation_length'] = (sum(stats['conversation_lengths']) / 
                                                 len(stats['conversation_lengths'])) if stats['conversation_lengths'] else 0
            stats['engagement_metrics']['unique_contacts'] = len(stats['engagement_metrics']['unique_contacts'])

            return {
                "success": True,
                "data": stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get email statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email content and metadata."""
        try:
            headers = email.get('payload', {}).get('headers', [])
            thread = self._get_thread(email)
            
            analysis = {
                'category': self._detect_category(email),
                'attachments': any(p.get('filename') for p in email.get('payload', {}).get('parts', [])),
                'is_forwarded': any(h['name'].lower() == 'x-forwarded-for' for h in headers),
                'is_reply': any(h['name'].lower() == 'in-reply-to' for h in headers),
                'thread_length': len(thread.get('messages', [])) if thread else 1,
                'response_time': self._calculate_response_time(thread),
                'sentiment': self._analyze_sentiment(email),
                'priority': self._determine_priority(email),
                'subject': self._get_header(email, 'Subject'),
                'from': self._get_header(email, 'From'),
                'to': self._get_header(email, 'To'),
                'date': self._get_header(email, 'Date'),
                'keywords': self._extract_keywords(email)
            }
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing email: {e}")
            return {
                'error': str(e)
            }

    def _detect_category(self, email: Dict[str, Any]) -> str:
        """Detect email category based on content."""
        try:
            headers = email.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '').lower()
            
            categories = {
                'meeting': ['meeting', 'conference', 'call', 'zoom', 'teams'],
                'invoice': ['invoice', 'bill', 'payment', 'charge'],
                'notification': ['notification', 'alert', 'reminder'],
                'personal': ['personal', 'family', 'friend'],
                'work': ['work', 'job', 'project', 'task'],
                'promotion': ['promotion', 'offer', 'discount', 'sale'],
                'update': ['update', 'status', 'report', 'summary'],
                'social': ['social', 'network', 'linkedin', 'facebook'],
                'travel': ['travel', 'flight', 'hotel', 'booking']
            }
            
            for category, keywords in categories.items():
                if any(keyword in subject for keyword in keywords):
                    return category
            
            return 'other'
        except Exception as e:
            self.logger.error(f"Error detecting category: {e}")
            return 'other'

    def _get_header(self, email: Dict[str, Any], header_name: str) -> str:
        """Get email header value."""
        try:
            headers = email.get('payload', {}).get('headers', [])
            return next((h['value'] for h in headers if h['name'].lower() == header_name.lower()), '')
        except Exception as e:
            self.logger.error(f"Error getting header {header_name}: {e}")
            return ''

    def _extract_keywords(self, email: Dict[str, Any]) -> List[str]:
        """Extract keywords from email content."""
        try:
            headers = email.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            body = email.get('snippet', '')
            
            content = f"{subject} {body}".lower()
            
            # Simple keyword extraction - split by spaces and filter common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            words = content.split()
            keywords = [word for word in words if len(word) > 3 and word not in common_words]
            
            return list(set(keywords))[:10]  # Return top 10 unique keywords
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
