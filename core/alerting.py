"""
Alerting system for the Atlas application.

This module provides mechanisms to notify users and developers of critical events,
performance issues, and errors through multiple channels.
"""

import logging
from typing import Callable, Dict, List, Optional
from datetime import datetime
import uuid

import json

try:
    from PySide6.QtWidgets import QMessageBox, QApplication, QWidget
    from PySide6.QtCore import Qt
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

try:
    import notify2
    NOTIFY2_AVAILABLE = True
except ImportError:
    NOTIFY2_AVAILABLE = False

try:
    from notifypy import Notify
    NOTIFYPY_AVAILABLE = True
except ImportError:
    NOTIFYPY_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import smtplib
    from email.mime.text import MIMEText
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

from core.config import get_config
from core.logging import get_logger

# Logger for alerting system
logger = get_logger("Alerting")

# Alert handlers for different channels
_ui_alert_handlers: List[Callable[[str, str, Dict], None]] = []
_email_alert_handlers: List[Callable[[str, str, Dict], None]] = []
_webhook_alert_handlers: List[Callable[[str, str, Dict], None]] = []
_desktop_alert_handlers: List[Callable[[str, str, Dict], None]] = []

# Alert severities
SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_ERROR = "ERROR"
SEVERITY_CRITICAL = "CRITICAL"

# Track if system is initialized
_initialized = False


def initialize_alerting() -> bool:
    """
    Initialize the alerting system based on available libraries and configuration.
    
    Returns:
        bool: True if at least one alerting mechanism is available
    """
    global _initialized
    if _initialized:
        return True
    
    config = get_config()
    alerting_config = config.get("alerting", {})
    
    # Check UI alerting (Qt)
    if QT_AVAILABLE and alerting_config.get("ui_alerts_enabled", True):
        _ui_alert_handlers.append(show_qt_alert)
        logger.info("Qt UI alerting enabled")
    else:
        logger.warning("Qt UI alerting unavailable - PySide6 not installed or disabled")
    
    # Check desktop notifications (notify2 for Linux)
    if NOTIFY2_AVAILABLE and alerting_config.get("desktop_notifications_enabled", True):
        try:
            notify2.init("Atlas")
            _desktop_alert_handlers.append(show_notify2_alert)
            logger.info("notify2 desktop alerting enabled")
        except Exception as e:
            logger.error("Failed to initialize notify2: %s", str(e))
    else:
        logger.warning("notify2 desktop alerting unavailable or disabled")
    
    # Check desktop notifications (notifypy for cross-platform)
    if NOTIFYPY_AVAILABLE and alerting_config.get("desktop_notifications_enabled", True):
        _desktop_alert_handlers.append(show_notifypy_alert)
        logger.info("notifypy desktop alerting enabled")
    else:
        logger.warning("notifypy desktop alerting unavailable or disabled")
    
    # Check email alerting
    if SMTP_AVAILABLE and alerting_config.get("email_alerts_enabled", False):
        email_config = alerting_config.get("email", {})
        if email_config.get("smtp_server") and email_config.get("from_address"):
            _email_alert_handlers.append(send_email_alert)
            logger.info("Email alerting enabled")
        else:
            logger.warning("Email alerting disabled - incomplete configuration")
    else:
        logger.warning("Email alerting unavailable - SMTP libraries not installed or disabled")
    
    # Check webhook alerting
    if REQUESTS_AVAILABLE and alerting_config.get("webhook_alerts_enabled", False):
        webhook_url = alerting_config.get("webhook_url", "")
        if webhook_url:
            _webhook_alert_handlers.append(send_webhook_alert)
            logger.info("Webhook alerting enabled")
        else:
            logger.warning("Webhook alerting disabled - no webhook URL configured")
    else:
        logger.warning("Webhook alerting unavailable - requests library not installed or disabled")
    
    _initialized = True
    total_handlers = (len(_ui_alert_handlers) + len(_desktop_alert_handlers) + 
                      len(_email_alert_handlers) + len(_webhook_alert_handlers))
    if total_handlers > 0:
        logger.info("Alerting system initialized with %d handler(s)", total_handlers)
        return True
    else:
        logger.error("Alerting system failed to initialize - no alerting mechanisms available")
        return False


def show_qt_alert(title: str, message: str, data: Dict) -> None:
    """
    Show alert using Qt QMessageBox.
    
    Args:
        title: Alert title
        message: Alert message
        data: Additional data for the alert
    """
    severity = data.get("severity", SEVERITY_WARNING)
    app = QApplication.instance()
    if not app:
        logger.warning("Cannot show Qt alert - no QApplication instance")
        return
    
    # Determine icon based on severity
    if severity == SEVERITY_INFO:
        icon = QMessageBox.Icon.Information
    elif severity == SEVERITY_WARNING:
        icon = QMessageBox.Icon.Warning
    elif severity in (SEVERITY_ERROR, SEVERITY_CRITICAL):
        icon = QMessageBox.Icon.Critical
    else:
        icon = QMessageBox.Icon.Warning
    
    # Find active window or create a new one
    parent = None
    if hasattr(app, "activeWindow") and app.activeWindow():
        parent = app.activeWindow()
    elif app.topLevelWidgets():
        parent = next((w for w in app.topLevelWidgets() if isinstance(w, QWidget)), None)
    
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    
    logger.info("Showing Qt alert: %s - %s", title, message)
    msg_box.exec()


def show_notify2_alert(title: str, message: str, data: Dict) -> None:
    """
    Show desktop notification using notify2 (Linux).
    
    Args:
        title: Alert title
        message: Alert message
        data: Additional data for the alert
    """
    severity = data.get("severity", SEVERITY_WARNING)
    urgency = {
        SEVERITY_INFO: notify2.URGENCY_LOW,
        SEVERITY_WARNING: notify2.URGENCY_NORMAL,
        SEVERITY_ERROR: notify2.URGENCY_CRITICAL,
        SEVERITY_CRITICAL: notify2.URGENCY_CRITICAL
    }.get(severity, notify2.URGENCY_NORMAL)
    
    notification = notify2.Notification(title, message)
    notification.set_urgency(urgency)
    try:
        notification.show()
        logger.info("Showing notify2 alert: %s - %s", title, message)
    except Exception as e:
        logger.error("Failed to show notify2 alert: %s", str(e))


def show_notifypy_alert(title: str, message: str, data: Dict) -> None:
    """
    Show desktop notification using notifypy (cross-platform).
    
    Args:
        title: Alert title
        message: Alert message
        data: Additional data for the alert
    """
    severity = data.get("severity", SEVERITY_WARNING)
    urgency = {
        SEVERITY_INFO: "low",
        SEVERITY_WARNING: "normal",
        SEVERITY_ERROR: "high",
        SEVERITY_CRITICAL: "high"
    }.get(severity, "normal")
    
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.urgency = urgency
    notification.application_name = "Atlas"
    
    try:
        notification.send()
        logger.info("Showing notifypy alert: %s - %s", title, message)
    except Exception as e:
        logger.error("Failed to show notifypy alert: %s", str(e))


def send_email_alert(title: str, message: str, data: Dict) -> None:
    """
    Send alert via email.
    
    Args:
        title: Alert title
        message: Alert message
        data: Additional data for the alert
    """
    config = get_config()
    email_config = config.get("alerting", {}).get("email", {})
    smtp_server = email_config.get("smtp_server", "")
    smtp_port = email_config.get("smtp_port", 587)
    from_address = email_config.get("from_address", "")
    to_addresses = email_config.get("to_addresses", [])
    username = email_config.get("username", "")
    password = email_config.get("password", "")
    
    if not to_addresses:
        logger.warning("Cannot send email alert - no recipients configured")
        return
    
    # Prepare email content
    severity = data.get("severity", SEVERITY_WARNING)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[Atlas {severity}] {title} - {timestamp}"
    body = f"Timestamp: {timestamp}\n"
    body += f"Severity: {severity}\n"
    body += f"Title: {title}\n\n"
    body += f"{message}\n\n"
    body += f"Additional Data:\n{json.dumps(data, indent=2)}"
    
    # Create MIME text
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addresses if isinstance(to_addresses, list) else [to_addresses])
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(from_address, to_addresses, msg.as_string())
        logger.info("Email alert sent: %s", subject)
    except Exception as e:
        logger.error("Failed to send email alert: %s", str(e))


def send_webhook_alert(title: str, message: str, data: Dict) -> None:
    """
    Send alert via webhook (HTTP POST).
    
    Args:
        title: Alert title
        message: Alert message
        data: Additional data for the alert
    """
    config = get_config()
    webhook_url = config.get("alerting", {}).get("webhook_url", "")
    if not webhook_url:
        logger.warning("Cannot send webhook alert - no URL configured")
        return
    
    severity = data.get("severity", SEVERITY_WARNING)
    timestamp = datetime.now().isoformat()
    payload = {
        "timestamp": timestamp,
        "severity": severity,
        "title": title,
        "message": message,
        "data": data
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Webhook alert sent: %s", title)
        else:
            logger.error("Webhook alert failed with status %d: %s", response.status_code, response.text)
    except Exception as e:
        logger.error("Failed to send webhook alert: %s", str(e))


def alert(title: str, message: str, severity: str = SEVERITY_WARNING, 
          data: Optional[Dict] = None) -> bool:
    """
    Send an alert through all configured channels.
    
    Args:
        title: Alert title
        message: Alert message
        severity: Alert severity (INFO, WARNING, ERROR, CRITICAL)
        data: Additional data for the alert
        
    Returns:
        bool: True if at least one alert channel succeeded
    """
    if not _initialized:
        initialize_alerting()
    
    full_data = data or {}
    full_data["severity"] = severity
    full_data["timestamp"] = datetime.now().isoformat()
    
    logger.log({
        SEVERITY_INFO: logging.INFO,
        SEVERITY_WARNING: logging.WARNING,
        SEVERITY_ERROR: logging.ERROR,
        SEVERITY_CRITICAL: logging.CRITICAL
    }.get(severity, logging.WARNING), "ALERT: %s - %s", title, message)
    
    success_count = 0
    total_channels = 0
    
    # Send to UI handlers
    total_channels += len(_ui_alert_handlers)
    for handler in _ui_alert_handlers:
        try:
            handler(title, message, full_data)
            success_count += 1
        except Exception as e:
            logger.error("UI alert handler failed: %s", str(e))
    
    # Send to desktop notification handlers
    total_channels += len(_desktop_alert_handlers)
    for handler in _desktop_alert_handlers:
        try:
            handler(title, message, full_data)
            success_count += 1
        except Exception as e:
            logger.error("Desktop alert handler failed: %s", str(e))
    
    # Send to email handlers (only for ERROR and CRITICAL by default)
    if severity in (SEVERITY_ERROR, SEVERITY_CRITICAL) or \
       get_config().get("alerting", {}).get("email_on_all_alerts", False):
        total_channels += len(_email_alert_handlers)
        for handler in _email_alert_handlers:
            try:
                handler(title, message, full_data)
                success_count += 1
            except Exception as e:
                logger.error("Email alert handler failed: %s", str(e))
    
    # Send to webhook handlers (only for ERROR and CRITICAL by default)
    if severity in (SEVERITY_ERROR, SEVERITY_CRITICAL) or \
       get_config().get("alerting", {}).get("webhook_on_all_alerts", False):
        total_channels += len(_webhook_alert_handlers)
        for handler in _webhook_alert_handlers:
            try:
                handler(title, message, full_data)
                success_count += 1
            except Exception as e:
                logger.error("Webhook alert handler failed: %s", str(e))
    
    if total_channels == 0:
        logger.warning("No alert channels available for: %s", title)
        return False
        
    logger.debug("Alert sent to %d/%d channels: %s", success_count, total_channels, title)
    return success_count > 0


def raise_alert(message: str, severity: str = SEVERITY_INFO, component: Optional[str] = None, 
                details: Optional[dict] = None) -> None:
    """
    Raise an alert with the specified message and severity.
    
    Args:
        message (str): The alert message
        severity (str): Severity level (INFO, WARNING, ERROR, CRITICAL)
        component (str, optional): Component raising the alert
        details (dict, optional): Additional structured data about the alert
    """
    alert_data = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'severity': severity,
        'component': component or 'unspecified',
        'details': details or {}
    }
    logger.log({
        SEVERITY_INFO: logging.INFO,
        SEVERITY_WARNING: logging.WARNING,
        SEVERITY_ERROR: logging.ERROR,
        SEVERITY_CRITICAL: logging.CRITICAL
    }.get(severity, logging.WARNING), f"Alert [{severity}]: {message}")
    for handler in _ui_alert_handlers + _desktop_alert_handlers + _email_alert_handlers + _webhook_alert_handlers:
        try:
            handler(alert_data)
        except Exception as e:
            logger.error(f"Error in alert handler: {e}")


def register_ui_alert_handler(handler: Callable[[str, str, Dict], None]) -> None:
    """
    Register a custom UI alert handler.
    
    Args:
        handler: Function taking title, message, and data arguments
    """
    _ui_alert_handlers.append(handler)
    logger.debug("Registered custom UI alert handler")


def register_desktop_alert_handler(handler: Callable[[str, str, Dict], None]) -> None:
    """
    Register a custom desktop notification handler.
    
    Args:
        handler: Function taking title, message, and data arguments
    """
    _desktop_alert_handlers.append(handler)
    logger.debug("Registered custom desktop alert handler")


def register_email_alert_handler(handler: Callable[[str, str, Dict], None]) -> None:
    """
    Register a custom email alert handler.
    
    Args:
        handler: Function taking title, message, and data arguments
    """
    _email_alert_handlers.append(handler)
    logger.debug("Registered custom email alert handler")


def register_webhook_alert_handler(handler: Callable[[str, str, Dict], None]) -> None:
    """
    Register a custom webhook alert handler.
    
    Args:
        handler: Function taking title, message, and data arguments
    """
    _webhook_alert_handlers.append(handler)
    logger.debug("Registered custom webhook alert handler")
