"""
Decision Engine for Atlas

This module implements the DecisionEngine class, which is responsible for making decisions based on context,
goals, and available actions. It integrates with the ContextEngine to ensure decisions are context-aware.
"""
import logging
from typing import Any, Callable, Dict, List

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
            self.context_engine.register_listener("decision_engine", self.on_context_update)
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

    def register_strategy(self, strategy_name: str, strategy_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Register a new decision-making strategy.
        Args:
            strategy_name: The name of the strategy.
            strategy_func: The function implementing the decision strategy.
        """
        self.decision_strategies[strategy_name] = strategy_func
        logger.info(f"Registered decision strategy: {strategy_name}")

    def make_decision(self, goal: str, strategy_name: str = "default") -> Dict[str, Any]:
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
        decision['goal'] = goal
        decision['strategy_used'] = strategy_name
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
            "factors_considered": list(self.decision_factors.keys())
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
