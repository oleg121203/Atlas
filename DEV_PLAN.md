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

## 🎯 Мілестоуни Міграції

- [x] **M1:** Аналіз поточної структури та виявлення дублікатів
- [x] **M2:** Створення резервної копії та нової структури
- [x] **M3:** Об'єднання кращих версій файлів  
- [x] **M4:** Виправлення всіх імпортів
- [x] **M5:** Оновлення конфігурацій запуску
- [x] **M6:** Тестування функціональності
- [x] **M7:** Очищення та фіналізація

## ✅ Статус Міграції

**ЗАВЕРШЕНО УСПІШНО!** 

Міграція структури проєкту завершена. Всі основні модулі працюють:
- ✅ Atlas запускається через `python -m atlas.main`
- ✅ UI повністю функціональний
- ✅ Всі модулі (Chat, Tools, Plugins, Settings, тощо) працюють
- ✅ Імпорти виправлені
- ✅ Старі дублікати видалені
- ✅ VS Code конфігурація оновлена

## 🚀 Запуск після Міграції

```bash
# Режим розробки (рекомендований)
python -m atlas.main

# Через встановлену команду (якщо налаштовано)
atlas

# Через pip в режимі розробки
pip install -e .
```

## 🔧 Розробка

### Добавлення Нових Модулів

1. Створити папку в `atlas/`
2. Добавити `__init__.py`
3. Реєструвати в `atlas/core/module_registry.py`
4. Оновити імпорти в `atlas/__init__.py`

### Код-стайл та Якість

```bash
# Форматування коду
ruff format atlas/

# Перевірка якості
ruff check atlas/

# Запуск тестів з покриттям
python -m pytest tests/ --cov=atlas --cov-report=html
```

## 📚 Документація

- **README.md** - Загальний огляд та швидкий старт
- **docs/** - Детальна документація архітектури
- **Цей файл** - План розробки та міграції

---

*Оновлено: 8 липня 2025*
*Статус: ✅ МІГРАЦІЯ ЗАВЕРШЕНА УСПІШНО*
