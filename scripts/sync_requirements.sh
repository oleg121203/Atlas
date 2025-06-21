#!/bin/bash
# sync_requirements.sh
# Synchronizes requirements files and ensures consistency across environments

set -e

echo "🔄 Synchronizing Atlas requirements files..."

# Current directory should be Atlas root
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Run this script from the Atlas root directory."
    exit 1
fi

# Function to check if a package is installed
check_package() {
    local pkg=$1
    if pip freeze | grep -qi "^$pkg=="; then
        echo "  ✅ Found $pkg"
        return 0
    else
        echo "  ❌ Missing dependency: $pkg"
        return 1
    fi
}

# Generate current requirements snapshot
pip freeze > requirements-current.txt
echo "✅ Generated requirements-current.txt"

# Check if current environment has all required development packages
echo "🔍 Checking development dependencies..."
missing_dev=0
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        continue
    fi
    
    # Extract package name without version
    pkg=$(echo "$line" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | xargs)
    
    # Check if package is installed
    if ! check_package "$pkg"; then
        missing_dev=$((missing_dev + 1))
    fi
done < requirements-dev.txt

# Check platform-specific dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🔍 Checking macOS dependencies..."
    platform_file="requirements-macos.txt"
else
    # Linux
    echo "🔍 Checking Linux dependencies..."
    platform_file="requirements-linux.txt"
fi

missing_platform=0
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        continue
    fi
    
    # Extract package name without version
    pkg=$(echo "$line" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | xargs)
    
    # Check if package is installed
    if ! check_package "$pkg"; then
        missing_platform=$((missing_platform + 1))
    fi
done < $platform_file

echo ""
echo "📋 Requirements Summary:"
echo "  - Base requirements:    $(grep -v '^#' requirements.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Linux requirements:   $(grep -v '^#' requirements-linux.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - macOS requirements:   $(grep -v '^#' requirements-macos.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Dev requirements:     $(grep -v '^#' requirements-dev.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Current environment:  $(pip freeze | wc -l | xargs) packages"

if [ $missing_dev -gt 0 ] || [ $missing_platform -gt 0 ]; then
    echo ""
    echo "⚠️  Missing dependencies detected:"
    echo "  - $missing_dev development dependencies"
    echo "  - $missing_platform platform dependencies"
    echo ""
    echo "To install missing dependencies:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  pip install -r requirements-macos.txt -r requirements-dev.txt"
    else
        echo "  pip install -r requirements-linux.txt -r requirements-dev.txt"
    fi
else
    echo ""
    echo "✅ All required dependencies are installed"
fi

echo ""
echo "📊 For a detailed platform analysis, run:"
echo "  ./scripts/balance_requirements.sh"
