---
description: A comprehensive workflow for Atlas development on macOS Apple Silicon, focusing on optimized performance, language standards, and autonomous error recovery.
---

# Atlas Development Workflow

This workflow outlines the steps for developing the Atlas project, ensuring continuous development, adherence to quality and security standards, and autonomous error recovery.

## Target Platform

Atlas is exclusively developed and optimized for:
- **Hardware**: Mac Studio M1 Max with 32GB unified memory
- **Operating System**: macOS
- **Architecture**: ARM64 (Apple Silicon)
- **Python Version**: 3.9.6

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

2. Ensure Python 3.9.6 is active and properly configured:
   ```bash
   python --version  # Must be Python 3.9.6
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
   - Ensure the development environment is set up according to `.windsurf/ENVIRONMENT_SETUP.md`.
   - Verify that all necessary tools and dependencies are installed for macOS Apple Silicon (M1 Max 32GB).
   - Use Python 3.9.6 (ARM64 native) within the `venv-macos` virtual environment.

2. **Review Current Tasks**
   - Open and review `DEV_PLAN.md` to identify the next uncompleted task under the current phase.
   - Prioritize tasks based on dependencies and estimated time, focusing on high-priority items.

3. **Code Development**
   - Create or modify necessary files to implement the selected task.
   - Follow English-only code and documentation standards as per the protocol.
   - Ensure code is optimized for macOS Apple Silicon hardware.
   - Implement multilingual UI support (Ukrainian, Russian, English) where applicable.

4. **Quality Assurance**
   - Write unit tests using PyTest to cover core logic of new modules.
   - Run `ruff` and `mypy` for linting before committing code.
   - Ensure public functions have Google-style docstrings.
   - Verify performance requirements (e.g., screen/input tools <100ms latency).

5. **Error Recovery and Continuation**
   - If errors occur (e.g., AttributeError, ImportError), auto-implement fixes inline without stopping.
   - For test failures, implement missing functionality and continue development.
   - Switch to the next available task if the current path is blocked, adhering to the NEVER-STOP MANDATE.

6. **Security Checks**
   - Use environment variables for credentials, never commit sensitive data.
   - Run `safety check` before adding new dependencies.
   - Sanitize all external inputs to prevent injection attacks.

7. **Documentation Updates**
   - Update `DEV_PLAN.md` to mark completed tasks with checkboxes.
   - Add detailed entries to `CHANGELOG.md` under *Unreleased* for each completed task.
   - Batch documentation updates at phase completion to avoid loops.

8. **Commit and Progress**
   - Commit small, logical code increments with descriptive messages in English.
   - Log progress in `CHANGELOG.md` at least every 30 minutes of active work.
   - If no immediate tasks remain, perform a retrospective and expand the plan with new milestones.

9. **Continuous Integration and Testing**
   - Ensure CI pipeline (GitHub Actions) runs `ruff`, `mypy`, and full test suite.
   - Maintain ≥90% test coverage; failing this blocks CI.
   - Continue testing even with minor issues, logging them separately without halting.

10. **Performance Optimization**
    - Monitor operation latencies and implement fallbacks for slow operations.
    - Auto-generate performance reports every 30 minutes.
    - Switch to fallback implementations on degradation, logging diagnostics.

11. **Autonomous Decision-Making**
    - Make development decisions without user input using best practices and existing patterns.
    - Auto-resume within 30 seconds if development stalls, selecting the next logical task.
    - Use `EXECUTE_UNTIL_COMPLETE_47` override code if needed to force continuous execution.

12. **Completion and Review**
    - Review completed phases and update `DEV_PLAN.md` with new phases if necessary.
    - Ensure all documentation and metrics are updated before moving to the next phase.
    - Self-review code diffs for quality control before major commits.

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