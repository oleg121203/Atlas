# Atlas (PySide6 Cyberpunk Edition)

Atlas — сучасна модульна AI-платформа з кіберпанк-дизайном, розширюваністю через плагіни та тулси.

## Основні особливості
- PySide6 + qdarkstyle (темний кіберпанк-інтерфейс)
- Модульна архітектура: Chat, Tasks, Agents, Plugins, Settings, Stats
- Плагінна система: тулси для Chat, Tasks, Agents, ...
- Drag&Drop, автозбереження, markdown, emoji, автокомпліт
- Легко розширюється через нові плагіни (plugins/)

## Структура
- `main.py` — точка входу (PySide6 UI)
- `ui_qt/` — всі QWidget-модулі (chat, tasks, agents, plugins, settings, stats, plugin_manager)
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

> **Cyberpunk is not a crime!** 