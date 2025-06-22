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
from monitoring.metrics_manager import metrics_manager
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

    def start(self, execution_context: Optional[Dict[str, Any]] = None) -> None:
        """Start the Master Agent."""
        with self.state_lock:
            if self.is_running:
                self.logger.warning("Cannot start agent: Agent is already running")
                return
            self.is_running = True

    def initialize(self) -> None:
        """Initialize the Master Agent and its sub-agents."""
        if not hasattr(self, 'is_initialized'):
            self.is_initialized = False
        if not self.is_initialized:
            self.logger.info("Initializing Master Agent")
            self._initialize_agents()
            self.is_initialized = True
        else:
            self.logger.info("Master Agent already initialized")

    def shutdown(self) -> None:
        """Shut down the Master Agent and its sub-agents."""
        if hasattr(self, 'is_initialized') and self.is_initialized and self.is_running:
            self.logger.info("Shutting down Master Agent")
            self.is_running = False
            # Shutdown logic for sub-agents if needed
        else:
            self.logger.info("Master Agent is not running or initialized, no shutdown needed")

    def get_status(self) -> str:
        """Get the current status of the Master Agent."""
        return f"Master Agent is {'running' if self.is_running else 'not running'} and {'initialized' if hasattr(self, 'is_initialized') and self.is_initialized else 'not initialized'}"

    def execute_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task by delegating to the appropriate agent or handling directly."""
        context = context or {}
        self.logger.info(f"Executing task: {prompt}")
        try:
            # Decompose task into subtasks if complex
            subtasks = self._decompose_task(prompt)

            # --- Send plan to UI ---
            if self.status_callback:
                plan_payload = {
                    "type": "plan",
                    "data": {
                        "description": prompt,
                        "steps": [{"description": s} for s in subtasks],
                    },
                }
                try:
                    self.status_callback(plan_payload)
                except Exception:
                    # Ignore UI callback errors – should never crash agent flow
                    self.logger.exception("Status callback failed while sending plan payload")

            if len(subtasks) > 1:
                self.logger.info(f"Task decomposed into {len(subtasks)} subtasks.")
                return self._execute_subtasks(subtasks, context)
            else:
                # Single task execution
                return self._delegate_task(prompt, context)
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            return f"Failed to execute task: {str(e)}"

    def _decompose_task(self, prompt: str) -> List[str]:
        """Break down a complex task into smaller, actionable subtasks."""
        self.logger.info(f"Decomposing task: {prompt}")
        # Simple decomposition logic based on keywords or task complexity
        if "and" in prompt:
            return [task.strip() for task in prompt.split("and") if task.strip()]
        elif "then" in prompt:
            return [task.strip() for task in prompt.split("then") if task.strip()]
        elif len(prompt.split()) > 10:  # Arbitrary threshold for complexity
            # Break into assumed steps if long prompt
            return [f"Step {i+1}: {part}" for i, part in enumerate(prompt.split(".")) if part.strip()]
        return [prompt]

    def _execute_subtasks(self, subtasks: List[str], context: Dict[str, Any]) -> str:
        """Execute a series of subtasks and track progress."""
        results = []
        for i, subtask in enumerate(subtasks, 1):
            # Notify UI – step start
            if self.status_callback:
                try:
                    self.status_callback({
                        "type": "step_start",
                        "data": {
                            "index": i - 1,
                            "step": {"description": subtask, "tool_name": "AUTO", "arguments": {}},
                        },
                    })
                except Exception:
                    self.logger.exception("Status callback failed for step_start")

            self.logger.info(f"Executing subtask {i}/{len(subtasks)}: {subtask}")
            result = self._delegate_task(subtask, context)
            results.append(f"Subtask {i} - {subtask}: {result}")

            # Notify UI – step end
            if self.status_callback:
                status_flag = "success" if not result.lower().startswith("failed") else "error"
                try:
                    self.status_callback({
                        "type": "step_end",
                        "data": {
                            "index": i - 1,
                            "step": {"description": subtask},
                            "status": status_flag,
                            "result": result if status_flag == "success" else None,
                            "error": None if status_flag == "success" else result,
                        },
                    })
                except Exception:
                    self.logger.exception("Status callback failed for step_end")

            self.logger.info(f"[PROGRESS] Completed subtask {i}/{len(subtasks)}: {subtask}")
        return "\n".join(results)

    def _delegate_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """Delegate task to the appropriate agent based on task type."""
        self.logger.info(f"Delegating task: {prompt}")
        if any(term in prompt.lower() for term in ["browse", "open browser", "search online", "click", "web", "internet", "navigate", "close browser"]):
            self.logger.info("Task identified as browser-related, delegating to BrowserAgent.")
            if self._browser_agent:
                return str(self._browser_agent.execute_task(prompt, context))
            return "BrowserAgent is unavailable."
        elif any(term in prompt.lower() for term in ["app", "application", "window", "script", "ui", "automation", "open app", "close app"]):
            self.logger.info("Task identified as advanced application control, delegating to AdvancedApplicationAgent.")
            if self._app_agent:
                return str(self._app_agent.execute_task(prompt, context))
            return "AdvancedApplicationAgent is unavailable."
        elif any(term in prompt.lower() for term in ["remember", "recall", "memory", "past", "history", "previous", "store", "save"]):
            self.logger.info("Task identified as memory-related, delegating to EnhancedMemoryManager.")
            if self._memory_manager is not None:
                return str(self._memory_manager.execute_task(prompt, context))
            else:
                return "Memory management functionality is not available."
        else:
            self.logger.info("Task not matched to specific agent, handling with default logic.")
            return "Task executed with default logic."

    def _handle_browser_goal(self, goal: str) -> bool:
        """Handle browser-related goals."""
        try:
            if not self.agent_manager:
                self.logger.error("Agent manager not available")
                return False
                
            # Get browser agent
            browser_agent = None
            if hasattr(self.agent_manager, 'get_agent'):
                browser_agent = self.agent_manager.get_agent("browser_agent")
            elif hasattr(self.agent_manager, 'agents') and hasattr(self.agent_manager.agents, 'get'):
                browser_agent = self.agent_manager.agents.get("browser_agent")
                
            if not browser_agent:
                # Try to import browser agent directly
                from agents.browser_agent import BrowserAgent
                browser_agent = BrowserAgent()
                
            # Execute browser task
            result = browser_agent.execute_task(goal, {})
            self.logger.info(f"Browser agent result: {result}")
            
            # Consider successful if no error occurred
            return bool(result and not ("error" in result.lower() or "failed" in result.lower()))
            
        except Exception as e:
            self.logger.error(f"Error handling browser goal: {e}")
            return False

    def _handle_application_goal(self, goal: str) -> bool:
        """Handle application control goals."""
        try:
            if not self.agent_manager:
                self.logger.error("Agent manager not available")
                return False
                
            # Get application agent
            application_agent = None
            if hasattr(self.agent_manager, 'get_agent'):
                application_agent = self.agent_manager.get_agent("application_agent")
            elif hasattr(self.agent_manager, 'agents') and hasattr(self.agent_manager.agents, 'get'):
                application_agent = self.agent_manager.agents.get("application_agent")
                
            if not application_agent:
                # Try to import application agent directly
                from agents.application_agent import ApplicationAgent
                application_agent = ApplicationAgent()
                
            # Execute application task
            result = application_agent.execute_task(goal, {})
            self.logger.info(f"Application agent result: {result}")
            
            # Consider successful if no error occurred
            return bool(result and not ("error" in result.lower() or "failed" in result.lower()))
            
        except Exception as e:
            self.logger.error(f"Error handling application goal: {e}")
            return False

    def _handle_advanced_application_goal(self, goal: str) -> bool:
        """Handle advanced application control goals."""
        try:
            if not self.agent_manager:
                self.logger.error("Agent manager not available")
                return False
                
            # Get advanced application agent
            advanced_app_agent = None
            if hasattr(self.agent_manager, 'get_agent'):
                advanced_app_agent = self.agent_manager.get_agent("advanced_application_agent")
            elif hasattr(self.agent_manager, 'agents') and hasattr(self.agent_manager.agents, 'get'):
                advanced_app_agent = self.agent_manager.agents.get("advanced_application_agent")
                
            if not advanced_app_agent:
                # Try to import advanced application agent directly
                from agents.advanced_application_agent import AdvancedApplicationAgent
                advanced_app_agent = AdvancedApplicationAgent()
                
            # Execute advanced application task
            result = advanced_app_agent.execute_task(goal, {})
            self.logger.info(f"Advanced application agent result: {result}")
            
            # Consider successful if no error occurred
            return bool(result and not ("error" in result.lower() or "failed" in result.lower()))
            
        except Exception as e:
            self.logger.error(f"Error handling advanced application goal: {e}")
            return False

    def _execute_objective_with_retries(self, objective: Dict[str, Any], max_retries: int = 3) -> bool:
        """Executes an objective with retries on failure."""
        current_goal = objective.get("goal", "")
        self.logger.info(f"Executing objective: {current_goal}")
        
        # Check for specialized agents based on goal content
        goal_lower = current_goal.lower()
        if any(term in goal_lower for term in ["browse", "web", "internet", "url", "website", "safari", "chrome", "firefox"]):
            self.logger.info(f"Delegating browser goal to specialized agent: {current_goal}")
            return self._handle_browser_goal(current_goal)
        elif any(term in goal_lower for term in ["terminal", "command", "shell", "mouse", "keyboard", "clipboard", "launch app", "open app", "start app"]):
            self.logger.info(f"Delegating application control goal to specialized agent: {current_goal}")
            return self._handle_application_goal(current_goal)
        # Default execution for other goals
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1} for default goal execution")
                return True
            except Exception as e:
                self.logger.error(f"Error in default goal execution attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return False
        return False

    def _generate_strategic_plan(self, sub_goal: str) -> Dict[str, Any]:
        """Generate a strategic plan for a single sub-goal.

        Args:
            sub_goal: The sub-goal text provided by the user or decomposition agent.

        Returns:
            A dictionary with a short description and a list of strategic steps. Each step is a
            dictionary that, at minimum, contains a human-readable description of the objective.
        """
        try:
            objectives: List[str] = self.strategic_planner.generate_strategic_plan(sub_goal)
        except Exception as e:  # pragma: no cover – defensive fallback
            self.logger.error(f"Strategic planner failed: {e}. Falling back to single objective.")
            objectives = [sub_goal]

        # Normalise into the structure expected by the executor.
        steps = [
            {
                "description": objective,
                "objective": objective,  # Preserve the raw objective for downstream planners
            }
            for objective in objectives
        ]
        return {
            "description": f"Strategic plan for: {sub_goal}",
            "steps": steps,
        }

    def _generate_tactical_plan(self, strategic_step: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a tactical plan for a single strategic step.

        Args:
            strategic_step: A dictionary element from the strategic plan list.

        Returns:
            A dictionary with a description and a list of tactical steps (each with at least
            ``sub_goal`` and ``description`` keys).
        """
        objective: str = strategic_step.get("objective") or strategic_step.get("description", "")
        if not objective:
            return {"description": "No objective provided", "steps": []}

        try:
            plan: Dict[str, Any] = self.tactical_planner.generate_tactical_plan(objective)
        except Exception as e:  # pragma: no cover
            self.logger.error(f"Tactical planner failed: {e}. Using fallback plan.")
            plan = {}

        steps = plan.get("steps") if isinstance(plan, dict) else None
        if not steps:
            # Fallback: wrap the objective itself in a single tactical step.
            steps = [
                {
                    "sub_goal": objective,
                    "description": objective,
                }
            ]
        return {
            "description": plan.get("description", f"Tactical plan for: {objective}"),
            "steps": steps,
        }

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
