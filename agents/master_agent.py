"""Master agent for orchestrating tasks."""

import json
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

from agents.browser_agent import BrowserAgent

try:
    from agents.enhanced_memory_manager import (
        EnhancedMemoryManager as MemoryManager,  # type: ignore
    )
    from agents.memory_manager import (  # type: ignore[attr-defined]
        MemoryScope,
        MemoryType,
    )
except (ImportError, AttributeError):
    try:
        from agents.memory_manager import (  # type: ignore[attr-defined]
            MemoryManager,
            MemoryScope,
            MemoryType,
        )
    except (ImportError, AttributeError):
        from agents.memory_manager import MemoryManager  # type: ignore
        MemoryType = object  # type: ignore
        MemoryScope = object  # type: ignore

from agents.agent_manager import (
    AgentManager,
    InvalidToolArgumentsError,
    ToolNotFoundError,
)
from agents.creator_authentication import CreatorAuthentication
from intelligence.context_awareness_engine import ContextAwarenessEngine

try:
    from agents.models import Plan, TokenUsage  # type: ignore
except ImportError:
    # Define a fallback if needed
    class _FallbackTokenUsage:
        def __init__(self, prompt_tokens=0, completion_tokens=0, total_tokens=0):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens
    TokenUsage = _FallbackTokenUsage  # type: ignore

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
        agent_manager: Optional["AgentManager"] = None,
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
        from utils.config_manager import config_manager as _cfg
        if memory_manager is None:
            try:
                memory_manager = MemoryManager(llm_manager=llm_manager, config_manager=_cfg)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover
                memory_manager = None  # fallback – some tests patch interactions anyway
        if context_awareness_engine is None:
            try:
                context_awareness_engine = ContextAwarenessEngine()
            except Exception:
                context_awareness_engine = None
        if agent_manager is None and memory_manager is not None:
            agent_manager = AgentManager(llm_manager=llm_manager, memory_manager=memory_manager)

        self.agent_manager = agent_manager  # type: ignore[assignment]
        # Backwards-compat: expose agent_manager through `.agents` as expected by tests
        self.agents = self.agent_manager
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.context_awareness_engine = context_awareness_engine
        self.status_callback = status_callback
        self.creator_auth = creator_auth  # Додано систему аутентифікації creator
        self.stop_event = threading.Event()
        self.last_executed_plan: Optional[Dict[str, Any]] = None
        self.system_prompt_template: Optional[str] = None
        self._tools_changed = True  # Force prompt regeneration on first run
        self.last_goal: Optional[str] = None
        self.last_plan: Optional[Plan] = None
        self.execution_context: Dict[str, Any] = {}
        # In-memory cache for generated plans to reduce redundant LLM calls
        self._plan_cache: Dict[str, Dict[str, Any]] = {}

        # Hierarchical Planners
        self.strategic_planner = StrategicPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager)
        self.tactical_planner = TacticalPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager)
        self.operational_planner = OperationalPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager, agent_manager=self.agent_manager)
        self.problem_decomposition_agent = ProblemDecompositionAgent(llm_manager=self.llm_manager)
        self.retry_count = 0

        # State for goal clarification
        self.is_clarifying = False
        self.clarification_question: Optional[str] = None

        # Set the callback on the agent manager to receive tool updates
        if self.agent_manager is not None:
            self.agent_manager.master_agent_update_callback = self._on_tools_updated

        if not self.agent_manager.has_agents:  # Check for registered agents
            self._register_default_agents()
        self.logger.info("MasterAgent initialized with creator authentication")

    def run(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> None:
        """Starts the agent's execution loop in a new thread."""

        # Verification на чутливі операції для аутентифікованого creator
        if self.creator_auth and self.creator_auth.is_creator_session_active:
            # Створець аутентифікований - беззаперечне виконання
            if self.creator_auth.should_execute_unconditionally():
                self.logger.info("Executing goal unconditionally for authenticated creator")
                if self.status_callback:
                    emotional_response = self.creator_auth.get_creator_emotional_response("obedience")
                    self.status_callback({"type": "info", "content": emotional_response})

        with self.state_lock:
            if self.is_running:
                self.logger.warning("Agent is already running.")
                return
            self.goals = [goal] if isinstance(goal, str) else goal
            if not self.goals:
                self.logger.warning("No goals provided to run.")
                return
            self.prompt = master_prompt
            self.options = options
            self.is_running = True
            self.is_paused = False
        self.thread = threading.Thread(target=self._execution_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info(f"MasterAgent started with goals: {self.goals}")

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

        # Use a fallback method if add_memory_for_agent with specific types isn't available
        try:
            if self.memory_manager is not None:
                if hasattr(self.memory_manager, "add_memory_for_agent"):
                    self.memory_manager.add_memory_for_agent(
                        agent_type=MemoryScope.USER_DATA if hasattr(MemoryScope, "USER_DATA") else "user_data",  # type: ignore
                        memory_type=MemoryType.FEEDBACK if hasattr(MemoryType, "FEEDBACK") else "feedback",  # type: ignore
                        content=memory_content,
                        metadata={"goal": goal, "feedback": feedback_str, "plan_id": plan_to_record.get("id", "N/A")},
                    )
                else:
                    self.logger.warning("add_memory_for_agent method not available in MemoryManager")
            else:
                self.logger.warning("MemoryManager is not initialized. Skipping memory addition.")
        except Exception as e:
            self.logger.error(f"Failed to add memory for agent: {e}")

        if hasattr(self.memory_manager, "add_memory"):
            try:
                self.memory_manager.add_memory(
                    content=memory_content,
                    metadata={"goal": goal, "feedback": feedback_str, "plan_id": plan_to_record.get("id", "N/A")},
                )  # type: ignore
            except TypeError:
                # Handle case where collection_name is not needed
                self.memory_manager.add_memory(
                    collection_name="default",
                    content=memory_content,
                    metadata={"goal": goal, "feedback": feedback_str, "plan_id": plan_to_record.get("id", "N/A")},
                )
        else:
            self.logger.warning("Memory manager does not support adding memories.")
        self.logger.info(f"Stored {feedback_str} feedback for goal: '{goal}'")

    def _check_goal_ambiguity(self, goal: str) -> Tuple[bool, Optional[str]]:
        """Placeholder for goal ambiguity check."""
        # For now, assume no goal is ambiguous to allow profiling to proceed.
        return False, None

    def run_once(self, goal: str) -> None:
        """Runs the full hierarchical planning and execution loop for a given goal."""
        if self.is_paused or not self.is_running:
            return

        if self.status_callback is not None:
            self.status_callback({"type": "info", "content": f"Starting new goal: {goal}"})
        self.last_goal = goal
        original_goal = goal

        # Check for goal ambiguity before proceeding
        is_ambiguous, question = self._check_goal_ambiguity(goal)
        if is_ambiguous:
            self.is_clarifying = True
            self.clarification_question = question
            self.is_paused = True
            if self.status_callback is not None:
                self.status_callback({"type": "request_clarification", "content": question})
            self.logger.info(f"Goal '{goal}' is ambiguous. Asking for clarification: {question}")
            return

        # Complexity Gate: Use ToT for complex goals.
        is_complex_goal = len(goal.split()) > 20
        if is_complex_goal:
            self.logger.info("Complex goal detected. Engaging Tree-of-Thought for decomposition.")
            sub_goals = self.problem_decomposition_agent.decompose_goal(goal)
            sub_goals = cast("List[str]", sub_goals)  # Ensure not Optional
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

    def _execute_objective_with_retries(self, current_goal: str):
        """Generates and executes a plan for an objective, with error handling and retries."""
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                plan = self._generate_plan(current_goal)
                if not plan or not plan.get("steps"):
                    self.logger.warning(f"Could not generate a plan for the objective: {current_goal}")
                    return

                self._execute_plan(plan)
                self.logger.info(f"Successfully executed plan for objective: {current_goal}")
                return  # Success, exit loop

            except PlanExecutionError as e:
                self.logger.warning(f"Plan execution failed (Attempt {attempt + 1}/{self.MAX_RETRIES + 1}). Error: {e.original_exception}")

                if attempt >= self.MAX_RETRIES:
                    self.logger.error(f"Failed to execute objective '{current_goal}' after {self.MAX_RETRIES + 1} attempts.")
                    raise e

                error = e.original_exception
                step = e.step

                if isinstance(error, ToolNotFoundError):
                    self._handle_tool_not_found(error, step)
                elif isinstance(error, InvalidToolArgumentsError):
                    current_goal = self._handle_invalid_tool_arguments(current_goal, step, error)
                else:
                    self._handle_generic_execution_error(step, attempt + 1)

            except Exception as e:
                self.logger.error(f"An unexpected error occurred while processing objective '{current_goal}': {e}", exc_info=True)
                raise e

    def _handle_tool_not_found(self, error: ToolNotFoundError, step: Dict[str, Any]):
        """Handles a ToolNotFoundError by attempting to create the missing tool."""
        self.logger.info(f"Attempting to recover from ToolNotFoundError for tool '{error.tool_name}'.")
        tool_description = f"a tool that can be used to {step.get('description', 'perform a task')}"
        creation_result = self.agent_manager.tool_creator_agent.create_tool(tool_description)
        if creation_result.get("status") != "success":
            self.logger.error("Failed to create the missing tool. Aborting objective.")
            raise error # Re-raise if tool creation fails

    def _handle_invalid_tool_arguments(self, goal: str, step: Dict[str, Any], error: InvalidToolArgumentsError) -> str:
        """Handles an InvalidToolArgumentsError by regenerating the plan with error context."""
        self.logger.info("Attempting to recover from InvalidToolArgumentsError by replanning.")
        return self._generate_plan_with_error_context(goal, step, error)

    def _handle_generic_execution_error(self, step: Dict[str, Any], attempt: int):
        """Handles a generic error by logging and waiting before a retry."""
        self.logger.info(f"Retrying step {step.get('step_id')} due to a transient error.")
        if self.status_callback:
            self.status_callback({"type": "info", "content": f"Retrying step {step.get('step_id')} (Attempt {attempt + 1}/{self.MAX_RETRIES + 1})..."})
        time.sleep(0.1) # Short delay before retrying

    def _generate_plan_with_error_context(self, original_goal: str, failed_step: Dict[str, Any], error: Exception) -> str:
        """Creates a new goal to regenerate the plan, incorporating the error context."""
        self.logger.info("Generating new plan with error context.")
        error_context = f"The previous attempt failed at step {failed_step.get('step_id')}: '{failed_step.get('description')}'. The error was: {error}. Please generate a new plan to achieve the original goal: '{original_goal}'"
        return error_context

    def stop(self) -> None:
        """Stops the agent's execution loop."""
        with self.state_lock:
            if not self.is_running:
                self.logger.warning("Cannot stop, agent is not running.")
                return
            self.is_running = False
            self.is_paused = False
        if self.thread:
            self.thread.join()  # Wait for the thread to finish
        self.logger.info("MasterAgent stopped.")

    def continue_with_feedback(self, instruction: str) -> None:
        """Continues a paused execution based on user feedback."""
        with self.state_lock:
            if not self.is_paused:
                self.logger.warning("Agent is not paused, cannot process feedback.")
                return

            original_goal = self.goals[-1]
            clarified_goal = f"{original_goal} (User clarification: {instruction})"
            self.goals[-1] = clarified_goal  # Update the current goal

            self.is_clarifying = False
            self.clarification_question = None
            self.is_paused = False  # Resume execution
            self.logger.info(f"Clarification received. New goal: {clarified_goal}")
            if self.status_callback is not None:
                self.status_callback({"type": "info", "content": "Clarification received. Resuming..."})

    def provide_clarification(self, clarification: str) -> None:
        """Receives clarification from the user and resumes execution."""
        with self.state_lock:
            if not self.is_clarifying:
                self.logger.warning("Not in a clarification state.")
                return

            original_goal = self.goals[-1]
            clarified_goal = f"{original_goal} (User clarification: {clarification})"
            self.goals[-1] = clarified_goal  # Update the current goal

            self.is_clarifying = False
            self.clarification_question = None
            self.is_paused = False  # Resume execution
            self.logger.info(f"Clarification received. New goal: {clarified_goal}")
            if self.status_callback is not None:
                self.status_callback({"type": "info", "content": "Clarification received. Resuming..."})

            # Resume processing with the clarified goal
            if self.is_running:
                self.run_once(clarified_goal)

    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extracts a JSON object or array from a string, even if it's in a markdown block."""
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        start_brace = text.find("{")
        start_bracket = text.find("[")

        if start_brace == -1 and start_bracket == -1:
            return None

        if start_brace == -1:
            start = start_bracket
        elif start_bracket == -1:
            start = start_brace
        else:
            start = min(start_brace, start_bracket)

        end_brace = text.rfind("}")
        end_bracket = text.rfind("]")
        end = max(end_brace, end_bracket)

        if start != -1 and end != -1 and end > start:
            return text[start:end+1]

        return None

    def _recover_from_error(self, original_goal: str, plan: Dict[str, Any], failed_step: Dict[str, Any], error: Exception, context: Dict[str, Any]) -> str:
        """
        Analyzes an error and generates a specialized recovery goal.
        """
        self.logger.info(f"Initiating recovery from error: {type(error).__name__}")
        context_summary = json.dumps(context, indent=2)

        if isinstance(error, ToolNotFoundError):
            # The tool doesn't exist. The recovery goal should be to create it.
            return (
                f"The plan failed because the tool '{failed_step.get('tool')}' does not exist. "
                f"The original sub-goal was: '{original_goal}'.\n"
                f"The error was: '{error}'.\n\n"
                f"Your new goal is to first create the missing tool using the 'create_tool' agent. "
                f"The tool should be able to accomplish this step: '{failed_step.get('description')}'. "
                f"After the tool is created, retry the original sub-goal. "
                f"The overall objective is still: {self.last_goal}"
            )

        if isinstance(error, InvalidToolArgumentsError):
            # The arguments were wrong. The recovery goal should be to fix them.
            return (
                f"The plan failed at step '{failed_step.get('description')}' due to invalid arguments for the tool '{failed_step.get('tool')}'.\n"
                f"The original sub-goal was: '{original_goal}'.\n"
                f"The error was: '{error}'.\n\n"
                f"Here is the execution context from the failed plan, showing the outputs of successful steps:\n{context_summary}\n\n"
                f"Please create a new, corrected plan to achieve the original sub-goal. Analyze the context and error to avoid repeating the mistake. "
                f"The overall objective is still: {self.last_goal}"
            )

        # For all other errors, use the generic recovery approach.
        self.logger.warning(f"Using generic recovery for an unrecognized error type: {type(error).__name__}")
        return self._create_recovery_goal(original_goal, plan, failed_step, error, context)

    def _create_recovery_goal(self, original_goal: str, plan: Dict[str, Any], failed_step: Dict[str, Any], error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Analyzes an error and generates a specialized recovery goal using an LLM.
        This forms the core of the agent's self-correction and learning loop.
        """
        self.logger.info("Engaging meta-cognitive loop to create a recovery goal...")

        # Serialize the context for the prompt, ensuring all data is convertible to string
        plan_summary = json.dumps(plan, indent=2, default=str)
        context_summary = json.dumps(context, indent=2, default=str)

        recovery_prompt = """You are a meta-cognitive reasoning engine integrated into an autonomous agent. Your purpose is to analyze execution failures and devise a robust recovery strategy.

        Analyze the provided context, which includes the original goal, the plan, the failed step, the error, and the execution history. Your analysis should identify the most likely root cause of the failure (e.g., flawed assumption, incorrect tool usage, environmental change, invalid arguments).

        Based on your analysis, generate a new, single, high-level goal to overcome the problem. The new goal must be:
        1.  **Actionable:** It should be a clear instruction that the agent can execute.
        2.  **Self-Contained:** It should not depend on prior, failed assumptions.
        3.  **Strategic:** It should aim to fix the root cause, not just the symptom.

        Return ONLY the new goal as a single line of text.
        """

        user_prompt = f"""
        **Execution Failure Report**

        **1. Original Goal:**
        {original_goal}

        **2. Failed Plan:**
        ```json
        {plan_summary}
        ```

        **3. Failed Step:**
        {failed_step.get('description', 'No description')}

        **4. Error Message:**
        {error}

        **5. Execution Context (Previous Steps):**
        ```json
        {context_summary}
        ```

        **Task:** Analyze this failure and provide a new, strategic recovery goal.
        """

        messages = [
            {"role": "system", "content": recovery_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            self.logger.info("Querying LLM for a recovery goal...")
            if self.llm_manager is not None:
                response = self.llm_manager.chat(messages=messages)

                if not response:
                    raise ValueError("LLM returned an empty response.")

                if hasattr(response, "response_text"):
                    recovery_goal = response.response_text.strip()  # type: ignore
                else:
                    recovery_goal = str(response).strip()
                self.logger.info(f"Generated recovery goal: '{recovery_goal}'")
                return recovery_goal
        except Exception as e:
            self.logger.error(f"Failed to generate recovery goal from LLM: {e}", exc_info=True)
            # Fallback to a simpler, default recovery goal
            return f"Attempt to recover from the failure in achieving the goal: '{original_goal}' after the error: '{error}'"

    def _execute_objective_with_retries(self, objective: str) -> None:
        current_goal = objective
        self.retry_count = 0
        while self.retry_count < self.MAX_RETRIES:
            # Capture current environmental snapshot (if available)
            baseline_context: Dict[str, Any] = {}
            if self.context_awareness_engine is not None and hasattr(self.context_awareness_engine, "get_current_context"):
                try:
                    baseline_context = self.context_awareness_engine.get_current_context() or {}
                except Exception:  # pragma: no cover – engine implementation may vary
                    baseline_context = {}

            try:
                if self.status_callback is not None:
                    self.status_callback({"type": "info", "content": f"Executing objective: {current_goal}"})  # type: ignore
                plan = self._generate_plan(current_goal)
                if not plan or not plan.get("steps"):
                    self.logger.error(f"Invalid plan generated for goal: {current_goal}")
                    raise ValueError(f"Invalid plan for goal: {current_goal}")
                self._execute_plan(plan)
                if self.status_callback is not None:
                    self.status_callback({"type": "success", "content": f"Completed objective: {current_goal}"})  # type: ignore
                break
            except PlanExecutionError as e:
                self.logger.error(f"Plan execution failed: {e!s}")
                self.retry_count += 1
                if self.retry_count < self.MAX_RETRIES:
                    # Check for environmental changes since we started this attempt
                    env_changed = False
                    if self.context_awareness_engine is not None and hasattr(self.context_awareness_engine, "get_current_context"):
                        try:
                            latest_context = self.context_awareness_engine.get_current_context() or {}
                            env_changed = latest_context != baseline_context
                        except Exception:  # pragma: no cover
                            env_changed = False

                    if env_changed:
                        if self.status_callback is not None:
                            self.status_callback({"type": "info", "content": "Environment changed – regenerating plan."})  # type: ignore
                        # On environmental change, simply restart loop with the same original goal (fresh plan)
                        continue

                    recovery_goal = self._recover_from_error(
                        original_goal=current_goal,
                        plan=e.step,
                        failed_step=e.step,
                        error=e.original_exception,
                        context=getattr(e, "context", {}),  # Safely access context attribute with fallback
                    )
                    if recovery_goal:
                        if self.status_callback is not None:
                            self.status_callback({"type": "warning", "content": f"Retrying with recovery goal: {recovery_goal}"})  # type: ignore
                        current_goal = recovery_goal
                    else:
                        if self.status_callback is not None:
                            self.status_callback({"type": "error", "content": f"Failed to generate recovery goal after {self.retry_count} retries."})  # type: ignore
                        self.logger.error(f"Failed to generate recovery goal after {self.retry_count} retries.")
                        raise
                else:
                    if self.status_callback is not None:
                        self.status_callback({"type": "error", "content": f"Failed to achieve objective after {self.retry_count} retries."})  # type: ignore
                    self.logger.error(f"Failed to achieve objective after {self.retry_count} retries.")
                    raise
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while processing objective '{objective}': {e}", exc_info=True)
                raise e  # Re-raise as a critical failure

    def _execute_plan(self, plan: Dict[str, Any]) -> None:
        start_time = time.perf_counter()
        """
        Executes the steps outlined in the plan.
        Raises:
            PlanExecutionError: If any step fails due to a tool error or other exception.
        """
        if plan is None:
            self.logger.error("Plan is None, cannot execute.")
            raise ValueError("Plan is None")
        steps = plan.get("steps", [])
        if not steps:
            self.logger.warning("Plan has no steps to execute.")
            return

        self.logger.info("Starting plan execution.")
        self.execution_context = {}  # Reset context for new plan

        i = 0
        while i < len(steps):
            step = steps[i]
            if step is None:
                self.logger.warning(f"Step {i+1} is None, skipping.")
                i += 1
                continue

            if not self.is_running:
                self.logger.info("Execution stopped mid-plan.")
                return

            while self.is_paused:
                time.sleep(0.1)

            step_num = i + 1
            tool_name = "unknown"
            resolved_args = {}
            try:
                tool_name = step.get("tool_name") or step.get("tool")
                if not tool_name:
                    raise ValueError("Step is missing 'tool_name' or 'tool'.")

                self.logger.info(f"Executing step {step_num}/{len(steps)}: {step.get('description', 'No description')}")
                if self.status_callback:
                    self.status_callback({"type": "step_start", "data": {"index": i, "description": step.get("description"), "step": step}})

                resolved_args = self._resolve_dependencies(step.get("arguments", {}), self.execution_context)

                if not self.agent_manager:
                    raise PlanExecutionError("Agent manager is not available.", step=step)

                result = self.agent_manager.execute_tool(tool_name, resolved_args)
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
                    raise PlanExecutionError(f"Tool '{tool_name}' not found and no description provided to create it.", step=step, original_exception=e)

                if self.status_callback:
                    self.status_callback({"type": "info", "content": f"Tool '{tool_name}' not found. Attempting to create it..."})
                
                try:
                    if not self.agent_manager:
                        raise PlanExecutionError("Agent manager is not available to create a tool.", step=step)

                    creation_result = self.agent_manager.execute_tool("create_tool", {"tool_description": tool_description})
                    
                    if creation_result.get("status") == "success":
                        new_tool_name = creation_result.get("tool_name", tool_name)
                        self.logger.info(f"Successfully created tool: {new_tool_name}")
                        if self.status_callback:
                            self.status_callback({"type": "info", "content": f"Tool '{new_tool_name}' created. Retrying step..."})
                        
                        self.agent_manager.load_tools()
                        self.logger.info(f"Retrying step {step_num} with newly created tool '{new_tool_name}'.")
                        continue  # Retry the current step without incrementing i
                    else:
                        error_msg = creation_result.get("error", "Unknown error during tool creation")
                        raise PlanExecutionError(f"Failed to create tool '{tool_name}': {error_msg}", step=step)

                except Exception as create_error:
                    self.logger.error(f"An error occurred while trying to create tool '{tool_name}': {create_error}", exc_info=True)
                    raise PlanExecutionError(f"Tool creation failed: {create_error}", step=step, original_exception=create_error)

            except (InvalidToolArgumentsError, ValueError) as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.warning(f"Tool execution failed for step {step_num}: {e}")
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({"type": "step_end", "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}})
                raise PlanExecutionError(str(e), step=step, original_exception=e)

            except Exception as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.error(f"An unexpected error occurred during step {step_num}: {e}", exc_info=True)
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({"type": "step_end", "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}})
                raise PlanExecutionError(str(e), step=step, original_exception=e)
            
            i += 1  # Increment to move to the next step

        self.logger.info("Plan execution completed successfully.")
        duration = time.perf_counter() - start_time
        metrics_manager.record_plan_execution_latency(duration)

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any], step: Dict[str, Any]) -> Any:
        try:
            if tool_name not in self.agent_manager.available_tools:  # type: ignore
                raise ToolNotFoundError(f"Tool '{tool_name}' not found in available tools.")

            resolved_args = self._resolve_dependencies(tool_args, self.execution_context)

            if self.status_callback is not None:
                self.status_callback({
                    "type": "info",
                    "content": f"Executing tool '{tool_name}' with arguments: {resolved_args}",
                })  # type: ignore

            tool_instance = self.agent_manager.available_tools[tool_name]  # type: ignore
            try:
                result = tool_instance(**resolved_args)
                if self.status_callback is not None:
                    self.status_callback({
                        "type": "success",
                        "content": f"Tool '{tool_name}' executed successfully.",
                    })  # type: ignore
                return result
            except TypeError as te:
                error_msg = f"Invalid arguments for tool '{tool_name}': {te!s}"
                self.logger.error(error_msg, exc_info=True)
                raise InvalidToolArgumentsError(error_msg)  # type: ignore
        except Exception as e:
            if isinstance(e, ToolNotFoundError):
                raise e
            if isinstance(e, InvalidToolArgumentsError):
                raise e
            error_msg = f"Unexpected error executing tool '{tool_name}': {e!s}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

    def _generate_plan(self, goal: str) -> Dict[str, Any]:
        """Generate an execution plan for a goal.

        This method now employs an in-memory cache to avoid redundant LLM calls
        for repeat goals and records latency metrics for performance analysis.
        """
        # Check cache first
        if goal in self._plan_cache:
            self.logger.info("Using cached plan for goal: '%s'", goal)
            return self._plan_cache[goal]

        start_time = time.perf_counter()
        if self.status_callback is not None:
            self.status_callback({"type": "info", "content": f"Generating plan for goal: {goal}"})  # type: ignore

        tool_schemas = self.agent_manager.get_tool_schemas() if self.agent_manager else []
        tools_json_string = json.dumps(tool_schemas, indent=2)

        prompt_template = """
        You are an expert AI orchestrator. Your sole purpose is to generate a JSON plan based on the user's request. You must only output a valid JSON object and nothing else. Do not add any explanatory text, markdown formatting, or any characters outside of the JSON structure.

        Generate a plan to achieve the following goal: {goal}

        You have access to the following tools. Use the schema to construct your plan, ensuring all arguments match the definition.

        **Available Tools Schema:**
        ```json
        {tools}
        ```

        **Instructions:**
        - Use the schema above to form your plan.
        - The `tool` in each step must be one of the tool names from the schema.
        - The `arguments` for each tool must be a dictionary where the keys are the argument names specified in the schema.
        - Provide values for all `required` arguments.
        - For the `create_tool` function, provide a natural language `tool_description` of what the new tool should do. Do not provide code or a tool name.
        """
        prompt_content = prompt_template.format(
            goal=goal,
            tools=tools_json_string
        )

        messages = [
            {"role": "system", "content": "You are an expert AI orchestrator. Your sole purpose is to generate a JSON plan based on the user's request. You must only output a valid JSON object and nothing else. Do not add any explanatory text, markdown formatting, or any characters outside of the JSON structure."},
            {"role": "user", "content": prompt_content}
        ]

        llm_result = self.llm_manager.chat(messages=messages)  # type: ignore
        if not llm_result or not llm_result.response_text:
            self.logger.error("LLM provided no response for plan generation.")
            raise ValueError("Failed to generate plan: No response from LLM")

        plan_text = llm_result.response_text.strip()
        self.logger.info(f"LLM raw response for plan generation: {plan_text}")

        try:
            # Use regex to find the JSON block
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan_text = json_match.group(0)
            else:
                self.logger.warning("Could not find a JSON block in the LLM response. Attempting to parse raw response.")

            self.logger.info(f"Extracted JSON from LLM response: {plan_text}")
            plan = json.loads(plan_text)

            # Extract steps from the plan, allowing for 'plan' or 'steps' key
            steps = plan.get("steps")
            if not steps and isinstance(plan.get("plan"), list):
                self.logger.warning("Plan received with 'plan' key instead of 'steps'. Adapting to new format.")
                steps = plan.get("plan")
                plan["steps"] = steps  # Normalize for downstream use
                if 'plan' in plan: del plan['plan']

            # Validate plan structure
            if not isinstance(steps, list) or len(steps) == 0:
                self.logger.error(f"Invalid plan structure received: {plan}")
                raise ValueError(f"Invalid plan format: 'steps' must be a non-empty list. Received: {plan}")

            self.logger.info(f"Successfully generated plan with {len(plan['steps'])} steps.")
            duration = time.perf_counter() - start_time
            metrics_manager.record_plan_generation_latency(duration)
            self._plan_cache[goal] = plan
            return plan
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse plan as JSON: {plan_text}")
            raise ValueError("Failed to parse plan as JSON")


    def _execution_loop(self) -> None:
        """The core loop where the agent processes its goals."""
        self.logger.info("Execution loop started.")
        is_cyclic = self.options.get("cyclic", False)

        while self.is_running:
            for current_goal in self.goals:
                if not self.is_running:
                    break
                self.logger.info(f"Processing goal: '{current_goal}'")
                self.run_once(current_goal)
                time.sleep(1)
            if not is_cyclic:
                break
        self.is_running = False
        self.logger.info("Execution loop finished.")

    def _on_tools_updated(self):
        """Callback function for when the agent_manager reloads tools."""
        self.logger.info("MasterAgent received notification of tool update. Prompt will be regenerated on next planning cycle.")
        self._tools_changed = True

    def _register_default_agents(self) -> None:
        """Registers the default set of specialized agents."""
        if self.agent_manager is not None:
            self.agent_manager.add_agent("BrowserAgent", BrowserAgent())
            self.agent_manager.add_agent("ScreenAgent", ScreenAgent())
            self.agent_manager.add_agent("TextAgent", TextAgent(self.llm_manager))
            self.agent_manager.add_agent("SystemInteractionAgent", SystemInteractionAgent())
            self.logger.info("Registered default specialized agents.")

    def decompose_goal(self, goal: str) -> List[str]:
        sub_goals = []
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant tasked with decomposing complex goals into smaller, manageable sub-goals."},
            {"role": "user", "content": f"Decompose the following goal into smaller sub-goals: {goal}"},
        ]
        llm_result = self.llm_manager.chat(messages)  # type: ignore
        if llm_result and llm_result.response_text:
            try:
                response_json = json.loads(llm_result.response_text)  # type: ignore
                if "sub_goals" in response_json and isinstance(response_json["sub_goals"], list):
                    sub_goals.extend(response_json["sub_goals"])
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse decompose_goal response as JSON, attempting manual extraction")
                sub_goals.extend(self._extract_sub_goals_manually(llm_result.response_text))  # type: ignore
        if not sub_goals:
            sub_goals.append(goal)
        return sub_goals

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
            self.status_callback({"type": "info", "content": f"Starting to achieve goal: {goal}"})  # type: ignore

        if self.llm_manager is None:
            self.logger.error("LLMManager is not initialized. Cannot proceed with goal.")
            raise ValueError("LLMManager is not initialized.")

        sub_goals = self.decompose_goal(goal)
        if len(sub_goals) == 0:  # type: ignore
            self.logger.error("No sub-goals were generated from goal decomposition.")
            raise ValueError("Failed to decompose goal into sub-goals.")

        if self.status_callback is not None:
            self.status_callback({
                "type": "info",
                "content": f"Decomposed goal into {len(sub_goals)} sub-goals.",  # type: ignore
            })  # type: ignore

        for i, sub_goal in enumerate(sub_goals):  # type: ignore
            self.logger.info(f"Processing sub-goal {i+1}/{len(sub_goals)}: {sub_goal}")  # type: ignore
            if self.status_callback is not None:
                self.status_callback({
                    "type": "info",
                    "content": f"Processing sub-goal {i+1}/{len(sub_goals)}: {sub_goal}",  # type: ignore
                })  # type: ignore
            self._execute_objective_with_retries(sub_goal)

        if self.status_callback is not None:
            self.status_callback({"type": "success", "content": f"Achieved goal: {goal}"})  # type: ignore
        self.logger.info(f"Successfully achieved goal: {goal}")
        return None

    def _add_memory_for_agents(self, title: str, content: str, memory_type: Any, scope: Any) -> None:
        """Adds a memory record for each agent managed by AgentManager, using safe fallbacks for older APIs."""
        if self.agent_manager is None:
            return
        for agent_name in self.agent_manager.get_all_agent_names():  # type: ignore[attr-defined]
            if hasattr(self.agent_manager, "add_memory_for_agent"):
                try:
                    self.agent_manager.add_memory_for_agent(
                        agent_name,
                        title,
                        content,
                        memory_type if memory_type is not None else MemoryType,  # type: ignore[name-defined]
                        scope if scope is not None else MemoryScope,  # type: ignore[name-defined]
                    )
                except TypeError:
                    # Fallback for legacy signature without type/scope
                    self.agent_manager.add_memory_for_agent(agent_name, title, content)  # type: ignore[attr-defined]
            else:
                self.logger.warning("AgentManager does not expose add_memory_for_agent()")
