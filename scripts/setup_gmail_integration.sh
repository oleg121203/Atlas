#!/bin/bash

# Gmail API Integration Setup Script for Atlas
# This script installs the required packages for Gmail API integration

echo "🔧 Setting up Gmail API Integration for Atlas"
echo "=============================================="

# Check if we're in the Atlas directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the Atlas root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install required packages
echo ""
echo "📦 Installing Gmail API packages..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not available. Please install pip first."
    exit 1
fi

# Install packages
echo "Installing google-auth-oauthlib..."
pip3 install google-auth-oauthlib

echo "Installing google-auth-httplib2..."
pip3 install google-auth-httplib2

echo "Installing google-api-python-client..."
pip3 install google-api-python-client

# Verify installation
echo ""
echo "🔍 Verifying installation..."

python3 -c "
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    print('✅ All Gmail API packages installed successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Gmail API Integration setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Create a Google Cloud Project"
    echo "2. Enable the Gmail API"
    echo "3. Create OAuth 2.0 credentials"
    echo "4. Download credentials.json and place it in the Atlas directory"
    echo "5. Run Atlas and authenticate with Gmail"
    echo ""
    echo "📖 For detailed instructions, see: docs/GMAIL_API_SETUP.md"
    echo ""
    echo "🧪 To test the integration, run:"
    echo "   python3 tools/gmail_tool.py"
else
    echo ""
    echo "❌ Installation verification failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi 