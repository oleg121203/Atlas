#!/bin/bash
# Quick configuration setup script for macOS

echo "🍎 Atlas macOS Configuration Setup"
echo "=================================="

CONFIG_FILE="config.ini"
BACKUP_FILE="config.ini.backup"

# Create backup if config exists
if [ -f "$CONFIG_FILE" ]; then
    echo "📋 Creating backup of existing config..."
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo "✅ Backup saved as $BACKUP_FILE"
fi

echo ""
echo "Current API configuration status:"
echo "================================="

# Check current API keys
echo "🔍 Checking API keys in config.ini..."

if grep -q "API_KEY = YOUR_API_KEY_HERE" "$CONFIG_FILE"; then
    echo "❌ OpenAI API key not configured"
    OPENAI_MISSING=true
else
    echo "✅ OpenAI API key appears to be set"
    OPENAI_MISSING=false
fi

if grep -q "API_KEY = your-working-gemini-key" "$CONFIG_FILE"; then
    echo "❌ Gemini API key placeholder detected"
    GEMINI_MISSING=true
else
    echo "✅ Gemini API key appears to be set"
    GEMINI_MISSING=false
fi

echo ""

# Check if we need to configure anything
if [ "$OPENAI_MISSING" = true ] || [ "$GEMINI_MISSING" = true ]; then
    echo "⚠️  Some API keys need configuration"
    echo ""
    echo "To configure API keys:"
    echo "1. Edit config.ini with your preferred text editor"
    echo "2. Replace placeholder values with your actual API keys"
    echo ""
    echo "Get API keys from:"
    if [ "$OPENAI_MISSING" = true ]; then
        echo "🔑 OpenAI: https://platform.openai.com/account/api-keys"
    fi
    if [ "$GEMINI_MISSING" = true ]; then
        echo "🔑 Gemini: https://makersuite.google.com/app/apikey"
    fi
    echo ""
    echo "Quick edit: nano config.ini"
else
    echo "✅ API configuration looks good!"
fi

echo ""
echo "🚀 To start Atlas:"
echo "python3 main.py"
echo ""
echo "🔧 To test screenshot functionality:"
echo "./quick_test_macos.sh"
echo ""
echo "📚 For more help:"
echo "cat MACOS_SETUP.md"
