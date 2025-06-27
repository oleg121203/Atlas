#!/usr/bin/env python3
"""
Organize Mock Files Script for Atlas Project

This script specifically organizes mock files within the tests directory.
"""

import glob
import os
import re
import shutil
from pathlib import Path

# Root directory
ROOT_DIR = Path(__file__).resolve().parent.parent


def ensure_directory_exists(file_path):
    """Create directory if it doesn't exist."""
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        # Create __init__.py in the directory
        init_py = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_py):
            with open(init_py, "w") as f:
                f.write("# Auto-generated __init__.py\n")


def find_files_with_import(module_name):
    """Find all Python files that import the specified module."""
    files = []
    for root, _, filenames in os.walk(ROOT_DIR):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    # Look for imports of this module
                    if re.search(rf"(from|import)\s+{module_name}\b", content):
                        files.append(file_path)
                except UnicodeDecodeError:
                    print(f"Warning: Couldn't read {file_path} as text")

    return files


def fix_imports_in_file(file_path, old_module_name, new_module_prefix):
    """Fix imports in a file."""
    if not new_module_prefix:  # Skip non-Python files
        return

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for line in lines:
            # Handle 'from module import ...'
            from_import_match = re.match(
                rf"^from\s+{re.escape(old_module_name)}\s+import\s+(.*)", line
            )
            if from_import_match:
                new_line = f"from {new_module_prefix}.{old_module_name} import {from_import_match.group(1)}"
                new_lines.append(new_line)
                changed = True
                continue

            # Handle 'import module'
            direct_import_match = re.match(
                rf"^import\s+{re.escape(old_module_name)}(\s*$|\s+as\s+.*$)", line
            )
            if direct_import_match:
                # Preserve any 'as' alias
                as_match = re.search(r"as\s+(.*?)$", line)
                if as_match:
                    new_line = f"import {new_module_prefix}.{old_module_name} as {as_match.group(1)}"
                else:
                    new_line = f"import {new_module_prefix}.{old_module_name}"
                new_lines.append(new_line)
                changed = True
                continue

            # If no matches, keep the line as is
            new_lines.append(line)

        if changed:
            with open(file_path, "w") as f:
                f.writelines(new_lines)
                print(f"Fixed imports in {file_path}")

    except UnicodeDecodeError:
        print(f"Warning: Couldn't read {file_path} as text")
    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")


def organize_mock_files():
    """Find and organize mock files in tests directory into tests/mocks."""
    print("Organizing mock files in tests directory...")

    # Create mocks directory if it doesn't exist
    mocks_dir = os.path.join(ROOT_DIR, "tests", "mocks")
    if not os.path.exists(mocks_dir):
        os.makedirs(mocks_dir)
        with open(os.path.join(mocks_dir, "__init__.py"), "w") as f:
            f.write("# Auto-generated __init__.py\n")

    # Find all mock files in the tests directory
    mock_pattern = os.path.join(ROOT_DIR, "tests", "mock_*.py")
    mock_files = glob.glob(mock_pattern)

    for file_path in mock_files:
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            dst_path = os.path.join(mocks_dir, filename)

            # Find all files importing this mock
            module_name = os.path.splitext(filename)[0]
            import_files = find_files_with_import(module_name)
            print(f"Found {len(import_files)} files importing {module_name}")

            # Copy the file to the new location
            shutil.copy2(file_path, dst_path)
            print(f"Copied {file_path} to {dst_path}")

            # Fix imports in all affected files
            for import_file in import_files:
                if os.path.abspath(import_file) != os.path.abspath(dst_path):
                    fix_imports_in_file(import_file, module_name, "tests.mocks")
                    print(f"Fixed imports in {import_file}")

    # Ask user if they want to remove the original files
    try:
        confirm = input(
            "Mock files have been moved to tests/mocks/. Delete originals? (y/n): "
        )
        if confirm.lower() == "y":
            for file_path in mock_files:
                os.remove(file_path)
                print(f"Removed original file {file_path}")
    except Exception as e:
        print(f"Skipping file deletion. Original files remain. Error: {str(e)}")


if __name__ == "__main__":
    organize_mock_files()
    print("Mock files organization complete!")
