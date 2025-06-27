"""
Advanced Workflow Execution Module

This module extends the WorkflowEngine to support advanced features like
parallel execution, conditional branching, and workflow templates.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from workflow.engine import WorkflowEngine
from workflow.error_handling import ActionExecutionError, ErrorHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedWorkflowEngine(WorkflowEngine):
    """Extends WorkflowEngine to support advanced execution features."""

    def __init__(self, db_path: str = "workflow_state.db", max_workers: int = 4):
        """Initialize the Advanced Workflow Engine.

        Args:
            db_path (str): Path to the SQLite database for storing workflow state.
            max_workers (int): Maximum number of parallel workers for action execution.
        """
        super().__init__(db_path)
        self.max_workers = max_workers
        self.error_handler = ErrorHandler()
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.versions: Dict[str, int] = {}

    def execute_parallel(self, actions: List[Callable[[], Any]]) -> List[Any]:
        """Execute multiple actions in parallel.

        Args:
            actions (List[Callable[[], Any]]): List of actions to execute in parallel.

        Returns:
            List[Any]: Results of the executed actions.

        Raises:
            WorkflowError: If any action fails and the error handler decides to stop execution.
        """
        if not self.current_workflow_id:
            raise ValueError("No active workflow. Call start_workflow() first.")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_action = {
                executor.submit(action): i for i, action in enumerate(actions)
            }
            for future in as_completed(future_to_action):
                action_index = future_to_action[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(
                        f"Parallel action {action_index} completed in workflow {self.current_workflow_id}"
                    )
                except Exception as e:
                    error = ActionExecutionError(
                        f"Parallel action {action_index} failed: {str(e)}",
                        action=f"parallel_action_{action_index}",
                        workflow_id=self.current_workflow_id,
                    )
                    if not self.error_handler.handle_error(error, self.conn.rollback):
                        logger.error(
                            f"Stopping workflow {self.current_workflow_id} due to parallel action failure"
                        )
                        raise
                    results.append(None)  # Append None for failed action
                    logger.warning(
                        f"Continuing workflow {self.current_workflow_id} despite parallel action failure"
                    )

        return results

    def execute_conditional(
        self,
        condition: Callable[[], bool],
        true_action: Callable[[], Any],
        false_action: Optional[Callable[[], Any]] = None,
    ) -> Any:
        """Execute actions based on a condition.

        Args:
            condition (Callable[[], bool]): Condition to evaluate.
            true_action (Callable[[], Any]): Action to execute if condition is True.
            false_action (Optional[Callable[[], Any]]): Action to execute if condition is False.

        Returns:
            Any: Result of the executed action.

        Raises:
            WorkflowError: If the action fails and the error handler decides to stop execution.
        """
        if not self.current_workflow_id:
            raise ValueError("No active workflow. Call start_workflow() first.")

        try:
            if condition():
                logger.info(
                    f"Condition true in workflow {self.current_workflow_id}, executing true action"
                )
                return self.execute_action(true_action)
            else:
                logger.info(f"Condition false in workflow {self.current_workflow_id}")
                if false_action:
                    return self.execute_action(false_action)
                return None
        except Exception as e:
            error = ActionExecutionError(
                f"Conditional execution failed: {str(e)}",
                action="conditional_action",
                workflow_id=self.current_workflow_id,
            )
            if not self.error_handler.handle_error(error, self.conn.rollback):
                logger.error(
                    f"Stopping workflow {self.current_workflow_id} due to conditional action failure"
                )
                raise
            logger.warning(
                f"Continuing workflow {self.current_workflow_id} despite conditional action failure"
            )
            return None

    def register_template(
        self, template_id: str, workflow_template: Dict[str, Any], version: int = 1
    ) -> None:
        """Register a workflow template for reuse.

        Args:
            template_id (str): Unique identifier for the template.
            workflow_template (Dict[str, Any]): Template definition including actions and triggers.
            version (int): Version number of the template.
        """
        self.templates[template_id] = workflow_template
        self.versions[template_id] = version
        logger.info(f"Registered workflow template {template_id} version {version}")

    def execute_from_template(
        self, template_id: str, parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute a workflow from a registered template with given parameters.

        Args:
            template_id (str): ID of the template to execute.
            parameters (Optional[Dict[str, Any]]): Parameters to substitute into the template.

        Raises:
            ValueError: If the template ID is not found.
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        workflow_def = self.templates[template_id]
        if parameters:
            # Substitute parameters into the workflow definition (simple placeholder replacement)
            workflow_def = self._apply_parameters(workflow_def, parameters)

        workflow_id = f"{template_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        initial_state = workflow_def.get("initial_state", {})
        self.start_workflow(workflow_id, initial_state)

        actions = workflow_def.get("actions", [])
        for action_def in actions:
            action_type = action_def.get("type", "simple")
            try:
                if action_type == "parallel":
                    action_funcs = [
                        self._create_action_func(a)
                        for a in action_def.get("actions", [])
                    ]
                    self.execute_parallel(action_funcs)
                elif action_type == "conditional":
                    condition_func = self._create_condition_func(
                        action_def.get("condition")
                    )
                    true_action_func = self._create_action_func(
                        action_def.get("true_action")
                    )
                    false_action_func = (
                        self._create_action_func(action_def.get("false_action"))
                        if "false_action" in action_def
                        else None
                    )
                    self.execute_conditional(
                        condition_func, true_action_func, false_action_func
                    )
                else:
                    action_func = self._create_action_func(action_def)
                    self.execute_action(action_func)
            except Exception as e:
                error = ActionExecutionError(
                    f"Template action failed: {str(e)}",
                    action=f"template_{template_id}_{action_type}",
                    workflow_id=workflow_id,
                )
                if not self.error_handler.handle_error(error, self.conn.rollback):
                    logger.error(
                        f"Stopping workflow {workflow_id} due to template action failure"
                    )
                    raise
                logger.warning(
                    f"Continuing workflow {workflow_id} despite template action failure"
                )

        self.complete_workflow()
        logger.info(f"Completed workflow {workflow_id} from template {template_id}")

    def migrate_workflow(
        self,
        template_id: str,
        old_version: int,
        new_version: int,
        migration_func: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Migrate a workflow template from an old version to a new version.

        Args:
            template_id (str): ID of the template to migrate.
            old_version (int): Current version of the template.
            new_version (int): Target version for migration.
            migration_func (Callable[[Dict[str, Any]], Dict[str, Any]]): Function to migrate the template.
        """
        if (
            template_id not in self.templates
            or self.versions.get(template_id, 0) != old_version
        ):
            raise ValueError(
                f"Cannot migrate template {template_id}: version mismatch or template not found"
            )

        self.templates[template_id] = migration_func(self.templates[template_id])
        self.versions[template_id] = new_version
        logger.info(
            f"Migrated template {template_id} from version {old_version} to {new_version}"
        )

    def _apply_parameters(
        self, workflow_def: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply parameters to a workflow definition (placeholder for real implementation).

        Args:
            workflow_def (Dict[str, Any]): Workflow definition.
            parameters (Dict[str, Any]): Parameters to apply.

        Returns:
            Dict[str, Any]: Workflow definition with parameters applied.
        """
        # This is a placeholder. A real implementation would substitute parameters
        # into placeholders within the workflow definition.
        return workflow_def

    def _create_action_func(self, action_def: Dict[str, Any]) -> Callable[[], Any]:
        """Create a callable action function from a definition (placeholder).

        Args:
            action_def (Dict[str, Any]): Definition of the action.

        Returns:
            Callable[[], Any]: Action function to execute.
        """

        # Placeholder for creating a real action function from a definition
        def dummy_action():
            logger.info(f"Executing action from definition: {action_def}")
            return True

        return dummy_action

    def _create_condition_func(
        self, condition_def: Dict[str, Any]
    ) -> Callable[[], bool]:
        """Create a callable condition function from a definition (placeholder).

        Args:
            condition_def (Dict[str, Any]): Definition of the condition.

        Returns:
            Callable[[], bool]: Condition function to evaluate.
        """

        # Placeholder for creating a real condition function from a definition
        def dummy_condition():
            logger.info(f"Evaluating condition from definition: {condition_def}")
            return True

        return dummy_condition

    def set_error_strategy(self, strategy: str) -> None:
        """Set the error handling strategy for the workflow engine.

        Args:
            strategy (str): Name of the strategy to use ("always_continue", "stop_on_critical", "retry").
        """
        from workflow.error_handling import AlwaysContinue, RetryAction, StopOnCritical

        if strategy == "always_continue":
            self.error_handler.set_strategy(AlwaysContinue())
        elif strategy == "stop_on_critical":
            self.error_handler.set_strategy(StopOnCritical())
        elif strategy == "retry":
            self.error_handler.set_strategy(RetryAction(max_retries=3))
        else:
            raise ValueError(f"Unknown error handling strategy: {strategy}")
        logger.info(f"Set error handling strategy to {strategy} for workflow engine")
