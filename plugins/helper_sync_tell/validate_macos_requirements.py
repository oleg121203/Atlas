#!/usr/bin/env python3
"""
Валідація requirements-macos.txt для Atlas та Helper Sync Tell плагіна.
"""

import sys
from pathlib import Path


def validate_requirements():
    """Перевіряє чи всі пакети в requirements-macos.txt існують."""

    print("🔍 Валідація requirements-macos.txt")
    print("=" * 50)

    requirements_file = Path("/workspaces/Atlas/requirements-macos.txt")

    if not requirements_file.exists():
        print("❌ Файл requirements-macos.txt не знайдено!")
        return False

    #Читаємо файл та витягуємо пакети
    packages = []
    with open(requirements_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                #Витягуємо назву пакета (до першого = або >=)
                if "==" in line:
                    package = line.split("==")[0].strip()
                elif ">=" in line:
                    package = line.split(">=")[0].strip()
                elif line and not any(op in line for op in ["<", ">", "!", "~"]):
                    package = line.strip()
                else:
                    continue

                if package:
                    packages.append(package)

    print(f"📦 Знайдено {len(packages)} пакетів для перевірки")
    print()

    #Критичні пакети для Helper Sync Tell
    critical_packages = [
        "requests",
        "PyYAML",
        "openai",
        "google-generativeai",
        "pyobjc-core",
        "pyobjc-framework-Cocoa",
        "pyobjc-framework-Quartz",
    ]

    print("🎯 Перевірка критичних пакетів для Helper Sync Tell:")
    all_critical_present = True

    for critical in critical_packages:
        found = any(pkg.startswith(critical) for pkg in packages)
        if found:
            print(f"   ✅ {critical}")
        else:
            print(f"   ❌ {critical} - ВІДСУТНІЙ!")
            all_critical_present = False

    print()

    #Verification проблемних пакетів
    problematic_packages = [
        "pyobjc-framework-Foundation",  #Цей пакет не існує
    ]

    print("⚠️  Перевірка потенційно проблемних пакетів:")
    problems_found = False

    for problematic in problematic_packages:
        found = any(pkg.startswith(problematic) for pkg in packages)
        if found:
            print(f"   ❌ {problematic} - ПРОБЛЕМНИЙ ПАКЕТ (не існує)")
            problems_found = True
        else:
            print(f"   ✅ {problematic} - не знайдено (добре)")

    print()

    #Підсумок
    print("📊 ПІДСУМОК ВАЛІДАЦІЇ:")
    if all_critical_present and not problems_found:
        print("✅ Всі критичні пакети присутні")
        print("✅ Проблемних пакетів не знайдено")
        print("✅ requirements-macos.txt ГОТОВИЙ для використання")
        return True
    if not all_critical_present:
        print("❌ Відсутні критичні пакети")
    if problems_found:
        print("❌ Знайдено проблемні пакети")
    print("⚠️  requirements-macos.txt ПОТРЕБУЄ ВИПРАВЛЕННЯ")
    return False

def main():
    """Основна функція валідації."""
    print("🍎 Валідатор залежностей macOS для Atlas")
    print("Специальна перевірка для Helper Sync Tell плагіна")
    print()

    success = validate_requirements()

    if success:
        print("\n🎉 РЕЗУЛЬТАТ: requirements-macos.txt валідний!")
        print("Helper Sync Tell плагін може бути встановлений на macOS.")
        return 0
    print("\n⚠️  РЕЗУЛЬТАТ: Потрібні виправлення в requirements-macos.txt")
    return 1

if __name__ == "__main__":
    sys.exit(main())
