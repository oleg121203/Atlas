"""
Decision Engine for Atlas

This module implements the DecisionEngine class, which is responsible for making decisions based on context,
goals, and available actions. It integrates with the ContextEngine to ensure decisions are context-aware.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionEngine(QObject):
    """A class to manage decision-making processes based on context and goals."""

    decision_made = Signal(dict)
    decision_factors_updated = Signal(dict)

    def __init__(self, context_engine=None, parent=None):
        """Initialize the DecisionEngine with an optional ContextEngine.
        Args:
            context_engine: An optional ContextEngine instance to integrate with for context-aware decisions.
            parent: The parent QObject, if any.
        """
        super().__init__(parent)
        self.context_engine = context_engine
        self.decision_factors = {}
        self.decision_history = []
        self.decision_strategies = {}
        logger.info("DecisionEngine initialized")
        if self.context_engine:
            self._connect_to_context_engine()

    def _connect_to_context_engine(self):
        """Connect to the ContextEngine to receive context updates."""
        if self.context_engine:
            self.context_engine.register_listener(
                "decision_engine", self.on_context_update
            )
        logger.info("Connected to ContextEngine for context updates")

    def on_context_update(self, context_type: str, context_data: Dict[str, Any]):
        """Handle context updates from the ContextEngine.
        Args:
            context_type: The type of context updated.
            context_data: The updated context data.
        """
        logger.info(f"Received context update: {context_type}")
        self.update_decision_factors(context_type, context_data)

    def update_decision_factors(self, factor_type: str, factors: Dict[str, Any]):
        """Update decision factors based on new information.
        Args:
            factor_type: The type of factor being updated.
            factors: The new factors to consider in decision-making.
        """
        self.decision_factors[factor_type] = factors
        logger.info(f"Updated decision factors for {factor_type}")
        self.decision_factors_updated.emit(self.decision_factors)

    def register_strategy(
        self,
        strategy_name: str,
        strategy_func: Callable[[Dict[str, Any]], Dict[str, Any]],
    ):
        """Register a new decision-making strategy.
        Args:
            strategy_name: The name of the strategy.
            strategy_func: The function implementing the decision strategy.
        """
        self.decision_strategies[strategy_name] = strategy_func
        logger.info(f"Registered decision strategy: {strategy_name}")

    def make_decision(
        self, goal: str, strategy_name: str = "default"
    ) -> Dict[str, Any]:
        """Make a decision based on the current context and a specified goal.
        Args:
            goal: The goal to achieve with this decision.
            strategy_name: The name of the strategy to use for decision-making.
        Returns:
            A dictionary containing the decision details.
        """
        if strategy_name not in self.decision_strategies:
            logger.warning(f"Strategy {strategy_name} not found, using default logic")
            decision = self._default_decision_logic(goal)
        else:
            decision = self.decision_strategies[strategy_name](self.decision_factors)
        decision["goal"] = goal
        decision["strategy_used"] = strategy_name
        self.decision_history.append(decision)
        logger.info(f"Decision made for goal: {goal} using strategy: {strategy_name}")
        self.decision_made.emit(decision)
        return decision

    def _default_decision_logic(self, goal: str) -> Dict[str, Any]:
        """Default decision-making logic when no specific strategy is defined.
        Args:
            goal: The goal to achieve with this decision.
        Returns:
            A dictionary with the decision details.
        """
        # Simple decision logic based on available factors
        return {
            "decision": f"Action towards {goal}",
            "confidence": 0.5,
            "factors_considered": list(self.decision_factors.keys()),
        }

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Retrieve the history of decisions made.
        Returns:
            A list of dictionaries containing past decisions.
        """
        return self.decision_history

    def clear_decision_history(self):
        """Clear the history of decisions made."""
        self.decision_history = []
        logger.info("Decision history cleared")

    def decide_tool(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Select the most appropriate tool for a given task based on context and goals.

        Args:
            task: Dictionary containing task details like goal, context, etc.

        Returns:
            Dict containing selected tool details including:
            - tool_name: Name of the selected tool
            - tool_args: Arguments to pass to the tool
            - confidence: Confidence score for the selection
        """
        goal = task.get("goal", "")
        context = task.get("context", {})

        # Try primary strategy
        strategy_name = self._select_strategy_from_context(goal, context)
        logger.info(f"Selected strategy '{strategy_name}' based on context")

        decision = self._try_strategy(strategy_name, goal, context)
        if decision:
            return decision

        # Try fallback strategies
        for name in self.decision_strategies:
            if name != strategy_name:
                decision = self._try_strategy(
                    name, goal, context, min_suitability=0.3, is_fallback=True
                )
                if decision:
                    return decision

        # Use default selection as last resort
        decision = self._default_tool_selection(goal, context)
        if decision:
            logger.info(f"Using default tool selection: {decision['tool_name']}")
            return decision

        logger.error(f"No suitable tool found for goal: {goal}")
        return {}

    def _default_tool_selection(
        self, goal: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default logic for tool selection when no strategy matches.

        Args:
            goal: The goal to achieve
            context: Additional context for decision making

        Returns:
            Dict containing tool selection details
        """
        # Simple matching based on goal keywords
        # This should be enhanced with more sophisticated matching in production
        goal_lower = goal.lower()

        tool_matches = []

        # Add your default tool matching logic here
        # Example:
        if "analyze" in goal_lower or "evaluate" in goal_lower:
            tool_matches.append(("analysis_tool", 0.8))
        elif "search" in goal_lower or "find" in goal_lower:
            tool_matches.append(("search_tool", 0.7))
        # Add more default matches...

        # Return the highest confidence match or empty if none found
        if tool_matches:
            tool_matches.sort(key=lambda x: x[1], reverse=True)
            tool_name, confidence = tool_matches[0]
            return {
                "tool_name": tool_name,
                "tool_args": {"goal": goal, **context},
                "confidence": confidence,
            }

        return {}

    def _validate_tool_decision(self, decision: Dict[str, Any]) -> bool:
        """
        Validate that a tool decision is complete and coherent.

        Args:
            decision: Decision dictionary to validate

        Returns:
            True if decision is valid, False otherwise
        """
        required_fields = ["tool", "args"]
        has_required = all(field in decision for field in required_fields)

        if not has_required:
            return False

        # Additional validation can be added here
        return True

    def _default_tool_decision(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple fallback logic when all strategies fail.
        Maps task types to default tools.
        """
        task_type = task.get("type", "unknown")

        # Default mappings
        default_tools = {
            "file": "file_manager",
            "network": "network_client",
            "process": "process_manager",
            "ui": "ui_automation",
            "unknown": "general_purpose",
        }

        tool = default_tools.get(task_type, "general_purpose")

        decision = {
            "tool": tool,
            "args": {"task": task},
            "confidence": 0.5,
            "reasoning": f"Default selection based on task type: {task_type}",
        }

        # Record this as a decision in history
        self.decision_history.append(decision)
        self.decision_made.emit(decision)

        return decision

    def _select_strategy_from_context(self, goal: str, context: Dict[str, Any]) -> str:
        """Select the best decision strategy based on current context.

        Args:
            goal: The task goal
            context: Current context information

        Returns:
            Name of the most appropriate strategy
        """
        # Use context to select strategy
        user_state = context.get("user_context", {}).get("state", "normal")
        system_load = context.get("system_context", {}).get("load", "normal")
        task_priority = context.get("task_context", {}).get("priority", "normal")

        if user_state == "focused" and task_priority == "high":
            return "performance_optimized"
        elif system_load == "high":
            return "resource_efficient"
        elif user_state == "learning":
            return "educational"

        return "default"

    def _evaluate_tool_suitability(
        self, tool_name: str, goal: str, context: Dict[str, Any]
    ) -> float:
        """Evaluate how suitable a tool is for the current goal and context.

        Args:
            tool_name: Name of the tool to evaluate
            goal: The task goal
            context: Current context information

        Returns:
            Float between 0 and 1 indicating suitability
        """
        # Base score from tool metadata matching
        base_score = self._calculate_base_score(tool_name, goal)

        # Context modifiers
        system_resources = context.get("system_context", {}).get("resources", {})
        if system_resources.get("memory_pressure", False) and tool_name in [
            "heavy_analysis",
            "large_model",
        ]:
            base_score *= 0.5

        user_preferences = context.get("user_context", {}).get("preferences", {})
        if tool_name in user_preferences.get("preferred_tools", []):
            base_score *= 1.2

        # Normalize final score
        return min(1.0, max(0.0, base_score))

    def _calculate_base_score(self, tool_name: str, goal: str) -> float:
        """Calculate base suitability score from tool metadata and goal.

        Args:
            tool_name: Name of the tool
            goal: Task goal

        Returns:
            Base suitability score between 0 and 1
        """
        # This should be enhanced with proper NLP/ML matching in production
        goal_keywords = set(goal.lower().split())
        tool_keywords = set(tool_name.lower().split("_"))

        # Simple keyword matching for now
        matches = len(goal_keywords.intersection(tool_keywords))
        return min(1.0, matches / max(1, len(goal_keywords)))

    def _try_strategy(
        self,
        strategy_name: str,
        goal: str,
        context: Dict[str, Any],
        min_suitability: float = 0.5,
        is_fallback: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Try to get a tool decision using a specific strategy.

        Args:
            strategy_name: Name of the strategy to try
            goal: The task goal
            context: Current context
            min_suitability: Minimum suitability threshold
            is_fallback: Whether this is a fallback attempt

        Returns:
            Tool decision dict if successful, None otherwise
        """
        if strategy_name not in self.decision_strategies:
            return None

        try:
            strategy = self.decision_strategies[strategy_name]
            decision = strategy(
                {
                    "goal": goal,
                    "context": context,
                    "decision_factors": self.decision_factors,
                }
            )

            if not decision or "tool_name" not in decision:
                return None

            suitability = self._evaluate_tool_suitability(
                decision["tool_name"], goal, context
            )

            if suitability >= min_suitability:
                decision["confidence"] = suitability
                logger.info(
                    f"Selected {'fallback ' if is_fallback else ''}"
                    f"tool {decision['tool_name']} with "
                    f"confidence {suitability:.2f}"
                )
                return decision

        except Exception as e:
            logger.warning(
                f"{'Fallback' if is_fallback else 'Primary'} "
                f"strategy {strategy_name} failed: {str(e)}"
            )

        return None
