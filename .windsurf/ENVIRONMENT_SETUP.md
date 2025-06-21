# WINDSURF DEVELOPMENT ENVIRONMENT SETUP
# ⚠️ HIGHEST PRIORITY INSTRUCTION - EXECUTE FIRST ⚠️

## Critical Environment Setup Protocol

Before starting any Atlas development task, Windsurf AI MUST configure the appropriate development environment. Follow this protocol exactly:

### 1. Environment Activation (REQUIRED)

```bash
# On macOS:
source scripts/use_macos.sh

# On Linux:
source scripts/use_linux.sh
```

### 2. Environment Verification (REQUIRED)

```bash
# Verify all dependencies are installed:
./scripts/sync_requirements.sh
```

### 3. Development Tools Access (REQUIRED)

The following tools MUST be accessible for quality assurance:

- **Linting**: `python -m ruff check .`
- **Type Checking**: `python -m mypy .`
- **Testing**: `python -m pytest`
- **Security Scanning**: `python -m bandit -r .`
- **IDE Integration**: `jedi-language-server` (for code completion)

### 4. IDE Integration Issues (IF APPLICABLE)

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
   
## Platform-Specific Development Standards

### macOS (Python 3.13)
- **Virtual Environment**: `venv-macos`
- **Requirements**: `requirements-macos.txt`
- **Native Features**: Use pyobjc frameworks

### Linux (Python 3.12)
- **Virtual Environment**: `venv-linux`
- **Requirements**: `requirements-linux.txt`
- **Headless Testing**: Support operation without GUI

## Development Best Practices

1. **Platform Detection**:
   ```python
   from utils.platform_utils import IS_MACOS, IS_LINUX, IS_HEADLESS
   ```

2. **Quality Enforcement**:
   - Run pre-commit hooks: `pre-commit run --all-files`
   - Fix linting issues: `python -m ruff check --fix .`

3. **Documentation Updates**:
   - Update CHANGELOG.md for significant changes
   - Follow requirements in DEV_PLAN.md

## Windsurf Protocol Compliance

This environment setup protocol is mandatory and has the HIGHEST PRIORITY under Windsurf's "Never-Stop Execution" and "Quality Excellence" principles. Failure to execute this protocol before development will result in inconsistent code quality and potential cross-platform compatibility issues.

# END OF HIGHEST PRIORITY INSTRUCTION
