# Atlas Plugin Development Guide

## Introduction

Welcome to the Atlas Plugin Development Guide. Atlas is a modern, modular AI platform with a cyberpunk design, built for extensibility through plugins and tools. This guide provides detailed instructions on how to create, test, and distribute plugins for the Atlas application.

Plugins in Atlas allow developers to extend the functionality of the core application. They can integrate with various modules such as Chat, Tasks, Agents, and more, providing custom features and tools to enhance user experience.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:
- **Python 3.9+**: Atlas is built with Python, so you'll need a compatible version installed.
- **Atlas Source Code**: Clone the Atlas repository or download the source code to understand the structure and test your plugins locally.
- **Development Environment**: Set up a virtual environment for Python to manage dependencies.

### Setting Up Your Development Environment

1. **Clone the Atlas Repository**:
   ```bash
   git clone https://github.com/oleg121203/Atlas.git
   cd Atlas
   ```

2. **Create and Activate a Virtual Environment**:
   - For macOS/Linux:
     ```bash
     python3 -m venv venv-macos
     source venv-macos/bin/activate
     ```
   - For Windows:
     ```bash
     python -m venv venv-windows
     venv-windows\Scripts\activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install PySide6 qdarkstyle markdown2
   ```

## Plugin Basics

### Plugin Structure

A typical Atlas plugin is a directory within the `plugins/` folder of the Atlas project. Each plugin should have the following structure:

```
plugins/
  my_plugin/
    __init__.py
    manifest.json
    main.py
    resources/ (optional)
```

- **`__init__.py`**: Marks the directory as a Python package.
- **`manifest.json`**: Contains metadata about the plugin, including name, version, dependencies, and entry points.
- **`main.py`**: The main entry point for your plugin's logic.
- **`resources/`**: Optional directory for storing icons, images, or other assets used by your plugin.

### Creating Your First Plugin

Let's create a simple plugin called `HelloWorldPlugin` that adds a custom tool to the Chat module.

1. **Create the Plugin Directory**:
   ```bash
   mkdir -p plugins/hello_world
   ```

2. **Create `manifest.json`**:
   ```json
   {
     "name": "HelloWorldPlugin",
     "version": "1.0.0",
     "description": "A simple plugin that adds a Hello World tool to the Chat module.",
     "author": "Your Name",
     "dependencies": {},
     "entry_points": {
       "chat_tool": "hello_world.main:HelloWorldTool"
     }
   }
   ```

3. **Create `main.py`**:
   ```python
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

   class HelloWorldTool(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.init_ui()

       def init_ui(self):
           layout = QVBoxLayout(self)
           label = QLabel("Hello, World!", self)
           button = QPushButton("Say Hello", self)
           button.clicked.connect(lambda: label.setText("Hello from Atlas!"))
           layout.addWidget(label)
           layout.addWidget(button)
           self.setLayout(layout)

       @staticmethod
       def get_widget():
           return HelloWorldTool
   ```

4. **Test Your Plugin**:
   - Start the Atlas application:
     ```bash
     python main.py
     ```
   - Navigate to the Plugins module, enable your plugin, and check the Chat module to see your tool in action.

## Advanced Plugin Development

### Interacting with Atlas Modules

Plugins can interact with various Atlas modules through defined APIs. For example, to interact with the Chat module, you can emit signals or call methods provided by the `ChatModule` class.

### Handling Dependencies

If your plugin depends on other plugins, specify them in the `dependencies` field of your `manifest.json`. For example:

```json
"dependencies": {
  "AnotherPlugin": ">=1.0.0"
}
```

Atlas will ensure that dependencies are met before enabling your plugin.

### Version Control

Use semantic versioning (e.g., `1.0.0`) for your plugin to ensure compatibility and update management within the Atlas ecosystem.

## Testing Your Plugin

### Writing Tests

Create unit tests for your plugin to ensure reliability. Place your tests in a `tests/` directory within your plugin folder. Use the `unittest` framework and mock dependencies as needed.

### Running Tests

Run your tests with:
```bash
python -m unittest discover plugins/my_plugin/tests
```

## Distributing Your Plugin

### Packaging

Package your plugin as a zip file or a Python package for distribution. Ensure all necessary files (`__init__.py`, `manifest.json`, `main.py`, etc.) are included.

### Submitting to the Atlas Marketplace

Once the Atlas Marketplace is fully implemented, you'll be able to submit your plugin for review and inclusion. Follow the submission guidelines provided in the marketplace documentation.

## Best Practices

- **Modularity**: Keep your plugin focused on a single feature or functionality.
- **Documentation**: Provide clear documentation within your plugin for users and developers.
- **Error Handling**: Implement robust error handling to prevent crashes in the main application.
- **Security**: Avoid executing untrusted code and sanitize all inputs.

## Troubleshooting

- **Plugin Not Loading**: Check `manifest.json` for syntax errors or missing fields. Ensure your entry point class and method exist.
- **Dependency Issues**: Verify that all dependencies are installed and meet version requirements.
- **UI Issues**: Ensure your widgets are compatible with PySide6 and follow Qt best practices.

## Additional Resources

- **Atlas GitHub Repository**: [https://github.com/oleg121203/Atlas](https://github.com/oleg121203/Atlas)
- **PySide6 Documentation**: [https://doc.qt.io/qtforpython/](https://doc.qt.io/qtforpython/)
- **Python Documentation**: [https://docs.python.org/3/](https://docs.python.org/3/)

---

*This guide will be updated as new features and capabilities are added to the Atlas plugin system.*
