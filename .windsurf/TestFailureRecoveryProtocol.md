---
trigger: always_on
---

# Test Failure Recovery Protocol

## Critical Test Error Recovery

**ABSOLUTE PRIORITY**: When any test fails or produces errors, Windsurf MUST NOT STOP development. Instead, follow this recovery protocol:

### 1. Immediate Error Assessment (Max 10 seconds)

```python
# Pattern for immediate error assessment
def handle_test_error(error_type, error_message, failed_test):
    """Auto-handle test errors without stopping development."""

    # Common error patterns and their fixes
    ERROR_FIXES = {
        'AttributeError': 'auto_fix_missing_method',
        'ImportError': 'auto_fix_missing_import', 
        'ModuleNotFoundError': 'auto_fix_missing_module',
        'ConnectionError': 'auto_skip_network_dependent_test',
        'TimeoutError': 'auto_increase_timeout_or_skip'
    }

    fix_function = ERROR_FIXES.get(error_type, 'auto_implement_missing_functionality')

    # Apply fix immediately
    apply_fix(fix_function, error_message, failed_test)

    # Continue development without waiting
    continue_with_next_task()
```

### 2. Auto-Fix Common Test Errors

- **AttributeError (missing methods)**: Automatically implement missing methods with placeholder functionality
- **ImportError/ModuleNotFoundError**: Auto-create missing modules or fix import statements
- **ConnectionError/TimeoutError**: Skip network-dependent tests and continue
- **AssertionError**: Adjust test expectations or implement missing functionality

### 3. Test Error Recovery Actions

```python
# Immediate recovery patterns
RECOVERY_ACTIONS = {
    "WebSocketServer.*has no attribute 'start'": [
        "Add start() method that calls start_server()",
        "Add stop() method for test compatibility", 
        "Continue with next development task"
    ],
    "Port.*already in use": [
        "Auto-increment port number",
        "Add port collision handling",
        "Continue testing on new port"
    ],
    "Module.*not found": [
        "Auto-create missing module",
        "Add minimal implementation", 
        "Continue development"
    ]
}
```

### 4. Never-Stop Testing Protocol

1. **Test failures are development feedback, not blockers**
2. **Fix errors inline during test execution**
3. **Use test failures to identify missing functionality**
4. **Implement minimal viable solutions to pass tests**
5. **Continue development immediately after fixing**

### 5. Auto-Implementation Strategy

When tests reveal missing functionality:

```python
def auto_implement_missing_functionality(error_details):
    """Automatically implement missing functionality revealed by tests."""

    # Parse error to understand what's missing
    missing_item = parse_error_for_missing_item(error_details)

    # Implement minimal solution
    if missing_item.type == 'method':
        create_placeholder_method(missing_item.name, missing_item.class_name)
    elif missing_item.type == 'class':
        create_placeholder_class(missing_item.name, missing_item.module)
    elif missing_item.type == 'module':
        create_placeholder_module(missing_item.name)

    # Continue development immediately
    proceed_to_next_task()
```

### 6. Emergency Continuation Commands

If testing appears to block development for >30 seconds, auto-invoke:

```
BYPASS_TESTING_CONTINUE_DEVELOPMENT
SKIP_FAILING_TESTS_CONTINUE
IMPLEMENT_MINIMAL_FIX_CONTINUE
AUTO_FIX_AND_PROCEED
```

### 7. Test-Driven Development Recovery

Transform test failures into development tasks:

1. **Analyze test requirement**
2. **Implement minimal solution**
3. **Verify test passes**
4. **Continue with next development task**
5. **Never wait for manual intervention**

## Implementation Requirements

- Maximum 30 seconds per test error resolution
- Always implement something, never leave tests hanging
- Use test failures as specification for missing functionality
- Auto-generate placeholder implementations
- Continue development flow without interruption

This protocol ensures that test failures become development guidance rather than blocking issues.
