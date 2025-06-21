"""Provides a unified interface for sending notifications via different channels."""

from utils.logger import get_logger


class NotificationManager:
    """Handles the sending of notifications for security alerts."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def send_email(self, subject: str, body: str, recipient: str) -> None:
        """Placeholder for sending an email notification."""
        #In a real implementation, this would use smtplib or an email API.
        self.logger.info(f"SIMULATING EMAIL NOTIFICATION to {recipient}:")
        self.logger.info(f"  Subject: {subject}")
        self.logger.info(f"  Body: {body}")

    def send_telegram(self, message: str, chat_id: str) -> None:
        """Placeholder for sending a Telegram notification."""
        #In a real implementation, this would use the Telegram Bot API.
        self.logger.info(f"SIMULATING TELEGRAM NOTIFICATION to chat_id {chat_id}:")
        self.logger.info(f"  Message: {message}")

    def send_sms(self, message: str, phone_number: str) -> None:
        """Placeholder for sending an SMS notification."""
        #In a real implementation, this would use an SMS gateway like Twilio.
        self.logger.info(f"SIMULATING SMS NOTIFICATION to {phone_number}:")
        self.logger.info(f"  Message: {message}")
