# 🤖 Atlas - Autonomous Computer Agent

Atlas - це потужний автономний комп'ютерний агент з AI, розроблений для автоматизації завдань на macOS.

## 🚀 Швидкий старт

### 1. Встановлення залежностей
```bash
pip install -r requirements-macos.txt
```

### 2. Налаштування API ключів
```bash
cp .env.example .env
# Відредагуйте .env файл, додавши свої API ключі
```

### 3. Запуск Atlas
```bash
python main.py
```

## 📁 Структура проекту

```
📦 Atlas/
├── 🤖 main.py                 # Головний файл програми
├── ⚙️ config_manager.py       # Менеджер конфігурації
├── 🔐 .env                    # API ключі (не в git)
├── 📋 .env.example            # Шаблон для .env
├── 
├── 📁 agents/                 # AI агенти
├── 📁 tools/                  # Інструменти автоматизації
├── 📁 ui/                     # Користувацький інтерфейс
├── 📁 docs/                   # Документація
├── 📁 data/                   # Дані програми
├── 📁 memory/                 # Система пам'яті
├── 📁 dev-tools/              # Інструменти розробки
└── 📁 unused/                 # Застарілі файли
```

## 🔧 Провайдери LLM

Atlas підтримує:
- **Gemini** (Google) - default
- **OpenAI** (GPT-4, ChatGPT)
- **Mistral AI**
- **Groq**
- **Anthropic** (Claude)

## 📚 Документація

Повну документацію дивіться в папці `docs/`:
- [Інсталяція](INSTALLATION.md)
- [Налаштування API ключів](dev-tools/documentation/API_KEYS_SETUP.md)

## 🛠️ Розробка

Інструменти розробки в папці `dev-tools/`:
- `testing/` - тести та налагодження
- `setup/` - скрипти налаштування
- `documentation/` - документація розробки

## 🎯 Особливості

- ✅ Автономне виконання завдань
- ✅ Інтеграція з macOS (screenshot, clipboard, mouse/keyboard)
- ✅ Підтримка множини LLM провайдерів
- ✅ Розумна система пам'яті
- ✅ Генерація власних інструментів
- ✅ Headless режим для серверів

---

Made with ❤️ для автоматизації рутинних завдань
