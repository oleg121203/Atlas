#!/usr/bin/env python3
"""
File Organization Script for Atlas Project

This script reorganizes the project by moving files to appropriate directories
and fixing imports in those files and any files that reference them.
"""

import glob
import os
import re
import shutil
from pathlib import Path

# Root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# File mappings - (source, destination, module_prefix)
FILE_MAPPINGS = [
    # Collaboration module files
    ("collaboration.py", "collaboration/collaboration.py", "collaboration"),
    # User files
    ("user_satisfaction.py", "user/user_satisfaction.py", "user"),
    # Slack integration files
    (
        "slack_integration.py",
        "integration/slack/slack_integration.py",
        "integration.slack",
    ),
    # Team management files
    ("team_management.py", "team/team_management.py", "team"),
    # Analytics files
    (
        "workflow_analytics_20250626.csv",
        "analytics/data/workflow_analytics_20250626.csv",
        None,
    ),
    ("onboarding_analytics.json", "analytics/data/onboarding_analytics.json", None),
    # Test data
    ("test_partnership_export.json", "tests/data/test_partnership_export.json", None),
    # Marketplace files
    ("marketplace_patterns.json", "marketplace/data/marketplace_patterns.json", None),
]

# Test files to move to appropriate test directories
# Format: (glob_pattern, destination_dir, import_module_prefix)
TEST_FILES = [
    ("test_workflow_*.py", "tests/workflow", "workflow"),
    ("test_user_*.py", "tests/user", "user"),
    ("test_collaboration_*.py", "tests/collaboration", "collaboration"),
    ("test_analytics_*.py", "tests/analytics", "analytics"),
    ("test_integration_*.py", "tests/integration", "integration"),
    ("test_security_*.py", "tests/security", "security"),
    ("mock_*.py", "tests/mocks", None),  # Mock files should go to mocks directory
]

# Patterns to look for imports
IMPORT_PATTERNS = [
    # from module import class
    (r"from\s+(([\w_]+))\s+import\s+([\w_, ]+)", r"from \2.\1 import \3"),
    # import module
    (r"import\s+([\w_]+)", r"import \1.\1"),
]


def ensure_directory_exists(file_path):
    """Create directory if it doesn't exist."""
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        # Create __init__.py in each directory
        init_py = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_py):
            with open(init_py, "w") as f:
                f.write("# Auto-generated __init__.py\n")

        # Also create __init__.py in parent directories that are within our project only
        current_dir = dir_path
        project_root = str(ROOT_DIR)

        while True:
            parent_dir = os.path.dirname(current_dir)
            # Check if we're still within the project root
            if parent_dir in (current_dir, project_root) or not parent_dir.startswith(
                project_root
            ):
                break

            parent_init = os.path.join(parent_dir, "__init__.py")
            if not os.path.exists(parent_init):
                try:
                    with open(parent_init, "w") as f:
                        f.write("# Auto-generated __init__.py\n")
                except PermissionError:
                    print(
                        f"Warning: Permission denied creating {parent_init}, skipping."
                    )

            current_dir = parent_dir


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

            # Handle 'import module, another_module'
            comma_import_match = re.search(
                rf"^import\s+(.*?){re.escape(old_module_name)}(.*?)$", line
            )
            if comma_import_match:
                prefix = comma_import_match.group(1)
                suffix = comma_import_match.group(2)
                new_line = (
                    f"import {prefix}{new_module_prefix}.{old_module_name}{suffix}"
                )
                new_lines.append(new_line)
                changed = True
                continue

            # If no matches, keep the line as is
            new_lines.append(line)

        if changed:
            with open(file_path, "w") as f:
                f.writelines(new_lines)

    except UnicodeDecodeError:
        print(f"Warning: Couldn't read {file_path} as text")
    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")


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


def analyze_imports_in_file(file_path):
    """Analyze imports in a file and return a list of imported modules."""
    imported_modules = set()

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Find all from ... import ... statements
        from_imports = re.findall(r"from\s+([\w\.]+)\s+import", content)
        imported_modules.update(from_imports)

        # Find all import ... statements
        direct_imports = re.findall(r"import\s+([\w\.]+)", content)
        imported_modules.update(direct_imports)

    except UnicodeDecodeError:
        print(f"Warning: Couldn't read {file_path} as text")
    except Exception as e:
        print(f"Error analyzing imports in {file_path}: {e}")

    return list(imported_modules)


def fix_imports_in_moved_file(file_path):
    """Fix imports in a moved file to account for its new location."""
    # Get the directory of the file relative to the root
    file_dir = os.path.dirname(os.path.relpath(file_path, ROOT_DIR))
    if not file_dir:  # If file is in root directory
        return

    # Get the depth of the file (number of directory levels)
    depth = len(file_dir.split(os.sep))

    # Analyze imports
    imported_modules = analyze_imports_in_file(file_path)

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for line in lines:
            line_changed = False

            # Check if line contains any of the imported modules
            for module in imported_modules:
                # Skip imports that already have dots (already qualified)
                if "." in module:
                    continue

                # Check if we have this module in our project structure
                possible_module_paths = [
                    os.path.join(ROOT_DIR, module),
                    os.path.join(ROOT_DIR, module + ".py"),
                ]

                if any(os.path.exists(path) for path in possible_module_paths):
                    # This is likely a local module that needs to be adjusted

                    # Handle 'from module import ...'
                    if re.match(rf"^from\s+{re.escape(module)}\s+import", line):
                        # Calculate relative import prefix
                        rel_prefix = "." * depth
                        new_line = re.sub(
                            rf"^from\s+{re.escape(module)}\s+",
                            f"from {rel_prefix}{module} ",
                            line,
                        )
                        new_lines.append(new_line)
                        line_changed = True
                        changed = True
                        break

                    # Handle 'import module'
                    elif re.match(
                        rf"^import\s+{re.escape(module)}(\s*$|\s+as\s+.*$)", line
                    ):
                        # Calculate relative import prefix
                        rel_prefix = "." * depth
                        new_line = re.sub(
                            rf"^import\s+{re.escape(module)}",
                            f"import {rel_prefix}{module}",
                            line,
                        )
                        new_lines.append(new_line)
                        line_changed = True
                        changed = True
                        break

            # If no changes were made to this line, keep it as is
            if not line_changed:
                new_lines.append(line)

        if changed:
            with open(file_path, "w") as f:
                f.writelines(new_lines)
                print(f"Fixed imports in moved file {file_path}")

    except Exception as e:
        print(f"Error fixing imports in moved file {file_path}: {e}")


def move_file_and_fix_imports(src_path, dst_path, module_prefix):
    """Move a file and fix imports in related files."""
    src_path = os.path.join(ROOT_DIR, src_path)
    dst_path = os.path.join(ROOT_DIR, dst_path)

    if not os.path.exists(src_path):
        print(f"Warning: Source file {src_path} does not exist. Skipping.")
        return

    # Get the module name from the source filename
    module_name = os.path.splitext(os.path.basename(src_path))[0]

    # Find all files that import this module
    if module_prefix:  # Only fix imports for Python files
        import_files = find_files_with_import(module_name)
        print(f"Found {len(import_files)} files importing {module_name}")
    else:
        import_files = []

    # Create destination directory if needed
    ensure_directory_exists(dst_path)

    # Move the file
    shutil.copy2(src_path, dst_path)
    print(f"Copied {src_path} to {dst_path}")

    # Fix imports in all affected files
    for file_path in import_files:
        if os.path.abspath(file_path) != os.path.abspath(
            dst_path
        ):  # Don't modify the destination file itself
            fix_imports_in_file(file_path, module_name, module_prefix)
            print(f"Fixed imports in {file_path}")

    # Fix imports in the moved file itself if it's a Python file
    if dst_path.endswith(".py"):
        fix_imports_in_moved_file(dst_path)


def process_test_files():
    """Process test files based on patterns and move them to appropriate test directories."""
    print("Processing test files...")

    for pattern, dest_dir, import_prefix in TEST_FILES:
        files = glob.glob(os.path.join(ROOT_DIR, pattern))
        for file_path in files:
            if os.path.isfile(file_path):
                # Get relative path for destination
                filename = os.path.basename(file_path)
                dst_path = os.path.join(ROOT_DIR, dest_dir, filename)

                # Create destination directory and move file
                ensure_directory_exists(dst_path)

                # Get the module name from the source filename
                module_name = os.path.splitext(filename)[0]

                # Find all files that import this module
                if os.path.exists(file_path):
                    import_files = find_files_with_import(module_name)
                    print(f"Found {len(import_files)} files importing {module_name}")

                    # Move the file
                    shutil.copy2(file_path, dst_path)
                    print(f"Copied {file_path} to {dst_path}")

                    # Fix imports in all affected files if this is a Python module with imports
                    if import_prefix:
                        for import_file in import_files:
                            if os.path.abspath(import_file) != os.path.abspath(
                                dst_path
                            ):
                                fix_imports_in_file(
                                    import_file, module_name, import_prefix
                                )
                                print(f"Fixed imports in {import_file}")


def get_module_files():
    """Find and return module files that should be organized."""
    print("Looking for module files to organize...")

    # Patterns for module files (glob_pattern, destination_dir, import_module_prefix)
    MODULE_PATTERNS = [
        ("workflow_*.py", "workflow", "workflow"),
        ("analytics_*.py", "analytics", "analytics"),
        ("user_*.py", "user", "user"),
        ("security_*.py", "security", "security"),
        ("integration_*.py", "integration", "integration"),
    ]

    additional_mappings = []

    for pattern, dest_dir, import_prefix in MODULE_PATTERNS:
        files = glob.glob(os.path.join(ROOT_DIR, pattern))
        for file_path in files:
            if os.path.isfile(file_path):
                # Get relative path for source and destination
                rel_path = os.path.relpath(file_path, ROOT_DIR)
                filename = os.path.basename(file_path)
                dst_rel_path = os.path.join(dest_dir, filename)

                additional_mappings.append((rel_path, dst_rel_path, import_prefix))

    return additional_mappings


def process_mock_files():
    """Find and organize mock files into tests/mocks directory."""
    print("Processing mock files...")

    # Find all mock files in the root directory
    mock_files = glob.glob(os.path.join(ROOT_DIR, "mock_*.py"))
    for file_path in mock_files:
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            dst_path = os.path.join(ROOT_DIR, "tests/mocks", filename)

            # Create destination directory
            ensure_directory_exists(dst_path)

            # Find all files importing this mock
            module_name = os.path.splitext(filename)[0]
            import_files = find_files_with_import(module_name)

            # Copy the file to the new location
            shutil.copy2(file_path, dst_path)
            print(f"Copied {file_path} to {dst_path}")

            # Fix imports in all affected files
            for import_file in import_files:
                if os.path.abspath(import_file) != os.path.abspath(dst_path):
                    fix_imports_in_file(import_file, module_name, "tests.mocks")
                    print(f"Fixed imports in {import_file}")

            # Fix imports in the moved file itself
            fix_imports_in_moved_file(dst_path)


def main():
    """Main function to execute the file organization."""
    print("Starting file organization...")

    # First process explicitly defined mappings
    for src_path, dst_path, module_prefix in FILE_MAPPINGS:
        move_file_and_fix_imports(src_path, dst_path, module_prefix)

    # Then process test files
    process_test_files()

    # Process mock files specifically
    process_mock_files()

    # Finally look for module files
    additional_mappings = get_module_files()
    for src_path, dst_path, module_prefix in additional_mappings:
        move_file_and_fix_imports(src_path, dst_path, module_prefix)

    # Ask user if they want to remove the original files after copying
    try:
        confirm = input(
            "Files have been copied to their new locations. Delete original files? (y/n): "
        )
        if confirm.lower() == "y":
            # Remove original files
            for src_path, _, _ in FILE_MAPPINGS:
                src_full_path = os.path.join(ROOT_DIR, src_path)
                if os.path.exists(src_full_path):
                    os.remove(src_full_path)
                    print(f"Removed original file {src_full_path}")

            # Remove original test files
            for pattern, _, _ in TEST_FILES:
                files = glob.glob(os.path.join(ROOT_DIR, pattern))
                for file_path in files:
                    if os.path.isfile(file_path) and os.path.dirname(file_path) == str(
                        ROOT_DIR
                    ):
                        os.remove(file_path)
                        print(f"Removed original file {file_path}")

            # Remove original mock files
            mock_files = glob.glob(os.path.join(ROOT_DIR, "mock_*.py"))
            for file_path in mock_files:
                if os.path.isfile(file_path) and os.path.dirname(file_path) == str(
                    ROOT_DIR
                ):
                    os.remove(file_path)
                    print(f"Removed original file {file_path}")
    except Exception as e:
        print(f"Skipping file deletion. Original files remain. Error: {str(e)}")

    print("File organization complete!")


if __name__ == "__main__":
    main()
