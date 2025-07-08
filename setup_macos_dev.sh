#!/bin/bash
# macOS Development Environment Setup Script for Atlas
# This script prepares a macOS system for Atlas development

# Exit on error
set -e

# Print header
echo "============================================"
echo "   Atlas macOS Development Environment Setup   "
echo "============================================"

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion)
echo "Detected macOS version: $MACOS_VERSION"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH based on architecture
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "Homebrew already installed, updating..."
    brew update
fi

# Install Python 3.9 via Homebrew
echo "Installing Python 3.9..."
brew install python@3.9

# Create symbolic link for Python 3.9
echo "Creating symbolic links..."
brew link --force python@3.9

# Install system dependencies
echo "Installing system dependencies..."
brew install cairo pango gdk-pixbuf libffi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install base requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Install development tools
echo "Installing development tools..."
pip install pytest pytest-cov mypy ruff pre-commit

# Setup VS Code if installed
if [ -d "/Applications/Visual Studio Code.app" ]; then
    echo "Setting up VS Code integration..."

    # Install recommended extensions
    code --install-extension ms-python.python
    code --install-extension ms-python.vscode-pylance
    code --install-extension charliermarsh.ruff
    code --install-extension ms-python.debugpy

    echo "VS Code extensions installed."
fi

# Initialize pre-commit
echo "Setting up pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with default settings..."
    cat > .env << EOL
# Atlas Environment Configuration
ATLAS_ENV=development
ATLAS_PLATFORM=macos
ATLAS_LOG_LEVEL=DEBUG
EOL
fi

echo "============================================"
echo "  macOS Development Environment Setup Complete  "
echo "============================================"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To start Atlas, run:"
echo "  ./launch_macos.sh"
echo ""
echo "Happy coding!"
