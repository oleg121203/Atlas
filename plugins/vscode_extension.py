"""
VS Code Extension for Atlas

This module provides integration with Visual Studio Code, allowing developers to manage Atlas projects,
view context data, and trigger intelligence operations directly from the IDE.
"""
import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class VSCodeExtension:
    """Manages integration with Visual Studio Code for Atlas."""

    def __init__(self, atlas_root_path: str):
        """Initialize the VS Code extension with the root path of Atlas.

        Args:
            atlas_root_path: The root directory path of the Atlas project.
        """
        self.atlas_root_path = atlas_root_path
        self.extension_name = "atlas-vscode-extension"
        self.extension_path = os.path.join(atlas_root_path, "plugins", "vscode", self.extension_name)
        self.package_json_path = os.path.join(self.extension_path, "package.json")
        self.is_initialized = False
        logger.info(f"VS Code Extension initialized with root path: {atlas_root_path}")

    def initialize(self) -> bool:
        """Initialize the VS Code extension by setting up necessary directories and files.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # Create extension directory if it doesn't exist
            os.makedirs(self.extension_path, exist_ok=True)

            # Create or update package.json for the extension
            self._create_package_json()

            # Create basic extension structure
            self._create_extension_structure()

            self.is_initialized = True
            logger.info("VS Code Extension for Atlas initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize VS Code Extension: {e}")
            return False

    def _create_package_json(self):
        """Create or update the package.json file for the VS Code extension."""
        package_data = {
            "name": self.extension_name,
            "displayName": "Atlas AI Integration",
            "description": "Integrates Atlas AI platform with VS Code for project management and "
                           "intelligence operations.",
            "version": "0.1.0",
            "engines": {
                "vscode": "^1.80.0"
            },
            "categories": [
                "AI",
                "Programming Languages",
                "Other"
            ],
            "activationEvents": [
                "onStartupFinished"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "atlas.connect",
                        "title": "Atlas: Connect to Project"
                    },
                    {
                        "command": "atlas.viewContext",
                        "title": "Atlas: View Context Data"
                    },
                    {
                        "command": "atlas.triggerDecision",
                        "title": "Atlas: Trigger Decision"
                    }
                ],
                "viewsContainers": {
                    "activitybar": [
                        {
                            "id": "atlas-sidebar",
                            "title": "Atlas AI",
                            "icon": "media/atlas.svg"
                        }
                    ]
                },
                "views": {
                    "atlas-sidebar": [
                        {
                            "id": "atlasContextView",
                            "name": "Context Data"
                        },
                        {
                            "id": "atlasIntelligenceView",
                            "name": "Intelligence Operations"
                        }
                    ]
                }
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc --watch -p ./"
            },
            "devDependencies": {
                "@types/node": "^18.15.11",
                "@types/vscode": "^1.80.0",
                "typescript": "^5.0.4"
            }
        }

        with open(self.package_json_path, "w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)
        logger.info(f"Created/Updated package.json at {self.package_json_path}")

    def _create_extension_structure(self):
        """Create the basic directory structure and placeholder files for the VS Code extension."""
        # Create source directory
        src_path = os.path.join(self.extension_path, "src")
        os.makedirs(src_path, exist_ok=True)

        # Create media directory for icons
        media_path = os.path.join(self.extension_path, "media")
        os.makedirs(media_path, exist_ok=True)

        # Create output directory for compiled files
        out_path = os.path.join(self.extension_path, "out")
        os.makedirs(out_path, exist_ok=True)

        # Create placeholder extension.ts file
        extension_ts_content = """import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Atlas AI Integration extension is now active!');

    // Command: Connect to Atlas Project
    let connectCommand = vscode.commands.registerCommand('atlas.connect', () => {
        vscode.window.showInformationMessage('Connecting to Atlas Project...');
        // TODO: Implement connection logic
    });
    context.subscriptions.push(connectCommand);

    // Command: View Context Data
    let viewContextCommand = vscode.commands.registerCommand('atlas.viewContext', () => {
        vscode.window.showInformationMessage('Fetching Atlas Context Data...');
        // TODO: Implement context data retrieval
    });
    context.subscriptions.push(viewContextCommand);

    // Command: Trigger Decision
    let triggerDecisionCommand = vscode.commands.registerCommand('atlas.triggerDecision', () => {
        vscode.window.showInformationMessage('Triggering Atlas Decision...');
        // TODO: Implement decision triggering logic
    });
    context.subscriptions.push(triggerDecisionCommand);
}

export function deactivate() {
    console.log('Atlas AI Integration extension deactivated.');
}
"""
        with open(os.path.join(src_path, "extension.ts"), "w", encoding="utf-8") as f:
            f.write(extension_ts_content)

        # Create tsconfig.json
        tsconfig_content = {
            "compilerOptions": {
                "target": "es2020",
                "module": "commonjs",
                "lib": ["es2020"],
                "outDir": "./out",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            }
        }
        with open(os.path.join(self.extension_path, "tsconfig.json"), "w", encoding="utf-8") as f:
            json.dump(tsconfig_content, f, indent=2)

        logger.info(f"Created basic VS Code extension structure at {self.extension_path}")

    def install_extension(self) -> bool:
        """Install the extension to VS Code for testing.

        Returns:
            bool: True if installation is successful, False otherwise.
        """
        if not self.is_initialized:
            logger.error("Extension not initialized. Call initialize() first.")
            return False

        try:
            # Compile TypeScript to JavaScript
            compile_cmd = ["npm", "run", "compile"]
            subprocess.run(compile_cmd, cwd=self.extension_path, check=True, capture_output=True, text=True)
            logger.info("Extension compiled successfully.")

            # Install the extension using vsce (VS Code Extension CLI)
            install_cmd = ["vsce", "package"]
            subprocess.run(install_cmd, cwd=self.extension_path, check=True, capture_output=True, text=True)
            logger.info("Extension packaged successfully.")

            vsix_file = f"{self.extension_name}-0.1.0.vsix"
            vsix_path = os.path.join(self.extension_path, vsix_file)
            if os.path.exists(vsix_path):
                install_vsix_cmd = ["code", "--install-extension", vsix_path]
                subprocess.run(install_vsix_cmd, check=True, capture_output=True, text=True)
                logger.info("VS Code Extension for Atlas installed successfully.")
                return True
            else:
                logger.error(f"VSIX file not found at {vsix_path}")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install VS Code Extension: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during extension installation: {e}")
            return False

    def connect_to_project(self) -> bool:
        """Simulate connecting to an Atlas project from VS Code.

        Returns:
            bool: True if connection is successful (mocked), False otherwise.
        """
        if not self.is_initialized:
            logger.error("Extension not initialized. Call initialize() first.")
            return False

        logger.info("Connecting to Atlas project from VS Code...")
        # TODO: Implement actual connection logic to Atlas backend
        logger.info("Connected to Atlas project (mocked).")
        return True

    def view_context_data(self) -> Optional[Dict[str, Any]]:
        """Retrieve and return context data from Atlas (mocked).

        Returns:
            Optional[Dict[str, Any]]: Mocked context data if successful, None otherwise.
        """
        if not self.is_initialized:
            logger.error("Extension not initialized. Call initialize() first.")
            return None

        logger.info("Fetching context data from Atlas...")
        # TODO: Implement actual context data retrieval from ContextEngine
        mock_context_data = {
            "environmental": {"time_of_day": "afternoon", "location": "office"},
            "user": {"activity_level": "moderate", "preferences": {"theme": "dark"}},
            "system": {"cpu_usage": 0.5, "memory_usage": 0.7}
        }
        logger.info("Context data retrieved (mocked).")
        return mock_context_data

    def trigger_decision(self, goal: str) -> Optional[Dict[str, Any]]:
        """Trigger a decision-making process in Atlas (mocked).

        Args:
            goal: The goal for the decision-making process.

        Returns:
            Optional[Dict[str, Any]]: Mocked decision result if successful, None otherwise.
        """
        if not self.is_initialized:
            logger.error("Extension not initialized. Call initialize() first.")
            return None

        logger.info(f"Triggering decision for goal: {goal}")
        # TODO: Implement actual decision triggering with DecisionEngine
        mock_decision = {
            "goal": goal,
            "decision": f"Recommended action for {goal}",
            "confidence": 0.85
        }
        logger.info(f"Decision triggered (mocked): {mock_decision['decision']}")
        return mock_decision


if __name__ == "__main__":
    # Example usage
    atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vscode_ext = VSCodeExtension(atlas_root)
    if vscode_ext.initialize():
        vscode_ext.connect_to_project()
        context_data = vscode_ext.view_context_data()
        if context_data:
            logger.info(f"Context Data: {context_data}")
        decision_result = vscode_ext.trigger_decision("Optimize workflow")
        if decision_result:
            logger.info(f"Decision Result: {decision_result}")
        # Uncomment to attempt installation (requires vsce and code CLI)
        # vscode_ext.install_extension()
