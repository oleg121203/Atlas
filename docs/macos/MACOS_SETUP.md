# Atlas - Setup and Launch Guide for macOS

## Prerequisites

1. **Python 3.8 or higher**
   ```bash
   # Check your Python version
   python3 --version
   
   # If Python is not installed, install via Homebrew:
   brew install python
   ```

2. **Git** (for cloning the repository)
   ```bash
   brew install git
   ```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/your-repo/Atlas.git
   cd Atlas
   ```

2. **Run the setup script**:
   ```bash
   ./launch_macos.sh
   ```
   
   This script will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Launch Atlas

## Manual Installation (Alternative)

If you prefer to set up manually:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   # Use macOS-specific requirements if available
   pip install -r requirements-macos.txt
   # Or use universal requirements
   pip install -r requirements.txt
   ```

3. **Launch Atlas**:
   ```bash
   python3 main.py
   ```

## macOS-Specific Features

### System Permissions

Atlas may request the following macOS permissions:

- **Screen Recording**: Required for screenshot functionality
- **Accessibility**: Required for automation features
- **Camera**: Required if using vision features
- **Microphone**: Required if using audio features

Grant these permissions when prompted via:
`System Preferences > Security & Privacy > Privacy`

### Native Features

- **Multiple screenshot methods**: 
  - Native `screencapture` command (primary)
  - AppleScript integration (backup)
  - Quartz API (legacy support)
- **System appearance**: Automatically adapts to light/dark mode
- **Dock integration**: Native macOS dock icon
- **Application Support**: Stores data in `~/Library/Application Support/Atlas`

## Testing Screenshot Functionality

After setup, verify screenshot functionality works:

### Quick Test
```bash
# Run enhanced quick test
./quick_test_macos.sh
```

### Comprehensive Test
```bash
# Run full diagnostic test
python3 test_screenshot_complete.py
```

### Manual Test
```bash
# Test screenshot capture directly
python3 -c "from tools.screenshot_tool import capture_screen; img = capture_screen(); print(f'Screenshot: {img.size[0]}x{img.size[1]} pixels')"
```

## Troubleshooting Screenshot Issues

If you encounter the error `'CGImageRef' object has no attribute 'width'`:

1. **Update pyobjc**:
   ```bash
   pip install --upgrade pyobjc-framework-Quartz pyobjc-framework-ApplicationServices
   ```

2. **Check Screen Recording permissions**:
   - System Preferences → Security & Privacy → Privacy → Screen Recording
   - Add Terminal and/or Python to allowed applications

3. **Verify fallback methods**:
   ```bash
   # Test native screencapture
   screencapture -x test.png && ls -la test.png && rm test.png
   ```

4. **Check detailed diagnostics**:
   ```bash
   python3 test_screenshot_complete.py
   ```

## Command Line Options

```bash
# Show platform information
python3 main.py --platform-info

# Enable debug logging
python3 main.py --debug

# Use custom config file
python3 main.py --config /path/to/config.json

# Display help
python3 main.py --help
```

## Troubleshooting

### Common Issues

1. **Permission Denied for Screenshots**:
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add your terminal application and/or Python

2. **Module Not Found Errors**:
   - Ensure you're using the virtual environment:
     ```bash
     source venv/bin/activate
     ```
   - Reinstall requirements:
     ```bash
     pip install -r requirements-macos.txt
     ```

3. **GUI Not Appearing**:
   - Ensure you're not running in headless mode
   - Check that X11 forwarding is not interfering (if using SSH)

### Performance Optimization

- **For Apple Silicon Macs**: Dependencies are optimized for ARM64
- **For Intel Macs**: Standard x86_64 packages are used
- **Memory usage**: Atlas automatically configures for available system memory

## Development Mode

For development work:

1. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt  # if available
   ```

2. **Run tests**:
   ```bash
   python3 -m pytest tests/
   ```

3. **Enable debug mode**:
   ```bash
   python3 main.py --debug
   ```

## Support

- Platform: macOS 10.15+ (Catalina and later)
- Python: 3.8+ required, 3.11+ recommended
- Architecture: Both Intel (x86_64) and Apple Silicon (ARM64) supported

For issues specific to macOS, include:
- macOS version (`sw_vers`)
- Python version (`python3 --version`)
- Architecture (`uname -m`)
- Output of `python3 main.py --platform-info`
