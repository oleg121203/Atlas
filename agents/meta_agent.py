import time
import json
from typing import Any, Dict, List, Optional
from agents.master_agent import MasterAgent, PlanExecutionError
from utils.logger import get_logger
# --- ToolCreatorAgent integration dependencies ---
from agents.tool_creator_agent import ToolCreatorAgent
from utils.llm_manager import LLMManager
from agents.memory_manager import MemoryManager
from agents.token_tracker import TokenTracker
from utils.config_manager import config_manager

class MetaAgent:
    """
    MetaAgent: A self-healing, self-improving agent that never gives up on a goal.
    - Tries multiple strategies and toolchains to achieve the goal.
    - Analyzes errors and generates new tools if needed.
    - Can fix code, retry, and log all reasoning steps.
    - Never stops until the goal is achieved or all options are exhausted.
    """
    def __init__(self, master_agent: MasterAgent):
        self.master_agent = master_agent
        self.logger = get_logger()
        self.reasoning_log: List[str] = []
        self.max_attempts = 10
        self.max_toolchain_variants = 5
        # --- ToolCreatorAgent and dependencies initialization ---
        self.token_tracker = TokenTracker()
        self.llm_manager = LLMManager(self.token_tracker, config_manager)
        self.memory_manager = MemoryManager(self.llm_manager, config_manager)
        self.tool_creator_agent = ToolCreatorAgent(self.llm_manager, self.memory_manager)

    def get_tool_feedback_stats(self, tool_name: str) -> dict:
        """
        Aggregate user feedback for a tool from persistent memory.
        Returns a dict with counts of likes, dislikes, and comments.
        """
        feedbacks = self.memory_manager.search_memories(
            query=tool_name,
            collection_name='meta_agent_feedback',
            n_results=50
        )
        stats = {'like': 0, 'dislike': 0, 'comments': []}
        for fb in feedbacks:
            content = fb.get('content')
            if not content:
                continue
            try:
                parsed = json.loads(content)
                fb_text = parsed.get('feedback', '').strip().lower()
                if '👍' in fb_text or 'like' in fb_text:
                    stats['like'] += 1
                elif '👎' in fb_text or 'dislike' in fb_text:
                    stats['dislike'] += 1
                elif fb_text:
                    stats['comments'].append(fb_text)
            except Exception:
                continue
        return stats

    def analyze_strategy_patterns(self, similar_cases):
        """
        Find strategies (sequences of steps) that led to repeated failures or successes.
        Returns two lists: bad_strategies, good_strategies.
        """
        strategy_stats = {}
        for case in similar_cases:
            doc = case.get('content')
            if not doc:
                continue
            try:
                parsed = json.loads(doc)
                status = parsed.get('status')
                log = parsed.get('reasoning_log', [])
                # Extract strategy signature (e.g., tuple of step messages)
                strategy = tuple(entry for entry in log if entry.startswith('Step:'))
                if not strategy:
                    continue
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'success': 0, 'failure': 0}
                if status in strategy_stats[strategy]:
                    strategy_stats[strategy][status] += 1
            except Exception:
                continue
        bad_strategies = [s for s, stats in strategy_stats.items() if stats['failure'] > stats['success']]
        good_strategies = [s for s, stats in strategy_stats.items() if stats['success'] > stats['failure']]
        return bad_strategies, good_strategies

    def request_user_choice(self, options: list, prompt: str = "Choose next action:") -> str:
        """
        Request user choice for next action (stub for UI integration).
        """
        self.logger.info(f"[MetaAgent] Requesting user choice: {prompt} Options: {options}")
        self.reasoning_log.append(f"Requesting user choice: {prompt} Options: {options}")
        # In UI: show dialog with options, return user's selection
        return ''

    def achieve_goal(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Try to achieve the goal using all available strategies, self-healing and generating tools as needed.
        Returns a dict with status, result, and reasoning log.
        """
        attempt = 0
        tried_toolchains = set()
        tried_tools = set()
        # Persistent learning: search for similar past cases before starting
        similar_cases = self.search_similar_cases(goal)
        suggested_tools = []
        fail_tools = []
        bad_strategies = []
        good_strategies = []
        if similar_cases:
            self.logger.info(f"[MetaAgent] Found similar past cases for goal: {goal}")
            self.reasoning_log.append(f"Found similar past cases for goal: {goal}")
            # Suggest tools from successful history
            suggested_tools = self.suggest_tools_from_history(similar_cases)
            if suggested_tools:
                self.logger.info(f"[MetaAgent] Suggesting tools from history: {suggested_tools}")
                self.reasoning_log.append(f"Suggesting tools from history: {suggested_tools}")
            # Analyze failure patterns
            fail_tools = self.analyze_failure_patterns(similar_cases)
            if fail_tools:
                self.logger.info(f"[MetaAgent] Tools with repeated failures: {fail_tools}")
                self.reasoning_log.append(f"Tools with repeated failures: {fail_tools}")
                # Auto-fix for these tools using ToolCreatorAgent
                for tool_name in fail_tools:
                    fix_description = f"Fix or improve the tool '{tool_name}' which has repeatedly failed in past attempts. Analyze the likely cause of failure and generate a corrected version."
                    fix_result = self.tool_creator_agent.create_tool(fix_description)
                    if fix_result.get("status") == "success":
                        self.logger.info(f"[MetaAgent] Auto-fixed tool: {tool_name}")
                        self.reasoning_log.append(f"Auto-fixed tool: {tool_name}")
                        if hasattr(self.master_agent, 'agent_manager') and self.master_agent.agent_manager:
                            self.master_agent.agent_manager.reload_generated_tools()
                            self.logger.info(f"[MetaAgent] Reloaded generated tools after auto-fix.")
                            self.reasoning_log.append(f"Reloaded generated tools after auto-fix.")
                    else:
                        self.logger.warning(f"[MetaAgent] Auto-fix failed for tool: {tool_name}")
                        self.reasoning_log.append(f"Auto-fix failed for tool: {tool_name}")
            # Analyze strategy patterns
            bad_strategies, good_strategies = self.analyze_strategy_patterns(similar_cases)
            if bad_strategies:
                self.logger.info(f"[MetaAgent] Found bad strategies: {bad_strategies}")
                self.reasoning_log.append(f"Found bad strategies: {bad_strategies}")
            if good_strategies:
                self.logger.info(f"[MetaAgent] Found good strategies: {good_strategies}")
                self.reasoning_log.append(f"Found good strategies: {good_strategies}")
        # Try suggested tools first
        preferred_tools_queue = suggested_tools if similar_cases and suggested_tools else []
        while attempt < self.max_attempts:
            attempt += 1
            self.logger.info(f"[MetaAgent] Attempt {attempt} to achieve goal: {goal}")
            self.reasoning_log.append(f"Attempt {attempt}: Trying to achieve goal: {goal}")
            # Use preferred_tool from history if available and not already tried
            current_context = dict(context) if context else {}
            tool_to_try = None
            if preferred_tools_queue:
                for tool in preferred_tools_queue:
                    if tool not in tried_tools:
                        # Check user feedback for this tool
                        feedback_stats = self.get_tool_feedback_stats(tool)
                        if feedback_stats['dislike'] > feedback_stats['like']:
                            self.logger.info(f"[MetaAgent] Skipping tool '{tool}' due to negative user feedback.")
                            self.reasoning_log.append(f"Skipping tool '{tool}' due to negative user feedback.")
                            continue
                        tool_to_try = tool
                        current_context['preferred_tool'] = tool
                        self.logger.info(f"[MetaAgent] Trying preferred tool from history: {tool}")
                        self.reasoning_log.append(f"Trying preferred tool from history: {tool}")
                        break
            # Meta-reasoning: check if planned strategy matches a bad one
            planned_strategy = tuple(entry for entry in self.reasoning_log if entry.startswith('Step:'))
            if bad_strategies and planned_strategy in bad_strategies:
                self.logger.warning(f"[MetaAgent] Planned strategy matches a known bad strategy. Requesting user input or skipping.")
                self.reasoning_log.append(f"Planned strategy matches a known bad strategy. Requesting user input or skipping.")
                # Optionally, request user choice (stub)
                user_choice = self.request_user_choice(options=['try anyway', 'choose different tool/strategy'], prompt="Planned strategy is known to fail. What should I do?")
                if user_choice == 'choose different tool/strategy':
                    continue  # Skip this attempt and try next
            try:
                result = self.master_agent.run(goal, current_context)
                if result and result.get("status") == "success":
                    self.logger.info(f"[MetaAgent] Goal achieved on attempt {attempt}")
                    self.reasoning_log.append(f"Goal achieved on attempt {attempt}")
                    self._store_reasoning_log(goal, "success")
                    return {"status": "success", "result": result, "reasoning_log": self.reasoning_log}
                else:
                    self.logger.warning(f"[MetaAgent] MasterAgent did not succeed. Result: {result}")
                    self.reasoning_log.append(f"MasterAgent did not succeed. Result: {result}")
            except PlanExecutionError as e:
                self.logger.error(f"[MetaAgent] PlanExecutionError: {e}")
                self.reasoning_log.append(f"PlanExecutionError: {e}")
                new_tool = self._handle_error(e, goal, current_context, tried_tools)
                if new_tool:
                    retry_result = self._retry_with_new_tool(goal, current_context, new_tool)
                    if retry_result and retry_result.get("status") == "success":
                        self.logger.info(f"[MetaAgent] Goal achieved with new tool: {new_tool}")
                        self.reasoning_log.append(f"Goal achieved with new tool: {new_tool}")
                        self._store_reasoning_log(goal, "success")
                        return {"status": "success", "result": retry_result, "reasoning_log": self.reasoning_log}
                    else:
                        self.logger.warning(f"[MetaAgent] Retry with new tool failed: {retry_result}")
                        self.reasoning_log.append(f"Retry with new tool failed: {retry_result}")
                    tried_tools.add(new_tool)
            except Exception as e:
                self.logger.error(f"[MetaAgent] Unexpected error: {e}")
                self.reasoning_log.append(f"Unexpected error: {e}")
                new_tool = self._handle_error(e, goal, current_context, tried_tools)
                if new_tool:
                    retry_result = self._retry_with_new_tool(goal, current_context, new_tool)
                    if retry_result and retry_result.get("status") == "success":
                        self.logger.info(f"[MetaAgent] Goal achieved with new tool: {new_tool}")
                        self.reasoning_log.append(f"Goal achieved with new tool: {new_tool}")
                        self._store_reasoning_log(goal, "success")
                        return {"status": "success", "result": retry_result, "reasoning_log": self.reasoning_log}
                    else:
                        self.logger.warning(f"[MetaAgent] Retry with new tool failed: {retry_result}")
                        self.reasoning_log.append(f"Retry with new tool failed: {retry_result}")
                    tried_tools.add(new_tool)
            # Try alternative toolchains or strategies
            if len(tried_toolchains) < self.max_toolchain_variants:
                self.logger.info(f"[MetaAgent] Trying alternative toolchain/strategy...")
                self.reasoning_log.append(f"Trying alternative toolchain/strategy...")
                self._try_alternative_toolchain(goal, current_context, tried_toolchains)
            else:
                self.logger.warning(f"[MetaAgent] All toolchain variants exhausted.")
                self.reasoning_log.append(f"All toolchain variants exhausted.")
                break
            time.sleep(1)  # Avoid tight loop
        self._store_reasoning_log(goal, "failure")
        return {"status": "failure", "reasoning_log": self.reasoning_log}

    def _handle_error(self, error: Exception, goal: str, context: Optional[Dict[str, Any]], tried_tools: set):
        # Analyze the error and try to generate a new tool using ToolCreatorAgent
        self.logger.info(f"[MetaAgent] Analyzing error: {error}")
        self.reasoning_log.append(f"Analyzing error: {error}")
        tool_description = f"Create a tool to solve the following goal: '{goal}'. The following error occurred: {error}"
        result = self.tool_creator_agent.create_tool(tool_description)
        if result.get("status") == "success":
            new_tool_name = result.get("tool_name")
            self.logger.info(f"[MetaAgent] New tool generated: {new_tool_name}")
            self.reasoning_log.append(f"New tool generated: {new_tool_name}")
            # Hot-reload generated tools so the new tool is available immediately
            if hasattr(self.master_agent, 'agent_manager') and self.master_agent.agent_manager:
                self.master_agent.agent_manager.reload_generated_tools()
                self.logger.info(f"[MetaAgent] Reloaded generated tools after tool creation.")
                self.reasoning_log.append(f"Reloaded generated tools after tool creation.")
            if new_tool_name in tried_tools:
                self.logger.info(f"[MetaAgent] Tool {new_tool_name} was already tried. Skipping retry.")
                self.reasoning_log.append(f"Tool {new_tool_name} was already tried. Skipping retry.")
                return None
            return new_tool_name
        else:
            self.logger.warning(f"[MetaAgent] Tool generation failed: {result.get('message')}")
            self.reasoning_log.append(f"Tool generation failed: {result.get('message')}")
            return None

    def _retry_with_new_tool(self, goal: str, context: Optional[Dict[str, Any]], tool_name: str):
        """
        Attempt to retry the goal, explicitly using the newly generated tool if possible.
        Injects 'preferred_tool' into the context for planner/tool selection.
        """
        self.logger.info(f"[MetaAgent] Retrying goal '{goal}' with new tool: {tool_name}")
        self.reasoning_log.append(f"Retrying goal '{goal}' with new tool: {tool_name}")
        # Inject preferred_tool into context for planner/tool selection
        context = dict(context) if context else {}
        context['preferred_tool'] = tool_name
        return self.master_agent.run(goal, context)

    def _try_alternative_toolchain(self, goal: str, context: Optional[Dict[str, Any]], tried_toolchains: set):
        # Placeholder: Generate or select an alternative toolchain/plan
        self.logger.info(f"[MetaAgent] Generating alternative toolchain for goal: {goal}")
        self.reasoning_log.append(f"Generating alternative toolchain for goal: {goal}")
        # TODO: Use LLM or heuristics to generate alternative plans
        tried_toolchains.add(f"dummy_toolchain_{len(tried_toolchains)+1}")
        pass

    def get_reasoning_log(self) -> list:
        """
        Returns the current reasoning log for UI or external inspection.
        """
        return self.reasoning_log 

    def _store_reasoning_log(self, goal: str, status: str):
        """
        Store the reasoning log, status, goal, and timestamp in persistent memory for learning.
        """
        doc = {
            'goal': goal,
            'status': status,
            'reasoning_log': self.reasoning_log,
            'timestamp': time.time()
        }
        if hasattr(self, 'memory_manager') and self.memory_manager:
            self.memory_manager.add_memory(
                content=json.dumps(doc),
                collection_name='meta_agent_history'
            )
            self.logger.info(f"[MetaAgent] Stored reasoning log for goal: {goal} with status: {status}")

    def search_similar_cases(self, goal: str, n_results: int = 3):
        """
        Search persistent memory for similar past cases to the current goal.
        """
        if hasattr(self, 'memory_manager') and self.memory_manager:
            results = self.memory_manager.search_memories(
                query=goal,
                collection_name='meta_agent_history',
                n_results=n_results
            )
            return results
        return [] 

    def suggest_tools_from_history(self, similar_cases):
        """
        Find tools that led to success in similar past cases.
        """
        tool_counts = {}
        for case in similar_cases:
            doc = case.get('content')
            if not doc:
                continue
            try:
                parsed = json.loads(doc)
                if parsed.get('status') == 'success':
                    log = parsed.get('reasoning_log', [])
                    for entry in log:
                        if 'New tool generated:' in entry or 'Retrying goal' in entry or 'Trying preferred tool from history' in entry:
                            # Extract tool name from log entry
                            tool_name = entry.split(':')[-1].strip()
                            if tool_name:
                                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            except Exception:
                continue
        if tool_counts:
            return sorted(tool_counts.keys(), key=lambda k: tool_counts[k], reverse=True)
        return []

    def analyze_failure_patterns(self, similar_cases):
        """
        Find tools with repeated failures in similar past cases.
        """
        fail_counts = {}
        for case in similar_cases:
            doc = case.get('content')
            if not doc:
                continue
            try:
                parsed = json.loads(doc)
                if parsed.get('status') == 'failure':
                    log = parsed.get('reasoning_log', [])
                    for entry in log:
                        if 'Retrying goal' in entry or 'tool' in entry:
                            tool_name = entry.split(':')[-1].strip()
                            if tool_name:
                                fail_counts[tool_name] = fail_counts.get(tool_name, 0) + 1
            except Exception:
                continue
        # Return tools with more than 2 failures (threshold can be tuned)
        return [tool for tool, count in fail_counts.items() if count > 2] 

    def get_reasoning_log_for_ui(self) -> list:
        """
        Returns the reasoning log as a list of dicts with timestamp and message for UI display and feedback.
        """
        return [{
            'timestamp': time.time(),
            'message': entry
        } for entry in self.reasoning_log] 

    def save_user_feedback(self, message: str, feedback: str):
        """
        Save user feedback (like/dislike/comment) for a reasoning log message in persistent memory for future learning.
        """
        doc = {
            'message': message,
            'feedback': feedback,
            'timestamp': time.time()
        }
        if hasattr(self, 'memory_manager') and self.memory_manager:
            self.memory_manager.add_memory(
                content=json.dumps(doc),
                collection_name='meta_agent_feedback'
            )
            self.logger.info(f"[MetaAgent] Saved user feedback: {feedback} for message: {message}") 

    def propose_code_patch(self, file_path: str, problem_description: str):
        """
        Use ToolCreatorAgent (or LLM) to generate a code patch for a problematic file.
        """
        patch_prompt = (
            f"The file '{file_path}' has been identified as problematic due to: {problem_description}.\n"
            "Generate a unified diff patch (in standard diff format) that fixes the issue. "
            "Only output the diff, no explanations."
        )
        result = self.tool_creator_agent.create_tool(patch_prompt)
        if result.get('status') == 'success':
            patch = result.get('code')
            self.logger.info(f'[MetaAgent] Proposed code patch for {file_path}:\n{patch}')
            self.reasoning_log.append(f'Proposed code patch for {file_path}')
            # (Optional) Apply patch automatically or ask user for approval (stub)
            # self.apply_patch(file_path, patch)
        else:
            self.logger.warning(f'[MetaAgent] Failed to generate code patch for {file_path}')
            self.reasoning_log.append(f'Failed to generate code patch for {file_path}')

    # ... in achieve_goal, after repeated auto-fix or failure ...
    # Example usage (pseudo-code, to be integrated where needed):
    # if tool_name in fail_tools and fail_tools[tool_name] > 5:
    #     file_path = f"tools/generated/{tool_name}.py"
    #     self.propose_code_patch(file_path, f"Repeated failures and unsuccessful auto-fixes for tool '{tool_name}'") 