"""
Task-aware Master Agent with memory isolation support

This is an enhanced version of MasterAgent that supports:
- Task-specific memory isolation
- Concurrent execution safety
- Resource-aware operation
"""

import json
import logging
import re
import threading
import time
from typing import Any, Dict, List, Optional, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.memory_manager import MemoryManager

from agents.agent_manager import AgentManager
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
from agents.master_agent import MasterAgent as BaseMasterAgent, TaskExecutionError
from utils.logger import get_logger


class TaskAwareMasterAgent(BaseMasterAgent):
    """Enhanced MasterAgent with task isolation and concurrent execution support."""
    
    def __init__(self, 
                 llm_manager,
                 agent_manager: AgentManager,
                 memory_manager: 'MemoryManager',
                 task_id: Optional[str] = None,
                 memory_scope: Optional[str] = None,
                 api_resource_manager=None,
                 status_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize TaskAwareMasterAgent with isolation support.
        
        Args:
            llm_manager: LLM manager for API calls
            agent_manager: Agent manager for tool access
            memory_manager: Memory manager for storage
            task_id: Unique task identifier
            memory_scope: Memory scope for isolation
            api_resource_manager: API resource manager for rate limiting
            status_callback: Callback for status updates
        """
        super().__init__(llm_manager, agent_manager, memory_manager, status_callback)
        
        #Task isolation properties
        self.task_id = task_id or f"task_{int(time.time())}"
        self.memory_scope = memory_scope or f"task_{self.task_id}"
        self.api_resource_manager = api_resource_manager
        
        #Task-specific execution context
        self.task_execution_context: Dict[str, Any] = {}
        self.task_metadata: Dict[str, Any] = {
            "task_id": self.task_id,
            "memory_scope": self.memory_scope,
            "created_at": time.time(),
            "isolated": True
        }
        
        #Cancellation support
        self.cancellation_requested = threading.Event()
        
        self.logger.info(f"TaskAwareMasterAgent initialized with task_id={self.task_id}, scope={self.memory_scope}")
    
    def set_task_metadata(self, metadata: Dict[str, Any]):
        """Set additional task metadata."""
        self.task_metadata.update(metadata)
    
    def request_cancellation(self):
        """Request cancellation of the current task."""
        self.cancellation_requested.set()
        self.logger.info(f"Cancellation requested for task {self.task_id}")
    
    def is_cancellation_requested(self) -> bool:
        """Check if cancellation has been requested."""
        return self.cancellation_requested.is_set()
    
    def _wait_for_api_availability(self, provider: str, timeout: float = 30.0) -> bool:
        """Wait for API availability with cancellation support."""
        if not self.api_resource_manager:
            return True
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_cancellation_requested():
                return False
                
            if self.api_resource_manager.can_make_request(provider):
                return self.api_resource_manager.register_request(provider)
                
            time.sleep(1)
        
        return False
    
    def _make_llm_request(self, messages: List[Dict], provider: str = "openai") -> Optional[Any]:
        """Make LLM request with resource management and cancellation support."""
        #Check for cancellation
        if self.is_cancellation_requested():
            self.logger.info(f"LLM request cancelled for task {self.task_id}")
            return None
        
        #Wait for API availability
        if not self._wait_for_api_availability(provider):
            self.logger.warning(f"API not available for task {self.task_id}")
            return None
        
        #Add task context to messages
        enhanced_messages = self._add_task_context_to_messages(messages)
        
        try:
            result = self.llm_manager.chat(enhanced_messages)
            
            #Store the interaction in task-specific memory
            self._store_task_interaction(messages, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM request failed for task {self.task_id}: {e}")
            return None
    
    def _add_task_context_to_messages(self, messages: List[Dict]) -> List[Dict]:
        """Add task-specific context to LLM messages."""
        #Clone messages to avoid modifying original
        enhanced_messages = messages.copy()
        
        #Add task context to system message if present
        if enhanced_messages and enhanced_messages[0].get("role") == "system":
            system_content = enhanced_messages[0]["content"]
            task_context = f"\n\n[Task Context: ID={self.task_id}, Scope={self.memory_scope}]"
            enhanced_messages[0]["content"] = system_content + task_context
        
        return enhanced_messages
    
    def _store_task_interaction(self, messages: List[Dict], result: Any):
        """Store LLM interaction in task-specific memory."""
        try:
            interaction_data = {
                "messages": messages,
                "response": result.response_text if result else None,
                "timestamp": time.time(),
                "task_metadata": self.task_metadata
            }
            
            #Store using task-specific scope
            if isinstance(self.memory_manager, EnhancedMemoryManager):
                self.memory_manager.store_memory(
                    agent_name=self.memory_scope,
                    memory_type=MemoryType.INTERACTION,
                    content=interaction_data,
                    metadata=self.task_metadata
                )
            
        except Exception as e:
            self.logger.warning(f"Failed to store task interaction: {e}")
    
    def _store_task_progress(self, step: str, status: str, details: Dict = None):
        """Store task progress in isolated memory."""
        try:
            progress_data = {
                "step": step,
                "status": status,
                "details": details or {},
                "timestamp": time.time(),
                "task_metadata": self.task_metadata
            }
            
            if isinstance(self.memory_manager, EnhancedMemoryManager):
                self.memory_manager.store_memory(
                    agent_name=self.memory_scope,
                    memory_type=MemoryType.SUCCESS,
                    content=progress_data,
                    metadata=self.task_metadata
                )
            
        except Exception as e:
            self.logger.warning(f"Failed to store task progress: {e}")
    
    def _get_task_specific_memories(self, memory_type: MemoryType, query: str = "", limit: int = 10) -> List[Dict]:
        """Retrieve memories specific to this task."""
        try:
            if isinstance(self.memory_manager, EnhancedMemoryManager):
                return self.memory_manager.retrieve_memories(
                    agent_name=self.memory_scope,
                    memory_type=memory_type,
                    query=query,
                    limit=limit
                )
        except Exception as e:
            self.logger.warning(f"Failed to retrieve task memories: {e}")
        
        return []
    
    def run_with_isolation(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with full task isolation."""
        #Set up task metadata
        task_metadata = {
            "goal": goal,
            "prompt": master_prompt,
            "options": options,
            "start_time": time.time()
        }
        self.set_task_metadata(task_metadata)
        
        #Store task start
        self._store_task_progress("task_start", "running", {"goal": goal})
        
        try:
            #Check for previous similar tasks
            similar_tasks = self._get_task_specific_memories(MemoryType.SUCCESS, goal, limit=3)
            if similar_tasks:
                self.logger.info(f"Found {len(similar_tasks)} similar completed tasks")
            
            #Run the main execution with cancellation checks
            result = self._run_with_cancellation_support(goal, master_prompt, options)
            
            #Store completion
            completion_status = "completed" if result.get("success", False) else "failed"
            self._store_task_progress("task_complete", completion_status, result)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task_id": self.task_id
            }
            
            self._store_task_progress("task_error", "failed", error_result)
            return error_result
    
    def _run_with_cancellation_support(self, goal: str, master_prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent execution with regular cancellation checks."""
        
        #Override the base run method with cancellation support
        with self.state_lock:
            if self.is_running:
                return {"success": False, "error": "Agent already running"}
            
            self.goals = [goal] if isinstance(goal, str) else goal
            if not self.goals:
                return {"success": False, "error": "No goals provided"}
            
            self.prompt = master_prompt
            self.options = options
            self.is_running = True
            self.is_paused = False
        
        try:
            #Execute the main loop with cancellation checks
            return self._execution_loop_with_cancellation()
            
        finally:
            with self.state_lock:
                self.is_running = False
    
    def _execution_loop_with_cancellation(self) -> Dict[str, Any]:
        """Main execution loop with cancellation support."""
        try:
            while self.goals and not self.is_cancellation_requested():
                current_goal = self.goals.pop(0)
                
                #Check for cancellation before each goal
                if self.is_cancellation_requested():
                    return {"success": False, "error": "Task cancelled", "task_id": self.task_id}
                
                #Store goal start
                self._store_task_progress("goal_start", "running", {"goal": current_goal})
                
                #Execute goal with cancellation checks
                success = self._execute_goal_with_cancellation(current_goal)
                
                if not success:
                    if self.is_cancellation_requested():
                        return {"success": False, "error": "Task cancelled", "task_id": self.task_id}
                    else:
                        return {"success": False, "error": "Goal execution failed", "task_id": self.task_id}
            
            return {"success": True, "task_id": self.task_id}
            
        except Exception as e:
            self.logger.error(f"Error in execution loop for task {self.task_id}: {e}", exc_info=True)
            return {"success": False, "error": str(e), "task_id": self.task_id}
    
    def _execute_goal_with_cancellation(self, goal: str) -> bool:
        """Execute a single goal with cancellation support."""
        try:
            #This is a simplified version - in reality, you'd implement
            #the full goal execution logic with cancellation checks
            
            #Check cancellation before major operations
            if self.is_cancellation_requested():
                return False
            
            #Decompose goal (with cancellation checks)
            sub_goals = self._decompose_goal_with_cancellation(goal)
            if not sub_goals:
                return False
            
            #Execute each sub-goal
            for sub_goal in sub_goals:
                if self.is_cancellation_requested():
                    return False
                
                success = self._execute_sub_goal_with_cancellation(sub_goal)
                if not success:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing goal for task {self.task_id}: {e}")
            return False
    
    def _decompose_goal_with_cancellation(self, goal: str) -> Optional[List[str]]:
        """Decompose goal with cancellation support."""
        if self.is_cancellation_requested():
            return None
        
        #Use the parent's decomposition method but with our LLM request method
        try:
            decomposition_prompt = f"""You are a helpful assistant that breaks down complex goals into a series of smaller, manageable sub-goals. 
            Analyze the following user goal. If the goal is simple and can be accomplished in a single plan (e.g., 'take a screenshot', 'check the weather'), respond with a JSON array containing only the original goal. 
            If the goal is complex (e.g., 'research a topic and write a summary', 'plan a trip'), break it down into a logical sequence of sub-goals.
            
            Respond ONLY with a valid JSON array of strings. Do not include any other text or explanation.
            
            User Goal: \"{goal}\""""
            
            messages = [{"role": "system", "content": decomposition_prompt}]
            llm_result = self._make_llm_request(messages)
            
            if not llm_result or not llm_result.response_text:
                return [goal]  #Fallback to original goal
            
            json_response = self._extract_json_from_response(llm_result.response_text)
            if not json_response:
                return [goal]
            
            sub_goals = json.loads(json_response)
            if isinstance(sub_goals, list) and all(isinstance(g, str) for g in sub_goals):
                return sub_goals
            else:
                return [goal]
                
        except Exception as e:
            self.logger.error(f"Goal decomposition failed for task {self.task_id}: {e}")
            return [goal]
    
    def _execute_sub_goal_with_cancellation(self, sub_goal: str) -> bool:
        """Execute a sub-goal with cancellation support."""
        if self.is_cancellation_requested():
            return False
        
        try:
            #Store sub-goal start
            self._store_task_progress("sub_goal_start", "running", {"sub_goal": sub_goal})
            
            #Here you would implement the actual sub-goal execution
            #For now, we'll simulate it
            time.sleep(0.1)  #Simulate work
            
            if self.is_cancellation_requested():
                return False
            
            #Store sub-goal completion
            self._store_task_progress("sub_goal_complete", "completed", {"sub_goal": sub_goal})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sub-goal execution failed for task {self.task_id}: {e}")
            return False
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get a summary of task execution."""
        memories = self._get_task_specific_memories(MemoryType.SUCCESS, limit=50)
        
        summary = {
            "task_id": self.task_id,
            "memory_scope": self.memory_scope,
            "total_operations": len(memories),
            "metadata": self.task_metadata,
            "is_cancelled": self.is_cancellation_requested()
        }
        
        #Analyze operation types
        operations = {}
        for memory in memories:
            content = memory.get("content", {})
            step = content.get("step", "unknown")
            operations[step] = operations.get(step, 0) + 1
        
        summary["operations"] = operations
        
        return summary


#Example usage
def demo_task_aware_agent():
    """Demonstrate TaskAwareMasterAgent functionality."""
    print("🧪 TaskAwareMasterAgent Demo - Isolated Memory")
    print("=" * 60)
    
    #This would normally be initialized through the TaskManager
    #but we'll create a simple demo here
    
    try:
        from agents.llm_manager import LLMManager
        from agents.agent_manager import AgentManager
        from agents.enhanced_memory_manager import EnhancedMemoryManager
        
        #Initialize components
        llm_manager = LLMManager()
        agent_manager = AgentManager()
        memory_manager = EnhancedMemoryManager()
        
        #Create two isolated agents for different tasks
        agent1 = TaskAwareMasterAgent(
            llm_manager=llm_manager,
            agent_manager=agent_manager,
            memory_manager=memory_manager,
            task_id="demo_task_1",
            memory_scope="task_demo_task_1"
        )
        
        agent2 = TaskAwareMasterAgent(
            llm_manager=llm_manager,
            agent_manager=agent_manager,
            memory_manager=memory_manager,
            task_id="demo_task_2", 
            memory_scope="task_demo_task_2"
        )
        
        print(f"✅ Created isolated agents:")
        print(f"   Agent 1: {agent1.task_id} (scope: {agent1.memory_scope})")
        print(f"   Agent 2: {agent2.task_id} (scope: {agent2.memory_scope})")
        
        #Simulate task execution
        result1 = agent1.run_with_isolation(
            "Take a screenshot",
            "Complete the screenshot task efficiently",
            {}
        )
        
        result2 = agent2.run_with_isolation(
            "Check system status",
            "Provide a comprehensive system status",
            {}
        )
        
        print(f"\n📊 Task Results:")
        print(f"   Task 1: {result1}")
        print(f"   Task 2: {result2}")
        
        #Show memory isolation
        summary1 = agent1.get_task_summary()
        summary2 = agent2.get_task_summary()
        
        print(f"\n🧠 Memory Isolation Verification:")
        print(f"   Task 1 operations: {summary1.get('operations', {})}")
        print(f"   Task 2 operations: {summary2.get('operations', {})}")
        
        print(f"\n✅ Task isolation demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_task_aware_agent()
