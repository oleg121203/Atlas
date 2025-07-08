#!/usr/bin/env python3
"""
Atlas Documentation Updater

Автоматично оновлює документацію на основі змін в коді та структурі проєкту.
"""

import re
from datetime import datetime
from pathlib import Path


def update_changelog_stats():
    """Оновлює статистику в CHANGELOG.md"""
    project_root = Path.cwd()
    atlas_dir = project_root / "atlas"

    if not atlas_dir.exists():
        print("⚠️ Atlas directory not found")
        return

    # Підраховуємо статистику
    py_files = list(atlas_dir.rglob("*.py"))
    total_lines = 0

    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                total_lines += len(f.readlines())
        except (IOError, UnicodeDecodeError):
            continue

    stats = {
        "total_files": len(py_files),
        "total_lines": total_lines,
        "modules": len(
            [
                d
                for d in atlas_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
        ),
        "updated": datetime.now().strftime("%Y-%m-%d"),
    }

    print(
        f"📊 Atlas Statistics: {stats['total_files']} files, {stats['total_lines']} lines"
    )
    return stats


def update_dev_plan_stats():
    """Оновлює статистику в DEV_PLAN.md"""
    dev_plan_path = Path("DEV_PLAN.md")

    if not dev_plan_path.exists():
        print("⚠️ DEV_PLAN.md not found")
        return

    stats = update_changelog_stats()
    if not stats:
        return

    # Читаємо поточний вміст
    with open(dev_plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Оновлюємо статистику
    stats_pattern = r"(\*\*Статистика міграції:\*\*\n)(.*?)(\*\*Готовність до наступних фаз розвитку:\*\*)"

    new_stats = f"""**Статистика міграції:**
- {stats["total_files"]} файлів додано до git tracking
- {stats["total_lines"]:,}+ рядків коду у atlas/ пакеті
- 3,000+ автоматичних замін імпортів
- Повне покриття модулів: core, ui, agents, memory, tools, plugins, workflows, utils
- Останнє оновлення: {stats["updated"]}

"""

    updated_content = re.sub(
        stats_pattern, r"\1" + new_stats + r"\3", content, flags=re.DOTALL
    )

    if updated_content != content:
        with open(dev_plan_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("✅ DEV_PLAN.md statistics updated")
    else:
        print("ℹ️ DEV_PLAN.md statistics already up to date")


def generate_module_docs():
    """Генерує документацію для модулів atlas/"""
    atlas_dir = Path("atlas")
    docs_dir = Path("docs")

    if not atlas_dir.exists():
        print("⚠️ Atlas directory not found")
        return

    docs_dir.mkdir(exist_ok=True)

    # Генеруємо docs для кожного модуля
    for module_dir in atlas_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith("."):
            module_name = module_dir.name
            doc_file = docs_dir / f"{module_name}.md"

            # Базовий шаблон документації
            doc_content = f"""# Atlas.{module_name.title()} Module

## Overview

The `atlas.{module_name}` module provides...

## Components

"""

            # Додаємо інформацію про Python файли в модулі
            py_files = list(module_dir.rglob("*.py"))
            for py_file in py_files:
                if py_file.name != "__init__.py":
                    relative_path = py_file.relative_to(module_dir)
                    doc_content += f"- `{relative_path}`\n"

            doc_content += f"""
## Usage

```python
from atlas.{module_name} import ...
```

## API Reference

*Generated on {datetime.now().strftime("%Y-%m-%d")}*
"""

            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(doc_content)

    print("✅ Module documentation generated")


def main():
    """Головна функція оновлення документації"""
    print("📚 Updating Atlas documentation...")

    # Оновлюємо статистику
    update_dev_plan_stats()

    # Генеруємо документацію модулів
    generate_module_docs()

    print("✅ Documentation update completed")


if __name__ == "__main__":
    main()
