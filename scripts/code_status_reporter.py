#!/usr/bin/env python3
"""
Atlas Code Status Reporter - Генерує звіт про стан коду проекту
Використовується для моніторингу прогресу у виправленні помилок коду
"""

import json
import logging
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("AtlasCodeReporter")

# Категорії помилок
ERROR_CATEGORIES = {
    "F": "Flake8 помилки",
    "E": "Стильові помилки",
    "W": "Попередження",
    "SIM": "Спрощення коду",
    "B": "Помилки контролю багів",
    "I": "Імпорти",
    "N": "Найменування",
    "C": "Складність",
    "D": "Документація",
    "PLR": "PyLint",
    "TRY": "Обробка винятків",
}

# Критичні типи помилок, які варто виправити першочергово
CRITICAL_ERRORS = ["F821", "B904", "E402", "F811", "SIM102", "SIM117"]


def run_ruff_check(select=None):
    """Виконання перевірки коду за допомогою Ruff."""
    cmd = ["ruff", "check", "--output-format=json"]

    if select:
        cmd.append(f"--select={select}")

    cmd.append(".")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            return []
    except Exception as ex:
        logger.error(f"Помилка при запуску Ruff: {ex}")
        return []


def categorize_errors(errors):
    """Категоризує помилки за типами та файлами."""
    error_types = Counter()
    errors_by_category = defaultdict(Counter)
    errors_by_file = defaultdict(Counter)
    critical_errors = Counter()

    for error in errors:
        error_code = error.get("code", "")
        filename = error.get("filename", "")

        error_types[error_code] += 1

        # Категоризуємо за префіксом коду
        category_prefix = "".join(c for c in error_code if not c.isdigit())
        category_name = ERROR_CATEGORIES.get(category_prefix, "Інше")
        errors_by_category[category_name][error_code] += 1

        # Рахуємо помилки по файлах
        errors_by_file[filename][error_code] += 1

        # Рахуємо критичні помилки
        if error_code in CRITICAL_ERRORS:
            critical_errors[error_code] += 1

    return {
        "error_types": error_types,
        "errors_by_category": errors_by_category,
        "errors_by_file": errors_by_file,
        "critical_errors": critical_errors,
    }


def generate_report(errors_data):
    """Генерує звіт із статистикою помилок."""

    if not errors_data.get("error_types"):
        logger.info("🎉 Помилок не знайдено! Код відповідає стандартам.")
        return

    error_types = errors_data["error_types"]
    errors_by_category = errors_data["errors_by_category"]
    errors_by_file = errors_data["errors_by_file"]
    critical_errors = errors_data["critical_errors"]

    total_errors = sum(error_types.values())

    report = []
    report.append(
        f"📊 ЗВІТ СТАНУ КОДУ ATLAS ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    )
    report.append("=" * 70)
    report.append(f"📈 Загальна кількість помилок: {total_errors}")

    # Критичні помилки
    if critical_errors:
        report.append("\n⚠️  КРИТИЧНІ ПОМИЛКИ, ЯКІ ПОТРІБНО ВИПРАВИТИ:")
        report.append("-" * 50)
        for code, count in critical_errors.most_common():
            report.append(f"  {code}: {count} випадків")

    # Помилки за категоріями
    report.append("\n📋 РОЗПОДІЛ ПОМИЛОК ЗА КАТЕГОРІЯМИ:")
    report.append("-" * 50)
    for category, codes in sorted(
        errors_by_category.items(), key=lambda x: sum(x[1].values()), reverse=True
    ):
        category_total = sum(codes.values())
        percentage = (category_total / total_errors) * 100
        report.append(f"  {category}: {category_total} помилок ({percentage:.1f}%)")

        # Деталі для кожної категорії (топ-5)
        for code, count in codes.most_common(5):
            report.append(f"    - {code}: {count} помилок")

        if len(codes) > 5:
            report.append(f"    - ... та ще {len(codes) - 5} типів")

    # Файли з найбільшою кількістю помилок (топ-10)
    report.append("\n📁 ФАЙЛИ З НАЙБІЛЬШОЮ КІЛЬКІСТЮ ПОМИЛОК:")
    report.append("-" * 50)
    for filename, codes in sorted(
        errors_by_file.items(), key=lambda x: sum(x[1].values()), reverse=True
    )[:10]:
        file_path = Path(filename)
        total_file_errors = sum(codes.values())
        report.append(f"  {file_path.name}: {total_file_errors} помилок")

        # Топ-3 типи помилок для цього файлу
        for code, count in codes.most_common(3):
            report.append(f"    - {code}: {count}")

    # Загальні рекомендації
    report.append("\n💡 РЕКОМЕНДАЦІЇ:")
    report.append("-" * 50)

    if critical_errors:
        report.append("  1. Усуньте критичні помилки першочергово:")
        for code in critical_errors:
            if code == "F821":
                report.append("     - F821: Додайте всі відсутні імпорти")
            elif code == "B904":
                report.append(
                    "     - B904: Використовуйте 'raise ... from err' в блоках except"
                )
            elif code == "SIM102" or code == "SIM117":
                report.append(
                    "     - SIM102/SIM117: Спростіть вкладені оператори if/with"
                )
            elif code == "E402":
                report.append("     - E402: Перемістіть всі імпорти на початок файлу")

    report.append("  2. Запустіть автоматичний фіксер для розв'язання типових проблем:")
    report.append("     python scripts/atlas_code_fixer.py")

    report.append("  3. Використовуйте pre-commit хуки для запобігання нових помилок:")
    report.append("     pre-commit install")

    # Зберігаємо звіт у файл
    report_path = Path("reports/code_quality_report.txt")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    logger.info(f"📄 Звіт збережено у {report_path}")

    # Виводимо звіт в консоль
    print("\n".join(report))


def save_errors_history(errors_data):
    """Зберігає історію помилок для відстеження прогресу."""
    history_path = Path("reports/errors_history.json")
    history_path.parent.mkdir(exist_ok=True)

    # Готуємо дані для зберігання
    error_counts = {
        "date": datetime.now().isoformat(),
        "total": sum(errors_data["error_types"].values()),
        "by_category": {
            category: sum(codes.values())
            for category, codes in errors_data["errors_by_category"].items()
        },
        "critical": sum(errors_data["critical_errors"].values()),
    }

    # Завантажуємо попередню історію
    history = []
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Не вдалося прочитати файл історії, створюємо новий")

    # Додаємо нові дані
    history.append(error_counts)

    # Зберігаємо оновлену історію
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    logger.info(f"📊 Історію помилок оновлено у {history_path}")


def main():
    """Головна функція."""
    logger.info("🔍 Запуск аналізу коду Atlas...")

    # Перевіряємо, чи ми в правильній директорії
    if not Path("pyproject.toml").exists():
        logger.error("❌ Запустіть скрипт з кореневої директорії проєкту Atlas")
        sys.exit(1)

    # Запускаємо перевірку Ruff
    logger.info("📊 Збираємо статистику помилок коду...")
    errors = run_ruff_check()

    # Аналізуємо помилки
    errors_data = categorize_errors(errors)

    # Генеруємо звіт
    generate_report(errors_data)

    # Зберігаємо історію
    save_errors_history(errors_data)

    logger.info("✅ Аналіз завершено!")


if __name__ == "__main__":
    main()
