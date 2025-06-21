#!/bin/bash
# activate_venv.sh
# Helper script to activate the correct virtual environment for the current platform

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    VENV_DIR="venv-macos"
else
    PLATFORM="Linux"
    VENV_DIR="venv-linux"
fi

echo "🔍 Detected platform: $PLATFORM"

# Check if the recommended virtual environment exists
if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
    echo "✅ Found $PLATFORM virtual environment: $VENV_DIR"
    echo "🔄 Activating environment..."
    
    # The source command cannot directly affect the parent shell from a script
    # So we provide instructions to the user
    echo ""
    echo "To activate the virtual environment, run this command:"
    echo "source $VENV_DIR/bin/activate"
    echo ""
    echo "Or use this shortcut:"
    echo "source scripts/use_$PLATFORM.sh"
else
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "Please run ./scripts/install_requirements.sh first to set up the environment"
fi
