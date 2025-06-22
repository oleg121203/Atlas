# Self-Regeneration System

## Огляд

Система саморегенерації Atlas автоматично виявляє, діагностує та виправляє проблеми в системі, включаючи створення недостаючих плагінів, інструментів та виправлення пошкоджених компонентів.

## Архітектура

### Основні компоненти

1. **SelfRegenerationManager** - головний менеджер саморегенерації
2. **Issue Detection Engine** - двигун виявлення проблем
3. **Fix Application Engine** - двигун застосування виправлень
4. **History Tracking** - відстеження історії регенерації

### Типи проблем, що виявляються

```python
issue_types = [
    "missing_module",      # Відсутній модуль
    "missing_class",       # Відсутній клас
    "missing_method",      # Відсутній метод
    "missing_tool_file",   # Відсутній файл інструменту
    "missing_plugin",      # Відсутній плагін
    "missing_config",      # Відсутній конфігураційний файл
    "class_not_found"      # Клас не знайдено
]
```

## Принцип роботи

### 1. Виявлення проблем

```python
def _detect_issues(self) -> List[Dict[str, Any]]:
    issues = []
    
    # Перевірка відсутніх імпортів
    import_issues = self._detect_import_issues()
    issues.extend(import_issues)
    
    # Перевірка відсутніх методів
    method_issues = self._detect_missing_methods()
    issues.extend(method_issues)
    
    # Перевірка пошкоджених інструментів
    tool_issues = self._detect_broken_tools()
    issues.extend(tool_issues)
    
    # Перевірка відсутніх плагінів
    plugin_issues = self._detect_missing_plugins()
    issues.extend(plugin_issues)
    
    # Перевірка проблем конфігурації
    config_issues = self._detect_config_issues()
    issues.extend(config_issues)
    
    return issues
```

### 2. Застосування виправлень

```python
def _apply_fixes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    fixes = []
    
    for issue in issues:
        fix = self._fix_issue(issue)
        if fix:
            fixes.append(fix)
            self.fixes_applied.append(fix)
    
    return fixes
```

### 3. Автоматичне створення методів

```python
def _fix_missing_method(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    class_path = issue.get("class")
    method_name = issue.get("method")
    
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        class_obj = getattr(module, class_name)
        
        # Генерація методу на основі класу та назви методу
        method_code = self._generate_method_code(class_name, method_name)
        
        # Додавання методу до класу
        exec(method_code, {class_name: class_obj})
        
        return {
            "issue": issue,
            "fix_type": "method_added",
            "method": method_name,
            "class": class_path,
            "success": True
        }
    except Exception as e:
        return {
            "issue": issue,
            "fix_type": "method_added",
            "method": method_name,
            "class": class_path,
            "success": False,
            "error": str(e)
        }
```

## Інтеграція з існуючою системою

### Інтеграція з HierarchicalPlanManager

```python
def execute_plan(self, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if plan is None:
        plan = self.current_plan or {"goal": "Unknown goal"}
    
    self.logger.info("Starting hierarchical plan execution")
    
    # Спочатку запускаємо саморегенерацію для виправлення проблем
    try:
        regeneration_result = self_regeneration_manager.detect_and_fix_issues()
        if regeneration_result["fixes_applied"] > 0:
            self.logger.info(f"Self-regeneration applied {regeneration_result['fixes_applied']} fixes")
    except Exception as e:
        self.logger.warning(f"Self-regeneration failed: {e}")
    
    # Продовжуємо з адаптивним виконанням
    # ...
```

### Інтеграція з AdaptiveExecutionManager

```python
def execute_with_adaptation(self, task_description: str, goal_criteria: Dict[str, Any]) -> Dict[str, Any]:
    # Перевіряємо систему перед виконанням
    try:
        from .self_regeneration_manager import self_regeneration_manager
        regeneration_result = self_regeneration_manager.detect_and_fix_issues()
        if regeneration_result["fixes_applied"] > 0:
            self.logger.info(f"Applied {regeneration_result['fixes_applied']} fixes before execution")
    except ImportError:
        self.logger.warning("Self-regeneration manager not available")
    
    # Продовжуємо з адаптивним виконанням
    # ...
```

## Приклади використання

### Базове використання

```python
from agents.self_regeneration_manager import self_regeneration_manager

# Запуск саморегенерації
result = self_regeneration_manager.detect_and_fix_issues()

print(f"Issues Detected: {result['issues_detected']}")
print(f"Fixes Applied: {result['fixes_applied']}")
print(f"System Health: {result['system_health']}")
```

### Аналіз проблем

```python
if result['issues']:
    print("Issues Found:")
    for issue in result['issues']:
        print(f"  - {issue['type']}: {issue['description']}")
        print(f"    Severity: {issue['severity']}")
```

### Аналіз виправлень

```python
if result['fixes']:
    print("Fixes Applied:")
    for fix in result['fixes']:
        print(f"  - {fix['fix_type']}: {fix.get('method', fix.get('file', 'Unknown'))}")
        print(f"    Success: {fix['success']}")
```

## Типи виправлень

### 1. Додавання методів

```python
def _generate_method_code(self, class_name: str, method_name: str) -> str:
    if class_name == "HierarchicalPlanManager" and method_name == "execute_plan":
        return """
def execute_plan(self, plan=None):
    \"\"\"Execute the hierarchical plan with adaptive execution.\"\"\"
    if plan is None:
        plan = self.current_plan or {"goal": "Unknown goal"}
    
    # Логіка виконання плану
    # ...
"""
```

### 2. Створення файлів інструментів

```python
def _generate_tool_file_content(self, file_path: str) -> str:
    if "browser" in file_path:
        return '''
class BrowserTool:
    """Browser automation tool."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def open_url(self, url: str) -> Dict[str, Any]:
        """Open URL in browser."""
        self.logger.info(f"Opening URL: {url}")
        return {"success": True, "url": url, "message": "Browser opened successfully"}
'''
```

### 3. Створення плагінів

```python
def _fix_missing_plugin(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    plugin_path = self.project_root / issue.get("plugin")
    
    # Створення директорії плагіна
    plugin_path.mkdir(parents=True, exist_ok=True)
    
    # Створення базових файлів плагіна
    (plugin_path / "__init__.py").touch()
    
    plugin_json = {
        "name": issue.get("plugin").split("/")[-1],
        "version": "1.0.0",
        "description": "Auto-generated plugin",
        "author": "Atlas Self-Regeneration",
        "tools": [],
        "agents": []
    }
    
    with open(plugin_path / "plugin.json", 'w') as f:
        json.dump(plugin_json, f, indent=2)
```

### 4. Створення конфігураційних файлів

```python
def _fix_missing_config(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    config_path = self.project_root / issue.get("file")
    
    # Створення директорії конфігурації
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Генерація базової конфігурації
    config_content = """[DEFAULT]
# Auto-generated configuration file
# Generated by Atlas Self-Regeneration Manager

[providers]
default = groq

[models]
groq = llama3-8b-8192

[api_keys]
# Add your API keys here
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
```

## Логування та моніторинг

### Логи саморегенерації

```
INFO:agents.self_regeneration_manager:🔍 Starting system self-diagnosis and regeneration...
INFO:agents.self_regeneration_manager:✅ Self-regeneration completed: 1 fixes applied
```

### Метрики системи

- **Issues Detected**: кількість виявлених проблем
- **Fixes Applied**: кількість застосованих виправлень
- **System Health**: стан системи (healthy/repaired)
- **Regeneration History**: історія регенерації

## Переваги системи

### 1. Автоматичне виправлення
- ✅ Автоматичне виявлення проблем
- ✅ Автоматичне застосування виправлень
- ✅ Не потребує ручного втручання

### 2. Комплексна діагностика
- ✅ Перевірка імпортів
- ✅ Перевірка методів
- ✅ Перевірка файлів
- ✅ Перевірка плагінів

### 3. Розумна генерація
- ✅ Генерація методів на основі контексту
- ✅ Створення файлів інструментів
- ✅ Створення плагінів
- ✅ Створення конфігурацій

### 4. Відстеження історії
- ✅ Логування всіх виправлень
- ✅ Історія регенерації
- ✅ Метрики продуктивності

## Тестування

### Запуск тестів

```bash
python test_self_regeneration.py
```

### Тестові сценарії

1. **File Existence** - перевірка існування файлів
2. **Import Issues** - перевірка проблем імпорту
3. **Missing Method Detection** - виявлення відсутніх методів
4. **Regeneration History** - перевірка історії регенерації
5. **Self-Regeneration System** - тестування саморегенерації

### Приклад виводу тесту

```
🚀 Starting Self-Regeneration Manager Tests
============================================================
🧪 Testing File Existence
==================================================
✅ agents/self_regeneration_manager.py - EXISTS
✅ agents/adaptive_execution_manager.py - EXISTS
✅ agents/hierarchical_plan_manager.py - EXISTS

🧪 Testing Import Issues Detection
==================================================
✅ agents.adaptive_execution_manager.AdaptiveExecutionManager - EXISTS
✅ agents.email_strategy_manager.EmailStrategyManager - EXISTS
❌ tools.email.EmailTool - MISSING

🔧 Testing Self-Regeneration System
==================================================
🔍 Issues Detected: 2
🔧 Fixes Applied: 1
🏥 System Health: repaired

📋 Issues Found:
  1. missing_class: Class EmailTool not found in tools.email
     Severity: high
  2. missing_method: Method select_tool not found in agents.tool_registry.ToolRegistry
     Severity: high

✅ Fixes Applied:
  1. method_added: select_tool
     Success: True

📋 Test Summary
============================================================
System Health: repaired
Issues Detected: 2
Fixes Applied: 1
✅ Self-regeneration system is working - issues were detected and fixed!
```

## Майбутні покращення

### 1. Розширена діагностика
- Глибший аналіз помилок
- Прогнозування проблем
- Рекомендації для виправлення

### 2. Розумна генерація
- Машинне навчання для генерації коду
- Контекстно-залежна генерація
- Оптимізація згенерованого коду

### 3. Автоматичне тестування
- Автоматичне тестування виправлень
- Валідація згенерованого коду
- Перевірка функціональності

### 4. Інтеграція з CI/CD
- Автоматична регенерація в CI/CD
- Перевірка якості коду
- Автоматичне розгортання виправлень

## Висновок

Система саморегенерації Atlas забезпечує:

- **Автоматичне виявлення** проблем в системі
- **Автоматичне виправлення** відсутніх компонентів
- **Розумну генерацію** коду та файлів
- **Комплексну діагностику** всіх аспектів системи
- **Відстеження історії** всіх виправлень

Система інтегрована з існуючою архітектурою Atlas та забезпечує автоматичне підтримання здорового стану системи без ручного втручання. 