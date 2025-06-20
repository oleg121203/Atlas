#!/bin/bash
# macOS Native Launcher for Atlas
# This script sets up and launches Atlas with native macOS integration

set -e

echo "🍎 Atlas macOS Native Launcher"
echo "=============================="

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This launcher is for macOS only"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version (should be 3.13+ for macOS)
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.13"

echo "🐍 Python version: $PYTHON_VERSION"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Warning: Python 3.13+ recommended for macOS target. Current: $PYTHON_VERSION"
fi

# Check if virtual environment exists
if [ ! -d "venv-macos" ]; then
    echo "📦 Creating macOS virtual environment..."
    python3 -m venv venv-macos
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv-macos/bin/activate

# Install/update dependencies
echo "📥 Installing macOS dependencies..."
pip install --upgrade pip
pip install -r requirements-macos.txt

# Configure macOS-specific settings
echo "⚙️ Configuring macOS integration..."

# Check and request permissions
echo "🔐 Checking macOS permissions..."

# Accessibility permissions check
cat << 'EOF' > /tmp/check_permissions.py
import sys
try:
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    print("✅ Screen recording permissions available")
except:
    print("❌ Screen recording permissions needed - please grant in System Preferences > Security & Privacy > Privacy > Screen Recording")
    sys.exit(1)
EOF

python /tmp/check_permissions.py
rm /tmp/check_permissions.py

# Launch Atlas with macOS optimizations
echo "🚀 Launching Atlas..."
echo "🎯 Target: macOS Native Application"
echo "🔧 Mode: Production"

# Set macOS-specific environment variables
export ATLAS_PLATFORM=macos
export ATLAS_GUI_MODE=native
export ATLAS_TARGET_ENV=production

# Launch with proper macOS integration
python main.py --platform=macos --gui-mode=native

echo "👋 Atlas session ended"
