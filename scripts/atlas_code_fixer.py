#!/usr/bin/env python3
"""
Atlas Code Fixer - Інтегрований скрипт для автоматизації виправлення коду
Поєднує функціонал попередніх скриптів та додає нові можливості

Виправляє:
- F821: Невизначені імена (відсутні імпорти)
- SIM102: Вкладені if-оператори
- SIM117: Вкладені with-оператори
- B904: Raise exceptions from err
- E402: Імпорти не на початку файлу
- F401: Невикористані імпорти
- F811: Повторне визначення
- SIM105: Try-except-pass (заміна на contextlib.suppress)
- E722: Голі except (додавання Exception)
"""

import logging

# Налаштування логування
import os  # Додаємо в початок файлу
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

DEBUG_MODE = os.environ.get("DEBUG", "0") == "1"
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("AtlasCodeFixer")

# Вивід деталізованої інформації у режимі відлагодження
if DEBUG_MODE:
    logger.debug("🔍 Запущено в режимі відлагодження")

# Мапа імпортів для виправлення F821
IMPORTS_MAP = {
    # Типи з typing
    "Any": "from typing import Any",
    "Dict": "from typing import Dict",
    "List": "from typing import List",
    "Optional": "from typing import Optional",
    "Tuple": "from typing import Tuple",
    "Union": "from typing import Union",
    "Callable": "from typing import Callable",
    "Type": "from typing import Type",
    "Set": "from typing import Set",
    "Iterable": "from typing import Iterable",
    # PySide6 компоненти
    "QWidget": "from PySide6.QtWidgets import QWidget",
    "QAction": "from PySide6.QtWidgets import QAction",
    "QMenu": "from PySide6.QtWidgets import QMenu",
    "QTabBar": "from PySide6.QtWidgets import QTabBar",
    "QListWidgetItem": "from PySide6.QtWidgets import QListWidgetItem",
    "Qt": "from PySide6.QtCore import Qt",
    "QObject": "from PySide6.QtCore import QObject",
    "QRunnable": "from PySide6.QtCore import QRunnable",
    "QSize": "from PySide6.QtCore import QSize",
    "QThreadPool": "from PySide6.QtCore import QThreadPool",
    "Signal": "from PySide6.QtCore import Signal",
    "Slot": "from PySide6.QtCore import Slot",
    "QColor": "from PySide6.QtGui import QColor",
    "QFont": "from PySide6.QtGui import QFont",
    "QIcon": "from PySide6.QtGui import QIcon",
    "QTextCharFormat": "from PySide6.QtGui import QTextCharFormat",
    "QApplication": "from PySide6.QtWidgets import QApplication",
    "QCheckBox": "from PySide6.QtWidgets import QCheckBox",
    "QComboBox": "from PySide6.QtWidgets import QComboBox",
    "QFrame": "from PySide6.QtWidgets import QFrame",
    "QListWidget": "from PySide6.QtWidgets import QListWidget",
    "QMenuBar": "from PySide6.QtWidgets import QMenuBar",
    "QStatusBar": "from PySide6.QtWidgets import QStatusBar",
    # Selenium компоненти
    "WebDriverWait": "from selenium.webdriver.support.wait import WebDriverWait",
    "EC": "from selenium.webdriver.support import expected_conditions as EC",
    "By": "from selenium.webdriver.common.by import By",
    # Стандартні модулі
    "time": "import time",
    "json": "import json",
    "datetime": "import datetime",
    "timedelta": "from datetime import timedelta",
    "sys": "import sys",
    "os": "import os",
    "re": "import re",
    "subprocess": "import subprocess",
    "contextlib": "import contextlib",
    "pathlib": "import pathlib",
    # Проєктні компоненти
    "LLMManager": "from core.llm_manager import LLMManager",
    "TokenUsage": "from core.token_usage import TokenUsage",
    "ChatWidget": "from ui.chat.chat_widget import ChatWidget",
    "TaskWidget": "from ui.tasks.task_widget import TaskWidget",
    "SettingsWidget": "from ui.settings.settings_widget import SettingsWidget",
    "PluginsWidget": "from ui.plugins.plugins_widget import PluginsWidget",
    "UserManagementWidget": "from ui.agents.user_management_widget import UserManagementWidget",
    "AIAssistantWidget": "from ui.chat.ai_assistant_widget import AIAssistantWidget",
    "get_logger": "from utils.logging_utils import get_logger",
    "EventBus": "from core.event_bus import EventBus",
    "PluginManager": "from ui.plugins.plugin_manager import PluginManager",
    # Спеціальні випадки
    "e": "Exception as e",  # Для випадків, коли 'e' використовується без визначення
}

# Патерни регулярних виразів для виправлення різних помилок
FIXES = {
    "SIM102": {  # Вкладені if statements
        "pattern": r"(\s+)if\s+(.*?):\s*\n(\s+)if\s+(.*?):\s*\n",
        "replacement": r"\1if \2 and \4:\n",
    },
    "SIM117": {  # Вкладені with statements
        "pattern": r"(\s+)with\s+(.*?):\s*\n(\s+)with\s+(.*?):\s*\n",
        "replacement": r"\1with \2, \4:\n",
    },
    "B904": {  # Raise from в except
        "pattern": r"(\s+)except\s+(.*?)\s+as\s+(\w+):\s*\n((?:\s+.*\n)*?)(\s+)raise\s+(.*?)(?:\s*\n)",
        "replacement": r"\1except \2 as \3:\n\4\5raise \6 from \3\n",
    },
    "SIM105": {  # contextlib.suppress
        "pattern": r"(\s+)try:\s*\n(\s+)(.*?)\s*\n\s+except\s+(.*?):\s*\n\s+pass\s*\n",
        "replacement": r"\1from contextlib import suppress\n\1with suppress(\4):\n\2\3\n",
    },
    "E722": {  # Голий except
        "pattern": r"(\s+)except:\s*\n",
        "replacement": r"\1except Exception:\n",
    },
    "B007": {  # Loop control variable not used
        "pattern": r"(\s+)for\s+(\w+)\s+in\s+(.*?):\s*\n\s+([^\n]*?)\s*\n",
        "replacement": lambda m: m.group(1)
        + "for _ in "
        + m.group(3)
        + ":\n"
        + m.group(1)
        + m.group(4)
        + "\n"
        if m.group(2) not in m.group(4)
        else m.group(0),
    },
    "B023": {  # Function definition does not bind loop variable
        "pattern": r"(\s+)for\s+(\w+)\s+in\s+(.*?):\s*\n((?:\s+.*\n)*?)(\s+)([^\n]*?lambda.*?\2.*?\n)",
        "replacement": r"\1for \2 in \3:\n\4\5\6",  # Потрібна додаткова логіка для виправлення в коді
    },
}


def fix_undefined_name(file_path: str, missing_name: str) -> bool:
    """Додає відсутній імпорт у файл для виправлення F821."""
    if missing_name not in IMPORTS_MAP:
        logger.info(
            f"[SKIP] Відсутнє визначення імпорту для {missing_name} у {file_path}"
        )
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Перевіряємо, чи імпорт вже існує
        import_line = IMPORTS_MAP[missing_name]

        # Спеціальна обробка для 'e', яка є змінною в except блоці
        if missing_name == "e" and "except" in content:
            # Регулярний вираз для пошуку except блоків без 'as e'
            pattern = r"except\s+\w+\s*:"
            replacement = "except Exception as e:"
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                logger.info(f"[FIXED] Додано 'as e' в except блоки у {file_path}")
                return True
            return False

        if import_line in content:
            logger.debug(f"[SKIP] Імпорт {import_line} вже існує у {file_path}")
            return True

        # Додаємо імпорт після останнього імпорту або на початок файлу
        import_section_end = 0
        for match in re.finditer(
            r"^(?:import|from)\s+.*?(?:\n|$)", content, re.MULTILINE
        ):
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

        logger.info(f"[FIXED] Додано імпорт {import_line} у {file_path}")
        return True
    except Exception as ex:
        logger.error(
            f"Помилка при додаванні імпорту {missing_name} у {file_path}: {ex}"
        )
        return False


def fix_pattern_issues(file_path: str, issue_code: str) -> bool:
    """Виправляє проблеми на основі патернів регулярних виразів."""
    if issue_code not in FIXES:
        logger.debug(
            f"[SKIP] Відсутнє визначення для виправлення {issue_code} у {file_path}"
        )
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        pattern = FIXES[issue_code]["pattern"]
        replacement = FIXES[issue_code]["replacement"]

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            logger.info(
                f"[FIXED] Застосовано {count} виправлень для {issue_code} у {file_path}"
            )
            return True

        logger.debug(
            f"[SKIP] Не знайдено відповідностей для {issue_code} у {file_path}"
        )
        return False
    except Exception as ex:
        logger.error(f"Помилка при виправленні {issue_code} у {file_path}: {ex}")
        return False


def fix_unused_imports(file_path: str) -> bool:
    """Видаляє невикористані імпорти (F401) з файлу."""
    try:
        # Запускаємо Ruff для виправлення невикористаних імпортів
        result = subprocess.run(
            ["ruff", "check", "--select=F401", "--fix", file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"[FIXED] Видалено невикористані імпорти у {file_path}")
            return True
        else:
            logger.debug(
                f"[SKIP] Не вдалося видалити невикористані імпорти у {file_path}: {result.stderr}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Помилка при видаленні невикористаних імпортів у {file_path}: {ex}"
        )
        return False


def fix_import_order(file_path: str) -> bool:
    """Виправляє порядок імпортів та переміщує імпорти на початок файлу (E402)."""
    try:
        # Запускаємо Ruff для виправлення порядку імпортів
        result = subprocess.run(
            ["ruff", "check", "--select=E402,I001", "--fix", file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"[FIXED] Виправлено порядок імпортів у {file_path}")
            return True
        else:
            logger.debug(
                f"[SKIP] Не вдалося виправити порядок імпортів у {file_path}: {result.stderr}"
            )
            return False
    except Exception as ex:
        logger.error(f"Помилка при виправленні порядку імпортів у {file_path}: {ex}")
        return False


def fix_redefinition(file_path: str) -> bool:
    """Виправляє повторне визначення змінних (F811)."""
    try:
        # Запускаємо Ruff для виправлення повторного визначення
        result = subprocess.run(
            ["ruff", "check", "--select=F811", "--fix", file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"[FIXED] Виправлено повторні визначення у {file_path}")
            return True
        else:
            logger.debug(
                f"[SKIP] Не вдалося виправити повторні визначення у {file_path}: {result.stderr}"
            )
            return False
    except Exception as ex:
        logger.error(f"Помилка при виправленні повторних визначень у {file_path}: {ex}")
        return False


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
                files.append(os.path.join(root, filename))

    logger.info(f"Знайдено {len(files)} Python файлів у проекті")
    return files


def process_ruff_errors() -> Tuple[int, List[str]]:
    """Обробляє помилки з виводу Ruff та застосовує виправлення."""
    fixes_applied = 0
    error_files = []

    try:
        # Запускаємо Ruff для отримання списку помилок
        ruff_cmd = [
            "ruff",
            "check",
            "--select=F821,F401,F811,E402,SIM102,SIM105,SIM117,B904,E722,B023,B007,B008",
            "--output-format=text",
            ".",
        ]

        logger.debug(f"Запуск команди: {' '.join(ruff_cmd)}")
        result = subprocess.run(ruff_cmd, capture_output=True, text=True)

        # Виводимо результат у режимі відлагодження
        if DEBUG_MODE:
            logger.debug(f"Код виходу Ruff: {result.returncode}")
            logger.debug(
                f"Вивід Ruff: {result.stdout[:500]}..."
                if len(result.stdout) > 500
                else f"{result.stdout}"
            )
            if result.stderr:
                logger.debug(f"Помилки Ruff: {result.stderr}")

        # Перевіряємо результат виконання
        if (
            result.stdout
        ):  # Змінюємо умову, щоб обробляти вивід навіть при нульовому коді виходу
            # Регулярний вираз для аналізу помилок Ruff
            pattern = r"(.*?):(\d+):\d+: ([A-Z0-9]{4,5}) (.*)"
            processed_files = set()

            # Додаємо лічильник для статистики
            error_count = 0

            for line in result.stdout.splitlines():
                error_count += 1
                match = re.search(pattern, line)
                if not match:
                    logger.debug(f"Не вдалося обробити рядок: {line}")
                    continue

                file_path, line_num, error_code, error_msg = match.groups()
                file_path = Path(file_path)

                if not file_path.exists():
                    logger.info(f"[SKIP] Файл не знайдено: {file_path}")
                    continue

                # Додаємо файл до списку файлів з помилками
                error_files.append(str(file_path))

                # Обробка за типом помилки
                if error_code == "F821":  # Невизначене ім'я
                    name_match = re.search(r"Undefined name `(.*?)`", error_msg)
                    if name_match:
                        missing_name = name_match.group(1)
                        if fix_undefined_name(str(file_path), missing_name):
                            fixes_applied += 1

                elif error_code in ["SIM102", "SIM117", "B904", "SIM105", "E722"]:
                    if fix_pattern_issues(str(file_path), error_code):
                        fixes_applied += 1

                # Обробляємо кожен файл лише раз для цих типів помилок
                if str(file_path) not in processed_files:
                    processed_files.add(str(file_path))

                    # Виправляємо F401, E402, F811
                    if error_code == "F401" and fix_unused_imports(str(file_path)):
                        fixes_applied += 1

                    if error_code == "E402" and fix_import_order(str(file_path)):
                        fixes_applied += 1

                    if error_code == "F811" and fix_redefinition(str(file_path)):
                        fixes_applied += 1

        # Якщо не знайдено помилок через командний рядок, шукаємо файли безпосередньо
        if not error_files:
            logger.info(
                "Не знайдено помилок через ruff check, шукаємо файли безпосередньо..."
            )
            python_files = find_python_files()

            # Обмежуємо кількість файлів для обробки
            sample_files = python_files[:30] if len(python_files) > 30 else python_files

            for file_path in sample_files:
                result = subprocess.run(
                    [
                        "ruff",
                        "check",
                        "--select=F821,F401,F811,E402,SIM102,SIM105,SIM117,B904,E722",
                        file_path,
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    file_fixes = fix_specific_file(file_path)
                    if file_fixes > 0:
                        fixes_applied += file_fixes
                        error_files.append(file_path)

        return fixes_applied, list(set(error_files))
    except Exception as ex:
        logger.error(f"Помилка при обробці помилок Ruff: {ex}")
        return fixes_applied, error_files


def format_with_ruff() -> bool:
    """Форматує код за допомогою Ruff."""
    try:
        logger.info("Форматування коду за допомогою Ruff...")
        result = subprocess.run(["ruff", "format", "."], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Код відформатовано успішно")
            return True
        else:
            logger.error(f"❌ Помилка форматування коду: {result.stderr}")
            return False
    except Exception as ex:
        logger.error(f"Помилка при форматуванні коду: {ex}")
        return False


def check_and_install_ruff() -> bool:
    """Перевіряє, чи встановлено Ruff, і встановлює його, якщо необхідно."""
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Ruff не встановлено. Встановлюю...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "ruff"], check=True)
            logger.info("✅ Ruff встановлено успішно")
            return True
        except subprocess.CalledProcessError as ex:
            logger.error(f"❌ Не вдалося встановити Ruff: {ex}")
            return False


def setup_pre_commit() -> bool:
    """Налаштовує pre-commit хуки для проекту."""
    try:
        # Перевіряємо, чи встановлено pre-commit
        try:
            subprocess.run(["pre-commit", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("pre-commit не встановлено. Встановлюю...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"], check=True
            )

        # Створюємо .pre-commit-config.yaml, якщо він не існує
        pre_commit_config = Path(".pre-commit-config.yaml")
        if not pre_commit_config.exists():
            logger.info("Створюю .pre-commit-config.yaml...")
            pre_commit_content = """repos:
-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.5
    hooks:
    -   id: ruff
        args: [--fix, --unsafe-fixes]
    -   id: ruff-format
"""
            with open(pre_commit_config, "w", encoding="utf-8") as f:
                f.write(pre_commit_content)

        # Встановлюємо хуки
        logger.info("Встановлюю pre-commit хуки...")
        subprocess.run(["pre-commit", "install"], check=True)
        logger.info("✅ pre-commit хуки встановлено")
        return True
    except Exception as ex:
        logger.error(f"❌ Помилка встановлення pre-commit: {ex}")
        return False


def print_summary(fixes_applied: int, processed_files: List[str]) -> None:
    """Виводить підсумок виконаних виправлень."""
    logger.info("\n" + "=" * 50)
    logger.info(f"✅ Застосовано автоматичних виправлень: {fixes_applied}")
    logger.info(f"📝 Оброблено файлів: {len(processed_files)}")

    if processed_files:
        logger.info("\nОброблені файли:")
        for file in processed_files[:10]:  # Показуємо перші 10 файлів
            logger.info(f" - {file}")

        if len(processed_files) > 10:
            logger.info(f" ... і ще {len(processed_files) - 10} файлів")

    logger.info("=" * 50)


def check_ruff_remaining_errors() -> bool:
    """Перевіряє наявність залишкових помилок після виправлення."""
    try:
        result = subprocess.run(
            ["ruff", "check", "--statistics"], capture_output=True, text=True
        )
        if result.stdout:
            logger.info("\n📊 Статистика залишкових помилок:")
            logger.info(result.stdout)
        return result.returncode == 0
    except Exception as ex:
        logger.error(f"Помилка при перевірці залишкових помилок: {ex}")
        return False


def fix_specific_file(file_path: str) -> int:
    """Виправляє помилки у конкретному файлі."""
    logger.info(f"🔍 Виправлення помилок у файлі {file_path}...")
    fixes_applied = 0

    try:
        # Перевіряємо існування файлу
        if not Path(file_path).exists():
            logger.error(f"❌ Файл не знайдено: {file_path}")
            return 0

        # Перевіряємо, що це Python файл
        if not file_path.endswith(".py"):
            logger.error(f"❌ Файл не є Python файлом: {file_path}")
            return 0

        # Запускаємо Ruff для отримання списку помилок у файлі
        result = subprocess.run(
            [
                "ruff",
                "check",
                "--select=F821,F401,F811,E402,SIM102,SIM105,SIM117,B904,E722,B023,B007,B008",
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        # Читаємо вміст файлу для аналізу
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Перша перевірка - аналіз потенційних проблем з імпортом
            missing_imports = set()

            # Перевіряємо наявність відомих типів
            for name in IMPORTS_MAP:
                if (
                    re.search(r"\b" + name + r"\b", content)
                    and IMPORTS_MAP[name] not in content
                ):
                    missing_imports.add(name)

            # Додаємо відсутні імпорти
            for name in missing_imports:
                if fix_undefined_name(file_path, name):
                    fixes_applied += 1
        except Exception as read_ex:
            logger.error(f"Помилка при читанні файлу {file_path}: {read_ex}")

        if result.stdout:
            if DEBUG_MODE:
                logger.debug(f"Знайдені помилки у {file_path}:\n{result.stdout}")
            else:
                logger.info(f"Знайдені помилки у {file_path}")

            # Спочатку виправляємо порядок імпортів та невикористані імпорти
            if fix_import_order(file_path):
                fixes_applied += 1

            if fix_unused_imports(file_path):
                fixes_applied += 1

            if fix_redefinition(file_path):
                fixes_applied += 1

            # Шукаємо типові шаблони помилок
            for pattern_code in ["SIM102", "SIM117", "B904", "SIM105", "E722"]:
                if fix_pattern_issues(file_path, pattern_code):
                    fixes_applied += 1

            # Шукаємо невизначені імена
            name_pattern = r"F821 Undefined name `(.*?)`"
            for line in result.stdout.splitlines():
                name_match = re.search(name_pattern, line)
                if name_match:
                    missing_name = name_match.group(1)
                    if fix_undefined_name(file_path, missing_name):
                        fixes_applied += 1

            # Застосовуємо ruff format для файлу
            subprocess.run(["ruff", "format", file_path], capture_output=True)

            if fixes_applied > 0:
                logger.info(
                    f"✅ Застосовано {fixes_applied} виправлень у файлі {file_path}"
                )
            return fixes_applied
        else:
            # Спробуємо застосувати деякі загальні виправлення навіть без знайдених помилок
            for pattern_code in ["SIM102", "SIM117"]:
                if fix_pattern_issues(file_path, pattern_code):
                    fixes_applied += 1

            if fixes_applied == 0:
                logger.debug(f"✅ Файл {file_path} не містить відомих помилок")
            return fixes_applied

    except Exception as ex:
        logger.error(f"Помилка при виправленні файлу {file_path}: {ex}")
        return 0


def process_files_batch(file_paths, batch_size=10):
    """Обробляє файли порціями для кращої продуктивності."""
    total_fixes = 0
    processed = []

    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i : i + batch_size]
        logger.info(
            f"Обробка порції файлів {i + 1}-{i + len(batch)} з {len(file_paths)}..."
        )

        for file_path in batch:
            fixes = fix_specific_file(file_path)
            if fixes > 0:
                total_fixes += fixes
                processed.append(file_path)

    return total_fixes, processed


def main() -> None:
    """Головна функція скрипту."""
    logger.info("🚀 Atlas Code Fixer - виправлення автоматичних помилок")
    logger.info("=" * 50)

    # Перевіряємо, чи ми в правильній директорії
    if not Path("pyproject.toml").exists():
        logger.error("❌ Запустіть скрипт з кореневої директорії проєкту Atlas")
        sys.exit(1)

    # Перевіряємо та встановлюємо Ruff
    if not check_and_install_ruff():
        logger.error("❌ Не вдалося встановити необхідні інструменти")
        sys.exit(1)

    # Перевіряємо, чи передано аргумент з ім'ям файлу
    specific_file = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        specific_file = sys.argv[1]
        if not Path(specific_file).exists():
            logger.error(f"❌ Файл не знайдено: {specific_file}")
            sys.exit(1)

    fixes_applied = 0
    processed_files = []

    # Форматування коду
    format_with_ruff()

    # Налаштування pre-commit хуків
    setup_pre_commit()

    if specific_file:
        # Виправляємо конкретний файл
        fixes_applied = fix_specific_file(specific_file)
        if fixes_applied > 0:
            processed_files = [specific_file]
    else:
        # 1. Обробляємо помилки Ruff по всьому проекту
        logger.info("🔍 Виявлення та виправлення помилок Ruff...")
        fixes_applied, processed_files = process_ruff_errors()

        # Якщо стандартний підхід не знайшов помилок, спробуємо прямий обхід файлів
        if fixes_applied == 0:
            logger.info(
                "Стандартний підхід не знайшов помилок. Спробуємо прямий обхід файлів..."
            )

            # Знаходимо всі Python файли
            python_files = find_python_files()

            # Встановлюємо ліміт на кількість оброблюваних файлів
            max_files = 50
            sample_files = (
                python_files[:max_files]
                if len(python_files) > max_files
                else python_files
            )

            # Обробляємо файли порціями
            batch_fixes, batch_processed = process_files_batch(sample_files)
            fixes_applied += batch_fixes
            processed_files.extend(batch_processed)

        # 4. Повторна перевірка для застосування всіх виправлень
        if fixes_applied > 0:
            logger.info("\n🔄 Повторна перевірка та виправлення...")
            additional_fixes, additional_files = process_ruff_errors()
            fixes_applied += additional_fixes
            processed_files.extend(additional_files)
            processed_files = list(set(processed_files))  # Видаляємо дублікати

    # 5. Перевірка залишкових помилок
    check_ruff_remaining_errors()

    # 6. Виводимо підсумок
    print_summary(fixes_applied, processed_files)

    # 7. Поради для залишкових помилок
    logger.info("\n💡 Поради:")
    logger.info(
        " - Використовуйте VS Code з Continue AI для виправлення складніших помилок"
    )
    logger.info(" - Запустіть 'ruff check .' для переліку залишкових помилок")
    logger.info(
        " - Для виправлення конкретного файлу: ./scripts/atlas_code_fixer.py шлях/до/файлу.py"
    )
    logger.info(" - Додайте нові шаблони виправлень у скрипт для автоматизації")


if __name__ == "__main__":
    main()
