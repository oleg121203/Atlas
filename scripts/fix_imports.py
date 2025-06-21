#!/usr/bin/env python3
"""Fix all imports from logger to utils.logger and config_manager to utils.config_manager"""

import re
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        #Fix logger imports
        content = re.sub(r"^from logger import (.+)$", r"from utils.logger import \1", content, flags=re.MULTILINE)
        content = re.sub(r"^import logger$", r"import utils.logger as logger", content, flags=re.MULTILINE)

        #Fix config_manager imports
        content = re.sub(r"^from config_manager import (.+)$", r"from utils.config_manager import \1", content, flags=re.MULTILINE)
        content = re.sub(r"^import config_manager$", r"import utils.config_manager as config_manager", content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files"""
    root_dir = Path()

    #Directories to process
    dirs_to_process = [
        "agents",
        "tools",
        "ui",
        "monitoring",
        "plugins",
        "scripts",
        "tests",
        "dev-tools",
    ]

    #Also process root level files
    for py_file in root_dir.glob("*.py"):
        if py_file.name != "fix_imports.py":  #Skip this script
            fix_imports_in_file(py_file)

    #Process directories
    for dir_name in dirs_to_process:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                fix_imports_in_file(py_file)

    print("Import fixing completed!")

if __name__ == "__main__":
    main()
