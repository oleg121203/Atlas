# Atlas Dual Development Environment

Atlas is developed using a dual-environment approach with specific requirements for each platform.

## Development Environments

### Primary Development (Linux)
- **Platform**: Linux (Ubuntu/Codespaces)
- **Python Version**: 3.12
- **Purpose**: Core development, testing, CI/CD
- **Environment**: Headless-compatible for cloud development
- **Requirements**: `requirements-linux.txt`

### Target Platform (macOS)
- **Platform**: macOS (Primary target deployment)
- **Python Version**: 3.13
- **Purpose**: Native macOS application deployment
- **Environment**: Full GUI with native macOS integration
- **Requirements**: `requirements-macos.txt`

## Requirements Structure

Atlas maintains multiple requirements files to support the dual-development approach:

1. **requirements.txt**: Core dependencies for all environments
2. **requirements-linux.txt**: Linux-specific dependencies (Python 3.12)
3. **requirements-macos.txt**: macOS-specific dependencies (Python 3.13)
4. **requirements-dev.txt**: Development tools and utilities
5. **requirements-current.txt**: Snapshot of the current environment

## Platform-Specific Dependencies

### Linux-Specific Dependencies
- Core AI and processing libraries
- Headless operation support
- CI/CD tooling
- Docker compatibility

### macOS-Specific Dependencies
- Native GUI libraries (PyObjC, Quartz)
- macOS application bundling (py2app)
- Status bar integration (rumps)
- macOS system service integration

### Development Dependencies
- Linting tools (Ruff, mypy, Black)
- Testing frameworks (pytest)
- Security scanning (bandit, safety)
- Type stubs for better code completion

## Managing Requirements

Use the provided script to synchronize and manage requirements:

```bash
# Synchronize requirements files
./scripts/sync_requirements.sh

# Install platform-specific requirements
# For Linux:
pip install -r requirements-linux.txt

# For macOS:
pip install -r requirements-macos.txt

# Install development tools
pip install -r requirements-dev.txt
```

## Version Management

Atlas enforces strict version management for dependencies:

1. Primary dependencies use `>=` to allow compatible updates
2. Critical dependencies use `==` to lock specific versions
3. Type stubs follow their corresponding package versions

## Cross-Platform Development Best Practices

1. Always use platform detection from `utils/platform_utils.py`
2. Test on both Linux and macOS before committing
3. Keep platform-specific code in dedicated modules
4. Use conditional imports for platform-specific features
5. Ensure headless operation works on Linux

## Integration with Windsurf Protocols

The requirements management follows the Windsurf protocols for quality assurance and security:

1. **Dependency Audit**: Ensure requirements remain minimal and pinned
2. **Dependency Security**: Run `safety check` before adding new dependencies
3. **Automated Updates**: Dependabot creates PRs for security patches

## More Information

For more details on development tools and utilities, see:
- `docs/TOOLS.md`: Comprehensive guide to development tools
- `LINTING.md`: Linting configuration and guidelines
