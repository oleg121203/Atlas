---
description: Development workflow protocols for Atlas - a modern modular AI platform with cyberpunk PySide6 interface. Ensures continuous execution and autonomous progression without development interruptions.
---

# Atlas Development Workflow Protocols

## Program Overview

**Atlas** is a modern modular AI platform designed as a cyberpunk-styled desktop application built with PySide6. The program serves as an extensible AI workspace featuring:

### Core Application Features
- **Cyberpunk PySide6 Interface**: Dark theme with modern aesthetics and responsive design
- **Modular Architecture**: Separate modules for Chat, Tasks, Agents, Plugins, Settings, and Statistics
- **Plugin Ecosystem**: Dynamic plugin loading system with hot-reload capabilities
- **AI Integration**: Multiple AI providers and autonomous operation capabilities
- **Self-Improvement System**: Automated learning from interactions and experience accumulation
- **Long-Term Memory**: Vector-based memory storage with ChromaDB for context-aware operations
- **Self-Healing Capabilities**: Automated diagnosis and component regeneration
- **Cross-platform Support**: Optimized for macOS with Apple Silicon compatibility

### Target Architecture Structure
```
atlas/
├── main.py                 # Application entry point
├── core/                   # Core system components
│   ├── application.py      # AtlasApplication main class
│   ├── config.py          # Configuration management
│   ├── event_bus.py        # Event distribution system
│   ├── module_registry.py # Module registry system
│   ├── plugin_system.py   # Plugin management system
│   ├── self_healing.py     # Self-healing and auto-recovery
│   └── agents/            # Meta-agent system
├── ui/                     # PySide6 UI components (UNIFIED INTERFACE)
│   ├── chat/              # Chat interface module
│   ├── tasks/             # Task management module
│   ├── agents/            # Agent control module
│   ├── plugins/           # Plugin management UI
│   ├── settings/          # Configuration interface
│   ├── tools/             # Tools management UI
│   ├── workflow/          # Workflow interface
│   ├── memory/            # Memory management UI
│   ├── self_improvement/  # Self-improvement center UI
│   └── stats/             # Statistics and analytics
├── tools/                 # Tool ecosystem
│   ├── base_tool.py       # BaseTool abstract class
│   ├── browser.py         # Browser automation tool
│   ├── terminal_tool.py   # Terminal integration tool
│   ├── screenshot_tool.py # Screenshot capture tool
│   └── {tool_name}.py     # Individual tool implementations
├── workflow/              # Workflow management system
│   ├── engine.py          # Workflow execution engine
│   ├── execution.py       # Workflow execution logic
│   └── natural_language_workflow.py # NL workflow processing
├── intelligence/          # AI and context awareness
│   ├── context_awareness_engine.py # Context understanding
│   └── llm.py             # LLM integration
├── utils/                 # Utilities and management
│   ├── memory_management.py # Long-term memory system
│   ├── llm_manager.py     # LLM provider management
│   └── cache_manager.py   # Caching and optimization
└── plugins/               # Plugin ecosystem
    ├── base.py            # PluginBase abstract class
    └── {plugin_name}/     # Individual plugin packages
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

### Target Architecture Patterns

**Core Application Structure:**
```
atlas/
├── main.py                 # Entry point with PySide6 initialization
├── core/                   # Core system components
│   ├── application.py      # AtlasApplication main class
│   ├── config_manager.py   # Configuration management
│   ├── event_bus.py        # Event system
│   ├── self_healing.py     # Self-healing mechanisms
│   ├── agents/            # Meta-agent system
│   └── registries/         # Module and plugin registries
├── ui/                     # PySide6 UI modules
│   ├── chat/              # Chat interface components
│   ├── tasks/             # Task management UI
│   ├── agents/            # Agent control panels
│   ├── plugins/           # Plugin management UI
│   ├── memory/            # Memory management UI
│   ├── self_improvement/  # Self-improvement center UI
│   └── settings/          # Configuration UI
├── intelligence/          # AI and learning systems
│   ├── context_awareness_engine.py # Context understanding
│   └── llm.py             # LLM integration
├── utils/                 # Core utilities
│   ├── memory_management.py # Long-term memory system
│   ├── llm_manager.py     # LLM provider management
│   └── cache_manager.py   # Performance optimization
└── plugins/               # Plugin ecosystem
    ├── base.py            # PluginBase class
    └── {plugin_name}/     # Individual plugins
```

**Component Migration Strategy:**
- **From**: backup_ui/ (tkinter/customtkinter)
- **To**: ui/ (PySide6 with cyberpunk styling)
- **Method**: Progressive replacement maintaining API compatibility

**Plugin Architecture:**
- **Base class**: PluginBase with lifecycle hooks
- **Auto-discovery**: Dynamic loading from plugins/ directory
- **UI integration**: get_widget() method for tool embedding

### Error Recovery Mechanisms

**Automatic Problem Resolution:**
1. **Import errors** → Create missing modules with basic structure
2. **Missing methods** → Implement with reasonable defaults
3. **Test failures** → Fix issues and continue execution
4. **Type errors** → Add proper type hints and fixes
5. **Performance issues** → Implement optimizations or fallbacks

**Continuous Execution Guarantees:**
- No manual intervention required
- Auto-progression through development tasks
- Intelligent context switching when blocked
- Emergency override protocols for critical situations

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

## Execution Directives

**NEVER-STOP MANDATE**: Development continues regardless of:
- Errors or exceptions
- Missing dependencies or imports
- Unclear requirements
- Test failures
- Performance issues

**AUTO-PROGRESSION PROTOCOL**: 
1. Complete current task or auto-fix blocking issues
2. Immediately begin next logical development step
3. Maintain continuous forward momentum
4. Expand scope when current objectives are met

**VISION-DRIVEN ADAPTATION**:
- Develop toward target architecture as if it already exists
- Bridge gaps between current and desired state
- Anticipate and implement required infrastructure
- Evolve codebase progressively toward the cyberpunk AI platform vision

This protocol ensures Atlas evolves continuously toward its target state as a modern, modular AI platform with cyberpunk aesthetics and autonomous capabilities, never stopping until the complete vision is realized.