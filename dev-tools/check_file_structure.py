#!/usr/bin/env python3
"""
Утиліта для перевірки дотримання структури файлів Atlas

Ця утиліта перевіряє, чи дотримується правильна структура файлів
відповідно до інструкцій платформи.
"""

import sys
from pathlib import Path

# Правильна структура файлів Atlas
EXPECTED_STRUCTURE = {
    "dev-tools/": [
        "testing/",  # Тести та тестові утиліти
        "analysis/",  # Аналітичні інструменти
        "setup/",  # Інструменти налаштування
        "documentation/",  # Документація для розробників
    ],
    "docs/": [
        "reports/",  # Звіти про розробку та аналіз
        "macos/",  # macOS-специфічна документація
    ],
    "utils/": [
        "platform_utils.py",  # Кросплатформні утиліти
        "macos_utils.py",  # macOS-специфічні утиліти
        "linux_utils.py",  # Linux-специфічні утиліти
    ],
    "root": [
        "requirements-linux.txt",  # Залежності для Linux (Python 3.12)
        "requirements-macos.txt",  # Залежності для macOS (Python 3.13)
        "launch_macos.sh",  # Запуск для macOS
    ],
}


def check_file_structure(base_path: str = ".") -> bool:
    """
    Перевіряє структуру файлів Atlas

    Returns:
        bool: True якщо структура правильна
    """
    base = Path(base_path)
    issues = []

    print("🔍 Перевірка структури файлів Atlas...")

    # Перевірка основних папок
    for folder, expected_items in EXPECTED_STRUCTURE.items():
        folder_path = base if folder == "root" else base / folder

        if not folder_path.exists():
            issues.append(f"❌ Відсутня папка: {folder_path}")
            continue

        print(f"✅ Папка існує: {folder_path}")

        # Перевірка вмісту папки
        for item in expected_items:
            item_path = folder_path / item
            if not item_path.exists():
                issues.append(f"⚠️ Відсутній елемент: {item_path}")
            else:
                print(f"  ✅ {item}")

    # Перевірка на файли не в тому місці
    wrong_place_files = [
        ("test_integration.py", "корінь", "dev-tools/testing/"),
        ("INTEGRATION_REPORT.md", "корінь", "docs/reports/"),
    ]

    for filename, wrong_location, correct_location in wrong_place_files:
        wrong_path = base / filename
        if wrong_path.exists():
            issues.append(
                f"🔄 Файл {filename} знаходиться в {wrong_location}, має бути в {correct_location}"
            )

    # Виведення результатів
    if issues:
        print("\n⚠️ Знайдені проблеми зі структурою:")
        for issue in issues:
            print(f"  {issue}")
        return False
    print("\n🎉 Структура файлів правильна!")
    return True


def suggest_fixes():
    """Пропонує виправлення для структури файлів"""
    print("\n🔧 Рекомендовані виправлення:")
    print("   mv test_integration.py dev-tools/testing/")
    print("   mv INTEGRATION_REPORT.md docs/reports/")
    print("   # Створити відсутні папки за потреби")


def main():
    """Основна функція"""
    print("📁 ПЕРЕВІРКА СТРУКТУРИ ФАЙЛІВ ATLAS")
    print("=" * 50)

    base_path = sys.argv[1] if len(sys.argv) > 1 else "."

    is_correct = check_file_structure(base_path)

    if not is_correct:
        suggest_fixes()
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
