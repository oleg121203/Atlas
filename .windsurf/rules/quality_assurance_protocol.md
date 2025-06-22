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
6. **Performance Requirements**:
   - Screen/input tools: <100ms latency
   - Planning operations: <500ms latency
   - Memory operations: <200ms latency
   - Monitor and log all operation times
   - Implement fallbacks for slow operations
   - Auto-generate performance reports every 30 minutes
7. **Dependency and Resource Management**:
   - Keep dependencies minimal and pinned
   - Implement lazy loading for heavy modules
   - Monitor memory usage and implement auto-cleanup
   - Cache frequently used results with TTL
8. **Continuous Quality Control**:
   - Self-review code diff
   - Run performance benchmarks
   - Update CHANGELOG.md
   - Verify graceful degradation paths
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
