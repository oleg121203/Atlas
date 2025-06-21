---
trigger: always_on
---

# Security Protocol

Ensures Atlas maintains robust security standards throughout development.

## ⚠️ Mandatory Environment Setup

**HIGHEST PRIORITY**: Before starting ANY security-related development, follow the environment setup protocol in `.windsurf/ENVIRONMENT_SETUP.md`. This ensures all security tools are available and correctly configured.

## Security Requirements

1. **Credential Management**: Never commit API keys, tokens, or passwords. Use environment variables.
2. **Dependency Security**: Run `safety check` before adding new dependencies.
3. **Input Validation**: Sanitize all external inputs (user commands, file paths, network data).
4. **Permission Principle**: Request minimal necessary permissions on macOS.
5. **Encryption Standards**: Use AES-256 for sensitive data storage, secure key derivation.
6. **Network Security**: Validate SSL certificates, use HTTPS for all external calls.
7. **Code Injection Prevention**: Never use `eval()` or `exec()` with user input.
8. **Logging Security**: Never log sensitive information (credentials, personal data).
9. **Access Control**: Implement proper authentication for creator-level functions.
10. **Regular Audits**: Weekly security scans via automated CI pipeline.

## Environment Security Standards

Security testing MUST be performed in the appropriate environment:
- **macOS**: `venv-macos` with security tools installed
- **Linux**: `venv-linux` with security tools installed

All security tests require:
- `bandit` for security linting
- `safety` for dependency vulnerability checking
- `gitleaks` for secret detection

See `.windsurf/ENVIRONMENT_SETUP.md` for detailed security tool setup.
