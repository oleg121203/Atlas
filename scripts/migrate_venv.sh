#!/bin/bash
# migrate_venv.sh
# Migrates packages from one virtual environment to another
# Useful for standardizing environments

set -e

echo "🔄 Virtual Environment Migration Tool"
echo "This tool will help migrate packages from one environment to another"
echo ""

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    TARGET_VENV="venv-macos"
else
    PLATFORM="Linux"
    TARGET_VENV="venv-linux"
fi

# Check if a source environment is specified
if [ -z "$1" ]; then
    echo "❌ Error: Source environment not specified"
    echo "Usage: $0 <source_venv_path>"
    echo "Example: $0 venv"
    exit 1
fi

SOURCE_VENV="$1"

# Verify source environment exists
if [[ ! -d "$SOURCE_VENV" || ! -f "$SOURCE_VENV/bin/activate" ]]; then
    echo "❌ Error: Source environment not found at $SOURCE_VENV"
    exit 1
fi

# Verify target environment exists
if [[ ! -d "$TARGET_VENV" || ! -f "$TARGET_VENV/bin/activate" ]]; then
    echo "Target environment does not exist. Creating it now..."
    python -m venv "$TARGET_VENV"
fi

echo "🔍 Migrating from: $SOURCE_VENV"
echo "🔍 Migrating to: $TARGET_VENV"
echo ""

# Create a temporary requirements file
TEMP_REQS=$(mktemp)

# Activate source environment and save package list
source "$SOURCE_VENV/bin/activate"
echo "📦 Source environment packages:"
pip freeze | tee "$TEMP_REQS"
deactivate

# Activate target environment and install packages
source "$TARGET_VENV/bin/activate"
echo ""
echo "📦 Installing packages in target environment..."
pip install -r "$TEMP_REQS"

echo ""
echo "✅ Migration complete"
echo "Current environment: $TARGET_VENV"
echo ""
echo "To start using the new environment, run:"
echo "source $TARGET_VENV/bin/activate"
echo ""
echo "You may now remove the old environment with:"
echo "rm -rf $SOURCE_VENV"

# Clean up
rm "$TEMP_REQS"
