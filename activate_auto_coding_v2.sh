#!/bin/bash

# === АТЛАС АВТО-КОДИНГ СИСТЕМА V2 ===
# Активація повної автоматизації Ruff + AI для локальної розробки з покращеними можливостями
# Версія 2.0 - оптимізована для великих проектів

echo "🚀 Активація Atlas Auto-Coding System v2.0..."

show_help() {
    echo "Використання: $0 [ОПЦІЇ]"
    echo "  -h, --help            Показати цю довідку"
    echo "  -q, --quick           Швидкий режим, лише imports та patterns"
    echo "  -f, --full            Повний режим з усіма виправленнями (за замовчуванням)"
    echo "  -s, --specific FILE   Виправити конкретний файл"
    echo "  -d, --debug           Режим відлагодження з детальним логуванням"
    echo "  -o, --ollama          Запустити Ollama для AI асистента"
    echo "  -p, --precommit       Налаштувати pre-commit хуки"
    echo "  -w, --watch           Запустити автоматичний watcher для Ruff"
    echo
}

# Аналіз аргументів командного рядка
MODE="full"
DEBUG=""
SPECIFIC_FILE=""
RUN_OLLAMA=false
SETUP_PRECOMMIT=true
RUN_WATCHER=false

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -q|--quick)
            MODE="quick"
            shift
            ;;
        -f|--full)
            MODE="full"
            shift
            ;;
        -s|--specific)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG="1"
            shift
            ;;
        -o|--ollama)
            RUN_OLLAMA=true
            shift
            ;;
        -p|--precommit)
            SETUP_PRECOMMIT=true
            shift
            ;;
        -w|--watch)
            RUN_WATCHER=true
            shift
            ;;
        *)
            echo "Невідомий параметр: $1"
            show_help
            exit 1
            ;;
    esac
done

# Перевірка існування файлів скриптів
if [[ ! -f "scripts/quick_imports_fixer.py" || ! -f "scripts/quick_pattern_fixer.py" || ! -f "scripts/atlas_code_fixer.py" ]]; then
    echo "❌ Відсутні необхідні скрипти в директорії scripts/"
    exit 1
fi

# Робимо скрипти виконуваними
chmod +x scripts/quick_imports_fixer.py scripts/quick_pattern_fixer.py scripts/atlas_code_fixer.py scripts/fix_all.py

# Запуск Ollama за вибором
if $RUN_OLLAMA; then
    # Перевірка Ollama
    if ! command -v ollama &> /dev/null; then
        echo "❌ Ollama не встановлено. Встановіть спочатку ollama."
        exit 1
    fi

    # Запуск Ollama
    echo "🔄 Запуск Ollama..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!

    # Перевірка моделей
    echo "🧠 Перевірка AI моделей..."
    if ! ollama list | grep -q "qwen2.5-coder:latest"; then
        echo "⬇️  Завантаження qwen2.5-coder:latest..."
        ollama pull qwen2.5-coder:latest
    fi
fi

# Перевірка і встановлення pre-commit хуків
if $SETUP_PRECOMMIT; then
    echo "🔧 Налаштування pre-commit хуків..."
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo "✅ Pre-commit хуки активовано"
    else
        echo "⚠️  pre-commit не встановлено. Встановлюємо..."
        pip install pre-commit
        pre-commit install
        echo "✅ Pre-commit хуки активовано"
    fi
fi

# Запуск автоматичного watcher для Ruff
if $RUN_WATCHER; then
    echo "👁️  Запуск Ruff auto-watcher..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py -- ruff check --fix --unsafe-fixes . &
        WATCHER_PID=$!
        echo "✅ Ruff watcher активовано (PID: $WATCHER_PID)"
    else
        echo "⚠️  watchexec не встановлено. Встановіть: brew install watchexec"
    fi
fi

# Запуск виправлення коду в залежності від режиму
echo "🛠️  Запуск виправлення коду..."

if [[ -n "$SPECIFIC_FILE" ]]; then
    echo "Виправлення конкретного файлу: $SPECIFIC_FILE"
    
    # Перевірка існування файлу
    if [[ ! -f "$SPECIFIC_FILE" ]]; then
        echo "❌ Файл не знайдено: $SPECIFIC_FILE"
        exit 1
    fi
    
    # Запуск з увімкненим режимом відлагодження, якщо задано
    if [[ -n "$DEBUG" ]]; then
        DEBUG=1 python scripts/atlas_code_fixer.py "$SPECIFIC_FILE"
    else
        python scripts/atlas_code_fixer.py "$SPECIFIC_FILE"
    fi
    
elif [[ "$MODE" = "quick" ]]; then
    echo "Використання швидкого режиму (imports + patterns)"
    
    # Запуск з увімкненим режимом відлагодження, якщо задано
    if [[ -n "$DEBUG" ]]; then
        DEBUG=1 python scripts/quick_imports_fixer.py
        DEBUG=1 python scripts/quick_pattern_fixer.py
    else
        python scripts/quick_imports_fixer.py
        python scripts/quick_pattern_fixer.py
    fi
    
    # Форматування коду
    ruff format .
    
else
    echo "Використання повного режиму виправлення коду"
    
    # Запуск з увімкненим режимом відлагодження, якщо задано
    if [[ -n "$DEBUG" ]]; then
        DEBUG=1 python scripts/fix_all.py
    else
        python scripts/fix_all.py
    fi
fi

# Запуск VS Code, якщо можливо
if command -v code &> /dev/null; then
    echo "💻 Запуск VS Code з налаштуваннями..."
    code .
fi

echo ""
echo "🎉 Atlas Auto-Coding System v2 завершив роботу!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Активні процеси:"
if [[ -n "$OLLAMA_PID" ]]; then
    echo "   • Ollama Server (PID: $OLLAMA_PID)"
fi
if [[ -n "$WATCHER_PID" ]]; then
    echo "   • Ruff Auto-Watcher (PID: $WATCHER_PID)"
fi
echo "   • VS Code з Continue AI"
echo ""
echo "📊 Статистика залишкових помилок:"
ruff check --statistics
echo ""
echo "💡 Для більш детальної інформації:"
echo "   • Запустіть 'ruff check .' для повного списку помилок"
echo "   • Використовуйте './activate_auto_coding_v2.sh --help' для перегляду всіх опцій"
echo ""
echo "🛑 Для зупинки: killall ollama watchexec"
