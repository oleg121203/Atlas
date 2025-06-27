#!/bin/bash

# === АТЛАС АВТО-КОДИНГ СИСТЕМА 2.0 ===
# Активація розширеної системи автоматизації коду з інтегрованими виправленнями

# Встановлюємо кольори для виводу
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${BLUE}┃                 ${GREEN}ATLAS AUTO-CODING SYSTEM 2.0${BLUE}                 ┃${NC}"
echo -e "${BLUE}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"

# Функція для перевірки залежностей
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}⚠️  $1 не встановлено.${NC}"
        return 1
    fi
    return 0
}

# Функція для встановлення залежностей Python
install_python_deps() {
    echo -e "${CYAN}📦 Встановлення Python залежностей...${NC}"
    pip install ruff pre-commit
    echo -e "${GREEN}✅ Python залежності встановлено${NC}"
}

# Перевірка, чи ми в правильній директорії
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Запустіть скрипт з кореневої директорії проєкту Atlas${NC}"
    exit 1
fi

# Перевіряємо залежності
echo -e "${CYAN}🔍 Перевірка залежностей...${NC}"
DEPENDENCIES_OK=true

check_dependency python || DEPENDENCIES_OK=false
check_dependency pip || DEPENDENCIES_OK=false

if [ "$DEPENDENCIES_OK" = false ]; then
    echo -e "${RED}❌ Відсутні необхідні залежності. Встановіть їх та спробуйте знову.${NC}"
    exit 1
fi

# Встановлюємо Python залежності
install_python_deps

# Запуск Ollama (якщо встановлено)
if check_dependency ollama; then
    echo -e "${CYAN}🧠 Запуск Ollama...${NC}"
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Перевірка моделей
    echo -e "${CYAN}🔍 Перевірка AI моделей...${NC}"
    if ! ollama list | grep -q "qwen2.5-coder:latest"; then
        echo -e "${YELLOW}⬇️  Завантаження qwen2.5-coder:latest...${NC}"
        ollama pull qwen2.5-coder:latest
    fi

    if ! ollama list | grep -q "qwen2.5-coder:1.5b"; then
        echo -e "${YELLOW}⬇️  Завантаження qwen2.5-coder:1.5b...${NC}"
        ollama pull qwen2.5-coder:1.5b
    fi
    
    echo -e "${GREEN}✅ Ollama запущено з моделями coder${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama не знайдено. AI функціонал буде обмежений.${NC}"
    echo -e "${YELLOW}   Встановіть Ollama: https://ollama.com${NC}"
fi

# Запускаємо інтегровані скрипти автоматичних виправлень
echo -e "${CYAN}🛠️  Запуск автоматичного виправлення коду...${NC}"

# Спочатку виправлення імпортів (найчастіша проблема)
echo -e "${CYAN}📦 Крок 1/3: Виправлення імпортів...${NC}"
python scripts/quick_imports_fixer.py

# Далі виправлення шаблонів
echo -e "${CYAN}🧩 Крок 2/3: Виправлення шаблонів коду...${NC}"
python scripts/quick_pattern_fixer.py

# Потім повний фіксер для всіх інших типів помилок
echo -e "${CYAN}🔍 Крок 3/3: Фінальний аналіз та виправлення...${NC}"
python scripts/atlas_code_fixer.py

# Налаштування pre-commit хуків
echo -e "${CYAN}🔧 Налаштування pre-commit хуків...${NC}"
pre-commit install
echo -e "${GREEN}✅ Pre-commit хуки активовано${NC}"

# Запуск автоматичного watcher для Ruff
if check_dependency watchexec; then
    echo -e "${CYAN}👁️  Запуск Ruff auto-watcher...${NC}"
    watchexec -e py -- ruff check --fix --unsafe-fixes . &
    WATCHER_PID=$!
    echo -e "${GREEN}✅ Ruff watcher активовано (PID: $WATCHER_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  watchexec не встановлено. Автоматичне відстеження файлів недоступне.${NC}"
    echo -e "${YELLOW}   Встановіть watchexec: brew install watchexec${NC}"
fi

# Запуск VS Code
echo -e "${CYAN}💻 Запуск VS Code з налаштуваннями...${NC}"
code .

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Atlas Auto-Coding System 2.0 активовано!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Інформація про активні процеси
echo -e "${CYAN}📋 Активні процеси:${NC}"
if [ ! -z "$OLLAMA_PID" ]; then
    echo -e "${GREEN}   • Ollama Server (PID: $OLLAMA_PID)${NC}"
fi
if [ ! -z "$WATCHER_PID" ]; then
    echo -e "${GREEN}   • Ruff Auto-Watcher (PID: $WATCHER_PID)${NC}"
fi
echo -e "${GREEN}   • VS Code з Continue AI${NC}"

# Функціональність
echo -e "\n${CYAN}🔥 Функціонал:${NC}"
echo -e "${GREEN}   ✓ Інтегрований автоматичний фіксер коду${NC}"
echo -e "${GREEN}   ✓ Виправлення помилок F821, SIM102, B904, E402, F401 та інших${NC}"
echo -e "${GREEN}   ✓ Автоматичне форматування коду${NC}"
echo -e "${GREEN}   ✓ Pre-commit хуки для контролю якості${NC}"
echo -e "${GREEN}   ✓ Постійний моніторинг файлів${NC}"
echo -e "${GREEN}   ✓ AI асистент для складних помилок${NC}"

# Інструкції з використання
echo -e "\n${CYAN}💡 Використання:${NC}"
echo -e "${GREEN}   • Для повного виправлення помилок: ./scripts/atlas_code_fixer.py${NC}"
echo -e "${GREEN}   • Просто редагуйте .py файли - Ruff виправить автоматично${NC}"
echo -e "${GREEN}   • Використовуйте Ctrl+I у VS Code для AI асистента${NC}"
echo -e "${GREEN}   • Для складних випадків: git commit (pre-commit запустить виправлення)${NC}"

# Інструкції з зупинки
echo -e "\n${CYAN}🛑 Для зупинки системи:${NC}"
echo -e "${GREEN}   killall ollama watchexec${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
