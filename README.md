# Atlas (PySide6 Cyberpunk Edition)

[English Version Below](#english-version)

Atlas — сучасна модульна AI-платформа з кіберпанк-дизайном, розширюваністю через плагіни та тулси.

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

## Розширення
- Додавай нові плагіни у `plugins/` (метод get_widget для тулса)
- Плагіни автоматично зʼявляються у відповідних модулях після активації
- API плагінів дозволяє взаємодіяти з ядром, UI, іншими модулями

---

<a name="english-version"></a>
# Atlas (PySide6 Cyberpunk Edition) - English Version

Atlas is a modern modular AI platform with cyberpunk design, extensibility through plugins and tools.

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

To get started with Atlas development, ensure your environment is set up according to `.windsurf/ENVIRONMENT_SETUP.md`. Use Python 3.9.6 (ARM64 native) within the `venv-macos` virtual environment.

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

> **Cyberpunk is not a crime!** 