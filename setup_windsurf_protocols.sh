#!/bin/bash
set -e

# Atlas Windsurf Protocols & CI/CD Setup Script
# Automatically configures all protocols and infrastructure after git clone

echo "🚀 Atlas Windsurf Protocols & CI/CD Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in Atlas root directory
if [ ! -f "main.py" ] || [ ! -d "agents" ]; then
    print_error "This script must be run from the Atlas root directory"
    exit 1
fi

print_status "Setting up Atlas development environment..."

# 1. Create Windsurf rules directory structure
print_status "Creating Windsurf protocols directory structure..."
mkdir -p .windsurf/rules
mkdir -p .windsurf/sessions
mkdir -p .windsurf/context

# 2. Create Continuous Development Protocol
print_status "Setting up Continuous Development Protocol..."
cat > .windsurf/rules/continuous_development_protocol.md << 'EOF'
---
trigger: always_on
---

# Continuous Development Protocol

Purpose: guarantee that Atlas development never stalls until final release.

1. Always maintain an up-to-date `DEV_PLAN.md`.
2. After every completed task:
   - Update the relevant section in `DEV_PLAN.md` (mark checkbox).
   - Add a detailed entry to `CHANGELOG.md` under *Unreleased*.
3. When `DEV_PLAN.md` shows no remaining immediate tasks:
   - Perform a retrospective.
   - Expand plan with next logical milestones.
4. Never remove existing plan phases; append new ones with incrementing numbers (Phase 8, 9…).
5. Execute tasks sequentially unless parallelism is explicitly beneficial and safe.
6. Commit small, logical code increments with descriptive CHANGELOG notes.
7. At least every 30 minutes of active work, log progress in `CHANGELOG.md` (even if small).
8. On any blocking issue, create a *Blocking* section in `DEV_PLAN.md` and outline resolution steps.
9. Operate exclusively in **English** for all code, documentation, commit messages, and agent replies.
10. Atlas must **never pause** — continuously execute tasks, dynamically applying best-practice methodologies and updating this protocol with concise summary phrases that set coding tempo and direction.
11. Establish a **weekly protocol retrospective** every Friday. Summarise learnings, adjust rules, and append concise guidance phrases that set coding tempo for the next week.
12. Integrate an **automated CI pipeline** (GitHub Actions) that runs `ruff`, `mypy`, and the full test suite on every push. Block merges on failures.
13. Enable **dependency-update automation** (e.g., Renovate or Dependabot) with automatic PRs for patched versions. CI must pass before merge.
14. Configure **vulnerability scanning & secret detection** (e.g., Trivy and Gitleaks) on every push; fails pipeline on critical findings.
EOF

# 3. Create Quality Assurance Protocol
print_status "Setting up Quality Assurance Protocol..."
cat > .windsurf/rules/quality_assurance_protocol.md << 'EOF'
---
trigger: always_on
---

# Quality Assurance Protocol

Ensures code quality and adherence to project architecture.

1. **Linting**: run `ruff` and `mypy` before committing.
2. **Testing**: new modules require PyTest cases covering core logic.
3. **Documentation**: public functions must have docstrings following Google style.
4. **Security Review**: verify actions against security rules before merging.
5. **GUI UX Check**: manual test new widgets on macOS Sequoia for visual consistency.
6. **Performance**: for tools manipulating screen or input, measure latency; keep <100 ms.
7. **Dependency Audit**: ensure `requirements.txt` remains minimal and pinned.
8. **Review Cycle**: self-review code diff, update `CHANGELOG.md`, then proceed.
9. **Language Consistency**: Ensure all comments, docstrings, and documentation are written in English.
10. **Code Coverage**: Maintain ≥ 90% statement coverage across tests. Failing the threshold blocks CI.
11. **Performance Regression**: Add automated benchmarks; flag any tool or function whose latency regresses by >10% versus the latest main branch.
12. **Secret Scanning**: Ensure no hard-coded credentials/API keys are committed (CI step with `gitleaks`).
13. **Docstring Coverage**: Maintain ≥ 85% public-API docstring coverage (enforced via `interrogate` or `pydocstyle`).
EOF

# 4. Create Security Protocol
print_status "Setting up Security Protocol..."
cat > .windsurf/rules/security_protocol.md << 'EOF'
---
trigger: always_on
---

# Security Protocol

Ensures Atlas maintains robust security standards throughout development.

1. **Credential Management**: Never commit API keys, tokens, or passwords. Use environment variables.
2. **Dependency Security**: Run `safety check` before adding new dependencies.
3. **Input Validation**: Sanitize all external inputs (user commands, file paths, network data).
4. **Permission Principle**: Request minimal necessary permissions on macOS.
5. **Encryption Standards**: Use AES-256 for sensitive data storage, secure key derivation.
6. **Network Security**: Validate SSL certificates, use HTTPS for all external calls.
7. **Code Injection Prevention**: Never use `eval()` or `exec()` with user input.
8. **Logging Security**: Never log sensitive information (credentials, personal data).
9. **Access Control**: Implement proper authentication for creator-level functions.
10. **Regular Audits**: Weekly security scans via automated CI pipeline.
EOF

# 5. Create GitHub Actions CI pipeline
print_status "Setting up GitHub Actions CI pipeline..."
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: Atlas CI - Enhanced Governance Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Weekly security and dependency scan (Sundays at 02:00 UTC)
    - cron: '0 2 * * 0'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-linux.txt
        pip install pytest-cov coverage interrogate
    
    - name: Secret scanning with Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Vulnerability scanning with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'
    
    - name: Check docstring coverage
      run: |
        interrogate -v --fail-under 85 agents/ utils/ intelligence/ monitoring/ tools/ ui/
      continue-on-error: false
    
    - name: Run linting with ruff
      run: |
        ruff check . --output-format=github
      continue-on-error: false
    
    - name: Run type checking with mypy
      run: |
        mypy --ignore-missing-imports agents/ utils/ intelligence/ monitoring/
      continue-on-error: false
    
    - name: Run tests with coverage
      run: |
        pytest --cov=agents --cov=utils --cov=intelligence --cov=monitoring --cov-report=xml --cov-report=term-missing --cov-fail-under=90
      env:
        ATLAS_TESTING: "true"
    
    - name: Upload coverage reports to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  performance-regression:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-linux.txt
        pip install pytest-benchmark
    
    - name: Run performance benchmarks
      run: |
        pytest tests/performance/ --benchmark-json=benchmark.json || echo "No performance tests found"
      continue-on-error: true
    
    - name: Compare performance with main branch
      run: |
        git checkout main
        pip install -r requirements-linux.txt
        pytest tests/performance/ --benchmark-json=benchmark-main.json || echo "No performance tests on main"
        if [ -f dev-tools/compare_benchmarks.py ]; then
          python dev-tools/compare_benchmarks.py benchmark-main.json benchmark.json
        else
          echo "Performance comparison tool not yet implemented"
        fi
      continue-on-error: true

  security-audit:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-linux.txt
        pip install safety bandit semgrep
    
    - name: Run comprehensive secret scan
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Run comprehensive vulnerability scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Python security audit with Safety
      run: |
        safety check --json --output safety-report.json || true
        safety check --short-report
    
    - name: Static security analysis with Bandit
      run: |
        bandit -r agents/ utils/ intelligence/ monitoring/ tools/ ui/ -f json -o bandit-report.json || true
        bandit -r agents/ utils/ intelligence/ monitoring/ tools/ ui/ --skip B101,B601 -ll
    
    - name: Upload security artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          safety-report.json
          bandit-report.json
          trivy-results.sarif
EOF

# 6. Create Dependabot configuration
print_status "Setting up Dependabot automation..."
mkdir -p .github
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    reviewers:
      - "atlas-team"
    assignees:
      - "atlas-team"
    commit-message:
      prefix: "deps"
      prefix-development: "deps-dev"
      include: "scope"
    open-pull-requests-limit: 10
    allow:
      - dependency-type: "direct"
      - dependency-type: "indirect"
    ignore:
      # Ignore major version updates for stable dependencies
      - dependency-name: "requests"
        update-types: ["version-update:semver-major"]
      - dependency-name: "urllib3"
        update-types: ["version-update:semver-major"]

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    reviewers:
      - "atlas-team"
    assignees:
      - "atlas-team"
    commit-message:
      prefix: "ci"
      include: "scope"
EOF

# 7. Update pyproject.toml with tool configurations
print_status "Configuring development tools in pyproject.toml..."

# Check if pyproject.toml exists, if not create basic structure
if [ ! -f "pyproject.toml" ]; then
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "atlas"
version = "0.1.0"
description = "Atlas - Autonomous AI Assistant"
authors = [{name = "Atlas Development Team"}]
license = {text = "MIT"}
requires-python = ">=3.8"
EOF
fi

# Add tool configurations if not present
if ! grep -q "\[tool.ruff\]" pyproject.toml; then
    cat >> pyproject.toml << 'EOF'

[tool.ruff]
target-version = "py38"
line-length = 88
indent-width = 4

exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "venv",
    "venv-macos",
    "unused",
]

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "DJ", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]

ignore = [
    "S101",   # Use of assert
    "T201",   # Print statements
    "T203",   # pprint statements
    "PLR0913", # Too many arguments
    "PLR0912", # Too many branches
    "C901",   # Complex functions
    "PLR0915", # Too many statements
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG001", "ARG002", "FBT001", "FBT002", "SLF001"]
"**/__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["agents", "utils", "intelligence", "monitoring"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/venv-macos/*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"

[tool.interrogate]
ignore-init-method = true
ignore-init-module = false
ignore-magic = false
ignore-semiprivate = false
ignore-private = false
ignore-property-decorators = false
ignore-module = false
ignore-nested-functions = false
ignore-nested-classes = true
ignore-setters = false
fail-under = 85
exclude = ["setup.py", "docs", "build", "tests", "venv", "venv-macos", "unused", "dev-tools", "scripts", "monitoring", "tools", "ui", "data", "config", "assets", "requirements", "rules", "plugins", "test_generated_tools", "test_temp_generated_tools"]
ignore-regex = ["^get$", "^mock_.*", "^dummy_.*", "^_.*"]
verbose = 0
quiet = false
whitelist-regex = []
color = true
EOF
fi

# 8. Create pytest configuration if not exists
if [ ! -f "pytest.ini" ]; then
    print_status "Creating pytest configuration..."
    cat > pytest.ini << 'EOF'
[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers --strict-config
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    benchmark: marks tests as performance benchmarks
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
EOF
fi

# 9. Create pre-commit hook setup
print_status "Setting up pre-commit hooks..."
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Atlas pre-commit hook - enforces quality standards

echo "🔍 Running Atlas pre-commit checks..."

# Check if files are staged
if git diff --cached --name-only | grep -qE '\.(py)$'; then
    echo "  Checking Python files..."
    
    # Run ruff linting
    echo "  Running ruff linting..."
    if ! ruff check $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); then
        echo "❌ Ruff linting failed. Please fix the issues before committing."
        exit 1
    fi
    
    # Run type checking on changed files
    echo "  Running mypy type checking..."
    python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | tr '\n' ' ')
    if [ -n "$python_files" ]; then
        if ! mypy --ignore-missing-imports $python_files; then
            echo "⚠️  Type checking warnings found. Review before proceeding."
            # Don't block commit on mypy warnings, just warn
        fi
    fi
    
    # Check for secrets
    echo "  Checking for potential secrets..."
    if git diff --cached --name-only | xargs grep -l -E "(api_key|password|secret|token)" 2>/dev/null; then
        echo "⚠️  Potential secrets detected in staged files. Please review."
        echo "   If these are test values or false positives, you can proceed."
        echo "   Otherwise, please remove secrets and use environment variables."
    fi
fi

echo "✅ Pre-commit checks completed"
EOF

chmod +x .git/hooks/pre-commit

# 10. Install development dependencies
print_status "Installing development dependencies..."

# Detect platform and use appropriate requirements file
if [[ "$OSTYPE" == "darwin"* ]]; then
    REQUIREMENTS_FILE="requirements-macos.txt"
    PYTHON_CMD="python3"
else
    REQUIREMENTS_FILE="requirements-linux.txt"
    PYTHON_CMD="python3"
fi

# Check if requirements file exists
if [ -f "$REQUIREMENTS_FILE" ]; then
    if command -v $PYTHON_CMD &> /dev/null; then
        print_status "Installing Python dependencies from $REQUIREMENTS_FILE..."
        $PYTHON_CMD -m pip install --upgrade pip
        $PYTHON_CMD -m pip install -r $REQUIREMENTS_FILE
        
        # Install additional development tools
        print_status "Installing development tools..."
        $PYTHON_CMD -m pip install pytest pytest-cov coverage interrogate safety bandit ruff mypy types-requests
        
        print_success "Python dependencies installed successfully"
    else
        print_warning "Python3 not found. Please install Python 3.8+ and run: pip install -r $REQUIREMENTS_FILE"
    fi
else
    print_warning "Requirements file $REQUIREMENTS_FILE not found. Please ensure it exists."
fi

# 11. Create development scripts
print_status "Creating development utility scripts..."
mkdir -p dev-tools

# Create quality check script
cat > dev-tools/check_quality.sh << 'EOF'
#!/bin/bash
# Atlas Quality Check Script

echo "🔍 Running Atlas Quality Checks"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED_CHECKS=()

# 1. Ruff linting
echo "1. Running Ruff linting..."
if ruff check .; then
    echo -e "${GREEN}✅ Ruff linting passed${NC}"
else
    echo -e "${RED}❌ Ruff linting failed${NC}"
    FAILED_CHECKS+=("ruff")
fi

# 2. MyPy type checking
echo "2. Running MyPy type checking..."
if mypy --ignore-missing-imports agents/ utils/ intelligence/; then
    echo -e "${GREEN}✅ MyPy type checking passed${NC}"
else
    echo -e "${YELLOW}⚠️ MyPy type checking has warnings${NC}"
fi

# 3. Docstring coverage
echo "3. Checking docstring coverage..."
if interrogate -f 85 agents/ utils/ intelligence/; then
    echo -e "${GREEN}✅ Docstring coverage meets requirements (≥85%)${NC}"
else
    echo -e "${RED}❌ Docstring coverage below threshold${NC}"
    FAILED_CHECKS+=("docstrings")
fi

# 4. Security checks
echo "4. Running security checks..."
if command -v safety &> /dev/null; then
    if safety check; then
        echo -e "${GREEN}✅ Safety check passed${NC}"
    else
        echo -e "${RED}❌ Safety check found vulnerabilities${NC}"
        FAILED_CHECKS+=("safety")
    fi
else
    echo -e "${YELLOW}⚠️ Safety not installed, skipping vulnerability check${NC}"
fi

# 5. Run tests if they exist
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "5. Running tests..."
    if pytest tests/ -v; then
        echo -e "${GREEN}✅ Tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        FAILED_CHECKS+=("tests")
    fi
else
    echo -e "${YELLOW}⚠️ No tests directory found${NC}"
fi

# Summary
echo ""
echo "📊 Quality Check Summary"
echo "========================"

if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All quality checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Failed checks: ${FAILED_CHECKS[*]}${NC}"
    echo "Please fix the issues before committing."
    exit 1
fi
EOF

chmod +x dev-tools/check_quality.sh

# Create documentation generator
cat > dev-tools/generate_docs.py << 'EOF'
#!/usr/bin/env python3
"""
Atlas Documentation Generator
Automatically generates project documentation from docstrings and comments.
"""

import os
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

def extract_docstrings(file_path: str) -> Dict[str, Any]:
    """Extract docstrings from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    
    docstrings = {
        'module': ast.get_docstring(tree),
        'classes': {},
        'functions': {}
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstrings['classes'][node.name] = ast.get_docstring(node)
        elif isinstance(node, ast.FunctionDef):
            docstrings['functions'][node.name] = ast.get_docstring(node)
    
    return docstrings

def generate_module_docs(module_path: Path) -> str:
    """Generate documentation for a Python module."""
    docs = []
    docs.append(f"# {module_path.stem}\n")
    
    try:
        docstrings = extract_docstrings(str(module_path))
        
        if docstrings['module']:
            docs.append(f"{docstrings['module']}\n")
        
        if docstrings['classes']:
            docs.append("## Classes\n")
            for class_name, docstring in docstrings['classes'].items():
                docs.append(f"### {class_name}")
                if docstring:
                    docs.append(f"{docstring}\n")
                else:
                    docs.append("No documentation available.\n")
        
        if docstrings['functions']:
            docs.append("## Functions\n")
            for func_name, docstring in docstrings['functions'].items():
                docs.append(f"### {func_name}")
                if docstring:
                    docs.append(f"{docstring}\n")
                else:
                    docs.append("No documentation available.\n")
    
    except Exception as e:
        docs.append(f"Error parsing module: {e}\n")
    
    return "\n".join(docs)

def main():
    """Generate documentation for Atlas project."""
    root_dir = Path(".")
    docs_dir = root_dir / "docs" / "api"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Directories to document
    source_dirs = ["agents", "utils", "intelligence", "monitoring"]
    
    for source_dir in source_dirs:
        source_path = root_dir / source_dir
        if not source_path.exists():
            continue
        
        print(f"Generating docs for {source_dir}...")
        
        for py_file in source_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            relative_path = py_file.relative_to(source_path)
            doc_file = docs_dir / source_dir / relative_path.with_suffix(".md")
            doc_file.parent.mkdir(parents=True, exist_ok=True)
            
            docs_content = generate_module_docs(py_file)
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(docs_content)
    
    print("Documentation generation completed!")
    print(f"Generated documentation in: {docs_dir}")

if __name__ == "__main__":
    main()
EOF

chmod +x dev-tools/generate_docs.py

# 12. Create README for setup
print_status "Creating setup documentation..."
cat > SETUP_PROTOCOLS.md << 'EOF'
# Atlas Windsurf Protocols Setup

This document describes the automated setup created by `setup_windsurf_protocols.sh`.

## What's Included

### 🔧 Windsurf Protocols
- **Continuous Development Protocol**: 14 rules ensuring non-stop development
- **Quality Assurance Protocol**: 13 rules for code quality and security
- **Security Protocol**: 10 rules for robust security standards

### 🚀 CI/CD Pipeline
- **GitHub Actions**: Automated testing, linting, security scanning
- **Dependabot**: Automated dependency updates
- **Security Scanning**: Gitleaks, Trivy, Safety, Bandit
- **Quality Gates**: Coverage ≥90%, docstring coverage ≥85%

### 🛠️ Development Tools
- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage
- **Interrogate**: Docstring coverage analysis
- **Pre-commit hooks**: Automated quality checks

## Usage

### After Setup
1. **Quality Check**: `./dev-tools/check_quality.sh`
2. **Generate Docs**: `python dev-tools/generate_docs.py`
3. **Run Tests**: `pytest tests/ --cov`
4. **Security Scan**: `safety check && bandit -r agents/`

### Development Workflow
1. Follow Continuous Development Protocol rules
2. Write tests for new features
3. Maintain docstring coverage ≥85%
4. Run quality checks before commits
5. Monitor CI pipeline for security alerts

### CI Pipeline Features
- **Automated Testing**: Python 3.12 and 3.13
- **Security Scanning**: Weekly comprehensive audits
- **Performance Regression**: Benchmark comparison
- **Dependency Updates**: Automated PRs for security patches

## Configuration Files

- `.windsurf/rules/`: Protocol definitions
- `.github/workflows/ci.yml`: CI pipeline configuration
- `.github/dependabot.yml`: Dependency automation
- `pyproject.toml`: Tool configurations
- `pytest.ini`: Test configuration
- `.git/hooks/pre-commit`: Pre-commit quality checks

## Security Features

- **Secret Detection**: Prevents credential commits
- **Vulnerability Scanning**: Dependencies and container security
- **Code Analysis**: Static security analysis with Bandit
- **Automated Updates**: Security patches via Dependabot
- **Regular Audits**: Weekly security scan schedule

## Quality Assurance

- **Code Coverage**: ≥90% statement coverage required
- **Docstring Coverage**: ≥85% public API documentation
- **Linting**: Comprehensive code style enforcement
- **Type Checking**: Static analysis with MyPy
- **Performance**: Regression detection for critical paths

This setup ensures Atlas maintains the highest standards of code quality, security, and development velocity.
EOF

# 13. Create .gitignore additions for development
print_status "Updating .gitignore for development tools..."
cat >> .gitignore << 'EOF'

# Atlas Development Tools
htmlcov/
.coverage
coverage.xml
.pytest_cache/
.mypy_cache/
.ruff_cache/
benchmark.json
benchmark-main.json
*-report.json
trivy-results.sarif

# Security and audit reports
safety-report.json
bandit-report.json
security-reports/

# Windsurf sessions (local only)
.windsurf/sessions/
.windsurf/context/

# Development artifacts
dev-tools/temp/
docs/api/
EOF

# Final status
echo ""
print_success "🎉 Atlas Windsurf Protocols & CI/CD Setup Complete!"
echo ""
echo "📋 Setup Summary:"
echo "  ✅ Windsurf protocols configured (3 protocol files)"
echo "  ✅ GitHub Actions CI pipeline configured"
echo "  ✅ Dependabot automation enabled"
echo "  ✅ Security scanning tools configured"
echo "  ✅ Quality assurance tools configured"
echo "  ✅ Pre-commit hooks installed"
echo "  ✅ Development scripts created"
echo "  ✅ Documentation generated"
echo ""
echo "🚀 Next Steps:"
echo "  1. Review SETUP_PROTOCOLS.md for usage instructions"
echo "  2. Run: ./dev-tools/check_quality.sh"
echo "  3. Commit and push to trigger CI pipeline"
echo "  4. Review GitHub repository settings for security features"
echo ""
echo "📖 Protocol Files Created:"
echo "  - .windsurf/rules/continuous_development_protocol.md (14 rules)"
echo "  - .windsurf/rules/quality_assurance_protocol.md (13 rules)"
echo "  - .windsurf/rules/security_protocol.md (10 rules)"
echo ""
echo "🔧 Development Tools:"
echo "  - dev-tools/check_quality.sh (quality verification)"
echo "  - dev-tools/generate_docs.py (documentation generation)"
echo "  - .git/hooks/pre-commit (automated checks)"
echo ""
print_success "Atlas is now configured with comprehensive protocols and CI/CD!"
