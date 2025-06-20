#!/bin/bash
# Quick test script for Atlas on macOS - Enhanced version

echo "🍎 Atlas macOS Quick Test (Enhanced)"
echo "===================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    exit 1
fi

# Show system info
echo "System Information:"
echo "- macOS version: $(sw_vers -productVersion)"
echo "- Python version: $(python3 --version)"
echo "- Architecture: $(uname -m)"

# Activate virtual environment if it exists
if [ -d "venv-macos" ]; then
    echo "📦 Activating macOS virtual environment..."
    source venv-macos/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ No virtual environment found, using system Python"
fi

# Test core dependencies
echo ""
echo "📦 Testing core dependencies..."
python3 -c "
dependencies = [
    ('PIL', 'from PIL import Image'),
    ('pathlib', 'from pathlib import Path'),
    ('platform', 'import platform'),
]

for name, import_str in dependencies:
    try:
        exec(import_str)
        print(f'✅ {name}: Available')
    except ImportError as e:
        print(f'❌ {name}: {e}')
"

# Test macOS-specific dependencies
echo ""
echo "🍎 Testing macOS-specific dependencies..."
python3 -c "
macos_deps = [
    ('Quartz', 'from Quartz import CGWindowListCreateImage'),
    ('PyAutoGUI', 'import pyautogui'),
    ('customtkinter', 'import customtkinter'),
]

for name, import_str in macos_deps:
    try:
        exec(import_str)
        print(f'✅ {name}: Available')
    except ImportError as e:
        print(f'⚠️ {name}: {e}')
"

# Test platform detection
echo ""
echo "🔍 Testing platform detection..."
python3 -c "
try:
    from utils.platform_utils import get_platform_info
    info = get_platform_info()
    print('✅ Platform detection working')
    print(f'   System: {info.get(\"system\", \"Unknown\")}')
    print(f'   macOS: {info.get(\"is_macos\", False)}')
    print(f'   Python: {info.get(\"python_version\", \"Unknown\")}')
except Exception as e:
    print(f'❌ Platform detection failed: {e}')
"

# Test native screenshot methods
echo ""
echo "📸 Testing native screenshot methods..."

# Test screencapture command
if command -v screencapture &> /dev/null; then
    echo "✅ screencapture command available"
    temp_file=$(mktemp /tmp/atlas_test_XXXXXX.png)
    if screencapture -x "$temp_file" 2>/dev/null; then
        if [[ -f "$temp_file" && -s "$temp_file" ]]; then
            file_size=$(stat -f%z "$temp_file" 2>/dev/null || echo "unknown")
            echo "✅ Native screenshot captured (${file_size} bytes)"
            rm -f "$temp_file"
        else
            echo "❌ Screenshot file not created or empty"
        fi
    else
        echo "❌ screencapture command failed"
    fi
else
    echo "❌ screencapture command not found"
fi

# Test Atlas screenshot tool
echo ""
echo "🎯 Testing Atlas screenshot tool..."
python3 -c "
import sys
import traceback
try:
    from tools.screenshot_tool import capture_screen
    print('✅ Screenshot tool imported successfully')
    
    # Quick test with fallback reporting
    img = capture_screen()
    if img:
        print(f'✅ Screenshot captured: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}')
    else:
        print('❌ Screenshot returned None')
        
except Exception as e:
    print(f'❌ Screenshot tool error: {e}')
    print('--- Error details ---')
    traceback.print_exc()
"

# Test main application startup (brief)
echo ""
echo "🚀 Testing main application startup..."
timeout 5 python3 -c "
try:
    import main
    print('✅ Main module imported successfully')
except Exception as e:
    print(f'❌ Main import failed: {e}')
" 2>/dev/null || {
    echo "⚠️ Main app test timed out or failed"
}

echo ""
echo "✅ Enhanced quick test completed!"
echo ""
echo "🔧 If issues found:"
echo "  - Install deps: pip install -r requirements-macos.txt"
echo "  - Full test: python3 test_screenshot_complete.py"
echo "  - Debug mode: python3 main.py --debug"
echo "  - Check logs in logs/ directory"
