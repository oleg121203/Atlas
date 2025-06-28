<!--
Developer Tools Usage Instructions for Atlas

This document provides detailed instructions on how to use the integrated developer tools within the Atlas ecosystem. These tools enhance development capabilities by providing IDE integration, debugging support, and performance monitoring directly within your development environment.
-->

# Developer Tools Usage Instructions

## Overview

Atlas integrates a suite of developer tools designed to streamline AI development workflows. These tools include IDE extensions for VS Code and PyCharm, debugging utilities, performance monitoring, and latency logging. This guide explains how to install, configure, and utilize each tool effectively within the Atlas platform.

## Prerequisites

Before using the developer tools, ensure you have the following:
- **Atlas Platform**: Installed and running on a macOS environment with Python 3.13.x.
- **IDE**: VS Code or PyCharm installed on your development machine.
- **Dependencies**: Necessary Python packages installed as per `requirements.txt`.

## 1. VS Code Extension for Atlas

The VS Code extension enables project management and intelligence operations directly from the VS Code IDE.

### Installation

1. **Initialize the Extension**:
   - Navigate to the `plugins` directory in your Atlas installation.
   - Run the initialization script for the VS Code extension:
     ```bash
     python vscode_extension.py
     ```
   - This will create the necessary extension structure and configuration files.

2. **Install the Extension**:
   - Open VS Code.
   - Go to the Extensions view (`Ctrl+Shift+X`).
   - Click on the `...` menu and select `Install from VSIX...`.
   - Navigate to `plugins/vscode/atlas-vscode-extension` and select the `.vsix` file generated during initialization (you may need to build it manually if not pre-built).

### Usage

- **Connect to Atlas Project**: Use the command palette (`Ctrl+Shift+P`) and select `Connect to Atlas Project` to link your current workspace with an Atlas project.
- **View Context Data**: Access current context data from Atlas AI via the command `View Context Data`.
- **Trigger Decisions**: Use `Trigger Atlas Decision` to initiate decision-making processes for specific goals directly from the IDE.

## 2. PyCharm Plugin for Atlas

The PyCharm plugin supports real-time code analysis and context-aware suggestions within the PyCharm IDE.

### Installation

1. **Initialize the Plugin**:
   - Navigate to the `plugins` directory in your Atlas installation.
   - Run the initialization script for the PyCharm plugin:
     ```bash
     python pycharm_plugin.py
     ```
   - This will set up the plugin structure and necessary configuration files.

2. **Install the Plugin**:
   - Open PyCharm.
   - Go to `Settings > Plugins`.
   - Click on `Install Plugin from Disk...`.
   - Navigate to `plugins/pycharm/atlas-pycharm-plugin` and select the plugin folder or built plugin file.

### Usage

- **Connect to Atlas Project**: Use the `Tools` menu and select `Connect to Atlas Project` to integrate with an Atlas project.
- **View Context Data**: Access context data via `Tools > View Context Data`.
- **Trigger Decisions**: Initiate decision-making with `Tools > Trigger Atlas Decision`.
- **Code Analysis**: Automatically receive suggestions and analysis as you code, with Atlas AI insights integrated into the PyCharm interface.

## 3. Debugging Tools

Atlas provides integration with debugging tools like `pdb++` and PySide6 debugging support for in-depth code inspection.

### Setup

1. **Initialize Debugging Tools**:
   - Run the debugging tools initialization script:
     ```bash
     python debugging_tools.py
     ```
   - This sets up configurations and installs hooks in key Atlas components.

2. **Enable Enhanced Debugging**:
   - Enable `pdb++` for enhanced debugging capabilities if installed:
     ```python
     from plugins.debugging_tools import DebuggingTools
     debugger = DebuggingTools('/path/to/atlas')
     debugger.initialize()
     debugger.enable_pdbpp()
     ```
   - Enable PySide6-specific debugging for UI components:
     ```python
     debugger.enable_pyside6_debugging()
     ```

### Usage

- **Set Breakpoints**: Use the `set_breakpoint` method to add breakpoints in specific files and lines:
  ```python
  debugger.set_breakpoint('main.py', 100)
  ```
- **Trace Operations**: Enable tracing for specific operations to monitor their execution:
  ```python
  debugger.trace_operation('context_update')
  ```

## 4. Performance Monitoring

Performance monitoring utilities track system resources and operation latency to ensure Atlas operates within performance thresholds.

### Setup

1. **Initialize Performance Monitor**:
   - Run the performance monitoring script:
     ```bash
     python performance_monitoring.py
     ```
   - Or initialize programmatically:
     ```python
     from plugins.performance_monitoring import PerformanceMonitor
     monitor = PerformanceMonitor('/path/to/atlas')
     monitor.initialize()
     ```

### Usage

- **Start Memory Tracing**: Begin tracing memory allocations with `tracemalloc`:
  ```python
  monitor.start_memory_tracing()
  ```
- **Get System Resources**: Retrieve current CPU and memory usage:
  ```python
  resources = monitor.get_system_resources()
  ```
- **Measure Latency**: Measure latency for specific operations:
  ```python
  latency_data = monitor.measure_latency('operation_name', some_function, arg1, arg2)
  ```
- **Generate Reports**: Generate a performance report:
  ```python
  monitor.generate_performance_report()
  ```

## 5. Latency Logger

The custom latency logger auto-generates performance reports every 30 minutes based on operation latency data.

### Setup

1. **Initialize Latency Logger**:
   - Run the latency logger script:
     ```bash
     python latency_logger.py
     ```
   - Or initialize programmatically:
     ```python
     from plugins.latency_logger import LatencyLogger
     logger = LatencyLogger('/path/to/atlas')
     logger.initialize()
     ```

### Usage

- **Start Auto-Reporting**: Start the auto-reporting thread to generate reports every 30 minutes:
  ```python
  logger.start_auto_reporting()
  ```
- **Log Latency**: Log latency data for operations:
  ```python
  logger.log_latency('screen_input', 85.5)
  ```
- **Get Latency Stats**: Retrieve latency statistics for specific operations or all:
  ```python
  stats = logger.get_latency_stats('screen_input')
  ```
- **Generate Report**: Manually generate a performance report:
  ```python
  logger.generate_performance_report()
  ```

## Advanced Usage Scenarios and Customization

### Advanced Debugging Hooks
- **Integration with Intelligence Components**: The debugging tools now offer deeper integration with key Atlas intelligence components such as `ContextEngine`, `DecisionEngine`, and `SelfImprovementEngine`. This allows developers to debug complex decision-making processes and context updates in real-time.
- **Customization**: Developers can customize debugging hooks by modifying the configuration in `plugins/debugging_tools.py`. You can specify which components to monitor and set custom breakpoints for specific events or conditions.
- **Usage Example**: 
  ```python
  from plugins.debugging_tools import AdvancedDebugger
  debugger = AdvancedDebugger(atlas_root_path)
  debugger.enable_component_monitoring(['ContextEngine', 'DecisionEngine'])
  debugger.set_custom_breakpoint('decision_made', condition='decision_score > 0.8')
  debugger.start_debugging()
  ```

### PyCharm Plugin Enhancements
- **Automated Refactoring Suggestions**: The PyCharm plugin now includes advanced features for automated refactoring suggestions. It analyzes your code in real-time and suggests improvements to reduce code duplication and enhance readability.
- **Customization**: You can configure the plugin's behavior by editing `plugin_config.json` in the plugin directory. Adjust settings like suggestion frequency, types of refactoring to suggest, and integration with Atlas AI intelligence.
- **Usage Example**: After installing the plugin in PyCharm, right-click on a code segment to trigger Atlas AI analysis. Select 'Suggest Refactoring' from the context menu to receive and apply suggestions.

### Performance Monitoring with Dashboard
- **Real-Time Dashboard Integration**: Performance monitoring now integrates with the Atlas UI to provide a real-time dashboard visualizing CPU usage, memory usage, and operation latencies.
- **Customization**: Modify `plugins/performance_monitoring.py` to adjust report intervals, enable/disable dashboard features, or set custom performance thresholds for alerts.
- **Usage Example**: 
  ```python
  from plugins.performance_monitoring import PerformanceMonitor
  monitor = PerformanceMonitor(atlas_root_path, report_interval=30)
  monitor.start_monitoring()
  monitor.setup_dashboard_ui()
  monitor.update_dashboard()
  ```

### Advanced Latency Analysis
- **Bottleneck Detection and Optimization Suggestions**: The new latency analyzer identifies operations with high latency and suggests optimizations to improve performance.
- **Customization**: In `plugins/latency_analyzer.py`, developers can set custom bottleneck thresholds and analysis intervals to tailor the tool to specific needs.
- **Usage Example**: 
  ```python
  from plugins.latency_analyzer import LatencyAnalyzer
  analyzer = LatencyAnalyzer(atlas_root_path, analysis_interval=10)
  analyzer.add_latency_data('Operation1', 0.7)
  analyzer.set_bottleneck_threshold(0.5)
  analyzer.start_analysis()
  results = analyzer.analyze_latencies()
  print(results)
  ```

## Multilingual Support

Atlas developer tools support multiple languages for user interfaces:
- **Ukrainian**: Default language when translations are unavailable.
- **Russian**: Fully supported for UI elements.
- **English**: Fully supported for UI elements and documentation.

Developers can contribute translations or modify existing ones by editing the language files in the `locales` directory of the Atlas project.

## Troubleshooting

- **Extension/Plugin Not Loading**: Ensure the extension or plugin is correctly initialized and installed. Check logs in `logs/` directory for errors.
- **Debugging Hooks Not Triggering**: Verify that debugging tools are initialized and hooks are installed in the correct components.
- **Performance Data Not Available**: Ensure `psutil` and `tracemalloc` are installed for system resource monitoring and memory tracing.

## Additional Resources

- **Source Code**: Review the source code in the `plugins/` directory for detailed implementation and customization options.
- **Community Support**: Join the Atlas AI community forums for additional support and to share feedback on developer tools.

---
*Last Updated: 2025-06-27*
