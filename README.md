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

## Phase 10: Critical Architecture Refactoring

As part of Phase 10, the project structure has been updated:
- Merged `/ui` and `/ui_qt` into a single `/ui` directory.
- Removed unused directories like `/archive`, `/plans`, `/models`, `/context_data`, `/CascadeProjects`, and `/~`.
- Clarification of `/app` vs root directory responsibilities is ongoing.

---

> **Cyberpunk is not a crime!** 