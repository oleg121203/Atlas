"""
Unit Tests for Workflow Trigger System

This module tests the functionality of the trigger system for workflows,
including time-based, event-based, and condition-based triggers.
"""

import time
import unittest
from datetime import datetime, timedelta

from workflow.trigger import (
    ConditionBasedTrigger,
    EventBasedTrigger,
    TimeBasedTrigger,
    TriggerManager,
)


class TestWorkflowTriggers(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.callback_executed = False
        self.callback = self._set_callback_flag

    def _set_callback_flag(self):
        """Set a flag when the callback is executed."""
        self.callback_executed = True

    def test_time_based_trigger_single_execution(self):
        """Test a time-based trigger that executes once."""
        trigger_time = datetime.now() + timedelta(seconds=2)
        trigger = TimeBasedTrigger("time_trigger_1", self.callback, trigger_time)
        trigger.start()
        time.sleep(3)  # Wait for trigger to execute
        self.assertTrue(self.callback_executed)
        trigger.stop()

    def test_time_based_trigger_with_interval(self):
        """Test a time-based trigger that repeats at an interval."""
        trigger_time = datetime.now() + timedelta(seconds=2)
        interval = timedelta(seconds=2)
        trigger = TimeBasedTrigger(
            "time_trigger_2", self.callback, trigger_time, interval
        )
        trigger.start()
        time.sleep(5)  # Wait for at least two executions
        self.assertTrue(self.callback_executed)
        trigger.stop()

    def test_event_based_trigger(self):
        """Test an event-based trigger."""

        def condition(x):
            return x == "test_data"

        trigger = EventBasedTrigger(
            "event_trigger_1", self.callback, "test_event", condition
        )
        trigger.start()
        trigger.on_event("wrong_data")  # Should not trigger
        self.assertFalse(self.callback_executed)
        trigger.on_event("test_data")  # Should trigger
        self.assertTrue(self.callback_executed)
        trigger.stop()

    def test_condition_based_trigger(self):
        """Test a condition-based trigger."""
        condition_flag = False

        def condition():
            nonlocal condition_flag
            condition_flag = True
            return condition_flag

        trigger = ConditionBasedTrigger(
            "condition_trigger_1", self.callback, condition, check_interval=1.0
        )
        trigger.start()
        time.sleep(2)  # Wait for condition to be checked
        self.assertTrue(self.callback_executed)
        trigger.stop()

    def test_trigger_manager(self):
        """Test managing multiple triggers with TriggerManager."""
        manager = TriggerManager()
        trigger_time = datetime.now() + timedelta(seconds=2)
        time_trigger = TimeBasedTrigger("time_trigger_3", self.callback, trigger_time)
        event_trigger = EventBasedTrigger(
            "event_trigger_2", self.callback, "test_event_2"
        )

        manager.add_trigger(time_trigger)
        manager.add_trigger(event_trigger)
        manager.start_all()

        time.sleep(3)  # Wait for time-based trigger
        manager.simulate_event("test_event_2", None)  # Simulate event

        self.assertTrue(self.callback_executed)
        manager.stop_all()


if __name__ == "__main__":
    unittest.main()
