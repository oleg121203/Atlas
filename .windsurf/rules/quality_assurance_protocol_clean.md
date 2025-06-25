---
trigger: always_on
---

# Quality Assurance Protocol

Ensures code quality and adherence to project architecture.

1. **Linting**: run `ruff` and `mypy` before committing.
2. **Testing**: new modules require PyTest cases covering core logic.
3. **Documentation**: public functions must have docstrings following Google style.
4. **Security Review**: verify actions against security rules before merging.
5. **GUI UX Check**: manual test new widgets on macOS Sequoia for visual consistency.
6. **Performance**: for tools manipulating screen or input, measure latency; keep <100 ms.
7. **Dependency Audit**: ensure `requirements.txt` remains minimal and pinned.
8. **Review Cycle**: self-review code diff, update `CHANGELOG.md`, then proceed.
9. **English-Only Code**: All code, variable names, function names, and comments must be in English.
10. **Multilingual UI**: Ensure UI supports Ukrainian, Russian, and English languages.
11. **macOS Optimization**: Optimize for Mac Studio M1 Max 32GB unified memory architecture.
12. **Continuous Testing**: Always continue testing even when minor issues are encountered. Log issues in a separate report but don't halt the testing process. Create fallback behaviors to allow tests to proceed past non-critical failures.
