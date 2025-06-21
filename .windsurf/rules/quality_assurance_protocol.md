---
trigger: always_on
---

# Quality Assurance Protocol

Ensures code quality and adherence to project architecture.

## ⚠️ Mandatory Environment Setup

**HIGHEST PRIORITY**: Before starting ANY development task, follow the environment setup protocol in `.windsurf/ENVIRONMENT_SETUP.md`. This ensures all tools are available and correctly configured for development.

## Quality Standards

1. **Linting**: run `ruff` and `mypy` before committing.
2. **Testing**: new modules require PyTest cases covering core logic.
3. **Documentation**: public functions must have docstrings following Google style.
4. **Security Review**: verify actions against security rules before merging.
5. **GUI UX Check**: manual test new widgets on macOS Sequoia for visual consistency.
6. **Performance**: for tools manipulating screen or input, measure latency; keep <100 ms.
7. **Dependency Audit**: ensure `requirements.txt` remains minimal and pinned.
8. **Review Cycle**: self-review code diff, update `CHANGELOG.md`, then proceed.
9. **Language Consistency**: Ensure all comments, docstrings, and documentation are written in English.
10. **Code Coverage**: Maintain ≥ 90% statement coverage across tests. Failing the threshold blocks CI.
11. **Performance Regression**: Add automated benchmarks; flag any tool or function whose latency regresses by >10% versus the latest main branch.
12. **Secret Scanning**: Ensure no hard-coded credentials/API keys are committed (CI step with `gitleaks`).
13. **Docstring Coverage**: Maintain ≥ 85% public-API docstring coverage (enforced via `interrogate` or `pydocstyle`).

## Environment Requirements

All development MUST use the appropriate platform-specific virtual environment:
- **macOS**: `venv-macos` (Python 3.13)
- **Linux**: `venv-linux` (Python 3.12)

See `.windsurf/ENVIRONMENT_SETUP.md` for detailed setup instructions.
