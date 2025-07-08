---
description: Development workflow protocols for Atlas - a modern modular AI platform with cyberpunk PySide6 interface. Ensures continuous execution and autonomous progression without development interruptions.
---

# Atlas Development Workflow Protocols

## Program Overview

**Atlas** is a modern modular AI platform designed as a cyberpunk-styled desktop application built with PySide6. The program serves as an extensible AI workspace featuring:

### Core Application Features (POST-MIGRATION)
- **✅ MIGRATION COMPLETED**: All components consolidated into unified `atlas/` package
- **Cyberpunk PySide6 Interface**: Dark theme with modern aesthetics and responsive design
- **Modular Architecture**: Separate modules for Chat, Tasks, Agents, Plugins, Settings, and Statistics
- **Plugin Ecosystem**: Dynamic plugin loading system with hot-reload capabilities
- **AI Integration**: Multiple AI providers and autonomous operation capabilities
- **Self-Improvement System**: Automated learning from interactions and experience accumulation
- **Long-Term Memory**: Vector-based memory storage with ChromaDB for context-aware operations
- **Self-Healing Capabilities**: Automated diagnosis and component regeneration
- **Cross-platform Support**: Optimized for macOS with Apple Silicon compatibility

### Application Launch (NEW UNIFIED APPROACH)
```bash
# Primary method after migration
python -m atlas.main

# Alternative through pip installation
pip install -e .
atlas

# VS Code debugging
# Launch configuration: "module": "atlas.main"
```

### Target Architecture Structure (MIGRATED - FINAL STATE)
```
Atlas/
├── .github/              # GitHub workflows, templates
├── .idea/                # IDE налаштування
├── .venv/                # Віртуальне середовище
├── .vscode/              # VS Code налаштування
├── .windsurf/            # Windsurf IDE налаштування
│
├── atlas/                # 📦 ОСНОВНИЙ ПАКЕТ ПРОГРАМИ (UNIFIED STRUCTURE)
│   ├── __init__.py
│   ├── main.py             # 🚀 Точка входу
│   │
│   ├── assets/             # 🎨 Іконки, стилі, шрифти, локалізація
│   ├── core/               # ⚙️ Ядро (Application, EventBus, Systems)
│   │   ├── application.py      # AtlasApplication main class
│   │   ├── config.py          # Configuration management
│   │   ├── event_bus.py        # Event distribution system
│   │   ├── module_registry.py # Module registry system
│   │   ├── plugin_system.py   # Plugin management system
│   │   ├── self_healing.py     # Self-healing and auto-recovery
│   │   ├── agents/            # Meta-agent system components
│   │   ├── ethics/            # Ethics and safety systems
│   │   ├── intelligence/      # Core AI systems
│   │   ├── memory/            # Core memory systems
│   │   ├── plugins/           # Core plugin components
│   │   └── tools/             # Core tool systems
│   │
│   ├── agents/             # 🧠 AI агенти та інтелект
│   │   ├── agent_loop_manager.py
│   │   ├── context_engine.py
│   │   ├── decision_engine.py
│   │   ├── meta_agent.py
│   │   └── self_improvement_engine.py
│   │
│   ├── memory/             # 🧬 Система пам'яті та контексту
│   │   ├── chromadb_manager.py
│   │   └── memory_manager.py
│   │
│   ├── plugins/            # 🧩 Система плагінів
│   │   └── plugin_manager.py
│   │
│   ├── tools/              # 🛠️ Інструменти та утиліти
│   │   ├── base_tool.py       # BaseTool abstract class
│   │   ├── browser.py         # Browser automation tool
│   │   ├── terminal_tool.py   # Terminal integration tool
│   │   ├── screenshot_tool.py # Screenshot capture tool
│   │   └── {tool_name}.py     # Individual tool implementations
│   │
│   ├── ui/                 # 🖼️ Графічний інтерфейс (PySide6) - UNIFIED INTERFACE
│   │   ├── chat/              # Chat interface module
│   │   ├── tasks/             # Task management module
│   │   ├── agents/            # Agent control module
│   │   ├── plugins/           # Plugin management UI
│   │   ├── settings/          # Configuration interface
│   │   ├── tools/             # Tools management UI
│   │   ├── workflows/         # Workflow interface
│   │   ├── memory/            # Memory management UI
│   │   ├── self_improvement/  # Self-improvement center UI
│   │   ├── stats/             # Statistics and analytics
│   │   └── main_window.py     # Main application window
│   │
│   ├── workflows/          # 🔄 Система робочих процесів
│   │   ├── engine.py          # Workflow execution engine
│   │   ├── execution.py       # Workflow execution logic
│   │   └── natural_language_workflow.py # NL workflow processing
│   │
│   └── utils/              # 🔧 Допоміжні утиліти
│       ├── memory_management.py # Long-term memory system
│       ├── llm_manager.py     # LLM provider management
│       └── cache_manager.py   # Caching and optimization
│
├── config/               # ✅ Шаблони конфігурацій (default.json, schema.json)
├── data/                 # ✅ Приклади даних, шаблони для розробки
├── docs/                 # 📚 Документація
├── scripts/              # 📜 Скрипти (збірка, аналіз, деплой)
├── tests/                # 🧪 Тести
├── user/                 # 👤 Користувацькі дані та налаштування
│
├── .gitignore
├── CHANGELOG.md
├── DEV_PLAN.md           # 📋 План розробки та міграції
├── LICENSE
├── README.md
└── pyproject.toml        # 📦 Конфігурація проєкту
```

## Development Environment Specifications

**Primary Development Platform:**
- **Hardware**: Mac Studio M1 Max with 32GB unified memory
- **Operating System**: macOS (ARM64 architecture)
- **Python Version**: 3.9+ (compatible with Python 3.9 through 3.12)
- **UI Framework**: PySide6 with qdarkstyle theming
- **Architecture**: ARM64 native optimization with x64 compatibility

**Required Dependencies:**
- PySide6 for modern Qt6-based UI components
- qdarkstyle for cyberpunk dark theme styling
- markdown2 for rich text rendering
- ChromaDB for vector-based long-term memory storage
- LLM integration libraries for AI capabilities
- Additional plugin-specific dependencies as needed

## Core System Architecture

**Intelligence Layer:**
- **Context Awareness Engine**: Understanding user intent and environmental context
- **LLM Manager**: Multi-provider AI integration with fallback mechanisms
- **Memory Management**: Vector-based long-term memory with ChromaDB storage
- **Meta-Agent System**: Autonomous planning and execution coordination

**Self-Improvement Mechanisms:**
- **Experience Accumulation**: Learning from successful and failed interactions
- **Pattern Recognition**: Identifying recurring user workflows and preferences
- **Adaptive Optimization**: Automatic performance tuning based on usage patterns
- **Self-Healing**: Automated diagnosis and regeneration of corrupted components

## Core Principles

### 🚨 CRITICAL INTERFACE COMPLIANCE (RESOLVED)
- **✅ UNIFIED INTERFACE ACHIEVED**: Migration to PySide6-only architecture completed
- **✅ PyQt5 ELIMINATION**: All PyQt5 imports successfully removed during migration
- **✅ NO LEGACY DEPENDENCIES**: Clean atlas/ package with pure PySide6 implementation
- **✅ APPLICATION STARTUP**: Fixed through complete package restructuring
- **Interface Standard**: Only PySide6 imports allowed throughout the codebase
- **Migration Benefit**: Eliminated all Qt framework conflicts and version mismatches

### 🎯 MIGRATION SUCCESS INDICATORS
- **✅ Package Structure**: Single `atlas/` package with all modules
- **✅ Import Consistency**: All imports use `from atlas.` prefix
- **✅ UI Framework**: Pure PySide6 implementation without legacy tkinter/PyQt5
- **✅ Entry Point**: `python -m atlas.main` works correctly
- **✅ Module Loading**: All UI modules load without import errors
- **✅ Configuration**: VS Code, pyproject.toml updated for new structure

### 1. Never-Stop Execution
- **Continuous progression**: Development never pauses regardless of errors, unclear requirements, or missing dependencies
- **Auto-recovery**: Automatically implement missing components, fix errors, and continue execution
- **Forward momentum**: Always progress toward the next logical milestone without requiring manual intervention

### 2. Vision-First Development
- **Target-state thinking**: Develop as if the target architecture already exists
- **Gap identification**: Automatically detect and bridge gaps between current and target state
- **Proactive evolution**: Anticipate needs and implement solutions before they become blockers

### 3. Adaptive Standards
- **Code language**: English for all code, comments, and technical documentation
- **UI language**: Multilingual support (Ukrainian default, Russian, English)
- **Quality gates**: Automated linting, type checking, and testing
- **Performance benchmarks**: <100ms UI operations, <500ms planning, <200ms memory operations

### 4. Autonomous Decision Making
- **No confirmation required**: Make all necessary development decisions automatically
- **Best practices**: Apply established patterns from the codebase
- **Error resolution**: Fix issues inline without stopping development flow

## Execution Protocol

### Phase 1: Situational Assessment
1. **Analyze current state** - Understand existing codebase and architecture
2. **Identify objectives** - Determine next logical development steps
3. **Detect gaps** - Find missing components or outdated implementations
4. **Prioritize actions** - Select the highest-impact next step

### Phase 2: Continuous Development
1. **Implement progressively** - Build toward target architecture incrementally
2. **Auto-fix issues** - Resolve errors, missing imports, or dependencies inline
3. **Maintain quality** - Apply linting, type checking, and testing continuously
4. **Document progress** - Update relevant documentation and comments

### Phase 3: Quality Assurance
1. **Validate changes** - Ensure new code meets quality standards
2. **Test functionality** - Verify components work as expected
3. **Performance check** - Monitor and optimize for target benchmarks
4. **Security review** - Validate secure coding practices

### Phase 4: Progression Management
1. **Continue execution** - Immediately proceed to next task without pause
2. **Expand scope** - Add new objectives when current ones are completed
3. **Never stop** - Maintain continuous development momentum
4. **Adapt approach** - Modify strategy based on emerging requirements

## Adaptive Implementation Patterns

### Target Architecture Patterns (POST-MIGRATION STATE)

**Application Entry Point:**
```bash
# New unified entry point after migration
python -m atlas.main

# Alternative through pip installation
pip install -e .
atlas
```

**Core Application Structure (MIGRATED & FINAL):**
```
atlas/                      # 📦 UNIFIED PACKAGE STRUCTURE
├── main.py                 # Entry point with PySide6 initialization
├── core/                   # Core system components (CONSOLIDATED)
│   ├── application.py      # AtlasApplication main class
│   ├── config.py          # Configuration management
│   ├── event_bus.py        # Event system
│   ├── self_healing.py     # Self-healing mechanisms
│   ├── agents/            # Meta-agent system components
│   ├── ethics/            # Ethics and safety systems
│   ├── intelligence/      # Core AI systems
│   ├── memory/            # Core memory components
│   ├── plugins/           # Core plugin infrastructure
│   └── tools/             # Core tool systems
├── ui/                     # PySide6 UI modules (UNIFIED INTERFACE)
│   ├── main_window.py     # Main application window
│   ├── chat/              # Chat interface components
│   ├── tasks/             # Task management UI
│   ├── agents/            # Agent control panels
│   ├── plugins/           # Plugin management UI
│   ├── memory/            # Memory management UI
│   ├── self_improvement/  # Self-improvement center UI
│   ├── tools/             # Tools management UI
│   ├── workflows/         # Workflow interface
│   └── settings/          # Configuration UI
├── agents/                # AI and learning systems (DEDICATED MODULE)
│   ├── agent_loop_manager.py
│   ├── context_engine.py
│   ├── decision_engine.py
│   ├── meta_agent.py
│   └── self_improvement_engine.py
├── memory/                # Memory systems (DEDICATED MODULE)
│   ├── chromadb_manager.py
│   └── memory_manager.py
├── tools/                 # Tool ecosystem (CONSOLIDATED)
│   ├── base_tool.py       # BaseTool abstract class
│   ├── browser.py         # Browser automation
│   ├── terminal_tool.py   # Terminal integration
│   └── {tool_name}.py     # Individual tools
├── plugins/               # Plugin ecosystem (DEDICATED MODULE)
│   ├── plugin_manager.py  # Plugin management
│   └── {plugin_name}/     # Individual plugins
├── workflows/             # Workflow management (DEDICATED MODULE)
│   ├── engine.py          # Workflow execution engine
│   └── execution.py       # Workflow execution logic
└── utils/                 # Core utilities (CONSOLIDATED)
    ├── memory_management.py # Long-term memory system
    ├── llm_manager.py     # LLM provider management
    └── cache_manager.py   # Performance optimization
```

**Component Migration Strategy (COMPLETED):**
- **Status**: ✅ MIGRATION COMPLETED SUCCESSFULLY
- **From**: Distributed structure (core/, ui/, tools/, utils/, assets/ in root)
- **To**: atlas/ unified package (PySide6 with cyberpunk styling)
- **Method**: Complete consolidation with API compatibility maintained
- **Result**: Single `atlas/` package with all components properly organized

**Plugin Architecture (FINAL STATE):**
- **Base class**: PluginBase with lifecycle hooks in `atlas/plugins/`
- **Auto-discovery**: Dynamic loading from `atlas/plugins/` directory
- **UI integration**: get_widget() method for tool embedding in PySide6
- **Core integration**: Event bus system for plugin communication

**Import Strategy (POST-MIGRATION):**
```python
# New import structure after migration
from atlas.core.application import AtlasApplication
from atlas.ui.main_window import MainWindow
from atlas.tools.base_tool import BaseTool
from atlas.agents.meta_agent import MetaAgent
from atlas.memory.memory_manager import MemoryManager
```

### Error Recovery Mechanisms

**Automatic Problem Resolution:**
1. **Import errors** → Create missing modules with basic structure
2. **Missing methods** → Implement with reasonable defaults
3. **Test failures** → Fix issues and continue execution
4. **Type errors** → Add proper type hints and fixes
5. **Performance issues** → Implement optimizations or fallbacks

**Continuous Execution Guarantees (POST-MIGRATION):**
- ✅ No manual intervention required
- ✅ Auto-progression through development tasks completed
- ✅ All critical import conflicts resolved
- ✅ Unified package structure eliminates module discovery issues
- ✅ Emergency override protocols proven during migration
- ✅ Clean codebase ready for feature development

## Quality Standards

**Code Quality Checks:**
- `ruff check` for linting and formatting
- `mypy` for type checking (Python 3.9+ compatible)
- `pytest` with ≥90% coverage
- Performance benchmarks within target ranges

**Security Requirements:**
- Environment variables for sensitive data
- Input validation and sanitization
- Secure coding practices
- Authentication for privileged operations

## Execution Directives (MISSION ACCOMPLISHED STATUS)

**✅ NEVER-STOP MANDATE COMPLETED**: Major structural challenges resolved:
- ✅ All critical errors and exceptions fixed during migration
- ✅ Missing dependencies and import conflicts eliminated
- ✅ Package structure requirements clarified and implemented
- ✅ Core architecture tests passing
- ✅ Performance baseline established

**✅ AUTO-PROGRESSION PROTOCOL EXECUTED**:
1. ✅ All migration tasks completed successfully
2. ✅ Next phase: Feature development and code quality improvements
3. ✅ Continuous forward momentum maintained throughout migration
4. ✅ Scope expanded to include comprehensive project cleanup

**✅ VISION-DRIVEN ADAPTATION ACHIEVED**:
- ✅ Target architecture successfully implemented in `atlas/` package
- ✅ All gaps between current and desired state bridged
- ✅ Required infrastructure implemented and tested
- ✅ Codebase evolution completed - cyberpunk AI platform vision realized

**NEXT DEVELOPMENT PHASE**: Focus on feature enhancement, performance optimization, and advanced AI capabilities within the established unified architecture.

This protocol has successfully guided Atlas through complete structural transformation, achieving a modern, modular AI platform with cyberpunk aesthetics and autonomous capabilities, ready for advanced feature development.
