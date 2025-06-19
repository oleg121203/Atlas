#!/bin/bash
# Atlas launch script for macOS (Python 3.13 Production)

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS"
    echo "For Linux development, use: ./setup_dev_linux.sh"
    exit 1
fi

# Check if Python 3.13 is available (preferred for macOS)
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo "🍎 Using Python 3.13 for optimal macOS experience"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ "$PYTHON_VERSION" == "3.13" ]]; then
        PYTHON_CMD="python3"
    else
        echo "⚠️ Python 3.13 recommended for macOS. Current: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    fi
else
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3.13 from https://python.org or using Homebrew:"
    echo "  brew install python@3.13"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv-macos" ]; then
    echo "📦 Creating Python virtual environment for macOS..."
    $PYTHON_CMD -m venv "$SCRIPT_DIR/venv-macos"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv-macos/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Check if requirements are installed
if [ ! -f "$SCRIPT_DIR/venv-macos/lib/python*/site-packages/customtkinter/__init__.py" ]; then
    echo "📚 Installing requirements for macOS..."
    
    # Use macOS requirements if available, otherwise universal
    if [ -f "$SCRIPT_DIR/requirements-macos.txt" ]; then
        echo "Using macOS-optimized requirements..."
        pip install -r "$SCRIPT_DIR/requirements-macos.txt"
    else
        echo "Using universal requirements..."
        pip install -r "$SCRIPT_DIR/requirements.txt"
    fi
fi

# Create production config if it doesn't exist
if [ ! -f "$SCRIPT_DIR/config-macos.ini" ]; then
    echo "⚙️ Creating macOS production configuration..."
    if [ -f "$SCRIPT_DIR/dev-tools/setup/config.ini.example" ]; then
        cp "$SCRIPT_DIR/dev-tools/setup/config.ini.example" "$SCRIPT_DIR/config-macos.ini"
        echo "# macOS production settings" >> "$SCRIPT_DIR/config-macos.ini"
        echo "gui_mode = true" >> "$SCRIPT_DIR/config-macos.ini"
        echo "native_integration = true" >> "$SCRIPT_DIR/config-macos.ini"
    fi
fi

# Display platform info
echo "🔍 Platform Information:"
$PYTHON_CMD -c "
from utils.platform_utils import get_platform_info
info = get_platform_info()
for key, value in info.items():
    if 'macos' in key.lower() or key in ['system', 'python_version', 'has_display']:
        print(f'  {key}: {value}')
"

# Check for required permissions (informational)
echo ""
echo "🔐 Atlas may request the following macOS permissions:"
echo "  • Screen Recording (for screenshots)"
echo "  • Accessibility (for automation)"
echo "  • Camera (if using vision features)"
echo "  • Microphone (if using audio features)"
echo "Please grant these when prompted via System Preferences."
echo ""

# Launch Atlas
echo "🚀 Starting Atlas for macOS..."
cd "$SCRIPT_DIR"

# Use macOS config if available
if [ -f "config-macos.ini" ]; then
    $PYTHON_CMD main.py --config config-macos.ini "$@"
else
    $PYTHON_CMD main.py "$@"
fi
