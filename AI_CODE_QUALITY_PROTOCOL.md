# 🤖 AI AGENT CODE QUALITY PROTOCOL

**Обов'язково для всіх ШІ агентів Windsurf при роботі з Atlas**

## 🚨 КРИТИЧНІ ПРАВИЛА

### 1. **ЗАВЖДИ після БУДЬ-ЯКОЇ зміни коду:**
```bash
./activate_auto_coding_2.1.sh
```
⏱️ **Очікуваний час**: 0.5-5 секунд  
❌ **Якщо зависло >10 сек**: Ctrl+C і запустити `python3 scripts/quick_syntax_fix.py`

### 2. **Перед зміною файлу:**
```bash
ruff check [файл.py]  # Перевірити поточний стан
```

### 3. **При виявленні помилок:**
- **F821** (undefined name) → Додати відсутні імпорти
- **Syntax errors** → Запустити `scripts/quick_syntax_fix.py`
- **F401, E402, F811** → Допустимі, не блокуючі

## 📋 АЛГОРИТМ ДІЙ

```
1. Змінити код
    ↓
2. Запустити: ./activate_auto_coding_2.1.sh
    ↓
3. Перевірити результат:
   ✅ <5 сек + "completed successfully" → OK
   ❌ >10 сек або помилки → Крок 4
    ↓
4. При проблемах:
   - python3 scripts/quick_syntax_fix.py
   - Повторити крок 2
    ↓
5. Продовжити розробку
```

## 🎯 КРИТЕРІЇ УСПІХУ

| Метрика | Ціль | Дія при невідповідності |
|---------|------|------------------------|
| Час виконання | <5 сек | Запустити quick_syntax_fix.py |
| Критичні помилки | 0 | Виправити F821, syntax errors |
| Прогрес | Чіткі повідомлення | Перевірити логи |
| Завершення | "successfully" | Проаналізувати помилки |

## 📂 ШВИДКІ ПОСИЛАННЯ

- **Детальний звіт проблем**: `AUTO_CODING_PROBLEM_RESOLUTION.md`
- **Команди Windsurf**: `WINDSURF_COMMANDS.md`
- **План розробки**: `DEV_PLAN.md`
- **Інструменти**: `scripts/` директорія

## 🚀 ПРИКЛАД ПРАВИЛЬНОГО ВИКОНАННЯ

```bash
$ ./activate_auto_coding_2.1.sh
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                 ATLAS AUTO-CODING SYSTEM 2.1                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Step 1/4: Critical syntax fixes - 0.1s
✅ Step 2/4: Improved code fixing - 0.6s  
✅ Step 3/4: Code formatting - 0.5s
⚠️  Step 4/4: Final check - Found 87 minor issues (expected)

🎉 Auto-coding completed successfully!
```

## ⚡ ШВИДКІ КОМАНДИ

```bash
# Повна перевірка
./activate_auto_coding_2.1.sh

# Тільки виправлення синтаксису
python3 scripts/quick_syntax_fix.py

# Поліпшення коду
python3 scripts/improved_atlas_code_fixer.py

# Форматування
ruff format .

# Статистика помилок
ruff check --statistics .
```

---
**Дата створення**: 2025-07-04  
**Версія**: 2.1  
**Статус**: Активний протокол для всіх ШІ агентів**
