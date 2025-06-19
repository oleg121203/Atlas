---
applyTo: '**'
---

# Atlas Development Platform Instructions

## Dual Development Environment

Atlas is developed using a dual-environment approach:

### Primary Development (Linux)
- **Platform**: Linux (Ubuntu/Codespaces)
- **Python Version**: 3.12
- **Purpose**: Core development, testing, CI/CD
- **Environment**: Headless-compatible for cloud development

### Target Platform (macOS)
- **Platform**: macOS (Primary target deployment)
- **Python Version**: 3.13
- **Purpose**: Native macOS application deployment
- **Environment**: Full GUI with native macOS integration

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

# Use version-appropriate features
if sys.version_info >= (3, 12):
    # Use Python 3.12+ features for Linux dev
    pass
elif sys.version_info >= (3, 13):
    # Use Python 3.13+ features for macOS
    pass
```

### Platform-Specific Development

#### Linux Development Environment
- **Focus**: Core logic, algorithms, AI integration
- **Testing**: Headless operation, CLI interface
- **Dependencies**: `requirements-linux.txt`
- **Features**: Docker support, CI/CD compatibility

#### macOS Target Environment  
- **Focus**: Native GUI, system integration, user experience
- **Testing**: Full GUI operation, native features
- **Dependencies**: `requirements-macos.txt`
- **Features**: Quartz API, Dock integration, native permissions

### File Structure Standards
```
Atlas/
├── utils/
│   ├── platform_utils.py      # Cross-platform detection
│   ├── macos_utils.py         # macOS-specific utilities
│   └── linux_utils.py         # Linux development utilities
├── requirements-linux.txt      # Linux (Python 3.12) deps
├── requirements-macos.txt      # macOS (Python 3.13) deps
├── launch_macos.sh            # macOS native launcher
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
1. **Development**: Linux environment with Python 3.12
2. **Testing**: Both platforms for compatibility
3. **Release**: macOS-optimized build with Python 3.13
4. **Distribution**: Native macOS application bundle

### Code Review Guidelines
- Ensure cross-platform compatibility
- Test on both Python 3.12 (Linux) and 3.13 (macOS)
- Verify headless operation works on Linux
- Confirm native features work on macOS
- Check platform detection logic

This dual-environment approach ensures robust development on Linux while delivering a native macOS experience.