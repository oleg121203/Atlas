# Testing Guidelines for Atlas

## Introduction

Testing is a critical part of the Atlas development process to ensure the reliability, performance, and maintainability of the application. This document outlines the guidelines and best practices for writing and maintaining tests for Atlas.

## Test Types

Atlas incorporates several types of tests to cover different aspects of the application:

- **Unit Tests**: These tests focus on individual components or functions to ensure they work as expected in isolation. They are quick to run and help catch regressions early.
- **Integration Tests**: These tests verify that different parts of the system work together correctly. They cover interactions between modules, plugins, and UI components.
- **Performance Tests**: These tests measure the system's performance under various conditions, ensuring that operations like plugin loading and enabling meet latency requirements.
- **UI Component Tests**: These tests focus on the user interface, verifying that widgets, menus, and other visual elements behave as expected.
- **Load Tests**: These tests simulate high usage scenarios to ensure the system can handle stress without degradation in performance.

## Testing Framework

Atlas uses the `unittest` framework for Python testing. All tests should be written to be compatible with this framework.

## Test Organization

- Tests should be organized in the `tests` directory, with subdirectories mirroring the structure of the main codebase where applicable (e.g., `tests/agents`, `tests/ui_qt`).
- Each test file should focus on a specific module or component (e.g., `plugin_edge_cases.py` for edge cases in plugin handling).
- Test names should be descriptive and indicate the purpose of the test (e.g., `test_plugin_with_invalid_metadata`).

## Writing Tests

### General Guidelines

1. **Isolation**: Ensure tests are independent of each other. Use `setUp` and `tearDown` methods to create a fresh environment for each test.
2. **Mocking**: Use the `unittest.mock` library to mock dependencies, especially for external systems or complex interactions.
3. **Coverage**: Aim for high test coverage, especially for critical components like `PluginManager` and `AgentManager`. Tests should cover normal operation, edge cases, and error conditions.
4. **Performance Metrics**: For performance and load tests, include timing assertions to ensure operations complete within acceptable limits.

### Unit Tests

- Focus on a single function or class.
- Test both the happy path and error conditions.
- Use mocks to isolate the unit under test from dependencies.

### Integration Tests

- Test interactions between components (e.g., how `PluginManager` interacts with `AgentManager`).
- Verify data flow and state changes across multiple components.

### Performance and Load Tests

- Set clear performance benchmarks (e.g., loading 100 plugins should take less than 1 second).
- Simulate realistic loads (e.g., enabling multiple plugins in quick succession).
- Measure and log performance metrics for analysis.

### UI Component Tests

- Test user interactions like clicks, drags, and keyboard shortcuts.
- Verify visual consistency and state changes in response to user actions.
- Use tools like `pytest-qt` if available for Qt-based UI testing.

## Running Tests

- Run tests using the command `python -m unittest discover tests` from the project root to execute all tests.
- Individual test files can be run with `python -m unittest tests/test_file.py`.
- Ensure the environment is set up as per `.windsurf/ENVIRONMENT_SETUP.md` before running tests.

## Continuous Integration (CI)

- All tests must pass in the CI pipeline before merging to the main branch.
- The CI pipeline includes running `ruff`, `mypy`, and the full test suite.
- Performance benchmarks are executed, and any regression greater than 10% will fail the pipeline.

## Test Maintenance

- **Update Tests with Code Changes**: When modifying code, update corresponding tests to reflect new behavior or requirements.
- **Remove Obsolete Tests**: Delete tests for deprecated features or components.
- **Review Test Coverage**: Regularly check test coverage using tools like `coverage.py` to identify untested areas.
- **Document Test Failures**: If a test fails consistently, document the issue in `DEV_PLAN.md` under a 'Blocking' section and outline resolution steps.

## Performance Requirements

- Screen/input tools: <100ms latency
- Planning operations: <500ms latency
- Memory operations: <200ms latency
- Monitor and log all operation times in performance tests.
- Implement fallbacks for slow operations and test graceful degradation paths.

## Code Coverage Goals

- Maintain ≥ 90% statement coverage across tests. Failing this threshold blocks CI.
- Maintain ≥ 85% public-API docstring coverage, enforced via tools like `interrogate` or `pydocstyle`.

## Security Testing

- Include tests for input validation and sanitization to prevent injection attacks.
- Test credential management to ensure no secrets are hard-coded or logged.
- Use tools like `bandit` for security linting as part of the test suite.

## Cross-Platform Testing

- Test on both macOS and Linux environments as specified in `.windsurf/ENVIRONMENT_SETUP.md`.
- Note any platform-specific issues or behaviors in test documentation.

## Test Data

- Use fixtures and mocks to create consistent test data.
- Develop comprehensive test data sets for various scenarios, including edge cases.

## Reporting and Metrics

- Tests should log detailed diagnostics on failure for debugging.
- Performance tests should generate reports every 30 minutes during active development.
- Use CI tools to track test results and identify trends or recurring issues.

## Conclusion

Adhering to these testing guidelines ensures that Atlas maintains a high standard of quality and reliability. By covering unit, integration, performance, load, and UI aspects, we can confidently develop and refactor the application knowing that regressions and issues will be caught early.
