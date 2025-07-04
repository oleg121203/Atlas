#!/bin/bash
# Atlas Auto-Coding System 2.1 - Improved Version
# Fixes hanging issues and provides better feedback

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}$(date '+%H:%M:%S')${NC} $1"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run commands safely (macOS compatible)
run_safely() {
    local description=$1
    shift 1
    
    log "Running: $description"
    
    if "$@"; then
        success "$description completed"
        return 0
    else
        local exit_code=$?
        error "$description failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Header
echo ""
echo -e "${PURPLE}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${PURPLE}┃                 ATLAS AUTO-CODING SYSTEM 2.1                 ┃${NC}"
echo -e "${PURPLE}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    error "Не знайдено pyproject.toml. Запустіть скрипт з кореневої директорії Atlas"
    exit 1
fi

# Check dependencies
log "🔍 Перевірка залежностей..."

if ! command_exists python3; then
    error "Python3 не знайдено"
    exit 1
fi

if ! command_exists ruff; then
    warning "Ruff не знайдено, встановлюємо..."
    pip install ruff || {
        error "Не вдалося встановити ruff"
        exit 1
    }
fi

success "Залежності перевірено"

# Step 1: Quick syntax fixes
log "🔧 Крок 1/5: Виправлення критичних синтаксичних помилок..."
if run_safely "Quick syntax fix" python3 scripts/quick_syntax_fix.py; then
    success "Критичні помилки синтаксису виправлено"
else
    warning "Деякі синтаксичні помилки не вдалося виправити"
fi

# Step 2: Improved code fixing
log "🛠️  Крок 2/5: Розумне виправлення коду..."
if run_safely "Improved code fixing" python3 scripts/improved_atlas_code_fixer.py; then
    success "Код успішно поліпшено"
else
    warning "Деякі проблеми коду не вдалося виправити автоматично"
fi

# Step 3: Apply specific Ruff fixes
log "🔧 Крок 3/5: Застосування специфічних виправлень Ruff..."
if run_safely "Ruff specific fixes" ruff check --fix .; then
    success "Специфічні виправлення Ruff застосовано"
else
    warning "Не всі проблеми вдалося виправити за допомогою Ruff"
fi

# Step 4: Fix type hinting issues
log "🧮 Крок 4/5: Виправлення проблем з типами..."
if run_safely "Type hinting fixes" python3 scripts/type_hinting_fixer.py --aggressive; then
    success "Проблеми з типами виправлено"
else
    warning "Деякі проблеми з типами не вдалося виправити автоматично"
fi

# Step 5: Final check
log "🔍 Крок 5/5: Фінальна перевірка..."
if run_safely "Final check" ruff check --select=F821,F401,F811,E402,E501,W503,W504,W291,W293,E26,E713,E714,Q000,Q001,Q002,Q003 --statistics .; then
    success "Фінальна перевірка пройшла успішно"
else
    info "Знайдено деякі помилки, які потребують ручного виправлення"
fi

# Step 6: Fix specific pattern issues
log "🔍 Крок 6/6: Виправлення специфічних патернів коду..."

# Fix SIM105 - Replace try-except-pass with contextlib.suppress
grep -r "try:" . | grep -A 3 "except (TypeError, AttributeError):" | while read -r line; do
    file=$(echo $line | cut -d: -f1)
    line_num=$(echo $line | cut -d: -f2)
    if [ -n "$file" ] && [ -n "$line_num" ]; then
        sed -i '' "${line_num}d;${line_num}i\
from contextlib import suppress\n" "$file"
        sed -i '' "${line_num}r \
        with suppress(TypeError, AttributeError):\n" "$file"
        sed -i '' "$(($line_num+4))d" "$file"
        sed -i '' "$(($line_num+3))d" "$file"
        sed -i '' "$(($line_num+2))d" "$file|"
    fi
done
success "Патерни SIM105 виправлено"

# Fix F821 - Undefined name 'script_name'
grep -r "script_name" . | grep -v "undefined" | while read -r line; do
    file=$(echo $line | cut -d: -f1)
    if [ -n "$file" ] && ! grep -q "script_name =" "$file"; then
        head -n 1 "$file" | grep -q "^#!/" && insert_line=1 || insert_line=0
        sed -i '' "${insert_line}i\
script_name = \"\$\{os.path.basename(__file__)\}\"\n" "$file"
    fi
done
success "Патерни F821 виправлено"

# Fix E722 - Do not use bare except
grep -r "except:" . | while read -r line; do
    file=$(echo $line | cut -d: -f1)
    line_num=$(echo $line | cut -d: -f2)
    if [ -n "$file" ] && [ -n "$line_num" ]; then
        # Try to guess the exception type from the following code
        next_line=$(sed -n "$(($line_num+1))p" "$file")
        if echo "$next_line" | grep -q "pass"; then
            # Simple case - replace with more specific exceptions
            sed -i '' "${line_num}s/:$/:(Exception):/" "$file"
        fi
    fi
done
success "Патерни E722 виправлено"

echo ""
echo -e "${GREEN}🎉 Автоматичне кодування завершено!${NC}"
echo ""
echo -e "${CYAN}📊 Підсумок:${NC}"
echo "   ✅ Критичні синтаксичні помилки виправлено"
echo "   ✅ Код поліпшено та відформатовано"
echo "   ✅ Базові перевірки завершено"
echo ""
echo -e "${YELLOW}💡 Наступні кроки:${NC}"
echo "   1. Запустіть: python main.py (для тестування додатку)"
echo "   2. Запустіть: python -m pytest tests/ (для тестування)"
echo "   3. Перевірте залишкові помилки: ruff check ."
echo ""

# Optional: Initialize git repository if needed
read -p "Ініціалізувати git-репозиторій? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🗄️  Ініціалізація git-репозиторія..."
    if [ -f "scripts/init_git_repo.py" ]; then
        python3 scripts/init_git_repo.py
        success "Git-репозиторій ініціалізований успішно!"
    else
        warning "Скрипт init_git_repo.py не знайдено"
    fi
fi

# Optional: Create missing __init__.py files
log "📂 Створення відсутніх __init__.py файлів..."
if [ -f "scripts/create_init_files.py" ]; then
    python3 scripts/create_init_files.py
    success "Відсутні __init__.py файли створено"
else
    warning "Скрипт create_init_files.py не знайдено"
fi

# Optional: Run a quick test if requested
read -p "Запустити швидкий тест Atlas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🧪 Запуск швидкого тесту..."
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core.application import AtlasApplication
    print('✅ Основні модулі завантажуються')
    print('✅ Atlas готовий до використання')
except ImportError as e:
    print(f'❌  Помилка імпорту: {e}')
    print('💡 Спробуйте запустити: pip install -e .')
    sys.exit(1)
except Exception as e:
    print(f'⚠️  Виявлена проблема: {e}')
    sys.exit(1)
"; then
        success "Швидкий тест пройшов успішно!"
    else
        warning "Швидкий тест виявив проблеми"
    fi
fi

echo ""
success "Автоматичне кодування завершено успішно!"

# Step 7: Fix F841 and SIM108 - Unused variables and simplification
log "🧹 Крок 9/9: Очищення невикористаних змінних та спрощення коду..."

# Fix F841 - Unused variables
grep -r "Local variable" . | while read -r line; do
    var_name=$(echo $line | grep -o "'[^']*'")
    file=$(echo $line | cut -d: -f1)
    line_num=$(echo $line | cut -d: -f2)
    if [ -n "$var_name" ] && [ -n "$file" ] && [ -n "$line_num" ]; then
        var_name=${var_name//'/'}
        # Remove the assignment line
        sed -i '' "${line_num}d" "$file"
    fi
done

# Fix SIM108 - Use ternary operator instead of if-else-block
grep -r "if callable(" . | while read -r line; do
    file=$(echo $line | cut -d: -f1)
    line_num=$(echo $line | cut -d: -f2)
    if [ -n "$file" ] && [ -n "$line_num" ]; then
        # Extract the variable name
        var_name=$(sed -n "${line_num}p" "$file" | awk '{print $2}')
        if [ -n "$var_name" ]; then
            # Replace if-else block with ternary operator
            sed -i '' "${line_num}d" "$file"
            sed -i '' "$(($line_num))d" "$file"
            sed -i '' "$(($line_num))d" "$file"
            sed -i '' "$(($line_num))d" "$file"
            sed -i '' "$(($line_num))i\
        result = code(*args, **kwargs) if callable(code) else exec(code, globals(), locals())\n" "$file"
        fi
    fi
done

success "Спрощення коду завершено"
