#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
APP_NAME="Atlas"
MAIN_SCRIPT="main.py"
ICON_FILE="assets/icon.icns"

# IMPORTANT: Replace with your Developer ID Application certificate name or hash
# To find this, run: security find-identity -v -p codesigning
DEVELOPER_ID_APPLICATION="YOUR_DEVELOPER_ID_APPLICATION"

# --- Build Process ---

echo "--- Cleaning up old builds ---"
rm -rf build dist "$APP_NAME.app"

echo "--- Building application with PyInstaller ---"
pyinstaller --name "$APP_NAME" \
            --windowed \
            --icon "$ICON_FILE" \
            --add-data "assets:assets" \
            --add-data "plugins:plugins" \
            "$MAIN_SCRIPT"

echo "--- Signing application bundle ---"
codesign --deep --force --options=runtime \
         --entitlements entitlements.plist \
         --sign "$DEVELOPER_ID_APPLICATION" \
         "dist/$APP_NAME.app"

echo "--- Verifying signature ---"
codesign --verify --verbose=4 "dist/$APP_NAME.app"
spctl --assess --verbose=4 "dist/$APP_NAME.app"

echo "--- Build and signing complete! ---"
echo "Application is available at: dist/$APP_NAME.app"
