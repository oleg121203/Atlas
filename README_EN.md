# Atlas - Autonomous Computer Agent

Atlas is a powerful autonomous computer agent designed to assist with various tasks through AI-powered automation.

## Platform Support

Atlas supports multiple platforms with platform-specific optimizations:

- **macOS**: Full native support with Quartz-based screenshots and system integration
- **Linux**: GUI and headless operation support  
- **Windows**: Basic support (GUI mode)

## Quick Start

### macOS
```bash
# Clone and run setup script
git clone <repository-url>
cd Atlas
./launch_macos.sh
```

### Linux
```bash
# Install dependencies
pip install -r requirements-linux.txt
# Run Atlas
python main.py
```

### Universal
```bash
# Install universal dependencies
pip install -r requirements.txt
# Run Atlas
python main.py
```

## Command Line Options

```bash
# Show platform information
python main.py --platform-info

# Enable debug logging
python main.py --debug

# Run in CLI mode (when available)
python main.py --cli

# Force headless mode
python main.py --headless

# Use custom configuration
python main.py --config /path/to/config.json

# Show help
python main.py --help
```

## Platform-Specific Documentation

- [macOS Setup Guide](MACOS_SETUP.md) - Detailed macOS installation and setup
- [Linux Setup](INSTALLATION.md) - Linux-specific instructions
- [Ukrainian README](README.md) - Основна документація українською

## Features

- **Cross-platform GUI** using CustomTkinter
- **Platform-optimized screenshots** (Quartz on macOS, PyAutoGUI fallback)
- **AI-powered automation** with multiple LLM provider support
- **Enhanced memory management** for context retention
- **Plugin system** for extensibility
- **Task management** for multi-goal execution
- **Security features** for safe operation

## Requirements

- Python 3.8+ (3.11+ recommended)
- Platform-specific requirements in respective requirements files
- GUI environment (for GUI mode) or headless operation support

## Configuration

1. Copy configuration template:
   ```bash
   cp dev-tools/setup/config.ini.example config.ini
   ```

2. Edit `config.ini` with your settings:
   - API keys for LLM providers
   - Preferred models and settings
   - Security and operational parameters

## Development

See the `dev-tools/` directory for development utilities and testing tools.

## Platform Information

To check your platform compatibility:
```bash
python main.py --platform-info
```

Example output:
```
Atlas Platform Information:
  system: Darwin
  is_macos: True
  is_linux: False
  is_windows: False
  is_headless: False
  has_display: True
  python_version: 3.11.5
```

## macOS-Specific Features

### Native Integration
- **Quartz screenshots**: High-performance screen capture
- **System appearance**: Auto dark/light mode
- **Dock integration**: Native macOS dock icon
- **Application Support**: Data stored in `~/Library/Application Support/Atlas`

### Required Permissions
Atlas may request these macOS permissions:
- Screen Recording (for screenshots)
- Accessibility (for automation)
- Camera (if using vision features)
- Microphone (if using audio features)

Grant permissions via: `System Preferences > Security & Privacy > Privacy`

## Support

For platform-specific issues, please include:
- Output of `python main.py --platform-info`
- Python version (`python3 --version`)
- Operating system version
- Error logs with `--debug` flag

## Cross-Platform Compatibility

Atlas automatically adapts to your platform:

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| GUI | ✅ Native | ✅ | ✅ |
| Screenshots | ✅ Quartz | ✅ PyAutoGUI | ✅ PyAutoGUI |
| Headless | ✅ | ✅ | ⚠️ Limited |
| CLI Mode | 🚧 Planned | 🚧 Planned | 🚧 Planned |

---

Atlas adapts to your platform for optimal performance and integration.
