# Atlas Project Structure

This document outlines the organization of core files in the Atlas project.

## Root Directory Files

The following files are maintained in the root directory for ease of access and import compatibility:

- `main.py` - Main entry point for the application
- `config_manager.py` - Configuration management utilities
- `plugin_manager.py` - Plugin discovery and management
- `logger.py` - Logging utilities
- `manage_api_keys.py` - API key management utility

Copies of these utility files are also available in their logical directories:
- `utils/config_manager.py`
- `utils/logger.py`
- `agents/plugin_manager.py`
- `scripts/manage_api_keys.py`

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
├── agents/                   # AI agent modules
├── tools/                    # Automation tools
├── utils/                    # Utility functions
├── ui/                       # User interface components
├── plugins/                  # Plugin system
│
├── config/                   # Additional configurations
├── requirements/             # Platform-specific requirements
├── scripts/                  # Launch and setup scripts
├── dev-tools/                # Development utilities
├── tests/                    # Test suites
├── docs/                     # Documentation
│   ├── reports/              # Project reports
│   └── macos/                # macOS-specific docs
│
└── data/                     # Application data
```

This structure balances import compatibility with logical organization.
