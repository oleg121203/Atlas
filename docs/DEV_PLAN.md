# Atlas – Development Plan

This document outlines the development milestones for the Atlas application.

## Phase 1: Application Stabilization (Completed)

- [x] **Fix Application Startup Errors:** Resolve all dependency issues, `AttributeError`, `TypeError`, and initialization order problems to allow the application to launch successfully in development mode.
- [x] **Restore Performance Metrics:** Investigate and fix the `matplotlib` installation issue on macOS to re-enable the performance visualization tab.
- [x] **Full Dependency Audit:** Review and pin all dependencies in `requirements.txt` to ensure reproducible builds.

## Phase 2: Core Functionality Activation

- [ ] **Enable LLM-Powered Agent:** Configure the OpenAI API key in `config.ini` to activate the `LLMManager` and enable the MasterAgent's planning and execution capabilities.
- [ ] **Test Core Agent Loop:** Run a simple goal to verify the agent can generate and execute a plan successfully.
- [ ] **Verify Plugin System:** Test the `Weather Tool` plugin to ensure it can be loaded and its tools can be executed by the agent.

## Phase 3: Feature Enhancement & Refinement

- [ ] **Enhance User Feedback Loop:** Test and refine the user feedback mechanism to ensure it correctly influences future agent plans.
- [ ] **Test Tool Creation Agent:** Verify that the `ToolCreatorAgent` can successfully generate, save, and load a new tool at runtime.
- [ ] **Improve UI/UX:** Conduct a review of the user interface for usability and consistency.

- [x] **Fix MasterAgent Error Recovery:** Stabilize the `MasterAgent` by fixing its error recovery mechanism, resolving test failures, and ensuring robust operation.

## Phase 2: Feature Expansion

- [x] **Implement Dynamic Tool Creation:** Added a `ToolCreatorAgent` that can generate new tools on the fly. This fulfills the need for a new core functionality and significantly expands the agent's capabilities.
- [x] **Enhance GUI:** Improved the user interface for better real-time feedback and user control during agent execution.
  - [x] The Plan View now shows detailed, real-time information for each step, including the tool, arguments, and results.

## Phase 3: Advanced Capabilities

- [x] **Implement long-term memory retrieval for ToolCreatorAgent:** The agent now learns from past tool creation attempts by searching its memory for similar requests and using them as examples in the prompt.
- [x] **Add more complex GUI interactions:** Added a 'Tools' tab to the GUI, allowing users to view dynamically generated tools, their descriptions, and file paths.

- [x] **Fix MasterAgent Prompt Caching**: Resolve the critical bug in `MasterAgent` where prompt caching failed due to duplicated code and incorrect template formatting. This ensures reliable and efficient prompt generation.
- [x] **Enhance Error Recovery in `MasterAgent`**: Implemented a context-aware error recovery system. The agent now analyzes the type of error (e.g., `ToolNotFoundError`, `InvalidToolArgumentsError`) and generates a specialized recovery plan. For a missing tool, it will try to create it; for bad arguments, it will try to fix them.
- [x] **Refactor AgentManager Tool Loading**: Streamlined the dynamic tool loading process in `AgentManager`. It now catches specific errors (e.g., `SyntaxError`) in tool files, logs the issue, and skips the malformed file, preventing a single bad tool from crashing the application.
- [x] **Increase Test Coverage for Core Agents**: Added comprehensive unit tests for `MasterAgent`'s new error recovery logic and `AgentManager`'s resilient tool loading. This ensures the stability and correctness of these critical components.

## Phase 4: GUI Interactivity and Agent Learning

- [ ] **Interactive Tool Management**: Enhance the 'Tools' tab in the GUI.
  - [x] Add a 'Delete' button to allow users to remove a generated tool file.
  - [x] Add an 'Edit' button to open the tool's source file for modification.
- [x] **Enhanced User Feedback Loop**: Improve the learning potential from user feedback.
  - [x] When a user marks a plan as 'Bad', prompt for a brief textual reason for the failure.
  - [x] Store this detailed feedback in memory for future planning.
- [ ] **Performance Optimization**: Profile and optimize key areas of the application.
  - [x] Analyze the performance of tool loading and memory searches as the number of items grows.

## Phase 5: Agent Learning and Advanced Observability

- [ ] **Agent Self-Correction from Feedback**:
  - [x] Implement logic for `MasterAgent` to query `user_feedback` memory before planning.
  - [x] Adjust plan generation based on reasons for past failures on similar goals.
- [ ] **Advanced Memory Viewer**:
  - [x] Add a dropdown to the 'Memory' tab to select and view different collections (e.g., `user_feedback`, `tool_creation_attempts`).
  - [x] Display memory content in a structured, readable format.
- [ ] **Performance Dashboard**:
  - [x] Create a new 'Performance' tab or section in the GUI.
  - [x] Visualize key metrics (tool loading time, memory search latency) using graphs.

## Phase 6: Live Metrics and Enhanced Tooling

- [x] **Live Performance Metrics**:
  - [x] Implement a log parsing utility or a metrics manager to collect performance data.
  - [x] Connect the 'Performance' tab charts to the live data source.
  - [x] Add a mechanism to clear or reset performance data.
- [ ] **Advanced Tool Management**:
  - [x] Add a feature to view the source code of generated tools directly within the GUI.
  - [x] Implement tracking and display of tool usage statistics (e.g., success/failure rates).
- [x] **Interactive Goal Clarification**:
  - [x] Implement a mechanism for the `MasterAgent` to ask for clarification if a goal is ambiguous.
  - [x] Update the GUI to handle and display clarification questions from the agent.

## Phase 2: GUI and User Experience

This phase focuses on improving the graphical user interface and overall user experience.

### Tasks

- [ ] **Implement Real-time Status Updates**: Display detailed, real-time status updates from the `MasterAgent` in the GUI.
- [ ] **Redesign Plugin Management UI**: Create a more intuitive UI for managing plugins, including descriptions and versioning.
- [ ] **Add Goal History**: Allow users to view and re-run previous goals.
### Phase 1: Core System Stabilization (Completed)

- [x] **Fix Critical Startup Errors**: Resolved multiple `AttributeError` and `TypeError` exceptions that prevented the application from launching.
- [x] **Correct State Management**: Replaced faulty `ConfigManager` logic with standard `json` handling for robust application state saving and loading.
- [x] **Stabilize UI Components**: Ensured all UI elements, including memory tabs and token counters, initialize and update correctly without race conditions.
- [x] **Dependency Injection Fixes**: Corrected `MasterAgent` and `TextAgent` initialization to ensure proper dependency injection (e.g., `LLMManager`).
- [x] **Plugin Loading**: Hardened the `PluginManager` to safely register plugins with varying function signatures.

### Phase 2: UI/UX Enhancements

- [x] **Implement User Feedback Mechanism**: Add UI elements for users to provide positive or negative feedback on agent performance.
- [x] **Improve Log Readability**: Add color-coding or icons to the log view to distinguish between different message levels (INFO, WARNING, ERROR).
- [x] **Add a "Clear Goal" Button**: Implement a button to easily clear the main goal input field.
- [x] **Refine Settings/Plugin Management**: Make the settings tab more intuitive, allowing users to easily enable/disable plugins and see their changes applied.

### Phase 3: Advanced Agent Capabilities

- [x] **Implement Goal Decomposition**: Enhance `MasterAgent` to break down complex goals into smaller, manageable sub-tasks.
- [x] **Enable Tool Chaining**: Allow the output of one tool to be used as the input for another in a multi-step plan.
- [x] **Integrate Long-Term Memory for Planning**: Allow agents to search memory for relevant information before creating a plan.
- [x] **Self-Extending Tools**: Implement an agent capable of creating new tools based on user requirements (`ToolCreatorAgent`).

### Phase 4: Quality Assurance and Refinement

- [ ] **Add Unit and Integration Tests**: Develop a suite of PyTest cases for critical components like `AgentManager`, `PluginManager`, and `MasterAgent`.
- [ ] **Code Linting and Formatting**: Enforce a consistent code style using `ruff` and `black`.
- [ ] **Add Comprehensive Docstrings**: Ensure all public modules, classes, and functions have clear, Google-style docstrings.
- [ ] **Performance Profiling**: Analyze and optimize any performance bottlenecks, especially in UI rendering and agent response times.

This document outlines the development roadmap for the Atlas autonomous agent.

## Phase 1: Core Architecture & Foundation (Completed)

- [x] Set up the initial project structure, including directories for agents, tools, and UI components.
- [x] Implement the main application window using `customtkinter`.
- [x] Create the `MasterAgent` with a basic execution loop.
- [x] Implement the `LLMManager` to abstract interactions with language models.
- [x] Develop the `ConfigManager` for loading and saving application settings.
- [x] Establish a basic logging system with GUI integration.

## Phase 2: Agent Capabilities & Intelligence (Completed)

- [x] Implement the `MemoryManager` for persistent, vector-based memory storage and retrieval.
- [x] Develop the `AgentManager` to dynamically load and manage specialized agents.
- [x] Create initial specialized agents (e.g., `ToolCreatorAgent`).
- [x] Implement robust planning and task decomposition logic in `MasterAgent`.
- [x] Design and integrate a `PluginManager` to allow for extensible functionality.
- [x] Add token tracking and display for monitoring API usage.

## Phase 3: Robustness and User Interaction (In Progress)

- [x] Implement a `PlanView` to visualize the agent's current plan and step-by-step progress.
- [x] Create a `ChatHistoryView` for logging agent actions and system messages.
- [x] Develop sophisticated error handling, retry logic, and status callbacks in `MasterAgent`.
- [x] **Implement an interactive feedback loop to allow user intervention on repeated execution failures.**
- [ ] Enhance the Settings tab with more granular controls (e.g., security thresholds, plugin management).
- [ ] Improve the Memory Viewer with advanced search, filtering, and editing capabilities.

## Phase 4: Advanced Features & Security

- [ ] Implement a `SecurityAgent` running in a separate process to monitor and approve sensitive operations.
- [ ] Develop a `DeputyAgent` for proactive assistance and background monitoring.
- [ ] Refine the plugin system with dependency management and isolated execution environments.
- [ ] Implement a comprehensive testing framework (PyTest) with coverage for core components.

## Phase 5: Deployment & Documentation

- [ ] Write comprehensive user and developer documentation.
- [ ] Create build scripts for packaging the application for different operating systems.
- [ ] Perform final QA and beta testing cycles.
- [ ] Release Version 1.0.

*(Living document – update after each milestone)*

## Phase 0 – Project Bootstrap 
Status: **Complete**  
Delivered: project structure, initial GUI scaffold, screenshot tool, LLM manager skeleton, docs.

---

## Phase 1 – GUI MVP (Week 1)

Goal: Achieve a functional CustomTkinter interface that can launch basic actions.

Tasks
1. Master Agent Tab
   - [x] Goal input `CTkTextbox`
   - [x] Master prompt `CTkTextbox`
   - [x] Execution controls: Run / Pause / Stop buttons with callbacks
   - [x] Execution-mode checkboxes (Cyclic mode and Goal List functional)
   - [x] Live screenshot preview (connect to `screenshot_tool.capture_screen`)
2. Agents Tab
   - [x] Dynamic list rendering via `CTkScrollableFrame`
   - [x] Provider/model selection widgets
   - [x] Fallback-chain editor
   - [x] Persist settings via `ConfigManager`
3. Logs & History Tab
   - [x] Live log console (stream from `logger`)
   - [x] Chat-style history blocks
4. Security Settings Tab
   - [x] Security rule textbox
   - [x] Three threshold sliders
   - [x] Notification channel check-boxes

Deliverable: GUI that can save/load config and show screenshots/logs.

---

## Phase 2 – Core Tools (Week 1-2)

- [x] `screenshot_tool`  
- [x] `ocr_tool` (Vision API + pytesseract fallback)  
- [x] `image_recognition_tool` (OpenCV template matching)  
- [x] `mouse_keyboard_tool` (PyAutoGUI + Quartz)  
- [x] `clipboard_tool`  
- [x] `terminal_tool`

Each tool ships with unit-testable API, returns rich dataclasses for traceability.

**Status: COMPLETE** - All core tools implemented with macOS native API support and fallbacks.

---

## Immediate Next Steps (Phase 1 & 2 Continued)
- **GUI MVP Completion**: **DONE**. Master Agent tab widgets are connected to `MasterAgent` callbacks.
- **Master Agent Core Logic**: **IN PROGRESS**. Refactored `MasterAgent` to use a modular planning (`_generate_plan`) and execution (`_execute_plan`) loop. The agent now instantiates and delegates tasks to the specialized agent framework.
- **Core Tools Implementation**:
  - Complete `image_recognition_tool.py` using OpenCV for template matching and object detection.
  - Implement `mouse_keyboard_tool.py` with PyAutoGUI and pynput for human-like input emulation.
  - Develop `clipboard_tool.py` for text/image operations using pyperclip and AppKit.
  - Create `terminal_tool.py` for shell command execution with subprocess.
- **Logs & History Tab**: Integrate live log streaming and chat history display in GUI using `logger.py` output.
- **Agents Tab Placeholder**: Add static placeholders for Specialized Agent configurations (to be expanded in Phase 4).

## Phase 3: LLM Manager Expansion
- **Fallback Logic**: Enhance `llm_manager.py` to support up to 10 fallback provider configurations per agent.
- **External API Integration**: Add plugins for OpenAI, Anthropic, and Gemini with user-provided API key handling.
- **Model Selection**: Implement dynamic model selection based on provider in GUI and backend.

## Phase 4: Agent Framework
- **Specialized Agents**: **COMPLETE**. All specialized agents (`SystemInteractionAgent`, `ScreenAgent`, `TextAgent`, `BrowserAgent`) now have baseline functional implementations. This completes the initial implementation of the agent framework.
- **Master Agent Full Workflow**: **IN PROGRESS**. Refined the LLM-driven planning in `_generate_plan` with a more structured and robust prompt, ensuring the LLM returns valid agent names for more reliable task delegation.
- **Deputy Agent**: **IN PROGRESS**. Implemented the initial `DeputyAgent` for background log monitoring. It runs in a separate thread and detects errors by tailing the log file.

## Phase 5: Monitoring & Security
- **Security Agent**: **COMPLETE**. The `SecurityAgent` is fully implemented as a process-isolated monitor. It dynamically receives rules from the GUI and can block goal execution in real-time based on those rules.
- **GUI Security Tab**: **COMPLETE**. The security tab now allows dynamic editing of security rules, which are sent to the `SecurityAgent` on save, enabling real-time policy updates.
- **Notification System**: **COMPLETE**. The `SecurityAgent` can now send alerts via Email, Telegram, and SMS (using placeholder handlers) when a rule is violated. Notification channels are dynamically configurable from the GUI.

## Phase 6: End-to-End Integration
- [x] **Full Workflow Testing**: Implemented and passed an end-to-end test (`test_full_workflow.py`) that validates multi-agent coordination, including plan generation, execution, and result chaining.
- **Performance Optimization**: **COMPLETE**. Profiled and optimized the `SecurityAgent`'s response latency, achieving an average of 0.11ms, well below the 100ms target.
- [x] **Error Recovery**: Implemented and tested Master Agent's ability to handle tool failures by replanning and retrying. The agent can now recover from task execution errors and complete its goals.

## Phase 7: Testing & Packaging
- [x] **Unit & Integration Tests**: Wrote comprehensive unit tests for all core, testable tools (`clipboard`, `notification`, `ocr`, `screenshot`, `image_recognition`, `terminal`).
- [x] **CI Setup**: Configured a GitHub Actions workflow (`ci.yml`) to automate linting, type checking, and testing on every push and pull request.
- [x] **Packaging**: Successfully created a standalone macOS app bundle using `pyinstaller`, resolving all dependency issues.
- [x] **Documentation**: Finalized README with detailed usage guides, build instructions, and architectural overview.

---

## Phase 8: Refinement & User Experience

Goal: Polish the application for a professional look and feel, improve usability, and prepare for a public release.

Tasks:
- **Application Icon**:
  - [x] Sourced and created a high-quality application icon (`.icns` format).
  - [x] Integrated the icon into the `pyinstaller` build process.
- **GUI Polish**:
  - [x] Refactored the entire GUI layout using the `.grid()` manager for consistent padding, alignment, and structure.
  - [x] Implement a visual loading indicator (progress bar) for long-running agent tasks.
- **User Settings**:
  - [x] Created a dedicated "Settings" tab by refactoring the old "Security" tab.
  - [x] Added GUI fields for users to configure API keys directly, removing the need to edit config files.
- **Release Management**:
  - [x] Created the `Atlas.app.zip` bundle, ready for release.
  - [x] Wrote clear release notes based on the `CHANGELOG.md`.

### Phase 8 Retrospective
*Phase 8 focused on polishing the user experience and preparing the application for its first distributable release. We successfully integrated a custom application icon, refactored the entire GUI for consistency, implemented a crucial loading indicator for agent tasks, and created a dedicated settings tab for API key management. The phase concluded with the successful packaging of the `.app` bundle and the drafting of release notes, marking a significant milestone in Atlas's maturity.*

---

## Phase 9: Advanced Features & Reliability

- **State Persistence & Resumption**:
  - [x] Save the complete application state (goals, prompts, chat history) on exit.
  - [x] Restore the previous state automatically on application launch.
- **Token Usage Monitoring**:
  - [x] Track and display token usage (prompt, completion, total) for each LLM call.
  - [x] Display cumulative token usage statistics in the Settings tab.
- **Plugin System Architecture**:
  - [x] Design a basic plugin architecture for adding new tools and agents dynamically.
  - [x] Create a sample plugin to demonstrate the new architecture (e.g., a simple weather tool).
- **Code Signing & Notarization (macOS)**:
  - [ ] **Research & Setup**:
    - [x] Research the end-to-end process for code signing and notarization.
    - [x] Document developer account and Xcode setup requirements.
    - [x] Create and store an app-specific password for the notarization tool (`altool`) in Keychain.
- [ ] **Build & Signing Process**:
    - [x] Create an `entitlements.plist` file for hardened runtime.
    - [x] Implement a build script (`build.sh`) that:
        - [x] Runs `pyinstaller` to create the `.app` bundle.
        - [x] Signs the bundled application using `codesign` with the Developer ID certificate.
- [x] **Packaging & Notarization**:
    - [x] Extend the build script to:
        - [x] Create a `.pkg` installer using `productbuild`.
        - [x] Submit the `.pkg` for notarization using `xcrun altool`.
        - [x] Document the manual steps for polling status and stapling the ticket.

### Phase 5: UI/UX Polish & Plugin Management

- **Plugin Management UI**:
  - [x] Design and implement a view in the Settings tab to list all discovered plugins.
  - [x] Add functionality to enable or disable individual plugins.
  - [x] Ensure the `PluginManager` respects the enabled/disabled state of plugins upon loading.
- **GUI Enhancements**:
  - [x] Redesign the main interaction panel to better display the conversation flow (user prompts, agent plans, execution results).
  - [x] Add syntax highlighting for code blocks in the agent's output.
- **Core Improvements**:
  - [x] Allow plugins to register custom agents, not just tools.
  - [x] Implement a more robust error recovery mechanism in the `MasterAgent`.

### Phase 6: Long-Term Memory & Advanced Agent Capabilities

- **Long-Term Memory Integration**:
    - [x] **Research & Select Vector Store**: Evaluate and choose a suitable local vector store library (e.g., ChromaDB, FAISS).
    - [x] **Implement Memory Manager**: Create a `MemoryManager` class responsible for storing, retrieving, and managing the agent's long-term memories.
    - [x] **Integrate with MasterAgent**:
        - [x] Automatically store key information (e.g., successful plans, user feedback) in long-term memory.
        - [x] Automatically retrieve relevant memories to inform plan generation.
- **Web Browsing Agent**:
    - [x] **Create Web Search Tool**: Develop a tool that can perform web searches and retrieve content from URLs.
    - [x] **Develop `WebSurferAgent`**: Create a new specialized agent that uses the web search tool to find up-to-date information.
    - [x] **Register as a Plugin**: Package the new agent and tool as a default plugin.
- **Developer Documentation**:
    - [x] **Update Plugin Docs**: Document the new process for creating and registering custom agents.
    - [x] **Document Memory System**: Explain how plugins can interact with the long-term memory system.

### Phase 7: Enhanced Agent Capabilities & User Interaction

- **Refine Agent Logic**:
    - [x] **Implement Agentic Loop in `WebSurferAgent`**: Replace the placeholder `execute` method with a true agentic loop that can chain tool calls (e.g., `web_search` -> `get_webpage_content` -> synthesize answer).
    - [x] **Improve `MasterAgent` Tool Integration**: Enhance the plan execution logic to allow the output of one tool to be used as the input for a subsequent tool.
- **User Interaction**:
    - [x] **Implement User Feedback Mechanism**: Add UI elements (e.g., thumbs up/down buttons) to allow the user to rate the agent's performance. Store this feedback in long-term memory.
    - [x] **Create Memory Viewer**: Develop a simple UI panel to allow the user to view and search the agent's long-term memories.

### Phase 8: Intelligence and Refinement

- **Agent Learning & Adaptation**:
    - [x] **Integrate Feedback into Planning**: Modify `MasterAgent` to query the `user_feedback` collection during plan generation. Use past feedback to avoid repeating failed plans and favor successful ones.
    - [x] **Proactive Memory Search**: Before generating a plan, have the `MasterAgent` automatically search its memory for information relevant to the current goal to enrich the planning context.
    - [x] **Implement Replanning on Failure**: Enhance the `_execute_plan` method to catch errors and trigger a replanning process, allowing the agent to recover from failed steps.
- **UI/UX Polish**:
    - [x] **Enhance Memory Viewer**: Add filtering by collection and sorting options to the Memory Viewer UI.

# Phase 9: Advanced Agent Capabilities & Infrastructure

- **Core Infrastructure**:
    - [x] **Standardize Memory Metadata**: Automatically add a `timestamp` to all memories upon creation in `MemoryManager` to ensure reliable date-based sorting and provide better traceability.
    - [x] **Configuration Management**: Introduce a `config.ini` or `config.json` file to manage settings like API keys and model names, removing hardcoded constants.
- **Advanced Agent Capabilities**:
    - [x] **Complex Goal Decomposition**: Enhance the `MasterAgent` to break down large, vague goals into smaller, manageable sub-goals, enabling it to tackle more complex problems.
    - [x] **Dynamic Tool Creation**: Implement an agent that can write, validate, and save new Python tool functions on the fly. The `AgentManager` should be able to dynamically load these new tools.
- **UI/UX Polish**:
    - [x] **Interactive Plan View**: Display the agent's plan in the UI and highlight the currently executing step to improve transparency.
    - [x] **Settings UI**: Create a dedicated tab for managing application settings (API keys, notifications, etc.).

### Phase 8: Advanced Environmental Interaction
- **Core Intelligence**:
    - [ ] **Refine Main Agent Loop**: Implement a more robust main loop in `MasterAgent` that can better handle errors, retry failed steps with modified approaches, and solicit user feedback when truly stuck.
- **Agent Capabilities**:
    - [ ] **Implement Screen Agent**: Flesh out the `ScreenAgent` with vision capabilities to understand GUI elements from screenshots and execute actions like clicking and typing at specific coordinates or on identified elements.
    - [ ] **Implement Browser Agent**: Flesh out the `BrowserAgent` with tools to control a web browser (e.g., using Selenium/Playwright) for tasks like navigation, scraping, and form submission.
- **UI/UX Polish**:
    - [ ] **Agent-Specific Controls**: In the "Agents" tab, add controls to configure or view the status of the new Screen and Browser agents (e.g., view what the browser agent sees).
