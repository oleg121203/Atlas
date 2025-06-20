#!/bin/bash
# Quick setup script for Advanced Web Browsing Plugin

echo "🚀 Setting up Advanced Web Browsing Plugin..."

# Install basic dependencies
echo "📦 Installing Python dependencies..."
pip install selenium playwright beautifulsoup4 requests pyautogui pynput webdriver-manager

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install

# Download Chrome driver
echo "🚗 Setting up Chrome WebDriver..."
python -c "
try:
    from webdriver_manager.chrome import ChromeDriverManager
    ChromeDriverManager().install()
    print('✅ Chrome WebDriver installed')
except Exception as e:
    print(f'⚠️ Chrome WebDriver setup failed: {e}')
"

# Test basic functionality
echo "🧪 Testing basic functionality..."
python -c "
import sys
import os

# Test imports
try:
    import selenium
    print('✅ Selenium imported successfully')
except ImportError:
    print('❌ Selenium import failed')

try:
    import playwright
    print('✅ Playwright imported successfully')
except ImportError:
    print('❌ Playwright import failed')

try:
    import requests
    print('✅ Requests imported successfully')
except ImportError:
    print('❌ Requests import failed')

try:
    import pyautogui
    print('✅ PyAutoGUI imported successfully')
except ImportError:
    print('❌ PyAutoGUI import failed')
"

echo "✅ Setup completed! The Advanced Web Browsing Plugin is ready."
echo ""
echo "📋 Available automation methods:"
echo "   1. Selenium WebDriver (Chrome, Firefox, Safari)"
echo "   2. Playwright (Chromium, Firefox, WebKit)"
echo "   3. System Events + PyAutoGUI"
echo "   4. Direct HTTP requests"
echo ""
echo "🔧 To test the plugin, run:"
echo "   python test_web_browsing.py"
