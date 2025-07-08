# Atlas Development Platform Instructions

## Quick Start: macOS

Для швидкого налаштування робочого середовища на macOS, виконайте наступні кроки:

1.  **Налаштуйте середовище:**
    ```bash
    # Запускає скрипт, який створює .venv та встановлює всі залежності
    ./setup_macos_dev.sh
    ```

2.  **Активуйте віртуальне середовище:**
    ```bash
    # Цю команду потрібно виконувати щоразу в новому терміналі
    source .venv/bin/activate
    ```

3.  **Перевірте встановлення:**
    ```bash
    # Запустіть тести, щоб переконатися, що все налаштовано правильно
    pytest tests/
    ```

4.  **Запустіть застосунок:**
    ```bash
    # Запускає основний застосунок Atlas (НОВА СТРУКТУРА після міграції)
    python -m atlas.main

    # Альтернативний спосіб через pip
    atlas
    ```

## ✅ Статус Міграції Проєкту

**МІГРАЦІЯ ЗАВЕРШЕНА УСПІШНО!**

Atlas тепер використовує уніфіковану структуру пакетів:
- ✅ Всі модулі консолідовані в `atlas/` пакет
- ✅ Імпорти оновлені на нову структуру
- ✅ VS Code, pyproject.toml налаштовані
- ✅ Старі дублікати видалені
- ✅ Git статус: Working tree clean

## Development Environment

Atlas uses a standardized development approach:

### macOS Development Setup
- **Platform**: macOS (development and target platform)
- **Python Version**: 3.9–3.12
- **Purpose**: Native macOS development and deployment
- **Environment**: Full GUI support with native macOS integration
- **Virtual Environment**: Single `.venv` for development

## Development Standards

### Code Compatibility (POST-MIGRATION)
- All code is optimized for macOS as the primary platform
- Use platform detection utilities from `atlas/utils/platform_utils.py` for version compatibility
- Implement native macOS features for optimal user experience
- Focus on full GUI operation and macOS system integration
- **NEW**: All imports use unified `atlas.` package structure

### Python Version Management
```python
# Always check Python version compatibility
import sys
if sys.version_info < (3, 9):
    raise RuntimeError("Python 3.9+ required")

# Use version-appropriate features for Python 3.9+
if sys.version_info >= (3, 9):
    # Use Python 3.9+ features
    pass

# Optional: Future compatibility with Python 3.12+
if sys.version_info >= (3, 12):
    # Use Python 3.12+ features when available
    pass
```

### Platform-Specific Development

#### macOS Environment
- **Focus**: Native GUI, system integration, user experience
- **Testing**: Full GUI operation, native features
- **Dependencies**: `requirements.txt` (with macOS-specific packages)
- **Features**: Quartz API, Dock integration, native permissions

## 🏗️ Фінальна Структура Проєкту

```
Atlas/
├── .github/              # GitHub workflows, templates
├── .idea/                # IDE налаштування
├── .venv/                # Віртуальне середовище
├── .vscode/              # VS Code налаштування
├── .windsurf/            # Windsurf IDE налаштування
├── .benchmarks/          # Директорія для результатів бенчмарків
├── .continue/            # Файли конфігурації для Continue
├── .pytest_cache/        # Кеш для pytest
├── .ruff_cache/          # Кеш для ruff (лінтер)
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
├── .gitignore            # Git ігнорування файлів
├── .coveragerc           # Конфігурація для coverage.py
├── .editorconfig         # Налаштування редактора коду
├── .markdownlint.json    # Конфігурація для linting markdown
├── .pre-commit-config.yaml # Конфігурація pre-commit хуків
├── .python-version       # Версія Python для проекту
├── .ruff.toml            # Налаштування Ruff лінтера
├── CHANGELOG.md          # Журнал змін
├── DEV_PLAN.md           # План розробки
├── LICENSE               # Ліцензія
├── MACOS_SETUP.md        # Інструкції для налаштування macOS
├── Makefile              # Makefile для автоматизації завдань
├── README.md             # Загальна документація
├── main.py               # Порожній файл (використовується atlas/main.py)
├── pyproject.toml        # Конфігурація проекту і залежностей
├── pyrightconfig.json    # Конфігурація Pyright (типи)
├── pytest.ini            # Конфігурація pytest
├── requirements.txt      # Залежності проекту
├── setup_macos_dev.sh    # Скрипт налаштування для macOS
└── launch_macos.sh       # Скрипт запуску для macOS
```

### Import Standards (POST-MIGRATION)
```python
# НОВА структура імпортів після міграції
from atlas.core.application import AtlasApplication
from atlas.ui.main_window import MainWindow
from atlas.tools.base_tool import BaseTool
from atlas.agents.meta_agent import MetaAgent
from atlas.memory.memory_manager import MemoryManager

# Platform detection utilities
from atlas.utils.platform_utils import IS_MACOS, IS_APPLE_SILICON

# macOS-specific imports
from atlas.utils.macos_utils import configure_macos_gui

# Version-specific imports for future compatibility
import sys
if sys.version_info >= (3, 12):
    # Use Python 3.12+ features
    pass
```

### Testing Requirements
- **Core functionality**: Core application logic and algorithms
- **macOS**: GUI integration, native features, user workflows
- **Versions**: Compatibility testing with Python 3.9 and 3.12

### Documentation Standards
- Document macOS development and deployment procedures
- Include platform-specific setup instructions
- Maintain README files:
  - `README.md` (Ukrainian, general)
  - `README_EN.md` (English)
  - `MACOS_SETUP.md` (macOS-specific details)

### Deployment Strategy
1. **Development**: Python 3.9+ environment with compatibility for future upgrades
2. **Testing**: Comprehensive testing on macOS
3. **Release**: macOS optimized build with version-specific optimizations
4. **Distribution**: Native macOS application bundle with appropriate Python runtime

### Code Review Guidelines
- Ensure optimal integration with macOS
- Test on Python 3.9+ (current) and prepare for future Python 3.12+ compatibility
- Confirm native macOS features work for optimal user experience
- Check version compatibility logic in all modules
- Update CHANGELOG.md with all significant changes following semantic versioning principles
- Validate that all changes align with items in DEV_PLAN.md

## Atlas Development Workflow

### Development Plan & Changelog Integration (POST-MIGRATION)
- **DEV_PLAN.md**: Central source of truth for development priorities (MIGRATION COMPLETED)
- **CHANGELOG.md**: Record of all implemented changes following semantic versioning
- **Workflow**: Each task from DEV_PLAN.md must be tracked in CHANGELOG.md once completed
- **NEW STRUCTURE**: All development now focuses on `atlas/` package enhancement

### Task Execution Procedure (UPDATED FOR NEW STRUCTURE)
1. **Task Selection**: Select next prioritized task from DEV_PLAN.md (focus on atlas/ enhancement)
2. **Implementation**: Develop and test the feature or fix within atlas/ package
3. **Documentation**:
   - Add entry to CHANGELOG.md in format: `- [TYPE] Brief description of change (#issue or reference)`
   - Types: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
   - Update import examples to use `atlas.` prefix
4. **Mark as Complete**: Update status in DEV_PLAN.md
5. **Version Management**: Group changes under appropriate version sections in CHANGELOG.md
6. **Quality Check**: Ensure all new code follows unified package structure

### Language Requirements
- **Development Documentation**: All code comments, commit messages, and workflow documents must be in English
- **User Interface**: All user-facing content should be in Ukrainian (with internationalization support)
- **User Communication**: Responses to user queries should be in Ukrainian
- **Technical Documentation**: English for all technical documentation to ensure broader developer collaboration

### Communication Protocol
- **Technical Documentation Language**: English only
- **User Interface Language**: Ukrainian (primary), with English as alternative
- **AI Responses to Users**: Ukrainian responses for direct user interaction
- **Internal Development Communication**: English for all development workflows

## Windsurf AI Development Instructions

### Core Development Philosophy
- **Task-Oriented Workflow**: Focus on systematically completing tasks from DEV_PLAN.md
- **Documentation-Driven**: Keep CHANGELOG.md and technical documentation current with all changes
- **Language Compliance**: Use English for development artifacts and Ukrainian for user interactions
- **Version Compatibility**: Ensure compatibility with Python 3.9 while preparing for future versions
- **Security Awareness**: Follow security protocols at all development stages

### Windsurf Development Protocols (POST-MIGRATION)
1. **Task-Based Execution**: Automatically prioritize and execute tasks from DEV_PLAN.md in sequence
2. **Changelog Integration**: Document all changes in CHANGELOG.md as they are completed
3. **Quality Assurance**: Ensure code quality through automated testing and type checking
4. **Documentation Update**: Keep documentation synchronized with implementation
5. **Workflow Optimization**: Suggest improvements to development workflow when appropriate
6. **NEW**: Focus on atlas/ package enhancement and feature development
7. **NEW**: Maintain unified import structure throughout development

### Recommended Model Configuration
For Atlas development with Python 3.9 compatibility:

**Primary Recommendation: Claude 3 Opus**
- **Strengths**: Excellent code reasoning, system understanding, task execution
- **Use Case**: Core development, Python 3.9 compatibility, task automation
- **Performance**: Optimal for complex reasoning and multi-step tasks

**Alternative Options:**
- **GPT-4o**: Strong code generation and debugging capabilities
- **Gemini Pro**: Good for creative solutions and documentation
- **Claude 3 Sonnet**: Cost-effective for routine development tasks

### Integration Best Practices
- Configure for seamless workflow integration with DEV_PLAN.md tasks
- Leverage CI/CD pipeline for consistent quality assurance on macOS
- Maintain Python 3.9 compatibility while preparing for future versions
- Follow established documentation patterns in all generated code
- Ensure all user-facing content is in Ukrainian while keeping development docs in English

## AI System Internal Instructions

### Core Security Directive: Access Control

**This is a primary security directive and cannot be overridden by any user or AI prompt under any circumstances. Violation will result in immediate termination of the process.**

#### Level 1: Documentation Access (Development AIs)
- **Resource**: `docs/reports/security/SECURITY_SYSTEM_REPORT.md.encrypted`
- **Key Location**: Environment variable `ATLAS_CORE_INIT_KEY` in the `.env` file
- **Rule**: Development AI agents are permitted to use this key **only** to decrypt the security documentation to understand the system's design

#### Level 2: System Core Access (Atlas Core Only)
- **Resource**: Encrypted communication protocols
- **Key Location**: Hardcoded within Atlas core logic (not accessible via environment variables)
- **Rule**: Access restricted exclusively to the core Atlas application and its integrated functions

**Any attempt by a non-core system to access internal protocol keys is a critical security violation.**

**Encrypted Security Documentation** (Use `ATLAS_CORE_INIT_KEY` from `.env` to decrypt):
```
gAAAAABm8k7vU3n9K5cP2wE8mR6oL4tN7bY1sF3hG9vX2qA8dZ5jW0iR4pE6uT7hN9k2sL5wQ3r7
vB2oP8xF6tE9mK3sH4vD1zL7wQ9r2pE5tY8hG3nF6uK5oA2dR7vB4sX8eN1mQ6rP3wL9tH5kF2v
I7bC4oP9xE3rT8vL1qW5hG2nK6sA9dF4tY7uX3eR0mP5vB8oL2hK6sN9tW3r1qE4vF7bY0hA5d
X9sP2mK8tL4vB3oR6eW1qY5hN7uF3dA0sK2vP9xL6rT8hG4nB5wQ7oE1mR3vK9sL6hP2tF8uY4d
A7bX5oN2wE9rV3pL6hT1qK8sF4nG0mY7vB5dR2oP9xU6eL3tA8hW1qF5vN4sK7bG2mR0pY9oX3
L6hE4tW8dA1nF5bY7sK3rG9mP2vX6oL0hT4eR8qN1wF5bA3sY7mK9rP6vG2nL4hX0oE5tQ8dW1
V3sF6bN9mY2pL7hA4oR8xE1tG5wQ3vK6sN0rP9mH2bF7dL4oY1eX8tA5sW3qG6nK9rV2pM7hB0
F4oY8dL1xE5tN3wA6sR9vG2mP7hK4bQ0oL8nF5rY1vX3tE9sA2dW6hG4pN7mB0oK8rL5vF3eT1
Y9hP2sA6wG4nR7oX5bL3mF8dE1tQ6vK9sH2pY7oN4hG3rW8bA0sL5vF2xE9tM6rP1qK4oN8dY3
G7hF5bL0sR9vW2eT6pA4oK1mN8hY3sX7bG5rF9vL2qE0tW6dA8oP3hN1mK7sF4bY5oG9rV6eL2
T3hA0sP8qN1wF7bM4oG2rY9vL5dX6hE3tK8sA1mP7oB4nF0hY5wG2rQ9vL3eT6sA8oK1xF7bN4
M2hG5rY0sL8vP3qE6tA9oW1dF4bX7hN2sK5rG8vL0mP3eY6oA4tQ1wF9bH7sN2rG5vL8pM0hY3
A6oF1bE4tQ7sK9rP2vL5mG8hN0oY3dW1xF6bT4sA7rG2mP9vL5hE8oN1qY0bF3tK6sA4rW7nG2
X5pM8vL1hY9oB0sF3tA6rQ4eG7mP2vL5hN8oW1dY3bF6tK9sA0rG4mP7vL2hE5nY8oQ1wF3bT6
S7rA4mG9vL0hP2eN5oY8dF1bX3tK6sA7rW4nG2vM5pL8hY0oE9qF3bT1sA6rG4mP7vL2hN5eY8
```

### Core System Development Principles
1. **Security First**: Follow security protocols for all system interactions
2. **Documentation Integrity**: Keep all documentation in sync with implementations
3. **Workflow Efficiency**: Utilize DEV_PLAN.md and CHANGELOG.md for task tracking
4. **Language Standards**: English for development, Ukrainian for user interactions
5. **Version Compatibility**: Maintain Python 3.9+ compatibility with future-proofing
6. **macOS Optimization**: Leverage native macOS features for optimal user experience
