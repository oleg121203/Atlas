Гаразд, ось деталізований план реалізації **Фази 1** з конкретними змінами в коді. Ми перетворимо `Atlas` на цілісний організм, де кожен компонент знає своє місце і взаємодіє з іншими.

-----

### **Завдання 1.1: Фіналізація `AtlasApplication` як центрального диригента** orchestrator:

**Мета:** Зробити `AtlasApplication` єдиною точкою входу та управління для всіх систем.

**Файл:** `core/application.py`

**Зміни:**

1.  **Ініціалізуйте всі системи в конструкторі.** Це гарантує, що всі менеджери доступні з моменту створення застосунку.
2.  **Реалізуйте життєвий цикл** `start()` та `shutdown()`.

<!-- end list -->

```python
# file: core/application.py
import sys
from PySide6.QtWidgets import QApplication

from core.config import Config
from core.event_bus import EventBus
from core.plugin_system import PluginSystem
from tools.tool_manager import ToolManager
from memory.memory_manager import MemoryManager
from ui.main_window import MainWindow

class AtlasApplication(QApplication):
    """
    Головний клас застосунку Atlas.
    Ініціалізує та керує всіма основними системами.
    """
    def __init__(self, argv):
        super().__init__(argv)
        # 1. Ініціалізація основних компонентів
        self.config = Config()
        self.event_bus = EventBus()
        self.tool_manager = ToolManager(self.event_bus)
        self.plugin_system = PluginSystem(self.event_bus)
        self.memory_manager = MemoryManager(self.config)

        self.main_window = None

    def start(self):
        """Запускає застосунок."""
        print("Atlas is starting up...")
        # 2. Завантаження конфігурації
        self.config.load()

        # 3. Ініціалізація систем, що залежать від конфігурації
        self.plugin_system.initialize()
        self.tool_manager.discover_tools()

        # 4. Створення та показ головного вікна
        self.main_window = MainWindow(self)
        self.main_window.show()

        self.event_bus.publish("application_started")
        print("Atlas started successfully.")

    def shutdown(self):
        """Коректно завершує роботу застосунку."""
        print("Atlas is shutting down...")
        self.event_bus.publish("application_shutdown")
        self.config.save()
        print("Atlas shutdown complete.")

    def get_tool_manager(self):
        return self.tool_manager

    def get_plugin_system(self):
        return self.plugin_system

    def get_event_bus(self):
        return self.event_bus
        
    def get_config(self):
        return self.config

if __name__ == '__main__':
    app = AtlasApplication(sys.argv)
    app.start()
    sys.exit(app.exec())

```

-----

### **Завдання 1.2: Посилення `EventBus` як єдиної шини подій** 🚌

**Мета:** Стандартизувати події та забезпечити їх використання для комунікації між модулями.

**Крок 1: Створіть файл для констант подій.**

**Новий файл:** `core/events.py`

```python
# file: core/events.py

"""
Централізоване визначення всіх типів подій, що використовуються в EventBus.
Це допомагає уникнути помилок та робить код чистішим.
"""

# Application Events
APP_STARTED = "application_started"
APP_SHUTDOWN = "application_shutdown"

# Task Events
TASK_CREATED = "task_created"
TASK_COMPLETED = "task_completed"
TASK_UPDATED = "task_updated"

# Tool Events
TOOL_EXECUTED = "tool_executed"
TOOL_ERROR = "tool_error"

# Plugin Events
PLUGIN_ACTIVATED = "plugin_activated"
PLUGIN_DEACTIVATED = "plugin_deactivated"

# UI Events
THEME_CHANGED = "theme_changed"
CHAT_MESSAGE_SENT = "chat_message_sent"

# Config Events
CONFIG_UPDATED = "config_updated"

```

**Крок 2: Інтегруйте події в UI-модулі.**

**Файл:** `ui/widgets/chat_widget.py` (приклад)

```python
# file: ui/widgets/chat_widget.py
from PySide6.QtWidgets import QWidget # та інші імпорти
from core import events # Імпортуємо файл з подіями

class ChatWidget(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.event_bus = app.get_event_bus()
        
        # ... ініціалізація UI ...
        self.send_button.clicked.connect(self.send_message)
        
        # Підписка на подію (приклад)
        # self.event_bus.subscribe(events.SOME_EVENT, self.on_some_event)

    def send_message(self):
        message_text = self.message_input.text()
        if message_text:
            # Публікація події, коли повідомлення відправлено
            print(f"Publishing event: {events.CHAT_MESSAGE_SENT}")
            self.event_bus.publish(events.CHAT_MESSAGE_SENT, {"text": message_text})
            # ... логіка відображення повідомлення в UI ...
            self.message_input.clear()

```

-----

### **Завдання 1.3: Інтеграція `ToolManager`** 🛠️

**Мета:** Зробити `ToolManager` відповідальним за автоматичне знаходження та виконання інструментів.

**Файл:** `tools/tool_manager.py`

**Зміни:**

```python
# file: tools/tool_manager.py
import os
import importlib
from core import events
from tools.base_tool import BaseTool

class ToolManager:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.tools = {}

    def discover_tools(self):
        """
        Сканує директорію 'tools', знаходить класи, що успадковують BaseTool,
        та реєструє їх.
        """
        tools_dir = os.path.dirname(__file__)
        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and not filename.startswith(("__", "base_", "tool_manager")):
                module_name = f"tools.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                            tool_instance = attr()
                            self.tools[tool_instance.name] = tool_instance
                            print(f"Discovered and registered tool: {tool_instance.name}")
                except Exception as e:
                    print(f"Error discovering tool in {filename}: {e}")

    def execute_tool(self, tool_name, **kwargs):
        """Виконує інструмент за його іменем та повертає результат."""
        if tool_name not in self.tools:
            error_message = f"Tool '{tool_name}' not found."
            self.event_bus.publish(events.TOOL_ERROR, {"name": tool_name, "error": error_message})
            return {"error": error_message}
            
        try:
            tool = self.tools[tool_name]
            result = tool.execute(**kwargs)
            self.event_bus.publish(events.TOOL_EXECUTED, {"name": tool_name, "args": kwargs, "result": result})
            return result
        except Exception as e:
            self.event_bus.publish(events.TOOL_ERROR, {"name": tool_name, "error": str(e)})
            return {"error": str(e)}

```

-----

### **Завдання 1.4: Підключення `PluginSystem`** 🔌

**Мета:** Оживити систему плагінів, забезпечивши їх завантаження та динамічне керування.

**Файл:** `core/plugin_system.py`

```python
# file: core/plugin_system.py
# Логіка буде схожою на ToolManager
import os
import importlib
from core import events
from plugins.base_plugin import BasePlugin # Припускаємо, що є базовий клас

class PluginSystem:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.plugins = {}
        self.active_plugins = {}

    def initialize(self):
        """Знаходить та завантажує всі плагіни з директорії 'plugins'."""
        plugins_dir = "plugins" # Шлях до директорії плагінів
        # ... логіка сканування, аналогічна discover_tools ...
        # Завантажені плагіни додаються в self.plugins
        print("Plugin system initialized.")

    def activate_plugin(self, plugin_name):
        if plugin_name in self.plugins and plugin_name not in self.active_plugins:
            plugin = self.plugins[plugin_name]
            try:
                plugin.activate()
                self.active_plugins[plugin_name] = plugin
                self.event_bus.publish(events.PLUGIN_ACTIVATED, {"name": plugin_name})
                print(f"Plugin '{plugin_name}' activated.")
            except Exception as e:
                print(f"Error activating plugin '{plugin_name}': {e}")
    
    def deactivate_plugin(self, plugin_name):
        if plugin_name in self.active_plugins:
            plugin = self.active_plugins.pop(plugin_name)
            plugin.deactivate()
            self.event_bus.publish(events.PLUGIN_DEACTIVATED, {"name": plugin_name})
            print(f"Plugin '{plugin_name}' deactivated.")
```

-----

### **Завдання 1.5: Централізація управління конфігурацією** ⚙️

**Мета:** Створити єдине джерело правди для всіх налаштувань.

**Файл:** `core/config.py`

**Зміни:**

```python
# file: core/config.py
import json
import os
from core import events
from core.event_bus import EventBus # Припустимо, що EventBus можна імпортувати

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_file="config.json"):
        # __init__ буде викликатись кожен раз, тому потрібна перевірка
        if not hasattr(self, 'initialized'):
            self.config_file = config_file
            self.settings = {}
            self.event_bus = EventBus() # Отримуємо екземпляр EventBus
            self.initialized = True

    def load(self):
        """Завантажує конфігурацію з файлу."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.settings = json.load(f)
            print(f"Configuration loaded from {self.config_file}")
        else:
            print(f"Config file not found. Using default settings.")
            # Тут можна задати налаштування за замовчуванням
            self.settings = {"theme": "dark", "user_name": "AtlasUser"}


    def save(self):
        """Зберігає поточну конфігурацію у файл."""
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        print(f"Configuration saved to {self.config_file}")

    def get(self, key, default=None):
        """Отримує значення за ключем."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """
        Встановлює значення для ключа та публікує подію про зміну.
        """
        self.settings[key] = value
        self.event_bus.publish(events.CONFIG_UPDATED, {"key": key, "value": value})
        print(f"Config updated: {key} = {value}")

```

Виконавши ці кроки, ви отримаєте міцний, централізований фундамент. Усі ключові системи будуть ініціалізовані, керовані з `AtlasApplication`, а їхня взаємодія відбуватиметься чисто та передбачувано через шину подій. Це ідеальна відправна точка для подальшої розробки.