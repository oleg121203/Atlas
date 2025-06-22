# Browser and Application Control Features

## Overview

Atlas now includes comprehensive control over browsers and applications, enabling users to automate interactions with various software on their system. This functionality is crucial for achieving complex automation tasks and enhancing user productivity.

## Browser Control

### Features
- **Browser Selection**: Users can specify their preferred browser (e.g., Safari, Chrome, Firefox) for web interactions.
- **URL Navigation**: Open specific URLs in the chosen browser.
- **Tab Control**: Manage browser tabs through the `BrowserAgent`.
- **Profile Support**: Open specific browser profiles for personalized settings.

### Implementation
- **BrowserAgent**: Located in `agents/browser_agent.py`, this agent handles browser-related tasks and integrates with the Advanced Web Browsing plugin.
- **Advanced Web Browsing Plugin**: Found in `plugins/web_browsing/plugin.py`, it supports multiple automation methods (Selenium, Playwright, system events) with fallback mechanisms.
- **Key Methods**:
  - `open_browser(browser_name)`: Initializes a browser based on user preference.
  - `navigate_to_url(url)`: Navigates to the specified URL.

### Usage
To open a URL in Safari, a user can simply request: "Open Safari and go to google.com". The `BrowserAgent` will handle the request by initializing Safari and navigating to the specified URL.

## Application Control

### Features
- **Terminal Command Execution**: Run shell commands and scripts directly from Atlas.
- **Mouse and Keyboard Control**: Automate mouse clicks, movements, and keyboard inputs.
- **Clipboard Management**: Copy, paste, and clear clipboard content programmatically.
- **Application Launching**: Open applications by name on macOS or Windows.

### Implementation
- **ApplicationAgent**: Newly developed in `agents/application_agent.py`, this agent manages general application control tasks.
- **Core Tools**: Located in `tools/` directory, including:
  - `terminal_tool.py` for command execution.
  - `mouse_keyboard_tool.py` for input device control.
  - `clipboard_tool.py` for clipboard operations.
- **Key Methods**:
  - `execute_task(prompt, context)`: Determines the type of application control task and delegates to specific handlers.
  - `_handle_terminal_command(command)`: Executes terminal commands.
  - `_handle_mouse_control(instruction)`: Manages mouse actions.
  - `_handle_keyboard_control(instruction)`: Manages keyboard inputs.
  - `_handle_clipboard_operation(instruction)`: Manages clipboard tasks.
  - `_handle_app_launch(instruction)`: Launches applications.

### Usage
To execute a terminal command, a user can request: "Run terminal command ls -l". For mouse control: "Click at 100 200". For launching an app: "Launch Safari". The `ApplicationAgent` interprets these requests and performs the actions using the underlying tools.

## Integration with MasterAgent

- **MasterAgent**: Updated in `agents/master_agent.py` to delegate browser and application control goals to specialized agents.
- **Delegation Logic**: Checks the goal content for keywords related to browser or application control and routes the task to `BrowserAgent` or `ApplicationAgent` accordingly.

## Testing

- **Unit Tests for BrowserAgent**: Existing tests ensure browser control functionality.
- **Unit Tests for ApplicationAgent**: New tests in `tests/test_application_agent.py` cover terminal commands, mouse/keyboard control, clipboard operations, and app launching.

## Performance Considerations

- **Latency**: Browser initialization and application control actions are designed to meet latency requirements (<100ms for screen/input tools).
- **Fallback Mechanisms**: Multiple automation methods ensure reliability if one method fails.

## Security Notes

- **Permission Management**: Atlas requests minimal necessary permissions for application control on macOS.
- **Input Sanitization**: All user inputs for terminal commands are sanitized to prevent injection attacks.

## Future Enhancements

- **Cross-Platform Support**: Enhance compatibility for Linux and other operating systems.
- **Advanced Application Interactions**: Develop deeper integration with specific applications for more complex automation tasks.
- **UI for Control Preferences**: Add graphical elements or CLI commands for users to specify control preferences explicitly.

For any issues or further enhancements, please refer to the development plan in `DEV_PLAN.md` under Phase 7.
