# Atlas Phase 14 Quick Start Guide

## 🚨 CRITICAL APPLICATION STARTUP FAILURE

**Current Status**: Atlas application has BLOCKING PyQt5 import errors preventing launch.

**Root Cause**: Direct violation of UNIFIED INTERFACE principle - PyQt5 imports found in PySide6-only codebase.

**Blocking Error**: 
```
File "/Users/dev/Documents/NIMDA/Atlas/ui/ai_assistant_widget.py", line 10
from PyQt5.QtCore import pyqtSignal
ModuleNotFoundError: No module named 'PyQt5'
```

**Priority**: Convert ALL PyQt5 imports to PySide6 equivalents immediately.

## ⚡ Quick Commands for Windsurf Chat

Copy and paste these commands into Windsurf chat for immediate execution:

### **Step 1: Fix CRITICAL PyQt5 Import Violations**
```
/chat Fix CRITICAL PyQt5 import violation in Atlas ui/ai_assistant_widget.py - convert PyQt5.QtCore.pyqtSignal to PySide6.QtCore.Signal and scan entire codebase for any other PyQt5 imports that violate the UNIFIED INTERFACE principle
```

### **Step 2: Fix Main Window GUI Errors**
```
/chat Fix Atlas main_window.py PySide6 errors - correct QAction import from PySide6.QtGui instead of QtWidgets, fix Qt attribute access using Qt.Orientation.Vertical and Qt.ToolBarArea.TopToolBarArea, and add missing main_layout, logger, theme_manager attribute initialization
```

### **Step 3: Create Minimal Functional Application**
```
/chat Create minimal functional Atlas application - implement basic AtlasMainWindow that launches successfully with error handling and graceful degradation for missing components, following the target architecture in DEV_PLAN.md
```

### **Step 4: Implement Cyberpunk Theme System**
```
/chat Implement Atlas cyberpunk and hacker theme system - fix theme_manager initialization, enhance hacker.json with terminal green matrix effects, and enhance cyberpunk_neon.json with neon glow effects and dark backgrounds
```

### **Step 5: Test Application**
```
/chat Test Atlas application startup and run available VS Code tasks - use Ruff: Lint, Ruff: Fix, and Pytest: Run All Tests to validate fixes and ensure application launches without errors
```

## 🎯 Success Criteria

- [ ] Atlas application launches without import errors
- [ ] Main window displays properly with PySide6 UI
- [ ] Theme system loads and applies cyberpunk/hacker themes
- [ ] No critical crashes or blocking errors
- [ ] Basic UI modules are functional

## 📋 Development Notes

- **Architecture**: Follow DEV_PLAN.md target structure exactly
- **UI Framework**: PySide6 only (unified interface)
- **Theme Focus**: Cyberpunk/hacker aesthetic with matrix effects
- **Error Handling**: Implement graceful degradation for missing components
- **Testing**: Use existing VS Code tasks for validation

## 🔄 Continuous Execution

After completing these steps, continue with full DEV_PLAN.md Phase 14 tasks using the commands in WINDSURF_COMMANDS.md.

**Next Phase**: Complete architecture compliance, implement developer tools integration, and achieve full cyberpunk AI platform functionality.
