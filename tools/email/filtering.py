"""Email Filtering Module

This module provides functionality for filtering emails based on rules and criteria.
"""

import logging
from typing import Dict

# Setup logging
logger = logging.getLogger(__name__)


class EmailFilter:
    """Class for filtering emails based on predefined rules and criteria."""

    def __init__(self):
        """Initialize the EmailFilter with empty rules."""
        self.rules = {}
        logger.info("EmailFilter initialized")

    def add_rule(self, rule_name: str, condition: callable, action: callable):
        """
        Add a filtering rule for emails.

        Args:
            rule_name (str): Name of the rule.
            condition (callable): Function that returns True if the rule applies to an email.
            action (callable): Function to execute when the rule applies.
        """
        self.rules[rule_name] = {"condition": condition, "action": action}
        logger.info(f"Added rule: {rule_name}")

    def apply_filters(self, email: Dict[str, any]):
        """
        Apply all filters to an email and execute actions if conditions are met.

        Args:
            email (Dict[str, any]): Email data to filter.

        Returns:
            bool: True if email passes all filters, False if it is filtered out.
        """
        for rule_name, rule in self.rules.items():
            if rule["condition"](email):
                logger.info(f"Rule {rule_name} applied to email")
                rule["action"](email)
                return False  # Email is filtered out
            else:
                logger.debug(f"Rule {rule_name} condition not met for email")
        return True  # Email passes all filters

    def remove_rule(self, rule_name: str):
        """
        Remove a filtering rule.

        Args:
            rule_name (str): Name of the rule to remove.
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"Removed rule: {rule_name}")
        else:
            logger.warning(f"Rule {rule_name} not found")
