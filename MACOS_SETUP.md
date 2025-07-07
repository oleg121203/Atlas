# Налаштування macOS для розробки Atlas

Цей документ містить інструкції щодо налаштування середовища розробки Atlas на macOS.

## Системні вимоги

- macOS 11.0 (Big Sur) або новіше
- 8 ГБ оперативної пам'яті (рекомендовано 16 ГБ)
- 5 ГБ вільного місця на диску
- Python 3.9 або новіше

## Швидке налаштування

Найпростіший спосіб налаштувати середовище розробки - використати наш автоматичний скрипт:

```bash
# Клонувати репозиторій (якщо ще не зроблено)
git clone https://github.com/your-org/atlas.git
cd atlas

# Зробити скрипт виконуваним та запустити його
chmod +x setup_macos_dev.sh
./setup_macos_dev.sh
```

Скрипт:
1. Встановить Homebrew (якщо не встановлено)
2. Встановить Python 3.9
3. Створить віртуальне середовище
4. Встановить всі залежності
5. Налаштує VS Code (якщо встановлено)
6. Створить файл .env з базовими налаштуваннями

## Ручне налаштування

Якщо ви бажаєте налаштувати середовище вручну, виконайте наступні кроки:

### 1. Встановіть Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Додайте Homebrew до PATH (для Apple Silicon Mac):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Або для Intel Mac:
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

### 2. Встановіть Python 3.9

```bash
brew install python@3.9
brew link --force python@3.9
```

### 3. Створіть віртуальне середовище

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Встановіть залежності

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Налаштуйте змінні середовища

Створіть файл `.env` в кореневій директорії проекту:
```
ATLAS_ENV=development
ATLAS_PLATFORM=macos
ATLAS_LOG_LEVEL=DEBUG
```

## Запуск додатка

Для запуску Atlas використовуйте скрипт `launch_macos.sh`:

```bash
./launch_macos.sh
```

Або запустіть напряму через Python:

```bash
source .venv/bin/activate
python app/main.py
```

## Розробка з VS Code

Для розробки в VS Code встановіть рекомендовані розширення:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Debugpy (ms-python.debugpy)

Відкрийте проект в VS Code, виберіть інтерпретатор Python з віртуального середовища та використовуйте наші попередньо налаштовані конфігурації запуску та завдання.

## Типові проблеми та їх вирішення

### Проблеми з віртуальним середовищем

Якщо виникають проблеми з віртуальним середовищем, спробуйте створити його заново:

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Проблеми з GUI компонентами

Якщо виникають проблеми з GUI:

```bash
# Встановіть додаткові системні залежності
brew install cairo pango gdk-pixbuf libffi
```

### Додаткова інформація

Для отримання додаткової інформації про розробку, див. документацію в директорії `docs/` або звертайтеся до технічної підтримки.

## Внесення змін

Перед відправкою змін:
1. Запустіть тести: `pytest tests/`
2. Перевірте стиль коду: `ruff check .`
3. Оновіть документацію, якщо необхідно
