"""Master agent for orchestrating tasks."""

import json
import re
import threading
import time
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from agents.browser_agent import BrowserAgent
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
try:
    from agents.agent_manager import AgentManager
except ImportError:
    AgentManager = object  # type: ignore[misc, assignment]
try:
    from agents.tool_execution import InvalidToolArgumentsError  # type: ignore[import-untyped]
except ImportError:
    InvalidToolArgumentsError = Exception  
try:
    from agents.tool_execution import ToolNotFoundError  
except ImportError:
    ToolNotFoundError = Exception  
try:
    from agents.models import CreatorAuthentication  # type: ignore[import-untyped]
except ImportError:
    CreatorAuthentication = Any

from agents.creator_authentication import CreatorAuthentication

from intelligence.context_awareness_engine import ContextAwarenessEngine

try:
    from agents.models import Plan, TokenUsage
except ImportError:
    class _FallbackTokenUsage:
        def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0) -> None:
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens
    TokenUsage = _FallbackTokenUsage

from agents.planning.operational_planner import OperationalPlanner
from agents.planning.strategic_planner import StrategicPlanner
from agents.planning.tactical_planner import TacticalPlanner
from agents.problem_decomposition_agent import ProblemDecompositionAgent
from agents.screen_agent import ScreenAgent
from agents.system_interaction_agent import SystemInteractionAgent
from agents.text_agent import TextAgent
from monitoring.metrics_manager import metrics_manager
from utils.llm_manager import LLMManager
from utils.logger import get_logger

try:
    from typing import cast
except ImportError:
    # Fallback for environments without typing.cast
    cast = lambda type_, value: value

try:
    from utils.config_manager import ConfigManager, config_manager as config_manager_instance
    _config_manager: Optional[ConfigManager] = config_manager_instance  
except ImportError:
    _config_manager = None


class MasterAgent:
    """Orchestrates goal execution by coordinating specialized agents and tools."""

    MAX_RETRIES = 3

    def __init__(
        self, 
        llm_manager: Any,  
        agent_id: str = "master-agent",
        agent_manager: Optional[AgentManager] = None,
        memory_manager: Optional[EnhancedMemoryManager] = None,  
        context_awareness_engine: Optional[ContextAwarenessEngine] = None,
        on_status_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        creator_auth: Optional[CreatorAuthentication] = None
    ) -> None:
        self.agent_id = agent_id
        self.goals: List[str] = []
        self.is_running = False
        self.execution_thread: Optional[threading.Thread] = None
        self.state_lock = threading.Lock()
        self.logger = get_logger()
        # If no components are provided we create minimal default instances so that
        # unit-tests can instantiate the MasterAgent with only an LLM manager.
        if memory_manager is None:
            try:
                if _config_manager is not None:
                    memory_manager = EnhancedMemoryManager(llm_manager=llm_manager, config_manager=_config_manager)  
                else:
                    memory_manager = None
            except Exception:  
                memory_manager = None  
        if context_awareness_engine is None:
            try:
                context_awareness_engine = ContextAwarenessEngine(project_root="")  
            except Exception:
                context_awareness_engine = None
        if agent_manager is None and memory_manager is not None:
            agent_manager = AgentManager(llm_manager=llm_manager, memory_manager=memory_manager)
        self.agent_manager = agent_manager  
        # Backwards-compat: expose agent_manager through `.agents` as expected by tests
        self.agents = self.agent_manager
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.context_awareness_engine = context_awareness_engine
        # Handle both old and new callback parameter names for backwards compatibility
        self.status_callback = status_callback or on_status_update
        self.creator_auth = creator_auth
        self.stop_event = threading.Event()
        self.last_executed_plan: Optional[Dict[str, Any]] = None
        self.last_plan: Optional[Dict[str, Any]] = None
        # Initialize execution context with consistent type
        if not hasattr(self, 'execution_context'):
            self.execution_context: Dict[str, Any] = {}
        self._plan_cache: Dict[str, Dict[str, Any]] = {}

        # Initialize hierarchical planners with lazy loading to reduce startup latency
        start_time = time.time()
        self._strategic_planner: Optional[Any] = None  
        self._tactical_planner: Optional[Any] = None  
        self._operational_planner: Optional[Any] = None  
        self.logger.info("Planners set to lazy initialization mode to reduce startup time")

        # Problem decomposition agent for breaking down complex goals
        self.decomposition_agent = ProblemDecompositionAgent(llm_manager)
        self.current_goal_index: int = 0
        self.is_waiting_for_clarification: bool = False
        self.last_clarification_request: Optional[str] = None
        # Callback for updating tool list in UI or other integrations
        self.tool_update_callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None
        # Initialize state
        self._initialize_state()

    @property
    def strategic_planner(self) -> Any:
        if self._strategic_planner is None:
            self._initialize_strategic_planner()
        return self._strategic_planner  

    @property
    def tactical_planner(self) -> Any:
        if self._tactical_planner is None:
            self._initialize_tactical_planner()
        return self._tactical_planner  

    @property
    def operational_planner(self) -> Any:
        if self._operational_planner is None:
            self._initialize_operational_planner()
        return self._operational_planner  

    def run(
        self, 
        goal: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if self.is_running:
            raise RuntimeError("An objective is already running")
        
        self.is_running = True
        try:
            # Delegate to a method that handles retries
            return self._run_with_retry(goal, context)
        finally:
            self.is_running = False

    def _initialize_strategic_planner(self) -> None:
        if self._strategic_planner is None:
            start_time = time.time()
            try:
                from agents.strategic_planning_agent import StrategicPlanningAgent  # type: ignore[import-untyped]
                self._strategic_planner = StrategicPlanningAgent(
                    llm_manager=self.llm_manager,  
                    agent_manager=self.agent_manager,  
                    memory_manager=self.memory_manager  
                )
                self.logger.info(f"Strategic Planner initialized in {time.time() - start_time:.2f} seconds")
            except ImportError as e:
                self.logger.error(f"Failed to initialize Strategic Planner: {e}")
                raise

    def _initialize_tactical_planner(self) -> None:
        if self._tactical_planner is None:
            start_time = time.time()
            try:
                from agents.tactical_planning_agent import TacticalPlanningAgent  # type: ignore[import-untyped]
                self._tactical_planner = TacticalPlanningAgent(
                    llm_manager=self.llm_manager,  
                    agent_manager=self.agent_manager,  
                    memory_manager=self.memory_manager  
                )
                self.logger.info(f"Tactical Planner initialized in {time.time() - start_time:.2f} seconds")
            except ImportError as e:
                self.logger.error(f"Failed to initialize Tactical Planner: {e}")
                raise

    def _initialize_operational_planner(self) -> None:
        if self._operational_planner is None:
            start_time = time.time()
            try:
                from agents.operational_planning_agent import OperationalPlanningAgent  # type: ignore[import-untyped]
                self._operational_planner = OperationalPlanningAgent(
                    llm_manager=self.llm_manager,  
                    agent_manager=self.agent_manager,  
                    memory_manager=self.memory_manager  
                )
                self.logger.info(f"Operational Planner initialized in {time.time() - start_time:.2f} seconds")
            except ImportError as e:
                self.logger.error(f"Failed to initialize Operational Planner: {e}")
                raise

    def _execute_step(self, step: Dict[str, Any]) -> Tuple[Optional[Exception], Optional[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()
        self.logger.debug(f"Executing step: {step.get('description', 'Unnamed step')}")
        error = None
        result = None
        status_update: Dict[str, Any] = {}
        try:
            tool_name = step.get("tool", "")
            args = step.get("args", {})
            self.logger.info(f"Executing step with tool: {tool_name}")
            result = self._execute_tool(tool_name, args)
            elapsed_time = time.time() - start_time
            self.logger.info(f"Step executed in {elapsed_time:.2f} seconds")
            if elapsed_time > 0.1:  # Log warning if step execution takes more than 100ms
                self.logger.warning(f"Step execution exceeded latency target: {elapsed_time:.2f} seconds")
            return None, result, {}
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"Error executing step after {elapsed_time:.2f} seconds: {str(e)}")
            return e, None, {}

    def _execute_tool(self, tool_name: str, tool_arguments: Dict[str, Any]) -> Any:
        if self.agent_manager is None:  
            raise ValueError("No AgentManager available to execute tools")
        try:
            result = self.agent_manager.execute_tool(tool_name, tool_arguments)  
            self.logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

    def get_all_agent_names(self) -> List[str]:
        if self.agent_manager is None:
            return []
        if hasattr(self.agent_manager, "get_all_agent_names"):
            result = self.agent_manager.get_all_agent_names()
            return result if isinstance(result, list) else []
        elif hasattr(self.agent_manager, "get_all_agents"):
            agents_dict = self.agent_manager.get_all_agents()
            return list(agents_dict.keys()) if isinstance(agents_dict, dict) else []
        return []

    def _initialize_state(self) -> None:
        """Placeholder for state initialization method to resolve type error."""
        pass

    def _run_with_retry(self, goal: str, context: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Placeholder for retry execution method to resolve type error."""
        return None

    def start(self, execution_context: Optional[Dict[str, Any]] = None) -> None:
        with self.state_lock:
            if self.is_running:
                self.logger.warning("Cannot start agent: Agent is already running")
                return
            self.is_running = True

    def _generate_strategic_plan(self, goal: str) -> Dict[str, Any]:
        if self.execution_context is None:
            return {}
        # Ensure strategic planner is available
        planner = self.strategic_planner
        assert planner is not None, "Strategic planner should be initialized"
        plan = planner.generate_strategic_plan(
            context=self.execution_context,
            goals=self._get_available_goals(),
            agent_id=self.agent_id
        )
        return plan if isinstance(plan, dict) else {}

    def _get_available_goals(self) -> List[str]:
        if self.execution_context is None:
            return []
        goals = self.execution_context.get("goals", [])
        if not isinstance(goals, list):
            return []
        return [str(goal) for goal in goals]

    def continue_with_feedback(self, feedback: str) -> None:
        """Continue execution with user feedback."""
        self.logger.info(f"Received feedback: {feedback}")
        # Implementation would handle feedback and continue execution
        pass

    def provide_clarification(self, clarification: str) -> None:
        """Provide clarification for the current task."""
        self.logger.info(f"Received clarification: {clarification}")
        self.is_waiting_for_clarification = False
        self.last_clarification_request = None
        # Implementation would handle clarification and continue execution
        pass

    def pause(self) -> None:
        """Pause execution."""
        with self.state_lock:
            if self.is_running:
                self.logger.info("Pausing agent execution")
                # Implementation would pause execution
                pass

    def stop(self) -> None:
        """Stop execution."""
        with self.state_lock:
            if self.is_running:
                self.logger.info("Stopping agent execution")
                self.is_running = False
                self.stop_event.set()
                if self.execution_thread and self.execution_thread.is_alive():
                    self.execution_thread.join(timeout=5.0)

    def record_feedback(self, feedback: str) -> None:
        """Record user feedback."""
        self.logger.info(f"Recording feedback: {feedback}")
        if self.memory_manager:
            try:
                self.memory_manager.add_memory(
                    content=f"User feedback: {feedback}",
                    collection_name="feedback",
                    metadata={"agent_id": self.agent_id, "timestamp": time.time()}
                )
            except Exception as e:
                self.logger.error(f"Failed to record feedback: {e}")

    @property
    def thread(self) -> Optional[threading.Thread]:
        """Get the execution thread."""
        return self.execution_thread
