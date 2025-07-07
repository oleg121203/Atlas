#!/bin/bash
# Atlas macOS Launcher Script
# This script sets up the environment and launches Atlas on macOS systems.

# Exit on error
set -e

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "Error: Python 3.9 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for Apple Silicon
if [[ $(uname -m) == "arm64" ]]; then
    echo "Detected Apple Silicon Mac"
    export MACOS_ARCH="arm64"
else
    echo "Detected Intel Mac"
    export MACOS_ARCH="x86_64"
fi

# Set environment variables
export ATLAS_ENV="production"
export ATLAS_PLATFORM="macos"

# Launch the application
echo "Launching Atlas..."
python app/main.py "$@"
