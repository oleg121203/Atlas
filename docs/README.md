# Atlas – Autonomous Computer Agent

Atlas is a macOS-native Python application that uses Large Language Models (LLMs) to reason about and interact with the computer's screen, keyboard, and mouse, automating complex tasks by mimicking human behavior.

## Features

*   **Modern GUI**: A sleek, theme-aware interface built with CustomTkinter.
*   **LLM Orchestration**: Supports local models via Ollama and external providers like OpenAI, with configurable fallback chains.
*   **Core Computer-Interaction Tools**: A suite of tools for screen capture, OCR, image recognition, mouse/keyboard control, clipboard access, and terminal commands.
*   **Advanced Agent Framework**: A multi-agent system, led by a `MasterAgent`, that can generate and execute complex plans.
*   **Real-time Security & Monitoring**: A `SecurityAgent` enforces user-defined rules in real-time, while a `DeputyAgent` monitors for errors.

## Architecture

Atlas operates on a multi-agent architecture:

1.  **Master Agent**: The central coordinator that receives user goals, generates a step-by-step plan using an LLM, and delegates tasks.
2.  **Specialized Agents**: Each agent is an expert in a specific domain (e.g., `ScreenAgent`, `BrowserAgent`, `TextAgent`) and executes tasks using the core tools.
3.  **Monitoring Agents**: The `SecurityAgent` and `DeputyAgent` run in the background to ensure safe and reliable operation.

This modular design allows for clear separation of concerns and makes the system highly extensible.

## Getting Started

### Prerequisites

*   macOS
*   Python 3.9+
*   Xcode Command Line Tools (for `git` and other build dependencies)

### Running from Source

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd autoclicker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv atlas_env
    source atlas_env/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    python3 -m pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python3 main.py
    ```

## Building the Application

Atlas is packaged into a standalone macOS application (`.app`) using `pyinstaller`.

1.  **Install build dependencies:**
    ```bash
    python3 -m pip install pyinstaller
    ```

2.  **Run the build command from the project root:**
    ```bash
    python3 -m PyInstaller main.py --windowed --name Atlas
    ```
    *Note: If you have a custom icon, you can add it with `--icon=path/to/icon.icns`.*

3.  **Find the application bundle** in the `dist/` directory: `dist/Atlas.app`.

## Troubleshooting

*   **`command not found: pip` or `command not found: pyinstaller`**: Your shell's `PATH` may not include Python's `bin` directory. Use `python3 -m pip` and `python3 -m PyInstaller` to ensure you're using the executables from your active Python environment.
*   **Permissions Errors on macOS**: The first time you run Atlas, macOS will prompt you to grant permissions for **Accessibility** and **Screen Recording**. These are required for the mouse, keyboard, and screenshot tools to function. If you deny them, you can grant them later in `System Settings > Privacy & Security`.
*   **Build Failures**: This project previously used `py2app`, which struggled with namespace packages like `rubicon-objc`. The switch to `pyinstaller` has made the build process much more reliable.
