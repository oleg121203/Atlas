# Atlas Plugin System

Система плагінів Atlas дозволяє створювати та використовувати плагіни, які інтегруються з активним провайдером у чаті. Це модульна система, яка дозволяє розширювати функціональність Atlas без зміни основного коду.

## Архітектура

### Основні компоненти

1. **BasePlugin** - базовий клас для всіх плагінів
2. **PluginManager** - менеджер для завантаження та виконання плагінів
3. **PluginMetadata** - метадані плагіна
4. **PluginResult** - результат виконання плагіна

### Структура плагіна

```python
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginResult

class MyPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            category="custom"
        )
    
    def initialize(self, provider) -> bool:
        # Ініціалізація з активним провайдером
        self.active_provider = provider
        return True
    
    def execute(self, command: str, **kwargs) -> PluginResult:
        # Виконання команд плагіна
        if command == "my_command":
            return PluginResult(
                success=True,
                data={"result": "success"}
            )
```

## Вбудовані плагіни

### Gmail Plugin

Плагін для роботи з Gmail API.

**Команди:**
- `search_emails` - пошук email
- `search_security_emails` - пошук безпеки email
- `get_email_content` - отримання вмісту email
- `list_labels` - список міток
- `authenticate` - перевірка автентифікації

**Приклад використання:**
```python
from plugins import execute_plugin_command

# Пошук email
result = execute_plugin_command("gmail", "search_emails", 
                               query="is:important", max_results=10)

# Пошук безпеки email
result = execute_plugin_command("gmail", "search_security_emails", 
                               days_back=7)
```

### Browser Plugin

Плагін для автоматизації браузера (Safari на macOS).

**Команди:**
- `open_browser` - відкриття браузера
- `navigate_to_url` - навігація до URL
- `open_gmail` - відкриття Gmail
- `search_gmail` - пошук в Gmail
- `get_page_title` - отримання заголовка сторінки
- `close_browser` - закриття браузера
- `click_element` - клік по елементу
- `fill_form` - заповнення форми

**Приклад використання:**
```python
# Відкриття Gmail
result = execute_plugin_command("browser", "open_gmail")

# Пошук в Gmail
result = execute_plugin_command("browser", "search_gmail", 
                               query="security")
```

## Інтеграція з інструментами

Система плагінів інтегрована з інструментами Atlas через `tools/plugin_tool.py`.

### Доступні інструменти

1. **initialize_plugin_system** - ініціалізація системи плагінів
2. **execute_plugin** - виконання команди плагіна
3. **list_plugins** - список доступних плагінів
4. **get_plugin_help** - довідка по плагіну
5. **gmail_search_emails** - пошук email через Gmail плагін
6. **gmail_search_security_emails** - пошук безпеки email
7. **browser_open_gmail** - відкриття Gmail в браузері
8. **browser_search_gmail** - пошук в Gmail через браузер
9. **browser_navigate_to_url** - навігація до URL
10. **browser_get_page_title** - отримання заголовка сторінки
11. **browser_close_browser** - закриття браузера

## Створення власного плагіна

### Крок 1: Створення класу плагіна

```python
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginResult

class MyCustomPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_custom_plugin",
            version="1.0.0",
            description="My custom plugin description",
            author="Your Name",
            category="custom",
            tags=["custom", "example"],
            dependencies=[],
            config_schema={
                "my_setting": {"type": "string", "default": "default_value"}
            }
        )
    
    def initialize(self, provider) -> bool:
        self.active_provider = provider
        self.logger.info(f"Plugin initialized with provider: {provider}")
        return True
    
    def execute(self, command: str, **kwargs) -> PluginResult:
        if command == "hello":
            return PluginResult(
                success=True,
                data={"message": "Hello from my plugin!"}
            )
        elif command == "process_data":
            data = kwargs.get("data", "")
            processed = data.upper()
            return PluginResult(
                success=True,
                data={"processed": processed}
            )
        else:
            return PluginResult(
                success=False,
                error=f"Unknown command: {command}"
            )
    
    def get_commands(self):
        return ["hello", "process_data"]
```

### Крок 2: Реєстрація плагіна

```python
from plugins.base_plugin import register_plugin

# Створення та реєстрація плагіна
plugin = MyCustomPlugin()
register_plugin(plugin)
```

### Крок 3: Використання плагіна

```python
from plugins import execute_plugin_command

# Виконання команди
result = execute_plugin_command("my_custom_plugin", "hello")
print(result.data["message"])

# Обробка даних
result = execute_plugin_command("my_custom_plugin", "process_data", 
                               data="hello world")
print(result.data["processed"])
```

## Налаштування

### Конфігурація плагіна

Плагіни можуть мати власну конфігурацію:

```python
config = {
    "gmail": {
        "credentials_path": "path/to/credentials.json",
        "max_results": 50
    },
    "browser": {
        "default_browser": "Safari",
        "timeout": 30
    }
}

# Створення плагіна з конфігурацією
gmail_plugin = GmailPlugin(config["gmail"])
browser_plugin = BrowserPlugin(config["browser"])
```

### Ініціалізація з провайдером

```python
from plugins import set_active_provider, register_builtin_plugins

# Встановлення активного провайдера
set_active_provider(your_provider)

# Реєстрація вбудованих плагінів
register_builtin_plugins()
```

## Тестування

Для тестування системи плагінів використовуйте `test_plugin_system.py`:

```bash
python test_plugin_system.py
```

Цей скрипт демонструє:
- Ініціалізацію системи плагінів
- Реєстрацію вбудованих плагінів
- Виконання команд плагінів
- Створення власного плагіна

## Переваги системи плагінів

1. **Модульність** - кожен плагін є незалежним модулем
2. **Розширюваність** - легко додавати нові плагіни
3. **Інтеграція з провайдером** - плагіни мають доступ до активного провайдера
4. **Стандартизація** - єдиний інтерфейс для всіх плагінів
5. **Безпека** - ізольоване виконання команд
6. **Гнучкість** - можливість налаштування та конфігурації

## Майбутні розширення

- Підтримка асинхронних плагінів
- Система залежностей між плагінами
- Автоматичне оновлення плагінів
- Графічний інтерфейс для управління плагінами
- Підтримка плагінів з веб-інтерфейсом 