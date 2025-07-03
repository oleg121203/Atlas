"""
Atlas Event Types

Цей файл містить всі стандартизовані типи подій для EventBus у системі Atlas.
Використовуйте ці константи для публікації та підписки на події у всіх модулях.
"""

# Події задач
TASK_COMPLETED = "TaskCompleted"  # Завдання виконано
TASK_CREATED = "TaskCreated"  # Створено нове завдання
TASK_UPDATED = "TaskUpdated"  # Оновлено завдання

# Події інструментів
NEW_TOOL_REGISTERED = "NewToolRegistered"  # Зареєстровано новий інструмент
TOOL_EXECUTED = "ToolExecuted"  # Інструмент виконано
TOOL_ERROR = "ToolError"  # Помилка під час виконання інструменту

# Події контексту та ШІ
CONTEXT_UPDATED = "ContextUpdated"  # Оновлено контекст
MEMORY_UPDATED = "MemoryUpdated"  # Оновлено пам'ять

# Події UI/UX
SHOW_NOTIFICATION = "ShowNotification"  # Показати повідомлення користувачу
USER_ACTION = "UserAction"  # Дія користувача (натискання, вибір)
THEME_CHANGED = "ThemeChanged"  # Змінено тему

# Події чату
CHAT_MESSAGE_SENT = "ChatMessageSent"  # Відправлено повідомлення у чат
CHAT_MESSAGE_RECEIVED = "ChatMessageReceived"  # Отримано повідомлення чату

# Події робочих процесів
WORKFLOW_EXECUTED = "WorkflowExecuted"  # Виконано робочий процес
