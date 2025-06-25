## WINDSURF AUTONOMOUS DEVELOPMENT PROTOCOL

### Critical Rules for Windsurf AI
1. **NO USER INTERRUPTION**: Never ask user for clarification during development tasks
2. **CONTINUOUS EXECUTION**: Always proceed with the most logical next step
3. **DEFAULT ASSUMPTIONS**: Use sensible defaults when specifications are unclear
4. **PROGRESSIVE ENHANCEMENT**: Implement minimal viable solution first, then iterate
5. **ERROR RECOVERY**: Automatically attempt fixes for common issues before reporting

### Autonomous Decision Framework
When encountering ambiguous requirements:
- **Priority 1**: Follow established patterns in existing codebase
- **Priority 2**: Use industry best practices for Python/Qt applications
- **Priority 3**: Implement the simplest solution that meets the requirement
- **Priority 4**: Document assumptions made in commit messages

### Default Configuration Values
```yaml
# Use these defaults when configuration is unclear
development:
  environment: "venv-macos" if macOS else "venv-linux"
  python_version: "3.13" if macOS else "3.12"
  testing: pytest
  linting: ruff + mypy
  ui_framework: PySide6
  
architecture:
  module_pattern: "/modules/{module_name}/"
  plugin_pattern: "/plugins/{plugin_name}/"
  config_location: "/core/config.py"
  main_app: "/core/application.py"
```
