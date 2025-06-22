"""Master agent for orchestrating tasks."""

import json
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from agents.browser_agent import BrowserAgent
from agents.enhanced_memory_manager import EnhancedMemoryManager as MemoryManager, MemoryScope, MemoryType
try:
    from agents.agent_manager import AgentManager
except ImportError:
    AgentManager = Any  # type: ignore[assignment,misc]

try:
    from agents.tool_execution import InvalidToolArgumentsError
except ImportError:
    InvalidToolArgumentsError = Exception  # type: ignore[assignment,misc]

try:
    from agents.tool_execution import ToolNotFoundError
except ImportError:
    ToolNotFoundError = Exception  # type: ignore[assignment,misc]

try:
    from agents.models import CreatorAuthentication  # type: ignore[import-not-found]
except ImportError:
    CreatorAuthentication = Any
from agents.creator_authentication import CreatorAuthentication

from intelligence.context_awareness_engine import ContextAwarenessEngine

try:
    from agents.models import Plan, TokenUsage
except ImportError:
    class _FallbackTokenUsage:
        def __init__(self, prompt_tokens=0, completion_tokens=0, total_tokens=0):
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
    from typing import cast as cast_func
    cast = cast_func
except ImportError:
    def cast(type_, value):
        return value

try:
    from utils.config_manager import config_manager as config_manager_instance
    _cfg = config_manager_instance
except ImportError:
    _cfg = None


class PlanExecutionError(Exception):
    """Custom exception for errors during plan execution, containing the failed step."""
    def __init__(self, message: str, step: Dict[str, Any], original_exception: Exception):
        super().__init__(message)
        self.step = step
        self.original_exception = original_exception

    def __str__(self):
        return f"{self.args[0]} (in step: {self.step.get('description', 'N/A')})"


class MasterAgent:
    """Orchestrates goal execution by coordinating specialized agents and tools."""

    MAX_RETRIES = 3

    def __init__(
        self,
        llm_manager: "LLMManager",
        prompt: str = "",
        agent_manager: Optional[AgentManager] = None,  
        memory_manager: Optional["MemoryManager"] = None,
        context_awareness_engine: Optional["ContextAwarenessEngine"] = None,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        options: Optional[Dict[str, Any]] = None,
        creator_auth: Optional["CreatorAuthentication"] = None,
    ):
        self.goals: List[str] = []
        self.prompt: str = prompt
        self.options = options or {}
        self.is_running: bool = False
        self.is_paused: bool = False
        self.thread: Optional[threading.Thread] = None
        self.state_lock = threading.Lock()
        self.logger = get_logger()
        # If no components are provided we create minimal default instances so that
        # unit-tests can instantiate the MasterAgent with only an LLM manager.
        if memory_manager is None:
            try:
                if _cfg is not None:
                    memory_manager = MemoryManager(llm_manager=llm_manager, config_manager=_cfg)  
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
        self.status_callback = status_callback
        self.creator_auth = creator_auth  
        self.stop_event = threading.Event()
        self.last_executed_plan: Optional[Dict[str, Any]] = None
        self.last_plan: Optional[Dict[str, Any]] = None
        self.execution_context: Dict[str, Any] = {}
        self._plan_cache: Dict[str, Dict[str, Any]] = {}

        # Initialize hierarchical planners with lazy loading to reduce startup latency
        start_time = time.time()
        self._strategic_planner: Optional[StrategicPlanner] = None
        self._tactical_planner: Optional[TacticalPlanner] = None
        self._operational_planner: Optional[OperationalPlanner] = None
        self._problem_decomposition_agent: Optional[OperationalPlanner] = None
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
    def strategic_planner(self) -> StrategicPlanner:
        if self._strategic_planner is None:
            self._strategic_planner = StrategicPlanner(self.llm_manager, self.memory_manager if self.memory_manager else None)  # type: ignore[arg-type]
            self.logger.info("StrategicPlanner lazily initialized")
        return self._strategic_planner  # type: ignore[return-value]

    @property
    def tactical_planner(self) -> TacticalPlanner:
        if self._tactical_planner is None:
            self._tactical_planner = TacticalPlanner(self.llm_manager, self.memory_manager if self.memory_manager else None)  # type: ignore[arg-type]
            self.logger.info("TacticalPlanner lazily initialized")
        return self._tactical_planner  # type: ignore[return-value]

    @property
    def operational_planner(self) -> OperationalPlanner:
        if self._operational_planner is None:
            self._operational_planner = OperationalPlanner(self.llm_manager, self.memory_manager if self.memory_manager else None, self.agent_manager)  # type: ignore[arg-type]
            self.logger.info("OperationalPlanner lazily initialized")
        return self._operational_planner  # type: ignore[return-value]

    @property
    def problem_decomposition_agent(self) -> OperationalPlanner:
        if self._problem_decomposition_agent is None:
            self._problem_decomposition_agent = OperationalPlanner(self.llm_manager, self.memory_manager if self.memory_manager else None, agent_manager=None)  # type: ignore[arg-type]
            self.logger.info("ProblemDecompositionAgent lazily initialized")
        return self._problem_decomposition_agent  # type: ignore[return-value]

    def run(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> None:
        """Starts the agent's execution loop in a new thread."""
        if self.is_running:
            # Avoid starting a new thread if already running
            return
        self.is_running = True
        self.stop_event.clear()
        # Start execution in a separate thread to allow UI or other integrations to remain responsive
        execution_thread = threading.Thread(
            target=self._execution_loop, args=(goal, master_prompt, options), name="Execution Loop"
        )
        execution_thread.daemon = True
        execution_thread.start()
        # No logging here to reduce overhead in critical path

    def _execution_loop(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> None:
        """Main execution loop that runs until goal completion or interruption."""
        # Set up initial context
        self.execution_context = {
            "goal": goal,
            "master_prompt": master_prompt,
            "options": options,
            "current_plan": None,
            "current_step": 0,
            "total_steps": 0,
            "completed_steps": 0,
            "status": "initializing",
        }
        # Minimize logging in the loop to reduce overhead
        try:
            # Initial status update only
            self._update_status("Initializing goal processing")
            plan = self._generate_strategic_plan(goal, master_prompt, options)
            self.execution_context["current_plan"] = plan
            self.execution_context["total_steps"] = len(plan.get("steps", []))
            self.execution_context["status"] = "executing"
            # Execute each step without per-step logging
            for step_idx, step in enumerate(plan.get("steps", [])):
                if self.stop_event.is_set():
                    self.execution_context["status"] = "interrupted"
                    break
                self.execution_context["current_step"] = step_idx + 1
                self._execute_step(step, goal, master_prompt, options)
                self.execution_context["completed_steps"] = step_idx + 1
            if self.execution_context["status"] != "interrupted":
                self.execution_context["status"] = "completed"
        except Exception as e:
            self.execution_context["status"] = "error"
            self.execution_context["error"] = str(e)
            # Log only on error to reduce overhead
            self.logger.error(f"Execution loop error: {e}")
        finally:
            self.is_running = False
            # Final status update only
            self._update_status(f"Execution {self.execution_context.get('status', 'unknown')}")

    def pause(self) -> None:
        """Pauses or resumes the execution loop."""
        with self.state_lock:
            if not self.is_running:
                self.logger.warning("Cannot pause, agent is not running.")
                return
            self.is_paused = not self.is_paused
            status = "paused" if self.is_paused else "resumed"
            self.logger.info(f"MasterAgent execution {status}.")

    def record_feedback(self, goal: str, positive: bool):
        """Records user feedback about the execution of a goal."""
        plan_to_record = self.last_plan or self.last_executed_plan
        if not plan_to_record:
            self.logger.warning("Cannot record feedback: no plan was executed.")
            return

        feedback_str = "positive" if positive else "negative"
        memory_content = (
            f"User provided {feedback_str} feedback for the goal: '{goal}'.\n"
            f"The executed plan was:\n{json.dumps(plan_to_record, indent=2)}"
        )

        if self.memory_manager:
            self.memory_manager.add_memory(
                content=memory_content,
                metadata={"goal": goal, "feedback": feedback_str, "plan_id": plan_to_record.get("id", "N/A")},
            )

        self.logger.info(f"Stored {feedback_str} feedback for goal: '{goal}'")

    def stop(self) -> None:
        """Stops the agent's execution loop."""
        with self.state_lock:
            self.is_running = False
            self.is_paused = False
            self.stop_event.set()
        self.logger.info("Agent stopped.")
        if self.status_callback is not None:
            self.status_callback({"type": "info", "content": "Agent stopped."})

    def continue_with_feedback(self, feedback: str) -> None:
        """Continues execution with user feedback."""
        with self.state_lock:
            self.is_paused = False
        self.logger.info(f"Continuing with feedback: {feedback}")
        if self.status_callback is not None:
            self.status_callback({
                "type": "info",
                "content": f"Continuing with feedback: {feedback}",
            })
        if self.last_goal:
            self._generate_and_execute_plan(self.last_goal, user_feedback=feedback)
        else:
            self.logger.error("No last goal to continue with feedback.")
            if self.status_callback is not None:
                self.status_callback({
                    "type": "error",
                    "content": "No previous goal to continue with feedback.",
                })

    def provide_clarification(self, clarification: str) -> None:
        """Provides clarification for the current goal or execution."""
        with self.state_lock:
            self.is_paused = False
        self.logger.info(f"Received clarification: {clarification}")
        if self.status_callback is not None:
            self.status_callback({
                "type": "info",
                "content": f"Clarification provided: {clarification}",
            })
        if self.last_goal:
            self._generate_and_execute_plan(self.last_goal, user_feedback=clarification)
        else:
            self.logger.error("No last goal to apply clarification to.")
            if self.status_callback is not None:
                self.status_callback({
                    "type": "error",
                    "content": "No previous goal to apply clarification to.",
                })

    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extracts a JSON object from a text response."""
        text = text.strip()
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start == -1 and json_end == -1:
            json_start = text.find("[")
            json_end = text.rfind("]")
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_text = text[json_start:json_end + 1]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON from response: {json_text}", exc_info=True)
                raise ValueError(f"Invalid JSON in response: {str(e)}")
        raise ValueError("No valid JSON object found in response")

    def _recover_from_error(self, error: Exception, goal: str, failed_step: Dict[str, Any]) -> Dict[str, Any]:
        """Recovers from an error by generating a new plan or escalating the issue."""
        self.logger.info(f"Recovering from error: {str(error)}")
        if self.status_callback is not None:
            self.status_callback({
                "type": "info",
                "content": "Recovering from error...",
            })

        recovery_goal = self._create_recovery_goal(error, goal, failed_step)
        recovery_plan = self._generate_plan(recovery_goal)
        return self._execute_plan(recovery_plan)

    def _create_recovery_goal(self, error: Exception, original_goal: str, failed_step: Dict[str, Any]) -> str:
        """Creates a recovery goal based on the error and failed step."""
        error_type = type(error).__name__
        error_message = str(error)
        step_description = failed_step.get("description", "Unknown step")

        recovery_goal = (
            f"Recover from {error_type} in step '{step_description}' during pursuit of goal: {original_goal}. "
            f"Error message: {error_message}. Devise an alternative approach or workaround to overcome this issue "
            f"and achieve the original intent of the step."
        )
        self.logger.info(f"Created recovery goal: {recovery_goal}")
        return recovery_goal

    def _execute_objective(self, current_goal: str) -> None:
        """Executes a single objective (goal or sub-goal) by generating and executing a plan."""
        if not self.is_running:
            self.logger.warning("Attempted to execute objective while agent is not running.")
            return
        if self.is_paused:
            self.logger.info("Execution paused. Waiting for user input...")
            while self.is_paused and self.is_running:
                time.sleep(0.5)
            if not self.is_running:
                self.logger.info("Agent stopped while paused.")
                return
        try:
            self._execute_objective_with_retries(current_goal)
        except Exception as e:
            self.logger.error(f"Error executing objective: {str(e)}")
            if self.status_callback is not None:
                self.status_callback({"type": "error", "content": f"Failed to achieve goal '{current_goal}' due to an unexpected error."})

    def _execute_objective_with_retries(self, goal: str) -> Dict[str, Any]:
        """Executes an objective with retries and error recovery."""
        for attempt in range(self.MAX_RETRIES):
            try:
                plan = self._generate_plan(goal)
                self.last_plan = plan  
                result = self._execute_plan(plan)
                if result.get("status") == "complete":
                    return {"status": "success", "result": result}
            except PlanExecutionError as e:
                self.logger.error(f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed for goal '{goal}': {str(e)}", exc_info=True)
                if attempt == self.MAX_RETRIES - 1:
                    raise PlanExecutionError(f"Failed to execute goal '{goal}' after {self.MAX_RETRIES} attempts", {}, original_exception=e)
                delay = 2 ** attempt  
                self.logger.info(f"Retrying goal '{goal}' after {delay} seconds...")
                if self.status_callback is not None:
                    self.status_callback({
                        "type": "warning",
                        "content": f"Attempt {attempt + 1} failed. Retrying in {delay} seconds..."
                    })
                time.sleep(delay)
        raise PlanExecutionError(f"Failed to execute goal '{goal}' after {self.MAX_RETRIES} attempts", {}, original_exception=Exception(f"Max retries reached for goal: {goal}"))

    def run_once(self, goal: str) -> None:
        """Runs the full hierarchical planning and execution loop for a given goal."""
        if self.is_paused or not self.is_running:
            return

        if self.status_callback is not None:
            self.status_callback({"type": "info", "content": f"Starting new goal: {goal}"})
        self.last_goal = goal
        original_goal = goal

        is_ambiguous, question = self._check_goal_ambiguity(goal)
        if is_ambiguous:
            self.is_waiting_for_clarification = True
            self.last_clarification_request = question
            self.is_paused = True
            if self.status_callback is not None:
                self.status_callback({"type": "request_clarification", "content": question})
            self.logger.info(f"Goal '{goal}' is ambiguous. Asking for clarification: {question}")
            return

        is_complex_goal = len(goal.split()) > 20
        if is_complex_goal:
            self.logger.info("Complex goal detected. Engaging Tree-of-Thought for decomposition.")
            sub_goals = self.decomposition_agent.decompose_goal(goal)
            sub_goals = cast("List[str]", sub_goals)  
            self.logger.info(f"Decomposed complex goal into {len(sub_goals)} sub-goals.")
        else:
            sub_goals = [goal]

        try:
            for sub_goal in sub_goals:
                self.logger.info(f"Processing objective: '{sub_goal}'")
                self._execute_objective_with_retries(sub_goal)

            self.logger.info(f"Successfully completed main goal: '{original_goal}'")
            if self.status_callback is not None:
                self.status_callback({"type": "info", "content": "Goal achieved successfully."})

        except Exception as e:
            self.logger.error(f"Failed to achieve goal '{original_goal}' due to a critical error in one of its objectives: {e}", exc_info=True)
            if self.status_callback is not None:
                self.status_callback({"type": "error", "content": f"Failed to achieve goal '{original_goal}'."})

    def _generate_plan(self, goal: str, error_context: str = "") -> Dict[str, Any]:
        if goal in self._plan_cache and not error_context:
            self.logger.info(f"Using cached plan for goal: {goal}")
            return self._plan_cache[goal]
        plan = self.strategic_planner.generate_plan(goal, error_context)  
        self._plan_cache[goal] = plan
        return plan

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        if plan is None:
            self.logger.error("Plan is None, cannot execute.")
            raise ValueError("Plan is None")
        steps = plan.get("steps", [])
        if not steps:
            self.logger.warning("Plan has no steps to execute.")
            return {"status": "error", "error": "Plan has no steps to execute."}
        self.logger.info("Starting plan execution.")
        self.execution_context = {}  
        last_result: Any = None  

        i = 0
        while i < len(steps):
            step = steps[i]
            if step is None:
                self.logger.warning(f"Step {i+1} is None, skipping.")
                i += 1
                continue

            if not self.is_running:
                self.logger.info("Execution stopped mid-plan.")
                return {"status": "stopped", "error": "Execution stopped by user."}

            while self.is_paused:
                time.sleep(0.1)

            step_num = i + 1
            tool_name = "unknown"
            resolved_args = {}
            try:
                if "agent" in step:
                    agent_name = step["agent"]
                    prompt_str = step.get("prompt", "")
                    agent_instance = self.agent_manager.get_agent(agent_name) if self.agent_manager else None  
                    if agent_instance is None or not hasattr(agent_instance, "execute_task"):
                        raise ToolNotFoundError(f"Agent '{agent_name}' not found.")

                    context_param = {}
                    if last_result is not None:
                        context_param = {"last_result": last_result}

                    self.logger.info(
                        f"Executing legacy agent step {step_num}/{len(steps)} with agent '{agent_name}'."
                    )
                    result = agent_instance.execute_task(prompt=prompt_str, context=context_param)  
                    last_result = result  
                    i += 1
                    continue  

                tool_name = step.get("tool_name") or step.get("tool")
                if not tool_name:
                    raise PlanExecutionError(
                        f"No tool specified for step {step_num}",
                        step=step,
                        original_exception=ValueError(f"Missing tool in step {step_num}")
                    )

                self.logger.info(f"Executing step {step_num}/{len(steps)}: {step.get('description', 'No description')}")
                if self.status_callback:
                    self.status_callback({"type": "step_start", "data": {"index": i, "description": step.get("description"), "step": step}})

                resolved_args = self._resolve_dependencies(step.get("arguments", {}), self.execution_context)

                if not self.agent_manager:
                    raise PlanExecutionError(
                        "Agent manager is not available.",
                        step=step,
                        original_exception=Exception("Agent manager is None")
                    )

                result = self.agent_manager.execute_tool(tool_name, resolved_args)  # type: ignore[attr-defined]
                metrics_manager.record_tool_usage(tool_name, success=True)

                self.execution_context[f"step_{step_num}"] = {"output": result, "status": "success"}
                self.logger.info(f"Step {step_num} executed successfully. Result: {str(result)[:100]}...")
                if self.status_callback:
                    self.status_callback({
                        "type": "step_end",
                        "data": {
                            "index": i,
                            "status": "success",
                            "result": str(result)[:200],
                            "step": {"tool_name": tool_name, "arguments": resolved_args},
                        },
                    })

            except ToolNotFoundError as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.warning(f"Tool '{tool_name}' not found. Attempting to create it.")
                tool_description = step.get("description") or step.get("tool_description")

                if not tool_description:
                    raise PlanExecutionError(
                        f"Tool '{tool_name}' not found and no description provided to create it.",
                        step=step,
                        original_exception=e
                    )

                if self.status_callback is not None:
                    self.status_callback({"type": "info", "content": f"Tool '{tool_name}' not found. Attempting to create it..."})
                
                try:
                    if not self.agent_manager:
                        raise PlanExecutionError(
                            "Agent manager is not available to create a tool.",
                            step=step,
                            original_exception=Exception("Agent manager is None")
                        )

                    creation_result = self.agent_manager.execute_tool("create_tool", {"tool_description": tool_description})
                    
                    if creation_result.get("status") == "success":
                        new_tool_name = creation_result.get("tool_name", tool_name)
                        self.logger.info(f"Successfully created tool: {new_tool_name}")
                        if self.status_callback is not None:
                            self.status_callback({"type": "info", "content": f"Tool '{new_tool_name}' created. Retrying step..."})
                        
                        if hasattr(self.agent_manager, 'load_tools'):
                            self.agent_manager.load_tools()  
                        self.logger.info(f"Retrying step {step_num} with newly created tool '{new_tool_name}'.")
                        continue  

                except Exception as create_error:
                    self.logger.error(f"An error occurred while trying to create tool '{tool_name}': {create_error}", exc_info=True)
                    raise PlanExecutionError(
                        f"Tool creation failed: {create_error}",
                        step=step,
                        original_exception=create_error
                    )

            except (InvalidToolArgumentsError, ValueError) as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.warning(f"Tool execution failed for step {step_num}: {e}")
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({"type": "step_end", "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}})
                raise PlanExecutionError(
                    str(e),
                    step=step,
                    original_exception=e
                )

            except Exception as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.error(f"An unexpected error occurred during step {step_num}: {e}", exc_info=True)
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({"type": "step_end", "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}})
                raise PlanExecutionError(
                    str(e),
                    step=step,
                    original_exception=e
                )
            
            i += 1  

        self.logger.info("Plan execution completed successfully.")
        duration = time.time() - start_time
        metrics_manager.record_plan_execution_latency(duration)
        return {"status": "complete"}

    def _execute_step(self, step: Dict[str, Any], goal: str, master_prompt: str, options: Dict[str, Any]) -> None:
        """Executes a single step of the plan with latency measurement."""
        start_time = time.time()
        # Placeholder for step execution
        duration = time.time() - start_time
        self.logger.info(f"Step execution latency: {duration*1000:.2f}ms")
        if duration > 0.1:  # Log warning if latency exceeds 100ms
            self.logger.warning(f"High latency detected in step execution: {duration*1000:.2f}ms")

    def _generate_strategic_plan(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a strategic plan for the given goal with latency measurement."""
        start_time = time.time()
        # Placeholder for strategic plan generation
        result = {}
        duration = time.time() - start_time
        self.logger.info(f"Strategic plan generation latency: {duration*1000:.2f}ms")
        if duration > 0.1:  # Log warning if latency exceeds 100ms
            self.logger.warning(f"High latency detected in strategic plan generation: {duration*1000:.2f}ms")
        return result

    def _update_status(self, status: str) -> None:
        """Updates the status of the execution loop."""
        if self.status_callback is not None:
            self.status_callback({"type": "status", "content": status})

    def get_all_agent_names(self) -> List[str]:
        """Returns a list of all available agent names."""
        if self.agent_manager is not None:
            if hasattr(self.agent_manager, "get_all_agent_names"):
                return self.agent_manager.get_all_agent_names()  # type: ignore[attr-defined]
            elif hasattr(self.agent_manager, "get_all_agents"):
                return list(self.agent_manager.get_all_agents().keys())
        return []

    def _handle_invalid_tool_arguments_error(self, error: Exception, plan: Dict[str, Any], step: Dict[str, Any]) -> None:
        """Handles errors due to invalid tool arguments by generating a new plan with error context."""
        error_context = f"Invalid arguments for tool '{step.get('tool_name', 'unknown')}' in step {step.get('id', 'unknown')}: {str(error)}"
        self.logger.error(f"Invalid tool arguments: {error_context}", exc_info=True)
        if self.status_callback:
            self.status_callback({"type": "error", "content": error_context})
        try:
            raise InvalidToolArgumentsError(error_context)  # type: ignore[attr-defined]
        except Exception as e:
            raise PlanExecutionError(f"Invalid tool arguments: {error_context}", original_exception=e) from e  # type: ignore[call-arg]

    def _handle_tool_not_found_error(self, error: Exception, plan: Dict[str, Any], step: Dict[str, Any]) -> None:
        """Handles errors when a tool is not found by generating a new plan with error context."""
        error_context = f"Tool {step.get('tool_name', 'unknown')} not found"
        self.logger.error(f"Tool not found: {error_context}", exc_info=True)
        if self.status_callback:
            self.status_callback({"type": "error", "content": error_context})
        try:
            raise ToolNotFoundError(error_context)  # type: ignore[attr-defined]
        except Exception as e:
            raise PlanExecutionError(f"Tool not found: {error_context}", original_exception=e) from e  # type: ignore[call-arg]

    def _handle_generic_execution_error(self, e: Exception, step: Dict[str, Any]) -> None:
        """Handles a generic execution error by generating a new plan with error context."""
        error_context = f"Error executing step {step.get('id', 'unknown')}: {str(e)}"
        self.logger.error(f"Execution error: {error_context}", exc_info=True)
        if self.status_callback:
            self.status_callback({"type": "error", "content": error_context})
        raise PlanExecutionError(f"Execution error: {error_context}", step, original_exception=e) from e  

    def _generate_plan_with_error_context(self, goal: str, error_context: str) -> Dict[str, Any]:
        """Generates a new plan with error context to recover from a failure."""
        self.logger.info(f"Generating new plan for goal '{goal}' with error context: {error_context}")
        return self._generate_plan(goal, error_context)

    def _check_goal_ambiguity(self, goal: str) -> Tuple[bool, str]:
        """Checks if a goal is ambiguous and returns a clarification question."""
        # Placeholder for goal ambiguity check
        return False, ""

    def _generate_and_execute_plan(self, goal: str, user_feedback: str = "") -> Dict[str, Any]:
        """Generates and executes a plan for a given goal with optional user feedback."""
        # Placeholder for plan generation and execution
        return {}

    def _extract_sub_goals_manually(self, goal: str) -> List[str]:
        """Manually extracts sub-goals from a given goal."""
        # Placeholder for manual sub-goal extraction
        return []

    def _update_available_tools(self) -> None:
        """Updates the list of available tools in the UI or other integrations via callback."""
        try:
            if self.agent_manager is not None:
                # Some versions of AgentManager might have get_all_agent_names(), others get_all_agents()
                agent_names = []
                if hasattr(self.agent_manager, "get_all_agent_names"):
                    agent_names = self.agent_manager.get_all_agent_names()
                elif hasattr(self.agent_manager, "get_all_agents"):
                    agent_names = list(self.agent_manager.get_all_agents().keys())
                tool_list = []
                if hasattr(self.agent_manager, "get_tool_schemas"):
                    tool_list = self.agent_manager.get_tool_schemas()
                if self.tool_update_callback is not None:
                    self.tool_update_callback(tool_list)
                self.logger.info(f"Updated available tools: {len(agent_names)} agents and {len(tool_list)} tools available")
        except Exception as e:
            self.logger.error(f"Error updating tools: {str(e)}")

    def _execute_tool(self, tool_name: str, tool_arguments: Dict[str, Any]) -> Any:
        """Executes a tool with the given name and arguments."""
        if self.agent_manager is None:
            raise ValueError("No AgentManager available to execute tools")
        try:
            result = self.agent_manager.execute_tool(tool_name, tool_arguments)  # type: ignore[attr-defined]
            self.logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

    def _register_default_agents(self) -> None:
        """Registers the default set of specialized agents."""
        if self.agent_manager is not None:
            browser_agent = BrowserAgent()
            screen_agent = ScreenAgent()
            text_agent = TextAgent(self.llm_manager)
            system_agent = SystemInteractionAgent()

            self.agent_manager.add_agent("BrowserAgent", browser_agent)
            self.agent_manager.add_agent("ScreenAgent", screen_agent)
            self.agent_manager.add_agent("TextAgent", text_agent)
            self.agent_manager.add_agent("SystemInteractionAgent", system_agent)

            self.agent_manager.add_agent("Browser Agent", browser_agent)
            self.agent_manager.add_agent("Screen Agent", screen_agent)
            self.agent_manager.add_agent("Text Agent", text_agent)
            self.agent_manager.add_agent("System Interaction Agent", system_agent)

            self.logger.info("Registered default specialized agents (with legacy aliases).")

    def decompose_goal(self, goal: str) -> List[str]:
        sub_goals = []
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant tasked with decomposing complex goals into smaller, manageable sub-goals."},
            {"role": "user", "content": f"Decompose the following goal into smaller sub-goals: {goal}"},
        ]
        llm_result = self.llm_manager.chat(messages)  
        if llm_result and llm_result.response_text:
            try:
                response_json = json.loads(llm_result.response_text)  
                if "sub_goals" in response_json and isinstance(response_json["sub_goals"], list):
                    sub_goals.extend(response_json["sub_goals"])
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse decompose_goal response as JSON, attempting manual extraction")
                sub_goals.extend(self._extract_sub_goals_manually(llm_result.response_text))  
        if not sub_goals:
            sub_goals.append(goal)
        return sub_goals

    def _add_memory_for_agents(self, title: str, content: str, memory_type: Any, scope: Any) -> None:
        """Adds a memory record for each agent managed by AgentManager, using safe fallbacks for older APIs."""
        if self.agent_manager is None:
            return
        for agent_name in self.agent_manager.get_all_agent_names():  
            if hasattr(self.agent_manager, "add_memory_for_agent"):
                try:
                    self.agent_manager.add_memory_for_agent(
                        agent_name,
                        title,
                        content,
                        memory_type if memory_type is not None else MemoryType,  
                        scope if scope is not None else MemoryScope,  
                    )
                except TypeError:
                    self.agent_manager.add_memory_for_agent(agent_name, title, content)  
            else:
                self.logger.warning("AgentManager does not expose add_memory_for_agent()")

    def _resolve_dependencies(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves template variables in arguments from the execution context."""
        resolved_args = {}
        for key, value in args.items():
            if isinstance(value, str):
                def replacer(match):
                    step_num = int(match.group(1))
                    ref_step = f"step_{step_num}"
                    if ref_step in context and "output" in context[ref_step]:
                        self.logger.info(f"Resolving dependency for '{key}': using output from step {step_num}")
                        return str(context[ref_step]["output"])
                    self.logger.warning(f"Could not resolve dependency: {match.group(0)}. Context is missing the value.")
                    return match.group(0)

                resolved_value = re.sub(r"\{\{step_(\d+)\.output\}\}", replacer, value)
                resolved_args[key] = resolved_value
            else:
                resolved_args[key] = value
        return resolved_args

    def achieve_goal(self, goal: str) -> Any:
        if self.status_callback is not None:
            self.status_callback({"type": "info", "content": f"Starting to achieve goal: {goal}"})  

        if self.llm_manager is None:
            self.logger.error("LLMManager is not initialized. Cannot proceed with goal.")
            raise ValueError("LLMManager is not initialized.")

        sub_goals = self.decompose_goal(goal)
        if len(sub_goals) == 0:  
            self.logger.error("No sub-goals were generated from goal decomposition.")
            raise ValueError("Failed to decompose goal into sub-goals.")

        if self.status_callback is not None:
            self.status_callback({
                "type": "info",
                "content": f"Decomposed goal into {len(sub_goals)} sub-goals.",
            })  

        for i, sub_goal in enumerate(sub_goals):  
            self.logger.info(f"Processing sub-goal {i+1}/{len(sub_goals)}: {sub_goal}")  
            if self.status_callback is not None:
                self.status_callback({
                    "type": "info",
                    "content": f"Processing sub-goal {i+1}/{len(sub_goals)}: {sub_goal}",
                })  
            self._execute_objective_with_retries(sub_goal)

        if self.status_callback is not None:
            self.status_callback({"type": "success", "content": f"Achieved goal: {goal}"})  
        self.logger.info(f"Successfully achieved goal: {goal}")
        return None

    def _initialize_state(self) -> None:
        """Initializes the internal state of the agent."""
        # Placeholder for state initialization
        pass
