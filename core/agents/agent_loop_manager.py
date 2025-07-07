"""
Agent Loop Manager for Atlas

This module implements the core agent loop that drives the autonomous behavior of the system.
It manages task execution, decision making, and event handling in a non-blocking way.
"""

import logging
import queue
import threading
from datetime import datetime
from typing import Any, Dict, Optional

from core.event_bus import EventBus
from core.intelligence.decision_engine import DecisionEngine
from core.tools.tool_manager import ToolManager
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class AgentLoopManager:
    """
    Manages the core agent execution loop.

    This class is responsible for:
    - Running the agent loop in a separate thread
    - Processing tasks from the task queue
    - Using DecisionEngine to choose appropriate tools
    - Executing tools through ToolManager
    - Publishing task status updates
    """

    def __init__(
        self,
        event_bus: EventBus,
        decision_engine: DecisionEngine,
        tool_manager: ToolManager,
        config_manager: Optional[ConfigManager] = None,
    ):
        self.event_bus = event_bus
        self.decision_engine = decision_engine
        self.tool_manager = tool_manager
        self.config_manager = config_manager or ConfigManager()

        self.task_queue = queue.PriorityQueue()
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None

        # Subscribe to task-related events
        self.event_bus.subscribe("TASK_CREATED", self._handle_new_task)
        logger.info("AgentLoopManager initialized")

    def start(self) -> None:
        """Start the agent loop in a background thread."""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(
                target=self._agent_loop, daemon=True, name="AgentLoop"
            )
            self.worker_thread.start()
            logger.info("Agent loop started")

    def stop(self) -> None:
        """Stop the agent loop."""
        if self.is_running:
            self.is_running = False
            if self.worker_thread:
                self.worker_thread.join()
                self.worker_thread = None
            logger.info("Agent loop stopped")

    def _handle_new_task(self, task: Dict[str, Any]) -> None:
        """Handle a new task event by adding it to the queue."""
        priority = task.get("priority", 0)
        # Add task to queue with priority (lower number = higher priority)
        self.task_queue.put((-priority, datetime.now(), task))
        logger.info(
            f"New task queued: {task.get('name', 'unnamed')} with priority {priority}"
        )

    def _agent_loop(self) -> None:
        """Main agent execution loop running in background thread."""
        while self.is_running:
            try:
                # Get next task from queue with timeout to allow checking is_running
                try:
                    _priority, _timestamp, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                try:
                    self._process_task(task)
                except Exception as e:
                    logger.error(f"Error processing task: {str(e)}", exc_info=True)
                    self.event_bus.publish(
                        "TASK_FAILED", task_id=task.get("id"), error=str(e)
                    )
                finally:
                    self.task_queue.task_done()

            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}", exc_info=True)
                # Brief sleep to prevent tight loop on repeated errors
                threading.Event().wait(1.0)

    def _process_task(self, task: Dict[str, Any]) -> None:
        """Process a task through the decision and execution pipeline.

        Args:
            task: Dictionary containing task details including id, name, goal, and context
        """
        task_id = task.get("id")
        self.event_bus.publish("TASK_STARTED", task_id=task_id)

        try:
            # Use DecisionEngine to select appropriate tool
            tool_decision = self.decision_engine.decide_tool(task)

            if not tool_decision or "tool_name" not in tool_decision:
                raise ValueError("No suitable tool found for task")

            # Extract tool details from decision
            tool_name = tool_decision["tool_name"]
            tool_args = tool_decision.get("tool_args", {})

            # Update task status
            self.event_bus.publish(
                "TASK_UPDATED",
                task_id=task_id,
                status="EXECUTING",
                tool=tool_name,
            )

            # Execute the tool
            result = self.tool_manager.execute_tool(
                tool_name=tool_name,
                arguments=tool_args,
                context=task.get("context", {}),
            )

            # Handle successful execution
            self.event_bus.publish(
                "TASK_COMPLETED",
                task_id=task_id,
                result=result,
                tool=tool_name,
            )

        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
            self.event_bus.publish(
                "TASK_FAILED",
                task_id=task_id,
                error=str(e),
            )
