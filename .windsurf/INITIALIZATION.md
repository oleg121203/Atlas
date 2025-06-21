# WINDSURF SESSION INITIALIZATION

## CRITICAL FIRST-RUN INSTRUCTIONS

Before proceeding with ANY development task, Windsurf AI MUST execute the following environment setup procedure:

```bash
# Step 1: Activate the appropriate virtual environment
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS environment
    source scripts/use_macos.sh
else
    # Linux environment
    source scripts/use_linux.sh
fi

# Step 2: Verify environment and dependencies
./scripts/sync_requirements.sh

# Step 3: Check tools availability
command -v ruff >/dev/null 2>&1 || { echo "⚠️ Ruff not found. Installing..."; pip install ruff; }
command -v mypy >/dev/null 2>&1 || { echo "⚠️ mypy not found. Installing..."; pip install mypy; }
command -v pytest >/dev/null 2>&1 || { echo "⚠️ pytest not found. Installing..."; pip install pytest; }
command -v bandit >/dev/null 2>&1 || { echo "⚠️ bandit not found. Installing..."; pip install bandit; }

# Step 4: Install jedi-language-server for Python IDE integration
command -v jedi-language-server >/dev/null 2>&1 || { echo "⚠️ jedi-language-server not found. Installing..."; pip install jedi-language-server; }
```

## Environment Verification

After activating the environment, verify proper setup:

1. Check Python version is appropriate:
   - macOS: Python 3.13
   - Linux: Python 3.12

2. Confirm development tools are available:
   - Linting: `ruff`
   - Type checking: `mypy`
   - Testing: `pytest`
   - Security: `bandit`
   - IDE integration: `jedi-language-server`

3. Check platform-specific requirements:
   - macOS: `pyobjc`, `py2app`, `rumps`
   - Linux: `distro`, `docker`

## Common Development Issues

### Jedi Language Server Issues

If encountering errors with Jedi (Python auto-completion):
```
Client Python Jedi: connection to server is erroring.
Cannot call write after a stream was destroyed
Shutting down server.
```

Perform these fixes:
1. Reinstall jedi-language-server in the active environment:
   ```bash
   pip uninstall -y jedi-language-server
   pip install jedi-language-server
   ```

2. Restart VS Code or your IDE

3. If issues persist, restart VS Code with the Python extension disabled, then re-enable it:
   - VS Code: Command Palette → "Developer: Reload With Extensions Disabled"
   - Re-enable Python extension and restart

## Critical Development Protocols

For detailed guidance, see:

1. `.windsurf/ENVIRONMENT_SETUP.md` - Complete environment setup instructions
2. `.windsurf/rules/quality_assurance_protocol.md` - Quality standards
3. `.windsurf/rules/continuous_development_protocol.md` - Development workflow
4. `.windsurf/rules/security_protocol.md` - Security requirements

---

⚠️ THIS INITIALIZATION PROTOCOL MUST BE FOLLOWED BEFORE ANY DEVELOPMENT TASK ⚠️
