import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

try:
    import importlib.util

    PYAUTOGUI_AVAILABLE = importlib.util.find_spec("pyautogui") is not None
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning(
        "PyAutoGUI not installed. Browser interaction functionality will be limited."
    )


class EnhancedBrowser(QWidget):
    """Enhanced browser tool with cyberpunk UI and advanced features."""

    content_updated = Signal(str)
    search_completed = Signal(list)

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.initialize_ui()
        self.initialize_browser_settings()

    def initialize_ui(self) -> None:
        """Initialize the UI components with a cyberpunk aesthetic."""
        try:
            self.setWindowTitle("Atlas CyberBrowser")
            layout = QVBoxLayout(self)

            # Navigation Bar with cyberpunk styling
            self.nav_bar = QWidget()
            nav_layout = QHBoxLayout()

            self.back_btn = QPushButton("◀")
            self.back_btn.setFixedSize(40, 30)
            self.back_btn.clicked.connect(self.go_back)
            self.style_button(self.back_btn)
            nav_layout.addWidget(self.back_btn)

            self.forward_btn = QPushButton("▶")
            self.forward_btn.setFixedSize(40, 30)
            self.forward_btn.clicked.connect(self.go_forward)
            self.style_button(self.forward_btn)
            nav_layout.addWidget(self.forward_btn)

            self.reload_btn = QPushButton("⟳")
            self.reload_btn.setFixedSize(40, 30)
            self.reload_btn.clicked.connect(self.reload_page)
            self.style_button(self.reload_btn)
            nav_layout.addWidget(self.reload_btn)

            self.url_input = QLineEdit()
            self.url_input.setPlaceholderText("Enter URL or search query")
            self.url_input.returnPressed.connect(self.load_url_from_input)
            self.style_line_edit(self.url_input)
            nav_layout.addWidget(self.url_input)

            self.go_btn = QPushButton("Go")
            self.go_btn.setFixedSize(60, 30)
            self.go_btn.clicked.connect(self.load_url_from_input)
            self.style_button(self.go_btn)
            nav_layout.addWidget(self.go_btn)

            self.nav_bar.setLayout(nav_layout)
            layout.addWidget(self.nav_bar)

            # Web View
            try:
                self.web_view = QWebEngineView()
                layout.addWidget(self.web_view)
            except Exception as e:
                self.logger.error(f"Failed to initialize QWebEngineView: {str(e)}")
                self.web_view = None

            # Status Bar with cyberpunk styling
            self.status_bar = QStatusBar()
            self.status_label = QLabel("Ready")
            self.status_bar.addWidget(self.status_label)
            self.style_status_bar(self.status_bar)
            layout.addWidget(self.status_bar)

            self.setLayout(layout)
            self.apply_cyberpunk_style()
        except Exception as e:
            self.logger.error(f"Error initializing UI: {str(e)}")

    def style_button(self, button: QPushButton) -> None:
        """Apply cyberpunk style to buttons."""
        button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        font = QFont("Courier New", 10)
        font.setBold(True)
        button.setFont(font)

    def style_line_edit(self, line_edit: QLineEdit) -> None:
        """Apply cyberpunk style to line edit."""
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 0 5px;
            }
        """)
        font = QFont("Courier New", 10)
        line_edit.setFont(font)

    def style_status_bar(self, status_bar: QStatusBar) -> None:
        """Apply cyberpunk style to status bar."""
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1a1a1a;
                color: #00ffaa;
                border-top: 1px solid #00ffaa;
            }
        """)
        font = QFont("Courier New", 9)
        status_bar.setFont(font)

    def apply_cyberpunk_style(self) -> None:
        """Apply overall cyberpunk styling to the browser widget."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0a0a0a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1a1a1a"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1a1a1a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.setPalette(palette)
        self.setStyleSheet("background-color: #0a0a0a;")

    def initialize_browser_settings(self) -> None:
        """Initialize browser settings and connect signals."""
        if self.web_view is not None:
            settings = self.web_view.page().settings()
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptEnabled, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True
            )
            default_url = self.config.get("default_url", "about:blank")
            self.web_view.setUrl(QUrl(default_url))
            self.web_view.loadStarted.connect(self.on_load_started)
            self.web_view.loadProgress.connect(self.on_load_progress)
            self.web_view.loadFinished.connect(self.on_load_finished)
            self.web_view.urlChanged.connect(self.on_url_changed)

    @Slot()
    def go_back(self) -> None:
        """Navigate to the previous page."""
        if self.web_view is not None:
            self.web_view.back()
            self.logger.info("Navigating back")

    @Slot()
    def go_forward(self) -> None:
        """Navigate to the next page."""
        if self.web_view is not None:
            self.web_view.forward()
            self.logger.info("Navigating forward")

    @Slot()
    def reload_page(self) -> None:
        """Reload the current page."""
        if self.web_view is not None:
            self.web_view.reload()
            self.logger.info("Reloading page")

    @Slot()
    def load_url_from_input(self) -> None:
        """Load URL from the input field."""
        url_text = self.url_input.text().strip()
        if not url_text:
            self.logger.warning("Empty URL input")
            return

        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            url_text = f"https://{url_text}"
        url = QUrl(url_text)
        if url.isValid():
            if self.web_view is not None:
                self.web_view.setUrl(url)
                self.logger.info("Loading URL: %s", url_text)
        else:
            self.logger.error("Invalid URL: %s", url_text)
            self.status_label.setText(f"Invalid URL: {url_text}")

    @Slot()
    def on_load_started(self) -> None:
        """Handle load started event."""
        self.status_label.setText("Loading...")
        self.logger.info("Page load started")

    @Slot(int)
    def on_load_progress(self, progress: int) -> None:
        """Handle load progress event."""
        self.status_label.setText(f"Loading: {progress}%")

    @Slot(bool)
    def on_load_finished(self, ok: bool) -> None:
        """Handle load finished event."""
        if ok:
            self.status_label.setText("Loaded successfully")
            self.logger.info("Page loaded successfully")
            if self.web_view is not None:
                self.web_view.page().toHtml(self.emit_content)
        else:
            self.status_label.setText("Load failed")
            self.logger.error("Page load failed")

    @Slot(QUrl)
    def on_url_changed(self, url: QUrl) -> None:
        """Handle URL changed event."""
        url_str = url.toString()
        self.url_input.setText(url_str)
        self.logger.info("URL changed to: %s", url_str)

    @Slot(str)
    def emit_content(self, html: str) -> None:
        """Emit the page content."""
        self.content_updated.emit(html)

    def execute_javascript(self, script: str) -> None:
        """Execute JavaScript code in the current page context."""
        if self.web_view is not None:
            self.logger.info("Executing JavaScript")
            self.web_view.page().runJavaScript(script)

    def search(self, query: str) -> None:
        """Search for a query on the current page."""

        def search_callback(found: bool) -> None:
            self.search_completed.emit([found, query])

        self.logger.info("Searching for: %s", query)
        if self.web_view is not None:
            self.web_view.page().findText(query)

    def zoom_in(self) -> None:
        """Zoom in on the current page."""
        if self.web_view is not None:
            current_zoom = self.web_view.zoomFactor()
            self.web_view.setZoomFactor(current_zoom + 0.1)
            self.logger.info("Zooming in, new factor: %.1f", current_zoom + 0.1)

    def zoom_out(self) -> None:
        """Zoom out on the current page."""
        if self.web_view is not None:
            current_zoom = self.web_view.zoomFactor()
            self.web_view.setZoomFactor(current_zoom - 0.1)
            self.logger.info("Zooming out, new factor: %.1f", current_zoom - 0.1)

    def reset_zoom(self) -> None:
        """Reset zoom to default level."""
        if self.web_view is not None:
            self.web_view.setZoomFactor(1.0)
            self.logger.info("Zoom reset to default")

    def load_url(self, url: str) -> bool:
        """Load a URL in the browser.

        Args:
            url (str): The URL to load.

        Returns:
            bool: True if the URL was loaded successfully, False otherwise.
        """
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        try:
            if self.web_view is not None:
                self.web_view.load(QUrl(url))
                self.url_input.setText(url)
                self.logger.info(f"Loading URL: {url}")
                return True
            else:
                self.logger.error("Web view not initialized. Cannot load URL.")
                return False
        except Exception as e:
            self.logger.error(f"Failed to load URL {url}: {str(e)}")
            return False

    def interact_with_element(
        self, selector: str, action: str, text: Optional[str] = None
    ) -> bool:
        """Interact with a web element using the specified action.

        Args:
            selector (str): CSS selector for the target element.
            action (str): Action to perform (click, type, hover).
            text (str, optional): Text to input if action is 'type'. Defaults to None.

        Returns:
            bool: True if interaction was successful, False otherwise.
        """
        if not PYAUTOGUI_AVAILABLE and action in ["click", "type", "hover"]:
            logging.error(
                "PyAutoGUI not installed. Cannot perform browser interactions."
            )
            return False
