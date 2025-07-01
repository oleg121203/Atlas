#!/bin/bash

# Atlas Development Environment Setup Script
# Цей скрипт автоматизує встановлення всіх покращень для Atlas проекту

set -e  # Вийти при будь-якій помилці

echo "🚀 Atlas Development Environment Setup"
echo "======================================"

# Функція для перевірки існування команди
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Функція для виведення помилки
error() {
    echo "❌ Error: $1" >&2
    exit 1
}

# Функція для виведення успіху
success() {
    echo "✅ $1"
}

# Функція для виведення інформації
info() {
    echo "ℹ️  $1"
}

# Перевірка Python версії
check_python() {
    info "Checking Python version..."
    if ! command_exists python3; then
        error "Python 3 is not installed"
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    min_version="3.12"
    
    if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
        error "Python $min_version or higher is required (found $python_version)"
    fi
    
    success "Python $python_version is supported"
}

# Встановлення Poetry
install_poetry() {
    if command_exists poetry; then
        success "Poetry is already installed ($(poetry --version))"
        return
    fi
    
    info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Додаємо Poetry до PATH для поточної сесії
    export PATH="$HOME/.local/bin:$PATH"
    
    if command_exists poetry; then
        success "Poetry installed successfully"
    else
        error "Poetry installation failed"
    fi
}

# Налаштування Poetry проекту
setup_poetry() {
    info "Setting up Poetry project..."
    
    # Якщо poetry.lock не існує, створюємо його
    if [ ! -f "poetry.lock" ]; then
        poetry lock
    fi
    
    # Встановлюємо залежності
    poetry install --with dev,docs,performance
    success "Poetry dependencies installed"
}

# Встановлення pip залежностей (як fallback)
install_pip_dependencies() {
    info "Installing dependencies with pip..."
    pip install -r requirements.txt
    
    # Встановлюємо додаткові інструменти для розробки
    pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist
    pip install ruff mypy pre-commit bandit safety
    pip install sphinx sphinx-rtd-theme myst-parser sphinx-autodoc-typehints sphinx-copybutton
    
    success "Pip dependencies installed"
}

# Налаштування pre-commit hooks
setup_precommit() {
    info "Setting up pre-commit hooks..."
    
    if command_exists poetry && [ -f "poetry.lock" ]; then
        poetry run pre-commit install
    else
        pre-commit install
    fi
    
    success "Pre-commit hooks installed"
}

# Запуск тестів для перевірки налаштування
run_tests() {
    info "Running tests to verify setup..."
    
    if command_exists poetry && [ -f "poetry.lock" ]; then
        poetry run pytest tests/ -v --tb=short
    else
        pytest tests/ -v --tb=short
    fi
    
    success "Tests completed successfully"
}

# Запуск linting для перевірки якості коду
run_linting() {
    info "Running code quality checks..."
    
    if command_exists poetry && [ -f "poetry.lock" ]; then
        poetry run ruff check .
        poetry run ruff format --check .
    else
        ruff check .
        ruff format --check .
    fi
    
    success "Code quality checks passed"
}

# Побудова документації
build_docs() {
    info "Building documentation..."
    
    if [ -d "docs" ]; then
        cd docs
        if command_exists poetry && [ -f "../poetry.lock" ]; then
            poetry run sphinx-build -b html . _build/html
        else
            sphinx-build -b html . _build/html
        fi
        cd ..
        success "Documentation built successfully"
        info "Open docs/_build/html/index.html to view documentation"
    else
        info "Skipping documentation build (docs directory not found)"
    fi
}

# Створення конфігураційних файлів (якщо не існують)
create_config_files() {
    info "Checking configuration files..."
    
    # .gitignore
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation
docs/_build/

# Ruff
.ruff_cache/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Atlas specific
atlas.log
bandit-report.json
coverage.xml
EOF
        success "Created .gitignore"
    fi
    
    # .env.example
    if [ ! -f ".env.example" ]; then
        cat > .env.example << 'EOF'
# Atlas Configuration Example
# Copy this file to .env and fill in your values

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Atlas Settings
ATLAS_DEBUG=false
ATLAS_LOG_LEVEL=INFO
ATLAS_THEME=dark

# Database (if using)
DATABASE_URL=sqlite:///atlas.db

# Analytics
ANALYTICS_ENABLED=true
PRIVACY_MODE=false
EOF
        success "Created .env.example"
    fi
}

# Виведення підсумку налаштування
print_summary() {
    echo ""
    echo "🎉 Atlas Development Environment Setup Complete!"
    echo "=============================================="
    echo ""
    echo "📋 What was installed/configured:"
    echo "  ✅ Python dependencies"
    echo "  ✅ Pre-commit hooks"
    echo "  ✅ Code quality tools (Ruff, Mypy, Bandit)"
    echo "  ✅ Testing framework (Pytest with coverage)"
    echo "  ✅ Documentation tools (Sphinx)"
    echo ""
    echo "🚀 Quick start commands:"
    echo "  make help          - Show all available commands"
    echo "  make test          - Run tests"
    echo "  make lint          - Run code quality checks"
    echo "  make format        - Format code"
    echo "  make docs          - Build documentation"
    echo "  make ci-local      - Run full CI pipeline"
    echo ""
    echo "📚 Next steps:"
    echo "  1. Copy .env.example to .env and configure your API keys"
    echo "  2. Read the documentation: make docs && open docs/_build/html/index.html"
    echo "  3. Start developing: python main.py"
    echo ""
    echo "💡 Tips:"
    echo "  - Use 'poetry shell' to activate the virtual environment (if using Poetry)"
    echo "  - Pre-commit hooks will run automatically before each commit"
    echo "  - Run 'make ci-local' before pushing to ensure everything passes"
    echo ""
}

# Основна функція
main() {
    echo "Starting Atlas development environment setup..."
    
    # Перевірка Python
    check_python
    
    # Створення конфігураційних файлів
    create_config_files
    
    # Спроба встановити Poetry і налаштувати проект
    if install_poetry 2>/dev/null && setup_poetry 2>/dev/null; then
        success "Using Poetry for dependency management"
        USE_POETRY=true
    else
        info "Falling back to pip for dependency management"
        install_pip_dependencies
        USE_POETRY=false
    fi
    
    # Налаштування pre-commit
    setup_precommit
    
    # Запуск тестів
    if run_tests 2>/dev/null; then
        success "All tests passed"
    else
        info "Some tests failed, but setup continues"
    fi
    
    # Перевірка якості коду
    if run_linting 2>/dev/null; then
        success "Code quality checks passed"
    else
        info "Code quality issues found, run 'make format' to fix"
    fi
    
    # Побудова документації
    build_docs 2>/dev/null || info "Documentation build skipped"
    
    # Виведення підсумку
    print_summary
}

# Запуск основної функції
main "$@"
