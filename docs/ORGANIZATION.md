# Atlas Project Structure

This document outlines the organization of core files in the Atlas project following cross-platform development standards.

## Development Standards

Atlas follows a **dual-environment approach**:
- **Primary Development**: Linux (Python 3.12) - English-only code
- **Target Platform**: macOS (Python 3.13) - English-only code with Ukrainian UI
- **Code Language**: All comments, docstrings, and variable names in English
- **User Interface**: Ukrainian for end users

## Root Directory Files

The following files are maintained in the root directory for ease of access and import compatibility:

- `main.py` - Main entry point for the application
- `config_manager.py` - Configuration management utilities (copy from utils/)
- `plugin_manager.py` - Plugin discovery and management (copy from agents/)
- `logger.py` - Logging utilities (copy from utils/)
- `manage_api_keys.py` - API key management utility (copy from scripts/)

**Note**: These are copies for backward compatibility. The canonical versions are in their logical directories.

## Directory Structure

```
Atlas/
├── main.py                   # Main entry point
├── README.md                 # Ukrainian documentation
├── README_EN.md              # English documentation
├── config.ini                # Main configuration
├── requirements.txt          # Main requirements file
├── .env                      # Environment variables
├── state.json                # Application state
│
├── agents/                   # AI agent modules (English code)
├── tools/                    # Automation tools (English code)
├── utils/                    # Utility functions (English code)
├── ui/                       # User interface components (Ukrainian UI)
├── plugins/                  # Plugin system (English code)
│
├── config/                   # Additional configurations
├── requirements/             # Platform-specific requirements
├── scripts/                  # Launch and setup scripts (English code)
├── dev-tools/                # Development utilities (English code)
│   ├── analysis/             # Code analysis tools
│   ├── setup/                # Setup utilities
│   └── testing/              # Development tests
├── tests/                    # Test suites (English code)
│   └── security/             # Security-specific tests
├── docs/                     # Documentation
│   ├── reports/              # Project reports
│   └── macos/                # macOS-specific docs
│
└── data/                     # Application data
```

## Code Standards

### Language Requirements
- **Code**: English only (comments, docstrings, variable names)
- **UI Messages**: Ukrainian for end users
- **Documentation**: Both Ukrainian (README.md) and English (README_EN.md)
- **Error Messages**: English in logs, Ukrainian for users

### Platform Compatibility
- All code must work on both Linux (development) and macOS (target)
- Use `utils/platform_utils.py` for platform detection
- Implement graceful fallbacks for platform-specific features

This structure balances import compatibility with logical organization while maintaining cross-platform development standards.
