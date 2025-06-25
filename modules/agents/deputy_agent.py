"""Deputy Agent for background monitoring and anomaly detection."""

import threading
import time
from typing import Any, Dict

from modules.agents.base_agent import BaseAgent
from utils.logger import LOG_FILE_PATH


class DeputyAgent(BaseAgent):
    """Monitors logs for anomalies and reports issues."""

    def __init__(self):
        super().__init__("Deputy Agent")
        self.is_running = False
        self.thread = None
        self.state_lock = threading.Lock()

    def start(self):
        """Starts the agent's execution loop in a new thread."""
        with self.state_lock:
            if self.is_running:
                self.logger.warning("Deputy Agent is already running.")
                return

            self.is_running = True
            self.thread = threading.Thread(target=self._monitoring_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("Deputy Agent started monitoring.")

    def stop(self):
        """Stops the agent's execution loop."""
        with self.state_lock:
            if not self.is_running:
                return
            self.is_running = False
        self.logger.info("Deputy Agent stopping...")

    def _monitoring_loop(self):
        """The core loop where the agent monitors the log file."""
        self.logger.info("Deputy Agent monitoring loop started.")
        try:
            with open(LOG_FILE_PATH) as f:
                f.seek(0, 2)  #Go to the end of the file
                while self.is_running:
                    line = f.readline()
                    if not line:
                        time.sleep(1)  #Wait for new lines
                        continue

                    if "ERROR" in line:
                        self.logger.warning(f"Anomaly Detected! Log entry: {line.strip()}")
                        #In a real scenario, this would trigger a more complex response.

        except FileNotFoundError:
            self.logger.error(f"Log file not found at {LOG_FILE_PATH}. Deputy Agent cannot monitor.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in the monitoring loop: {e}")

        self.logger.info("Deputy Agent monitoring loop finished.")

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """Deputy agent does not execute direct tasks, it only monitors."""
        return "Deputy Agent is a monitoring agent and does not accept direct tasks."
