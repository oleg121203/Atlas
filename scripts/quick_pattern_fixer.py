#!/usr/bin/env python3
"""
Atlas Quick Pattern Fixer - автоматизоване виправлення типових шаблонів коду
Виправляє SIM102, SIM117, B904 та інші типові шаблонні помилки коду
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Патерни регулярних виразів для виправлення різних помилок
FIXES = {
    "SIM102": {  # Вкладені if statements
        "pattern": r"(\s+)if\s+(.*?):\s*\n\s+if\s+(.*?):\s*\n",
        "replacement": r"\1if \2 and \3:\n",
        "description": "Об'єднання вкладених if-операторів",
    },
    "SIM117": {  # Вкладені with statements
        "pattern": r"(\s+)with\s+(.*?):\s*\n\s+with\s+(.*?):\s*\n",
        "replacement": r"\1with \2, \3:\n",
        "description": "Об'єднання вкладених with-операторів",
    },
    "B904": {  # Raise from в except
        "pattern": r"(\s+)except\s+(.*?)\s+as\s+(\w+):\s*\n((?:\s+.*\n)*?)(\s+)raise\s+(.*?)(?:\s*\n)",
        "replacement": r"\1except \2 as \3:\n\4\5raise \6 from \3\n",
        "description": "Додавання from err до raise в except",
    },
    "SIM105": {  # contextlib.suppress
        "pattern": r"(\s+)try:\s*\n\s+(.*?)\s*\n\s+except\s+(.*?):\s*\n\s+pass\s*\n",
        "replacement": r"\1from contextlib import suppress\n\1with suppress(\3):\n\1    \2\n",
        "description": "Заміна try-except-pass на contextlib.suppress",
    },
    "E722": {  # Голий except
        "pattern": r"(\s+)except:\s*\n",
        "replacement": r"\1except Exception:\n",
        "description": "Заміна голого except на except Exception",
    },
}


def find_python_files():
    """Знаходить всі Python файли в проекті."""
    files = []
    for root, dirs, filenames in os.walk(".", topdown=True):
        # Пропускаємо директорії, які починаються на . або backup_
        dirs[:] = [
            d
            for d in dirs
            if not (d.startswith(".") or d.startswith("backup_") or d == "venv")
        ]
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                files.append(filepath)
    return files


def fix_pattern_in_file(file_path, error_code):
    """Виправляє патерн у файлі."""
    if error_code not in FIXES:
        return 0

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        pattern = FIXES[error_code]["pattern"]
        replacement = FIXES[error_code]["replacement"]
        description = FIXES[error_code]["description"]

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(
                f"[FIXED] {error_code} - {description} ({count} випадків) в {file_path}"
            )
            return count
        return 0
    except Exception as e:
        print(f"[ERROR] Помилка при виправленні {error_code} в {file_path}: {e}")
        return 0


def fix_all_patterns_in_file(file_path):
    """Виправляє всі шаблони в одному файлі."""
    total_fixes = 0
    for error_code in FIXES:
        total_fixes += fix_pattern_in_file(file_path, error_code)
    return total_fixes


def fix_all_pattern_issues():
    """Виправляє всі шаблонні помилки коду в проекті."""
    print("Аналіз помилок шаблонів у проекті за допомогою Ruff...")

    result = subprocess.run(
        [
            "ruff",
            "check",
            "--select=SIM102,SIM105,SIM117,B904,E722",
            "--format=text",
            ".",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    # ruff check повертає 1, якщо знаходить проблеми, що для нас не є помилкою.
    # Нас хвилюють лише справжні помилки виконання (код повернення > 1).
    if result.returncode > 1 and result.stderr:
        print(f"Помилка при запуску ruff: {result.stderr}")
        return

    output = result.stdout
    lines = output.strip().split("\n")

    if not lines or (len(lines) == 1 and not lines[0]):
        print("✅ Помилок шаблонів не знайдено.")
        return

    # Отримуємо унікальні існуючі шляхи до файлів з виводу
    files_to_fix = sorted(
        {
            line.split(":")[0]
            for line in lines
            if ":" in line and os.path.exists(line.split(":")[0])
        }
    )

    if not files_to_fix:
        print("✅ Помилок шаблонів не знайдено.")
        return

    print(
        f"Знайдено {len(files_to_fix)} файлів з помилками шаблонів. Починаємо виправлення..."
    )
    print("=" * 50)

    total_fixed_count = 0
    fixed_files_count = 0

    for i, file_path in enumerate(files_to_fix, 1):
        print(f"[{i}/{len(files_to_fix)}] Обробка файлу: {file_path}")
        fixes = fix_all_patterns_in_file(file_path)

        if fixes > 0:
            fixed_files_count += 1
            total_fixed_count += fixes

    print("\n" + "=" * 50)
    print(f"✅ Виправлено шаблонів коду: {total_fixed_count}")
    print(f"✅ В {fixed_files_count} файлах")


if __name__ == "__main__":
    # Перевіряємо, чи ми в правильній директорії
    if not Path("pyproject.toml").exists():
        print("❌ Запустіть скрипт з кореневої директорії проєкту Atlas")
        sys.exit(1)

    print("🚀 Atlas Quick Pattern Fixer")
    print("=" * 50)

    # Виправляємо всі шаблонні помилки
    fix_all_pattern_issues()
