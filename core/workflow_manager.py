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

    def execute_step(self, workflow_id: str, step_id: str) -> bool:
        """
        Execute a specific step in a workflow.

        Args:
            workflow_id (str): The unique identifier of the workflow.
            step_id (str): The identifier of the step to execute.

        Returns:
            bool: True if the step was executed successfully, False otherwise.
        """
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False

        workflow = self.workflows[workflow_id]
        if workflow["state"]["current_step"] != step_id:
            logger.warning(
                f"Step {step_id} is not the current step in workflow {workflow_id}"
            )
            return False

        # Mark the current step as completed
        workflow["state"]["status"] = "in_progress"
        workflow["state"]["last_updated"] = datetime.now().isoformat()
        workflow["history"].append(
            {
                "step": step_id,
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Simulate step execution
        result = self._execute_step_logic(workflow, step_id)
        if result["success"]:
            # Determine the next step
            steps = workflow["definition"].get("steps", [])
            current_step_index = steps.index(step_id) if step_id in steps else -1
            if current_step_index >= 0 and current_step_index < len(steps) - 1:
                workflow["state"]["current_step"] = steps[current_step_index + 1]
            else:
                workflow["state"]["current_step"] = ""
                workflow["state"]["status"] = "completed"
            workflow["history"][-1]["status"] = "completed"
        else:
            workflow["state"]["status"] = "failed"
            workflow["state"]["error"] = result.get("error", "Unknown error")
            workflow["state"]["retry_count"] += 1
            workflow["history"][-1]["status"] = "failed"
            logger.error(
                f"Step {step_id} failed in workflow {workflow_id}: {workflow['state']['error']}"
            )
            raise_alert(
                "error",
                f"Step Failed: {step_id} in {workflow_id}",
                workflow["state"]["error"],
            )

        self._persist_workflow_state(workflow_id)
        return result["success"]

    def update_workflow_state(self, workflow_id: str, new_state: dict) -> bool:
        """
        Update the state of a workflow.

        Args:
            workflow_id (str): The unique identifier of the workflow.
            new_state (dict): The new state to set for the workflow.

        Returns:
            bool: True if the state was updated successfully, False otherwise.
        """
        if workflow_id not in self.workflows:
            return False

        self.workflows[workflow_id]["state"] = new_state
        return True

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
            return self.execute_step(workflow_id, workflow["state"]["current_step"])
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
                if entry["status"] == "completed":
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

    def _execute_step_logic(self, workflow: Dict, step_id: str) -> Dict:
        """Execute the logic for a specific step in a workflow.

        Args:
            workflow (Dict): The workflow definition.
            step_id (str): The ID of the step to execute.

        Returns:
            Dict: Result of the step execution.
        """
        # In a real implementation, this would execute the actual step logic
        step_def = workflow["definition"].get("step_definitions", {}).get(step_id, {})
        return self._simulate_step_execution(step_def)

    def execute_workflow(self, workflow_id: str) -> bool:
        """
        Execute an entire workflow from start to finish or resume from current step.

        Args:
            workflow_id (str): ID of the workflow to execute.

        Returns:
            bool: True if execution successful, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                raise_alert(
                    "error",
                    f"Workflow Not Found: {workflow_id}",
                    "Cannot execute non-existent workflow",
                )
                return False

            workflow = self.workflows[workflow_id]
            if workflow["state"]["status"] not in ["created", "running", "paused"]:
                logger.error(
                    f"Workflow {workflow_id} is not in executable state: {workflow['state']['status']}"
                )
                raise_alert(
                    "error",
                    f"Invalid Workflow State: {workflow_id}",
                    f"Workflow is in {workflow['state']['status']} state",
                )
                return False

            workflow["state"]["status"] = "running"
            workflow["state"]["last_updated"] = datetime.now().isoformat()
            self.current_workflow_id = workflow_id
            logger.info(f"Executing workflow {workflow_id}")

            # Execute each step until completion or error
            while workflow["state"]["status"] == "running":
                current_step = workflow["state"]["current_step"]
                if not current_step:
                    workflow["state"]["status"] = "completed"
                    break

                success = self.execute_step(workflow_id, current_step)
                if not success:
                    workflow["state"]["status"] = "failed"
                    workflow["state"]["error"] = (
                        f"Failed to execute step {current_step}"
                    )
                    workflow["state"]["retry_count"] += 1
                    logger.error(
                        f"Workflow {workflow_id} failed at step {current_step}"
                    )
                    raise_alert(
                        "error",
                        f"Workflow Execution Failed: {workflow_id}",
                        f"Failed at step {current_step}",
                    )
                    break

                workflow["state"]["last_updated"] = datetime.now().isoformat()
                workflow["history"].append(
                    {
                        "step": current_step,
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                self._persist_workflow_state(workflow_id)

            logger.info(
                f"Workflow {workflow_id} execution completed with status: {workflow['state']['status']}"
            )
            self._persist_workflow_state(workflow_id)
            return workflow["state"]["status"] == "completed"
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {str(e)}")
            raise_alert("error", f"Workflow Execution Failed: {workflow_id}", str(e))
            if workflow_id in self.workflows:
                self.workflows[workflow_id]["state"]["status"] = "failed"
                self.workflows[workflow_id]["state"]["error"] = str(e)
                self._persist_workflow_state(workflow_id)
            return False

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """
        Get the current status and state of a workflow.

        Args:
            workflow_id (str): ID of the workflow to query.

        Returns:
            Optional[Dict]: Workflow state dictionary if found, None otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.warning(f"Workflow {workflow_id} not found")
                return None
            return self.workflows[workflow_id]["state"]
        except Exception as e:
            logger.error(f"Error getting status for workflow {workflow_id}: {str(e)}")
            return None

    def add_step(self, workflow_id: str, step_id: str, step_definition: Dict) -> bool:
        """
        Add a new step to an existing workflow definition.

        Args:
            workflow_id (str): ID of the workflow to modify.
            step_id (str): ID of the new step.
            step_definition (Dict): Definition of the new step.

        Returns:
            bool: True if step added successfully, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return False

            workflow = self.workflows[workflow_id]
            if "steps" not in workflow["definition"]:
                workflow["definition"]["steps"] = []

            # Check if step already exists
            if step_id in workflow["definition"]["steps"]:
                logger.warning(
                    f"Step {step_id} already exists in workflow {workflow_id}"
                )
                return False

            workflow["definition"]["steps"].append(step_id)
            # Assuming there's a dictionary of step definitions
            if "step_definitions" not in workflow["definition"]:
                workflow["definition"]["step_definitions"] = {}
            workflow["definition"]["step_definitions"][step_id] = step_definition

            logger.info(f"Added step {step_id} to workflow {workflow_id}")
            self._persist_workflow_state(workflow_id)
            return True
        except Exception as e:
            logger.error(f"Failed to add step to workflow {workflow_id}: {str(e)}")
            return False

    def remove_step(self, workflow_id: str, step_id: str) -> bool:
        """
        Remove a step from an existing workflow definition.

        Args:
            workflow_id (str): ID of the workflow to modify.
            step_id (str): ID of the step to remove.

        Returns:
            bool: True if step removed successfully, False otherwise.
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return False

            workflow = self.workflows[workflow_id]
            if (
                "steps" not in workflow["definition"]
                or step_id not in workflow["definition"]["steps"]
            ):
                logger.warning(f"Step {step_id} not found in workflow {workflow_id}")
                return False

            # Don't allow removal if it's the current step or initial step
            if (
                workflow["state"]["current_step"] == step_id
                or workflow["definition"].get("initial_step") == step_id
            ):
                logger.error(
                    f"Cannot remove active or initial step {step_id} from workflow {workflow_id}"
                )
                return False

            workflow["definition"]["steps"].remove(step_id)
            if (
                "step_definitions" in workflow["definition"]
                and step_id in workflow["definition"]["step_definitions"]
            ):
                del workflow["definition"]["step_definitions"][step_id]

            logger.info(f"Removed step {step_id} from workflow {workflow_id}")
            self._persist_workflow_state(workflow_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove step from workflow {workflow_id}: {str(e)}")
            return False

    def list_workflows(self) -> list:
        """
        List all available workflows with their current status.

        Returns:
            list: List of dictionaries with workflow ID and state.
        """
        try:
            return [{"id": wid, **w["state"]} for wid, w in self.workflows.items()]
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return []
