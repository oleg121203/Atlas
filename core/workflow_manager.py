"""
Workflow Manager for Atlas

Manages workflow execution, state persistence, and error recovery.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from core.alerting import raise_alert
from core.logging import get_logger

logger = get_logger("WorkflowManager")


class WorkflowManager:
    """Manages workflows, including execution, persistence, and error recovery."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Workflow Manager.

        Args:
            config (Dict[str, Any]): Configuration for workflow management.
        """
        self.config = config
        self.workflows: Dict[str, Dict] = {}
        self.workflow_states_dir = config.get("workflow_states_dir", "workflows/states")
        self.current_workflow_id: Optional[str] = None
        logger.info("WorkflowManager initialized")

    def create_workflow(self, workflow_id: str, definition: Dict) -> bool:
        """Create a new workflow with the given definition.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            definition (Dict): Workflow definition including steps and transitions.

        Returns:
            bool: True if creation successful, False otherwise.
        """
        try:
            if workflow_id in self.workflows:
                logger.warning(f"Workflow {workflow_id} already exists, overwriting")
                raise_alert(
                    "warning",
                    f"Workflow Overwrite: {workflow_id}",
                    "Existing workflow overwritten with new definition",
                )

            self.workflows[workflow_id] = {
                "definition": definition,
                "state": {
                    "current_step": definition.get("initial_step", "start"),
                    "status": "created",
                    "last_updated": datetime.now().isoformat(),
                    "error": None,
                    "retry_count": 0,
                },
                "history": [],
            }
            logger.info(f"Workflow {workflow_id} created successfully")
            self._persist_workflow_state(workflow_id)
            return True
        except Exception as e:
            logger.error(f"Failed to create workflow {workflow_id}: {str(e)}")
            raise_alert("error", f"Workflow Creation Failed: {workflow_id}", str(e))
            return False

    def start_workflow(self, workflow_id: str) -> bool:
        """Start execution of a workflow.

        Args:
            workflow_id (str): ID of the workflow to start.

        Returns:
            bool: True if start successful, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                raise_alert(
                    "error",
                    f"Workflow Not Found: {workflow_id}",
                    "Cannot start non-existent workflow",
                )
                return False

            workflow = self.workflows[workflow_id]
            workflow["state"]["status"] = "running"
            workflow["state"]["last_updated"] = datetime.now().isoformat()
            self.current_workflow_id = workflow_id
            logger.info(f"Workflow {workflow_id} started")
            self._persist_workflow_state(workflow_id)
            return True
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {str(e)}")
            raise_alert("error", f"Workflow Start Failed: {workflow_id}", str(e))
            return False

    def execute_step(self, workflow_id: str, step_id: Optional[str] = None) -> bool:
        """Execute a specific step in a workflow.

        Args:
            workflow_id (str): ID of the workflow.
            step_id (Optional[str]): Specific step to execute, if None use current step.

        Returns:
            bool: True if step executed successfully, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                raise_alert(
                    "error",
                    f"Workflow Not Found: {workflow_id}",
                    "Cannot execute step in non-existent workflow",
                )
                return False

            workflow = self.workflows[workflow_id]
            current_step = step_id if step_id else workflow["state"]["current_step"]
            step_definition = workflow["definition"]["steps"].get(current_step)

            if not step_definition:
                logger.error(f"Step {current_step} not found in workflow {workflow_id}")
                raise_alert(
                    "error",
                    f"Step Not Found: {current_step}",
                    f"Step not defined in workflow {workflow_id}",
                )
                return False

            logger.info(f"Executing step {current_step} in workflow {workflow_id}")
            # Simulate step execution (in real implementation, this would call the actual step logic)
            result = self._simulate_step_execution(step_definition)

            # Update workflow state based on result
            if result["success"]:
                workflow["state"]["current_step"] = step_definition.get(
                    "next_step", "end"
                )
                workflow["state"]["status"] = (
                    "running"
                    if workflow["state"]["current_step"] != "end"
                    else "completed"
                )
                workflow["state"]["error"] = None
                workflow["state"]["retry_count"] = 0
            else:
                workflow["state"]["status"] = "error"
                workflow["state"]["error"] = result["error"]
                workflow["state"]["retry_count"] += 1
                raise_alert(
                    "error", f"Step Execution Failed: {current_step}", result["error"]
                )

            workflow["state"]["last_updated"] = datetime.now().isoformat()
            workflow["history"].append(
                {
                    "step": current_step,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(
                f"Step {current_step} execution {'succeeded' if result['success'] else 'failed'} in workflow {workflow_id}"
            )
            self._persist_workflow_state(workflow_id)
            return result["success"]
        except Exception as e:
            logger.error(
                f"Error executing step {step_id or 'current'} in workflow {workflow_id}: {str(e)}"
            )
            raise_alert("error", f"Step Execution Error: {workflow_id}", str(e))
            return False

    def retry_step(self, workflow_id: str) -> bool:
        """Retry the current step in a workflow after an error.

        Args:
            workflow_id (str): ID of the workflow to retry.

        Returns:
            bool: True if retry successful, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                raise_alert(
                    "error",
                    f"Workflow Not Found: {workflow_id}",
                    "Cannot retry non-existent workflow",
                )
                return False

            workflow = self.workflows[workflow_id]
            max_retries = self.config.get("max_retries", 3)
            if workflow["state"]["retry_count"] >= max_retries:
                logger.error(f"Max retries reached for workflow {workflow_id}")
                raise_alert(
                    "error",
                    f"Max Retries Reached: {workflow_id}",
                    f"Workflow has reached maximum retry limit of {max_retries}",
                )
                workflow["state"]["status"] = "failed"
                self._persist_workflow_state(workflow_id)
                return False

            logger.info(
                f"Retrying step {workflow['state']['current_step']} in workflow {workflow_id}"
            )
            return self.execute_step(workflow_id)
        except Exception as e:
            logger.error(f"Failed to retry step in workflow {workflow_id}: {str(e)}")
            raise_alert("error", f"Retry Failed: {workflow_id}", str(e))
            return False

    def rollback_workflow(self, workflow_id: str) -> bool:
        """Rollback a workflow to the last successful step.

        Args:
            workflow_id (str): ID of the workflow to rollback.

        Returns:
            bool: True if rollback successful, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                raise_alert(
                    "error",
                    f"Workflow Not Found: {workflow_id}",
                    "Cannot rollback non-existent workflow",
                )
                return False

            workflow = self.workflows[workflow_id]
            # Find last successful step in history
            last_successful = None
            for entry in reversed(workflow["history"]):
                if entry["result"]["success"]:
                    last_successful = entry["step"]
                    break

            if last_successful:
                workflow["state"]["current_step"] = last_successful
                workflow["state"]["status"] = "running"
                workflow["state"]["error"] = None
                workflow["state"]["retry_count"] = 0
                workflow["state"]["last_updated"] = datetime.now().isoformat()
                logger.info(
                    f"Workflow {workflow_id} rolled back to step {last_successful}"
                )
                raise_alert(
                    "info",
                    f"Workflow Rolled Back: {workflow_id}",
                    f"Rolled back to last successful step: {last_successful}",
                )
                self._persist_workflow_state(workflow_id)
                return True
            else:
                logger.warning(
                    f"No successful step found to rollback workflow {workflow_id}"
                )
                raise_alert(
                    "warning",
                    f"Rollback Failed: {workflow_id}",
                    "No successful step found in history to rollback to",
                )
                workflow["state"]["status"] = "failed"
                self._persist_workflow_state(workflow_id)
                return False
        except Exception as e:
            logger.error(f"Failed to rollback workflow {workflow_id}: {str(e)}")
            raise_alert("error", f"Rollback Error: {workflow_id}", str(e))
            return False

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict]:
        """Get the current state of a workflow.

        Args:
            workflow_id (str): ID of the workflow.

        Returns:
            Optional[Dict]: Current state of the workflow, or None if not found.
        """
        return self.workflows.get(workflow_id, {}).get("state")

    def load_workflow_state(self, workflow_id: str) -> bool:
        """Load workflow state from persistence.

        Args:
            workflow_id (str): ID of the workflow to load.

        Returns:
            bool: True if load successful, False otherwise.
        """
        try:
            state_file = os.path.join(self.workflow_states_dir, f"{workflow_id}.json")
            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    state_data = json.load(f)
                    if workflow_id in self.workflows:
                        self.workflows[workflow_id].update(state_data)
                    else:
                        self.workflows[workflow_id] = state_data
                    logger.info(f"Workflow state loaded for {workflow_id}")
                    return True
            else:
                logger.warning(f"No state file found for workflow {workflow_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to load workflow state for {workflow_id}: {str(e)}")
            raise_alert("error", f"State Load Failed: {workflow_id}", str(e))
            return False

    def _persist_workflow_state(self, workflow_id: str) -> bool:
        """Persist workflow state to disk with transactional integrity.

        Args:
            workflow_id (str): ID of the workflow to persist.

        Returns:
            bool: True if persistence successful, False otherwise.
        """
        try:
            os.makedirs(self.workflow_states_dir, exist_ok=True)
            state_file = os.path.join(self.workflow_states_dir, f"{workflow_id}.json")
            temp_file = state_file + ".tmp"

            # Write to temporary file first
            with open(temp_file, "w") as f:
                json.dump(self.workflows[workflow_id], f, indent=2)

            # Atomically replace the original file
            os.replace(temp_file, state_file)
            logger.debug(f"Workflow state persisted for {workflow_id}")
            return True
        except Exception as e:
            logger.error(
                f"Failed to persist workflow state for {workflow_id}: {str(e)}"
            )
            raise_alert("error", f"State Persistence Failed: {workflow_id}", str(e))
            return False

    def _simulate_step_execution(self, step_definition: Dict) -> Dict:
        """Simulate step execution for testing purposes.

        Args:
            step_definition (Dict): Definition of the step to simulate.

        Returns:
            Dict: Result of the simulated execution.
        """
        # In a real implementation, this would execute the actual step logic
        should_fail = step_definition.get("simulate_failure", False)
        if should_fail:
            return {"success": False, "error": "Simulated step failure"}
        return {"success": True, "data": "Simulated step success"}
