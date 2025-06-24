# Atlas Linting Configuration

This document explains the linting configuration for the Atlas project.

## Pre-commit Hook

The project uses pre-commit hooks to ensure code quality. The hooks check:

1. **Ruff** - A fast Python linter
2. **mypy** - Static type checking
3. **Secret scanning** - Basic detection of potential secrets in code

## Ruff Configuration

Ruff is configured in two places:

1. **pyproject.toml** - Contains the base Ruff configuration
2. **.ruff.toml** - Contains additional configurations to make the pre-commit hook pass

The `.ruff.toml` file temporarily ignores some common linting errors to allow commits to proceed while the codebase is being improved. These ignored rules can be gradually fixed over time.

## Temporarily Ignored Rules

The following rules are temporarily ignored in `.ruff.toml`:

- `E501`: Line too long
- `FA100`: Future-rewritable type annotation
- `G004`: Logging f-string
- `T201`: Print statement
- `TRY400`: Error instead of Exception
- `W293`: Blank line with whitespace
- `DTZ005`: Call datetime.now without tzinfo
- `PGH003`: Blanket type ignore
- `PLC0415`: Import outside top level
- `RUF001`: Ambiguous unicode character string
- `TRY300`: Try-consider-else
- `G201`: Logging exc_info
- `ARG002`: Unused method argument
- `RUF013`: Implicit optional
- `PLR2004`: Magic value comparison
- `C901`: Complex structure

## Future Improvements

The goal is to gradually fix these issues and enforce stricter linting rules over time. To do so:

1. Choose one rule to fix (e.g., `T201` to remove print statements)
2. Remove it from the ignore list in `.ruff.toml`
3. Run `python -m ruff check . --fix --select T201` to auto-fix where possible
4. Manually fix remaining issues
5. Commit the changes

## Type Checking with mypy

The pre-commit hook also runs mypy for type checking. While it reports errors, it currently allows commits to proceed with warnings.

## Secret Detection

The pre-commit hook includes basic secret detection to prevent accidentally committing sensitive information.

## Related Documentation

For more detailed information about development tools and requirements:

- [Tools Documentation](docs/TOOLS.md) - Comprehensive guide to all development tools
- [Requirements Management](docs/REQUIREMENTS.md) - Platform-specific requirements strategy
- [Development Plan](DEV_PLAN.md) - Overall development roadmap and plans

## Installation

All linting tools are included in the `requirements-dev.txt` file. Install them with:

```bash
pip install -r requirements-dev.txt
```
