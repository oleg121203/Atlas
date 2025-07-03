# Atlas API Reference

This section provides comprehensive API documentation for all Atlas components.

## Core Systems

```{toctree}
:maxdepth: 2

api/core
api/tools
api/plugins
api/ui
```

## Core Architecture

Atlas is built around several key architectural components:

### Event-Driven Architecture
The entire system communicates through a centralized `EventBus` that enables loose coupling and real-time updates.

### Plugin System
Dynamic plugin loading and management with lifecycle control and self-healing capabilities.

### Tool Management
Comprehensive tool discovery, registration, and execution framework.

### Configuration Management
Environment-based configuration with type safety and validation.

## Quick Start

```python
from core.application import AtlasApplication

# Initialize Atlas with all systems
app = AtlasApplication()

# Start the application (headless mode)
app.start()

# Access core systems
plugin_system = app.plugin_system
tool_manager = app.tool_manager
event_bus = app.event_bus

# Load and activate a plugin
if plugin_system.load_plugin('git_integration'):
    plugin_system.activate_plugin('git_integration')
    print("Git integration plugin is active!")
```

## Architecture Overview

```{mermaid}
graph TD
    A[AtlasApplication] --> B[EventBus]
    A --> C[PluginSystem]
    A --> D[ToolManager]
    A --> E[Config]
    A --> F[SelfHealing]
    
    C --> G[Plugin Registry]
    C --> H[Active Plugins]
    D --> I[Tool Discovery]
    D --> J[Tool Execution]
    
    B --> K[UI Components]
    B --> L[Plugin Events]
    B --> M[Tool Events]
```
