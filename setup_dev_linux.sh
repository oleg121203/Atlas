#!/bin/bash
# Atlas Development Environment Setup for Linux (Python 3.12)

echo "🐧 Setting up Atlas development environment for Linux..."

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux development environment"
    exit 1
fi

# Check Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 is required for development"
    echo "Install with: sudo apt update && sudo apt install python3.12 python3.12-venv"
    exit 1
fi

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create development virtual environment
if [ ! -d "$SCRIPT_DIR/venv-dev" ]; then
    echo "📦 Creating Python 3.12 development virtual environment..."
    python3.12 -m venv "$SCRIPT_DIR/venv-dev"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv-dev/bin/activate"

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing Linux development dependencies..."
if [ -f "$SCRIPT_DIR/requirements-linux.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements-linux.txt"
else
    echo "⚠️ requirements-linux.txt not found, using universal requirements"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Install development tools
echo "🔧 Installing development tools..."
pip install pytest black flake8 mypy

# Create development config if it doesn't exist
if [ ! -f "$SCRIPT_DIR/config-dev.ini" ]; then
    echo "⚙️ Creating development configuration..."
    if [ -f "$SCRIPT_DIR/dev-tools/setup/config.ini.example" ]; then
        cp "$SCRIPT_DIR/dev-tools/setup/config.ini.example" "$SCRIPT_DIR/config-dev.ini"
        echo "# Development environment settings" >> "$SCRIPT_DIR/config-dev.ini"
        echo "headless_mode = true" >> "$SCRIPT_DIR/config-dev.ini"
        echo "debug_mode = true" >> "$SCRIPT_DIR/config-dev.ini"
    fi
fi

# Test platform detection
echo "🔍 Testing platform detection..."
python3.12 -c "
from utils.platform_utils import get_platform_info
import json
info = get_platform_info()
print('Platform Info:')
for key, value in info.items():
    print(f'  {key}: {value}')
"

# Test headless operation
echo "🚀 Testing headless operation..."
python3.12 main.py --platform-info --headless

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🔧 Development Commands:"
echo "  source venv-dev/bin/activate     # Activate development environment"
echo "  python main.py --headless        # Run in headless mode"
echo "  python main.py --debug           # Run with debug logging"
echo "  python -m pytest tests/          # Run tests"
echo "  black .                          # Format code"
echo ""
echo "📝 Configuration:"
echo "  Edit config-dev.ini for development settings"
echo "  Use --config config-dev.ini to use development config"
echo ""
echo "🎯 Ready for Atlas development on Linux Python 3.12!"
