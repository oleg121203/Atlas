"""Ethical Guidelines for Atlas AI

This module defines the ethical principles and guidelines that govern the behavior
of AI agents within the Atlas application. These guidelines ensure responsible AI
decision-making and user trust.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EthicalPrinciple(Enum):
    """Enum defining core ethical principles for AI behavior."""

    TRANSPARENCY = "Transparency"
    ACCOUNTABILITY = "Accountability"
    FAIRNESS = "Fairness"
    PRIVACY = "Privacy"
    BENEFICENCE = "Beneficence"


class EthicalGuidelines:
    """Class encapsulating ethical guidelines and evaluation methods for AI actions."""

    def __init__(self):
        self.principles: Dict[EthicalPrinciple, str] = {
            EthicalPrinciple.TRANSPARENCY: "AI must clearly explain its decisions and actions to users.",
            EthicalPrinciple.ACCOUNTABILITY: "AI must be accountable for its actions and decisions.",
            EthicalPrinciple.FAIRNESS: "AI must avoid bias and ensure fair treatment of all users.",
            EthicalPrinciple.PRIVACY: "AI must protect user data and respect privacy.",
            EthicalPrinciple.BENEFICENCE: "AI must aim to benefit users and avoid harm.",
        }
        self.consent_records: Dict[str, Dict[str, bool]] = {}
        self.ethical_reviews: List[Dict] = []  # Store ethical evaluations for review
        logger.info("Ethical Guidelines initialized")

    def evaluate_action(
        self, action: str, context: Dict
    ) -> Dict[EthicalPrinciple, float]:
        """Evaluate a proposed action against all ethical principles.

        Args:
            action: Description of the proposed action.
            context: Contextual information about the action and user.

        Returns:
            Dictionary mapping each ethical principle to a compliance score (0.0 to 1.0).
        """
        scores = {}
        for principle in EthicalPrinciple:
            score = self._evaluate_principle(action, context, principle)
            scores[principle] = score
            logger.debug(f"Score for {principle}: {score}")
        return scores

    def _evaluate_principle(
        self, action: str, context: Dict, principle: EthicalPrinciple
    ) -> float:
        """Evaluate an action against a specific ethical principle.

        Args:
            action: Description of the proposed action.
            context: Contextual information about the action and user.
            principle: The ethical principle to evaluate against.

        Returns:
            Compliance score between 0.0 (non-compliant) and 1.0 (fully compliant).
        """
        logger.debug(f"Evaluating {principle} for action: {action}")

        if principle == EthicalPrinciple.TRANSPARENCY:
            return 1.0 if "explanation" in context and context["explanation"] else 0.5
        elif principle == EthicalPrinciple.ACCOUNTABILITY:
            return 1.0 if "audit_log" in context and context["audit_log"] else 0.7
        elif principle == EthicalPrinciple.FAIRNESS:
            return 1.0 if "bias_check" in context and context["bias_check"] else 0.6
        elif principle == EthicalPrinciple.PRIVACY:
            return (
                1.0
                if "data_protection" in context and context["data_protection"]
                else 0.4
            )
        elif principle == EthicalPrinciple.BENEFICENCE:
            return 1.0 if "user_benefit" in context and context["user_benefit"] else 0.5

        return 0.8  # Default score for unhandled principles

    def get_principle_description(self, principle: EthicalPrinciple) -> str:
        """Get the description of an ethical principle.

        Args:
            principle: The ethical principle to describe.

        Returns:
            Description of the principle.
        """
        return self.principles.get(principle, "Unknown principle")

    def check_consent(self, user_id: str, action_type: str) -> bool:
        """Check if user has consented to a specific type of action.

        Args:
            user_id: Identifier for the user.
            action_type: Type of action requiring consent.

        Returns:
            Boolean indicating if consent is granted.
        """
        logger.info(f"Checking consent for user {user_id} and action {action_type}")
        if (
            user_id in self.consent_records
            and action_type in self.consent_records[user_id]
        ):
            return self.consent_records[user_id][action_type]
        return False  # Default to no consent if not explicitly granted

    def update_consent(self, user_id: str, action_type: str, consent: bool) -> None:
        """Update consent status for a user and action type.

        Args:
            user_id: Identifier for the user.
            action_type: Type of action requiring consent.
            consent: Boolean indicating if consent is granted.
        """
        logger.info(
            f"Updating consent for user {user_id} and action {action_type} to {consent}"
        )
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        self.consent_records[user_id][action_type] = consent

    def get_minimum_compliance_score(self) -> float:
        """Get the minimum compliance score required for an action to be considered ethical.

        Returns:
            Minimum compliance score (0.0 to 1.0).
        """
        return 0.75  # Actions must meet at least 75% compliance across principles

    def is_action_ethical(
        self, action: str, context: Dict
    ) -> tuple[bool, Dict[EthicalPrinciple, float], str]:
        """Determine if an action meets ethical guidelines.

        Args:
            action: Description of the proposed action.
            context: Contextual information about the action and user.

        Returns:
            Tuple of (is_ethical: bool, scores: Dict[EthicalPrinciple, float], explanation: str).
        """
        scores = self.evaluate_action(action, context)
        min_score = self.get_minimum_compliance_score()
        total_score = sum(scores.values()) / len(scores)
        is_ethical = total_score >= min_score

        explanation = f"Action: {action}\nEthical Evaluation:\n"
        for principle, score in scores.items():
            explanation += f"- {principle.value}: {score:.2f} ({self.get_principle_description(principle)})\n"
        explanation += (
            f"Total Score: {total_score:.2f} (Minimum Required: {min_score:.2f})\n"
        )
        explanation += "Result: " + ("Ethical" if is_ethical else "Not Ethical")

        # Log the evaluation for review
        self.log_ethical_review(action, context, scores, is_ethical, explanation)

        logger.info(
            f"Ethical evaluation for {action}: {total_score:.2f}, Ethical: {is_ethical}"
        )
        return is_ethical, scores, explanation

    def log_ethical_review(
        self,
        action: str,
        context: Dict,
        scores: Dict[EthicalPrinciple, float],
        is_ethical: bool,
        explanation: str,
    ) -> None:
        """Log an ethical evaluation for future review.

        Args:
            action: Description of the proposed action.
            context: Contextual information about the action.
            scores: Dictionary mapping each ethical principle to a compliance score.
            is_ethical: Boolean indicating if the action is considered ethical.
            explanation: Detailed explanation of the ethical evaluation.
        """
        review_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "context": context,
            "scores": {k.value: v for k, v in scores.items()},
            "is_ethical": is_ethical,
            "explanation": explanation,
        }
        self.ethical_reviews.append(review_entry)
        logger.debug(f"Logged ethical review for action: {action}")

    def get_ethical_reviews(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Retrieve logged ethical reviews within a specified date range.

        Args:
            start_date: Optional start date for filtering reviews.
            end_date: Optional end date for filtering reviews.

        Returns:
            List of ethical review entries.
        """
        if start_date is None and end_date is None:
            return self.ethical_reviews

        filtered_reviews = []
        for review in self.ethical_reviews:
            review_time = datetime.fromisoformat(review["timestamp"])
            if start_date and review_time < start_date:
                continue
            if end_date and review_time > end_date:
                continue
            filtered_reviews.append(review)
        return filtered_reviews
