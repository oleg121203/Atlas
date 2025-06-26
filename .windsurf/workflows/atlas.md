---
description: A comprehensive workflow for Atlas development on macOS Apple Silicon, focusing on optimized performance, language standards, and autonomous error recovery.
---
# Atlas Development Workflow

This workflow outlines the steps for developing the Atlas project on macOS Apple Silicon, ensuring optimized performance, adherence to language standards, and autonomous error recovery as per the Continuous Development Protocol.

## Target Platform

Atlas is exclusively developed and optimized for:
- **Hardware**: Mac Studio M1 Max with 32GB unified memory
- **Operating System**: macOS
- **Architecture**: ARM64 (Apple Silicon)
- **Python Version**: 3.13.x

## Development Rules

### Environment Setup

Before starting development:

1. Verify macOS Apple Silicon environment:
   ```bash
   # Verify Apple Silicon
   if [[ "$(uname -m)" != "arm64" ]]; then
       echo "❌ ERROR: Must run on Apple Silicon Mac"
       exit 1
   fi

   # Configure Python environment
   export ARCHFLAGS="-arch arm64"
   export _PYTHON_HOST_PLATFORM="macosx-11.0-arm64"
   alias pip='arch -arm64 pip'
   ```

2. Ensure Python 3.13.x is active and properly configured:
   ```bash
   python --version  # Must be Python 3.13.x
   python -c "import platform; assert platform.machine() == 'arm64'"
   ```

### Code Standards

1. **English-Only Code**: All code, comments, and documentation must be in English
   ```python
   # ✅ CORRECT
   def process_task(task_id: str) -> Task:
       """Process the task with the given ID."""
       return Task(task_id)
   ```

2. **Multilingual UI**: User interface must support all three languages:
   - Ukrainian (default)
   - Russian
   - English

   ```python
   UI_STRINGS = {
       'task_create': {
           'uk': 'Створити завдання',
           'ru': 'Создать задачу', 
           'en': 'Create Task'
       }
   }
   ```

### Development Workflow

1. **Environment Setup**
   - Ensure the development environment is set up according to `.windsurf/ENVIRONMENT_SETUP.md`. This includes using macOS on Mac Studio M1 Max with 32GB unified memory, Python 3.13.x (ARM64 native), and the `venv-macos` virtual environment.
   - Activate the virtual environment: `source venv-macos/bin/activate`.

2. **Review DEV_PLAN.md**
   - Open and review `DEV_PLAN.md` to identify the next uncompleted task or phase. Focus on tasks marked as 'Not Started' or 'In Progress'.
   - If no immediate tasks are available, perform a retrospective and expand the plan with the next logical milestones.

3. **Code Development**
   - **Implement Features**: Based on the current task in `DEV_PLAN.md`, develop the required feature or fix. Ensure all code adheres to English-only standards for code, comments, and documentation.
   - **Optimize for macOS**: Leverage native macOS frameworks like PyObjC, Metal, and CoreML for performance optimization on Apple Silicon.
   - **Autonomous Decision-Making**: Make necessary development decisions without user input, using best practices and existing patterns in the codebase.

4. **Quality Assurance**
   - **Linting**: Run `ruff` and `mypy` to ensure code quality before committing.
   - **Testing**: Write and run PyTest cases for new modules, ensuring coverage of core logic. Maintain ≥90% statement coverage.
   - **Documentation**: Add Google-style docstrings for all public functions.
   - **Performance**: Measure latency for tools manipulating screen or input (<100ms), planning operations (<500ms), and memory operations (<200ms). Log performance metrics.

5. **Error Recovery and Continuation**
   - **Auto-Error-Recovery**: If errors occur (e.g., AttributeError, ImportError, test failures), automatically implement fixes inline without stopping. For example, create missing methods or modules as needed.
   - **Test-Failure-Continuation**: When tests fail, auto-implement missing functionality and continue development.
   - **Automatic Context Switching**: If a task path is blocked, immediately switch to the next available task without waiting.

6. **Security and Compliance**
   - **Credential Management**: Use environment variables for API keys and sensitive data, never commit them to code.
   - **Input Validation**: Sanitize all external inputs to prevent injection attacks.
   - **Encryption**: Use AES-256 for sensitive data storage.

7. **Progress Updates**
   - **Update DEV_PLAN.md**: After completing a task, mark the relevant checkbox in `DEV_PLAN.md`.
   - **Batch Documentation**: Skip changelog updates during active development, batch them at phase completion unless explicitly requested.
   - **Minimal Reporting**: Only report completion of major milestones or phases, skip intermediate task reporting.

8. **Continuous Execution**
   - **Never-Stop Mandate**: Continue development without any pauses until all tasks in `DEV_PLAN.md` are completed, regardless of errors or unclear requirements.
   - **Auto-Proceed**: Immediately execute the next task after current completion or error resolution without confirmation.
   - **Unstoppable Execution Guarantee**: If development stalls for any reason, auto-resume within 30 seconds using the next logical task.

9. **Performance Degradation Handling**
   - If performance degradation is detected, switch to fallback implementations, log detailed diagnostics, continue with a reduced feature set, and auto-generate optimization tasks in `DEV_PLAN.md`.

10. **CI Pipeline and Dependency Management**
    - Ensure an automated CI pipeline (e.g., GitHub Actions) runs `ruff`, `mypy`, and the full test suite, blocking merges on failures or performance regressions.
    - Enable dependency-update automation (e.g., Renovate or Dependabot) with automatic PRs for patched versions, ensuring CI passes before merge.
    - Configure vulnerability scanning and secret detection (e.g., Trivy and Gitleaks) on every push, failing the pipeline on critical findings.

11. **Multilingual UI Support**
    - While code must be in English, ensure the UI supports Ukrainian, Russian, and English languages. Validate UI language files against injection attacks.

12. **Commit and Logging**
    - Commit small, logical code increments with descriptive messages in English.
    - Batch progress updates, logging significant milestones only, not every small task.
    - Log execution metrics every 10 minutes and auto-diagnose if any operation exceeds 2x target latency.

13. **Emergency Override**
    - Use the emergency override code `EXECUTE_UNTIL_COMPLETE_47` to force continuous execution regardless of other protocols if needed.

### Quality Gates

- Code must pass `ruff check` before commit
- Type checking with `mypy` must pass
- All tests must pass before moving to next task
- Documentation must be updated for architectural changes

## Default Implementation Patterns

### Module Structure
```
/modules/{module_name}/
├── __init__.py          # Export main classes
├── {module_name}.py     # Main module class  
├── config.py            # Module configuration
├── models.py            # Data models
└── tests/               # Module tests
```

### Plugin Structure
```
/plugins/{plugin_name}/
├── __init__.py          # Plugin registration
├── plugin.py            # Main plugin class
├── config.py            # Plugin configuration
└── README.md            # Plugin documentation
```

### Security Protocols

1. Never commit API keys or credentials
2. Validate all user inputs
3. Use secure coding practices
4. Implement proper authentication for privileged operations

## Autonomous Error Recovery

Implement automatic recovery for common issues:
- Memory optimization issues
- Import and dependency errors
- GUI rendering problems
- Plugin loading failures

This workflow ensures continuous development without pauses, adhering to the ABSOLUTE NEVER-STOP MANDATE until all tasks are completed.