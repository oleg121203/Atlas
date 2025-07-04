current_language = "en"

translations = {
    "en": {
        "Chat": "Chat",
        "Tasks": "Tasks",
        "Agents": "Agents",
        "Plugins": "Plugins",
        "Settings": "Settings",
        "Stats": "Stats",
        "Profile": "Profile",
        "Theme": "Theme",
        "Refresh": "Refresh",
        "Reload Plugins": "Reload Plugins",
        "History": "History",
        "Add Task": "Add Task",
        "Delete Task": "Delete Task",
        "Add Agent": "Add Agent",
        "Delete Agent": "Delete Agent",
        "Enable": "Enable",
        "Disable": "Disable",
        "Edit": "Edit",
        "Save": "Save",
        "API usage:": "API usage:",
        "Active agents:": "Active agents:",
        "Tasks:": "Tasks:",
        "Plugins:": "Plugins:",
        "Select a task to delete.": "Select a task to delete.",
        "Select an agent to delete.": "Select an agent to delete.",
        "Select a plugin to enable.": "Select a plugin to enable.",
        "Select a plugin to disable.": "Select a plugin to disable.",
        "Select a setting to edit.": "Select a setting to edit.",
        "Settings saved (stub).": "Settings saved (stub).",
        "Click to generate a task": "Click to generate a task",
        "Generate Task": "Generate Task",
        "Type your message… (Markdown, emoji supported)": "Type your message… (Markdown, emoji supported)",
        "Send": "Send",
        "Open chat history": "Open chat history",
        "Save chat history": "Save chat history",
    },
    "uk": {
        "Chat": "Чат",
        "Tasks": "Завдання",
        "Agents": "Агенти",
        "Plugins": "Плагіни",
        "Settings": "Налаштування",
        "Stats": "Статистика",
        "Profile": "Профіль",
        "Theme": "Тема",
        "Refresh": "Оновити",
        "Reload Plugins": "Перезавантажити плагіни",
        "History": "Історія",
        "Add Task": "Додати завдання",
        "Delete Task": "Видалити завдання",
        "Add Agent": "Додати агента",
        "Delete Agent": "Видалити агента",
        "Enable": "Увімкнути",
        "Disable": "Вимкнути",
        "Edit": "Редагувати",
        "Save": "Зберегти",
        "API usage:": "Використання API:",
        "Active agents:": "Активних агентів:",
        "Tasks:": "Завдань:",
        "Plugins:": "Плагінів:",
        "Select a task to delete.": "Виберіть завдання для видалення.",
        "Select an agent to delete.": "Виберіть агента для видалення.",
        "Select a plugin to enable.": "Виберіть плагін для увімкнення.",
        "Select a plugin to disable.": "Виберіть плагін для вимкнення.",
        "Select a setting to edit.": "Виберіть налаштування для редагування.",
        "Settings saved (stub).": "Налаштування збережено (заглушка).",
        "Click to generate a task": "Натисніть, щоб згенерувати завдання",
        "Generate Task": "Згенерувати завдання",
        "Type your message… (Markdown, emoji supported)": "Введіть повідомлення… (Markdown, emoji підтримується)",
        "Send": "Відправити",
        "Open chat history": "Відкрити історію чату",
        "Save chat history": "Зберегти історію чату",
    },
    "ru": {
        "Chat": "Чат",
        "Tasks": "Задачи",
        "Agents": "Агенты",
        "Plugins": "Плагины",
        "Settings": "Настройки",
        "Stats": "Статистика",
        "Profile": "Профиль",
        "Theme": "Тема",
        "Refresh": "Обновить",
        "Reload Plugins": "Перезагрузить плагины",
        "History": "История",
        "Add Task": "Добавить задачу",
        "Delete Task": "Удалить задачу",
        "Add Agent": "Добавить агента",
        "Delete Agent": "Удалить агента",
        "Enable": "Включить",
        "Disable": "Выключить",
        "Edit": "Редактировать",
        "Save": "Сохранить",
        "API usage:": "Использование API:",
        "Active agents:": "Активных агентов:",
        "Tasks:": "Задач:",
        "Plugins:": "Плагинов:",
        "Select a task to delete.": "Выберите задачу для удаления.",
        "Select an agent to delete.": "Выберите агента для удаления.",
        "Select a plugin to enable.": "Выберите плагин для включения.",
        "Select a plugin to disable.": "Выберите плагин для выключения.",
        "Select a setting to edit.": "Выберите настройку для редактирования.",
        "Settings saved (stub).": "Настройки сохранены (заглушка).",
        "Click to generate a task": "Нажмите, чтобы сгенерировать задачу",
        "Generate Task": "Сгенерировать задачу",
        "Type your message… (Markdown, emoji supported)": "Введите сообщение… (Markdown, emoji поддерживается)",
        "Send": "Отправить",
        "Open chat history": "Открыть историю чата",
        "Save chat history": "Сохранить историю чата",
    },
}


def _(text):
    return translations.get(current_language, translations["en"]).get(text, text)


def set_language(lang_code):
    global current_language
    if lang_code in translations:
        current_language = lang_code
