#!/bin/bash
# use_macos.sh
# Quick shortcut to activate the macOS virtual environment

VENV_DIR="venv-macos"

if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
    # This script should be sourced, not executed
    # The output is just a reminder if executed directly
    echo "Activating macOS virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "✅ macOS environment activated"
    
    # Show Python and pip versions
    python --version
    pip --version
else
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "Please run ./scripts/install_requirements.sh first to set up the environment"
    exit 1
fi
