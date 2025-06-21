#!/bin/bash
# balance_requirements.sh
# Analyzes and balances requirements across platforms

set -e

echo "🔍 Analyzing Atlas requirements balance..."

# Current directory should be Atlas root
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Run this script from the Atlas root directory."
    exit 1
fi

# Temporary files for analysis
mkdir -p .tmp
LINUX_PKGS=".tmp/linux_pkgs.txt"
MACOS_PKGS=".tmp/macos_pkgs.txt"
DEV_PKGS=".tmp/dev_pkgs.txt"
COMMON_PKGS=".tmp/common_pkgs.txt"
UNIQUE_LINUX=".tmp/unique_linux.txt"
UNIQUE_MACOS=".tmp/unique_macos.txt"

# Extract package names without versions
grep -v "^#" requirements-linux.txt | grep -v "^$" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | sort > $LINUX_PKGS
grep -v "^#" requirements-macos.txt | grep -v "^$" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | sort > $MACOS_PKGS
grep -v "^#" requirements-dev.txt | grep -v "^$" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | sort > $DEV_PKGS

# Find common packages between Linux and macOS
comm -12 $LINUX_PKGS $MACOS_PKGS > $COMMON_PKGS

# Find unique packages in each platform
comm -23 $LINUX_PKGS $MACOS_PKGS > $UNIQUE_LINUX
comm -13 $LINUX_PKGS $MACOS_PKGS > $UNIQUE_MACOS

# Calculate statistics
LINUX_COUNT=$(wc -l < $LINUX_PKGS)
MACOS_COUNT=$(wc -l < $MACOS_PKGS)
DEV_COUNT=$(wc -l < $DEV_PKGS)
COMMON_COUNT=$(wc -l < $COMMON_PKGS)
UNIQUE_LINUX_COUNT=$(wc -l < $UNIQUE_LINUX)
UNIQUE_MACOS_COUNT=$(wc -l < $UNIQUE_MACOS)

echo ""
echo "📊 Requirements Balance Report:"
echo "  - Common packages: $COMMON_COUNT"
echo "  - Linux-specific: $UNIQUE_LINUX_COUNT"
echo "  - macOS-specific: $UNIQUE_MACOS_COUNT"
echo "  - Total Linux: $LINUX_COUNT"
echo "  - Total macOS: $MACOS_COUNT"
echo "  - Development: $DEV_COUNT"

echo ""
echo "🔍 Platform-specific packages:"
echo ""
echo "Linux-specific packages:"
cat $UNIQUE_LINUX | sed 's/^/  - /'
echo ""
echo "macOS-specific packages:"
cat $UNIQUE_MACOS | sed 's/^/  - /'

echo ""
echo "✅ Analysis complete"
echo ""
echo "To install packages:"
echo "  - Linux: pip install -r requirements-linux.txt -r requirements-dev.txt"
echo "  - macOS: pip install -r requirements-macos.txt -r requirements-dev.txt"
echo ""

# Clean up
rm -rf .tmp
