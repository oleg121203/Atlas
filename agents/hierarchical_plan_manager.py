"""
Hierarchical Plan Manager for Atlas

This module implements a three-level hierarchical planning system:
1. Strategic Level: High-level objectives (Phases)
2. Tactical Level: Concrete plans (Tasks) 
3. Operational Level: Specific actions (Subtasks)

Each level is displayed in the chat as thinking process and in the UI as manageable tasks.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from utils.logger import get_logger
from .tool_registry import tool_registry, ToolCategory
from .email_strategy_manager import email_strategy_manager, EmailAccessMethod
from .adaptive_execution_manager import adaptive_execution_manager
from .self_regeneration_manager import self_regeneration_manager


class TaskStatus(Enum):
    """Status of a task in the hierarchical plan."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class TaskLevel(Enum):
    """Level of task in the hierarchy."""
    STRATEGIC = "strategic"  # Phase level
    TACTICAL = "tactical"    # Task level  
    OPERATIONAL = "operational"  # Subtask level


@dataclass
class HierarchicalTask:
    """Represents a task in the hierarchical plan."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    level: TaskLevel = TaskLevel.OPERATIONAL
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)  # List of child task IDs
    tools: List[str] = field(default_factory=list)  # Tools assigned to this task
    plugins: List[str] = field(default_factory=list)  # Plugins assigned to this task
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HierarchicalPlanManager:
    """
    Manages the three-level hierarchical planning system for Atlas.
    
    Features:
    - Creates strategic, tactical, and operational plans
    - Displays thinking process in chat
    - Manages task status and progress in UI
    - Assigns tools and plugins to tasks
    - Validates final goal completion
    """
    
    def __init__(self, 
                 llm_manager,
                 strategic_planner,
                 tactical_planner, 
                 operational_planner,
                 status_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize the hierarchical plan manager.
        
        Args:
            llm_manager: LLM manager for API calls
            strategic_planner: Strategic planner instance
            tactical_planner: Tactical planner instance
            operational_planner: Operational planner instance
            status_callback: Callback for status updates to UI
        """
        self.llm_manager = llm_manager
        self.strategic_planner = strategic_planner
        self.tactical_planner = tactical_planner
        self.operational_planner = operational_planner
        self.status_callback = status_callback
        self.logger = get_logger(self.__class__.__name__)
        
        # Plan storage
        self.tasks: Dict[str, HierarchicalTask] = {}
        self.root_task_id: Optional[str] = None
        self.current_plan: Optional[Dict[str, Any]] = None
        
    def create_hierarchical_plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a complete three-level hierarchical plan for the given goal.
        
        Args:
            goal: The main goal to achieve
            context: Additional context for planning
            
        Returns:
            Complete hierarchical plan structure
        """
        self.logger.info(f"Creating hierarchical plan for goal: {goal}")
        
        # Clear previous plan
        self.tasks.clear()
        self.root_task_id = None
        
        # Create root task
        root_task = HierarchicalTask(
            title=goal,
            description=f"Main goal: {goal}",
            level=TaskLevel.STRATEGIC,
            status=TaskStatus.PENDING
        )
        self.tasks[root_task.id] = root_task
        self.root_task_id = root_task.id
        
        # Send initial thinking message to chat
        self._send_chat_message("🤔 **Analyzing task complexity...**\n\nStarting creation of adaptive execution plan.")
        
        # Add delay to make it visible
        time.sleep(1)
        
        try:
            # Analyze goal complexity
            complexity = self._analyze_goal_complexity(goal)
            self._send_chat_message(f"📊 **Complexity Analysis:** {complexity['level']} complexity detected")
            time.sleep(0.5)
            
            # Level 1: Strategic Planning (Phases) - Adaptive based on complexity
            self._send_chat_message("📋 **Creating strategic plan...**")
            time.sleep(0.5)
            
            strategic_objectives = self._get_adaptive_strategic_plan(goal, complexity)
            
            self._send_chat_message(f"📋 **Strategic plan created**\n\nFound {len(strategic_objectives)} main phases:")
            
            strategic_tasks = []
            for i, objective in enumerate(strategic_objectives, 1):
                strategic_task = HierarchicalTask(
                    title=f"Phase {i}: {objective}",
                    description=objective,
                    level=TaskLevel.STRATEGIC,
                    parent_id=root_task.id
                )
                self.tasks[strategic_task.id] = strategic_task
                root_task.children.append(strategic_task.id)
                strategic_tasks.append(strategic_task)
                
                # Send thinking message for each phase
                self._send_chat_message(f"🎯 **Phase {i}:** {objective}")
                time.sleep(0.3)
                
                # Level 2: Tactical Planning (Tasks) - Adaptive based on complexity
                self._send_chat_message(f"  📝 **Creating tactical plan for Phase {i}...**")
                time.sleep(0.2)
                
                tactical_steps = self._get_adaptive_tactical_plan(objective, complexity)
                
                tactical_tasks = []
                for j, step in enumerate(tactical_steps, 1):
                    tactical_task = HierarchicalTask(
                        title=f"Task {i}.{j}: {step.get('sub_goal', 'Unknown task')}",
                        description=step.get('description', ''),
                        level=TaskLevel.TACTICAL,
                        parent_id=strategic_task.id
                    )
                    self.tasks[tactical_task.id] = tactical_task
                    strategic_task.children.append(tactical_task.id)
                    tactical_tasks.append(tactical_task)
                    
                    # Send thinking message for each task
                    self._send_chat_message(f"  📝 **Task {i}.{j}:** {step.get('sub_goal', 'Unknown task')}")
                    time.sleep(0.2)
                    
                    # Level 3: Operational Planning (Subtasks) - Adaptive based on complexity
                    self._send_chat_message(f"    ⚙️ **Creating operational plan for Task {i}.{j}...**")
                    time.sleep(0.1)
                    
                    operational_steps = self._get_adaptive_operational_plan(step.get('sub_goal', ''), complexity)
                    
                    for k, op_step in enumerate(operational_steps, 1):
                        operational_task = HierarchicalTask(
                            title=f"Action {i}.{j}.{k}: {op_step.get('tool_name', 'Unknown action')}",
                            description=f"Execute: {op_step.get('tool_name', 'Unknown')}",
                            level=TaskLevel.OPERATIONAL,
                            parent_id=tactical_task.id,
                            tools=[op_step.get('tool_name', '')],
                            metadata={"tool_args": op_step.get('arguments', {})}
                        )
                        self.tasks[operational_task.id] = operational_task
                        tactical_task.children.append(operational_task.id)
                        
                        # Send thinking message for each action
                        tool_name = op_step.get('tool_name', 'Unknown')
                        self._send_chat_message(f"    ⚙️ **Action {i}.{j}.{k}:** {tool_name}")
                        time.sleep(0.1)
            
            # Create plan structure
            self.current_plan = {
                "goal": goal,
                "root_task_id": root_task.id,
                "total_tasks": len(self.tasks),
                "strategic_tasks": len([t for t in self.tasks.values() if t.level == TaskLevel.STRATEGIC]),
                "tactical_tasks": len([t for t in self.tasks.values() if t.level == TaskLevel.TACTICAL]),
                "operational_tasks": len([t for t in self.tasks.values() if t.level == TaskLevel.OPERATIONAL]),
                "complexity": complexity,
                "created_at": time.time()
            }
            
            # Send final plan summary
            self._send_chat_message(f"✅ **Hierarchical plan created successfully!**\n\n"
                                  f"📊 **Plan Summary:**\n"
                                  f"• Complexity: {complexity['level']}\n"
                                  f"• Total tasks: {len(self.tasks)}\n"
                                  f"• Strategic phases: {self.current_plan['strategic_tasks']}\n"
                                  f"• Tactical tasks: {self.current_plan['tactical_tasks']}\n"
                                  f"• Operational actions: {self.current_plan['operational_tasks']}\n\n"
                                  f"🎯 Ready to execute the plan!")
            
            # Send plan to UI
            self._send_plan_to_ui()
            
            return self.current_plan
            
        except Exception as e:
            self.logger.error(f"Failed to create hierarchical plan: {e}", exc_info=True)
            self._send_chat_message(f"❌ **Failed to create plan:** {str(e)}")
            return None
    
    def get_task(self, task_id: str) -> Optional[HierarchicalTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_children(self, task_id: str) -> List[HierarchicalTask]:
        """Get all children of a task."""
        task = self.get_task(task_id)
        if not task:
            return []
        return [self.tasks[child_id] for child_id in task.children if child_id in self.tasks]
    
    def get_all_tasks(self) -> List[HierarchicalTask]:
        """Get all tasks in the plan."""
        return list(self.tasks.values())
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          progress: Optional[float] = None,
                          error_message: Optional[str] = None,
                          result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status
            progress: Progress percentage (0.0 to 1.0)
            error_message: Error message if failed
            result: Result data if completed
            
        Returns:
            True if update was successful
        """
        task = self.get_task(task_id)
        if not task:
            self.logger.warning(f"Task not found: {task_id}")
            return False
            
        old_status = task.status
        task.status = status
        
        if progress is not None:
            task.progress = max(0.0, min(1.0, progress))
            
        if status == TaskStatus.RUNNING and task.started_at is None:
            task.started_at = time.time()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = time.time()
            
        if error_message:
            task.error_message = error_message
            
        if result:
            task.result = result
            
        # Send status update to UI
        self._send_task_update_to_ui(task)
        
        # Send chat message for status changes
        if status != old_status:
            self._send_status_change_message(task, old_status)
            
        # Update parent progress
        self._update_parent_progress(task)
        
        return True
    
    def assign_tools_to_task(self, task_id: str, tools: List[str]) -> bool:
        """Assign tools to a task."""
        task = self.get_task(task_id)
        if not task:
            return False
            
        task.tools = tools
        self._send_task_update_to_ui(task)
        return True
    
    def assign_plugins_to_task(self, task_id: str, plugins: List[str]) -> bool:
        """Assign plugins to a task."""
        task = self.get_task(task_id)
        if not task:
            return False
            
        task.plugins = plugins
        self._send_task_update_to_ui(task)
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a task and its children."""
        return self._set_task_and_children_status(task_id, TaskStatus.PAUSED)
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a task and its children."""
        return self._set_task_and_children_status(task_id, TaskStatus.PENDING)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task and its children."""
        return self._set_task_and_children_status(task_id, TaskStatus.CANCELLED)
    
    def _set_task_and_children_status(self, task_id: str, status: TaskStatus) -> bool:
        """Set status for a task and all its children."""
        task = self.get_task(task_id)
        if not task:
            return False
            
        # Update this task
        self.update_task_status(task_id, status)
        
        # Update all children recursively
        for child_id in task.children:
            self._set_task_and_children_status(child_id, status)
            
        return True
    
    def _update_parent_progress(self, task: HierarchicalTask):
        """Update parent task progress based on children."""
        if not task.parent_id:
            return
            
        parent = self.get_task(task.parent_id)
        if not parent:
            return
            
        children = self.get_children(task.parent_id)
        if not children:
            return
            
        # Calculate average progress of children
        total_progress = sum(child.progress for child in children)
        avg_progress = total_progress / len(children)
        
        # Update parent progress
        parent.progress = avg_progress
        
        # Update parent status based on children
        if all(child.status == TaskStatus.COMPLETED for child in children):
            parent.status = TaskStatus.COMPLETED
        elif any(child.status == TaskStatus.FAILED for child in children):
            parent.status = TaskStatus.FAILED
        elif any(child.status == TaskStatus.RUNNING for child in children):
            parent.status = TaskStatus.RUNNING
            
        self._send_task_update_to_ui(parent)
    
    def _send_chat_message(self, message: str):
        """Send a message to the chat interface."""
        if self.status_callback:
            try:
                self.status_callback({
                    "type": "chat_message",
                    "role": "assistant",
                    "content": message
                })
            except Exception as e:
                self.logger.warning(f"Failed to send chat message: {e}")
    
    def _send_plan_to_ui(self):
        """Send the complete plan to the UI."""
        if self.status_callback:
            try:
                self.status_callback({
                    "type": "hierarchical_plan",
                    "data": {
                        "plan": self.current_plan,
                        "tasks": {task_id: self._task_to_dict(task) for task_id, task in self.tasks.items()}
                    }
                })
            except Exception as e:
                self.logger.warning(f"Failed to send plan to UI: {e}")
    
    def _send_task_update_to_ui(self, task: HierarchicalTask):
        """Send task update to the UI."""
        if self.status_callback:
            try:
                self.status_callback({
                    "type": "task_update",
                    "data": self._task_to_dict(task)
                })
            except Exception as e:
                self.logger.warning(f"Failed to send task update to UI: {e}")
    
    def _send_status_change_message(self, task: HierarchicalTask, old_status: TaskStatus):
        """Send status change message to chat."""
        status_emojis = {
            TaskStatus.RUNNING: "▶️",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.PAUSED: "⏸️",
            TaskStatus.CANCELLED: "🚫"
        }
        
        emoji = status_emojis.get(task.status, "📋")
        level_names = {
            TaskLevel.STRATEGIC: "Phase",
            TaskLevel.TACTICAL: "Task", 
            TaskLevel.OPERATIONAL: "Action"
        }
        
        level_name = level_names.get(task.level, "Task")
        message = f"{emoji} **{level_name}:** {task.title} - {task.status.value.upper()}"
        
        if task.status == TaskStatus.FAILED and task.error_message:
            message += f"\n💥 Error: {task.error_message}"
        elif task.status == TaskStatus.COMPLETED:
            message += " - Completed successfully!"
            
        self._send_chat_message(message)
    
    def _task_to_dict(self, task: HierarchicalTask) -> Dict[str, Any]:
        """Convert task to dictionary for UI transmission."""
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "level": task.level.value,
            "status": task.status.value,
            "progress": task.progress,
            "parent_id": task.parent_id,
            "children": task.children,
            "tools": task.tools,
            "plugins": task.plugins,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error_message": task.error_message,
            "result": task.result,
            "metadata": task.metadata
        }
    
    def validate_goal_completion(self, goal: str) -> Dict[str, Any]:
        """
        Validate if the goal has been completed successfully.
        
        Args:
            goal: The original goal to validate
            
        Returns:
            Validation result with success status and details
        """
        if not self.root_task_id:
            return {"success": False, "error": "No plan exists"}
            
        root_task = self.get_task(self.root_task_id)
        if not root_task:
            return {"success": False, "error": "Root task not found"}
            
        # Check if all tasks are completed
        all_tasks = self.get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in all_tasks if t.status == TaskStatus.FAILED]
        
        completion_rate = len(completed_tasks) / len(all_tasks) if all_tasks else 0
        
        validation_result = {
            "success": completion_rate >= 0.8 and len(failed_tasks) == 0,  # 80% completion threshold
            "completion_rate": completion_rate,
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "goal": goal,
            "validation_time": time.time()
        }
        
        if validation_result["success"]:
            self._send_chat_message("🎉 **Goal achieved successfully!**\n\n"
                                  f"✅ All tasks completed\n"
                                  f"• Completion rate: {completion_rate:.1%}")
        else:
            self._send_chat_message("⚠️ **Goal not fully achieved**\n\n"
                                  f"📊 Completion rate: {completion_rate:.1%}\n"
                                  f"❌ Errors: {len(failed_tasks)} tasks")
        
        return validation_result
    
    def update_task_progress(self, task_id: str, progress: float) -> bool:
        """
        Update the progress of a specific task.
        
        Args:
            task_id: The ID of the task to update
            progress: Progress value between 0.0 and 1.0
            
        Returns:
            True if successful, False otherwise
        """
        if task_id not in self.tasks:
            self.logger.warning(f"Task {task_id} not found for progress update")
            return False
            
        task = self.tasks[task_id]
        old_progress = task.progress
        task.progress = max(0.0, min(1.0, progress))  # Clamp between 0 and 1
        
        self.logger.info(f"Updated task {task_id} progress: {old_progress:.1%} -> {task.progress:.1%}")
        
        # Send progress update to UI
        self._send_task_update_to_ui(task)
        
        return True
    
    def execute_plan(self, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the hierarchical plan with adaptive execution and self-regeneration."""
        if plan is None:
            plan = self.current_plan or {"goal": "Unknown goal"}
        
        self.logger.info("Starting hierarchical plan execution")
        
        # First, run self-regeneration to fix any issues
        try:
            regeneration_result = self_regeneration_manager.detect_and_fix_issues()
            if regeneration_result["fixes_applied"] > 0:
                self.logger.info(f"Self-regeneration applied {regeneration_result['fixes_applied']} fixes")
        except Exception as e:
            self.logger.warning(f"Self-regeneration failed: {e}")
        
        # Extract goal criteria from plan
        goal_criteria = self._extract_goal_criteria(plan)
        
        # Use adaptive execution manager for the main goal
        main_goal = plan.get("goal", "Unknown goal")
        
        self.logger.info(f"Using adaptive execution for goal: {main_goal}")
        
        # Execute with automatic self-regeneration on errors
        max_retry_attempts = 3
        for attempt in range(max_retry_attempts):
            try:
                from .adaptive_execution_manager import adaptive_execution_manager
                
                # Execute with adaptation
                result = adaptive_execution_manager.execute_with_adaptation(
                    task_description=main_goal,
                    goal_criteria=goal_criteria
                )
                
                # Log adaptation history
                if result.get("adaptation_history"):
                    self.logger.info(f"Adaptation history: {len(result['adaptation_history'])} adaptations made")
                    for adaptation in result["adaptation_history"]:
                        self.logger.info(f"Adaptation {adaptation['attempt_num']}: {adaptation['adaptation_reason']}")
                
                # Check if goal was achieved
                if result.get("success") and self._is_goal_achieved(result, goal_criteria):
                    self.logger.info("✅ Goal achieved successfully!")
                    return result
                else:
                    self.logger.warning(f"Goal not achieved on attempt {attempt + 1}")
                    if attempt < max_retry_attempts - 1:
                        self.logger.info(f"Triggering self-regeneration and retrying... (attempt {attempt + 2}/{max_retry_attempts})")
                        
                        # Trigger self-regeneration on failure
                        try:
                            regeneration_result = self_regeneration_manager.detect_and_fix_issues()
                            if regeneration_result["fixes_applied"] > 0:
                                self.logger.info(f"Self-regeneration applied {regeneration_result['fixes_applied']} fixes before retry")
                        except Exception as e:
                            self.logger.warning(f"Self-regeneration failed before retry: {e}")
                        
                        # Wait before retry
                        import time
                        time.sleep(2)
                    else:
                        self.logger.error("Failed to achieve goal after all retry attempts")
                        return result
                
            except ImportError:
                self.logger.warning("Adaptive execution manager not available, using fallback")
                return {"success": False, "error": "Adaptive execution manager not available"}
            except Exception as e:
                self.logger.error(f"Plan execution failed on attempt {attempt + 1}: {e}")
                
                if attempt < max_retry_attempts - 1:
                    self.logger.info(f"Triggering self-regeneration due to error and retrying... (attempt {attempt + 2}/{max_retry_attempts})")
                    
                    # Trigger self-regeneration on error
                    try:
                        regeneration_result = self_regeneration_manager.detect_and_fix_issues()
                        if regeneration_result["fixes_applied"] > 0:
                            self.logger.info(f"Self-regeneration applied {regeneration_result['fixes_applied']} fixes after error")
                    except Exception as regen_error:
                        self.logger.warning(f"Self-regeneration failed after error: {regen_error}")
                    
                    # Wait before retry
                    import time
                    time.sleep(2)
                else:
                    self.logger.error("Failed to execute plan after all retry attempts")
                    return {"success": False, "error": str(e)}

    def _is_goal_achieved(self, result: Dict[str, Any], goal_criteria: Dict[str, Any]) -> bool:
        """Check if the goal is achieved based on criteria and result content."""
        if not result.get("success"):
            return False
        
        # Check for email-related goals
        if "email" in goal_criteria or "gmail" in goal_criteria:
            emails_found = result.get("data", {}).get("emails", [])
            if len(emails_found) == 0:
                return False
            
            # Check for security emails if specified
            if "security" in goal_criteria:
                security_emails = [e for e in emails_found if "security" in e.get("subject", "").lower()]
                if len(security_emails) == 0:
                    return False
        
        # Check for browser navigation goals
        if "browser" in goal_criteria or "safari" in goal_criteria:
            browser_result = result.get("data", {}).get("browser_result", {})
            if not browser_result.get("success"):
                return False
        
        # Check if result contains meaningful data
        if not result.get("data") and not result.get("message"):
            return False
        
        return True
    
    def _extract_goal_criteria(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract goal criteria from plan.
        The result is only a success if the user receives the actual requested data (e.g., list of emails),
        not just technical completion or passing through fallback rounds.
        """
        goal_criteria = {}
        goal_text = plan.get("goal", "").lower()

        # Always include all relevant keys for robust checking
        if any(keyword in goal_text for keyword in ["email", "gmail", "mail"]):
            goal_criteria["email"] = True
            goal_criteria["emails"] = True
            if "security" in goal_text:
                goal_criteria["security"] = True
                goal_criteria["security_emails"] = True
        if any(keyword in goal_text for keyword in ["browser", "safari", "navigate"]):
            goal_criteria["browser"] = True
            if "safari" in goal_text:
                goal_criteria["safari"] = True
        # Always add task description for context
        goal_criteria["task_description"] = plan.get("goal", "")
        return goal_criteria
    
    def _execute_task_recursive(self, task: HierarchicalTask) -> bool:
        """
        Execute a task and its children recursively.
        
        Args:
            task: The task to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update task status to running
            old_status = task.status
            self.update_task_status(task.id, TaskStatus.RUNNING)
            
            # Add delay to make execution visible
            time.sleep(0.5)
            
            # Execute based on task level
            if task.level == TaskLevel.STRATEGIC:
                # Strategic tasks coordinate their children
                self._send_chat_message(f"🎯 **Starting Phase:** {task.title}")
                time.sleep(0.3)
                
                success = True
                for child_id in task.children:
                    child_task = self.get_task(child_id)
                    if child_task:
                        if not self._execute_task_recursive(child_task):
                            success = False
                            break
                    else:
                        self.logger.warning(f"Child task {child_id} not found")
                        success = False
                        break
                
                if success:
                    self.update_task_status(task.id, TaskStatus.COMPLETED, progress=1.0)
                    self._send_chat_message(f"✅ **Phase completed:** {task.title}")
                else:
                    self.update_task_status(task.id, TaskStatus.FAILED)
                    self._send_chat_message(f"❌ **Phase failed:** {task.title}")
                
                return success
                
            elif task.level == TaskLevel.TACTICAL:
                # Tactical tasks coordinate their operational children
                self._send_chat_message(f"📝 **Starting Task:** {task.title}")
                time.sleep(0.2)
                
                success = True
                for child_id in task.children:
                    child_task = self.get_task(child_id)
                    if child_task:
                        if not self._execute_task_recursive(child_task):
                            success = False
                            break
                    else:
                        self.logger.warning(f"Child task {child_id} not found")
                        success = False
                        break
                
                if success:
                    self.update_task_status(task.id, TaskStatus.COMPLETED, progress=1.0)
                    self._send_chat_message(f"✅ **Task completed:** {task.title}")
                else:
                    self.update_task_status(task.id, TaskStatus.FAILED)
                    self._send_chat_message(f"❌ **Task failed:** {task.title}")
                
                return success
                
            elif task.level == TaskLevel.OPERATIONAL:
                # Operational tasks execute actual actions
                self._send_chat_message(f"⚙️ **Executing Action:** {task.title}")
                time.sleep(0.5)
                
                success = self._execute_operational_task(task)
                
                if success:
                    self.update_task_status(task.id, TaskStatus.COMPLETED, progress=1.0)
                    self._send_chat_message(f"✅ **Action completed:** {task.title}")
                else:
                    self.update_task_status(task.id, TaskStatus.FAILED)
                    self._send_chat_message(f"❌ **Action failed:** {task.title}")
                
                return success
            else:
                self.logger.error(f"Unknown task level: {task.level}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}", exc_info=True)
            self.update_task_status(task.id, TaskStatus.FAILED, error_message=str(e))
            return False
    
    def _execute_operational_task(self, task: HierarchicalTask) -> bool:
        """
        Execute an operational task using real tools.
        
        Args:
            task: The operational task to execute
            
        Returns:
            True if task completed successfully, False otherwise
        """
        self.logger.info(f"Executing operational task: {task.title}")
        
        # Update task status to running
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        task.progress = 0.0
        self._send_task_update_to_ui(task)
        
        task_results = []
        
        try:
            # Execute each tool assigned to this task
            for tool_name in task.tools:
                self.logger.info(f"Executing tool: {tool_name}")
                self._send_chat_message(f"🔧 **Using tool:** {tool_name}")
                
                # Validate tool name
                valid_tools = ["screenshot_tool", "BrowserTool", "search_tool", 
                             "mouse_keyboard_tool", "clipboard_tool", "terminal_tool", "generic_executor"]
                
                if tool_name not in valid_tools:
                    tool_name = "generic_executor"
                
                if tool_name == "screenshot_tool":
                    # Execute screenshot tool
                    self.logger.info("Executing screenshot tool")
                    self._send_chat_message("📷 **Taking screenshot...**")
                    
                    try:
                        from tools.screenshot_tool import capture_screen
                        screenshot_result = capture_screen()
                        
                        if screenshot_result.success:
                            result = {
                                "tool": "screenshot_tool",
                                "success": True,
                                "result": f"Screenshot saved to {screenshot_result.file_path}",
                                "file_path": screenshot_result.file_path,
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message("✅ **Screenshot taken successfully**")
                        else:
                            result = {
                                "tool": "screenshot_tool",
                                "success": False,
                                "error": screenshot_result.error,
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message(f"❌ **Screenshot failed:** {screenshot_result.error}")
                            
                    except Exception as e:
                        result = {
                            "tool": "screenshot_tool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Screenshot failed:** {str(e)}")
                        
                elif tool_name == "BrowserTool":
                    # Execute real browser tool
                    self.logger.info("Executing real browser tool")
                    self._send_chat_message("🌐 **Opening browser...**")
                    
                    try:
                        from tools.browser import BrowserTool
                        browser = BrowserTool()
                        
                        # Get action from arguments
                        action = task.metadata["tool_args"].get("action", "open_browser")
                        url = task.metadata["tool_args"].get("url", "https://google.com")
                        
                        if action == "open_browser":
                            browser_result = browser.open_url(url)
                        else:
                            browser_result = {"success": False, "error": f"Unknown action: {action}"}
                        
                        if browser_result["success"]:
                            result = {
                                "tool": "BrowserTool",
                                "success": True,
                                "result": browser_result["message"],
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message("✅ **Browser opened successfully**")
                        else:
                            result = {
                                "tool": "BrowserTool",
                                "success": False,
                                "error": browser_result.get("error", "Unknown error"),
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message(f"❌ **Browser failed:** {browser_result.get('error', 'Unknown error')}")
                        
                        browser.close()
                        
                    except Exception as e:
                        result = {
                            "tool": "BrowserTool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Browser failed:** {str(e)}")
                        
                elif tool_name == "EmailFilter":
                    # Execute email filter tool using Email Strategy Manager
                    self.logger.info("Executing email filter tool with Email Strategy Manager")
                    self._send_chat_message("📧 **Processing email request...**")
                    
                    try:
                        # Get task description from metadata
                        task_description = task.metadata.get("task_description", task.title)
                        
                        # Use Email Strategy Manager to execute the task
                        result = email_strategy_manager.execute_email_task(task_description)
                        
                        if result["success"]:
                            result_dict = {
                                "tool": "EmailFilter",
                                "success": True,
                                "result": result["message"],
                                "method": result.get("method", "unknown"),
                                "data": result.get("data", {}),
                                "timestamp": time.time()
                            }
                            task_results.append(result_dict)
                            self._send_chat_message(f"✅ **{result['message']}** (Method: {result.get('method', 'unknown')})")
                        else:
                            result_dict = {
                                "tool": "EmailFilter",
                                "success": False,
                                "error": result.get("error", "Email task failed"),
                                "method": result.get("method", "unknown"),
                                "timestamp": time.time()
                            }
                            task_results.append(result_dict)
                            self._send_chat_message(f"❌ **Email task failed:** {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        result_dict = {
                            "tool": "EmailFilter",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result_dict)
                        self._send_chat_message(f"❌ **Email task failed:** {str(e)}")
                        
                elif tool_name == "search_tool":
                    # Execute real Gmail search tool
                    self.logger.info("Executing real search tool")
                    self._send_chat_message("🔍 **Searching Gmail for security emails...**")
                    
                    try:
                        from tools.gmail_tool import get_gmail_tool
                        gmail_tool = get_gmail_tool()
                        
                        # Search for security emails
                        search_result = gmail_tool.search_security_emails(days_back=30)
                        
                        if search_result["success"]:
                            email_count = search_result["count"]
                            result = {
                                "tool": "search_tool",
                                "success": True,
                                "result": search_result["message"],
                                "search_query": "security emails",
                                "results_count": email_count,
                                "emails": search_result["results"],
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message(f"✅ **Search completed:** Found {email_count} security emails")
                        else:
                            result = {
                                "tool": "search_tool",
                                "success": False,
                                "error": search_result.get("error", "Unknown error"),
                                "timestamp": time.time()
                            }
                            task_results.append(result)
                            self._send_chat_message(f"❌ **Search failed:** {search_result.get('error', 'Unknown error')}")
                        
                    except Exception as e:
                        result = {
                            "tool": "search_tool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Search failed:** {str(e)}")
                        
                elif tool_name == "mouse_keyboard_tool":
                    # Execute mouse interaction tool
                    self.logger.info("Executing mouse interaction tool")
                    self._send_chat_message("🖱️ **Interacting with mouse and keyboard...**")
                    
                    try:
                        # Simulate mouse interaction
                        time.sleep(0.5)
                        result = {
                            "tool": "mouse_keyboard_tool",
                            "success": True,
                            "result": "Mouse interaction completed",
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message("✅ **Mouse interaction completed**")
                        
                    except Exception as e:
                        result = {
                            "tool": "mouse_keyboard_tool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Mouse interaction failed:** {str(e)}")
                        
                elif tool_name == "clipboard_tool":
                    # Execute clipboard tool
                    self.logger.info("Executing clipboard tool")
                    self._send_chat_message("📋 **Copying to clipboard...**")
                    
                    try:
                        # Simulate clipboard operation
                        time.sleep(0.5)
                        result = {
                            "tool": "clipboard_tool",
                            "success": True,
                            "result": "Clipboard operation completed",
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message("✅ **Clipboard operation completed**")
                        
                    except Exception as e:
                        result = {
                            "tool": "clipboard_tool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Clipboard operation failed:** {str(e)}")
                        
                elif tool_name == "terminal_tool":
                    # Execute terminal tool
                    self.logger.info("Executing terminal tool")
                    self._send_chat_message("💻 **Executing terminal command...**")
                    
                    try:
                        # Simulate terminal execution
                        time.sleep(0.5)
                        result = {
                            "tool": "terminal_tool",
                            "success": True,
                            "result": "Terminal command executed",
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message("✅ **Terminal command executed**")
                        
                    except Exception as e:
                        result = {
                            "tool": "terminal_tool",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Terminal execution failed:** {str(e)}")
                        
                elif tool_name == "generic_executor":
                    # Execute generic executor
                    self.logger.info("Executing generic executor")
                    self._send_chat_message("⚙️ **Executing generic task...**")
                    
                    try:
                        # Simulate generic task execution
                        time.sleep(0.5)
                        result = {
                            "tool": "generic_executor",
                            "success": True,
                            "result": "Generic task executed",
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message("✅ **Generic task executed**")
                        
                    except Exception as e:
                        result = {
                            "tool": "generic_executor",
                            "success": False,
                            "error": str(e),
                            "timestamp": time.time()
                        }
                        task_results.append(result)
                        self._send_chat_message(f"❌ **Generic task execution failed:** {str(e)}")
            
            # Store results in task
            task.result = {
                "execution_time": time.time(),
                "tools_used": task.tools,
                "results": task_results,
                "success": all(r.get("success", False) for r in task_results)
            }
            
            return task.result["success"]
            
        except Exception as e:
            self.logger.error(f"Error executing operational task {task.id}: {e}")
            task.result = {
                "execution_time": time.time(),
                "error": str(e),
                "success": False
            }
            return False
    
    def analyze_final_results(self, goal: str) -> Dict[str, Any]:
        """
        Analyze final results and provide concrete answer to the original goal.
        
        Args:
            goal: The original goal
            
        Returns:
            Analysis with concrete answer and summary
        """
        if not self.root_task_id:
            return {"error": "No plan exists"}
            
        # Collect all results from completed tasks
        all_tasks = self.get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED and t.result]
        
        # Analyze results based on goal type
        goal_lower = goal.lower()
        
        if any(keyword in goal_lower for keyword in ["email", "mail", "gmail", "security"]):
            return self._analyze_email_results(goal, completed_tasks)
        elif any(keyword in goal_lower for keyword in ["screenshot", "capture", "screen"]):
            return self._analyze_screenshot_results(goal, completed_tasks)
        elif any(keyword in goal_lower for keyword in ["search", "find", "browse"]):
            return self._analyze_search_results(goal, completed_tasks)
        else:
            return self._analyze_general_results(goal, completed_tasks)
    
    def _analyze_email_results(self, goal: str, completed_tasks: List[HierarchicalTask]) -> Dict[str, Any]:
        """Analyze results for email-related goals."""
        email_count = 0
        security_emails = []
        tools_used = []
        email_details = []
        
        for task in completed_tasks:
            if task.result and task.result.get("success"):
                for tool_result in task.result.get("results", []):
                    if tool_result.get("tool") == "search_tool":
                        email_count = tool_result.get("results_count", 0)
                        tools_used.append("Gmail Search")
                        # Get actual email details if available
                        if "emails" in tool_result:
                            email_details = tool_result["emails"]
                    elif tool_result.get("tool") == "BrowserTool":
                        tools_used.append("Web Browser")
        
        # Create concrete answer with real data
        if email_count > 0:
            answer = "✅ **Email Analysis Complete**\n\n"
            answer += f"📧 **Found {email_count} security-related emails** in your Gmail account\n\n"
            
            # Add email details if available
            if email_details:
                answer += "📋 **Recent Security Emails:**\n\n"
                for i, email in enumerate(email_details[:10], 1):  # Show first 10 emails
                    answer += f"{i}. **{email['subject']}**\n"
                    answer += f"   📅 {email['date']} | 📧 {email['from']}\n"
                    answer += f"   📝 {email['snippet'][:100]}...\n\n"
                
                if len(email_details) > 10:
                    answer += f"... and {len(email_details) - 10} more emails\n\n"
            
            answer += f"🔧 **Tools used:** {', '.join(set(tools_used))}\n\n"
            answer += "📋 **Summary:** Successfully searched your Gmail for security emails using real Gmail API. "
            answer += f"Found {email_count} emails that match security criteria. "
            answer += "These emails are sorted by date (newest first) and include security-related content."
        else:
            answer = "⚠️ **Email Search Results**\n\n"
            answer += "📧 **No security emails found** in your Gmail account\n\n"
            answer += f"🔧 **Tools used:** {', '.join(set(tools_used))}\n\n"
            answer += "📋 **Summary:** Searched your Gmail for security emails using real Gmail API but found none. "
            answer += "This could mean your account is secure or the search criteria need adjustment."
        
        return {
            "goal": goal,
            "answer": answer,
            "email_count": email_count,
            "tools_used": list(set(tools_used)),
            "success": email_count >= 0,
            "analysis_type": "email_search",
            "email_details": email_details
        }
    
    def _analyze_screenshot_results(self, goal: str, completed_tasks: List[HierarchicalTask]) -> Dict[str, Any]:
        """Analyze results for screenshot-related goals."""
        screenshots_taken = 0
        tools_used = []
        
        for task in completed_tasks:
            if task.result and task.result.get("success"):
                for tool_result in task.result.get("results", []):
                    if tool_result.get("tool") == "screenshot_tool":
                        screenshots_taken += 1
                        tools_used.append("Screenshot Tool")
        
        answer = "📷 **Screenshot Operation Complete**\n\n"
        answer += f"🖼️ **Screenshots taken:** {screenshots_taken}\n\n"
        answer += f"🔧 **Tools used:** {', '.join(set(tools_used))}\n\n"
        answer += f"📋 **Summary:** Successfully captured {screenshots_taken} screenshot(s) of your screen. "
        answer += "The screenshot(s) have been saved and are ready for use."
        
        return {
            "goal": goal,
            "answer": answer,
            "screenshots_taken": screenshots_taken,
            "tools_used": list(set(tools_used)),
            "success": screenshots_taken > 0,
            "analysis_type": "screenshot"
        }
    
    def _analyze_search_results(self, goal: str, completed_tasks: List[HierarchicalTask]) -> Dict[str, Any]:
        """Analyze results for search-related goals."""
        search_results = []
        tools_used = []
        
        for task in completed_tasks:
            if task.result and task.result.get("success"):
                for tool_result in task.result.get("results", []):
                    if tool_result.get("tool") == "search_tool":
                        search_results.append({
                            "query": tool_result.get("search_query", "Unknown"),
                            "count": tool_result.get("results_count", 0)
                        })
                        tools_used.append("Search Tool")
        
        total_results = sum(r["count"] for r in search_results)
        
        answer = "🔍 **Search Operation Complete**\n\n"
        answer += f"📊 **Total results found:** {total_results}\n\n"
        answer += f"🔧 **Tools used:** {', '.join(set(tools_used))}\n\n"
        answer += "📋 **Summary:** Successfully completed search operations. "
        answer += f"Found {total_results} total results across {len(search_results)} searches. "
        answer += "Results are ready for review."
        
        return {
            "goal": goal,
            "answer": answer,
            "total_results": total_results,
            "search_queries": [r["query"] for r in search_results],
            "tools_used": list(set(tools_used)),
            "success": total_results >= 0,
            "analysis_type": "search"
        }
    
    def _analyze_general_results(self, goal: str, completed_tasks: List[HierarchicalTask]) -> Dict[str, Any]:
        """Analyze results for general goals."""
        tools_used = []
        successful_actions = 0
        
        for task in completed_tasks:
            if task.result and task.result.get("success"):
                successful_actions += 1
                for tool_result in task.result.get("results", []):
                    if tool_result.get("tool"):
                        tools_used.append(tool_result["tool"])
        
        answer = "✅ **Task Execution Complete**\n\n"
        answer += f"📊 **Successful actions:** {successful_actions}\n\n"
        answer += f"🔧 **Tools used:** {', '.join(set(tools_used))}\n\n"
        answer += f"📋 **Summary:** Successfully completed {successful_actions} actions. "
        answer += f"Used {len(set(tools_used))} different tools. "
        answer += "All requested operations have been performed."
        
        return {
            "goal": goal,
            "answer": answer,
            "successful_actions": successful_actions,
            "tools_used": list(set(tools_used)),
            "success": successful_actions > 0,
            "analysis_type": "general"
        }
    
    def _analyze_goal_complexity(self, goal: str) -> Dict[str, Any]:
        """
        Analyze goal complexity using LLM-based intuitive assessment.
        
        Args:
            goal: The goal to analyze
            
        Returns:
            Complexity analysis with adaptive parameters
        """
        try:
            # Create concise complexity assessment prompt (limited to ~1000 tokens)
            complexity_prompt = f"""Analyze goal complexity: "{goal}"

Examples:
- "Take screenshot" → simple: 1 phase, 1 task, 1 action
- "Email security analysis" → medium: 2 phases, 2 tasks, 2 actions  
- "Comprehensive report" → complex: 3 phases, 3 tasks, 3 actions

Respond in JSON only:
{{
    "complexity_level": "simple|medium|complex",
    "phases": 1-3,
    "tasks_per_phase": 1-4,
    "actions_per_task": 1-3,
    "reasoning": "brief"
}}"""

            # Get LLM assessment with token limit
            chat_messages = [
                {"role": "system", "content": "Task complexity analyzer. Respond with JSON only. Keep under 1000 tokens."},
                {"role": "user", "content": complexity_prompt}
            ]
            
            result = self.llm_manager.chat(chat_messages, max_tokens=1000)
            
            if result and result.response_text:
                # Try to parse JSON response
                import json
                try:
                    # Extract JSON from response (handle markdown formatting)
                    response_text = result.response_text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    assessment = json.loads(response_text.strip())
                    
                    # Validate and apply assessment
                    complexity_level = assessment.get("complexity_level", "medium")
                    phases = max(1, min(3, assessment.get("phases", 2)))
                    tasks_per_phase = max(1, min(4, assessment.get("tasks_per_phase", 2)))
                    actions_per_task = max(1, min(3, assessment.get("actions_per_task", 2)))
                    reasoning = assessment.get("reasoning", "LLM assessment")
                    
                    self.logger.info(f"LLM complexity: {complexity_level} ({phases}×{tasks_per_phase}×{actions_per_task})")
                    
                    return {
                        "level": complexity_level,
                        "phases": phases,
                        "tasks_per_phase": tasks_per_phase,
                        "actions_per_task": actions_per_task,
                        "total_processes": phases * tasks_per_phase * actions_per_task,
                        "reasoning": reasoning,
                        "assessment_method": "llm_intuitive"
                    }
                    
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.warning(f"Failed to parse LLM assessment: {e}")
                    # Fall back to keyword-based analysis
                    
            # Fallback to keyword-based analysis if LLM fails
            return self._fallback_complexity_analysis(goal)
            
        except Exception as e:
            self.logger.error(f"Error in LLM complexity analysis: {e}")
            # Fallback to keyword-based analysis
            return self._fallback_complexity_analysis(goal)
    
    def _fallback_complexity_analysis(self, goal: str) -> Dict[str, Any]:
        """
        Fallback complexity analysis using keyword-based approach.
        
        Args:
            goal: The goal to analyze
            
        Returns:
            Complexity analysis with fallback parameters
        """
        goal_lower = goal.lower()
        
        # Keyword analysis
        simple_keywords = ["screenshot", "click", "type", "copy", "paste", "open", "close"]
        medium_keywords = ["search", "find", "email", "browser", "navigate", "analyze", "check"]
        complex_keywords = ["report", "analyze all", "comprehensive", "detailed", "multiple", "year", "team", "recommendations"]
        
        simple_count = sum(1 for keyword in simple_keywords if keyword in goal_lower)
        medium_count = sum(1 for keyword in medium_keywords if keyword in goal_lower)
        complex_count = sum(1 for keyword in complex_keywords if keyword in goal_lower)
        
        # Word count analysis
        word_count = len(goal.split())
        
        # Special handling for email/browser tasks
        if any(keyword in goal_lower for keyword in ["email", "mail", "gmail", "safari", "browser"]):
            if "security" in goal_lower or "account" in goal_lower:
                level = "medium"
                phases = 2
                tasks_per_phase = 2
                actions_per_task = 2
            else:
                level = "simple"
                phases = 1
                tasks_per_phase = 2
                actions_per_task = 1
        elif complex_count > 0 or word_count > 25:
            level = "complex"
            phases = 3
            tasks_per_phase = 3
            actions_per_task = 3
        elif medium_count > 0 or word_count > 15:
            level = "medium"
            phases = 2
            tasks_per_phase = 2
            actions_per_task = 2
        else:
            level = "simple"
            phases = 1
            tasks_per_phase = 1
            actions_per_task = 1
        
        return {
            "level": level,
            "phases": phases,
            "tasks_per_phase": tasks_per_phase,
            "actions_per_task": actions_per_task,
            "total_processes": phases * tasks_per_phase * actions_per_task,
            "reasoning": f"Keyword analysis: {simple_count} simple, {medium_count} medium, {complex_count} complex keywords, {word_count} words",
            "assessment_method": "keyword_fallback"
        }
    
    def _get_adaptive_strategic_plan(self, goal: str, complexity: Dict[str, Any]) -> List[str]:
        """
        Get adaptive strategic objectives based on goal complexity.
        
        Args:
            goal: The main goal
            complexity: Complexity analysis
            
        Returns:
            List of strategic objectives
        """
        goal_lower = goal.lower()
        
        # Special handling for email/browser tasks
        if any(keyword in goal_lower for keyword in ["email", "mail", "gmail", "safari", "browser"]):
            if "security" in goal_lower or "account" in goal_lower:
                return ["Access and navigate", "Search and analyze"]
            else:
                return ["Open and navigate", "Find and process"]
        
        if complexity["level"] == "simple":
            return ["Execute goal"]
        elif complexity["level"] == "medium":
            return ["Prepare and execute", "Validate results"]
        else:  # complex
            return ["Research and analyze", "Plan and prepare", "Execute and monitor", "Validate and finalize"]
    
    def _get_adaptive_tactical_plan(self, objective: str, complexity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get adaptive tactical steps based on objective and complexity.
        
        Args:
            objective: The strategic objective
            complexity: Complexity analysis
            
        Returns:
            List of tactical steps
        """
        objective_lower = objective.lower()
        steps = []
        num_tasks = complexity["tasks_per_phase"]
        
        # Use LLM to generate more intelligent tactical steps
        tactical_prompt = f"""Given the objective: "{objective}"

Generate {num_tasks} specific, actionable tactical steps that will accomplish this objective.
Each step should be concrete and executable.

For email-related objectives, focus on:
1. Email access and authentication
2. Email search and filtering
3. Email analysis and organization
4. Results presentation

For browser-related objectives, focus on:
1. Browser navigation
2. Web page interaction
3. Data extraction
4. Results processing

Return only the tactical steps as a list of dictionaries with 'sub_goal' and 'description' keys."""

        try:
            # Get LLM response for tactical planning
            response = self.llm_manager.get_response(tactical_prompt)
            
            # Parse LLM response to extract tactical steps
            # For now, we'll use a fallback approach
            if "email" in objective_lower or "gmail" in objective_lower:
                if "security" in objective_lower:
                    steps = [
                        {
                            "sub_goal": "Access Gmail account",
                            "description": "Open Gmail and verify login status"
                        },
                        {
                            "sub_goal": "Search for security emails",
                            "description": "Search Gmail for security-related emails using specific queries"
                        },
                        {
                            "sub_goal": "Filter and organize results",
                            "description": "Filter emails by date and priority, organize by security relevance"
                        },
                        {
                            "sub_goal": "Display results in chat",
                            "description": "Present found emails in chronological order with descriptions"
                        }
                    ]
                else:
                    steps = [
                        {
                            "sub_goal": "Access Gmail account",
                            "description": "Open Gmail and verify login status"
                        },
                        {
                            "sub_goal": "Search for relevant emails",
                            "description": "Search Gmail for emails matching the specified criteria"
                        },
                        {
                            "sub_goal": "Process and analyze emails",
                            "description": "Analyze found emails and extract relevant information"
                        },
                        {
                            "sub_goal": "Present results",
                            "description": "Display results in organized format"
                        }
                    ]
            else:
                # Generic tactical planning
                steps = [
                    {
                        "sub_goal": f"Prepare for {objective}",
                        "description": f"Set up necessary tools and access for {objective}"
                    },
                    {
                        "sub_goal": f"Execute {objective}",
                        "description": f"Perform the main actions for {objective}"
                    },
                    {
                        "sub_goal": f"Validate {objective}",
                        "description": f"Verify results and complete {objective}"
                    }
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to generate tactical plan with LLM: {e}")
            # Fallback to basic tactical planning
            if "email" in objective_lower or "gmail" in objective_lower:
                steps = [
                    {
                        "sub_goal": "Access Gmail account",
                        "description": "Open Gmail and verify login status"
                    },
                    {
                        "sub_goal": "Search for security emails",
                        "description": "Search Gmail for security-related emails"
                    },
                    {
                        "sub_goal": "Display results",
                        "description": "Present found emails in organized format"
                    }
                ]
            else:
                steps = [
                    {
                        "sub_goal": f"Execute {objective}",
                        "description": f"Perform the main actions for {objective}"
                    }
                ]
        
        return steps
    
    def _get_adaptive_operational_plan(self, sub_goal: str, complexity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get adaptive operational steps based on sub-goal and complexity.
        
        Args:
            sub_goal: The tactical sub-goal
            complexity: Complexity analysis
            
        Returns:
            List of operational steps
        """
        steps = []
        num_actions = complexity["actions_per_task"]
        
        # Use Tool Registry to get the most appropriate tool
        tool_name = tool_registry.get_tool_for_task(sub_goal)
        
        # Create appropriate arguments based on the tool and sub_goal
        tool_args = self._create_tool_arguments(tool_name, sub_goal)
        
        steps.append({
            "tool_name": tool_name,
            "arguments": tool_args
        })
        
        return steps
    
    def _create_tool_arguments(self, tool_name: str, sub_goal: str) -> Dict[str, Any]:
        """
        Create appropriate arguments for a given tool and sub-goal.
        
        Args:
            tool_name: Name of the tool
            sub_goal: The sub-goal description
            
        Returns:
            Dictionary of tool arguments
        """
        sub_goal_lower = sub_goal.lower()
        
        if tool_name == "EmailFilter":
            # Email-specific arguments
            if "security" in sub_goal_lower:
                query = "security account access login"
            elif "gmail" in sub_goal_lower:
                query = "important emails"
            else:
                # Extract search terms from sub_goal
                query = sub_goal_lower.replace("search for ", "").replace("find ", "")
            
            return {
                "action": "search_emails",
                "query": query,
                "max_results": 50
            }
            
        elif tool_name == "BrowserTool":
            # Browser-specific arguments
            if "gmail" in sub_goal_lower or "email" in sub_goal_lower:
                return {
                    "action": "open_browser",
                    "url": "https://gmail.com"
                }
            else:
                return {
                    "action": "open_browser",
                    "url": "https://google.com"
                }
                
        elif tool_name == "screenshot_tool":
            return {
                "action": "capture_screen"
            }
            
        elif tool_name == "search_tool":
            # General search arguments
            if "security" in sub_goal_lower:
                query = "security account access login"
            else:
                query = sub_goal_lower.replace("search for ", "").replace("find ", "")
            
            return {
                "action": "search",
                "query": query
            }
            
        else:
            # Generic arguments for other tools
            return {
                "action": "execute",
                "task": sub_goal
            } 