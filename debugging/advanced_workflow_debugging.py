import threading
import time
from typing import Any, Dict, List, Optional


class WorkflowDebugger:
    """A comprehensive debugger for workflow execution with step-through, breakpoints, and profiling."""

    def __init__(self):
        """Initialize the workflow debugger with empty state."""
        self.breakpoints: List[str] = []
        self.watch_variables: Dict[str, Any] = {}
        self.execution_state: Dict[str, Any] = {}
        self.profiling_data: Dict[str, float] = {}
        self.current_workflow_id: Optional[str] = None
        self.paused = False
        self.step_mode = False
        self.lock = threading.Lock()

    def set_breakpoint(self, workflow_id: str, step_id: str) -> None:
        """Set a breakpoint at a specific step in a workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            step_id (str): The ID of the step to break at.
        """
        breakpoint_key = f"{workflow_id}:{step_id}"
        with self.lock:
            if breakpoint_key not in self.breakpoints:
                self.breakpoints.append(breakpoint_key)
                print(f"Breakpoint set at {breakpoint_key}")

    def remove_breakpoint(self, workflow_id: str, step_id: str) -> None:
        """Remove a breakpoint from a specific step in a workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            step_id (str): The ID of the step to remove the breakpoint from.
        """
        breakpoint_key = f"{workflow_id}:{step_id}"
        with self.lock:
            if breakpoint_key in self.breakpoints:
                self.breakpoints.remove(breakpoint_key)
                print(f"Breakpoint removed from {breakpoint_key}")

    def watch_variable(self, name: str, value: Any) -> None:
        """Add or update a variable to watch during execution.

        Args:
            name (str): The name of the variable.
            value (Any): The current value of the variable.
        """
        with self.lock:
            self.watch_variables[name] = value
            print(f"Watching variable '{name}' with value: {value}")

    def start_debug_session(self, workflow_id: str) -> None:
        """Start a debug session for a specific workflow.

        Args:
            workflow_id (str): The ID of the workflow to debug.
        """
        with self.lock:
            self.current_workflow_id = workflow_id
            self.execution_state = {}
            self.profiling_data[workflow_id] = 0.0
            print(f"Debug session started for workflow {workflow_id}")

    def end_debug_session(self) -> None:
        """End the current debug session."""
        with self.lock:
            if self.current_workflow_id:
                print(f"Debug session ended for workflow {self.current_workflow_id}")
                print(
                    f"Profiling data: Total execution time = {self.profiling_data.get(self.current_workflow_id, 0.0):.2f} seconds"
                )
                self.current_workflow_id = None
                self.paused = False
                self.step_mode = False

    def before_step(
        self, workflow_id: str, step_id: str, step_func: callable, *args, **kwargs
    ) -> None:
        """Called before each step execution to check for breakpoints or step mode.

        Args:
            workflow_id (str): The ID of the workflow.
            step_id (str): The ID of the current step.
            step_func (callable): The function representing the step.
            *args: Positional arguments to the step function.
            **kwargs: Keyword arguments to the step function.
        """
        if self.current_workflow_id != workflow_id:
            return

        start_time = time.time()
        breakpoint_key = f"{workflow_id}:{step_id}"
        with self.lock:
            if breakpoint_key in self.breakpoints or self.step_mode:
                self.paused = True
                print(f"Paused at {breakpoint_key}")
                print(f"Step function: {step_func.__name__}")
                print(f"Arguments: args={args}, kwargs={kwargs}")
                print(f"Watched variables: {self.watch_variables}")
                self._handle_user_input()

        # Record execution time
        with self.lock:
            self.execution_state[breakpoint_key] = {
                "start_time": start_time,
                "completed": False,
            }

    def after_step(self, workflow_id: str, step_id: str, result: Any) -> None:
        """Called after each step execution to record results and timing.

        Args:
            workflow_id (str): The ID of the workflow.
            step_id (str): The ID of the current step.
            result (Any): The result of the step execution.
        """
        if self.current_workflow_id != workflow_id:
            return

        end_time = time.time()
        breakpoint_key = f"{workflow_id}:{step_id}"
        with self.lock:
            if breakpoint_key in self.execution_state:
                start_time = self.execution_state[breakpoint_key]["start_time"]
                duration = end_time - start_time
                self.execution_state[breakpoint_key]["completed"] = True
                self.execution_state[breakpoint_key]["duration"] = duration
                self.execution_state[breakpoint_key]["result"] = result
                self.profiling_data[workflow_id] += duration
                print(
                    f"Step {breakpoint_key} completed in {duration:.2f} seconds with result: {result}"
                )

    def _handle_user_input(self) -> None:
        """Handle user input during a paused debug session."""
        while self.paused:
            print(
                "Debug options: (c)ontinue, (s)tep, (w)atch variable, (b)reakpoint, (p)rofile, (q)uit debug"
            )
            choice = input("Enter choice: ").lower()
            if choice == "c":
                self.paused = False
                self.step_mode = False
            elif choice == "s":
                self.paused = False
                self.step_mode = True
            elif choice == "w":
                var_name = input("Enter variable name to watch: ")
                var_value = input("Enter current value or leave blank to placeholder: ")
                self.watch_variable(
                    var_name, var_value if var_value else "<placeholder>"
                )
            elif choice == "b":
                action = input("(a)dd or (r)emove breakpoint? ").lower()
                workflow_id = input("Workflow ID: ")
                step_id = input("Step ID: ")
                if action == "a":
                    self.set_breakpoint(workflow_id, step_id)
                elif action == "r":
                    self.remove_breakpoint(workflow_id, step_id)
            elif choice == "p":
                if self.current_workflow_id:
                    print(
                        f"Current profiling for {self.current_workflow_id}: {self.profiling_data.get(self.current_workflow_id, 0.0):.2f} seconds"
                    )
                    for key, state in self.execution_state.items():
                        if state["completed"]:
                            print(f"  {key}: {state['duration']:.2f} seconds")
            elif choice == "q":
                self.end_debug_session()
                self.paused = False
                self.step_mode = False

    def get_visual_debug_representation(self, workflow_id: str) -> str:
        """Generate a visual representation of the workflow debug state.

        Args:
            workflow_id (str): The ID of the workflow to visualize.

        Returns:
            str: A string representation of the debug state.
        """
        output = f"Debug State for Workflow {workflow_id}\n"
        output += "=====================================\n"
        output += f"Total Execution Time: {self.profiling_data.get(workflow_id, 0.0):.2f} seconds\n"
        output += "Breakpoints:\n"
        for bp in self.breakpoints:
            if bp.startswith(workflow_id):
                output += f"  - {bp}\n"
        output += "Watched Variables:\n"
        for var_name, var_value in self.watch_variables.items():
            output += f"  - {var_name}: {var_value}\n"
        output += "Execution State:\n"
        for key, state in self.execution_state.items():
            if key.startswith(workflow_id):
                status = "Completed" if state["completed"] else "Running"
                duration = state.get("duration", 0.0)
                output += f"  - {key}: {status} ({duration:.2f} seconds)\n"
        return output


if __name__ == "__main__":
    # Example usage
    debugger = WorkflowDebugger()
    debugger.start_debug_session("test_workflow")
    debugger.set_breakpoint("test_workflow", "step1")
    debugger.watch_variable("input_data", 42)
    debugger.before_step("test_workflow", "step1", lambda x: x, 10)
    time.sleep(1)  # Simulate some processing time
    debugger.after_step("test_workflow", "step1", 20)
    print(debugger.get_visual_debug_representation("test_workflow"))
    debugger.end_debug_session()
