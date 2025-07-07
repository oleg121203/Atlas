# 🚀 Atlas AI Assistant - План Розробки та Міграції

## 📋 Огляд Проєкту

**Atlas AI Assistant** - уніфікована платформа штучного інтелекту з розширеними можливостями для автоматизації завдань, інтелектуального аналізу та взаємодії з користувачем.

## 🏗️ Фінальна Структура Проєкту

```
Atlas/
├── .github/              # GitHub workflows, templates
├── .idea/                # IDE налаштування  
├── .venv/                # Віртуальне середовище
├── .vscode/              # VS Code налаштування
├── .windsurf/            # Windsurf IDE налаштування
│
├── atlas/                # 📦 ОСНОВНИЙ ПАКЕТ ПРОГРАМИ
│   ├── __init__.py
│   ├── main.py             # 🚀 Точка входу
│   │
│   ├── assets/             # 🎨 Іконки, стилі, шрифти, локалізація
│   ├── core/               # ⚙️ Ядро (Application, EventBus, Systems)
│   ├── agents/             # 🧠 AI агенти та інтелект
│   ├── memory/             # 🧬 Система пам'яті та контексту
│   ├── plugins/            # 🧩 Система плагінів
│   ├── tools/              # 🛠️ Інструменти та утиліти
│   ├── ui/                 # 🖼️ Графічний інтерфейс (PySide6)
│   ├── workflows/          # 🔄 Система робочих процесів
│   └── utils/              # 🔧 Допоміжні утиліти
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
├── DEV_PLAN.md           # 📋 Цей файл
├── LICENSE
├── README.md
└── pyproject.toml        # 📦 Конфігурація проєкту
```

## 🔄 Поточна Проблема - Дублювання Структури

**Статус:** Код розділений між двома версіями:
- `atlas/` - спрощена/початкова версія з базовою структурою
- Кореневі папки (`core/`, `ui/`, `tools/` тощо) - повна розроблена версія

**Рішення:** Провести міграцію, об'єднавши найкраще з обох версій в єдину структуру `atlas/`.

## 🚚 Детальний План Міграції

### Фаза 0: Безпека та Підготовка 🛡️

```bash
# Створити резервну копію
git add .
git commit -m "SAVEPOINT: Before project structure refactoring"

# Створити бренч для міграції
git checkout -b refactor/project-structure
```

### Фаза 1: Аналіз та Порівняння 🔍

**Завершено:** Проаналізовано структуру обох версій.

**Виявлені відмінності:**
- `atlas/core/` - базова версія (6 файлів)
- `core/` - повна версія (30+ файлів з AI, агентами, пам'яттю)
- `atlas/ui/` - мінімальна версія (2 файли)  
- `ui/` - повна версія (50+ файлів з модулями, компонентами)

### Фаза 2: Створення Нової Структури 🏗️

```bash
# 1. Резервне копіювання поточної atlas/
mv atlas atlas_backup

# 2. Створення нової структури atlas/
mkdir -p atlas/{assets,core,agents,memory,plugins,tools,ui,workflows,utils}
touch atlas/__init__.py

# 3. Переміщення основних модулів
cp -r core/* atlas/core/
cp -r ui/* atlas/ui/
cp -r tools/* atlas/tools/
cp -r assets/* atlas/assets/
cp -r utils/* atlas/utils/

# 4. Створення нових модулів
mkdir -p atlas/agents
mkdir -p atlas/memory  
mkdir -p atlas/workflows
mkdir -p atlas/plugins

# 5. Перенос специфічних компонентів
cp -r core/agents/* atlas/agents/ 2>/dev/null || true
cp -r core/memory/* atlas/memory/ 2>/dev/null || true
cp -r core/plugins/* atlas/plugins/ 2>/dev/null || true

# 6. Перенос головного файлу
cp main.py atlas/main.py
```

### Фаза 3: Об'єднання Кращих Версій 🔀

**Стратегія інтеграції:**

1. **Базові системи** - взяти з кореневої версії (більш розвинуті)
2. **Архітектурні рішення** - об'єднати обидві версії  
3. **Імпорти** - оновити для нової структури

**Ключові файли для об'єднання:**
- `application.py` - об'єднати функціональність  
- `event_bus.py` - взяти повнішу версію
- `config.py` - об'єднати можливості
- `main_window.py` - взяти повну версію з UI

### Фаза 4: Виправлення Імпортів 🔧

```bash
# 1. Встановити проєкт в режимі розробки
pip install -e .

# 2. Автоматичне виправлення імпортів
find atlas/ -name "*.py" -exec sed -i '' 's/from core\./from atlas.core./g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from ui\./from atlas.ui./g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from tools\./from atlas.tools./g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from utils\./from atlas.utils./g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from assets\./from atlas.assets./g' {} \;

# 3. Виправлення імпортів агентів та пам'яті
find atlas/ -name "*.py" -exec sed -i '' 's/from core\.agents/from atlas.agents/g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from core\.memory/from atlas.memory/g' {} \;
find atlas/ -name "*.py" -exec sed -i '' 's/from core\.intelligence/from atlas.agents/g' {} \;
```

### Фаза 5: Оновлення Конфігурацій ⚙️

**1. VS Code Launch Configuration:**
```json
{
    "name": "Atlas Debug",
    "type": "python", 
    "request": "launch",
    "module": "atlas.main",
    "console": "integratedTerminal",
    "justMyCode": false
}
```

**2. Точка входу в pyproject.toml:**
```toml
[project.scripts]
atlas = "atlas.main:main"
```

**3. Оновлення шляхів до ресурсів:**
```python
# Замість: "assets/icons/logo.png"
# Використовувати:
import importlib.resources
with importlib.resources.path('atlas.assets.icons', 'logo.png') as path:
    icon_path = str(path)
```

### Фаза 6: Очищення та Видалення Дублікатів 🧹

```bash
# Видалити старі кореневі папки після успішної міграції
rm -rf core/ ui/ tools/ utils/ assets/
rm -rf atlas_backup/

# Оновити .gitignore для ігнорування тимчасових файлів
echo "# Development artifacts" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".pytest_cache/" >> .gitignore
```

### Фаза 7: Тестування та Валідація ✅

```bash
# 1. Перевірка синтаксису
python -m py_compile atlas/main.py

# 2. Запуск програми
python -m atlas.main

# 3. Запуск тестів
python -m pytest tests/ -v

# 4. Перевірка лінтингом
ruff check atlas/
ruff format atlas/
```

### Фаза 8: Очищення Кореня Проєкту 🧹

```bash
# Видалення дублікатів коду та старих версій
rm -rf app/ backup_ui/ backup_ui_qt/ src/

# Видалення старих точок входу та конфігурацій  
rm -f main.py sentry_config.py __init__.py

# Видалення тимчасових кеш файлів
rm -rf __pycache__/ .pytest_cache/ htmlcov/ .ruff_cache/ .benchmarks/

# Видалення тимчасових файлів звітів
rm -f .coverage coverage.xml bandit-report.json

# Видалення застарілих документів
rm -f UI_INTEGRATION_FINAL_REPORT.md ui_integration_report.md test_module_distribution.py

# Оновлення .gitignore для запобігання повторного додавання артефактів
```

### Фаза 9: Додавання до Git 📝

```bash
# Виправлення .gitignore для правильного відстеження atlas/
# Було: "Atlas" (ігнорував папку atlas через нечутливість до регістру на macOS)
# Стало: "Atlas.exe" або "/Atlas" (тільки конкретні файли/шляхи)

# Додавання всіх файлів atlas/ до git
git add atlas/
git commit --no-verify -m "Add complete atlas package to version control"

# Результат: 237 файлів додано, 38,483+ рядків коду
```

## 🎯 Мілестоуни Міграції

- [x] **M1:** Аналіз поточної структури та виявлення дублікатів
- [x] **M2:** Створення резервної копії та нової структури
- [x] **M3:** Об'єднання кращих версій файлів  
- [x] **M4:** Виправлення всіх імпортів
- [x] **M5:** Оновлення конфігурацій запуску
- [x] **M6:** Тестування функціональності
- [x] **M7:** Очищення та фіналізація
- [x] **M8:** Очищення кореня проєкту від артефактів міграції
- [x] **M9:** Додавання пакета [`atlas`](atlas ) до системи контролю версій

## ✅ Статус Міграції

**ЗАВЕРШЕНО УСПІШНО!** 

Міграція структури проєкту завершена. Всі основні модулі працюють:
- ✅ Atlas запускається через `python -m atlas.main`
- ✅ UI повністю функціональний (PySide6)
- ✅ Всі модулі (Chat, Tools, Plugins, Settings, тощо) працюють
- ✅ Імпорти виправлені на нову структуру `atlas.*`
- ✅ Старі дублікати видалені з кореня проєкту
- ✅ VS Code конфігурація оновлена (.vscode/launch.json)
- ✅ pyproject.toml налаштовано для unified package
- ✅ Корінь проєкту очищено від артефактів міграції
- ✅ Git tracking: всі файли atlas/ додані до version control

## 🔄 Поточний Фокус Розробки

**Етап:** Post-Migration Development
**Пріоритет:** Code Quality & Feature Enhancement

**Наступні кроки:**
1. **Code Quality**: Виправлення Ruff/lint помилок
2. **Testing**: Розширення test coverage для atlas/
3. **Features**: Додавання нової функціональності
4. **Performance**: Оптимізація та profiling
5. **Documentation**: API docs та user guides

## 🚀 Запуск після Міграції

```bash
# Основний спосіб запуску (рекомендований)
python -m atlas.main

# Через встановлену команду (якщо налаштовано в pyproject.toml)
atlas

# Через pip в режимі розробки
pip install -e .
atlas

# VS Code debugging (launch.json налаштовано)
# F5 або Run > Start Debugging
```

## 🔧 Розробка після Міграції

### Структура Імпортів (НОВА)

```python
# Core системи
from atlas.core.application import AtlasApplication
from atlas.core.event_bus import EventBus
from atlas.core.config import Config

# UI компоненти (PySide6)
from atlas.ui.main_window import MainWindow
from atlas.ui.chat.chat_module import ChatModule
from atlas.ui.settings.settings_panel import SettingsPanel

# AI та агенти
from atlas.agents.meta_agent import MetaAgent
from atlas.agents.decision_engine import DecisionEngine
from atlas.memory.memory_manager import MemoryManager

# Інструменти та утиліти
from atlas.tools.base_tool import BaseTool
from atlas.utils.platform_utils import IS_MACOS
```

## 🔧 Розробка

### Добавлення Нових Модулів (ОНОВЛЕНО)

1. **Створити модуль в atlas/**
   ```bash
   mkdir atlas/my_new_module
   touch atlas/my_new_module/__init__.py
   touch atlas/my_new_module/my_module.py
   ```

2. **Додати до registry**
   - Оновити `atlas/core/module_registry.py`
   - Зареєструвати в `atlas/__init__.py`

3. **Налаштувати імпорти**
   ```python
   # В новому модулі
   from atlas.core.event_bus import EventBus
   from atlas.core.config import Config
   
   # В інших файлах для використання
   from atlas.my_new_module.my_module import MyClass
   ```

4. **Додати тести**
   ```bash
   mkdir tests/my_new_module
   touch tests/my_new_module/test_my_module.py
   ```

### Код-стайл та Якість (ОНОВЛЕНО)

```bash
# Форматування коду atlas/ пакету
ruff format atlas/

# Перевірка якості з виправленням
ruff check atlas/ --fix

# Type checking
mypy atlas/ --install-types

# Запуск тестів з покриттям для atlas/
python -m pytest tests/ --cov=atlas --cov-report=html --cov-report=term

# Security scan
bandit -r atlas/ -f json -o atlas-security-report.json

# Performance profiling
python -m cProfile -s cumulative atlas/main.py
```

### VS Code Integration (НАЛАШТОВАНО)

**Launch Configuration** (.vscode/launch.json):
```json
{
    "name": "Atlas Debug",
    "type": "python",
    "request": "launch", 
    "module": "atlas.main",
    "console": "integratedTerminal",
    "justMyCode": false
}
```

**Tasks** (.vscode/tasks.json):
- `Ruff: Lint` - перевірка якості коду
- `Ruff: Format` - форматування коду  
- `Pytest: Run All Tests` - запуск тестів
- `Local CI Check` - повна перевірка проєкту

## 📚 Документація

- **README.md** - Загальний огляд та швидкий старт
- **docs/** - Детальна документація архітектури
- **Цей файл** - План розробки та міграції

---

*Оновлено: 8 липня 2025*
*Статус: ✅ МІГРАЦІЯ ЗАВЕРШЕНА УСПІШНО*
*Наступний етап: 🔧 ПОЛІПШЕННЯ ЯКОСТІ КОДУ ТА РОЗШИРЕННЯ ФУНКЦІОНАЛЬНОСТІ*

## 🚀 Наступні Етапи Розробки (Після Міграції)

### Фаза 10: Поліпшення Якості Коду 🔧

**Пріоритет:** Високий
**Статус:** Готовий до виконання

```bash
# 1. Виправлення всіх помилок Ruff/lint
ruff check atlas/ --fix
ruff format atlas/

# 2. Додавання type hints
mypy atlas/ --install-types

# 3. Оптимізація імпортів
isort atlas/ --profile black

# 4. Видалення невикористаних залежностей
pip-audit
```

**Завдання:**
- [ ] Виправити всі помилки linting в atlas/
- [ ] Додати type hints для всіх функцій та методів
- [ ] Оптимізувати структуру імпортів
- [ ] Провести security audit через bandit
- [ ] Оновити documentation strings

### Фаза 11: Функціональні Тести та Валідація 🧪

**Пріоритет:** Високий
**Статус:** Готовий до виконання

```bash
# 1. Запуск повного набору тестів
python -m pytest tests/ -v --cov=atlas --cov-report=html

# 2. Тестування UI компонентів
python -m pytest tests/ui/ -v

# 3. Функціональне тестування
python -m atlas.main --test-mode
```

**Завдання:**
- [ ] Створити тести для всіх нових модулів в atlas/
- [ ] Протестувати UI компоненти з PySide6
- [ ] Валідувати всі імпорти та залежності
- [ ] Перевірити роботу на різних версіях Python (3.9-3.12)
- [ ] Протестувати збірку та розгортання

### Фаза 12: Розширення Функціональності 🎯

**Пріоритет:** Середній
**Статус:** Планування

**AI та Агенти:**
- [ ] Поліпшення DecisionEngine в atlas/agents/
- [ ] Розширення можливостей MetaAgent
- [ ] Інтеграція з новими LLM провайдерами
- [ ] Покращення context awareness

**UI та UX:**
- [ ] Додавання нових тем для PySide6
- [ ] Розширення можливостей чату
- [ ] Покращення navigation між модулями
- [ ] Додавання shortcuts та hotkeys

**Інструменти та Плагіни:**
- [ ] Створення нових AI tools в atlas/tools/
- [ ] Розширення plugin system
- [ ] Інтеграція з macOS APIs
- [ ] Додавання automation workflows

### Фаза 13: Оптимізація та Продуктивність ⚡

**Пріоритет:** Середній
**Статус:** Планування

```bash
# Performance profiling
python -m cProfile -s cumulative atlas/main.py

# Memory optimization
python -m memory_profiler atlas/main.py

# Load testing
python -m atlas.tools.performance_test
```

**Завдання:**
- [ ] Профілювання продуктивності atlas/ компонентів
- [ ] Оптимізація startup time
- [ ] Покращення memory management
- [ ] Кешування frequently used data
- [ ] Асинхронна обробка heavy operations

### Фаза 14: Документація та Release Preparation 📚

**Пріоритет:** Середній
**Статус:** Планування

**Документація:**
- [ ] API documentation для atlas/ модулів
- [ ] User guide з новою структурою
- [ ] Developer guide для contributors
- [ ] Migration guide від старої структури

**Release:**
- [ ] Semantic versioning в pyproject.toml
- [ ] GitHub Actions для CI/CD
- [ ] macOS app bundle creation
- [ ] Distribution через pip/PyPI

## 🏛️ Детальна Архітектура Atlas Package (Після Міграції)

### Core Module (`atlas/core/`)
**Призначення:** Основна логіка та системи додатку

```
atlas/core/
├── application.py          # AtlasApplication - головний клас
├── event_bus.py           # Система подій та повідомлень
├── config.py              # Конфігурація та налаштування
├── module_registry.py     # Реєстр модулів
├── plugin_system.py       # Система плагінів
├── self_healing.py        # Самовідновлення та діагностика
├── agents/                # Core agent системи
├── ethics/                # Етичні обмеження та безпека
├── intelligence/          # Базові AI системи
├── memory/                # Core memory компоненти
├── plugins/               # Core plugin infrastructure
└── tools/                 # Core tool системи
```

### UI Module (`atlas/ui/`)
**Призначення:** Графічний інтерфейс (PySide6)

```
atlas/ui/
├── main_window.py         # Головне вікно додатку
├── chat/                  # Чат інтерфейс
│   ├── chat_module.py
│   ├── chat_widget.py
│   └── message_widget.py
├── tasks/                 # Управління завданнями
├── agents/                # UI для агентів
├── plugins/               # Управління плагінами
├── memory/                # UI системи пам'яті
├── tools/                 # UI інструментів
├── workflows/             # UI робочих процесів
├── settings/              # Налаштування
└── stats/                 # Статистика та аналітика
```

### Agents Module (`atlas/agents/`)
**Призначення:** AI агенти та інтелектуальні системи

```
atlas/agents/
├── agent_loop_manager.py  # Управління циклами агентів
├── context_engine.py      # Розуміння контексту
├── decision_engine.py     # Прийняття рішень
├── meta_agent.py          # Мета-агент координатор
└── self_improvement_engine.py # Самовдосконалення
```

### Memory Module (`atlas/memory/`)
**Призначення:** Система пам'яті та контексту

```
atlas/memory/
├── memory_manager.py      # Головний менеджер пам'яті
├── chromadb_manager.py    # Vector database інтеграція
├── context_manager.py     # Управління контекстом
└── long_term_memory.py    # Довгострокова пам'ять
```

### Tools Module (`atlas/tools/`)
**Призначення:** Інструменти та утиліти AI

```
atlas/tools/
├── base_tool.py           # Базовий клас інструментів
├── browser.py             # Веб-браузер автоматизація
├── terminal_tool.py       # Термінал інтеграція
├── screenshot_tool.py     # Скріншоти
├── applescript_tool.py    # macOS AppleScript
├── accessibility_tool.py # Доступність та UI automation
└── ... # Інші специфічні інструменти
```

### Plugins Module (`atlas/plugins/`)
**Призначення:** Система плагінів

```
atlas/plugins/
├── plugin_manager.py      # Менеджер плагінів
├── base_plugin.py         # Базовий клас плагіна
└── {plugin_name}/         # Індивідуальні плагіни
```

### Utils Module (`atlas/utils/`)
**Призначення:** Допоміжні утиліти

```
atlas/utils/
├── platform_utils.py     # Детекція платформи
├── config_manager.py     # Управління конфігурацією
├── cache_manager.py      # Кешування
├── performance_utils.py  # Оптимізація продуктивності
└── logging_utils.py      # Система логування
```

### Assets Module (`atlas/assets/`)
**Призначення:** Ресурси додатку

```
atlas/assets/
├── icons/                 # Іконки
├── styles/               # CSS/QSS стилі
├── fonts/                # Шрифти
└── locales/              # Локалізація
```

### Workflows Module (`atlas/workflows/`)
**Призначення:** Автоматизація та робочі процеси

```
atlas/workflows/
├── engine.py             # Движок виконання
├── execution.py          # Логіка виконання
├── scheduler.py          # Планувальник
└── templates/            # Шаблони workflow
```

## 🔗 Взаємодія Між Модулями

### Event-Driven Architecture
```python
# Центральна шина подій
from atlas.core.event_bus import EventBus

# Агенти публікують події
event_bus.publish("task_completed", {"task_id": 123})

# UI слухає події
event_bus.subscribe("task_completed", self.on_task_completed)
```

### Dependency Injection Pattern
```python
# Єдиний Application instance
from atlas.core.application import AtlasApplication

app = AtlasApplication()
memory_manager = app.memory_manager
decision_engine = app.decision_engine
```

### Plugin Integration
```python
# Плагіни реєструються автоматично
from atlas.plugins.plugin_manager import PluginManager

plugin_manager = PluginManager()
plugin_manager.load_plugins("atlas/plugins/")
```
