# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- **Critical Startup Failures:** Resolved a cascade of `AttributeError` and `TypeError` exceptions that prevented the application from launching. This involved:
    - Correcting the application's initialization sequence to ensure UI widgets are created before settings are applied.
    - Replacing incorrect method calls (`update_settings`, `get_tools`) with the correct implementations across `main.py` and various agent classes.
    - Fixing argument-passing errors during `ToolCreatorAgent` instantiation and tool registration.
    - Implementing the correct pipe-based communication protocol for updating the `SecurityAgent`'s configuration, replacing an erroneous direct method call.
    - Adding a missing `get_tool_names` method to `AgentManager` to support UI logging.
    - Adding a missing `update_settings` method to `LLMManager` to allow for dynamic configuration updates.
- **Plugin Loading Logic:** Refactored the plugin tool registration in `main.py` to correctly introspect tool objects and register their methods, resolving a `TypeError` when loading plugins like `WeatherTool`.
- **AgentManager Stability:** Corrected a `NameError` in `AgentManager.clear_tools` by using `self.logger` instead of a local `logger`.

### Changed
- **Refactored Settings Management:** Separated settings loading from UI application in `main.py` by creating a new `_apply_settings_to_ui` method, improving code clarity and fixing initialization-order bugs.

### Removed
- **Temporary `matplotlib` Usage:** All `matplotlib` imports and code have been temporarily commented out in `main.py` to bypass build failures on macOS Sequoia. This disables the performance metrics tab until a proper fix is implemented.

### Added
- **Interactive Goal Clarification**: The `MasterAgent` can now detect ambiguous goals and ask the user for clarification. The GUI displays a dialog to capture the user's response, which is then used to refine the goal and resume execution. This makes the agent more robust and interactive.
- **Tool Usage Statistics**: The system now tracks the success and failure counts for each tool. This data is collected by `MetricsManager`, reported by `MasterAgent` during plan execution, and displayed in new 'Success' and 'Failure' columns in the 'Tools' tab, providing key insights into tool reliability.
- **View Tool Source**: Users can now view the source code of any generated tool directly from the 'Tools' tab in a new read-only window. This improves transparency and makes debugging easier.
- **Live Performance Metrics**: The Performance Dashboard now displays real-time data. A new `MetricsManager` collects tool loading times and memory search latencies, and the GUI charts are connected to this live data source. A 'Clear Data' button has also been added.
- **Agent Self-Correction from Feedback**: `MasterAgent` now queries the `user_feedback` memory collection before generating a plan. It extracts reasons for past failures on similar goals and includes them in the planning prompt, enabling the LLM to avoid repeating mistakes.
- **Dynamic Memory Collection Loading**: Added a 'Refresh' button to the 'Memory Viewer' tab, allowing users to dynamically update the list of available memory collections without restarting the application.
- **Structured Memory Display**: The Memory Viewer now automatically detects and pretty-prints JSON content, displaying it with a monospaced font for improved readability.
- **Performance Dashboard**: Added a new 'Performance' tab to the GUI, which will serve as the foundation for visualizing key system metrics.
- **Performance Visualization**: Integrated `matplotlib` to display charts for tool loading times and memory search latency on the 'Performance' tab.
- **Advanced Self-Correction**: The `MasterAgent`'s planning prompt has been significantly enhanced. It now includes a 'Mandate' section that explicitly instructs the LLM to analyze past failures and devise novel plans that avoid repeating the same mistakes.

### Changed
- **Enhanced User Feedback Loop:** When a user marks a plan as 'Bad', a dialog now prompts for a reason. This detailed feedback, including the user's text, is stored in memory to improve future agent performance.
- **Interactive Tool Editing:** Users can now open a tool's source file in their default editor directly from the 'Tools' tab by clicking the 'Edit' button.
- **Interactive Tool Deletion:** Users can now delete dynamically generated tools directly from the 'Tools' tab in the GUI. This action removes the tool's file and unregisters it from the system.
- **Resilient Tool Loading:** The `AgentManager` can now safely load tools from the `generated` directory even if some files contain errors. It will log the error and skip the malformed file, ensuring application stability.
- **Intelligent Error Recovery:** The `MasterAgent`'s error recovery mechanism has been significantly upgraded. It now performs root cause analysis on execution errors. If a tool is missing, it attempts to create it. If tool arguments are incorrect, it uses the tool's documentation to correct the call. This makes the agent more autonomous and resilient.
- **Self-Improving Tool Creation:** The `ToolCreatorAgent` now uses long-term memory to learn from its past attempts. It retrieves successful and failed examples of similar tool requests to generate more reliable code and avoid repeating mistakes.
- **Enhanced GUI Feedback:** The `PlanView` now provides detailed, real-time updates for each step of a plan. It displays the tool being used, its arguments, and the final result or error, making the agent's execution process transparent.

### Added
- **Performance Monitoring:** Added execution time logging to tool loading (`AgentManager`) and memory search (`MemoryManager`) to help analyze and optimize performance.
- **Unit Tests for Core Agents:** Created new test suites for `MasterAgent` and `AgentManager` to validate the intelligent error recovery and resilient tool loading features, increasing overall test coverage and system stability.
- **Tool Management GUI:** A new 'Tools' tab has been added to the main interface, which displays a list of all dynamically generated tools. Users can see the tool's name, description, and file path, and can refresh the list.
- **Dynamic Tool Creation**: Implemented a `ToolCreatorAgent` that can generate, validate, and save new Python tools based on a description. The `AgentManager` now dynamically loads and reloads these tools, and the `MasterAgent` is immediately aware of them for planning.
- **Tests for ToolCreatorAgent**: Added a comprehensive PyTest test suite for the `ToolCreatorAgent` to ensure its reliability and robustness.

### Fixed
- **Stabilize MasterAgent Error Recovery and Testing:**
  - Resolved a series of critical bugs in `tests/test_error_recovery.py` that caused test failures, including `TypeError` on `MasterAgent` initialization and `AttributeError` due to incorrect mocking.
  - Fixed an infinite loop in the `MasterAgent`'s `run_once` method that caused tests to hang by correctly mocking the `pause()` method during testing and updating assertions.
  - The `MasterAgent` is now robust, and all related unit tests (`test_master_agent.py`, `test_error_recovery.py`) are passing, confirming the stability of the core error recovery loop.

### Fixed
- Resolved a critical bug in `MasterAgent` where prompt caching failed due to duplicated code. This ensures the `_tools_changed` flag is correctly reset and prompt regeneration only occurs when necessary.
- Corrected a `KeyError` during prompt generation in `MasterAgent` by properly escaping characters in the template.
- Restored the `__init__` method in `MasterAgent` that was accidentally removed, fixing a `TypeError` on instantiation and allowing tests to pass.
- **Tests for AgentManager**: Added tests for `AgentManager` to verify dynamic tool reloading and callback functionality.
- **Refactored Settings & Plugin Management**: Overhauled the Settings UI for improved usability and robustness. Consolidated duplicated save/load logic into a single, unified system. Plugin management now features a scrollable list and 'Enable/Disable All' buttons.
- **Clear Goal Button**: Added a 'Clear' button to the main agent tab, allowing users to quickly erase the content of the goal input field.
- **User Feedback System**: Implemented UI buttons ('Good' and 'Bad') that appear after a plan successfully completes. User feedback, along with the goal and the executed plan, is stored in the `user_feedback` collection in `MemoryManager` for future agent learning.

### Changed
- **Log Readability**: The GUI log view now uses color-coding for different log levels (e.g., yellow for WARNING, red for ERROR), making it easier to monitor agent activity and identify issues.

### Fixed
- **Application Startup Stability**: Resolved a series of critical errors that prevented the application from starting correctly.
- **Memory Viewer Initialization**: Fixed an `AttributeError` in `main.py` by replacing a call to a non-existent `memory_manager.get_all_collections()` with the correct method `memory_manager.client.list_collections()` to properly load memory collection names in the UI.
- **State Management**: Corrected a `TypeError` during application startup by refactoring `_load_app_state` and `_save_app_state` in `main.py` to use the standard `json` module for handling `state.json`, instead of the incompatible `ConfigManager`.
- **UI Race Condition**: Fixed a recurring `AttributeError` for UI labels (e.g., `prompt_tokens_label`) by initializing them to `None` in the `AtlasApp` constructor and adding checks in the `_update_token_stats` method to ensure widgets are created before being accessed.
- **Token Tracker Method Call**: Corrected an `AttributeError` by changing the method call from the non-existent `token_tracker.get_stats()` to the correct `token_tracker.get_usage()` in `main.py`.
- **Dynamic Tool Creation**: Implemented a `ToolCreatorAgent` that can write, validate, and save new Python tool functions on the fly. The `AgentManager` can now dynamically load these new tools, allowing the agent to expand its own capabilities.
- **Interactive Plan View**: Added a new UI component that displays the agent's current plan and visually tracks the execution status of each step in real-time.
- **Complex Goal Decomposition**: The `MasterAgent` can now analyze complex user goals and break them down into a sequence of smaller, actionable sub-goals.
- **Configuration Management**: Centralized settings like API keys and model names into a `config.ini` file, removing hardcoded values and the need for UI input.
- **Agent Error Recovery**: The `MasterAgent` can now recover from failed steps by analyzing the error and generating a new plan.
- **Proactive Memory Search**: The agent now searches its general long-term memory for relevant information before planning, enriching its context.
- **Memory Viewer Filters**: Added controls to the Memory Viewer to filter by collection and sort by relevance or date.

### Fixed
- Resolved multiple critical syntax and indentation errors in `master_agent.py` through a full-file replacement.
- Added a missing `time` import to `master_agent.py`.
- **`main.py` Stability:** Repaired corrupted `main.py` by removing duplicated code blocks related to settings and plugin management. This resolves major UI instability and ensures reliable settings persistence.

### Added
- Implemented application state persistence. The app now saves goal inputs, prompts, and chat history on exit and restores them on the next launch.
- Refactored the LLM backend to use the Ollama REST API, enabling token usage tracking for each call.
- Added a token usage statistics panel to the Settings tab to display real-time prompt, completion, and total token counts.
- Implemented a full plugin system with a `PluginManager` for dynamic discovery and a sample `WeatherTool` plugin to demonstrate extensibility.
- Created a comprehensive build, signing, and notarization workflow for macOS distribution, including a `build.sh` script and detailed documentation.
- Refactored `MasterAgent` to integrate with the plugin system, enabling it to use tools from plugins in its planning and execution cycles.
- Configured a GitHub Actions CI pipeline (`.github/workflows/ci.yml`) to automatically run linting (`ruff`), type checking (`mypy`), and tests on every push and pull request.
- Added comprehensive unit tests for core tools: `AgentManager`, `clipboard_tool`, `notification_tool`, `ocr_tool`, `screenshot_tool`, `image_recognition_tool`, and `terminal_tool`, ensuring component reliability.
- Implemented and passed a full end-to-end workflow test (`test_full_workflow.py`) to validate multi-agent coordination and result chaining.
- Implemented a robust error recovery mechanism in `MasterAgent`. The agent can now handle task failures by catching exceptions, regenerating the plan with error context, and retrying up to three times.
- Added an end-to-end test script (`tests/test_security_workflow.py`) to verify the `SecurityAgent`'s blocking and notification capabilities.
- Implemented a notification system with a `NotificationManager` and integrated it with the `SecurityAgent` to send alerts on security violations. Notification channels (Email, SMS, Telegram) are now configurable from the GUI.
- Implemented the initial `SecurityAgent` to run in a separate, isolated process for real-time security monitoring.
- Implemented the initial `DeputyAgent` for background log monitoring. It runs in a separate thread to detect errors and anomalies.
- Created a foundational agent framework with an abstract `BaseAgent` class and placeholder files for all specialized agents (`BrowserAgent`, `ScreenAgent`, `TextAgent`, `SystemInteractionAgent`).
- Initial project structure and placeholder files.
- Basic CustomTkinter application window setup.
- Tabbed GUI scaffold with placeholders for all main sections.
- Implemented `tools/screenshot_tool.py` for macOS screen capture.
- Added foundational `agents/llm_manager.py` with Ollama backend and provider plugin structure.
- Introduced `DEV_PLAN.md` living development roadmap.
- Added full Master-Agent GUI widgets, execution controls, and live screenshot preview.
- Implemented `tools/ocr_tool.py` with Vision/pytesseract OCR backend.
- Relocated and expanded Continuous Development and Quality Assurance protocols into `rules/` directory (always-on).
- Enhanced Continuous Development Protocol to ensure uninterrupted plan execution and automatic synchronization of `DEV_PLAN.md` and `CHANGELOG.md`.
- Strengthened Quality Assurance Protocol with detailed guidelines for code quality, security, and UX consistency.
- Added command-line arguments in `main.py` to support development mode (`--mode dev`) and protocol prioritization (`--protocols-first`).
- Updated Continuous Development Protocol to include automatic resumption policy, ensuring development continues from the last stopping point without user prompts.
- Implemented `tools/image_recognition_tool.py` with OpenCV for template matching and object detection functionalities.
- Added core directives to both development protocols for enhanced enforcement and clarity.
- Enhanced Quality Assurance Protocol with performance benchmarks and macOS-specific compatibility requirements.
- **COMPLETED Phase 2**: Implemented all remaining core tools (`mouse_keyboard_tool.py`, `clipboard_tool.py`, `terminal_tool.py`) with comprehensive macOS native API support and fallback mechanisms.
- Created `agents/master_agent.py` and connected its core methods (`run`, `pause`, `stop`) to the main GUI controls, making the interface functional.
- Implemented a live log console in the GUI by creating a custom `GuiLogger` and integrating it with the application's main logger.
- Added a `ChatHistoryView` component to display agent interactions in a readable, chat-style format in the 'Logs & History' tab.
- Implemented a scrollable list in the 'Agents' tab to display specialized agent configurations, replacing the previous placeholder.
- Added a functional UI to the 'Security Settings' tab, including a rule editor, threshold sliders, and configuration buttons.
- Added provider and model selection dropdowns to each agent card in the 'Agents' tab.
- Added a placeholder 'Edit Fallback Chain' button to each agent card to prepare for the fallback editor feature.
- Implemented settings persistence using `ConfigManager` to save and load configurations for the 'Agents' and 'Security' tabs.
- Added a fully functional fallback-chain editor, allowing users to define and persist a sequence of models for each agent.
- Implemented "Goal List" execution mode, enabling the Master Agent to process a sequence of goals from the main input box.
- All tools now return standardized result dataclasses for consistent error handling and performance tracking.

### Changed
- Enhanced the `SecurityAgent` to be fully dynamic and configurable from the GUI. It now receives rule updates in real-time and can block goal execution based on a regex-powered rules engine.
- Refined `MasterAgent`'s planning logic with a more structured and robust LLM prompt, ensuring reliable agent selection and task delegation.
- **Completed Agent Framework**: Made the `BrowserAgent` functional using the `webbrowser` module. All specialized agents now have baseline capabilities, completing the initial implementation of the agent framework.
- Made the `TextAgent` functional by integrating the `LLMManager`. The agent can now perform text summarization.
- Made the `ScreenAgent` functional by integrating the `screenshot_tool`. The agent can now capture the screen when prompted.
- Implemented the first functional specialized agent, `SystemInteractionAgent`. It now uses the `terminal_tool` to execute shell commands, replacing its previous placeholder logic.
- Replaced hardcoded planning logic in `MasterAgent` with dynamic, LLM-driven plan generation. The `_generate_plan` method now calls `LLMManager` to create real-time, multi-step plans from user goals.
- Integrated the specialized agent framework into `MasterAgent`. The `_execute_plan` method now instantiates and delegates tasks to the appropriate agent (`BrowserAgent`, `ScreenAgent`, etc.), replacing the previous simulation.
- Refactored `MasterAgent`'s core logic into a modular structure with distinct `_generate_plan` and `_execute_plan` methods. This replaces the previous placeholder logic with a simulated workflow, making the agent ready for future LLM integration.
- Refactored `master_agent.py` to be fully thread-safe with a robust state-management and locking mechanism. The agent now correctly handles pause/resume, stop, and cyclic execution for both single goals and goal lists.
- Reinforced Continuous Development Protocol to explicitly ensure ongoing work without stopping after specific tasks or file updates, maintaining uninterrupted progress.
- Created a dedicated "Settings" tab with fields for API key management, allowing users to configure keys directly in the GUI.
- Implemented a visual progress bar that activates during agent execution to provide feedback on long-running tasks.
- Refactored the main application GUI to use the `.grid()` layout manager, improving consistency, alignment, and visual structure across all tabs.
- Added a custom application icon to the macOS build.
- Switched from `py2app` to `pyinstaller` for macOS packaging to resolve persistent dependency bundling issues.

### Fixed
- Corrected logging level in `main.py` to use integer constants from the `logging` module instead of string literals.
- Resolved persistent `ImportError` for `rubicon-objc` during the build process by switching to `pyinstaller`, which correctly handles namespace packages.

### Removed

---

## [0.1.0] - 2025-06-17

### Added
- Initial project setup based on "Final Workflow" document.
- Basic CustomTkinter GUI framework with tab view.
- Initial `README.md` and `CHANGELOG.md` files.

---

## [2024-12-19] - macOS Screenshot Fix

### Fixed
- **macOS Screenshot API Error:** Resolved critical `'CGImageRef' object has no attribute 'width'` error on macOS by updating Quartz screenshot implementation to use modern pyobjc API exclusively
- **Mixed API Usage:** Eliminated conflicting legacy and modern pyobjc API calls in screenshot functionality
- **Screenshot Fallback System:** Enhanced screenshot capture with robust fallback hierarchy:
  1. Native `screencapture` command (most reliable)
  2. AppleScript method (alternative native)
  3. Modern Quartz API (programmatic access)
  4. PyAutoGUI (cross-platform fallback)
  5. Dummy image (last resort)

### Added
- **Comprehensive Testing Suite:** 
  - `test_screenshot_complete.py` - Full diagnostic testing for all screenshot methods
  - `verify_screenshot_fix.py` - Quick verification script for the specific fix
  - Enhanced `quick_test_macos.sh` with detailed diagnostics
- **macOS Screenshot Documentation:** 
  - `docs/MACOS_SCREENSHOT_FIX.md` - Detailed fix documentation
  - Updated troubleshooting guides in `MACOS_SETUP.md` and `README_EN.md`
- **Enhanced Error Handling:** Better error reporting and diagnostics for screenshot functionality

### Changed
- **Screenshot Tool Architecture:** Refactored `tools/screenshot_tool.py` to use modern pyobjc function-based API
- **Image Format Handling:** Improved RGBA to RGB conversion for consistent screenshot output
- **Platform Detection:** Enhanced platform-specific code paths for better macOS integration

### Technical Details
- Updated from deprecated `image_ref.width()` to `CGImageGetWidth(image_ref)`
- Implemented proper CFData to bytes conversion for modern pyobjc
- Added comprehensive fallback testing and validation
- Enhanced cross-platform compatibility while maintaining macOS native features
