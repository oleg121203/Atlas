#!/usr/bin/env python3
"""
Автоматизація виправлення помилок Ruff у проєкті Atlas.
Скрипт додає відсутні імпорти та виправляє найчастіші типи помилок.
"""

import re
from pathlib import Path

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
}

FIXES = {
    "SIM102": {  # Nested if statements
        "pattern": r"(\s+)if\s+(.*?):\s*\n\s+if\s+(.*?):\s*\n",
        "replacement": r"\1if \2 and \3:\n",
    },
    "SIM117": {  # Nested with statements
        "pattern": r"(\s+)with\s+(.*?):\s*\n\s+with\s+(.*?):\s*\n",
        "replacement": r"\1with \2, \3:\n",
    },
    "B904": {  # Raise from in except
        "pattern": r"(\s+)except\s+(.*?)\s+as\s+(\w+):\s*\n((?:\s+.*\n)*?)(\s+)raise\s+(.*?)(?:\s*\n)",
        "replacement": r"\1except \2 as \3:\n\4\5raise \6 from \3\n",
    },
    "SIM105": {  # contextlib.suppress
        "pattern": r"(\s+)try:\s*\n\s+.*?\s*\n\s+except\s+(.*?):\s*\n\s+pass\s*\n",
        "replacement": r"\1from contextlib import suppress\n\1with suppress(\2):\n\1    pass\n",
    },
}


def fix_undefined_name(file_path, missing_name):
    """Додає відсутній імпорт у файл."""
    if missing_name not in IMPORTS_MAP:
        print(f"[SKIP] No import definition for {missing_name} in {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Перевіряємо, чи імпорт вже існує
    import_line = IMPORTS_MAP[missing_name]
    if import_line in content:
        print(f"[SKIP] Import {import_line} already exists in {file_path}")
        return True

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

    print(f"[FIXED] Added import {import_line} to {file_path}")
    return True


def fix_pattern_issues(file_path, issue_code):
    """Виправляє проблеми на основі патернів."""
    if issue_code not in FIXES:
        print(f"[SKIP] No pattern fix for {issue_code} in {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    pattern = FIXES[issue_code]["pattern"]
    replacement = FIXES[issue_code]["replacement"]

    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"[FIXED] Applied {count} fixes for {issue_code} in {file_path}")
        return True

    print(f"[SKIP] No matches found for {issue_code} pattern in {file_path}")
    return False


def process_errors(ruff_output):
    """Обробляє помилки з виводу Ruff."""
    fixes_applied = 0

    # Регулярний вираз для аналізу помилок Ruff
    pattern = r"(.*?):(\d+):\d+: (F821|SIM102|SIM117|B904|SIM105) (.*)"

    for line in ruff_output.splitlines():
        match = re.search(pattern, line)
        if not match:
            continue

        file_path, line_num, error_code, error_msg = match.groups()
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"[SKIP] File not found: {file_path}")
            continue

        if error_code == "F821":  # Undefined name
            # Отримуємо ім'я невизначеної змінної
            name_match = re.search(r"Undefined name `(.*?)`", error_msg)
            if not name_match:
                print(f"[SKIP] Could not extract undefined name from: {error_msg}")
                continue

            missing_name = name_match.group(1)
            if fix_undefined_name(file_path, missing_name):
                fixes_applied += 1

        elif error_code in FIXES:
            if fix_pattern_issues(file_path, error_code):
                fixes_applied += 1

    return fixes_applied


def run_ruff_and_fix():
    """Запускає Ruff і виправляє знайдені помилки."""
    try:
        import subprocess

        # Запускаємо Ruff для отримання списку помилок
        result = subprocess.run(
            ["ruff", "check", "--select=F821,SIM102,SIM117,B904,SIM105", "."],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 and result.stdout:
            # Якщо є помилки, намагаємось їх виправити
            fixes = process_errors(result.stdout)
            print(f"\nApplied {fixes} automatic fixes")

            # Повторно запускаємо Ruff з автоматичними виправленнями
            subprocess.run(["ruff", "check", "--fix", "--unsafe-fixes", "."])
            print("\nRuff automatic fixes applied")
        else:
            print("No errors found or Ruff is not installed")

    except Exception as e:
        print(f"Error running Ruff: {e}")


if __name__ == "__main__":
    run_ruff_and_fix()
