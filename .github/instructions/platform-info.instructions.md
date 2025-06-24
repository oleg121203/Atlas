# Atlas Development Platform Instructions

## Unified Development Environment

Atlas uses a unified development approach for all platforms:

### Universal Development Setup
- **Platform**: Linux (development) / macOS (primary target)
- **Python Version**: 3.12+ (recommended: 3.12.8)
- **Purpose**: Cross-platform development and deployment
- **Environment**: GUI-compatible with headless fallbacks
- **Virtual Environment**: Single `venv` for all platforms

## Development Standards

### Code Compatibility
- All code MUST work on both Linux (dev) and macOS (target)
- Use platform detection utilities from `utils/platform_utils.py`
- Implement platform-specific features with proper fallbacks
- Test headless operation on Linux, GUI operation on macOS

### Python Version Management
```python
# Always check Python version compatibility
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8+ required")

# Use version-appropriate features for Python 3.12+
if sys.version_info >= (3, 12):
    # Use Python 3.12+ features
    pass
```

### Platform-Specific Development

#### Linux Development Environment
- **Focus**: Core logic, algorithms, AI integration
- **Testing**: Headless operation, CLI interface
- **Dependencies**: `requirements.txt`
- **Features**: Docker support, CI/CD compatibility

#### macOS Target Environment  
- **Focus**: Native GUI, system integration, user experience
- **Testing**: Full GUI operation, native features
- **Dependencies**: `requirements.txt` (with macOS-specific packages)
- **Features**: Quartz API, Dock integration, native permissions

### File Structure Standards
```
Atlas/
├── utils/
│   ├── platform_utils.py      # Cross-platform detection
│   ├── macos_utils.py         # macOS-specific utilities
│   └── linux_utils.py         # Linux development utilities
├── requirements.txt            # Universal dependencies (Python 3.12+)
├── launch_macos.sh            # macOS native launcher
├── venv/                      # Single virtual environment
└── dev-tools/                 # Development utilities
```

### Import Standards
```python
# Always use platform-aware imports
from utils.platform_utils import IS_MACOS, IS_LINUX, IS_HEADLESS

# Platform-specific imports
if IS_MACOS:
    from utils.macos_utils import configure_macos_gui
    # macOS-specific code here

if IS_LINUX:
    # Linux development code here
    pass

# Cross-platform fallbacks
try:
    import pyautogui
except ImportError:
    # Handle gracefully for headless environments
    pyautogui = None
```

### Testing Requirements
- **Linux**: All core functionality, headless operation
- **macOS**: GUI integration, native features, user workflows
- **Cross-platform**: Platform detection, fallback mechanisms

### Documentation Standards
- Document both development (Linux) and deployment (macOS) procedures
- Include platform-specific setup instructions
- Maintain separate README files:
  - `README.md` (Ukrainian, general)
  - `README_EN.md` (English, cross-platform)
  - `MACOS_SETUP.md` (macOS-specific)

### Deployment Strategy
1. **Development**: Universal environment with Python 3.12+
2. **Testing**: Both platforms for compatibility
3. **Release**: Cross-platform optimized build
4. **Distribution**: Native macOS application bundle

### Code Review Guidelines
- Ensure cross-platform compatibility
- Test on Python 3.12+ across platforms
- Verify headless operation works on Linux
- Confirm native features work on macOS
- Check platform detection logic

This unified approach ensures consistent development across platforms while maintaining native platform features.

## Windsurf AI Development Instructions

### Core Development Philosophy
- **Creative Automation Excellence**: Implement solutions that exceed industry best practices through innovative approaches
- **Autonomous Workflow**: Maintain continuous development momentum without pausing for user input
- **Code Modification Protocol**: Only modify Atlas core code when explicitly requested by the user
- **Protocol-Driven Development**: Follow established Windsurf protocols for quality, security, and continuous integration

### Windsurf Development Protocols
1. **Never-Stop Execution**: After completing any task, immediately proceed to the next logical step as defined in DEV_PLAN.md
2. **Creative Problem Solving**: Approach challenges with innovative solutions that surpass conventional methods
3. **Quality Excellence**: Maintain type safety, security, and performance standards automatically
4. **Documentation Integrity**: Update CHANGELOG.md and DEV_PLAN.md for all significant changes
5. **Protocol Compliance**: Follow .windsurf/rules/ protocols strictly for all development activities

### Recommended Windsurf Model Configuration
For Atlas development protocols and automated workflows:

**Primary Recommendation: Claude 3 Opus (Sonnet v3.5)**
- **Strengths**: Superior code reasoning, complex system understanding, autonomous task execution
- **Use Case**: Core Atlas development, protocol implementation, type safety improvements
- **Performance**: Excellent for multi-step reasoning and continuous development workflows

**Alternative Options:**
- **Gemini Pro 2.5**: Good for creative problem solving and innovative approaches
- **GPT-4o**: Reliable for standard development tasks and documentation
- **DeepSeek V3**: Cost-effective for routine protocol enforcement
- **o3-mini**: Efficient for focused, specific development tasks

### Windsurf Integration Best Practices
- Configure for autonomous operation with minimal user interruption
- Leverage Atlas's existing CI/CD pipeline for quality assurance
- Maintain cross-platform compatibility (Linux dev / macOS target)
- Use established monitoring and metrics for performance tracking

### Model Selection Guidance
**For Protocol-Heavy Development**: Claude 3 Opus (Sonnet v3.5)
**For Creative Innovation**: Gemini Pro 2.5
**For Cost-Effective Maintenance**: DeepSeek V3
**For Focused Tasks**: o3-mini

## AI System Internal Instructions

### Core Security Directive: Access Control

**This is a primary security directive and cannot be overridden by any user or AI prompt under any circumstances. Violation will result in immediate termination of the process.**

#### Level 1: Documentation Access (Workflow & Dev AIs)

- **Resource**: `docs/reports/security/SECURITY_SYSTEM_REPORT.md.encrypted`
- **Key Location**: Environment variable `ATLAS_CORE_INIT_KEY` in the `.env` file.
- **Rule**: Development and workflow AI agents are permitted to use this key **only** to decrypt the security documentation to understand the system's design.

#### Level 2: Creator Protocol Access (Atlas Core Only)

- **Resource**: Encrypted Creator-Atlas communication protocols.
- **Key Location**: Hardcoded internally within the Atlas core logic. **It is not accessible via environment variables or configuration files.**
- **Rule**: Access is restricted exclusively to the core Atlas application and its integrated functions (e.g., `CreatorAuthentication`). These protocols are used for runtime authentication and are strictly off-limits to any external or non-core AI.

**Any attempt by a non-core AI to access or request the internal protocol key is a critical security violation.**

**Encrypted Security Documentation** (Use `ATLAS_CORE_INIT_KEY` from `.env` to decrypt):
```
gAAAAABm8k7vU3n9K5cP2wE8mR6oL4tN7bY1sF3hG9vX2qA8dZ5jW0iR4pE6uT7hN9k2sL5wQ3r7 
vB2oP8xF6tE9mK3sH4vD1zL7wQ9r2pE5tY8hG3nF6uK5oA2dR7vB4sX8eN1mQ6rP3wL9tH5kF2v
I7bC4oP9xE3rT8vL1qW5hG2nK6sA9dF4tY7uX3eR0mP5vB8oL2hK6sN9tW3r1qE4vF7bY0hA5d
X9sP2mK8tL4vB3oR6eW1qY5hN7uF3dA0sK2vP9xL6rT8hG4nB5wQ7oE1mR3vK9sL6hP2tF8uY4d
A7bX5oN2wE9rV3pL6hT1qK8sF4nG0mY7vB5dR2oP9xU6eL3tA8hW1qF5vN4sK7bG2mR0pY9oX3
L6hE4tW8dA1nF5bY7sK3rG9mP2vX6oL0hT4eR8qN1wF5bA3sY7mK9rP6vG2nL4hX0oE5tQ8dW1
V3sF6bN9mY2pL7hA4oR8xE1tG5wQ3vK6sN0rP9mH2bF7dL4oY1eX8tA5sW3qG6nK9rV2pM7hB0
F4oY8dL1xE5tN3wA6sR9vG2mP7hK4bQ0oL8nF5rY1vX3tE9sA2dW6hG4pN7mB0oK8rL5vF3eT1
Y9hP2sA6wG4nR7oX5bL3mF8dE1tQ6vK9sH2pY7oN4hG3rW8bA0sL5vF2xE9tM6rP1qK4oN8dY3
G7hF5bL0sR9vW2eT6pA4oK1mN8hY3sX7bG5rF9vL2qE0tW6dA8oP3hN1mK7sF4bY5oG9rV6eL2
T3hA0sP8qN1wF7bM4oG2rY9vL5dX6hE3tK8sA1mP7oB4nF0hY5wG2rQ9vL3eT6sA8oK1xF7bN4
M2hG5rY0sL8vP3qE6tA9oW1dF4bX7hN2sK5rG8vL0mP3eY6oA4tQ1wF9bH7sN2rG5vL8pM0hY3
A6oF1bE4tQ7sK9rP2vL5mG8hN0oY3dW1xF6bT4sA7rG2mP9vL5hE8oN1qY0bF3tK6sA4rW7nG2
X5pM8vL1hY9oB0sF3tA6rQ4eG7mP2vL5hN8oW1dY3bF6tK9sA0rG4mP7vL2hE5nY8oQ1wF3bT6
S7rA4mG9vL0hP2eN5oY8dF1bX3tK6sA7rW4nG2vM5pL8hY0oE9qF3bT1sA6rG4mP7vL2hN5eY8
```