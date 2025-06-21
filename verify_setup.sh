#!/bin/bash
# Quick verification script to test setup
echo "🔍 Verifying Atlas Windsurf Protocols Setup"
echo "==========================================="

# Check if setup script exists
if [ ! -f "setup_windsurf_protocols.sh" ]; then
    echo "❌ Setup script not found!"
    exit 1
fi

echo "✅ Setup script found: setup_windsurf_protocols.sh"

# Check existing configuration
echo ""
echo "📋 Current Configuration Status:"

# Windsurf protocols
if [ -d ".windsurf/rules" ]; then
    echo "✅ Windsurf rules directory exists"
    echo "   Protocols found:"
    ls -1 .windsurf/rules/*.md 2>/dev/null | sed 's/^/   - /'
else
    echo "❌ Windsurf rules directory missing"
fi

# GitHub Actions
if [ -f ".github/workflows/ci.yml" ]; then
    echo "✅ GitHub Actions CI configured"
else
    echo "❌ GitHub Actions CI missing"
fi

# Dependabot
if [ -f ".github/dependabot.yml" ]; then
    echo "✅ Dependabot configuration exists"
else
    echo "❌ Dependabot configuration missing"
fi

# Development tools
if [ -f "pyproject.toml" ]; then
    echo "✅ Tool configurations in pyproject.toml"
else
    echo "❌ pyproject.toml missing"
fi

# Pre-commit hook
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook missing"
fi

echo ""
echo "🚀 To run full setup: ./setup_windsurf_protocols.sh"
echo "📖 For more info: cat SETUP_PROTOCOLS.md (after setup)"
