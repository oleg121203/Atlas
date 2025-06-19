"""Security Agent for real-time monitoring and threat interception."""

import multiprocessing
import re
import time
from typing import Any, Dict, List, Tuple, Optional

from logger import get_logger
from tools.notification_tool import NotificationManager


class SecurityAgent(multiprocessing.Process):
    """Monitors actions for security violations in a separate process."""

    def __init__(self, pipe_conn, config_manager=None):
        super().__init__(daemon=True)
        self.pipe_conn = pipe_conn
        self.config_manager = config_manager
        self.is_running = multiprocessing.Value('b', True)
        self.logger = get_logger()
        self.rules: List[str] = []
        self.notification_manager = NotificationManager()
        self.notification_channels = {
            "email": False, "telegram": False, "sms": False
        }
        self.memory_manager = None  # Will be initialized in run()

    def run(self):
        """The main execution loop for the security agent process."""
        self.logger.info("Security Agent process started.")
        
        # Initialize memory manager in process context
        if self.config_manager:
            try:
                from agents.llm_manager import LLMManager
                from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
                
                llm_manager = LLMManager(self.config_manager)
                self.memory_manager = EnhancedMemoryManager(llm_manager, self.config_manager)
                self.logger.info("Security Agent memory manager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize memory manager: {e}")
        
        while self.is_running.value:
            try:
                if self.pipe_conn.poll(timeout=1):  # Wait for an event
                    event = self.pipe_conn.recv()
                    log_event = event if event.get("type") != "UPDATE_RULES" else {**event, "details": "..."}
                    self.logger.info(f"Security Agent received event: {log_event}")
                    self._evaluate_event(event)
                else:
                    # No event, continue loop
                    continue
            except (EOFError, BrokenPipeError):
                self.logger.warning("Connection pipe was closed. Shutting down Security Agent.")
                break
            except Exception as e:
                self.logger.error(f"An unexpected error occurred in Security Agent: {e}")
                time.sleep(1)

        self.logger.info("Security Agent process finished.")

    def stop(self):
        """Signals the agent to stop its execution loop."""
        self.logger.info("Security Agent stopping...")
        self.is_running.value = False
        self.pipe_conn.close()

    def _evaluate_event(self, event: Dict[str, Any]):
        """Evaluates an event or updates internal state based on event type."""
        event_type = event.get("type")
        details = event.get("details", {})

        if event_type == "UPDATE_RULES":
            self.rules = details.get("rules", [])
            self.logger.info(f"Security rules updated. {len(self.rules)} rules loaded.")
            return  # No response needed for rule updates

        elif event_type == "UPDATE_NOTIFICATION_SETTINGS":
            self.notification_channels = details.get("channels", {})
            self.logger.info(f"Notification settings updated: {self.notification_channels}")
            return

        elif event_type == "GOAL_EXECUTION_REQUEST":
            self.logger.info(f"Evaluating goal execution request...")
            is_allowed, reason = self._check_rules(event)

            if is_allowed:
                response = {"action": "ALLOW", "event_type": event_type}
            else:
                response = {"action": "BLOCK", "event_type": event_type, "reason": reason}
            self.pipe_conn.send(response)

        else:
            self.logger.warning(f"Received unhandled event type: {event_type}")
            response = {"action": "ALLOW", "event_type": event_type, "reason": "Unhandled event type"}
            self.pipe_conn.send(response)

    def _check_rules(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Checks the given event against the loaded security rules.
        Returns a tuple of (is_allowed, reason).
        """
        goal = event.get("details", {}).get("goal", "")

        for rule_str in self.rules:
            if not rule_str.strip() or rule_str.startswith('#'):
                continue  # Skip empty lines and comments

            try:
                parts = rule_str.split(',', 2)
                if len(parts) != 3:
                    self.logger.warning(f"Skipping malformed rule: {rule_str}")
                    continue

                action, _, pattern = [p.strip() for p in parts]
                action = action.upper()

                if re.search(pattern, goal, re.IGNORECASE):
                    if action == "DENY":
                        reason = f"Execution blocked by rule: '{pattern}'"
                        self.logger.warning(reason)
                        self._send_notifications(reason)
                        
                        # Store security event in memory
                        if self.memory_manager:
                            try:
                                from agents.enhanced_memory_manager import MemoryScope, MemoryType
                                self.memory_manager.add_memory_for_agent(
                                    agent_type=MemoryScope.SECURITY_AGENT,
                                    memory_type=MemoryType.ERROR,
                                    content=f"BLOCKED: {goal} - Rule: {pattern}",
                                    metadata={
                                        "action": "DENY",
                                        "rule_pattern": pattern,
                                        "blocked_goal": goal,
                                        "event_type": event.get("type", "unknown")
                                    }
                                )
                            except Exception as e:
                                self.logger.error(f"Failed to store security event: {e}")
                        
                        return False, reason
            except re.error as e:
                self.logger.error(f"Invalid regex in rule '{rule_str}': {e}")
                continue

        return True, "All security rules passed."

    def _send_notifications(self, reason: str):
        """Sends notifications based on enabled channels."""
        subject = "Atlas Security Alert"
        body = f"An action was blocked by the Atlas Security Agent.\n\nReason: {reason}"

        if self.notification_channels.get("email"):
            # Placeholder recipient
            self.notification_manager.send_email(subject, body, "admin@example.com")
        if self.notification_channels.get("telegram"):
            # Placeholder chat_id
            self.notification_manager.send_telegram(body, "-123456789")
        if self.notification_channels.get("sms"):
            # Placeholder phone number
            self.notification_manager.send_sms(body, "+15551234567")
