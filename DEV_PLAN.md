# UI Components Migration Plan from tkinter/customtkinter to PySide6

**UNIFIED INTERFACE**: PySide6 - the only UI framework for the entire application

## Atlas Target Architecture

```
atlas/
├── main.py                 # Application entry point (PySide6)
├── core/                   # Core system components
│   ├── application.py      # AtlasApplication main class
│   ├── config.py          # Configuration management
│   ├── event_bus.py        # Event system
│   ├── module_registry.py # Module registry
│   ├── plugin_system.py   # Plugin system
│   ├── self_healing.py     # Self-healing and auto-recovery
│   └── agents/            # Meta-agent system
├── ui/                     # PySide6 UI components (UNIFIED INTERFACE)
│   ├── chat/              # Chat module
│   ├── tasks/             # Tasks module  
│   ├── agents/            # Agents module
│   ├── plugins/           # Plugin management UI
│   ├── settings/          # Settings interface
│   ├── tools/             # Tools management UI
│   ├── workflow/          # Workflow UI
│   ├── memory/            # Memory management UI
│   ├── self_improvement/  # Self-improvement center UI
│   ├── themes/            # Theme system and switcher
│   ├── developer/         # Developer tools integration
│   ├── context/           # Context awareness engine UI
│   └── stats/             # Statistics and analytics
├── tools/                 # Tools ecosystem
│   ├── base_tool.py       # Base tool class
│   ├── browser.py         # Browser tool
│   ├── terminal_tool.py   # Terminal tool
│   ├── screenshot_tool.py # Screenshot tool
│   └── {tool_name}.py     # Individual tools
├── workflow/              # Workflow management system
│   ├── engine.py          # Workflow engine
│   ├── execution.py       # Process execution
│   └── natural_language_workflow.py # NL workflows
├── intelligence/          # AI and context awareness
│   ├── context_awareness_engine.py # Context understanding
│   └── llm.py             # LLM integration
├── utils/                 # Core utilities
│   ├── memory_management.py # Long-term memory system
│   ├── llm_manager.py     # LLM provider management
│   └── cache_manager.py   # Performance optimization
└── plugins/               # Plugin ecosystem (to create)
    ├── base.py            # PluginBase abstract class
    └── {plugin_name}/     # Individual plugin packages
```

Of course. Here is the modified development plan, focused on the first and most critical stage of getting the application to a stable, runnable state.

This plan addresses the immediate startup errors and begins to align the codebase with the target architecture. This is your first package of tasks.

---

# DEV_PLAN.md: Stage 1 - Application Startup & Core Stabilization

**Objective**: Resolve all critical startup errors and establish a stable application foundation that aligns with the unified PySide6 architecture. This phase will focus on making the application launch successfully without crashes.

---

## **Phase 1: Critical Startup and Architecture Fixes**

### **Sub-Phase 1.1: Fix Blocking Startup Errors**

These tasks are the absolute highest priority to get the application running.

* [ ] **1. Resolve PyQt5 Conflict:**
    * **File**: `ui/ai_assistant_widget.py`
    * **Task**: Remove the `from PyQt5.QtCore import pyqtSignal` import and replace it with the correct PySide6 equivalent: `from PySide6.QtCore import Signal`. This resolves the primary `ModuleNotFoundError`.

* [ ] **2. Create Missing Core Modules & Files:**
    * Create the following missing files with basic placeholder classes/functions to resolve `ImportError` exceptions at startup:
        * `debugging/debugging_hooks.py` (with a `DebuggingHooks` class)
        * `performance/performance_monitor.py` (with a `PerformanceMonitor` class)
        * `sentry_config.py` (with an `init_sentry` function)

* [ ] **3. Fix `main_window.py` Critical Errors:**
    * **Fix `QAction` Import**: Change the import from `PySide6.QtWidgets` to `from PySide6.QtGui import QAction`.
    * **Fix `Qt` Constants**: Update all `Qt` constants to use the new enum-based access (e.g., `Qt.Vertical` becomes `Qt.Orientation.Vertical`, `Qt.TopToolBarArea` becomes `Qt.ToolBarArea.TopToolBarArea`).
    * **Initialize Missing Attributes**: In the `AtlasMainWindow` constructor (`__init__`), add initializations for `self.main_layout`, `self.logger`, and `self.theme_manager` to prevent `AttributeError` crashes.

### **Sub-Phase 1.2: Core Architecture Alignment**

With the immediate startup crashes resolved, the next step is to align the core structure with the target architecture.

* [ ] **1. Restructure `main.py`:**
    * **Task**: Create `core/application.py` and move the core `AtlasApplication` logic into it. The `main.py` file should now be a simple entry point that initializes and runs `AtlasApplication`.
    * **Task**: Remove hardcoded references like `task_view` from the main application class. These will be replaced by a proper module loading system.

* [ ] **2. Create Core System Modules:**
    * Create the following essential core modules with basic class structures:
        * `core/module_registry.py` (for managing UI and backend modules)
        * `core/plugin_system.py` (for the plugin architecture)
        * `core/self_healing.py` (for auto-recovery mechanisms)

* [ ] **3. Organize UI Module Structure:**
    * **Task**: Begin restructuring the `ui/` directory. Move the existing UI files into the appropriate subdirectories (`chat/`, `tasks/`, `agents/`, etc.) as defined in the target architecture.
    * **Task**: Create `__init__.py` files in each new UI subdirectory to ensure they are recognized as Python packages.
    * **Task**: Update all import paths in the moved files to reflect their new locations.

---

## **Next Steps After This Package**

Once all tasks in this first package are complete, the application should start without crashing. At that point, contact me again, and we will proceed to the next package of tasks, which will focus on:

1.  **Implementing the `event_bus`** for communication between modules.
2.  **Fixing and integrating the intelligence and memory systems.**
3.  **Repairing the tools ecosystem and their UI integrations.**

This step-by-step approach will ensure we build on a stable foundation.