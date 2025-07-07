#!/bin/bash
# macOS Development Utility Script for Atlas
# This script provides development utilities for macOS

# Function to show help
show_help() {
    echo "Atlas macOS Development Utilities"
    echo "=================================="
    echo "Usage: ./macos_dev_utils.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       Setup development environment"
    echo "  test        Run tests"
    echo "  lint        Run linters"
    echo "  build       Build macOS application bundle"
    echo "  clean       Clean build artifacts"
    echo "  reset       Reset development environment"
    echo "  install     Install dependencies"
    echo "  help        Show this help message"
    echo ""
}

# Function to run tests
run_tests() {
    echo "Running tests..."
    source ../.venv/bin/activate
    python -m pytest ../tests/ -v "$@"
}

# Function to run linters
run_linters() {
    echo "Running linters..."
    source ../.venv/bin/activate
    echo "Running ruff checks..."
    ruff check ..
    echo "Running mypy type checking..."
    mypy ..
    echo "Running security checks..."
    bandit -r ../app ../core ../tools ../utils
}

# Function to clean build artifacts
clean_build() {
    echo "Cleaning build artifacts..."
    rm -rf ../build ../dist ../*.egg-info
    find .. -name "__pycache__" -type d -exec rm -rf {} +
    find .. -name "*.pyc" -delete
    find .. -name ".DS_Store" -delete
}

# Function to reset development environment
reset_env() {
    echo "Resetting development environment..."
    rm -rf ../.venv
    clean_build
    echo "Environment reset completed."
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    source ../.venv/bin/activate
    pip install --upgrade pip
    pip install -r ../requirements.txt
    pip install pytest pytest-cov mypy ruff bandit pre-commit
    echo "Dependencies installed."
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Change to script directory
cd "$(dirname "$0")"

# Process commands
case "$1" in
    setup)
        ../setup_macos_dev.sh
        ;;
    test)
        shift
        run_tests "$@"
        ;;
    lint)
        run_linters
        ;;
    build)
        ../scripts/build_macos_app.sh
        ;;
    clean)
        clean_build
        ;;
    reset)
        reset_env
        ;;
    install)
        install_deps
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0
