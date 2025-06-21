"""Master agent for orchestrating tasks."""

import json
import re
import threading
import time
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.memory_manager import MemoryManager
    from agents.creator_authentication import CreatorAuthentication
    from agents.agent_manager import AgentManager
    from agents.context_awareness_engine import ContextAwarenessEngine
    from agents.memory.memory_manager import EnhancedMemoryManager, MemoryScope
    from agents.models import Plan, PlanStep, ToolCall
    from agents.planning.strategic_planner import StrategicPlanner
    from agents.planning.tactical_planner import TacticalPlanner
    from agents.planning.operational_planner import OperationalPlanner
    from agents.tool_registry import ToolRegistry
    from utils.creator_authentication import CreatorAuthentication
    from utils.llm_manager import LLMManager
    from agents.screen_agent import ScreenAgent
    from agents.system_interaction_agent import SystemInteractionAgent
    from agents.text_agent import TextAgent
    from utils.logger import get_logger
    from monitoring.metrics_manager import metrics_manager


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
        agent_manager: "AgentManager",
        llm_manager: "LLMManager",
        memory_manager: 'MemoryManager',
        context_awareness_engine: "ContextAwarenessEngine",
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        options: Optional[Dict[str, Any]] = None,
        creator_auth: Optional['CreatorAuthentication'] = None
    ):
        self.goals: List[str] = []
        self.prompt: str = ""
        self.options = options or {}
        self.is_running: bool = False
        self.is_paused: bool = False
        self.thread: Optional[threading.Thread] = None
        self.state_lock = threading.Lock()
        self.logger = get_logger()
        self.agent_manager = agent_manager
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

        # Hierarchical Planners
        self.strategic_planner = StrategicPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager)
        self.tactical_planner = TacticalPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager)
        self.operational_planner = OperationalPlanner(llm_manager=self.llm_manager, memory_manager=self.memory_manager, agent_manager=self.agent_manager)
        self.retry_count = 0

        # State for goal clarification
        self.is_clarifying = False
        self.clarification_question: Optional[str] = None

        # Set the callback on the agent manager to receive tool updates
        self.agent_manager.master_agent_update_callback = self._on_tools_updated

        if not self.agent_manager._agents:  # Check internal agent dict
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

        self.memory_manager.add_memory_for_agent(
            agent_type=MemoryScope.USER_DATA,
            memory_type=MemoryType.FEEDBACK,
            content=memory_content,
            metadata={"goal": goal, "feedback": feedback_str, "plan_id": plan_to_record.get("id", "N/A")}
        )
        self.logger.info(f"Stored {feedback_str} feedback for goal: '{goal}'")

    def run_once(self, goal: str) -> None:
        """Runs the full hierarchical planning and execution loop for a given goal."""
        if self.is_paused or not self.is_running:
            return

        self.status_callback({"type": "info", "data": {"message": f"Starting new goal: {goal}"}})
        self.last_goal = goal
        original_goal = goal
        self.retry_count = 0

        while self.retry_count < self.MAX_RETRIES:
            try:
                # Phase 1: Strategic Planning
                self.status_callback({"type": "info", "data": {"message": "Phase 1: Decomposing goal into strategic objectives..."}})
                strategic_objectives = self.strategic_planner.generate_strategic_plan(goal)
                if not strategic_objectives:
                    self.logger.error("Strategic planner failed to generate objectives.")
                    raise Exception("Could not devise a strategic plan.")
                self.logger.info(f"Generated strategic objectives: {strategic_objectives}")
                self.status_callback({"type": "strategic_plan", "data": strategic_objectives})

                # Execute plans for each strategic objective
                for i, objective in enumerate(strategic_objectives):
                    self.status_callback({"type": "info", "data": {"message": f"Executing Strategic Objective {i+1}/{len(strategic_objectives)}: {objective}"}})
                    
                    # Phase 2: Tactical Planning
                    self.status_callback({"type": "info", "data": {"message": f"Phase 2: Breaking down objective into tactical steps..."}})
                    tactical_plan = self.tactical_planner.generate_tactical_plan(objective)
                    if not tactical_plan or 'steps' not in tactical_plan:
                        self.logger.error(f"Tactical planner failed for objective: {objective}")
                        continue # Try the next strategic objective
                    self.logger.info(f"Generated tactical plan: {tactical_plan}")
                    self.status_callback({"type": "tactical_plan", "data": tactical_plan})

                    # Phase 3: Operational Planning & Execution
                    for tactical_step in tactical_plan.get('steps', []) :
                        sub_goal = tactical_step.get('sub_goal')
                        description = tactical_step.get('description')
                        self.status_callback({"type": "info", "data": {"message": f"Executing: {description}"}})
                        
                        context = self.context_awareness_engine.get_current_context()
                        operational_plan = self.operational_planner.generate_operational_plan(sub_goal, context)
                        
                        if not operational_plan:
                            raise PlanExecutionError("Failed to generate operational plan.", tactical_step, Exception("Operational planner returned None"))

                        self.last_plan = operational_plan
                        self.logger.info(f"Generated operational plan: {operational_plan.get('description')}")
                        self.status_callback({"type": "operational_plan", "data": operational_plan})
                        
                        self._execute_plan(operational_plan)

                self.logger.info("Goal achieved successfully.")
                self.status_callback({"type": "info", "data": {"message": "Goal achieved successfully."}})
                return  # Exit after successful completion of all objectives

            except PlanExecutionError as e:
                self.logger.warning(f"Execution failed: {e}. Attempting recovery ({self.retry_count + 1}/{self.MAX_RETRIES}).")
                self.status_callback({"type": "info", "data": {"message": f"Execution failed. Attempting recovery..."}})
                recovery_goal = self._create_recovery_goal(original_goal, self.last_plan, e.step, e.original_exception, self.execution_context)
                goal = recovery_goal  # Set the new goal for the next loop iteration
                self.retry_count += 1
            
            except Exception as e:
                self.logger.error(f"A critical error occurred in run_once: {e}", exc_info=True)
                self.status_callback({"type": "error", "data": {"message": f"A critical error occurred: {e}"}})
                return  # Exit on critical failure

        self.logger.error(f"Failed to achieve goal '{original_goal}' after {self.MAX_RETRIES} retries.")
        self.status_callback({"type": "error", "data": {"message": f"Failed to achieve goal after {self.MAX_RETRIES} retries."}})

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
            if self.status_callback:
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
            if self.status_callback:
                self.status_callback({"type": "info", "content": "Clarification received. Resuming..."})

    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extracts a JSON object or array from a string, even if it's in a markdown block."""
        match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        start_brace = text.find('{')
        start_bracket = text.find('[')
        
        if start_brace == -1 and start_bracket == -1:
            return None

        if start_brace == -1:
            start = start_bracket
        elif start_bracket == -1:
            start = start_brace
        else:
            start = min(start_brace, start_bracket)

        end_brace = text.rfind('}')
        end_bracket = text.rfind(']')
        end = max(end_brace, end_bracket)

        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
            
        return None

    def _decompose_goal(self, goal: str) -> Optional[List[str]]:
        """Decomposes a complex goal into a list of simpler sub-goals."""
        if self.status_callback:
            self.status_callback({"type": "info", "content": "Analyzing goal complexity..."})
        
        decomposition_prompt = f"""You are a helpful assistant that breaks down complex goals into a series of smaller, manageable sub-goals. 
        Analyze the following user goal. If the goal is simple and can be accomplished in a single plan (e.g., 'take a screenshot', 'check the weather'), respond with a JSON array containing only the original goal. 
        If the goal is complex (e.g., 'research a topic and write a summary', 'plan a trip'), break it down into a logical sequence of sub-goals.
        
        Respond ONLY with a valid JSON array of strings. Do not include any other text or explanation.
        
        User Goal: \"{goal}\""""
        
        try:
            messages = [{"role": "system", "content": decomposition_prompt}]
            llm_result = self.llm_manager.chat(messages)
            
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM provided no response for goal decomposition.")
                return None

            json_response = self._extract_json_from_response(llm_result.response_text)
            if not json_response:
                self.logger.error(f"Failed to extract valid JSON from decomposition response: {llm_result.response_text}")
                return [goal]  # Fallback to original goal

            sub_goals = json.loads(json_response)
            if isinstance(sub_goals, list) and all(isinstance(g, str) for g in sub_goals):
                return sub_goals
            else:
                self.logger.error(f"Decomposition response is not a list of strings: {sub_goals}")
                return [goal]  # Fallback to original goal

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding failed for decomposition: {e}\nResponse was: {llm_result.response_text}", exc_info=True)
            return [goal]  # Fallback to original goal
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during goal decomposition: {e}", exc_info=True)
            return None

    def _check_goal_ambiguity(self, goal: str) -> Tuple[bool, Optional[str]]:
        """Checks if a goal is ambiguous and returns a clarification question if so."""
        if self.status_callback:
            self.status_callback({"type": "info", "content": "Checking goal for ambiguity..."})

        prompt = f"""You are an analytical assistant. Your task is to evaluate a user's goal for ambiguity.
A goal is ambiguous if it is too vague, lacks specific details, or could be interpreted in multiple ways.

Examples of ambiguous goals:
- "Process the document." (Which document? What kind of processing?)
- "Improve the file." (Which file? What does "improve" mean?)
- "Run a search." (What should be searched for? Where?)

Examples of clear goals:
- "Take a screenshot of the active window and save it to the desktop."
- "Summarize the contents of the file at 'C:/docs/report.txt'."
- "Search for 'latest AI research papers' on Google."

Analyze the following goal: "{goal}"

Respond with a JSON object with two keys:
1. "is_ambiguous": a boolean (true if the goal is ambiguous, false otherwise).
2. "question": a string. If the goal is ambiguous, this should be a clear, concise question to ask the user for clarification. If the goal is clear, this should be an empty string.

Your response must be ONLY the JSON object.
"""
        try:
            messages = [{"role": "system", "content": prompt}]
            llm_result = self.llm_manager.chat(messages)

            if not llm_result or not llm_result.response_text:
                self.logger.warning("LLM provided no response for ambiguity check.")
                return False, None

            json_response = self._extract_json_from_response(llm_result.response_text)
            if not json_response:
                self.logger.error(f"Failed to extract JSON from ambiguity check response: {llm_result.response_text}")
                return False, None

            data = json.loads(json_response)
            is_ambiguous = data.get("is_ambiguous", False)
            question = data.get("question", "")

            if is_ambiguous and question:
                return True, question
            return False, None

        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Error processing ambiguity check response: {e}\nResponse was: {llm_result.response_text}", exc_info=True)
            return False, None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during ambiguity check: {e}", exc_info=True)
            return False, None

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
        
        elif isinstance(error, InvalidToolArgumentsError):
            # The arguments were wrong. The recovery goal should be to fix them.
            return (
                f"The plan failed at step '{failed_step.get('description')}' due to invalid arguments for the tool '{failed_step.get('tool')}'.\n"
                f"The original sub-goal was: '{original_goal}'.\n"
                f"The error was: '{error}'.\n\n"
                f"Here is the execution context from the failed plan, showing the outputs of successful steps:\n{context_summary}\n\n"
                f"Please create a new, corrected plan to achieve the original sub-goal. Analyze the context and error to avoid repeating the mistake. "
                f"The overall objective is still: {self.last_goal}"
            )

        else:
            # For all other errors, use the generic recovery approach.
            self.logger.warning(f"Using generic recovery for an unrecognized error type: {type(error).__name__}")
            return self._create_recovery_goal(original_goal, plan, failed_step, error, context)

    def _create_recovery_goal(self, original_goal: str, plan: Dict[str, Any], failed_step: Dict[str, Any], error: Exception, context: Dict[str, Any]) -> str:
        """Creates a new goal to recover from a failed step, including execution context."""
        self.logger.info("Creating a recovery goal...")
        context_summary = json.dumps(context, indent=2)
        return f"""The original sub-goal was: '{original_goal}'.
A plan was created, but it failed at the step: {failed_step.get('description')}.
The error was: '{error}'.

Here is the execution context from previous successful steps:
{context_summary}

Please create a new plan to achieve the original sub-goal. Analyze the context and error to avoid repeating the mistake. The overall objective is still: {self.last_goal}"""

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
                    else:
                        self.logger.warning(f"Could not resolve dependency: {match.group(0)}. Context is missing the value.")
                        return match.group(0)

                resolved_value = re.sub(r"\{\{step_(\d+)\.output\}\}", replacer, value)
                resolved_args[key] = resolved_value
            else:
                resolved_args[key] = value
        return resolved_args

    def _execute_plan(self, plan: Dict[str, Any]) -> None:
        """
        Executes the steps outlined in the plan.
        Raises:
            PlanExecutionError: If any step fails due to a tool error or other exception.
        """
        self.logger.info("Starting plan execution.")
        self.execution_context = {}  # Reset context for new plan

        steps = plan.get("steps", [])
        if not steps:
            self.logger.warning("Plan has no steps to execute.")
            return

        for i, step in enumerate(steps):
            if not self.is_running:
                self.logger.info("Execution stopped mid-plan.")
                return

            while self.is_paused:
                time.sleep(0.1)

            step_num = i + 1
            tool_name = "unknown"
            resolved_args = {}
            try:
                tool_name = step.get("tool_name")
                if not tool_name:
                    raise ValueError("Step is missing 'tool_name'.")

                self.logger.info(f"Executing step {step_num}/{len(steps)}: {step.get('description', 'No description')}")
                if self.status_callback:
                    self.status_callback({"type": "step_start", "data": {"index": i, "description": step.get('description'), "step": step}})

                # Resolve dependencies from context
                resolved_args = self._resolve_dependencies(step.get("arguments", {}), self.execution_context)

                # Execute the tool via the agent manager
                result = self.agent_manager.execute_tool(tool_name, resolved_args)
                metrics_manager.record_tool_usage(tool_name, success=True)
                
                # Update execution context
                self.execution_context[f"step_{step_num}"] = {"output": result, "status": "success"}
                self.logger.info(f"Step {step_num} executed successfully. Result: {str(result)[:100]}...")
                if self.status_callback:
                    self.status_callback({
                        "type": "step_end", 
                        "data": {
                            "index": i, 
                            "status": "success", 
                            "result": str(result)[:200],
                            "step": {"tool_name": tool_name, "arguments": resolved_args}
                        }
                    })

            except (ToolNotFoundError, InvalidToolArgumentsError, ValueError) as e:
                metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.warning(f"Tool execution failed for step {step_num}: {e}")
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({
                        "type": "step_end",
                        "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}
                    })
                raise PlanExecutionError(message=str(e), step=step, original_exception=e)
            
            except Exception as e:
                if tool_name != "unknown":
                    metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.error(f"An unexpected error occurred during step {step_num}: {e}", exc_info=True)
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({
                        "type": "step_end",
                        "data": {"index": i, "status": "failure", "error": str(e), "step": {"tool_name": tool_name, "arguments": resolved_args}}
                    })
                raise PlanExecutionError(message=str(e), step=step, original_exception=e)

        self.logger.info("Plan execution completed successfully.")

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
    """Orchestrates goal execution by coordinating specialized agents and tools."""

    def _on_tools_updated(self):
        """Callback function for when the agent_manager reloads tools."""
        self.logger.info("MasterAgent received notification of tool update. Prompt will be regenerated on next planning cycle.")
        self._tools_changed = True



    def _register_default_agents(self) -> None:
        """Registers the default set of specialized agents."""
        self.agent_manager.add_agent("BrowserAgent", BrowserAgent())
        self.agent_manager.add_agent("ScreenAgent", ScreenAgent())
        self.agent_manager.add_agent("TextAgent", TextAgent(self.llm_manager))
        self.agent_manager.add_agent("SystemInteractionAgent", SystemInteractionAgent())
        self.logger.info("Registered default specialized agents.")


