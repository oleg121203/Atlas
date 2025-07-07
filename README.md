# Atlas (PySide6 Cyberpunk Edition)

[English Version Below](#english-version)

Atlas — сучасна модульна AI-платформа з кіберпанк-дизайном, розширюваністю через плагіни та тулси.

## Системні вимоги
- **Python**: 3.9.2+
- **Інтерфейс**: PySide6

## Основні особливості
- PySide6 + qdarkstyle (темний кіберпанк-інтерфейс)
- Модульна архітектура: Chat, Tasks, Agents, Plugins, Settings, Stats
- Плагінна система: тулси для Chat, Tasks, Agents, ...
- Drag&Drop, автозбереження, markdown, emoji, автокомпліт
- Легко розширюється через нові плагіни (plugins/)
- Оптимізовано для Mac Studio M1 Max 32GB

## Структура
- **AtlasApplication**: Головний клас програми, відповідальний за ініціалізацію, управління життєвим циклом та інтеграцію компонентів.
- **ConfigManager**: Керує конфігурацією програми з підтримкою середовищно-залежних налаштувань та перевірки JSON-схеми.
- **EventBus**: Обробляє розповсюдження подій по всій програмі для відокремленого спілкування між компонентами.
- **ModuleRegistry**: Керує реєстрацією та життєвим циклом модулів програми.
- **PluginRegistry**: Відкриває, завантажує та керує плагінами з хуками життєвого циклу (ініціалізація, запуск, зупинка, завершення роботи).
- `main.py` — точка входу (PySide6 UI)
- `ui/` — всі QWidget-модулі (chat, tasks, agents, plugins, settings, stats, plugin_manager)
- `plugins/` — плагіни (кожен — клас-нащадок PluginBase)

## Запуск
1. Встанови залежності:
   ```bash
   pip install -r requirements.txt
   pip install PySide6 qdarkstyle markdown2
   ```
2. Запусти:
   ```bash
   python main.py
   ```

## 🚀 Windsurf Development Commands
Для швидкого продовження розробки в Windsurf Chat використовуй команди з файлу:
**[WINDSURF_COMMANDS.md](WINDSURF_COMMANDS.md)** - Всі команди для автоматичного виконання DEV_PLAN.md

### 🚨 Phase 14: Critical Error Resolution
**[PHASE14_QUICKSTART.md](PHASE14_QUICKSTART.md)** - Негайне виправлення критичних помилок запуску

### Швидкий старт Phase 14:
```
/chat Fix critical startup errors in Atlas main.py - create missing debugging/debugging_hooks.py, performance/performance_monitor.py, performance/latency_analyzer.py, and sentry_config.py modules with proper class implementations to resolve import errors
```

### Повна автоматизація:
```
ATLAS_AUTO_EXECUTE
```
Ця команда автоматично продовжить розробку з поточного етапу згідно з протоколами.

## Розширення
- Додавай нові плагіни у `plugins/` (метод get_widget для тулса)
- Плагіни автоматично зʼявляються у відповідних модулях після активації
- API плагінів дозволяє взаємодіяти з ядром, UI, іншими модулями

---

<a name="english-version"></a>
# Atlas (PySide6 Cyberpunk Edition) - English Version

Atlas is a modern modular AI platform with cyberpunk design, extensibility through plugins and tools.
# Atlas - AI Assistant Platform

**Atlas** is a modular AI assistant platform built with Python and PySide6, featuring a modern cyberpunk interface, plugin ecosystem, and powerful tool integration.

## Features

- **Modern UI**: Sleek cyberpunk design built with PySide6
- **Modular Architecture**: Core systems for plugins, tools, workflows, and agents
- **Performance Monitoring**: Built-in performance tracking and optimization
- **Self-Healing**: Automatic recovery from errors and component failures
- **Plugin System**: Extensible plugin architecture for custom functionality
- **Tool Ecosystem**: Powerful tools for browsing, terminal access, screenshots, and more
- **Workflow Engine**: Define and automate complex workflows
- **Event System**: Reactive architecture with publish-subscribe pattern

## System Requirements

- Python 3.9.2+
- PySide6
- Mac Studio M1 Max 32GB (optimized for)
- macOS Sequoia (optimized for)

## Installation

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Architecture

Atlas is built with a modular architecture centered around these core components:

- **AtlasApplication**: Central application class managing all components
- **EventBus**: Publish-subscribe system for loosely coupled communication
- **ModuleRegistry**: Registry of all loaded modules
- **PluginSystem**: System for discovering, loading, and managing plugins
- **ToolManager**: System for registering and executing tools
- **SelfHealingSystem**: System for automatic recovery from errors

UI components are built exclusively with PySide6 and follow a consistent cyberpunk theme.

## Development

Atlas follows these development practices:

- **Testing**: Comprehensive unit tests for all core components
- **Performance**: Regular performance benchmarking and optimization
- **Documentation**: Detailed docstrings and module documentation
- **Error Handling**: Robust error handling and reporting via Sentry

## Extending Atlas

### Creating Plugins

Plugins should be created as Python packages with these required components:

```python
# myplugin/__init__.py
def activate():
    """Called when the plugin is activated."""
    print("Plugin activated!")

def deactivate():
    """Called when the plugin is deactivated."""
    print("Plugin deactivated!")
```

### Creating Tools

Tools are classes that extend the BaseTool class:

```python
from tools.base_tool import BaseTool

class MyTool(BaseTool):
    TOOL_NAME = "my_tool"

    def __init__(self, event_bus):
        super().__init__(event_bus)

    def initialize(self):
        """Initialize the tool."""
        pass

    async def execute(self, **kwargs):
        """Execute the tool."""
        return {"result": "Tool executed!"}

    def shutdown(self):
        """Clean up resources."""
        pass
```

## License

Proprietary - All rights reserved

## Contact

For questions or support, please contact the development team.
## Key Features
- PySide6 + qdarkstyle (dark cyberpunk interface)
- Modular architecture: Chat, Tasks, Agents, Plugins, Settings, Stats
- Plugin system: tools for Chat, Tasks, Agents, ...
- Drag&Drop, auto-save, markdown, emoji, autocomplete
- Easily extendable through new plugins (plugins/)
- Optimized for Mac Studio M1 Max 32GB

## Structure
- **AtlasApplication**: The main application class responsible for initialization, lifecycle management, and integration of components.
- **ConfigManager**: Manages application configuration with support for environment-based settings and JSON schema validation.
- **EventBus**: Handles event distribution across the application for decoupled communication between components.
- **ModuleRegistry**: Manages the registration and lifecycle of application modules.
- **PluginRegistry**: Discovers, loads, and manages plugins with lifecycle hooks (initialize, start, stop, shutdown).
- `main.py` — entry point (PySide6 UI)
- `ui/` — all QWidget modules (chat, tasks, agents, plugins, settings, stats, plugin_manager)
- `plugins/` — plugins (each one is a PluginBase child class)

## Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install PySide6 qdarkstyle markdown2
   ```
2. Run:
   ```bash
   python main.py
   ```

## 🚀 Windsurf Development Commands
For quick development continuation in Windsurf Chat, use commands from:
**[WINDSURF_COMMANDS.md](WINDSURF_COMMANDS.md)** - All commands for automatic DEV_PLAN.md execution

### 🚨 Phase 14: Critical Error Resolution
**[PHASE14_QUICKSTART.md](PHASE14_QUICKSTART.md)** - Immediate critical startup error fixes

### Quick Start Phase 14:
```
/chat Fix critical startup errors in Atlas main.py - create missing debugging/debugging_hooks.py, performance/performance_monitor.py, performance/latency_analyzer.py, and sentry_config.py modules with proper class implementations to resolve import errors
```

### Full Automation:
```
ATLAS_AUTO_EXECUTE
```
This command automatically continues development from current stage following protocols.

## Extension
- Add new plugins in `plugins/` (get_widget method for tools)
- Plugins automatically appear in corresponding modules after activation
- Plugin API allows interaction with core, UI, other modules

---

# Atlas Project

Atlas is a comprehensive workflow management and analytics platform optimized for macOS Apple Silicon (M1 Max 32GB). It provides advanced features for workflow execution, monitoring, and optimization.

## Key Features

- **Workflow Execution Analytics (WFE-008)**: Detailed performance metrics, bottleneck visualization with heatmaps, customizable dashboards, comparative analytics across teams/users, and predictive failure analysis.
- **User Satisfaction Monitoring (WFE-007)**: Net Promoter Score (NPS) collection, in-app feedback mechanism with sentiment analysis, and comprehensive analytics dashboard for satisfaction metrics.
- **Complex Workflow Testing Framework (WFE-009)**: Unit tests for individual workflow steps, integration tests for entire processes, mocking of external dependencies, test data generation, and test coverage analysis.
- **Workflow Optimization Recommendations (WFE-010)**: Analysis of historical performance data, integration of user feedback, intelligent recommendations for step reordering/parallelization, resource allocation suggestions, and impact evaluation over time.

## Development Status

- **Phase 18: Continuous Improvement and Optimization** - In Progress
  - WFE-007: User Satisfaction Monitoring System - Completed
  - WFE-008: Workflow Execution Analytics - Completed
  - WFE-009: Complex Workflow Testing Framework - Completed
  - WFE-010: Workflow Optimization Recommendations - Completed

## Getting Started

To get started with Atlas development, ensure your environment is set up according to `.windsurf/ENVIRONMENT_SETUP.md`. Use Python 3.9.6 (ARM64 native) within the `.venv` virtual environment.

Run the demo scripts to see the features in action:
- Workflow Analytics: `python3.9 workflow_analytics_demo.py`
- User Satisfaction Monitoring: (coming soon)
- Workflow Testing Framework: `python3.9 workflow_testing_demo.py`
- Workflow Optimization: `python3.9 workflow_optimization_demo.py`

## Continuous Development Protocol

Atlas development adheres to the ABSOLUTE NEVER-STOP MANDATE, ensuring continuous progress without pauses until all tasks are completed. For detailed development guidelines, refer to the workflow in `.windsurf/workflows/atlas.md`.

---

# Phase 10: Critical Architecture Refactoring

As part of Phase 10, the project structure has been updated:
- Merged `/ui` and `/ui_qt` into a single `/ui` directory.
- Removed unused directories like `/archive`, `/plans`, `/models`, `/context_data`, `/CascadeProjects`, and `/~`.
- Clarification of `/app` vs root directory responsibilities is ongoing.

---

## 🔧 Code Quality & Автоматична Перевірка

### Обов'язково для розробників та ШІ агентів:
```bash
# ЗАВЖДИ запускати після змін у коді:
./activate_auto_coding_2.1.sh
```

**Особливості системи автоматичної перевірки:**
- ⚡ **Швидкість**: <5 секунд (було зависання)
- 🛡️ **Захист**: Автоматичне виправлення синтаксичних помилок
- 📊 **Прогрес**: Чіткі індикатори стану
- 🎯 **Пріоритети**: Обробка найважливіших файлів першими

### Для ШІ агентів Windsurf:
- 📋 **Протокол**: `AI_CODE_QUALITY_PROTOCOL.md`
- 🔧 **Команди**: `WINDSURF_COMMANDS.md` → розділ "Code Quality"
- 📖 **Звіт**: `AUTO_CODING_PROBLEM_RESOLUTION.md`

### Швидкі команди:
```bash
# Виправлення критичних помилок
python3 scripts/quick_syntax_fix.py

# Поліпшення коду
python3 scripts/improved_atlas_code_fixer.py

# Перевірка статистики
ruff check --statistics .
```

---

> **Cyberpunk is not a crime!** # Atlas
