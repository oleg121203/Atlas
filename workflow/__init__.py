"""
Workflow Module for Atlas

This package contains the workflow execution engine, trigger system components, analytics components, integration components,
security components, and related components for automating processes within the Atlas application.
"""

from .analytics import WorkflowAnalytics
from .engine import WorkflowEngine
from .error_handling import (
    ActionExecutionError,
    AlwaysContinue,
    ErrorHandler,
    RetryAction,
    StatePersistenceError,
    StopOnCritical,
    WorkflowError,
)
from .execution import AdvancedWorkflowEngine
from .integration import IntegrationAdapter, RESTApiAdapter, WorkflowIntegrator
from .security import AccessControl, AuditLogger, EncryptionManager, WorkflowSecurity
from .trigger import (
    ConditionBasedTrigger,
    EventBasedTrigger,
    TimeBasedTrigger,
    Trigger,
    TriggerManager,
)

__all__ = [
    "WorkflowEngine",
    "AdvancedWorkflowEngine",
    "ErrorHandler",
    "AlwaysContinue",
    "StopOnCritical",
    "RetryAction",
    "WorkflowError",
    "ActionExecutionError",
    "StatePersistenceError",
    "Trigger",
    "TimeBasedTrigger",
    "EventBasedTrigger",
    "ConditionBasedTrigger",
    "TriggerManager",
    "WorkflowAnalytics",
    "IntegrationAdapter",
    "RESTApiAdapter",
    "WorkflowIntegrator",
    "AccessControl",
    "EncryptionManager",
    "AuditLogger",
    "WorkflowSecurity",
]
