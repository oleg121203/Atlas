# 🚀 Atlas Development Strategy

## Подвійна Архітектура Розробки

Atlas розробляється з використанням інноваційного підходу **dual-environment development**:

### 🐧 Linux Development (Python 3.12)
**Призначення**: Основне середовище розробки
- **Платформа**: Linux (Ubuntu/Codespaces)  
- **Python**: 3.12
- **Режим**: Headless, CLI, Backend development
- **Фокус**: Ядро системи, логіка, тестування

### 🍎 macOS Production (Python 3.13)
**Призначення**: Цільова платформа для користувачів
- **Платформа**: macOS (нативна інтеграція)
- **Python**: 3.13  
- **Режим**: GUI, Native features
- **Фокус**: Користувацький досвід, нативні функції

---

## 🏗️ Швидкий Старт

### Для розробників (Linux)
```bash
# Клонування репозиторію
git clone <repository-url>
cd Atlas

# Налаштування середовища розробки
./setup_dev_linux.sh

# Розробка в headless режимі
source venv-dev/bin/activate
python main.py --headless --debug --config config-dev.ini
```

### Для користувачів (macOS)
```bash
# Запуск продакшн версії
./launch_macos.sh

# Або ручне налаштування
python3.13 -m venv venv-macos
source venv-macos/bin/activate
pip install -r requirements-macos.txt
python main.py --config config-macos.ini
```

---

## 📁 Структура Проекту

```
Atlas/
├── 🔧 Development (Linux Python 3.12)
│   ├── setup_dev_linux.sh         # Автоматичне налаштування
│   ├── config-dev.ini              # Конфігурація розробки
│   ├── requirements-linux.txt      # Залежності Linux
│   └── venv-dev/                   # Virtual environment розробки
│
├── 🍎 Production (macOS Python 3.13)
│   ├── launch_macos.sh             # Запуск для macOS
│   ├── config-macos.ini            # Конфігурація продакшн
│   ├── requirements-macos.txt      # Залежності macOS
│   └── venv-macos/                 # Virtual environment продакшн
│
├── 🛠️ Cross-Platform Code
│   ├── utils/platform_utils.py     # Детекція платформи
│   ├── utils/macos_utils.py        # macOS нативні функції
│   ├── tools/screenshot_tool.py    # Кросплатформенні інструменти
│   └── main.py                     # Головний файл
│
└── 📚 Documentation
    ├── docs/DEVELOPMENT_GUIDE.md   # Повний гід розробки
    ├── docs/DEVELOPMENT_COMMANDS.md # Команди для розробників
    ├── MACOS_SETUP.md              # Інструкції для macOS
    └── README_EN.md                # Англійська документація
```

---

## 🔄 Workflow Розробки

### 1. 💻 Фаза Розробки (Linux)
```bash
# Активація середовища
source venv-dev/bin/activate

# Розробка нових функцій
python main.py --headless --debug

# Тестування
python -m pytest tests/ -v

# Форматування коду
black . && flake8 .
```

### 2. 🧪 Фаза Тестування (macOS)
```bash
# Активація prod середовища
source venv-macos/bin/activate

# Тестування GUI
python main.py --config config-macos.ini

# Тестування нативних функцій
python main.py --test-native
```

### 3. 🚀 Фаза Релізу
```bash
# Збірка для macOS
python setup.py bdist_dmg

# Підписання та дистрибуція
codesign -s "Developer ID" Atlas.app
```

---

## 🎯 Платформні Особливості

### Linux Development Features
- ✅ Headless operation
- ✅ CI/CD integration  
- ✅ Docker support
- ✅ Automated testing
- ✅ Debug tools

### macOS Production Features
- ✅ Native GUI (CustomTkinter)
- ✅ Quartz screenshots
- ✅ Dock integration
- ✅ System permissions
- ✅ Dark/Light mode
- ✅ Application Support directory

---

## ⚙️ Конфігурація

### Development (Linux)
```ini
# config-dev.ini
[General]
debug_mode = true
headless_mode = true
log_level = DEBUG

[Platform]
target_platform = linux
gui_enabled = false
```

### Production (macOS)
```ini
# config-macos.ini
[General]
debug_mode = false
headless_mode = false
log_level = INFO

[macOS]
quartz_screenshots = true
dock_integration = true
appearance_mode = system
```

---

## 🛠️ Команди Розробки

| Дія | Linux Dev | macOS Prod |
|-----|-----------|------------|
| Налаштування | `./setup_dev_linux.sh` | `./launch_macos.sh` |
| Активація | `source venv-dev/bin/activate` | `source venv-macos/bin/activate` |
| Запуск | `python main.py --headless` | `python main.py` |
| Тести | `pytest tests/` | GUI testing |
| Конфіг | `--config config-dev.ini` | `--config config-macos.ini` |

---

## 📊 Платформна Інформація

Перевірити сумісність:
```bash
python main.py --platform-info
```

Очікуваний вивід:
```
Atlas Platform Information:
  system: Darwin / Linux
  python_version: 3.13.x / 3.12.x
  is_macos: True / False
  is_linux: False / True
  is_headless: False / True
  has_display: True / False
```

---

## 📖 Документація

- **[DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)** - Повний гід розробки
- **[DEVELOPMENT_COMMANDS.md](docs/DEVELOPMENT_COMMANDS.md)** - Команди та утиліти
- **[MACOS_SETUP.md](MACOS_SETUP.md)** - Налаштування macOS
- **[README_EN.md](README_EN.md)** - English documentation

---

## 🤝 Contributing

1. Розробляйте на **Linux Python 3.12**
2. Тестуйте на **macOS Python 3.13**
3. Використовуйте платформні утиліти
4. Забезпечте кросплатформенну сумісність
5. Документуйте зміни

---

**Atlas** - інноваційний підхід до розробки з оптимізацією під кожну платформу! 🌟
