# Adaptive Execution System

## Огляд

Адаптивна система виконання Atlas автоматично змінює стратегію виконання завдань, якщо початковий підхід не досягає бажаного результату. Система включає самодіагностику, аналіз помилок та автоматичну адаптацію стратегій.

## Архітектура

### Основні компоненти

1. **AdaptiveExecutionManager** - головний менеджер адаптивного виконання
2. **ExecutionStrategy** - перелік доступних стратегій виконання
3. **ExecutionAttempt** - представлення спроби виконання
4. **Self-Diagnosis Engine** - двигун самодіагностики

### Стратегії виконання

```python
class ExecutionStrategy(Enum):
    DIRECT_API = "direct_api"           # Прямий API доступ
    BROWSER_AUTOMATION = "browser_automation"  # Автоматизація браузера
    HYBRID_APPROACH = "hybrid_approach" # Гібридний підхід
    MANUAL_SIMULATION = "manual_simulation"     # Ручна симуляція
    ALTERNATIVE_METHODS = "alternative_methods" # Альтернативні методи
```

## Принцип роботи

### 1. Аналіз завдання
Система аналізує опис завдання та визначає найкращі початкові стратегії:

```python
def _get_strategies_for_task(self, task_description: str) -> List[ExecutionStrategy]:
    task_lower = task_description.lower()
    
    if any(keyword in task_lower for keyword in ["email", "gmail", "mail"]):
        return [
            ExecutionStrategy.DIRECT_API,
            ExecutionStrategy.BROWSER_AUTOMATION,
            ExecutionStrategy.HYBRID_APPROACH,
            ExecutionStrategy.MANUAL_SIMULATION
        ]
```

### 2. Виконання з адаптацією
```python
def execute_with_adaptation(self, task_description: str, goal_criteria: Dict[str, Any]) -> Dict[str, Any]:
    for attempt_num in range(self.max_attempts):
        strategy = strategies[attempt_num]
        result = self._execute_strategy(strategy, task_description, attempt)
        
        if self._is_goal_achieved(result, goal_criteria):
            return self._create_final_result(result, attempt_num + 1, strategy)
        else:
            # Самодіагностика та адаптація
            diagnosis = self._perform_self_diagnosis(task_description, result, attempt)
            self._adapt_strategy(task_description, diagnosis, attempt_num)
```

### 3. Самодіагностика
Система автоматично аналізує причини невдачі:

```python
def _perform_self_diagnosis(self, task_description: str, result: Dict[str, Any], attempt: ExecutionAttempt) -> Dict[str, Any]:
    diagnosis = {
        "task_description": task_description,
        "strategy_used": attempt.strategy.value,
        "execution_time": (attempt.end_time or 0) - attempt.start_time,
        "issues_found": []
    }
    
    # Аналіз результатів
    if not result.get("success"):
        diagnosis["issues_found"].append("Execution failed")
    
    if "emails" in task_description.lower():
        emails_found = result.get("data", {}).get("emails", [])
        if len(emails_found) == 0:
            diagnosis["issues_found"].append("No emails found")
```

### 4. Адаптація стратегії
На основі діагностики система генерує нову стратегію:

```python
def _generate_adaptive_strategy(self, task_description: str, attempt_num: int) -> ExecutionStrategy:
    failed_strategies = [a.strategy for a in self.attempts if a.status == ExecutionStatus.FAILED]
    all_strategies = list(ExecutionStrategy)
    untried_strategies = [s for s in all_strategies if s not in failed_strategies]
    
    if untried_strategies:
        return untried_strategies[0]
    else:
        if "email" in task_description.lower():
            return ExecutionStrategy.MANUAL_SIMULATION
        else:
            return ExecutionStrategy.ALTERNATIVE_METHODS
```

## Інтеграція з існуючою системою

### Інтеграція з HierarchicalPlanManager

```python
def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
    # Використання адаптивного виконання для головної мети
    main_goal = plan.get("goal", "Unknown goal")
    
    result = adaptive_execution_manager.execute_with_adaptation(
        task_description=main_goal,
        goal_criteria=goal_criteria
    )
    
    return result
```

### Інтеграція з Email Strategy Manager

```python
def _execute_direct_api(self, task_description: str, attempt: ExecutionAttempt) -> Dict[str, Any]:
    if any(keyword in task_description.lower() for keyword in ["email", "gmail", "mail"]):
        try:
            from .email_strategy_manager import email_strategy_manager
            return email_strategy_manager.execute_email_task(task_description)
        except ImportError:
            self.logger.warning("Email Strategy Manager not available")
```

## Приклади використання

### Базове використання

```python
from agents.adaptive_execution_manager import adaptive_execution_manager

# Виконання завдання з адаптацією
result = adaptive_execution_manager.execute_with_adaptation(
    task_description="Find all security emails in Gmail",
    goal_criteria={
        "emails": True,
        "security_emails": True
    }
)

print(f"Success: {result['success']}")
print(f"Attempts: {result['attempts_used']}")
print(f"Final Strategy: {result['final_strategy']}")
```

### Аналіз історії адаптації

```python
if result.get('adaptation_history'):
    for adaptation in result['adaptation_history']:
        print(f"Attempt {adaptation['attempt_num']}: {adaptation['adaptation_reason']}")
        if 'diagnosis' in adaptation:
            issues = adaptation['diagnosis'].get('issues_found', [])
            print(f"  Issues: {', '.join(issues)}")
```

## Критерії успіху

### Для email завдань
```python
goal_criteria = {
    "emails": True,           # Знайдено хоча б один email
    "security_emails": True   # Знайдено хоча б один security email
}
```

### Для browser завдань
```python
goal_criteria = {
    "navigation": True,       # Успішна навігація
    "search": True           # Успішний пошук
}
```

## Логування та моніторинг

### Логи адаптації
```
INFO:agents.adaptive_execution_manager:Starting adaptive execution for: Find all emails related to Google account security in Gmail
INFO:agents.adaptive_execution_manager:Attempt 1: Using strategy direct_api
WARNING:agents.adaptive_execution_manager:Goal not achieved with direct_api. Diagnosis: {'issues_found': ['No emails found']}
INFO:agents.adaptive_execution_manager:Adapting strategy after attempt 1
INFO:agents.adaptive_execution_manager:Attempt 2: Using strategy browser_automation
```

### Метрики виконання
- Кількість спроб
- Час виконання кожної стратегії
- Історія адаптацій
- Діагностика помилок

## Переваги системи

### 1. Автоматична адаптація
- Система автоматично змінює стратегію при невдачі
- Не потребує ручного втручання
- Адаптується до різних типів завдань

### 2. Самодіагностика
- Автоматичний аналіз причин невдачі
- Детальна діагностика кожного кроку
- Логування всіх адаптацій

### 3. Універсальність
- Підтримка різних типів завдань
- Розширюваний набір стратегій
- Інтеграція з існуючими системами

### 4. Надійність
- Множинні спроби виконання
- Fallback стратегії
- Детальна звітність

## Майбутні покращення

### 1. Машинне навчання
- Навчання на основі історії адаптацій
- Прогнозування найкращої стратегії
- Оптимізація послідовності спроб

### 2. Розширені стратегії
- Паралельне виконання
- Комбіновані стратегії
- Спеціалізовані адаптери

### 3. Покращена діагностика
- Глибший аналіз помилок
- Рекомендації для виправлення
- Прогнозування проблем

## Тестування

### Запуск тестів
```bash
python test_adaptive_execution.py
```

### Тестові сценарії
1. **Email Task Adaptation** - тестування адаптації для email завдань
2. **Browser Task Adaptation** - тестування адаптації для browser завдань
3. **Strategy Generation** - тестування генерації стратегій
4. **Goal Achievement Detection** - тестування визначення досягнення мети

### Приклад виводу тесту
```
🧪 Testing Email Task Adaptation
==================================================
Task: Find all emails related to Google account security in Gmail
Goal Criteria: {'emails': True, 'security_emails': True}

📊 Execution Results:
Success: True
Attempts Used: 4
Final Strategy: manual_simulation
Total Execution Time: 6.95s
Message: Goal achieved after 4 attempts using manual_simulation

🔄 Adaptation History:
  1. Attempt 0: Goal not achieved or error occurred
     Issues: No emails found, No security emails found
  2. Attempt 1: Goal not achieved or error occurred
     Issues: No emails found, No security emails found
  3. Attempt 2: Goal not achieved or error occurred
     Issues: No emails found, No security emails found
```

## Висновок

Адаптивна система виконання Atlas забезпечує:

- **Автоматичну адаптацію** стратегій при невдачі
- **Самодіагностику** проблем та помилок
- **Універсальність** для різних типів завдань
- **Надійність** через множинні спроби
- **Детальне логування** всіх адаптацій

Система інтегрована з існуючою архітектурою Atlas та забезпечує інтелектуальне виконання завдань з автоматичною адаптацією до змінних умов. 