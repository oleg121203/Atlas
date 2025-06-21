#!/bin/bash
# fix_jedi.sh
# Script to fix issues with Jedi Language Server

echo "🔧 Fixing Jedi Language Server issues..."

# Check if running in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Error: Not running in a virtual environment"
    echo "Please activate your virtual environment first:"
    echo "  source scripts/use_macos.sh  # for macOS"
    echo "  source scripts/use_linux.sh  # for Linux"
    exit 1
fi

# Uninstall current jedi and jedi-language-server
echo "🔄 Removing current Jedi installations..."
pip uninstall -y jedi-language-server jedi

# Install the latest versions
echo "📦 Installing latest Jedi packages..."
pip install jedi jedi-language-server

# Verify installation
echo "✅ Verifying installation..."
python -c "import jedi; print(f'Jedi version: {jedi.__version__}')"
echo "jedi-language-server version: $(jedi-language-server --version 2>&1 || echo 'Not available')"

echo ""
echo "✅ Jedi reinstallation complete"
echo ""
echo "If you still experience issues in VS Code:"
echo "1. Press Ctrl+Shift+P (or Cmd+Shift+P on macOS)"
echo "2. Type and select 'Developer: Reload With Extensions Disabled'"
echo "3. Re-enable the Python extension"
echo "4. Restart VS Code"
