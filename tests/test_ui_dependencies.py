"""
Test to ensure UI components only use PySide6.
"""

import ast
import os
from pathlib import Path


def get_imports(file_path):
    """Get all imports from a Python file."""
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def test_ui_uses_only_pyside6():
    """Test that UI components only use PySide6 and not tkinter."""
    ui_dir = Path(__file__).parent.parent / "ui"
    forbidden_imports = {"tkinter", "customtkinter", "tk"}

    violations = []

    for root, _, files in os.walk(ui_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imports = get_imports(file_path)

                for imp in imports:
                    if any(forbidden in imp.lower() for forbidden in forbidden_imports):
                        violations.append(f"{file_path}: uses {imp}")

    assert not violations, "Found tkinter usage in UI files:\n" + "\n".join(violations)
