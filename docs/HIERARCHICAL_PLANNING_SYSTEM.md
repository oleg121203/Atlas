# Hierarchical Planning System

## Огляд

Система ієрархічного планування Atlas реалізує трирівневу структуру планування завдань, яка дозволяє розбивати складні цілі на управляні компоненти.

## Архітектура

### Три рівні планування:

1. **Стратегічний рівень (Phases)** 🎯
   - Високорівневі стратегічні цілі
   - Розбиває основну мету на 3-5 основних фаз
   - Приклад: "Дослідження", "Аналіз", "Реалізація", "Тестування"

2. **Тактичний рівень (Tasks)** 📝
   - Конкретні завдання для кожної фази
   - Розбиває фази на виконувані завдання
   - Приклад: "Зібрати дані", "Проаналізувати результати", "Написати звіт"

3. **Операційний рівень (Subtasks)** ⚙️
   - Конкретні дії з використанням інструментів
   - Виконувані кроки з призначеними інструментами
   - Приклад: "Використати search_web", "Використати analyze_data"

## Компоненти системи

### HierarchicalPlanManager
Основний клас для управління ієрархічним плануванням.

**Основні функції:**
- `create_hierarchical_plan(goal, context)` - створює повний план
- `update_task_status(task_id, status, progress)` - оновлює статус завдання
- `assign_tools_to_task(task_id, tools)` - призначає інструменти
- `validate_goal_completion(goal)` - валідує завершення цілі

### HierarchicalTaskView
UI компонент для відображення та управління завданнями.

**Особливості:**
- Деревовидна структура завдань
- Індикатори статусу та прогресу
- Кнопки управління (пауза, відновлення, скасування)
- Детальна інформація про завдання

## Статуси завдань

- **PENDING** - очікує виконання
- **RUNNING** - виконується
- **COMPLETED** - завершено успішно
- **FAILED** - завершено з помилкою
- **PAUSED** - призупинено
- **CANCELLED** - скасовано

## Інтеграція з Atlas

### В чаті
Система відображає процес планування в чаті як "думання":
```
🤔 Аналізую завдання...
📋 Стратегічний план створено
🎯 Фаза 1: Дослідження
  📝 Завдання 1.1: Зібрати дані
    ⚙️ Дія 1.1.1: search_web
```

### В інтерфейсі
Нова вкладка "Hierarchical Tasks" показує:
- Ієрархічну структуру завдань
- Статус кожного завдання
- Прогрес виконання
- Призначені інструменти та плагіни
- Можливість управління завданнями

## Процес роботи

1. **Створення плану**
   - Користувач вводить ціль
   - Система створює стратегічний план
   - Для кожної фази створюється тактичний план
   - Для кожного завдання створюється операційний план

2. **Виконання**
   - Завдання виконуються послідовно
   - Статус оновлюється в реальному часі
   - Прогрес передається на батьківські завдання

3. **Валідація**
   - Система перевіряє завершення всіх завдань
   - Визначає успішність досягнення цілі
   - Надає звіт про виконання

## Приклад використання

```python
# Створення плану
plan = hierarchical_plan_manager.create_hierarchical_plan(
    goal="Створити звіт про штучний інтелект",
    context={"format": "pdf", "sources": 10}
)

# Оновлення статусу завдання
hierarchical_plan_manager.update_task_status(
    task_id="task_123",
    status=TaskStatus.RUNNING,
    progress=0.5
)

# Валідація завершення
result = hierarchical_plan_manager.validate_goal_completion(goal)
```

## Переваги системи

1. **Структурованість** - чітка ієрархія завдань
2. **Відстеження** - повний контроль над виконанням
3. **Гнучкість** - можливість паузи та відновлення
4. **Прозорість** - відображення процесу в чаті
5. **Валідація** - автоматична перевірка завершення

## Майбутні покращення

- [ ] Автоматичне призначення інструментів
- [ ] Паралельне виконання незалежних завдань
- [ ] Машинне навчання для оптимізації планів
- [ ] Інтеграція з зовнішніми системами
- [ ] Розширені аналітики продуктивності 