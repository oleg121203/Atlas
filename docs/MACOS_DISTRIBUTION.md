# macOS Application Distribution Guide

This document outlines the necessary steps to sign, notarize, and package the Atlas application for distribution on macOS.

## 1. Initial Setup Requirements

Before you can sign and notarize the application, you must complete the following setup steps.

### 1.1. Apple Developer Program

- **Enroll in the Apple Developer Program**: You must have an active membership in the Apple Developer Program, which costs $99 per year. This provides the certificates needed for code signing.
  - [Apple Developer Program](https://developer.apple.com/programs/)

### 1.2. Xcode and Command Line Tools

- **Install Xcode**: Download and install the latest version of Xcode from the Mac App Store. Xcode includes the Command Line Tools, which provide `codesign`, `productbuild`, and other essential utilities.
- **Initial Xcode Setup**: Launch Xcode at least once to allow it to install any additional required components.
- **Add Apple ID to Xcode**: 
  1. Open Xcode.
  2. Go to **Xcode > Settings...** (or **Preferences...**).
  3. Select the **Accounts** tab.
  4. Click the **+** button in the bottom-left corner and select **Apple ID**.
  5. Sign in with your Apple Developer account credentials. This will automatically make your signing certificates available to the system.

### 1.3. Create an App-Specific Password

The notarization service requires an app-specific password.

1.  **Generate Password**:
    - Sign in to [appleid.apple.com](https://appleid.apple.com).
    - In the "Sign-In and Security" section, select **App-Specific Passwords**.
    - Click **Generate an app-specific password** or the **+** button, give it a memorable name (e.g., `atlas-notary-tool`), and copy the generated password.

2.  **Store in Keychain**:
    - Open the **Keychain Access** application.
    - Select the **login** keychain.
    - Go to **File > New Password Item...**.
    - Enter the following details:
        - **Keychain Item Name**: `atlas-notary-tool` (a name of your choice for the build script)
        - **Account Name**: Your Apple ID (e.g., `developer@example.com`)
        - **Password**: The app-specific password you generated.
    - Click **Add**. The build script will use this keychain entry to authenticate with the notarization service.
