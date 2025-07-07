# Atlas Tools

This directory contains automation tools used by Atlas agents.

## Available Tools

### Screen and Input Tools
- **screenshot_tool.py**: Captures screen content for analysis
- **mouse_keyboard_tool.py**: Controls mouse and keyboard for automation
- **ocr_tool.py**: Performs optical character recognition on screen content

### Content Processing Tools
- **code_reader_tool.py**: Analyzes and extracts information from code files
- **translation_tool.py**: Translates text between languages
- **image_recognition_tool.py**: Identifies objects and content in images

### System Integration Tools
- **terminal_tool.py**: Executes terminal commands and processes output
- **notification_tool.py**: Sends system notifications
- **clipboard_tool.py**: Interacts with the system clipboard
- **web_browser_tool.py**: Controls web browsers for automated navigation

### Memory and Storage Tools
- **memory_demo.py**: Demonstrates memory functionality
- **simple_memory_test.py**: Tests basic memory operations
- **chat_memory_demo.py**: Shows chat history memory capabilities
- **memory_migration.py**: Handles memory format migrations

### Development and Debugging Tools
- **performance_profiler.py**: Profiles tool execution performance
- **dependency_analyzer.py**: Analyzes tool dependencies

## Generated Tools

The `generated/` directory contains tools that are dynamically created by the `ToolCreatorAgent` during runtime based on user needs.

## Tool Development Guidelines

When developing new tools for Atlas:

1. **Platform Compatibility**: Ensure the tool works on both Linux (dev) and macOS (target)
2. **Performance**: Tools that manipulate screen or input should have <100ms latency
3. **Error Handling**: Include robust error handling and graceful degradation
4. **Documentation**: Include comprehensive docstrings following Google style
5. **Testing**: Write unit tests in the corresponding test directory

## Integrating New Tools

New tools need to be:
1. Registered in the `plugin_manager.py`
2. Documented in this README
3. Tested on both platforms (Linux/macOS)
4. Added to the appropriate test suite

## Performance Requirements

- Screen manipulation tools must respond in <100ms
- Long-running tools should support asynchronous operation
- All tools should report their execution time for monitoring

## Related Documentation

For more information on the tools system:
- `docs/TOOLS.md`: Comprehensive guide to all development tools
- `agents/tool_creator_agent.py`: Dynamic tool creation documentation
