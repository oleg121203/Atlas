from logging import getLogger
from typing import Any, Callable, Dict, List, Optional

logger = getLogger(__name__)


class MetaAgent:
    """Manages multiple agents, their lifecycle, task delegation, and state persistence."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MetaAgent with configuration and empty agent registry."""
        self.config = config or {}
        self.state: Dict[str, Any] = {}
        self.agents: Dict[str, Any] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        logger.info("MetaAgent initialized with config: %s", self.config)

    def initialize(self) -> None:
        """Initialize the meta agent by loading agent configurations and states."""
        logger.info("Initializing MetaAgent")
        self.load_state()
        self.register_default_agents()
        for agent_id, agent in self.agents.items():
            try:
                agent_state = self.agent_states.get(agent_id, {})
                if hasattr(agent, "initialize"):
                    agent.initialize(state=agent_state)
                logger.info("Initialized agent: %s", agent_id)
            except Exception as e:
                logger.error("Failed to initialize agent %s: %s", agent_id, str(e))

    def register_agent(
        self, agent_id: str, agent: Any, initial_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new agent with an optional initial state."""
        self.agents[agent_id] = agent
        if initial_state is not None:
            self.agent_states[agent_id] = initial_state
        logger.info("Registered agent: %s", agent_id)

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent and save its final state."""
        if agent_id in self.agents:
            try:
                if hasattr(self.agents[agent_id], "shutdown"):
                    self.agents[agent_id].shutdown()
                self.save_agent_state(agent_id)
                del self.agents[agent_id]
                logger.info("Unregistered agent: %s", agent_id)
                return True
            except Exception as e:
                logger.error("Error unregistering agent %s: %s", agent_id, str(e))
                return False
        return False

    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data, delegate to appropriate agent, and return a response."""
        logger.debug("Processing input: %s", input_data)
        task_type = input_data.get("type", "unknown")

        # Find suitable agent for the task
        suitable_agent = self.select_agent_for_task(task_type)
        if suitable_agent is None:
            logger.error("No suitable agent found for task type: %s", task_type)
            return {
                "status": "error",
                "message": f"No agent available for task type: {task_type}",
            }

        try:
            agent_id, agent = suitable_agent
            response = (
                agent.process_input(input_data)
                if hasattr(agent, "process_input")
                else agent(input_data)
            )
            self.save_agent_state(agent_id)
            self.notify_event("task_completed", agent_id=agent_id, response=response)
            logger.debug("Task processed by %s: %s", agent_id, response)
            return {"status": "success", "data": response, "agent": agent_id}
        except Exception as e:
            logger.error("Error processing input with agent: %s", str(e))
            return {"status": "error", "message": str(e)}

    def update_state(self, key: str, value: Any) -> None:
        """Update the agent's internal state and notify listeners."""
        self.state[key] = value
        logger.debug("Updated state: %s = %s", key, value)
        self.notify_event("state_updated", key=key, value=value)

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from the agent's internal state."""
        return self.state.get(key, default)

    def save_state(self) -> None:
        """Save the current state of all agents to persistent storage."""
        logger.info("Saving MetaAgent state")
        for agent_id in list(
            self.agents.keys()
        ):  # Create a list to avoid runtime modification issues
            self.save_agent_state(agent_id)
        # TODO: Implement state persistence to file or database

    def load_state(self) -> None:
        """Load the state of all agents from persistent storage."""
        logger.info("Loading MetaAgent state")
        # TODO: Implement state loading from file or database

    def save_agent_state(self, agent_id: str) -> bool:
        """Save the state of a specific agent."""
        if agent_id in self.agents:
            try:
                agent = self.agents[agent_id]
                if hasattr(agent, "get_state"):
                    self.agent_states[agent_id] = agent.get_state()
                elif hasattr(agent, "state"):
                    self.agent_states[agent_id] = agent.state
                logger.debug("Saved state for agent: %s", agent_id)
                return True
            except Exception as e:
                logger.error("Error saving state for agent %s: %s", agent_id, str(e))
                return False
        return False

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler for UI or other components to react to agent events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info("Registered event handler for: %s", event_type)

    def notify_event(self, event_type: str, **kwargs) -> None:
        """Notify all handlers of a specific event type."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(**kwargs)
                except Exception as e:
                    logger.error(
                        "Error in event handler for %s: %s", event_type, str(e)
                    )

    def select_agent_for_task(self, task_type: str) -> Optional[tuple[str, Any]]:
        """Select an appropriate agent for a given task type based on capabilities."""
        # TODO: Implement sophisticated agent selection based on capabilities and task requirements
        for agent_id, agent in self.agents.items():
            if hasattr(agent, "can_handle_task") and agent.can_handle_task(task_type):
                return agent_id, agent
        # Fallback to any available agent if no specific match is found
        if self.agents:
            agent_id = list(self.agents.keys())[0]
            return agent_id, self.agents[agent_id]
        return None

    def register_default_agents(self) -> None:
        """Register default agents based on configuration or standard setup."""
        # TODO: Implement registration of standard agents based on configuration
        logger.info("Registering default agents")

    def enqueue_task(self, task: Dict[str, Any], priority: int = 0) -> None:
        """Enqueue a task for processing by an appropriate agent."""
        task_with_priority = task.copy()
        task_with_priority["priority"] = priority
        self.task_queue.append(task_with_priority)
        logger.debug("Enqueued task: %s with priority: %d", task, priority)
        self.notify_event("task_enqueued", task=task, priority=priority)

    def process_task_queue(self) -> None:
        """Process tasks from the queue, delegating to appropriate agents."""
        if not self.task_queue:
            return

        # Sort by priority (higher number = higher priority)
        self.task_queue.sort(key=lambda x: x.get("priority", 0), reverse=True)
        task = self.task_queue.pop(0)
        logger.debug("Processing task from queue: %s", task)
        result = self.process_input(task)
        self.notify_event("task_processed", task=task, result=result)
