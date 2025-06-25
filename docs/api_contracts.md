# Atlas API Contracts

This document outlines the API contracts for key components and modules within the Atlas application. These contracts define the expected interfaces, methods, and behaviors for interaction between different parts of the system.

## Table of Contents
- [Core Application](#core-application)
- [Modules](#modules)
- [Plugins](#plugins)
- [UI Components](#ui-components)
- [Events](#events)
- [Configuration](#configuration)

## Core Application

### `AtlasApplication`
The main application class responsible for initialization, lifecycle management, and integration.

**Methods**:
- `initialize() -> bool`: Initialize application components. Returns `True` if successful.
- `start() -> bool`: Start the application and its components. Returns `True` if successful.
- `run() -> int`: Run the application main loop. Returns the exit code.
- `stop() -> bool`: Stop the application and its components. Returns `True` if successful.
- `shutdown() -> bool`: Shut down the application, cleaning up resources. Returns `True` if successful.

**Attributes**:
- `app: QApplication`: The Qt application instance.
- `config_manager: ConfigManager`: The configuration manager instance.
- `event_bus: EventBus`: The event bus for application-wide events.
- `module_registry: ModuleRegistry`: Registry for managing application modules.
- `plugin_registry: PluginRegistry`: Registry for managing plugins.
- `running: bool`: Indicates if the application is currently running.

### `ConfigManager`
Manages application configuration with support for environment-based settings and validation.

**Methods**:
- `load_config() -> None`: Load configuration from files and environment variables.
- `get(key: str, default: Optional[Any] = None) -> Any`: Get a configuration value by key.
- `set(key: str, value: Any) -> None`: Set a configuration value.
- `save(environment: Optional[str] = None) -> bool`: Save configuration to file. Returns `True` if successful.
- `validate() -> bool`: Validate the configuration. Returns `True` if valid.
- `get_environment() -> str`: Get the current environment.
- `set_environment(environment: str) -> None`: Set the current environment and reload configuration.

### `EventBus`
Handles event distribution for decoupled communication.

**Methods**:
- `subscribe(event_type: str, callback: Callable) -> None`: Subscribe to an event type with a callback function.
- `unsubscribe(event_type: str, callback: Callable) -> None`: Unsubscribe a callback from an event type.
- `publish(event_type: str, data: Any = None) -> None`: Publish an event with optional data.

### `ModuleRegistry`
Manages registration and lifecycle of application modules.

**Methods**:
- `register_module(module_name: str) -> bool`: Register a module by name. Returns `True` if successful.
- `get_module(module_name: str) -> Optional[Any]`: Get a module instance by name.
- `get_module_names() -> List[str]`: Get a list of registered module names.

### `PluginRegistry`
Manages discovery, loading, and lifecycle of plugins.

**Methods**:
- `set_application_context(context: Dict[str, Any]) -> None`: Set the application context for plugins.
- `discover_plugins() -> List[str]`: Discover available plugins in the plugins directory.
- `register_plugin(plugin_name: str) -> bool`: Register a plugin class. Returns `True` if successful.
- `load_plugin(plugin_name: str, config: Optional[dict] = None) -> Optional[PluginBase]`: Load and instantiate a plugin.
- `start_plugin(plugin_name: str) -> bool`: Start a specific plugin. Returns `True` if successful.
- `stop_plugin(plugin_name: str) -> bool`: Stop a specific plugin. Returns `True` if successful.
- `unload_plugin(plugin_name: str) -> bool`: Unload a plugin. Returns `True` if successful.
- `start_all_plugins() -> List[str]`: Start all loaded plugins. Returns list of started plugin names.
- `stop_all_plugins() -> List[str]`: Stop all loaded plugins. Returns list of stopped plugin names.
- `unload_all_plugins() -> List[str]`: Unload all loaded plugins. Returns list of unloaded plugin names.
- `get_plugin(plugin_name: str) -> Optional[PluginBase]`: Get a loaded plugin instance.
- `load_all_plugins(config: Optional[Dict[str, dict]] = None) -> List[str]`: Load all discovered plugins. Returns list of loaded plugin names.

## Modules

### Chat Module (`modules.chat`)
Handles conversational interfaces.

**Class: `ChatProcessor`**
- `process_message(message: str) -> str`: Process a user message and return a response.

### Tasks Module (`modules.tasks`)
Manages task creation and execution.

**Class: `TaskManager`**
- `create_task(description: str) -> Dict[str, Any]`: Create a new task. Returns task details.
- `get_tasks() -> List[Dict[str, Any]]`: Get list of all tasks.

### Agents Module (`modules.agents`)
Coordinates AI agent interactions.

**Class: `AgentManager`**
- `create_agent(model: str) -> Dict[str, Any]`: Create a new agent with specified model. Returns agent details.
- `get_agents() -> List[Dict[str, Any]]`: Get list of all agents.

## Plugins

### `PluginBase` (Abstract Base Class)
All plugins must inherit from this class.

**Methods** (Abstract):
- `_get_metadata() -> PluginMetadata`: Define plugin metadata.
- `_get_settings() -> Dict[str, Any]`: Define plugin settings.
- `execute(*args, **kwargs) -> Any`: Execute the main functionality of the plugin.

**Methods** (Concrete):
- `get_metadata() -> PluginMetadata`: Get plugin metadata.
- `get_settings() -> Dict[str, Any]`: Get plugin settings.
- `activate(app_context: Optional[Dict[str, Any]] = None) -> None`: Activate the plugin.
- `deactivate() -> None`: Deactivate the plugin.
- `get_state() -> Dict[str, Any]`: Get the current state of the plugin.
- `get_metadata_dict() -> Dict[str, Any]`: Return metadata as dictionary.
- `configure(config: Dict[str, Any]) -> None`: Update plugin configuration.
- `initialize() -> bool`: Initialize resources. Returns `True` if successful.
- `start() -> bool`: Start plugin operations. Returns `True` if successful.
- `stop() -> bool`: Stop plugin operations. Returns `True` if successful.
- `shutdown() -> bool`: Cleanup resources. Returns `True` if successful.
- `get_widget(parent: Optional[QWidget] = None) -> Optional[QWidget]`: Get main widget for UI integration.
- `set_settings(settings: Dict[str, Any]) -> None`: Set plugin settings.
- `settings_widget(parent: Optional[QWidget] = None) -> Optional[QWidget]`: Get settings widget for editing.
- `info() -> Dict[str, Any]`: Get plugin information.
- `on_activate(app_context: Optional[Dict[str, Any]] = None) -> None`: Called when plugin is activated.
- `on_deactivate() -> None`: Called when plugin is deactivated.

## UI Components

### `MainWindow`
Primary interface for user interaction.

**Methods**:
- `show_main_window() -> None`: Show the main application window.

### `ConfigWidget`
UI for editing configuration settings.

**Methods**:
- `save_config() -> None`: Save configuration from UI elements.

## Events

Events are used for decoupled communication between components. Key event types include:
- `config_updated`: Fired when configuration changes.
- `plugin_loaded`: Fired when a plugin is loaded.
- `plugin_unloaded`: Fired when a plugin is unloaded.
- `module_initialized`: Fired when a module is initialized.

## Configuration

Configuration follows a JSON schema defined in `config/schema.json`. Key configuration sections include:
- `app_name`: Application name.
- `version`: Application version.
- `language`: UI language (en, uk, ru).
- `theme`: UI theme (dark, light).
- `debug`: Enable debug mode.
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `ui`: UI settings (font_size, window_width, window_height).
- `chat`: Chat module settings.
- `tasks`: Tasks module settings.
- `agents`: Agents module settings.
- `plugins`: Plugin-specific configurations.

**Note**: This document will be expanded with detailed parameter descriptions, return types, and example usage as part of the ongoing documentation updates in Phase 10.
