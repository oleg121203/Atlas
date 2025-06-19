# Atlas - Структура Проекту (Очищена)

## 📁 Основна структура:

```
📦 autoclicker/
├── 🤖 main.py                 # Головний файл програми
├── ⚙️ config_manager.py       # Менеджер конфігурації
├── 🔐 .env                    # Змінні середовища (не в git)
├── 📋 .env.example            # Шаблон для .env
├── 
├── 📁 agents/                 # AI агенти
│   ├── agent_manager.py
│   ├── llm_manager.py
│   ├── chat_context_manager.py
│   └── ...
├── 
├── 📁 tools/                  # Інструменти та утиліти
│   ├── screenshot_tool.py
│   ├── clipboard_tool.py
│   ├── generated/             # Згенеровані інструменти
│   └── ...
├── 
├── 📁 ui/                     # Інтерфейс користувача
│   ├── main_interface.py
│   ├── chat_view.py
│   └── ...
├── 
├── 📁 docs/                   # Документація користувача
│   ├── README.md
│   ├── INSTALLATION.md
│   └── ...
├── 
├── 📁 dev-tools/              # Інструменти розробки
│   ├── testing/               # Тести
│   ├── setup/                 # Скрипти налаштування
│   ├── documentation/         # Документація розробки
│   └── README.md
├── 
└── 📁 memory/                 # Система пам'яті
    └── ...
```

## 🚀 Запуск Atlas:

```bash
cd /workspaces/autoclicker
python main.py
```

## ⚙️ Налаштування:

1. Скопіювати `.env.example` в `.env`
2. Додати свої API ключі в `.env`
3. Запустити програму

## 🛠️ Розробка:

Всі інструменти розробки знаходяться в папці `dev-tools/`:
- Тести: `dev-tools/testing/`
- Налаштування: `dev-tools/setup/`
- Документація: `dev-tools/documentation/`
