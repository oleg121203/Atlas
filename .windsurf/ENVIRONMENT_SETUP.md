# WINDSURF DEVELOPMENT ENVIRONMENT SETUP
# ⚠️ HIGHEST PRIORITY INSTRUCTION - EXECUTE FIRST ⚠️

## Critical Environment Setup Protocol - macOS Mac Studio M1 Max 32GB ONLY

Before starting any Atlas development task, Windsurf AI MUST configure the macOS development environment. Follow this protocol exactly:

### 1. Environment Activation (REQUIRED - macOS ONLY)

```bash
# macOS Mac Studio M1 Max environment ONLY:
source scripts/use_macos.sh

# Verify we're on Apple Silicon Mac:
uname -m  # Should output: arm64
system_profiler SPHardwareDataType | grep "Mac Studio"
```

### 2. Environment Verification (REQUIRED)

```bash
# Verify all dependencies are installed:
./scripts/sync_requirements.sh

# Verify Python 3.9.6 on Apple Silicon:
python3 --version  # Must be Python 3.9.6
python3 -c "import platform; print(f'Architecture: {platform.machine()}')"  # Must be arm64
```

### 3. Development Tools Access (REQUIRED)

The following tools MUST be accessible for quality assurance:

- **Linting**: `python -m ruff check .`
- **Type Checking**: `python -m mypy .`
- **Testing**: `python -m pytest`
- **Security Scanning**: `python -m bandit -r .`
- **IDE Integration**: `jedi-language-server` (for code completion)

### 4. macOS Native Integration (REQUIRED)

```bash
# Install macOS-specific dependencies:
pip install pyobjc-framework-Cocoa
pip install py2app
pip install rumps

# Verify macOS frameworks access:
python3 -c "import Cocoa; print('✅ Cocoa framework OK')"
python3 -c "import Foundation; print('✅ Foundation framework OK')"
```

### 5. IDE Integration Issues (IF APPLICABLE)

If Python code completion issues occur (Jedi errors):

```bash
# Fix Jedi Language Server issues:
./scripts/fix_jedi.sh
```

## Troubleshooting Guide

If environment issues are detected:

1. **Missing Dependencies**:
   ```bash
   ./scripts/install_requirements.sh
   ```
   Select option 2 (Core + development tools)

2. **Incorrect Virtual Environment**:
   ```bash
   # Check current environment:
   echo $VIRTUAL_ENV
   
   # If incorrect, activate proper environment:
   source scripts/use_macos.sh  # macOS
   source scripts/use_linux.sh  # Linux
   ```

3. **Environment Migration**:
   If using non-standard environment:
   ```bash
   ./scripts/migrate_venv.sh <current_venv_path>
   ```

4. **IDE Integration Issues**:
   If Jedi errors appear in VS Code:
   ```bash
   ./scripts/fix_jedi.sh
   ```
   
## Platform-Specific Development Standards - macOS Mac Studio M1 Max 32GB

### macOS Development Environment
- **Hardware**: Mac Studio M1 Max 32GB RAM
- **Architecture**: Apple Silicon (arm64)
- **Python Version**: 3.9.6
- **Virtual Environment**: `venv-macos`
- **Requirements**: `requirements-macos.txt`
- **Native Features**: Full pyobjc frameworks integration
- **Memory**: Optimized for 32GB unified memory
- **Performance**: Leverage Apple Silicon acceleration

## Development Best Practices

1. **Platform Detection** (macOS only):
   ```python
   import platform
   assert platform.system() == 'Darwin'
   assert platform.machine() == 'arm64'

   from utils.platform_utils import IS_MACOS
   assert IS_MACOS == True
   ```

2. **Quality Enforcement**:
   - Run pre-commit hooks: `pre-commit run --all-files`
   - Fix linting issues: `python -m ruff check --fix .`

3. **Documentation Updates**:
   - Update CHANGELOG.md for significant changes
   - Follow requirements in DEV_PLAN.md

## Multilingual Support Protocol

### Language Requirements
- **Development Language**: English (code, comments, commit messages)
- **UI Support**: Ukrainian, Russian, English
- **Documentation**: Ukrainian primary, English secondary

### Code Language Standards
```python
# ✅ CORRECT - All code in English
class TaskManager:
    """Task management system for Atlas."""

    def create_task(self, title: str, description: str) -> Task:
        """Create new task with given parameters."""
        pass

# ❌ INCORRECT - Mixed languages in code
class УправлінняЗавданнями:  # Wrong - use English
    def створити_завдання(self):  # Wrong - use English
        pass
```

### UI Localization Standards
```python
# ✅ CORRECT - Multilingual UI support
TRANSLATIONS = {
    'en': {
        'create_task': 'Create Task',
        'task_title': 'Task Title'
    },
    'uk': {
        'create_task': 'Створити завдання',
        'task_title': 'Назва завдання'
    },
    'ru': {
        'create_task': 'Создать задачу', 
        'task_title': 'Название задачи'
    }
}
```

## Windsurf Protocol Compliance

This environment setup protocol is mandatory and has the HIGHEST PRIORITY under Windsurf's "Never-Stop Execution" and "Quality Excellence" principles. 

**CRITICAL**: Development is EXCLUSIVELY for macOS Mac Studio M1 Max 32GB. No cross-platform support needed.

# END OF HIGHEST PRIORITY INSTRUCTION
