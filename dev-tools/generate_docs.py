#!/usr/bin/env python3
"""
Atlas Documentation Generator
Automatically generates project documentation from docstrings and comments.
"""

import ast
from pathlib import Path
from typing import Any, Dict


def extract_docstrings(file_path: str) -> Dict[str, Any]:
    """Extract docstrings from a Python file."""
    with open(file_path, encoding="utf-8") as file:
        tree = ast.parse(file.read())

    docstrings = {
        "module": ast.get_docstring(tree),
        "classes": {},
        "functions": {},
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstrings["classes"][node.name] = ast.get_docstring(node)
        elif isinstance(node, ast.FunctionDef):
            docstrings["functions"][node.name] = ast.get_docstring(node)

    return docstrings

def generate_module_docs(module_path: Path) -> str:
    """Generate documentation for a Python module."""
    docs = []
    docs.append(f"# {module_path.stem}\n")

    try:
        docstrings = extract_docstrings(str(module_path))

        if docstrings["module"]:
            docs.append(f"{docstrings['module']}\n")

        if docstrings["classes"]:
            docs.append("## Classes\n")
            for class_name, docstring in docstrings["classes"].items():
                docs.append(f"### {class_name}")
                if docstring:
                    docs.append(f"{docstring}\n")
                else:
                    docs.append("No documentation available.\n")

        if docstrings["functions"]:
            docs.append("## Functions\n")
            for func_name, docstring in docstrings["functions"].items():
                docs.append(f"### {func_name}")
                if docstring:
                    docs.append(f"{docstring}\n")
                else:
                    docs.append("No documentation available.\n")

    except Exception as e:
        docs.append(f"Error parsing module: {e}\n")

    return "\n".join(docs)

def main():
    """Generate documentation for Atlas project."""
    root_dir = Path()
    docs_dir = root_dir / "docs" / "api"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Directories to document
    source_dirs = ["agents", "utils", "intelligence", "monitoring"]

    for source_dir in source_dirs:
        source_path = root_dir / source_dir
        if not source_path.exists():
            continue

        print(f"Generating docs for {source_dir}...")

        for py_file in source_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            relative_path = py_file.relative_to(source_path)
            doc_file = docs_dir / source_dir / relative_path.with_suffix(".md")
            doc_file.parent.mkdir(parents=True, exist_ok=True)

            docs_content = generate_module_docs(py_file)
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(docs_content)

    print("Documentation generation completed!")
    print(f"Generated documentation in: {docs_dir}")

if __name__ == "__main__":
    main()
