"""
Workflow Error Handling Module

This module provides error handling strategies for workflow execution,
including continuation strategies and rollback mechanisms.
"""

import logging
from typing import Callable, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    """Base exception class for workflow-related errors."""

    def __init__(self, message: str, action: str = "", workflow_id: str = ""):
        self.action = action
        self.workflow_id = workflow_id
        super().__init__(message)


class ActionExecutionError(WorkflowError):
    """Raised when an action fails during workflow execution."""

    pass


class StatePersistenceError(WorkflowError):
    """Raised when there's an error in saving or recovering workflow state."""

    pass


class ContinuationStrategy:
    """Base class for continuation strategies after an error occurs."""

    def should_continue(self, error: WorkflowError) -> bool:
        """Determine if workflow execution should continue after an error.

        Args:
            error (WorkflowError): The error that occurred during execution.

        Returns:
            bool: True if execution should continue, False otherwise.
        """
        raise NotImplementedError(
            "Continuation strategy must implement should_continue method."
        )


class AlwaysContinue(ContinuationStrategy):
    """Always continue workflow execution regardless of the error."""

    def should_continue(self, error: WorkflowError) -> bool:
        logger.warning(
            f"Continuing workflow {error.workflow_id} despite error in action {error.action}: {str(error)}"
        )
        return True


class StopOnCritical(ContinuationStrategy):
    """Stop workflow execution only on critical errors."""

    def should_continue(self, error: WorkflowError) -> bool:
        if isinstance(error, ActionExecutionError):
            logger.warning(
                f"Continuing workflow {error.workflow_id} after non-critical error in action {error.action}: {str(error)}"
            )
            return True
        logger.error(
            f"Stopping workflow {error.workflow_id} due to critical error: {str(error)}"
        )
        return False


class RetryAction(ContinuationStrategy):
    """Retry the action a specified number of times before giving up."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.attempts: Dict[str, int] = {}

    def should_continue(self, error: WorkflowError) -> bool:
        action_key = f"{error.workflow_id}:{error.action}"
        self.attempts[action_key] = self.attempts.get(action_key, 0) + 1

        if self.attempts[action_key] <= self.max_retries:
            logger.info(
                f"Retrying action {error.action} in workflow {error.workflow_id}, attempt {self.attempts[action_key]} of {self.max_retries}"
            )
            return True
        else:
            logger.error(
                f"Failed action {error.action} in workflow {error.workflow_id} after {self.max_retries} retries: {str(error)}"
            )
            self.attempts[action_key] = 0  # Reset for future attempts
            return False


class ErrorHandler:
    """Handles errors during workflow execution with configurable strategies."""

    def __init__(self, strategy: ContinuationStrategy = None):
        self.strategy = strategy if strategy is not None else DEFAULT_STRATEGY

    def set_strategy(self, strategy: ContinuationStrategy) -> None:
        """Set the continuation strategy for error handling.

        Args:
            strategy (ContinuationStrategy): The strategy to use for error continuation.
        """
        self.strategy = strategy
        logger.info(f"Set error handling strategy to {strategy.__class__.__name__}")

    def handle_error(
        self, error: WorkflowError, rollback_action: Optional[Callable[[], None]] = None
    ) -> bool:
        """Handle an error that occurred during workflow execution.

        Args:
            error (WorkflowError): The error that occurred.
            rollback_action (Optional[Callable[[], None]]): Action to perform for rollback if continuation is not possible.

        Returns:
            bool: True if execution should continue, False if it should stop.
        """
        logger.error(
            f"Error occurred in workflow {error.workflow_id}, action {error.action}: {str(error)}"
        )

        if self.strategy.should_continue(error):
            return True
        else:
            if rollback_action:
                try:
                    rollback_action()
                    logger.info(
                        f"Rollback successful for workflow {error.workflow_id}, action {error.action}"
                    )
                except Exception as e:
                    logger.error(
                        f"Rollback failed for workflow {error.workflow_id}, action {error.action}: {e}"
                    )
            return False


# Default continuation strategy
DEFAULT_STRATEGY = StopOnCritical()
