#!/bin/bash
# use_linux.sh
# Quick shortcut to activate the Linux virtual environment

VENV_DIR="venv-linux"

if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
    # This script should be sourced, not executed
    # The output is just a reminder if executed directly
    echo "Activating Linux virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "✅ Linux environment activated"
    
    # Show Python and pip versions
    python --version
    pip --version
else
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "Please run ./scripts/install_requirements.sh first to set up the environment"
    exit 1
fi
