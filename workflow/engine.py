"""
Workflow Execution Engine

This module provides the core functionality for executing workflows in Atlas.
It implements transactional execution, error handling, logging, and state persistence.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self, db_path: str = "workflow_state.db"):
        """Initialize the Workflow Engine with a database for state persistence.

        Args:
            db_path (str): Path to the SQLite database for storing workflow state.
        """
        self.db_path = db_path
        self.conn = None
        self.current_workflow_id = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize the SQLite database for workflow state persistence."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_state (
                    workflow_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    last_updated TIMESTAMP
                )
            """)
            self.conn.commit()
            logger.info("Database initialized for workflow state persistence.")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def start_workflow(self, workflow_id: str, initial_state: Dict[str, Any]) -> None:
        """Start a new workflow with the given ID and initial state.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            initial_state (Dict[str, Any]): Initial state of the workflow.
        """
        self.current_workflow_id = workflow_id
        try:
            cursor = self.conn.cursor()
            state_json = json.dumps(initial_state)
            cursor.execute(
                """
                INSERT OR REPLACE INTO workflow_state (workflow_id, state, last_updated)
                VALUES (?, ?, ?)
            """,
                (workflow_id, state_json, datetime.now()),
            )
            self.conn.commit()
            logger.info(f"Started workflow {workflow_id} with initial state.")
        except sqlite3.Error as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            self.conn.rollback()
            raise

    def execute_action(self, action: callable, *args, **kwargs) -> Any:
        """Execute a single action within the current workflow transactionally.

        Args:
            action (callable): The action to execute.
            *args: Positional arguments to pass to the action.
            **kwargs: Keyword arguments to pass to the action.

        Returns:
            Any: Result of the action execution.

        Raises:
            Exception: If the action fails, rollback the transaction and re-raise the exception.
        """
        if not self.current_workflow_id:
            raise ValueError("No active workflow. Call start_workflow() first.")

        try:
            result = action(*args, **kwargs)
            logger.info(
                f"Successfully executed action in workflow {self.current_workflow_id}"
            )
            return result
        except Exception as e:
            logger.error(f"Action failed in workflow {self.current_workflow_id}: {e}")
            self.conn.rollback()
            raise

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update the state of the current workflow.

        Args:
            new_state (Dict[str, Any]): New state to save for the workflow.
        """
        if not self.current_workflow_id:
            raise ValueError("No active workflow. Call start_workflow() first.")

        try:
            cursor = self.conn.cursor()
            state_json = json.dumps(new_state)
            cursor.execute(
                """
                UPDATE workflow_state
                SET state = ?, last_updated = ?
                WHERE workflow_id = ?
            """,
                (state_json, datetime.now(), self.current_workflow_id),
            )
            self.conn.commit()
            logger.info(f"Updated state for workflow {self.current_workflow_id}")
        except sqlite3.Error as e:
            logger.error(
                f"Failed to update state for workflow {self.current_workflow_id}: {e}"
            )
            self.conn.rollback()
            raise

    def recover_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Recover the state of a previously started workflow.

        Args:
            workflow_id (str): Unique identifier of the workflow to recover.

        Returns:
            Optional[Dict[str, Any]]: The recovered state if found, None otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT state FROM workflow_state WHERE workflow_id = ?", (workflow_id,)
            )
            result = cursor.fetchone()
            if result:
                state = json.loads(result[0])
                self.current_workflow_id = workflow_id
                logger.info(f"Recovered workflow {workflow_id} with state.")
                return state
            logger.warning(f"No state found for workflow {workflow_id}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to recover workflow {workflow_id}: {e}")
            raise

    def complete_workflow(self) -> None:
        """Mark the current workflow as completed and clean up."""
        if not self.current_workflow_id:
            raise ValueError("No active workflow. Call start_workflow() first.")

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM workflow_state WHERE workflow_id = ?",
                (self.current_workflow_id,),
            )
            self.conn.commit()
            logger.info(f"Completed and cleaned up workflow {self.current_workflow_id}")
            self.current_workflow_id = None
        except sqlite3.Error as e:
            logger.error(f"Failed to complete workflow {self.current_workflow_id}: {e}")
            self.conn.rollback()
            raise

    def execute_workflow_plan(
        self, plan: list, initial_state: dict, continue_on_error: bool = False
    ) -> dict:
        """
        Execute a workflow plan (list of steps), each step is a dict: {'tool_name': str, 'params': dict}.
        Args:
            plan: List of workflow steps.
            initial_state: Initial workflow state.
            continue_on_error: If True, workflow continues after error; else stops.
        Returns:
            dict: Final state with results and errors.
        """
        from agents.self_regeneration_manager import self_regeneration_manager

        state = initial_state.copy()
        results = []
        errors = []
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_workflow(workflow_id, state)
        for idx, step in enumerate(plan):
            tool_name = step.get("tool_name")
            params = step.get("params", {})
            logger.info(f"[Workflow] Step {idx + 1}/{len(plan)}: {tool_name}({params})")
            try:
                result = self.execute_action(
                    self_regeneration_manager.execute_tool, tool_name, params
                )
                results.append({"step": idx + 1, "tool": tool_name, "result": result})
                state[f"step_{idx + 1}"] = result
                self.update_state(state)
                if not result.get("success", True) and not continue_on_error:
                    logger.error(
                        f"[Workflow] Step {idx + 1} failed, stopping workflow."
                    )
                    errors.append({"step": idx + 1, "tool": tool_name, "error": result})
                    break
            except Exception as e:
                logger.error(f"[Workflow] Exception in step {idx + 1}: {e}")
                errors.append({"step": idx + 1, "tool": tool_name, "error": str(e)})
                if not continue_on_error:
                    break
        self.complete_workflow()
        return {"results": results, "errors": errors, "final_state": state}

    def __del__(self):
        """Cleanup database connection on object destruction."""
        if self.conn:
            self.conn.close()
            logger.info("Closed database connection for WorkflowEngine.")
