"""Theme Manager component for Atlas."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot


class ThemeManager(QObject):
    """Manager for handling themes in Atlas with support for cyberpunk styling."""

    theme_changed = Signal(str)
    themes_updated = Signal(list)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.themes_directory = os.path.join(os.path.dirname(__file__), "themes")
        self.current_theme = "default"
        self.available_themes: List[str] = []
        self.theme_data: Dict[str, Dict[str, Any]] = {}
        self.initialize_themes()
        self.logger.info("ThemeManager initialized")

    def initialize_themes(self) -> None:
        """Initialize available themes from the themes directory."""
        if not os.path.exists(self.themes_directory):
            os.makedirs(self.themes_directory)
            self.logger.info(f"Created themes directory: {self.themes_directory}")

        # Default theme as fallback
        default_theme = {
            "name": "Default Cyberpunk",
            "stylesheet": """
                QWidget {
                    background-color: #0a0a0a;
                    color: #00ffaa;
                }
                QPushButton {
                    background-color: #1a1a1a;
                    color: #00ffaa;
                    border: 1px solid #00ffaa;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #00ffaa;
                    color: #000000;
                }
            """,
            "icon_set": "default",
        }
        self.theme_data["default"] = default_theme
        self.available_themes.append("default")

        # Load themes from JSON files in the themes directory
        for filename in os.listdir(self.themes_directory):
            if filename.endswith(".json"):
                theme_id = filename[:-5]
                theme_path = os.path.join(self.themes_directory, filename)
                try:
                    with open(theme_path, "r", encoding="utf-8") as f:
                        theme_info = json.load(f)
                        self.theme_data[theme_id] = theme_info
                        self.available_themes.append(theme_id)
                        self.logger.debug(f"Loaded theme: {theme_id}")
                except Exception as e:
                    self.logger.error(f"Failed to load theme {theme_id}: {str(e)}")

        self.themes_updated.emit(self.available_themes)
        self.logger.info(f"Initialized {len(self.available_themes)} themes")

    def get_current_theme(self) -> str:
        """Get the ID of the current theme.

        Returns:
            str: The ID of the current theme.
        """
        return self.current_theme

    def get_theme_stylesheet(self, theme_id: Optional[str] = None) -> str:
        """Get the stylesheet for a specific theme.

        Args:
            theme_id (Optional[str]): The ID of the theme. Defaults to current theme.

        Returns:
            str: The stylesheet content for the theme.
        """
        if theme_id is None:
            theme_id = self.current_theme
        theme = self.theme_data.get(theme_id, self.theme_data["default"])
        return theme.get("stylesheet", "")

    def get_theme_icon_set(self, theme_id: Optional[str] = None) -> str:
        """Get the icon set for a specific theme.

        Args:
            theme_id (Optional[str]): The ID of the theme. Defaults to current theme.

        Returns:
            str: The icon set identifier for the theme.
        """
        if theme_id is None:
            theme_id = self.current_theme
        theme = self.theme_data.get(theme_id, self.theme_data["default"])
        return theme.get("icon_set", "default")

    def get_theme_info(self, theme_id: Optional[str] = None) -> Dict[str, Any]:
        """Get full information about a specific theme.

        Args:
            theme_id (Optional[str]): The ID of the theme. Defaults to current theme.

        Returns:
            Dict[str, Any]: Dictionary containing theme information.
        """
        if theme_id is None:
            theme_id = self.current_theme
        return self.theme_data.get(theme_id, self.theme_data["default"])

    def get_available_themes(self) -> List[str]:
        """Get a list of available theme IDs.

        Returns:
            List[str]: List of theme IDs.
        """
        return self.available_themes

    @Slot(str)
    def apply_theme(self, theme_id: str) -> None:
        """Apply a theme by ID.

        Args:
            theme_id (str): The ID of the theme to apply.
        """
        if theme_id in self.theme_data:
            self.current_theme = theme_id
            self.theme_changed.emit(theme_id)
            self.logger.info(f"Applied theme: {theme_id}")
        else:
            self.logger.warning(f"Theme not found: {theme_id}")
