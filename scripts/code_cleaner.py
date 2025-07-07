#!/usr/bin/env python3
"""Automatic fixing of common Python code issues."""

from pathlib import Path


def remove_definition(file_path, definition_name):
    """Removes the specified definition from the file."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    in_definition = False
    result = []

    for line in lines:
        if line.startswith(f"def {definition_name}(") or line.startswith(
            f"class {definition_name}("
        ):
            in_definition = True
            continue
        elif in_definition and (line.startswith("def ") or line.startswith("class ")):
            in_definition = False
            result.append(line)
        elif not in_definition:
            result.append(line)

    with open(file_path, "w") as f:
        f.writelines(result)
    return in_definition


def format_long_lines(file_path, max_length=120):
    """Formats long lines by splitting them into multiple lines."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if len(line.rstrip("\n")) > max_length:
            # Check if this is a string literal
            if ('"' in line or "'" in line) and not line.strip().startswith("#"):
                # Split string literal
                quote_char = '"' if '"' in line else "'"
                split_pos = line.find(quote_char)
                if split_pos != -1:
                    before_quote = line[:split_pos]
                    after_quote = line[split_pos:]

                    # Find end of string
                    j = i
                    while j < len(lines) and after_quote.count(quote_char) % 2 != 0:
                        j += 1
                        if j < len(lines):
                            after_quote += lines[j]

                    # Split the line
                    result.append(
                        before_quote
                        + after_quote[: len(after_quote) // 2]
                        + " \
"
                    )
                    result.append(after_quote[len(after_quote) // 2 :])
            else:
                # Just add line break
                result.append(
                    line[:max_length]
                    + " \
"
                )
                result.append(line[max_length:])
            i += 1
        else:
            result.append(line)
            i += 1

    with open(file_path, "w") as f:
        f.writelines(result)


if __name__ == "__main__":
    # Example usage
    project_root = Path(__file__).parent.parent

    # Remove the specified definition
    for file_path in project_root.rglob("*.py"):
        if "venv" not in str(file_path):
            removed = remove_definition(file_path, "get_platform_info")
            if removed:
                print(f"Definition get_platform_info removed from {file_path}")

    # Format long lines
    for file_path in project_root.rglob("*.py"):
        if "venv" not in str(file_path):
            format_long_lines(file_path)
            print(f"Formatted long lines in {file_path}")
