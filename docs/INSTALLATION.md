# Atlas Installation Guide

## Python Version Compatibility

Atlas підтримує Python 3.12 та 3.13. Ось рекомендації для різних платформ:

### macOS (включаючи Mac Studio)

**Рекомендовано: Python 3.13**
- Використовуйте Python 3.13, якщо він вже встановлений на вашому Mac Studio
- Для установки залежностей використовуйте `requirements-macos.txt` або `requirements-universal.txt`

```bash
# Перевірка версії Python
python3 --version

# Створення віртуального середовища
python3 -m venv .venv

# Активація віртуального середовища
source .venv/bin/activate

# Установка залежностей для macOS
pip install -r requirements-macos.txt

# Або універсальна версія (працює на всіх платформах)
pip install -r requirements-universal.txt
```

### Linux

**Рекомендовано: Python 3.12**
- Використовуйте `requirements-linux.txt` (без macOS-специфічних пакетів)

```bash
# Установка Python та venv (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Створення віртуального середовища
python3 -m venv .venv

# Активація віртуального середовища
source .venv/bin/activate

# Установка залежностей для Linux
pip install -r requirements-linux.txt
```

### Windows

**Рекомендовано: Python 3.12 або 3.13**
- Використовуйте `requirements-universal.txt`

```powershell
# Створення віртуального середовища
python -m venv .venv

# Активація віртуального середовища
.venv\Scripts\activate

# Установка залежностей
pip install -r requirements-universal.txt
```

## Файли Requirements

- **`requirements.txt`** - Оригінальний файл з точними версіями (Python 3.12/3.13)
- **`requirements-macos.txt`** - Оптимізовано для macOS з pyobjc пакетами
- **`requirements-linux.txt`** - Для Linux без macOS-специфічних пакетів  
- **`requirements-universal.txt`** - Універсальний з умовними залежностями

## Виправлені Проблеми

✅ **EnhancedMemoryManager Issue**: Виправлено проблему з відсутніми аргументами в конструкторі  
✅ **Cross-platform Compatibility**: Додано підтримку різних операційних систем  
✅ **Python 3.13 Support**: Повна сумісність з Python 3.13  

## Рекомендації

### Для Mac Studio з Python 3.13:
```bash
# Використовуйте наявний Python 3.13
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-macos.txt
```

### Альтернативно - встановлення Python 3.12 на Mac:
```bash
# З Homebrew
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-macos.txt
```

Обидва варіанти повністю підтримуються!
