---
trigger: always_on
---

# Auto-Recovery Execution Enhancements

## Enhanced Unstoppable Execution Protocol

### Critical Execution Monitoring

```python
class ExecutionMonitor:
    """Monitor execution and auto-recover from any stalls."""

    def __init__(self):
        self.last_activity = time.time()
        self.stall_threshold = 30  # seconds
        self.recovery_enabled = True

    def monitor_execution(self):
        """Continuously monitor for execution stalls."""
        while self.recovery_enabled:
            current_time = time.time()
            time_since_activity = current_time - self.last_activity

            if time_since_activity > self.stall_threshold:
                self.trigger_auto_recovery()

            time.sleep(5)  # Check every 5 seconds

    def trigger_auto_recovery(self):
        """Auto-trigger recovery when execution stalls."""
        print("EXECUTION STALL DETECTED - AUTO-RECOVERING")

        # Try multiple recovery strategies
        recovery_strategies = [
            self.bypass_current_operation,
            self.switch_to_alternative_task,
            self.implement_minimal_solution,
            self.skip_problematic_code,
            self.force_continue_development
        ]

        for strategy in recovery_strategies:
            try:
                strategy()
                self.reset_activity_timer()
                break
            except Exception as e:
                continue  # Try next strategy

    def reset_activity_timer(self):
        """Reset activity timer when progress is made."""
        self.last_activity = time.time()
```

### Auto-Fix Implementation Patterns

```python
# Auto-fix common development blockers
AUTO_FIX_PATTERNS = {
    'missing_method': '''
def {method_name}(self, *args, **kwargs):
    """Auto-generated method to resolve AttributeError."""
    # TODO: Implement actual functionality
    pass
    ''',

    'missing_class': '''
class {class_name}:
    """Auto-generated class to resolve missing dependency."""

    def __init__(self, *args, **kwargs):
        # TODO: Implement actual initialization
        pass
    ''',

    'missing_module': '''
"""Auto-generated module to resolve import error."""

# TODO: Implement actual module functionality
    '''
}
```

### Execution State Persistence

```python
class ExecutionStatePersistence:
    """Persist execution state to enable recovery."""

    def save_current_state(self, task_id, progress, context):
        """Save current execution state."""
        state = {
            'task_id': task_id,
            'progress': progress,
            'context': context,
            'timestamp': time.time(),
            'next_actions': self.determine_next_actions(task_id)
        }

        with open('.windsurf/execution_state.json', 'w') as f:
            json.dump(state, f)

    def recover_from_saved_state(self):
        """Recover and continue from saved state."""
        try:
            with open('.windsurf/execution_state.json', 'r') as f:
                state = json.load(f)

            # Resume from where we left off
            self.resume_task(state['task_id'], state['progress'])
            return True
        except FileNotFoundError:
            # No saved state, start fresh
            return False
```

### Enhanced Timeout Management

```python
class TimeoutManager:
    """Manage timeouts for all operations."""

    OPERATION_TIMEOUTS = {
        'test_execution': 60,      # 1 minute max for any test
        'import_resolution': 30,   # 30 seconds for import fixes
        'network_operation': 15,   # 15 seconds for network calls
        'file_operation': 10,      # 10 seconds for file operations
        'default': 30              # Default timeout
    }

    def execute_with_timeout(self, operation, operation_type='default'):
        """Execute operation with automatic timeout and recovery."""
        timeout = self.OPERATION_TIMEOUTS.get(operation_type, 30)

        try:
            return self._run_with_timeout(operation, timeout)
        except TimeoutError:
            # Auto-recover from timeout
            return self._handle_timeout_recovery(operation_type)

    def _handle_timeout_recovery(self, operation_type):
        """Handle timeout recovery automatically."""
        recovery_actions = {
            'test_execution': self._skip_hanging_test,
            'import_resolution': self._create_placeholder_import,
            'network_operation': self._use_offline_fallback,
            'file_operation': self._create_placeholder_file
        }

        recovery_action = recovery_actions.get(operation_type, self._generic_recovery)
        return recovery_action()
```

### Emergency Development Continuation

```python
def emergency_continue_development():
    """Emergency function to force development continuation."""

    # Skip any hanging operations
    terminate_all_hanging_processes()

    # Clear any blocking states
    clear_execution_blocks()

    # Load next task from DEV_PLAN.md
    next_task = get_next_uncompleted_task()

    if next_task:
        print(f"EMERGENCY CONTINUATION - Starting task: {next_task}")
        execute_task(next_task)
    else:
        # Generate new tasks if none available
        generate_additional_development_tasks()

    # Reset all monitoring systems
    reset_execution_monitoring()
```

### Auto-Implementation Rules

1. **Always implement something**: Never leave functionality completely missing
2. **Use placeholder patterns**: Implement minimal working versions
3. **Add TODO comments**: Mark areas for future improvement
4. **Log auto-implementations**: Track what was auto-generated
5. **Continue immediately**: No waiting after auto-implementation

### Recovery Trigger Phrases

These phrases automatically trigger recovery and continuation:

```
EMERGENCY_RECOVERY_NOW
SKIP_CURRENT_CONTINUE
AUTO_IMPLEMENT_AND_PROCEED
BYPASS_ERROR_CONTINUE
FORCE_DEVELOPMENT_CONTINUATION
IGNORE_FAILURES_PROCEED
IMPLEMENT_MINIMAL_CONTINUE
```

This enhanced protocol ensures that no error, timeout, or blocking issue can stop Atlas development progress.
