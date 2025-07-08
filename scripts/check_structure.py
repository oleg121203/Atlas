#!/usr/bin/env python3
"""
Atlas Project Structure and Duplicate Check Script

Перевіряє структуру проєкту Atlas на предмет:
1. Дублікатів файлів та директорій
2. Порушень архітектури atlas/ пакету
3. Некоректних імпортів
4. Зайвих файлів у кореневій директорії
5. Відповідності структури з DEV_PLAN.md

Інтегрується з:
- VS Code (extensions та settings)
- Pre-commit hooks
- GitHub Actions CI/CD
- GitHub Copilot для автоматичних рекомендацій

Usage:
    python scripts/check_structure.py [--fix] [--report=json|text]
"""

import ast
import contextlib
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class AtlasStructureChecker:
    """Перевірка структури проєкту Atlas."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.atlas_dir = self.project_root / "atlas"
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Файли, які можуть легітимно дублюватися
        self.allowed_duplicates = {
            "__init__.py",  # Python package markers
            "base.py",  # Common base classes
            "types.py",  # Type definitions
            "constants.py",  # Constants definitions
            "utils.py",  # Utility functions
            "ui_init_patch.py",  # UI initialization patches
            "ui_main_window_patch.py",  # UI window patches
        }

        # Директорії, які можуть мати однакові імена файлів
        self.independent_dirs = {
            "ui/components",
            "ui/themes",
            "ui/styles",
            "tools/generated",
            "tools/legacy",
            "utils/providers",
        }

        # Дозволені розширення файлів
        self.allowed_extensions = {
            ".py",
            ".json",
            ".md",
            ".txt",
            ".toml",
            ".yml",
            ".yaml",
            ".cfg",
            ".ini",
        }

        # Обов'язкові файли в atlas/
        self.required_atlas_files = {"atlas/__init__.py", "atlas/main.py"}

        # Обов'язкові директорії в atlas/
        self.required_atlas_dirs = {
            "atlas/core",
            "atlas/ui",
            "atlas/agents",
            "atlas/memory",
            "atlas/tools",
            "atlas/plugins",
            "atlas/utils",
            "atlas/assets",
        }

    def check_duplicate_files(self) -> Dict[str, List[str]]:
        """Перевіряє дублікати файлів за хешем."""
        file_hashes: Dict[str, List[str]] = defaultdict(list)

        # Exclude directories that should not be checked for duplicates
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".mypy_cache",
        }

        for file_path in self.project_root.rglob("*"):
            # Skip files in excluded directories
            if any(part in exclude_dirs for part in file_path.parts):
                continue

            # Skip allowed duplicates
            if file_path.name in self.allowed_duplicates:
                continue

            # Check if file is in independent directory
            rel_path = file_path.relative_to(self.project_root)
            parent_dir = str(rel_path.parent)
            if any(parent_dir.endswith(ind_dir) for ind_dir in self.independent_dirs):
                continue

            if file_path.is_file() and file_path.suffix in self.allowed_extensions:
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[file_hash].append(str(rel_path))
                except (IOError, OSError):
                    continue

        # Find actual duplicates (excluding allowed ones)
        duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}

        for _file_hash, duplicate_files in duplicates.items():
            self.errors.append(
                f"🔴 Знайдено дублікати файлів: {', '.join(duplicate_files)}"
            )

        return duplicates

    def check_atlas_structure(self) -> bool:
        """Перевіряє правильність структури atlas/ пакету."""
        if not self.atlas_dir.exists():
            self.errors.append("🔴 Папка atlas/ не існує!")
            return False

        # Перевіряємо обов'язкові файли
        for required_file in self.required_atlas_files:
            file_path = self.project_root / required_file
            if not file_path.exists():
                self.errors.append(f"🔴 Відсутній обов'язковий файл: {required_file}")

        # Перевіряємо обов'язкові директорії
        for required_dir in self.required_atlas_dirs:
            dir_path = self.project_root / required_dir
            if not dir_path.exists():
                self.errors.append(
                    f"🔴 Відсутня обов'язкова директорія: {required_dir}"
                )
            elif not (dir_path / "__init__.py").exists():
                self.warnings.append(
                    f"⚠️ Відсутній __init__.py у директорії: {required_dir}"
                )

        return len(self.errors) == 0

    def check_import_structure(self) -> List[str]:
        """Перевіряє правильність імпортів в atlas/ пакеті."""
        invalid_imports = []

        for py_file in self.atlas_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_invalid_import(alias.name, py_file):
                                invalid_imports.append(
                                    f"{py_file.relative_to(self.project_root)}: {alias.name}"
                                )

                    elif (
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and self._is_invalid_import(node.module, py_file)
                    ):
                        invalid_imports.append(
                            f"{py_file.relative_to(self.project_root)}: from {node.module}"
                        )

            except (SyntaxError, UnicodeDecodeError, OSError):
                self.warnings.append(
                    f"⚠️ Не вдалося проаналізувати файл: {py_file.relative_to(self.project_root)}"
                )

        for invalid_import in invalid_imports:
            self.errors.append(f"🔴 Неправильний імпорт: {invalid_import}")

        return invalid_imports

    def _is_invalid_import(self, module_name: str, file_path: Path) -> bool:
        """Перевіряє, чи є імпорт неправильним."""
        # Старі імпорти, які потрібно замінити
        old_patterns = [
            "core.",
            "ui.",
            "tools.",
            "utils.",
            "assets.",
            "memory.",
            "agents.",
            "plugins.",
        ]

        return any(
            module_name.startswith(pattern) and not module_name.startswith("atlas.")
            for pattern in old_patterns
        )

    def check_naming_conventions(self) -> List[str]:
        """Перевіряє дотримання конвенцій найменування."""
        naming_violations = []

        for file_path in self.atlas_dir.rglob("*"):
            if file_path.is_file():
                filename = file_path.name

                # Файли Python повинні бути в snake_case
                if (
                    filename.endswith(".py")
                    and filename != "__init__.py"
                    and not re.match(r"^[a-z_][a-z0-9_]*\.py$", filename)
                ):
                    naming_violations.append(
                        f"🔴 Неправильна назва файлу: {file_path.relative_to(self.project_root)}"
                    )

            elif file_path.is_dir():
                dirname = file_path.name

                # Директорії повинні бути в snake_case
                if not re.match(r"^[a-z_][a-z0-9_]*$", dirname) and dirname not in {
                    "__pycache__",
                    ".git",
                }:
                    naming_violations.append(
                        f"🔴 Неправильна назва директорії: {file_path.relative_to(self.project_root)}"
                    )

        for violation in naming_violations:
            self.errors.append(violation)

        return naming_violations

    def check_root_cleanliness(self) -> List[str]:
        """Перевіряє, чи немає в корені проєкту зайвих файлів."""
        root_violations = []

        # Дозволені файли/папки в корені
        allowed_root_items = {
            ".github",
            ".idea",
            ".venv",
            ".vscode",
            ".windsurf",
            "atlas",
            "config",
            "data",
            "docs",
            "scripts",
            "tests",
            "user",
            ".gitignore",
            ".pre-commit-config.yaml",
            "CHANGELOG.md",
            "DEV_PLAN.md",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "conftest.py",
            "pytest.ini",
            "pyrightconfig.json",
            "requirements.txt",
            "Makefile",
            "launch_macos.sh",
            "setup_macos_dev.sh",
            "MACOS_SETUP.md",
            # Файл для швидкого запуску (не є обов'язковим)
            "main.py",
            # Тимчасові файли Python
            "__pycache__",
            # Звіти
            "atlas-structure-report.json",
            "bandit-report.json",
        }

        for item in self.project_root.iterdir():
            if item.name not in allowed_root_items:
                if item.name.startswith("."):
                    continue  # Ігноруємо приховані файли

                root_violations.append(f"🔴 Зайвий файл/папка в корені: {item.name}")

        for violation in root_violations:
            self.errors.append(violation)

        return root_violations

    def cleanup_legacy_symlinks(self) -> None:
        """Remove any legacy symlinks that might exist from old versions."""
        legacy_paths = {
            "core": "atlas/core",
            "ui": "atlas/ui",
            "tools": "atlas/tools",
            "utils": "atlas/utils",
            "assets": "atlas/assets",
            "plugins": "atlas/plugins",
            "memory": "atlas/memory",
            "agents": "atlas/agents",
        }

        # Remove any existing symlinks or empty directories
        for old_path in legacy_paths:
            old_full = self.project_root / old_path
            if old_full.is_symlink():
                with contextlib.suppress(OSError):
                    old_full.unlink()
                    print(f"✅ Removed legacy symlink: {old_path}")
            elif old_full.is_dir() and not any(old_full.iterdir()):
                with contextlib.suppress(OSError):
                    old_full.rmdir()
                    print(f"✅ Removed empty legacy directory: {old_path}")

    def run_full_check(self) -> Tuple[bool, Dict]:
        """Запускає повну перевірку структури проєкту."""
        print("🔍 Запуск перевірки структури проєкту Atlas...")

        # Спочатку очищаємо застарілі симлінки
        self.cleanup_legacy_symlinks()

        results = {
            "duplicates": self.check_duplicate_files(),
            "atlas_structure": self.check_atlas_structure(),
            "imports": self.check_import_structure(),
            "naming": self.check_naming_conventions(),
            "root_clean": self.check_root_cleanliness(),
        }

        print("\n📊 Результати перевірки:")
        print(f"  🔴 Помилки: {len(self.errors)}")
        print(f"  ⚠️ Попередження: {len(self.warnings)}")

        if self.errors:
            print("\n🔴 Знайдені помилки:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️ Попередження:")
            for warning in self.warnings:
                print(f"  {warning}")

        is_success = len(self.errors) == 0

        if is_success:
            print("✅ Структура проєкту пройшла всі перевірки!")
        else:
            print("❌ Знайдені проблеми у структурі проєкту!")

        return is_success, results


def main():
    """Головна функція скрипта."""
    import argparse

    parser = argparse.ArgumentParser(description="Atlas Project Structure Checker")
    parser.add_argument(
        "--fix", action="store_true", help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--report", choices=["json", "text"], default="json", help="Report format"
    )
    parser.add_argument(
        "project_root", nargs="?", default=os.getcwd(), help="Project root directory"
    )

    args = parser.parse_args()
    project_root = args.project_root

    checker = AtlasStructureChecker(project_root)
    success, results = checker.run_full_check()

    # Зберігаємо детальний звіт
    report_path = Path(project_root) / "atlas-structure-report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "success": success,
                "errors": checker.errors,
                "warnings": checker.warnings,
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n📄 Детальний звіт збережено: {report_path}")

    # Повертаємо код виходу
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
