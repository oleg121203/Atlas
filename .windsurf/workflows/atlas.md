---
description: A comprehensive workflow for Atlas development on macOS Apple Silicon, focusing on optimized performance, language standards, and autonomous error recovery.
---

# Atlas Development Workflow

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

1. **Continuous Progress**: Complete tasks sequentially without interruption
2. **Quality Assurance**: Run tests and linting before committing changes
3. **Memory Optimization**: Leverage M1 Max unified memory architecture
4. **Performance**: Monitor resource usage and optimize for Apple Silicon
5. **Error Recovery**: Implement automatic error detection and recovery

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

This workflow ensures consistent, high-quality development for Atlas on the Mac Studio M1 Max platform.