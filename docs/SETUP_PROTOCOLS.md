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
