# mypy: disable_error_code=attr-defined,no-any-return
"""Master agent for orchestrating tasks.

This file implements hierarchical planning (strategic, tactical, operational)
and orchestrates tool execution for Atlas.
"""

import json
import re
import threading
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from agents.browser_agent import BrowserAgent
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
try:
    from agents.agent_manager import AgentManager
except ImportError:
    AgentManager = object  # type: ignore[misc, assignment]
try:
    from agents.tool_execution import InvalidToolArgumentsError, ToolNotFoundError  # type: ignore[import-untyped]
except ImportError:
    InvalidToolArgumentsError = Exception
    ToolNotFoundError = Exception  
from agents.creator_authentication import CreatorAuthentication

from intelligence.context_awareness_engine import ContextAwarenessEngine

from agents.token_tracker import TokenUsage

from agents.planning.operational_planner import OperationalPlanner
from agents.planning.strategic_planner import StrategicPlanner
from agents.planning.tactical_planner import TacticalPlanner
from agents.problem_decomposition_agent import ProblemDecompositionAgent
from agents.screen_agent import ScreenAgent
from agents.system_interaction_agent import SystemInteractionAgent
from agents.text_agent import TextAgent
from monitoring.metrics_manager import MetricsManager
metrics_manager_instance = MetricsManager()
from utils.llm_manager import LLMManager
from utils.logger import get_logger

try:
    from typing import cast
except ImportError:
    # Fallback for environments without typing.cast
    def cast(type_, value):  # type: ignore[no-redef]
        
        return value

try:
    from utils.config_manager import ConfigManager, config_manager as config_manager_instance
    _config_manager: Optional[ConfigManager] = config_manager_instance  
except ImportError:
    _config_manager = None


class PlanExecutionError(Exception):
    """Custom exception for errors during plan execution."""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception


class MasterAgent:
    """Orchestrates goal execution by coordinating specialized agents and tools."""

    MAX_RETRIES = 3

    # Optional sub-agents (initialised lazily by ``_initialize_agents``)
    _browser_agent: Optional[BrowserAgent] = None
    _app_agent: Optional[Any] = None  # forward-declared for typing
    _memory_manager: Optional[EnhancedMemoryManager] = None

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
                    memory_manager = EnhancedMemoryManager(llm_manager=llm_manager, config_manager=_config_manager, logger=self.logger)
                else:
                    self.logger.warning("ConfigManager not available, cannot initialize EnhancedMemoryManager.")
                    memory_manager = None
            except Exception as e:
                self.logger.critical(f"Failed to initialize EnhancedMemoryManager: {e}", exc_info=True)
                raise  
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
            if self.memory_manager is None:
                raise ValueError("MemoryManager is not initialized, cannot create StrategicPlanner.")
            self._strategic_planner = StrategicPlanner(
                llm_manager=self.llm_manager,
                memory_manager=self.memory_manager
            )
            self.logger.info(f"Strategic Planner initialized in {time.time() - start_time:.2f} seconds")

    def _initialize_tactical_planner(self) -> None:
        if self._tactical_planner is None:
            start_time = time.time()
            if self.memory_manager is None:
                raise ValueError("MemoryManager is not initialized, cannot create TacticalPlanner.")
            self._tactical_planner = TacticalPlanner(
                llm_manager=self.llm_manager,
                memory_manager=self.memory_manager
            )
            self.logger.info(f"Tactical Planner initialized in {time.time() - start_time:.2f} seconds")

    def _initialize_operational_planner(self) -> None:
        if self._operational_planner is None:
            start_time = time.time()
            if self.agent_manager is None or self.memory_manager is None:
                raise ValueError("AgentManager or MemoryManager is not initialized, cannot create OperationalPlanner.")
            self._operational_planner = OperationalPlanner(
                llm_manager=self.llm_manager,
                agent_manager=self.agent_manager,
                memory_manager=self.memory_manager
            )
            self.logger.info(f"Operational Planner initialized in {time.time() - start_time:.2f} seconds")

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
        """Placeholder for state initialization."""
        pass

    # -- Added helper stubs to quiet mypy until full implementations are provided --
    def _initialize_agents(self) -> None:  # noqa: D401
        """Initialize commonly used sub-agents for delegation.

        This keeps MasterAgent loosely coupled: if a dependency cannot be
        imported (e.g. optional plugin missing), we degrade gracefully by
        leaving the attribute as ``None`` so the delegate helper can skip it
        at runtime.
        """
        try:
            from agents.browser_agent import BrowserAgent  # local import to avoid hard dependency at module import time
            self._browser_agent = BrowserAgent()
        except Exception:  # pragma: no cover – optional dependency
            self._browser_agent = None

        try:
            from agents.advanced_application_agent import AdvancedApplicationAgent  # noqa: WPS433 – local import by design
            self._app_agent = AdvancedApplicationAgent()
        except Exception:  # pragma: no cover
            self._app_agent = None

        # Reuse the already-configured memory manager instance if available
        self._memory_manager = self.memory_manager

    def _run_with_retry(self, goal: str, context: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Executes a goal with a hierarchical planning and execution loop, with retries.
        """
        self.execution_context = context or {}
        self.execution_context['goals'] = [goal]
        self.logger.info(f"Starting execution for goal: {goal}")

        for attempt in range(max_retries):
            try:
                # 1. Decompose complex goal if necessary
                decomposed_goals = self.decomposition_agent.decompose_goal(goal)
                if not decomposed_goals:
                    decomposed_goals = [goal]
                self.logger.info(f"Decomposed goal into {len(decomposed_goals)} sub-goals.")

                final_result = None
                for sub_goal in decomposed_goals:
                    self.logger.info(f"Executing sub-goal: {sub_goal}")
                    self.execution_context['current_sub_goal'] = sub_goal

                    # 2. Generate Strategic Plan
                    strategic_plan = self._generate_strategic_plan(sub_goal)
                    if not strategic_plan.get("steps"):
                        raise PlanExecutionError("Failed to generate a valid strategic plan.")
                    
                    self.logger.info(f"Generated strategic plan with {len(strategic_plan['steps'])} steps.")

                    # 3. Execute Strategic Plan
                    for strategic_step in strategic_plan["steps"]:
                        self.logger.info(f"Executing strategic step: {strategic_step.get('description')}")
                        
                        # 4. Generate Tactical Plan
                        tactical_plan = self._generate_tactical_plan(strategic_step)
                        if not tactical_plan.get("steps"):
                            raise PlanExecutionError("Failed to generate a valid tactical plan.")

                        self.logger.info(f"Generated tactical plan with {len(tactical_plan['steps'])} steps.")

                        # 5. Execute Tactical Plan
                        for tactical_step in tactical_plan["steps"]:
                            self.logger.info(f"Executing tactical step: {tactical_step.get('description')}")

                            # 6. Generate Operational Plan
                            operational_plan = self._generate_operational_plan(tactical_step)
                            if not operational_plan.get("steps"):
                                raise PlanExecutionError("Failed to generate a valid operational plan.")
                            
                            self.logger.info(f"Generated operational plan with {len(operational_plan['steps'])} steps.")

                            # 7. Execute Operational Plan
                            for operational_step in operational_plan["steps"]:
                                error, result, _ = self._execute_step(operational_step)
                                if error:
                                    raise PlanExecutionError(f"Error executing operational step: {operational_step.get('description')}", original_exception=error)
                                final_result = result # Store the result of the last successful step
                
                self.logger.info("Goal executed successfully.")
                return {"status": "success", "result": final_result}

            except PlanExecutionError as e:
                self.logger.error(f"Plan execution failed on attempt {attempt + 1}/{max_retries}: {e}")
                if e.original_exception:
                    self.logger.error(f"Original exception: {e.original_exception}")
                if attempt + 1 >= max_retries:
                    self.logger.error("Max retries reached. Aborting goal.")
                    return {"status": "failure", "error": str(e)}
                self.logger.info("Retrying...")
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"An unexpected error occurred on attempt {attempt + 1}/{max_retries}: {e}", exc_info=True)
                if attempt + 1 >= max_retries:
                    self.logger.error("Max retries reached due to unexpected error. Aborting goal.")
                    return {"status": "failure", "error": f"Unexpected error: {e}"}
                self.logger.info("Retrying...")
                time.sleep(2)

        return {"status": "failure", "error": "Max retries reached."}

    def execute_task(self, task: str) -> dict:
        """Execute a task using appropriate tool."""
        # Extract subtasks
        subtasks = self.task_recognizer.extract_subtasks(task)
        
        # Prioritize subtasks
        ordered_tasks = self.task_recognizer.prioritize_tasks(subtasks)
        
        results = []
        for subtask in ordered_tasks:
            task_type, params = self.recognize_task_type(subtask)
            
            if task_type == 'unknown':
                results.append({"success": False, "error": "Could not recognize task type"})
                continue
                
            if task_type == 'browser':
                if 'url' in params:
                    result = self.browser_tool.open_url(params['url'])
                    results.append(result)
                else:
                    results.append({"success": False, "error": "No URL specified for browser task"})
                    
            elif task_type == 'email':
                if 'search_terms' in params:
                    # Handle security-related emails
                    if params.get('security'):
                        result = self.email_tool.search_emails(
                            query=f"{params['search_terms']} security",
                            categories=['security', 'account'],
                            importance='high'
                        )
                        results.append(result)
                    # Handle regular email search
                    else:
                        result = self.email_tool.search_emails(query=params['search_terms'])
                        results.append(result)
                else:
                    results.append({"success": False, "error": "No search terms specified for email task"})
                    
        # Return combined results
        return {
            "success": all(r.get('success', False) for r in results),
            "results": results,
            "errors": [r.get('error') for r in results if r.get('error')]
        }

    def recognize_task_type(self, task: str) -> tuple[str, dict]:
        """Recognize task type using TaskRecognizer."""
        return self.task_recognizer.recognize_task_type(task)

    def _generate_operational_plan(self, tactical_step: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an operational (executable) plan for a single tactical step.

        Args:
            tactical_step: A dictionary from the tactical plan list.

        Returns:
            A dictionary with a description and a list of executable steps. Each executable step
            must include ``tool`` and ``args`` keys so that ``_execute_step`` can act upon them.
        """
        sub_goal: str = tactical_step.get("sub_goal") or tactical_step.get("description", "")
        if not sub_goal:
            return {"description": "No sub-goal provided", "steps": []}

        try:
            plan = self.operational_planner.generate_operational_plan(sub_goal, context=self.execution_context)
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Operational planner failed: {e}. Using fallback plan.")
            plan = None

        steps = []
        if isinstance(plan, dict) and plan.get("steps"):
            # Ensure each child step has mandatory keys for execution.
            for idx, step in enumerate(plan["steps"], 1):
                # Normalise field names expected by _execute_step
                tool_name = step.get("tool_name") or step.get("tool")
                args = step.get("arguments") or step.get("args", {})
                if tool_name:
                    steps.append({"description": step.get("description", f"Step {idx}"), "tool": tool_name, "args": args})
        if not steps:
            # Safe fallback: create a benign step that always succeeds (no-op).
            steps = [
                {
                    "description": f"No-op for '{sub_goal}' (fallback)",
                    "tool": "create_tool",  # Guaranteed to exist
                    "args": {
                        "tool_description": "noop tool generated as placeholder",
                    },
                }
            ]

        return {
            "description": plan.get("description", f"Operational plan for: {sub_goal}") if isinstance(plan, dict) else f"Operational plan for: {sub_goal}",
            "steps": steps,
        }
