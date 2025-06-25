# Internal APIs for Module Interactions

This document outlines the internal APIs used for interactions between core modules, plugins, and other components within the Atlas application. It serves as a reference for developers to understand how different parts of the system communicate and integrate.

## Table of Contents
- [Overview](#overview)
- [Core Module APIs](#core-module-apis)
  - [AtlasMainWindow](#atlasmainwindow)
  - [PluginManager](#pluginmanager)
  - [AgentManager](#agentmanager)
- [UI Module APIs](#ui-module-apis)
  - [ChatModule](#chatmodule)
  - [TasksModule](#tasksmodule)
  - [AgentsModule](#agentsmodule)
  - [PluginsModule](#pluginsmodule)
  - [SettingsModule](#settingsmodule)
  - [StatsModule](#statsmodule)
  - [SystemControlModule](#systemcontrolmodule)
  - [SelfImprovementCenter](#selfimprovementcenter)
- [Plugin Interaction APIs](#plugin-interaction-apis)
- [Error Handling and Fallbacks](#error-handling-and-fallbacks)

## Overview
The Atlas application is designed with a modular architecture to ensure flexibility and extensibility. Core modules handle primary functionalities, while plugins extend the system with additional features. Internal APIs define how these components interact, ensuring seamless communication and error handling.

## Core Module APIs

### AtlasMainWindow
The main window of the Atlas application, responsible for initializing and managing all UI modules and core components.

- **Initialization**: 
  - `_init_ui()`: Sets up the main UI components including sidebar, topbar, and central widget area.
  - `_init_modules(meta_agent)`: Initializes all UI modules with error handling and fallback widgets. It safely retrieves `agent_manager` from `meta_agent` if available.
  - `_connect_signals()`: Connects UI signals like button clicks to their respective slots.

- **Module Switching**:
  - `_switch_module(module_name)`: Switches the central widget to display the specified module. Handles special case for `self_improvement_module`.

- **Language Management**:
  - `change_language()`: Updates the application language based on user selection, refreshes UI elements, and calls `update_ui()` on modules that support it.

### PluginManager
Manages the lifecycle of plugins, including discovery, loading, activation, and deactivation.

- **Plugin Lifecycle**:
  - `load_plugins()`: Scans the plugins directory and loads plugin modules dynamically.
  - `activate(name, app_context=None)`: Activates a specific plugin, passing an optional application context.
  - `deactivate(name)`: Deactivates a specific plugin.
  - `reload_plugin(name)`: Reloads a specific plugin to update changes.
  - `reload_all()`: Hot-reloads all plugins.

- **Plugin Information**:
  - `get_plugin_list()`: Returns a list of plugin information dictionaries.
  - `get_plugin_widget(name, parent=None)`: Retrieves the UI widget for a specific plugin if available.

### AgentManager
Manages agents and tools, facilitating their registration and execution within the application.

- **Agent Management**:
  - `add_agent(name, agent_instance)`: Registers a new agent with the given name.

- **Tool Management**:
  - `add_tool(name, tool_function, description=None, silent_overwrite=False)`: Registers a new tool with its function and description.
  - `execute_tool(tool_name, params)`: Executes a named tool with given parameters (assumed based on usage in `SystemControlModule`).

- **Integration**:
  - `set_plugin_manager(plugin_manager)`: Sets the plugin manager instance to avoid circular dependencies.

## UI Module APIs
Each UI module inherits from `QWidget` and provides specific functionality. They share common interaction patterns with `PluginManager` for plugin tools/widgets.

### ChatModule
Handles chat interactions with language model integration.

- **Plugin Integration**:
  - `set_plugin_manager(manager)`: Sets the plugin manager and updates plugin tools in the UI.
  - `update_tools()`: Updates UI with tools/widgets from active plugins.

- **Message Handling**:
  - `set_llm_callback(callback)`: Sets the callback function for handling responses from the language model.
  - `send_message()`: Sends the user’s input as a message to the chat.

### TasksModule
Manages task creation, deletion, and organization.

- **Plugin Integration**:
  - `set_plugin_manager(manager)`: Sets the plugin manager and updates plugin tools.
  - `update_tools()`: Updates UI with tools/widgets from active plugins.

- **Task Operations**:
  - `add_task()`: Opens a dialog to add a new task.
  - `delete_task()`: Deletes the selected task from the list.
  - `search(query)`: Searches tasks based on the input query.
  - `select_by_key(key)`: Selects a task by its key.

### AgentsModule
Manages agent interactions and configurations.

- **Plugin Integration**:
  - Similar to other modules, sets plugin manager and updates tools.

- **Agent Operations**:
  - Similar search and selection APIs as `TasksModule`.

### PluginsModule
Provides a UI for managing plugins (activation, deactivation, reload).

- **Plugin Management**:
  - `set_plugin_manager(manager)`: Sets the plugin manager and updates the plugin list.
  - `update_plugins()`: Updates the UI list with current plugin statuses.
  - `activate_plugin()`: Activates the selected plugin.
  - `deactivate_plugin()`: Deactivates the selected plugin.
  - `reload_plugins()`: Reloads all plugins.
  - `update_tools()`: Updates plugin tools/widgets in the UI.

### SettingsModule
Handles application and plugin settings.

- **Plugin Integration**:
  - `set_plugin_manager(manager)`: Sets the plugin manager and updates plugin settings UI.
  - `update_plugin_settings_section()`: Updates the UI with settings widgets from active plugins.

- **Settings Management**:
  - Manages language and theme selection via UI controls.

### StatsModule
Displays application statistics.

- **Basic UI**:
  - Currently provides a placeholder for statistics display without specific APIs for interaction.

### SystemControlModule
Provides system control functionalities (volume, sleep, app launching).

- **Initialization**:
  - `__init__(agent_manager=None, parent=None)`: Initializes with an optional `agent_manager` for tool execution.

- **System Operations**:
  - Uses `agent_manager.execute_tool()` for operations like mute, unmute, sleep, etc.

### SelfImprovementCenter
Enhances application capabilities (specific functionalities not detailed in current codebase view).

- **Initialization**:
  - Requires `meta_agent` for full functionality, otherwise falls back to a placeholder widget in `AtlasMainWindow`.

## Plugin Interaction APIs
Plugins follow a standardized interaction model with the core application:

- **Base Class**: Plugins inherit from `PluginBase`, implementing required methods like `activate()`, `deactivate()`, `get_widget()`, `settings_widget()`, and `info()`.
- **UI Integration**: Plugins can provide widgets for integration into various modules (`get_widget()` for tools, `settings_widget()` for configuration).
- **Activation**: Managed through `PluginManager`, which calls `activate()` and `deactivate()` methods.

## Error Handling and Fallbacks
- **Module Initialization**: `AtlasMainWindow` uses try-except blocks to catch errors during module creation, providing fallback `QWidget` instances to maintain UI integrity.
- **Plugin Loading**: `PluginManager` handles exceptions during plugin loading, logging errors without crashing the application.
- **Agent/Manager Availability**: Checks for `meta_agent` and `agent_manager` availability before usage, logging warnings if not available.
- **UI Updates**: Methods like `update_ui()` in modules handle language or theme changes gracefully.

This documentation will be updated as new modules or interaction patterns are introduced into the Atlas application.
