# Atlas Development Tools Guide

This document provides a comprehensive overview of the development tools and utilities used in the Atlas project.

## Core Development Tools

### Linting and Code Quality

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **Ruff** | Fast Python linter | `pyproject.toml` and `.ruff.toml` | `python -m ruff check .` |
| **mypy** | Static type checking | `pyproject.toml` | `python -m mypy .` |
| **Black** | Code formatter | `pyproject.toml` | `python -m black .` |
| **isort** | Import sorter | `pyproject.toml` | `python -m isort .` |

### Testing

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **pytest** | Testing framework | `pytest.ini` | `python -m pytest` |
| **pytest-cov** | Test coverage | `pytest.ini` | `python -m pytest --cov=.` |
| **interrogate** | Docstring coverage | `pyproject.toml` | `interrogate -v .` |

### Security

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **safety** | Dependency security checker | N/A | `safety check` |
| **bandit** | Security linter | `.bandit` | `bandit -r .` |
| **gitleaks** | Secret scanning | `.gitleaks.toml` | `gitleaks detect` |

### Performance Profiling

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **py-spy** | Sampling profiler | N/A | `py-spy record -o profile.svg -- python your_script.py` |
| **line-profiler** | Line-by-line profiling | N/A | `kernprof -l -v your_script.py` |

## Project Management Tools

### Version Control Hooks

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **pre-commit** | Git hook manager | `.pre-commit-config.yaml` | `pre-commit run --all-files` |

### CI/CD Pipeline

| Tool | Description | Configuration | Usage |
|------|-------------|--------------|-------|
| **GitHub Actions** | CI/CD automation | `.github/workflows/ci.yml` | Automatic on push |
| **Dependabot** | Dependency updates | `.github/dependabot.yml` | Automatic |

## Atlas-Specific Tools

### Windsurf Protocol Tools

| Tool | Description | Location | Usage |
|------|-------------|----------|-------|
| **setup_windsurf_protocols.sh** | Setup Windsurf protocols | `/` | `./setup_windsurf_protocols.sh` |
| **verify_setup.sh** | Verify protocol setup | `/` | `./verify_setup.sh` |
| **validate_atlas_setup.sh** | Validate Atlas setup | `/` | `./validate_atlas_setup.sh` |

### Development Utilities

| Tool | Description | Location | Usage |
|------|-------------|----------|-------|
| **check_file_structure.py** | Check project structure | `dev-tools/` | `python dev-tools/check_file_structure.py` |
| **check_quality.sh** | Check code quality | `dev-tools/` | `./dev-tools/check_quality.sh` |
| **diagnose_atlas.py** | Diagnose Atlas issues | `dev-tools/` | `python dev-tools/diagnose_atlas.py` |
| **analyze_performance.py** | Analyze performance | `dev-tools/` | `python dev-tools/analyze_performance.py` |
| **generate_docs.py** | Generate documentation | `dev-tools/` | `python dev-tools/generate_docs.py` |
| **sync_requirements.sh** | Sync requirement files | `scripts/` | `./scripts/sync_requirements.sh` |

## Platform-Specific Tools

### Linux Development

| Tool | Description | Usage |
|------|-------------|-------|
| **Docker** | Containerization | `docker-compose up` |
| **GitHub Codespaces** | Cloud development | Access via GitHub |

### macOS Development

| Tool | Description | Usage |
|------|-------------|-------|
| **py2app** | macOS app bundling | `python setup.py py2app` |
| **launch_macos.sh** | Launch macOS app | `./launch_macos.sh` |

## Tool Installation

To install all development tools:

```bash
# Install core development dependencies
pip install -r requirements-dev.txt

# Install platform-specific dependencies
# For Linux:
pip install -r requirements-linux.txt

# For macOS:
pip install -r requirements-macos.txt

# Install pre-commit hooks
pre-commit install
```

## Windsurf Protocol Compliance

The Windsurf protocols mandate specific tools for quality assurance, continuous development, and security. These requirements are reflected in the tools listed above and their configurations.

### Quality Assurance Protocol Requirements

- Linting: Ruff and mypy
- Testing: pytest with coverage
- Documentation: Google-style docstrings
- Code coverage: Minimum 90% statement coverage
- Docstring coverage: Minimum 85% public-API coverage

### Continuous Development Protocol Requirements

- CI/CD: GitHub Actions
- Dependency updates: Dependabot
- Security scanning: gitleaks and Trivy

### Security Protocol Requirements

- Credential management: Environment variables
- Dependency security: safety check
- Regular audits: Weekly security scans

## Adding New Tools

When adding new development tools to the Atlas project:

1. Add the tool to the appropriate requirements file:
   - `requirements-dev.txt` for development tools
   - `requirements-linux.txt` or `requirements-macos.txt` for platform-specific tools
2. Document the tool in this guide
3. Configure the tool in the appropriate configuration file
4. Update the CI pipeline if necessary
5. Update the Windsurf protocols if the tool affects compliance

## More Information

For more details on development protocols and standards, see:

- `.windsurf/rules/quality_assurance_protocol.md`
- `.windsurf/rules/continuous_development_protocol.md`
- `.windsurf/rules/security_protocol.md`
- `ORGANIZATION.md`
- `LINTING.md`

## Superhuman Tools

### CreativeTool
- **Purpose:** Chain other tools in creative ways to solve complex or open-ended tasks.
- **Capabilities:** chain_tools, creative_workflows
- **Example Workflow:** Screenshot → OCR → Translate → Search

### ProactiveTool
- **Purpose:** Monitor for triggers (e.g., repeated actions, idle time) and suggest or launch automations.
- **Capabilities:** monitor_triggers, suggest_automations, auto_launch
- **Example Workflow:** Detects user idle for 5 seconds, suggests automating a repeated task.

### PlayfulTool
- **Purpose:** Gamify routine tasks or add creative, playful outputs.
- **Capabilities:** gamify_tasks, creative_outputs
- **Example Workflow:** Inbox Zero Challenge – turns email cleanup into a game.

## Superhuman Workflows (Demo Scenarios)

- **Automated Multistep Task:**
    - User clicks 'Screenshot → OCR → Translate' in the UI.
    - Atlas takes a screenshot, extracts text, translates it, and displays the result.

- **Proactive Automation:**
    - Atlas detects the user is idle for 10 seconds.
    - Suggests automating the last repeated action (e.g., opening three apps together).

- **Gamified Productivity:**
    - User launches 'Inbox Zero Challenge'.
    - Atlas tracks email cleanup progress and celebrates when the inbox is empty.

- **Custom Tool Chain:**
    - User opens the Custom Tool Chain Composer.
    - Builds a chain: Download file → Extract text → Summarize → Email summary.
    - Atlas executes the chain and reports results.
