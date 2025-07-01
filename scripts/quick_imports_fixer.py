#!/usr/bin/env python3
"""
Atlas Quick Imports Fixer - швидкий скрипт для виправлення помилок з імпортами
Фокусується на швидкому виправленні найчастіших проблем з імпортами в проекті
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Мапа імпортів для виправлення F821
IMPORTS_MAP = {
    "Any": "from typing import Any",
    "Dict": "from typing import Dict",
    "List": "from typing import List",
    "Optional": "from typing import Optional",
    "QWidget": "from PySide6.QtWidgets import QWidget",
    "QAction": "from PySide6.QtWidgets import QAction",
    "QMenu": "from PySide6.QtWidgets import QMenu",
    "QTabBar": "from PySide6.QtWidgets import QTabBar",
    "QListWidgetItem": "from PySide6.QtWidgets import QListWidgetItem",
    "Qt": "from PySide6.QtCore import Qt",
    "WebDriverWait": "from selenium.webdriver.support.wait import WebDriverWait",
    "EC": "from selenium.webdriver.support import expected_conditions as EC",
    "By": "from selenium.webdriver.common.by import By",
    "time": "import time",
    "json": "import json",
    "timedelta": "from datetime import timedelta",
    "LLMManager": "from core.llm_manager import LLMManager",
    "TokenUsage": "from core.token_usage import TokenUsage",
    "ChatWidget": "from ui.chat.chat_widget import ChatWidget",
    "TaskWidget": "from ui.tasks.task_widget import TaskWidget",
    "SettingsWidget": "from ui.settings.settings_widget import SettingsWidget",
    "PluginsWidget": "from ui.plugins.plugins_widget import PluginsWidget",
    "UserManagementWidget": "from ui.agents.user_management_widget import UserManagementWidget",
    "AIAssistantWidget": "from ui.chat.ai_assistant_widget import AIAssistantWidget",
    "get_logger": "from utils.logging_utils import get_logger",
    "e": "Exception as e",  # Для випадків, коли 'e' використовується без визначення
    "PluginManager": "from ui.plugins.plugin_manager import PluginManager",
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


def add_missing_import(file_path, missing_name):
    """Додає відсутній імпорт у файл."""
    if missing_name not in IMPORTS_MAP:
        print(f"[SKIP] Немає визначення для {missing_name} в {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Перевіряємо, чи імпорт вже існує
    import_line = IMPORTS_MAP[missing_name]
    if import_line in content:
        return False

    # Додаємо імпорт після останнього імпорту або на початок файлу
    import_section_end = 0
    for match in re.finditer(r"^(?:import|from)\s+.*?(?:\n|$)", content, re.MULTILINE):
        end = match.end()
        if end > import_section_end:
            import_section_end = end

    if import_section_end > 0:
        new_content = (
            content[:import_section_end]
            + "\n"
            + import_line
            + "\n"
            + content[import_section_end:]
        )
    else:
        new_content = import_line + "\n\n" + content

    # Зберігаємо файл
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)

    print(f"[FIXED] Додано імпорт {import_line} в {file_path}")
    return True


def fix_file_undefined_imports(file_path):
    """Виправляє невизначені імпорти у файлі."""
    try:
        # Запускаємо Ruff для пошуку невизначених імен
        result = subprocess.run(
            ["ruff", "check", "--select=F821", file_path],
            capture_output=True,
            text=True,
        )

        if not result.stdout:
            return 0

        fixes_applied = 0
        # Регулярний вираз для пошуку невизначених змінних
        pattern = r"F821 Undefined name `(.*?)`"
        for match in re.finditer(pattern, result.stdout):
            missing_name = match.group(1)
            if add_missing_import(file_path, missing_name):
                fixes_applied += 1

        return fixes_applied
    except Exception as e:
        print(f"[ERROR] Помилка при обробці {file_path}: {e}")
        return 0


def fix_file_unused_imports(file_path):
    """Видаляє невикористані імпорти з файлу."""
    try:
        before_fix = get_file_error_count(file_path, "F401")
        if before_fix == 0:
            return 0

        # Виправляємо невикористані імпорти
        subprocess.run(
            ["ruff", "check", "--select=F401", "--fix", file_path], capture_output=True
        )

        # Перевіряємо, скільки помилок залишилось
        after_fix = get_file_error_count(file_path, "F401")
        fixes_applied = before_fix - after_fix

        if fixes_applied > 0:
            print(
                f"[FIXED] Видалено {fixes_applied} невикористаних імпортів у {file_path}"
            )

        return fixes_applied
    except Exception as e:
        print(f"[ERROR] Помилка при обробці невикористаних імпортів у {file_path}: {e}")
        return 0


def fix_file_import_order(file_path):
    """Виправляє порядок імпортів у файлі."""
    try:
        before_fix = get_file_error_count(file_path, "E402")
        if before_fix == 0:
            return 0

        # Виправляємо порядок імпортів
        subprocess.run(
            ["ruff", "check", "--select=E402,I001", "--fix", file_path],
            capture_output=True,
        )

        # Перевіряємо, скільки помилок залишилось
        after_fix = get_file_error_count(file_path, "E402")
        fixes_applied = before_fix - after_fix

        if fixes_applied > 0:
            print(f"[FIXED] Виправлено порядок {fixes_applied} імпортів у {file_path}")

        return fixes_applied
    except Exception as e:
        print(f"[ERROR] Помилка при виправленні порядку імпортів у {file_path}: {e}")
        return 0


def get_file_error_count(file_path, error_code):
    """Отримує кількість помилок певного типу у файлі."""
    try:
        result = subprocess.run(
            ["ruff", "check", f"--select={error_code}", file_path],
            capture_output=True,
            text=True,
        )

        # Рахуємо кількість рядків з помилками даного типу
        count = 0
        for line in result.stdout.splitlines():
            if f": {error_code} " in line:
                count += 1

        return count
    except Exception:
        return 0


def fix_all_import_issues():
    """Виправляє всі помилки з імпортами в проекті."""
    python_files = find_python_files()

    total_undefined = 0
    total_unused = 0
    total_order = 0

    print(f"Знайдено {len(python_files)} Python файлів")
    print("=" * 50)

    for i, file_path in enumerate(python_files, 1):
        print(f"[{i}/{len(python_files)}] Обробка файлу {file_path}...")

        # Виправляємо невизначені змінні
        undefined_fixed = fix_file_undefined_imports(file_path)
        total_undefined += undefined_fixed

        # Видаляємо невикористані імпорти
        unused_fixed = fix_file_unused_imports(file_path)
        total_unused += unused_fixed

        # Виправляємо порядок імпортів
        order_fixed = fix_file_import_order(file_path)
        total_order += order_fixed

    print("\n" + "=" * 50)
    print(f"✅ Додано відсутніх імпортів: {total_undefined}")
    print(f"✅ Видалено невикористаних імпортів: {total_unused}")
    print(f"✅ Виправлено порядок імпортів: {total_order}")
    print(f"✅ Всього виправлень: {total_undefined + total_unused + total_order}")


if __name__ == "__main__":
    # Перевіряємо, чи ми в правильній директорії
    if not Path("pyproject.toml").exists():
        print("❌ Запустіть скрипт з кореневої директорії проєкту Atlas")
        sys.exit(1)

    print("🚀 Atlas Quick Imports Fixer")
    print("=" * 50)

    # Виправляємо всі помилки з імпортами
    fix_all_import_issues()
