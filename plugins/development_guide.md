# Atlas Plugin Development Guide

This guide provides detailed instructions on how to develop plugins for the Atlas application. Plugins extend Atlas's functionality, allowing for custom tools, integrations, and features.

## Table of Contents
- [Introduction](#introduction)
- [Plugin Architecture](#plugin-architecture)
- [Development Environment](#development-environment)
- [Creating Your First Plugin](#creating-your-first-plugin)
  - [Plugin Structure](#plugin-structure)
  - [Metadata File](#metadata-file)
  - [Implementing Functionality](#implementing-functionality)
- [Testing Your Plugin](#testing-your-plugin)
- [Submitting to Marketplace](#submitting-to-marketplace)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Introduction

Atlas plugins are modular extensions that can interact with core functionalities, UI elements, and other plugins. They are written in Python and follow a specific structure to ensure compatibility and ease of integration.

## Plugin Architecture

Atlas uses a plugin system that allows dynamic loading and management. Key components include:
- **Plugin Manager**: Handles loading, activation, and deactivation of plugins.
- **Plugin Base Class**: Provides the foundation for all plugins with methods for initialization, command execution, and UI integration.
- **Tool Integration**: Plugins can register tools that users can interact with via the Atlas UI or API.

## Development Environment

To develop plugins for Atlas, ensure you have:
- **Python**: Version 3.9.6+ (ARM64 native for macOS)
- **Atlas Source Code**: Access to the latest Atlas repository for reference and testing.
- **IDE**: Any Python-compatible IDE, configured with linting tools like `ruff` and `mypy`.

Clone the Atlas repository and set up a virtual environment:
```bash
# Clone the repository (if you have access)
git clone <repository-url>
cd Atlas

# Set up virtual environment
python3 -m venv venv-macos
source venv-macos/bin/activate
pip install -r requirements.txt
```

## Creating Your First Plugin

### Plugin Structure

A typical plugin directory structure looks like this:
```
my_plugin/
│
├── __init__.py          # Marks directory as a Python package
├── main.py              # Main plugin implementation
├── metadata.json        # Plugin metadata and configuration
├── README.md            # Documentation for users
└── resources/           # Optional: Icons, UI files, additional assets
    └── icon.png
```

Create this structure in `plugins/marketplace/community/my_plugin` or within your development workspace.

### Metadata File

`metadata.json` describes your plugin for Atlas to recognize and manage it:
```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A brief description of what your plugin does.",
  "dependencies": {
    "atlas": "1.0.0"
  },
  "commands": [
    {
      "name": "mycommand",
      "description": "Description of the command",
      "parameters": [
        {
          "name": "param1",
          "type": "string",
          "required": true
        }
      ]
    }
  ],
  "ui_elements": [
    {
      "type": "button",
      "label": "My Button",
      "command": "mycommand"
    }
  ]
}
```

### Implementing Functionality

In `main.py`, define your plugin class inheriting from `PluginBase`:
```python
# my_plugin/main.py
from plugins.base import PluginBase

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "My Plugin"
        self.version = "1.0.0"
        
    def initialize(self):
        """Initialize the plugin, called when plugin is loaded."""
        print(f"{self.name} initialized")
        return True
    
    def execute(self, command: str, **kwargs):
        """Execute a command provided by the plugin."""
        if command == "mycommand":
            param1 = kwargs.get("param1", "")
            return {
                "success": True,
                "data": {"message": f"Received param1: {param1}"}
            }
        return {"success": False, "error": f"Unknown command: {command}"}
    
    def shutdown(self):
        """Cleanup when plugin is unloaded."""
        print(f"{self.name} shutdown")
```

## Testing Your Plugin

1. **Local Testing**: Copy your plugin folder to `plugins/marketplace/community` in your Atlas installation or development environment.
2. **Run Atlas**: Start Atlas and navigate to the Plugins section to activate your plugin.
3. **Debug**: Use logging to debug your plugin. Ensure logs are directed to a file or console for visibility.
4. **Unit Tests**: Write tests for your plugin's functionality, following the structure in `tests/plugins` if available.

## Submitting to Marketplace

Once your plugin is ready:
- Ensure all files are included and documentation is complete.
- Submit a pull request to the Atlas repository under `plugins/marketplace/community`, or follow submission guidelines if it's a separate process.
- Await review for security, compatibility, and functionality.

## Best Practices

- **Modularity**: Keep your plugin focused on a specific functionality.
- **Compatibility**: Test with the latest version of Atlas and specify compatible versions in `metadata.json`.
- **Security**: Avoid storing sensitive data in plain text; use Atlas's secure storage if necessary.
- **Documentation**: Provide clear instructions on usage, configuration, and troubleshooting.
- **Localization**: Support multiple languages if possible, following Atlas's UI language structure (Ukrainian, Russian, English).

## API Reference

Atlas provides several APIs for plugin interaction:

- **Core API**: Access to basic Atlas functions like logging and configuration.
  ```python
  from core.logging import get_logger
  logger = get_logger("MyPlugin")
  logger.info("Plugin initialized")
  ```
- **UI API**: Register UI elements to integrate with Atlas's interface.
- **Tool API**: Create tools that can be invoked via commands or UI.

For detailed API documentation, refer to the internal API docs or contact the Atlas development team.

---

Thank you for developing plugins for Atlas! If you have questions or need assistance, reach out via the community forums or developer channels.
