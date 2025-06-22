#!/bin/bash
# install_requirements.sh
# Installs the appropriate requirements for the current platform

set -e

echo "📦 Installing Atlas requirements for the current platform..."

# Detect platform and set variables
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    PLATFORM_FILE="requirements-macos.txt"
    PYTHON_VERSION="3.13"
    VENV_DIR="venv-macos"
    
    # Handle gitleaks installation for macOS
    echo "Checking for gitleaks installation..."
    if ! command -v gitleaks &> /dev/null; then
        echo "Installing gitleaks via homebrew..."
        brew install gitleaks
    else
        echo "gitleaks is already installed."
    fi
else
    PLATFORM="Linux"
    PLATFORM_FILE="requirements-linux.txt"
    PYTHON_VERSION="3.12"
    VENV_DIR="venv-linux"
fi

echo "🔍 Detected platform: $PLATFORM"
echo "🐍 Expected Python version: $PYTHON_VERSION"
echo "🏠 Virtual environment: $VENV_DIR"

# Check if running inside a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️ Not running in a virtual environment"
    
    # Check if the platform-specific virtual environment exists
    if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
        echo "🔍 Found existing $PLATFORM virtual environment: $VENV_DIR"
        read -p "Activate existing virtual environment? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 Activating $VENV_DIR environment..."
            source "$VENV_DIR/bin/activate"
            echo "✅ Virtual environment activated"
        else
            echo "🔄 Creating a new virtual environment..."
            python -m venv "$VENV_DIR"
            source "$VENV_DIR/bin/activate"
            echo "✅ New virtual environment created and activated"
        fi
    else
        echo "🔄 Creating a new virtual environment: $VENV_DIR"
        python -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        echo "✅ New virtual environment created and activated"
    fi
else
    # Extract the name of the current virtual environment
    CURRENT_VENV=$(basename "$VIRTUAL_ENV")
    echo "🔍 Currently using virtual environment: $CURRENT_VENV"
    
    if [[ "$CURRENT_VENV" != "$VENV_DIR" && "$CURRENT_VENV" != "venv" ]]; then
        echo "⚠️ Warning: Current virtual environment ($CURRENT_VENV) does not match recommended environment ($VENV_DIR)"
        echo "⚠️ This may lead to inconsistencies in package installations"
        read -p "Continue with current environment? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "⚠️ Please restart the script after activating the correct environment:"
            echo "   source $VENV_DIR/bin/activate"
            exit 1
        fi
    fi
fi

# Check Python version
CURRENT_PYTHON_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ "$CURRENT_PYTHON_VERSION" != "$PYTHON_VERSION" ]]; then
    echo "⚠️ Warning: Current Python version ($CURRENT_PYTHON_VERSION) does not match expected version ($PYTHON_VERSION)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation aborted"
        exit 1
    fi
fi

# Upgrade pip to latest version
echo "🔄 Upgrading pip to the latest version..."
pip install --upgrade pip

# Install options
echo "Select installation options:"
echo "1) Core requirements only"
echo "2) Core + development tools"
echo "3) Full installation (core + development + additional tools)"
read -p "Option (1-3): " option

case $option in
    1)
        echo "📦 Installing core requirements..."
        pip install -r "$PLATFORM_FILE"
        ;;
    2)
        echo "📦 Installing core requirements and development tools..."
        pip install -r "$PLATFORM_FILE" -r requirements-dev.txt
        ;;
    3)
        echo "📦 Installing all requirements..."
        pip install -r "$PLATFORM_FILE" -r requirements-dev.txt
        
        # Additional platform-specific tools
        if [[ "$PLATFORM" == "macOS" ]]; then
            echo "📦 Installing macOS-specific tools..."
            pip install py2app rumps
        elif [[ "$PLATFORM" == "Linux" ]]; then
            echo "📦 Installing Linux-specific tools..."
            pip install docker
        fi
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo "✅ Installation complete"
echo ""
echo "To verify installation, run:"
echo "  ./scripts/sync_requirements.sh"
echo ""
echo "Current virtual environment: $(basename "$VIRTUAL_ENV")"
echo "To activate this environment in the future, run:"
echo "  source $VIRTUAL_ENV/bin/activate"