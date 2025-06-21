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

# Generate current requirements snapshot
pip freeze > requirements-current.txt
echo "✅ Generated requirements-current.txt"

# Extract development dependencies that match requirements-dev.txt
echo "🔍 Checking for development dependencies..."
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        continue
    fi
    
    # Extract package name without version
    pkg=$(echo "$line" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | xargs)
    
    # Check if package is installed
    if pip freeze | grep -qi "^$pkg=="; then
        echo "  - Found $pkg"
    else
        echo "⚠️  Missing development dependency: $pkg"
    fi
done < requirements-dev.txt

echo ""
echo "📋 Requirements Summary:"
echo "  - Base requirements:    $(grep -v '^#' requirements.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Linux requirements:   $(grep -v '^#' requirements-linux.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - macOS requirements:   $(grep -v '^#' requirements-macos.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Dev requirements:     $(grep -v '^#' requirements-dev.txt | grep -v '^$' | wc -l | xargs) packages"
echo "  - Current environment:  $(pip freeze | wc -l | xargs) packages"

echo ""
echo "✅ Requirements synchronization complete"
echo "  - To install development dependencies: pip install -r requirements-dev.txt"
echo "  - To install Linux dependencies: pip install -r requirements-linux.txt"
echo "  - To install macOS dependencies: pip install -r requirements-macos.txt"
