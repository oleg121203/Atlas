# Tool System Import Issues Fix Plan

## Issues Identified:

1. **chat_memory_demo.py**: Imports from non-existent `modules` package
2. **creative_tool.py**: Uses relative import `.base_tool` 
3. **delay_tool.py**: Uses relative import
4. **memory_demo.py**: Imports from non-existent `modules` package  
5. **memory_migration.py**: Imports from non-existent `modules` package
6. **performance_audit.py**: Import error with `email.parser`
7. **playful_tool.py**: Uses relative import
8. **plugin_tool.py**: Imports non-existent functions from `plugins`
9. **proactive_tool.py**: Uses relative import
10. **safari_professional_tool.py**: Missing selenium dependency

## Fix Strategy:

### Phase 1: Fix Relative Imports
- Replace `.base_tool` with `tools.base_tool` in all tools
- Update import statements to use absolute imports

### Phase 2: Fix Missing Dependencies
- Either fix imports or move problematic tools to legacy folder
- Install missing dependencies where appropriate

### Phase 3: Fix Tools That Import Non-existent Modules
- Update chat_memory_demo.py to use correct imports
- Fix plugin_tool.py to use new plugin system
- Update memory_* tools to use correct imports

### Phase 4: Validate Tool Loading
- Run integration test to verify all tools load correctly
- Update tool_manager.py if needed
