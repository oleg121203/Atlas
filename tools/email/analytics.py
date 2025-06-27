"""
Email Analytics Module for Atlas

This module provides tools for analyzing email campaign performance.
"""


class EmailAnalytics:
    def __init__(self):
        self.data = []

    def track_email(self, email_id, recipient, subject, sent_date):
        """Track an email that was sent."""
        self.data.append(
            {
                "email_id": email_id,
                "recipient": recipient,
                "subject": subject,
                "sent_date": sent_date,
                "opened": False,
                "clicked": False,
            }
        )

    def record_open(self, email_id):
        """Record when an email is opened."""
        for email in self.data:
            if email["email_id"] == email_id:
                email["opened"] = True
                break

    def record_click(self, email_id):
        """Record when a link in an email is clicked."""
        for email in self.data:
            if email["email_id"] == email_id:
                email["clicked"] = True
                break

    def get_open_rate(self):
        """Calculate the open rate for tracked emails."""
        if not self.data:
            return 0.0
        opened = sum(1 for email in self.data if email["opened"])
        return (opened / len(self.data)) * 100

    def get_click_rate(self):
        """Calculate the click-through rate for tracked emails."""
        if not self.data:
            return 0.0
        clicked = sum(1 for email in self.data if email["clicked"])
        return (clicked / len(self.data)) * 100
