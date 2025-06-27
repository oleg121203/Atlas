# Atlas Development Makefile
# Provides convenient commands for development workflow

.PHONY: help install test lint format security clean ci-local setup-dev

# Default target
help:
	@echo "🚀 Atlas Development Commands"
	@echo "============================"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install     - Install all dependencies"
	@echo "  make setup-dev   - Setup development environment"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make lint        - Run linting checks"
	@echo "  make format      - Format code"
	@echo "  make security    - Run security checks"
	@echo ""
	@echo "🔧 CI/CD:"
	@echo "  make ci-local    - Run full CI pipeline locally"
	@echo "  make pre-commit  - Run pre-commit hooks"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make clean-all   - Clean everything including cache"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install ruff pre-commit pytest pytest-cov bandit safety

# Setup development environment
setup-dev: install
	@echo "🔧 Setting up development environment..."
	pre-commit install
	pre-commit autoupdate
	@echo "✅ Development environment ready!"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	ruff check .

# Fix linting issues
lint-fix:
	@echo "🔧 Auto-fixing linting issues..."
	ruff check . --fix

# Format code
format:
	@echo "📝 Formatting code..."
	ruff format .

# Check formatting
format-check:
	@echo "📝 Checking code formatting..."
	ruff format --check .

# Run security checks
security:
	@echo "🔒 Running security checks..."
	bandit -r . -f txt -ll --exclude backup_archive,backup_ui,backup_ui_qt,tests,.venv || true
	safety check || true

# Run pre-commit hooks
pre-commit:
	@echo "🔧 Running pre-commit hooks..."
	pre-commit run --all-files

# Run full CI pipeline locally
ci-local:
	@echo "🚀 Running full CI pipeline locally..."
	./scripts/local_ci_check.sh

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

# Clean everything including cache
clean-all: clean
	@echo "🧹 Deep cleaning..."
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .venv/ venv/ env/

# Quick development cycle
dev: lint-fix format test
	@echo "✅ Development cycle complete!"

# Release preparation
release-check: ci-local
	@echo "🎯 Release checks complete!"
	@echo "📋 Ready for release!"

# Show project status
status:
	@echo "📊 Project Status"
	@echo "================"
	@echo "📁 Current directory: $(PWD)"
	@echo "🐍 Python version: $(shell python --version)"
	@echo "📦 Pip version: $(shell pip --version)"
	@echo "🔧 Ruff version: $(shell ruff --version 2>/dev/null || echo 'Not installed')"
	@echo "🧪 Pytest version: $(shell pytest --version 2>/dev/null || echo 'Not installed')"
	@echo "🎯 Pre-commit version: $(shell pre-commit --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "📋 Git status:"
	@git status --porcelain | head -10
