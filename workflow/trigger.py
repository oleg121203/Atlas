"""
Workflow Trigger System

This module provides functionality for defining and managing triggers
that initiate workflows based on time, events, or conditions.
"""

import logging
import time
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
import sched
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Trigger:
    """Base class for workflow triggers."""
    def __init__(self, trigger_id: str, callback: Callable[[], None]):
        """Initialize a trigger with a unique ID and callback function.

        Args:
            trigger_id (str): Unique identifier for the trigger.
            callback (Callable[[], None]): Function to call when the trigger is activated.
        """
        self.trigger_id = trigger_id
        self.callback = callback
        self.active = False

    def validate(self) -> bool:
        """Validate the trigger configuration.

        Returns:
            bool: True if the trigger is valid, False otherwise.
        """
        raise NotImplementedError("Trigger must implement validate method.")

    def start(self) -> None:
        """Start monitoring for the trigger condition."""
        raise NotImplementedError("Trigger must implement start method.")

    def stop(self) -> None:
        """Stop monitoring for the trigger condition."""
        raise NotImplementedError("Trigger must implement stop method.")

class TimeBasedTrigger(Trigger):
    """Trigger workflows based on a specific time or interval."""
    def __init__(self, trigger_id: str, callback: Callable[[], None], trigger_time: datetime, interval: Optional[timedelta] = None):
        """Initialize a time-based trigger.

        Args:
            trigger_id (str): Unique identifier for the trigger.
            callback (Callable[[], None]): Function to call when the trigger is activated.
            trigger_time (datetime): The specific time to trigger the workflow.
            interval (Optional[timedelta]): If provided, repeat the trigger at this interval.
        """
        super().__init__(trigger_id, callback)
        self.trigger_time = trigger_time
        self.interval = interval
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.event = None
        self.thread = None

    def validate(self) -> bool:
        """Validate the time-based trigger configuration.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        if self.trigger_time < datetime.now():
            if not self.interval:
                logger.error(f"Trigger {self.trigger_id} has a past trigger time without an interval.")
                return False
        if self.interval and self.interval.total_seconds() <= 0:
            logger.error(f"Trigger {self.trigger_id} has a non-positive interval.")
            return False
        return True

    def start(self) -> None:
        """Start the time-based trigger."""
        if not self.validate():
            raise ValueError(f"Invalid configuration for trigger {self.trigger_id}")
        
        self.active = True
        delay = (self.trigger_time - datetime.now()).total_seconds()
        if delay < 0:
            if self.interval:
                delay = self.interval.total_seconds()
            else:
                logger.warning(f"Trigger {self.trigger_id} time is in the past and no interval set. Trigger will not activate.")
                return

        self.event = self.scheduler.enter(delay, 1, self._activate)
        self.thread = threading.Thread(target=self.scheduler.run)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Started time-based trigger {self.trigger_id} for {self.trigger_time}")

    def _activate(self) -> None:
        """Activate the trigger and schedule the next occurrence if interval is set."""
        if self.active:
            logger.info(f"Trigger {self.trigger_id} activated at {datetime.now()}")
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error executing callback for trigger {self.trigger_id}: {e}")

            if self.interval and self.active:
                self.trigger_time += self.interval
                delay = self.interval.total_seconds()
                self.event = self.scheduler.enter(delay, 1, self._activate)
                logger.info(f"Scheduled next activation for trigger {self.trigger_id} at {self.trigger_time}")

    def stop(self) -> None:
        """Stop the time-based trigger."""
        self.active = False
        if self.event:
            try:
                self.scheduler.cancel(self.event)
            except ValueError:
                pass  # Event might have already been executed
        logger.info(f"Stopped time-based trigger {self.trigger_id}")

class EventBasedTrigger(Trigger):
    """Trigger workflows based on specific events."""
    def __init__(self, trigger_id: str, callback: Callable[[], None], event_type: str, condition: Optional[Callable[[Any], bool]] = None):
        """Initialize an event-based trigger.

        Args:
            trigger_id (str): Unique identifier for the trigger.
            callback (Callable[[], None]): Function to call when the trigger is activated.
            event_type (str): Type of event to listen for.
            condition (Optional[Callable[[Any], bool]]): Optional condition to check on the event data.
        """
        super().__init__(trigger_id, callback)
        self.event_type = event_type
        self.condition = condition or (lambda x: True)
        self.listeners = []

    def validate(self) -> bool:
        """Validate the event-based trigger configuration.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        if not self.event_type:
            logger.error(f"Trigger {self.trigger_id} has no event type specified.")
            return False
        return True

    def start(self) -> None:
        """Start listening for the specified event."""
        if not self.validate():
            raise ValueError(f"Invalid configuration for trigger {self.trigger_id}")
        
        self.active = True
        # Placeholder for event listener registration
        # In a real implementation, this would register with an event system
        logger.info(f"Started event-based trigger {self.trigger_id} for event type {self.event_type}")

    def stop(self) -> None:
        """Stop listening for the specified event."""
        self.active = False
        # Placeholder for event listener unregistration
        logger.info(f"Stopped event-based trigger {self.trigger_id} for event type {self.event_type}")

    def on_event(self, event_data: Any) -> None:
        """Handle incoming events and trigger callback if conditions are met.

        Args:
            event_data (Any): Data associated with the event.
        """
        if self.active and self.condition(event_data):
            logger.info(f"Event trigger {self.trigger_id} activated by event {self.event_type}")
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error executing callback for trigger {self.trigger_id}: {e}")

class ConditionBasedTrigger(Trigger):
    """Trigger workflows based on a condition being met."""
    def __init__(self, trigger_id: str, callback: Callable[[], None], condition: Callable[[], bool], check_interval: float = 60.0):
        """Initialize a condition-based trigger.

        Args:
            trigger_id (str): Unique identifier for the trigger.
            callback (Callable[[], None]): Function to call when the trigger is activated.
            condition (Callable[[], bool]): Condition function to evaluate.
            check_interval (float): Interval in seconds to check the condition.
        """
        super().__init__(trigger_id, callback)
        self.condition = condition
        self.check_interval = check_interval
        self.thread = None

    def validate(self) -> bool:
        """Validate the condition-based trigger configuration.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        if self.check_interval <= 0:
            logger.error(f"Trigger {self.trigger_id} has a non-positive check interval.")
            return False
        return True

    def start(self) -> None:
        """Start checking the condition at the specified interval."""
        if not self.validate():
            raise ValueError(f"Invalid configuration for trigger {self.trigger_id}")
        
        self.active = True
        self.thread = threading.Thread(target=self._check_condition_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Started condition-based trigger {self.trigger_id} with check interval {self.check_interval} seconds")

    def _check_condition_loop(self) -> None:
        """Continuously check the condition until stopped."""
        while self.active:
            try:
                if self.condition():
                    logger.info(f"Condition trigger {self.trigger_id} activated")
                    self.callback()
                    # Optionally stop after first activation, could be configurable
                    self.stop()
                    break
            except Exception as e:
                logger.error(f"Error checking condition for trigger {self.trigger_id}: {e}")
            time.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop checking the condition."""
        self.active = False
        logger.info(f"Stopped condition-based trigger {self.trigger_id}")

class TriggerManager:
    """Manages multiple triggers for workflows."""
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}

    def add_trigger(self, trigger: Trigger) -> None:
        """Add a trigger to manage.

        Args:
            trigger (Trigger): The trigger to add.
        """
        self.triggers[trigger.trigger_id] = trigger
        logger.info(f"Added trigger {trigger.trigger_id} to manager")

    def remove_trigger(self, trigger_id: str) -> None:
        """Remove a trigger from management.

        Args:
            trigger_id (str): The ID of the trigger to remove.
        """
        if trigger_id in self.triggers:
            self.triggers[trigger_id].stop()
            del self.triggers[trigger_id]
            logger.info(f"Removed trigger {trigger_id} from manager")

    def start_all(self) -> None:
        """Start all managed triggers."""
        for trigger in self.triggers.values():
            try:
                trigger.start()
            except Exception as e:
                logger.error(f"Failed to start trigger {trigger.trigger_id}: {e}")

    def stop_all(self) -> None:
        """Stop all managed triggers."""
        for trigger in self.triggers.values():
            try:
                trigger.stop()
            except Exception as e:
                logger.error(f"Failed to stop trigger {trigger.trigger_id}: {e}")

    def simulate_event(self, event_type: str, event_data: Any) -> None:
        """Simulate an event for testing event-based triggers.

        Args:
            event_type (str): Type of event to simulate.
            event_data (Any): Data associated with the event.
        """
        for trigger in self.triggers.values():
            if isinstance(trigger, EventBasedTrigger) and trigger.event_type == event_type:
                trigger.on_event(event_data)
                logger.info(f"Simulated event {event_type} for trigger {trigger.trigger_id}")
