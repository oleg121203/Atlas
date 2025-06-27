#!/usr/bin/env python3
"""
Швидкий масовий фіксер для Atlas проєкту
Виправляє найчастіші помилки Ruff автоматично
"""

import subprocess
import sys
from pathlib import Path


def run_ruff_fixes():
    """Запускає Ruff з автоматичними виправленнями"""

    # Список правил для автоматичного виправлення
    fixable_rules = [
        "F401",  # Невикористані імпорти
        "F811",  # Повторне визначення
        "E402",  # Імпорти не на початку файлу
        "SIM108",  # Ternary operator
        "I001",  # Сортування імпортів
    ]

    print("🔧 Запуск автоматичних виправлень Ruff...")

    try:
        # Запускаємо ruff з --fix для правил, які можна виправити автоматично
        cmd = [
            "ruff",
            "check",
            f"--select={','.join(fixable_rules)}",
            "--fix",
            "--unsafe-fixes",
            ".",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Автоматичні виправлення застосовано успішно")
        else:
            print(f"⚠️  Деякі помилки залишились: {result.stdout}")

        # Запускаємо форматування
        print("🎨 Форматування коду...")
        subprocess.run(["ruff", "format", "."], check=True)

        # Показуємо статистику залишкових помилок
        print("\n📊 Аналіз залишкових помилок:")
        result = subprocess.run(
            ["ruff", "check", "--statistics"], capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка виконання ruff: {e}")
        return False
    except FileNotFoundError:
        print("❌ Ruff не встановлено. Встановіть: pip install ruff")
        return False

    return True


def fix_common_import_issues():
    """Додає часто використовувані імпорти у файли, де вони відсутні"""

    common_fixes = {
        "from typing import Any": ["Any"],
        "from typing import Dict": ["Dict"],
        "from typing import List": ["List"],
        "from typing import Optional": ["Optional"],
        "import json": ["json"],
        "import time": ["time"],
        "from datetime import timedelta": ["timedelta"],
    }

    print("📦 Додавання часто відсутніх імпортів...")

    # Знаходимо всі Python файли
    py_files = list(Path(".").rglob("*.py"))

    for py_file in py_files:
        if "backup_" in str(py_file) or ".git" in str(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            modified = False
            for import_line, needed_names in common_fixes.items():
                for name in needed_names:
                    # Перевіряємо, чи є недефінована змінна і немає імпорту
                    if (
                        f"name `{name}`"
                        in subprocess.run(
                            ["ruff", "check", "--select=F821", str(py_file)],
                            capture_output=True,
                            text=True,
                        ).stdout
                        and import_line not in content
                    ):
                        # Знаходимо місце для додавання імпорту
                        lines = content.split("\n")
                        insert_idx = 0

                        # Знаходимо останній імпорт
                        for i, line in enumerate(lines):
                            if line.strip().startswith(("import ", "from ")):
                                insert_idx = i + 1

                        # Додаємо імпорт
                        lines.insert(insert_idx, import_line)
                        content = "\n".join(lines)
                        modified = True
                        print(f"  ✓ Додано {import_line} у {py_file}")

            if modified:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"  ⚠️  Помилка обробки {py_file}: {e}")


def main():
    print("🚀 Atlas Auto-Fixer - Швидке виправлення помилок")
    print("=" * 50)

    # Перевіряємо, чи ми в правильній директорії
    if not Path("pyproject.toml").exists():
        print("❌ Запустіть скрипт з кореневої директорії проєкту Atlas")
        sys.exit(1)

    # 1. Спочатку автоматичні виправлення Ruff
    if not run_ruff_fixes():
        print("❌ Не вдалося запустити Ruff")
        sys.exit(1)

    # 2. Додаємо відсутні імпорти
    fix_common_import_issues()

    # 3. Повторний запуск Ruff після додавання імпортів
    print("\n🔄 Повторний запуск Ruff після додавання імпортів...")
    run_ruff_fixes()

    print("\n🎉 Автоматичне виправлення завершено!")
    print("💡 Для залишкових помилок використовуйте AI асистента Continue у VS Code")


if __name__ == "__main__":
    main()
