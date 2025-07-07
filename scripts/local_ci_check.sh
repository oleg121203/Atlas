#!/bin/bash
# Local CI Check Script for Atlas AI Assistant
# This script runs all the checks that would be performed in CI/CD pipeline

set -e  # Exit on any error

echo "🚀 Starting Local CI Check for Atlas AI Assistant..."
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Are you in the project root?"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ ! -d ".venv" ]; then
    print_warning "Virtual environment not detected. Consider creating one with: python -m venv .venv"
fi

# Step 1: Run Ruff linting
print_step "Running Ruff linting..."
if command -v ruff &> /dev/null; then
    ruff check .
    print_success "Ruff linting passed"
else
    print_error "Ruff not found. Install with: pip install ruff"
    exit 1
fi

# Step 2: Run Ruff formatting check
print_step "Checking code formatting with Ruff..."
ruff format --check .
print_success "Code formatting check passed"

# Step 3: Run type checking with Pyright (if available)
print_step "Running type checking..."
if command -v pyright &> /dev/null; then
    pyright
    print_success "Type checking passed"
else
    print_warning "Pyright not found. Install with: npm install -g pyright"
fi

# Step 4: Run tests
print_step "Running tests..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v --tb=short
    print_success "Tests passed"
else
    print_warning "No tests directory found"
fi

# Step 5: Run security scan with Bandit
print_step "Running security scan with Bandit..."
if command -v bandit &> /dev/null; then
    bandit -r . -f json -o bandit-report.json --exclude .venv,__pycache__,.git
    print_success "Security scan completed"
else
    print_warning "Bandit not found. Install with: pip install bandit"
fi

# Step 6: Run pre-commit hooks (if available)
print_step "Running pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit run --all-files
    print_success "Pre-commit hooks passed"
else
    print_warning "Pre-commit not found. Install with: pip install pre-commit"
fi

# Step 7: Check for common issues
print_step "Checking for common issues..."

# Check for Python cache files
if find . -name "*.pyc" -o -name "__pycache__" | grep -q .; then
    print_warning "Python cache files found. Consider adding them to .gitignore"
fi

# Check for large files
large_files=$(find . -type f -size +10M -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null || true)
if [ -n "$large_files" ]; then
    print_warning "Large files detected:"
    echo "$large_files"
fi

print_success "Common issues check completed"

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Local CI Check completed successfully!${NC}"
echo "Your code is ready for commit and push."
echo "=================================================="
