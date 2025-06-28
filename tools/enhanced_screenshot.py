"""Enhanced Screenshot Tool for Atlas."""

import logging
import os
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    import importlib.util

    PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None
except ImportError:
    PILLOW_AVAILABLE = False
    logging.warning("Pillow not installed. Screenshot functionality will be limited.")


class EnhancedScreenshot(QWidget):
    """An enhanced screenshot tool for Atlas with advanced capture and annotation capabilities."""

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.screenshots: List[str] = []
        self.init_ui()
        self.initialize()

    def init_ui(self) -> None:
        """Initialize the UI components for the screenshot tool."""
        layout = QVBoxLayout(self)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(
            "background-color: #1a1a1a; border: 1px solid #00ffaa; min-height: 300px;"
        )
        layout.addWidget(self.preview_label)

        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Capture Screen")
        self.capture_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.capture_button.clicked.connect(self.capture_screenshot)
        button_layout.addWidget(self.capture_button)

        self.save_button = QPushButton("Save Screenshot")
        self.save_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.save_button.clicked.connect(self.save_screenshot)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.screenshot_list = QListWidget()
        self.screenshot_list.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; border: 1px solid #00ffaa;"
        )
        self.screenshot_list.itemClicked.connect(self.display_screenshot)
        layout.addWidget(self.screenshot_list)

        self.setLayout(layout)

    def initialize(self) -> None:
        """Initialize the screenshot tool settings and configurations."""
        self.logger.info("Initializing Enhanced Screenshot Tool")
        self.screenshot_dir = self.config.get(
            "screenshot_dir", os.path.expanduser("~/Screenshots")
        )
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        self.logger.info("Screenshot directory set to: %s", self.screenshot_dir)

    def capture_screenshot(self) -> None:
        """Capture a screenshot of the entire screen."""
        if not PILLOW_AVAILABLE:
            logging.error("Pillow not installed. Cannot capture screenshot.")
            return
        self.logger.info("Capturing screenshot")
        try:
            from PySide6.QtGui import QGuiApplication

            screen = QGuiApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            screenshot_path = os.path.join(
                self.screenshot_dir, f"screenshot_{len(self.screenshots)}.png"
            )
            screenshot.save(screenshot_path)
            self.screenshots.append(screenshot_path)
            self.screenshot_list.addItem(os.path.basename(screenshot_path))
            self.preview_label.setPixmap(
                screenshot.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.logger.info("Screenshot captured and saved to: %s", screenshot_path)
        except Exception as e:
            self.logger.error("Failed to capture screenshot: %s", e)

    def save_screenshot(self) -> None:
        """Save the latest screenshot to a user-specified location."""
        if not self.screenshots:
            self.logger.warning("No screenshots to save")
            return

        latest_screenshot = self.screenshots[-1]
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", latest_screenshot, "Images (*.png *.jpg *.bmp)"
        )
        if save_path:
            try:
                os.rename(latest_screenshot, save_path)
                self.screenshots[-1] = save_path
                self.screenshot_list.takeItem(self.screenshot_list.count() - 1)
                self.screenshot_list.addItem(os.path.basename(save_path))
                self.logger.info("Screenshot saved to: %s", save_path)
            except Exception as e:
                self.logger.error("Failed to save screenshot: %s", e)

    def display_screenshot(self, item) -> None:
        """Display the selected screenshot in the preview area."""
        index = self.screenshot_list.row(item)
        if index >= 0 and index < len(self.screenshots):
            screenshot_path = self.screenshots[index]
            pixmap = QPixmap(screenshot_path)
            self.preview_label.setPixmap(
                pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.logger.debug("Displaying screenshot: %s", screenshot_path)
