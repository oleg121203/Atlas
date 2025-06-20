"""Master agent for orchestrating tasks."""

import json
import logging
import re
import threading
import time
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.memory_manager import MemoryManager
    from agents.creator_authentication import CreatorAuthentication

from agents.agent_manager import AgentManager, ToolNotFoundError, InvalidToolArgumentsError
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
from agents.browser_agent import BrowserAgent
from agents.llm_manager import LLMManager
from agents.screen_agent import ScreenAgent
from agents.system_interaction_agent import SystemInteractionAgent
from agents.text_agent import TextAgent
from logger import get_logger
from monitoring.metrics_manager import metrics_manager


class TaskExecutionError(Exception):
    """Custom exception for errors during task execution."""
    pass


class MasterAgent:
    """Orchestrates goal execution by coordinating specialized agents and tools."""

    MAX_RETRIES = 3

    def __init__(
        self,
        llm_manager: LLMManager,
        agent_manager: AgentManager,
        memory_manager: 'MemoryManager',
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        creator_auth: Optional['CreatorAuthentication'] = None
    ):
        self.goals: List[str] = []
        self.prompt: str = ""
        self.options: Dict[str, Any] = {}
        self.is_running: bool = False
        self.is_paused: bool = False
        self.thread: Optional[threading.Thread] = None
        self.state_lock = threading.Lock()
        self.logger = get_logger()
        self.llm_manager = llm_manager
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.status_callback = status_callback
        self.creator_auth = creator_auth  # Додано систему аутентифікації творця
        self.stop_event = threading.Event()
        self.last_executed_plan: Optional[Dict[str, Any]] = None
        self.system_prompt_template: Optional[str] = None
        self._tools_changed = True  # Force prompt regeneration on first run
        self.last_goal: Optional[str] = None
        self.last_plan: Optional[Dict[str, Any]] = None
        self.execution_context: Dict[str, Any] = {}
        self.retry_count = 0

        # State for goal clarification
        self.is_clarifying = False
        self.clarification_question: Optional[str] = None

        # Set the callback on the agent manager to receive tool updates
        self.agent_manager.master_agent_update_callback = self._on_tools_updated

        if not self.agent_manager._agents: # Check internal agent dict
            self._register_default_agents()
        self.logger.info("MasterAgent initialized with creator authentication")

    def run(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> None:
        """Starts the agent's execution loop in a new thread."""
        
        # Перевірка на чутливі операції для аутентифікованого творця
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

    def stop(self) -> None:
        """Stops the agent's execution loop."""
        with self.state_lock:
            if not self.is_running:
                self.logger.warning("Cannot stop, agent is not running.")
                return
            self.is_running = False
            self.is_paused = False
        if self.thread:
            self.thread.join() # Wait for the thread to finish
        self.logger.info("MasterAgent stopped.")

    def continue_with_feedback(self, instruction: str) -> None:
        """Continues a paused execution based on user feedback."""
        with self.state_lock:
            if not self.is_paused:
                self.logger.warning("Agent is not paused, cannot process feedback.")
                return
            self.feedback_instruction = instruction
            self.is_paused = False  # This un-pauses the waiting loop in run_once
        self.logger.info(f"Resuming execution with user instruction: {instruction}")

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
                return [goal] # Fallback to original goal

            sub_goals = json.loads(json_response)
            if isinstance(sub_goals, list) and all(isinstance(g, str) for g in sub_goals):
                return sub_goals
            else:
                self.logger.error(f"Decomposition response is not a list of strings: {sub_goals}")
                return [goal] # Fallback to original goal

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding failed for decomposition: {e}\nResponse was: {llm_result.response_text}", exc_info=True)
            return [goal] # Fallback to original goal
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during goal decomposition: {e}", exc_info=True)
            return None

    def provide_clarification(self, clarification: str) -> None:
        """Receives clarification from the user and resumes execution."""
        with self.state_lock:
            if not self.is_clarifying:
                self.logger.warning("Not in a clarification state.")
                return
            
            original_goal = self.goals[-1]
            clarified_goal = f"{original_goal} (User clarification: {clarification})"
            self.goals[-1] = clarified_goal # Update the current goal
            
            self.is_clarifying = False
            self.clarification_question = None
            self.is_paused = False # Resume execution
            self.logger.info(f"Clarification received. New goal: {clarified_goal}")
            if self.status_callback:
                self.status_callback({"type": "info", "content": "Clarification received. Resuming..."})

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
                f"Here is the execution context from previous successful steps:\n{context_summary}\n\n"
                f"Please create a new plan to achieve the original sub-goal. Pay close attention to the tool's documentation in the error message and provide the correct arguments. "
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
        return (
            f"The original sub-goal was: '{original_goal}'.\n"
            f"A plan was created, but it failed at the step: {failed_step.get('description')}.\n"
            f"The error was: '{error}'.\n\n"
            f"Here is the execution context from the failed plan, showing the outputs of successful steps:\n{context_summary}\n\n"
            f"Please create a new, corrected plan to achieve the original sub-goal. Analyze the context and error to avoid repeating the mistake. "
            f"The overall objective is still: {self.last_goal}"
        )

    def run_once(self, goal: str) -> None:
        """Runs the full agent loop once for a given goal, including decomposition and recovery."""
        if self.status_callback:
            self.status_callback({"type": "info", "content": f"Received goal: {goal}"})
        # 1. Check for ambiguity
        is_ambiguous, question = self._check_goal_ambiguity(goal)
        if is_ambiguous:
            self.logger.info(f"Goal is ambiguous. Asking for clarification: {question}")
            self.clarification_question = question
            self.is_clarifying = True
            if self.status_callback:
                self.status_callback({"type": "request_clarification", "content": question})

            self.pause()  # Pause to wait for clarification
            # The loop will wait here until provide_clarification is called
            while self.is_paused and self.is_running:
                time.sleep(0.5)

            if not self.is_running:  # Check if stop was called while waiting
                return

            # The goal is updated in provide_clarification, so we re-assign it here
            goal = self.goals[-1]  # The clarified goal is the new last goal
            self.logger.info(f"Resuming with clarified goal: {goal}")

        self.last_goal = goal
        self.last_plan = None
        self.execution_context = {}

        sub_goals = self._decompose_goal(goal)
        if not sub_goals:
            if self.status_callback:
                self.status_callback({"type": "error", "content": "Failed to decompose goal. Aborting."})
            return

        if self.status_callback:
            self.status_callback({"type": "info", "content": f"Decomposed into {len(sub_goals)} sub-goals: {sub_goals}"})

        for i, sub_goal in enumerate(sub_goals):
            if not self.is_running:
                break
            if self.status_callback:
                self.status_callback({"type": "info", "content": f"--- Starting Sub-Goal {i+1}/{len(sub_goals)}: {sub_goal} ---"})
            
            self.retry_count = 0
            sub_goal_achieved = False
            current_sub_goal = sub_goal

            while self.retry_count <= self.MAX_RETRIES and not sub_goal_achieved and self.is_running:
                plan = self._generate_plan(current_sub_goal)

                error, failed_step, context = (None, None, self.execution_context)
                if not plan:
                    error = TaskExecutionError("Failed to generate a valid plan.")
                else:
                    self.last_plan = plan
                    self.last_executed_plan = plan
                    if self.status_callback:
                        self.status_callback({"type": "plan", "data": plan})
                    error, failed_step, context = self._execute_plan(plan)

                self.execution_context = context

                if error:
                    self.retry_count += 1
                    if self.retry_count <= self.MAX_RETRIES:
                        self.logger.warning(f"An error occurred: {error}. Retrying ({self.retry_count}/{self.MAX_RETRIES}).")
                        if self.status_callback:
                            self.status_callback({"type": "error", "content": f"An error occurred: {error}. Retrying ({self.retry_count}/{self.MAX_RETRIES})."})
                        current_sub_goal = self._recover_from_error(sub_goal, self.last_plan, failed_step, error, self.execution_context)
                        continue
                    else:
                        self.logger.error(f"Sub-goal '{sub_goal}' failed after {self.MAX_RETRIES} retries. Last error: {error}")
                        if self.status_callback:
                            self.status_callback({"type": "request_feedback", "content": f"I've failed to achieve the sub-goal '{sub_goal}'. The last error was: {error}. Please provide guidance..."})
                        
                        self.pause()
                        while self.is_paused and self.is_running:
                            time.sleep(0.5)
                        
                        feedback = getattr(self, 'feedback_instruction', 'abort').lower()
                        self.feedback_instruction = None

                        if not self.is_running or feedback == 'abort':
                            if self.status_callback:
                                self.status_callback({"type": "error", "content": "User aborted the goal."})
                            return
                        
                        if feedback == 'skip':
                            if self.status_callback:
                                self.status_callback({"type": "info", "content": "User skipped the sub-goal."})
                            sub_goal_achieved = True
                            continue
                        
                        # New instructions from user
                        self.logger.info(f"User provided new instructions: {feedback}")
                        if self.status_callback:
                            self.status_callback({"type": "info", "content": "User provided new instructions. Retrying..."})
                        current_sub_goal = f"The original sub-goal was '{sub_goal}'. It failed with error '{error}'. The user has provided new instructions: '{feedback}'. Please create a new plan based on this."
                        self.retry_count = 0
                        self.execution_context = {}
                        continue
                else:
                    # Success
                    self.logger.info(f"Sub-goal '{sub_goal}' executed successfully!")
                    if self.status_callback:
                        self.status_callback({"type": "success", "content": f"Sub-goal '{sub_goal}' executed successfully!"})
                    self.memory_manager.add_memory_for_agent(
                        agent_type=MemoryScope.MASTER_AGENT,
                        memory_type=MemoryType.SUCCESS,
                        content=f"Successfully executed plan for sub-goal: {sub_goal}. Plan: {json.dumps(self.last_plan, indent=2)}",
                        metadata={"goal": self.last_goal, "sub_goal": sub_goal}
                    )
                    sub_goal_achieved = True

            if not sub_goal_achieved:
                self.logger.error(f"Failed to achieve sub-goal '{sub_goal}'. Aborting goal.")
                if self.status_callback:
                    self.status_callback({"type": "error", "content": f"Failed to achieve sub-goal '{sub_goal}'. Aborting entire goal."})
                return

        if self.is_running: self.status_callback({"type": "success", "content": "All sub-goals completed. Main goal achieved!"})

    def _execution_loop(self) -> None:
        """The core loop where the agent processes its goals."""
        self.logger.info("Execution loop started.")
        is_cyclic = self.options.get("cyclic", False)

        while self.is_running:
            for current_goal in self.goals:
                if not self.is_running: break
                self.logger.info(f"Processing goal: '{current_goal}'")
                self.run_once(current_goal)
                time.sleep(1)
            if not is_cyclic:
                break
        self.is_running = False
        self.logger.info("Execution loop finished.")

    def _get_planning_prompt(self, goal: str, feedback: List[Dict[str, Any]], knowledge: List[Dict[str, Any]]) -> str:
        """Constructs the system prompt for the planning LLM."""
        tools_string = self.agent_manager.get_tool_list_string()

        # Process feedback
        feedback_context = "No past attempts on record for this goal."
        if feedback:
            feedback_items = []
            for mem in feedback:
                try:
                    content_data = json.loads(mem.get('content', '{}'))
                    feedback_type = content_data.get("feedback", "unknown")
                    past_goal = content_data.get("goal", "unknown goal")
                    reason = content_data.get("reason", "")
                    outcome = "succeeded" if feedback_type == "good" else "failed"
                    
                    entry = f"- For a past goal '{past_goal}', a plan was executed and it {outcome}."
                    if feedback_type == "bad" and reason and reason != "No reason provided.":
                        entry += f" The stated reason for failure was: '{reason}'"
                    feedback_items.append(entry)
                except json.JSONDecodeError:
                    feedback_items.append(f"- A past execution resulted in: {mem.get('content', 'N/A')}")
            if feedback_items:
                feedback_context = "\n".join(feedback_items)

        # Process knowledge
        general_context = "No relevant general knowledge found."
        if knowledge:
            knowledge_items = [f"- (From collection: {mem.get('collection', 'general')}) {mem.get('content', 'N/A')}" for mem in knowledge]
            if knowledge_items:
                general_context = "\n".join(knowledge_items)

        prompt = f"""You are an expert planner AI. Your task is to create a JSON-based step-by-step plan to achieve a high-level goal.
Analyze the user's goal and create a precise plan using only the tools available to you.

**Goal:**
{goal}

**Available Tools:**
{tools_string}

**Critique of Past Attempts (Learn from these!):**
{feedback_context}

**Relevant General Knowledge:**
{general_context}

**Your Mandate:**
Based on the goal and the critique of past attempts, devise a new, superior plan.
- If past attempts FAILED, your new plan MUST propose a different sequence of actions or use different arguments to avoid repeating the same mistakes.
- Do not repeat a failed plan. Think critically and devise a novel approach.
- If past attempts succeeded, consider if the plan can be made more efficient or robust.

**Your Plan (MUST be a single JSON object):**
- The plan must be a JSON object with two keys: "description" and "steps".
- "description" should be a brief, user-friendly summary of the plan.
- "steps" must be a list of JSON objects, where each object represents a single step.
- Each step object must have "tool_name" and "arguments".
- "tool_name" must be one of the available tools.
- "arguments" must be a JSON object of key-value pairs for the tool's parameters.
- Use the special syntax `{{{{step_N.output}}}}` to reference the output of a previous step (e.g., `{{{{step_1.output}}}}`).

Generate the plan now.
"""
        return prompt
        return template.format(
            feedback_section=feedback_prompt_section,
            knowledge_section=knowledge_prompt_section,
            goal=goal
        )

    def _generate_plan(self, goal: str, override_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generates a plan using the LLM to achieve the given goal."""
        feedback_memories = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.USER_DATA,
            query=goal,
            memory_type=MemoryType.FEEDBACK,
            n_results=3
        )
        general_memories = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            query=goal,
            memory_type=MemoryType.SUCCESS,
            n_results=5
        )

        self.logger.info(f"Generating plan for goal: '{goal}'...")
        if self.status_callback: self.status_callback({"type": "info", "content": f"Generating plan for goal: {goal}"})

        prompt = override_prompt or self._get_planning_prompt(goal, feedback_memories, general_memories)

        messages = [{"role": "system", "content": prompt}]
        try:
            llm_result = self.llm_manager.chat(messages)
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for plan generation.")
                return None

            response_str = llm_result.response_text
            self.logger.debug(f"LLM raw response for plan: {response_str}")
            
            json_str = self._extract_json_from_response(response_str)
            if not json_str:
                self.logger.error(f"Could not extract JSON from LLM response: {response_str}")
                return None

            plan = json.loads(json_str)
            if self.status_callback:
                self.status_callback({"type": "plan", "data": plan})
            return plan
        except Exception as e:
            self.logger.error(f"Plan generation failed: {e}", exc_info=True)
            if self.status_callback:
                self.status_callback({"type": "error", "data": {"message": f"Plan generation failed: {e}"}})
            return None

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

    def _execute_plan(self, plan: Dict[str, Any]) -> Tuple[Optional[Exception], Optional[Dict[str, Any]], Dict[str, Any]]:
        """Executes the steps outlined in the plan. Returns error, failed step, and context."""
        self.logger.info(f"Executing plan: {plan.get('description', 'No description')}")
        self.execution_context: Dict[str, Any] = {}

        for i, step in enumerate(plan.get("steps", [])):
            if not self.is_running:
                self.logger.info("Execution stopped by user.")
                return TaskExecutionError("Execution stopped by user."), step, self.execution_context

            step_num = i + 1
            self.logger.info(f"Executing step {step_num}/{len(plan['steps'])}: {step['description']}")
            
            tool_name = "unknown"
            resolved_args = {}
            try:
                tool_name = step.get("tool")
                if not tool_name:
                    raise TaskExecutionError(f"Step {step_num} is missing the 'tool' key.")

                args = step.get("args", {})
                resolved_args = self._resolve_dependencies(args, self.execution_context)
                
                if self.status_callback:
                    self.status_callback({
                        "type": "step_start", 
                        "data": {
                            "index": i, 
                            "description": step['description'],
                            "step": {"tool_name": tool_name, "arguments": resolved_args}
                        }
                    })

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
                            "step": {"tool_name": tool_name, "arguments": resolved_args}
                        }
                    })

            except Exception as e:
                if tool_name and tool_name != "unknown":
                    metrics_manager.record_tool_usage(tool_name, success=False)
                self.logger.error(f"Error executing step {step_num}: {e}", exc_info=True)
                self.execution_context[f"step_{step_num}"] = {"output": str(e), "status": "failure"}
                if self.status_callback:
                    self.status_callback({
                        "type": "step_end", 
                        "data": {
                            "index": i, 
                            "status": "failure", 
                            "error": str(e),
                            "step": {"tool_name": tool_name, "arguments": resolved_args}
                        }
                    })
                return e, step, self.execution_context

        self.logger.info("Plan execution completed successfully.")
        return None, None, self.execution_context

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


