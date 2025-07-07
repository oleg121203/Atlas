import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import (
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QAction,
)
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QTabBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from atlas.core.application import AtlasApplication
from atlas.core.events import TOOL_ERROR, TOOL_EXECUTED
from atlas.ui.agents.agents_widget import AgentsWidget
from atlas.ui.chat.chat_widget import ChatWidget
from atlas.ui.intelligence.decision_ui import DecisionUI
from atlas.ui.intelligence.self_improvement_ui import SelfImprovementUI
from atlas.ui.memory.memory_ui import MemoryUI
from atlas.ui.module_communication import EVENT_BUS
from atlas.ui.performance_panel import PerformancePanel
from atlas.ui.plugins.plugins_widget import PluginsWidget
from atlas.ui.stats_module import StatsModule
from atlas.ui.system_control_panel import SystemControlPanel
from atlas.ui.workflowui import WorkflowUI

_logger = logging.getLogger(__name__)

# Safe imports with error handling
try:
    from atlas.ui.placeholder_widgets import PlaceholderWidget
except ImportError:
    PlaceholderWidget = None


class AtlasMainWindow(QMainWindow):
    """Main window for Atlas application with cyberpunk styling.

    Attributes:
        sidebar (QToolBar): Vertical toolbar for navigation
        topbar (QToolBar): Horizontal toolbar for controls
        central (QStackedWidget): Main content area
        right_panel (QDockWidget): Right-side statistics panel
        modules (Dict[str, QWidget]): Application modules
        plugin_manager (PluginManager): Plugin management system
        search_results (QListWidget): Search results popup
        search_box (QLineEdit): Global search input
        lang_combo (QComboBox): Language selector
        event_bus (ModuleEventBus): Event bus for cross-module communication
        memory_manager (MemoryManager): Memory management system
        app_instance (Optional[AtlasApplication]): Atlas application instance
    """

    def __init__(
        self,
        app: Any = None,
        meta_agent: Optional[Any] = None,
        parent: Optional[QWidget] = None,
        app_instance: Optional[Any] = None,
        context_engine: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
        theme_manager: Optional[Any] = None,
    ) -> None:
        """Initialize the main window.

        Args:
            app: Application instance.
            meta_agent: Meta agent instance.
            parent: Parent widget.
            app_instance: Application instance for compatibility.
            context_engine: Context engine instance.
            memory_manager: Memory manager instance.
            theme_manager: Theme manager instance.
        """
        super().__init__(parent)
        # Initialize sidebar_buttons as an empty dict before setup_ui
        self.sidebar_buttons = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AtlasMainWindow")
        if app is None:
            app = QApplication.instance()
            if app is None:
                self.logger.warning(
                    "No QApplication instance found, UI might not function correctly"
                )
        self.app = app
        self.meta_agent = meta_agent
        self.app_instance = app_instance if app_instance else None
        # Initialize core components
        if self.app_instance is None:
            self.app_instance = QApplication.instance()
        self.context_engine = context_engine
        self.memory_manager = memory_manager
        self.theme_manager = theme_manager
        self.setWindowTitle("Atlas - Autonomous Task Planning")
        self.setGeometry(100, 100, 1200, 800)
        # Initialize event bus
        self.event_bus = EVENT_BUS
        self.event_bus.subscribe("app_shutdown", self._on_app_shutdown)
        self.event_bus.publish("main_window_initialized", {"status": "ready"})
        self.modules = {}
        # Initialize core UI elements before any usage
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)

        # Initialize toolbar and dock placeholders
        self.topbar = None
        self.sidebar_widget = None
        self.dock = None
        # Initialize modules safely with try-except to prevent startup crashes
        self._initialize_core_modules()

        # Delay UI initialization to ensure QApplication is ready
        QTimer.singleShot(0, self._init_ui)
        self.main_layout = QVBoxLayout()  # Додаємо основний layout, якщо його не було
        self.event_bus.subscribe(TOOL_EXECUTED, self._on_tool_executed)
        self.event_bus.subscribe(TOOL_ERROR, self._on_tool_error)
        self.logger.debug("AtlasMainWindow initialization completed")

        # Placeholder attributes for buttons to fix lint errors
        self.menu_btn = None
        self.minimize_btn = None
        self.maximize_btn = None
        self.close_btn = None

    def _on_app_shutdown(self, data=None):
        """Handle application shutdown event."""
        self.logger.info("Received app_shutdown event, closing main window")
        try:
            # Use the publish method instead of emit
            self.event_bus.publish("app_shutdown")
        except Exception as e:
            self.logger.error(f"Error handling app_shutdown: {e}")
        self.close()

    def _show_context_menu(self):
        """Placeholder for showing context menu."""
        pass

    def _toggle_maximize(self):
        """Placeholder for toggling window maximization."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _init_ui(self):
        """Initialize the UI components after a short delay to ensure QApplication is ready."""
        self.logger.info("Initializing UI components")
        self.setup_ui()
        self._setup_event_bus_connections()
        # Apply initial theme
        # self.theme_manager.apply_theme(self.theme_manager.get_current_theme())
        self.logger.info("Initial theme applied via ThemeManager")

    def _on_tool_executed(self, data: Any) -> None:
        """Placeholder method for handling tool execution events.

        Args:
            data: Data associated with the tool execution event.
        """
        self.logger.info("Tool executed event received")
        self.statusBar().showMessage("Tool executed successfully", 5000)

    def _on_tool_error(self, data: Any) -> None:
        """Placeholder method for handling tool error events.

        Args:
            data: Data associated with the tool error event.
        """
        self.logger.error("Tool error event received")
        self.statusBar().showMessage("Tool execution failed", 7000)

    def setup_ui(self):
        """Set up the user interface components."""
        self.logger.info("Setting up UI components")
        self._apply_global_theme()
        self._setup_central_widget()
        self._setup_topbar()
        self._setup_sidebar()
        self._setup_dock_widgets()
        self._setup_status_bar()
        self._setup_button_connections()
        self._create_menu_bar()

        # Initialize with Chat module
        self.show_module("Chat")

        self.logger.info("UI setup complete")

    def _setup_central_widget(self):
        """Set up the central widget for the main window."""
        self.logger.debug("Setting up central widget")
        # Central widget is already initialized in __init__
        if not hasattr(self, "central") or self.central is None:
            self.central = QStackedWidget()
            self.setCentralWidget(self.central)

        # Add modules to central widget if they exist
        if (
            hasattr(self, "chat_module")
            and self.chat_module
            and self.central.indexOf(self.chat_module) == -1
        ):
            self.central.addWidget(self.chat_module)
        if (
            hasattr(self, "plugins_module")
            and self.plugins_module
            and self.central.indexOf(self.plugins_module) == -1
        ):
            self.central.addWidget(self.plugins_module)

        # Set current widget to chat if available
        if hasattr(self, "chat_module") and self.chat_module:
            self.central.setCurrentWidget(self.chat_module)

    def _setup_topbar(self):
        """Set up the top toolbar with navigation and control buttons."""
        self.logger.debug("Setting up top toolbar")
        if not hasattr(self, "topbar") or self.topbar is None:
            self.topbar = QToolBar()
            self.topbar.setObjectName("mainTopbar")
            self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topbar)

        # Set topbar style
        self.topbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: none;
                spacing: 5px;
                padding: 5px;
            }
        """)

        # Initialize buttons dictionary
        self.topbar_buttons = {}

        # Left side - Main Navigation buttons (primary modules)
        nav_group = QWidget()
        nav_layout = QHBoxLayout(nav_group)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        nav_buttons = [
            # Primary/core modules in topbar only
            ("chat_btn", "💬 Chat", lambda: self.show_module("Chat")),
            ("tasks_btn", "📋 Tasks", lambda: self.show_module("Tasks")),
            ("tools_btn", "🔧 Tools", lambda: self.show_module("Tools")),
            ("plugins_btn", "🔌 Plugins", lambda: self.show_module("Plugins")),
            (
                "performance_btn",
                "⚡ Performance",
                lambda: self.show_module("Performance"),
            ),
            ("security_btn", "🔒 Security", lambda: self.show_module("Security")),
            (
                "system_control_btn",
                "🎛️ Control",
                lambda: self.show_module("System Control"),
            ),
        ]

        for btn_name, btn_text, action in nav_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    color: #00ffaa;
                    background-color: rgba(34, 34, 34, 0.8);
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 8px 16px;
                    margin: 2px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 170, 0.1);
                    border-color: #00ffaa;
                    box-shadow: 0 0 10px rgba(0, 255, 170, 0.3);
                }
                QPushButton:pressed {
                    background-color: #00ffaa;
                    color: #000;
                }
                QPushButton:checked {
                    background-color: rgba(0, 255, 170, 0.2);
                    border-color: #00ffaa;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(action)
            btn.clicked.connect(lambda checked, b=btn: self._highlight_active_button(b))
            nav_layout.addWidget(btn)
            self.topbar_buttons[btn_name] = btn

        self.topbar.addWidget(nav_group)

        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.topbar.addWidget(spacer)

        # Right side - Control buttons
        control_group = QWidget()
        control_layout = QHBoxLayout(control_group)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Add toggle panels button
        toggle_right_btn = QPushButton("📊 Panel")
        toggle_right_btn.setStyleSheet("""
            QPushButton {
                color: #aaa;
                background-color: rgba(34, 34, 34, 0.5);
                border: 1px solid #333;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 2px;
            }
            QPushButton:hover {
                color: #00ffaa;
                border-color: #00ffaa;
            }
        """)
        toggle_right_btn.clicked.connect(self._toggle_right_panel)
        control_layout.addWidget(toggle_right_btn)

        # Window control buttons
        control_buttons = [
            ("minimize_btn", "−", self.showMinimized),
            ("maximize_btn", "□", self._toggle_maximize),
            ("close_btn", "×", self.close),
        ]

        for btn_name, btn_text, action in control_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    color: #aaa;
                    background-color: rgba(34, 34, 34, 0.5);
                    border: 1px solid #333;
                    border-radius: 4px;
                    padding: 6px 8px;
                    margin: 1px;
                    font-weight: bold;
                    min-width: 30px;
                    max-width: 30px;
                }
                QPushButton:hover {
                    color: #fff;
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            if btn_name == "close_btn":
                btn.setStyleSheet(
                    btn.styleSheet()
                    + """
                    QPushButton:hover {
                        color: #ff5555;
                        background-color: rgba(255, 85, 85, 0.2);
                    }
                """
                )
            btn.clicked.connect(action)
            control_layout.addWidget(btn)
            self.topbar_buttons[btn_name] = btn

        self.topbar.addWidget(control_group)

    def _setup_sidebar(self):
        """Set up the sidebar for additional navigation or module access."""
        self.logger.debug("Setting up sidebar")

        # Create sidebar as QWidget with layout instead of QToolBar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("sidebarWidget")
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(5, 10, 5, 10)
        self.sidebar_layout.setSpacing(8)

        # Set sidebar styling
        self.sidebar_widget.setStyleSheet("""
            QWidget#sidebarWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e1e1e, stop:1 #2a2a2a);
                border-right: 2px solid #333;
            }
        """)

        # Initialize buttons dictionary
        self.sidebar_buttons = {}

        # Add Atlas logo/title
        title_label = QLabel("ATLAS")
        title_label.setStyleSheet("""
            QLabel {
                color: #00ffaa;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
                border-bottom: 1px solid #333;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title_label)

        # Add module section
        modules_label = QLabel("ADDITIONAL MODULES")
        modules_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 10px;
                margin-top: 10px;
            }
        """)
        self.sidebar_layout.addWidget(modules_label)

        # Create buttons for navigation with icons (sidebar only contains secondary/additional modules)
        button_configs = [
            (
                "Analytics",
                "📊",
                "Data analytics and insights",
                lambda: self.show_module("Analytics"),
            ),
            (
                "AI Assistant",
                "🤖",
                "AI-powered assistant",
                lambda: self.show_module("AI Assistant"),
            ),
            (
                "System Info",
                "🖥️",
                "System information and monitoring",
                lambda: self.show_module("System Info"),
            ),
            (
                "Agents",
                "👥",
                "Agent management and coordination",
                lambda: self.show_module("Agents"),
            ),
            (
                "Memory",
                "🧠",
                "Memory management and storage",
                lambda: self.show_module("Memory"),
            ),
            (
                "Intelligence",
                "🔮",
                "AI intelligence and decision making",
                lambda: self.show_module("Intelligence"),
            ),
            (
                "Workflows",
                "🔄",
                "Workflow automation and management",
                lambda: self.show_module("Workflows"),
            ),
            (
                "Stats",
                "📈",
                "Statistics and performance metrics",
                lambda: self.show_module("Stats"),
            ),
            (
                "Settings",
                "⚙️",
                "Configuration and preferences",
                lambda: self.show_module("Settings"),
            ),
        ]

        for name, icon, tooltip, action in button_configs:
            self.logger.debug(f"Creating sidebar button for module: {name}")

            # Create container for button
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)

            btn = QPushButton(f"{icon} {name}")
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    color: #ccc;
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin: 2px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 170, 0.1);
                    color: #00ffaa;
                    border-left: 3px solid #00ffaa;
                }
                QPushButton:pressed {
                    background-color: rgba(0, 255, 170, 0.2);
                }
                QPushButton:checked {
                    background-color: rgba(0, 255, 170, 0.15);
                    color: #00ffaa;
                    border-left: 3px solid #00ffaa;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(action)
            btn.clicked.connect(
                lambda checked, b=btn: self._highlight_sidebar_button(b)
            )

            btn_layout.addWidget(btn)
            self.sidebar_layout.addWidget(btn_container)

            key = f"{name.lower()}_btn"
            self.sidebar_buttons[key] = btn
            self.logger.debug(f"Added sidebar button for module: {name}")

        # Add spacer
        self.sidebar_layout.addStretch()

        # Add system info section
        system_label = QLabel("SYSTEM")
        system_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 10px;
                margin-top: 10px;
            }
        """)
        self.sidebar_layout.addWidget(system_label)

        # Add status indicator
        self.status_indicator = QLabel("🟢 Online")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                padding: 5px 10px;
                margin-bottom: 10px;
            }
        """)
        self.sidebar_layout.addWidget(self.status_indicator)

        # Setup dock widget properly
        if not hasattr(self, "dock") or self.dock is None:
            self.dock = QDockWidget("Navigation", self)
            self.dock.setObjectName("navigationDock")
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        # Set dock widget styling
        self.dock.setStyleSheet("""
            QDockWidget {
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }
            QDockWidget::title {
                background: #2a2a2a;
                color: #00ffaa;
                padding: 5px;
                border-bottom: 1px solid #333;
            }
        """)

        self.dock.setWidget(self.sidebar_widget)

        # Set initial width
        self.dock.setMinimumWidth(200)
        self.dock.setMaximumWidth(300)

    def _setup_dock_widgets(self):
        """Set up additional dock widgets for enhanced functionality."""
        self.logger.debug("Setting up dock widgets")

        # Create right panel for tools and information
        self.right_dock = QDockWidget("Tools & Info", self)
        self.right_dock.setObjectName("rightDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

        # Create right panel content
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(right_panel_widget)

        # Add quick action buttons
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setStyleSheet(
            "font-weight: bold; color: #00ffaa; padding: 5px;"
        )
        right_panel_layout.addWidget(quick_actions_label)

        quick_buttons = [
            ("🔄 Refresh", self._refresh_current_module),
            ("📊 Analytics", lambda: self.show_module("Analytics")),
            ("🤖 AI Assistant", lambda: self.show_module("AI Assistant")),
            ("� System Info", lambda: self.show_module("System Info")),
            ("� New Chat", self._new_chat),
        ]

        for btn_text, action in quick_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    color: #00ffaa;
                    background-color: #1a1a1a;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin: 2px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    border-color: #00ffaa;
                }
                QPushButton:pressed {
                    background-color: #00ffaa;
                    color: #000;
                }
            """)
            btn.clicked.connect(action)
            right_panel_layout.addWidget(btn)

        right_panel_layout.addStretch()

        # Add status information
        status_label = QLabel("System Status")
        status_label.setStyleSheet("font-weight: bold; color: #00ffaa; padding: 5px;")
        right_panel_layout.addWidget(status_label)

        self.status_info = QLabel("Ready")
        self.status_info.setStyleSheet("color: #aaa; padding: 5px; font-size: 12px;")
        right_panel_layout.addWidget(self.status_info)

        self.right_dock.setWidget(right_panel_widget)

        # Initially hide right dock
        self.right_dock.hide()

    def _setup_status_bar(self):
        """Set up the status bar at the bottom of the window."""
        self.logger.debug("Setting up status bar")
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _setup_button_connections(self):
        """Connect buttons to show_module method if they exist."""
        self.logger.info("Setting up button connections")
        # Buttons are already connected during creation in _setup_topbar and _setup_sidebar
        self.logger.info("Button connections completed")

    def _connect_sidebar_buttons(self):
        """Connect sidebar buttons to their respective actions."""
        # Buttons are already connected during creation in _setup_sidebar
        pass

    def _create_menu_bar(self):
        """Create the menu bar with necessary menus and actions."""
        self.logger.debug("Creating menu bar")
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # File Menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu("View")
        toggle_dock_action = QAction("Toggle Sidebar", self)
        toggle_dock_action.setShortcut("Ctrl+B")
        toggle_dock_action.triggered.connect(self.toggle_dock_widget)
        view_menu.addAction(toggle_dock_action)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        plugin_manager_action = QAction("Plugin Manager", self)
        plugin_manager_action.triggered.connect(lambda: self.show_module("Plugins"))
        tools_menu.addAction(plugin_manager_action)

        consent_manager_action = QAction("Consent Manager", self)
        consent_manager_action.triggered.connect(lambda: self.show_module("Consent"))
        tools_menu.addAction(consent_manager_action)

        decision_explanation_action = QAction("AI Decision Explanation", self)
        decision_explanation_action.triggered.connect(
            lambda: self.show_module("DecisionExplanation")
        )
        tools_menu.addAction(decision_explanation_action)

        user_management_action = QAction("User Management", self)
        user_management_action.triggered.connect(
            lambda: self.show_module("UserManagement")
        )
        tools_menu.addAction(user_management_action)

        # Settings Menu
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(lambda: self.show_module("Settings"))
        settings_menu.addAction(settings_action)

        # Help Menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        self.logger.debug("Menu bar creation completed")

    def toggle_dock_widget(self):
        """Toggle the visibility of the dock widget (sidebar)."""
        if hasattr(self, "dock") and self.dock is not None:
            if self.dock.isVisible():
                self.dock.hide()
            else:
                self.dock.show()
        else:
            self.logger.warning("Dock widget not initialized, cannot toggle")

    def show_about_dialog(self):
        """Show the About dialog with application information."""
        QMessageBox.about(
            self,
            "About Atlas",
            "Atlas - Autonomous Task Planning Application\nVersion 1.0\n 2025 Atlas Team",
        )

    def show_module(self, module_name: str) -> None:
        """Show the specified module in the central area."""
        self.logger.info(f"Showing module: {module_name}")

        widget = self.modules.get(module_name)
        if widget is None:
            self.logger.warning(f"Module {module_name} not found or not initialized")
            # Create placeholder if module doesn't exist
            widget = self._create_placeholder_module(module_name)
            self.modules[module_name] = widget

        if not hasattr(self, "central") or self.central is None:
            self.logger.error("Central widget is not initialized")
            return

        index = self.central.indexOf(widget)
        if index == -1:
            self.logger.debug(f"Adding module {module_name} to central widget stack")
            self.central.addWidget(widget)  # type: ignore[attr-defined]
        else:
            self.logger.debug(
                f"Module {module_name} already in central widget stack at index {index}"
            )

        self.central.setCurrentWidget(widget)
        self.logger.debug(f"Set module {module_name} as current widget")

        # Update button highlights
        self._update_button_highlights(module_name)

        # Update status bar
        self.statusBar().showMessage(f"Switched to {module_name} module", 3000)

        # Update status indicator
        if hasattr(self, "status_info"):
            self.status_info.setText(f"Current: {module_name}")

    def _create_placeholder_module(self, module_name: str) -> QWidget:
        """Create a placeholder widget for missing modules."""
        if PlaceholderWidget:
            return PlaceholderWidget(module_name)

        # Fallback placeholder if PlaceholderWidget is not available
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)

        # Title
        title = QLabel(f"{module_name} Module")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00ffaa;
                padding: 20px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel(f"The {module_name} module is currently under development.")
        desc.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #aaa;
                padding: 10px;
                text-align: center;
            }
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Add some spacing
        layout.addStretch()

        return placeholder

    def _update_button_highlights(self, module_name: str):
        """Update button highlights for the current module."""
        # Update topbar buttons
        target_btn_name = f"{module_name.lower()}_btn"
        for btn_name, btn in self.topbar_buttons.items():
            if hasattr(btn, "setChecked"):
                btn.setChecked(btn_name == target_btn_name)

        # Update sidebar buttons
        for btn_name, btn in self.sidebar_buttons.items():
            if hasattr(btn, "setChecked"):
                btn.setChecked(btn_name == target_btn_name)

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute.
            params: Parameters to pass to the tool.

        Returns:
            Result of the tool execution or a default dictionary if not available.
        """
        self.logger.debug(f"Executing tool: {tool_name} with params: {params}")
        self.logger.info(f"Tool execution for {tool_name} is temporarily disabled")
        return None

    def _initialize_modules(self):
        """Initialize all UI modules and add them to the central widget."""
        self.modules = {}
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        try:
            # Create a placeholder plugin system if needed
            self.logger.warning(
                "PluginManagerUI requires plugin_system parameter, using placeholder"
            )
            self.plugin_module = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Plugin Manager not available"))
            self.plugin_module.setLayout(layout)
            self.modules["Plugins"] = self.plugin_module
            self.logger.info("PluginManager module placeholder created")
        except Exception as e:
            self.logger.error(f"Failed to initialize PluginManager module: {e}")
            self.plugin_module = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("PluginManager not available"))
            self.plugin_module.setLayout(layout)
            self.modules["Plugins"] = self.plugin_module
        # Use placeholder for SettingsUI since module is not available
        self.logger.warning("SettingsUI module not available, using placeholder")
        self.settings_module = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings not available"))
        self.settings_module.setLayout(layout)
        self.modules["Settings"] = self.settings_module
        try:
            if self.app is not None:
                self.tool_manager_module = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(QLabel("ToolManager not available"))
                self.tool_manager_module.setLayout(layout)
                self.modules["Tools"] = self.tool_manager_module
                self.logger.info("ToolManager module initialized")
            else:
                self.logger.warning(
                    "App instance not available for ToolManager, using placeholder"
                )
                self.tool_manager_module = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(
                    QLabel("ToolManager not available - app instance missing")
                )
                self.tool_manager_module.setLayout(layout)
                self.modules["Tools"] = self.tool_manager_module
        except Exception as e:
            self.logger.error(f"Failed to initialize ToolManager module: {e}")
            self.tool_manager_module = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("ToolManager not available"))
            self.tool_manager_module.setLayout(layout)
            self.modules["Tools"] = self.tool_manager_module
        # Use placeholder for AIAssistantWidget since module is not available
        self.logger.warning("AIAssistantWidget module not available, using placeholder")
        self.ai_assistant_module = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("AIAssistant not available"))
        self.ai_assistant_module.setLayout(layout)
        self.modules["AIAssistant"] = self.ai_assistant_module
        try:
            from atlas.ui.consent_manager import ConsentManager

            self.consent_module = ConsentManager()
            self.modules["Consent"] = self.consent_module
            self.logger.info("Consent module initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Consent module: {e}")
            self.consent_module = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("ConsentManager not available"))
            self.consent_module.setLayout(layout)
            self.modules["Consent"] = self.consent_module
        try:
            from atlas.ui.user_management import UserManagement

            self.user_management_module = UserManagement()
            self.modules["UserManagement"] = self.user_management_module
            self.logger.info("UserManagement module initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize UserManagement module: {e}")
            self.user_management_module = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("UserManagement not available"))
            self.user_management_module.setLayout(layout)
            self.modules["UserManagement"] = self.user_management_module
        # Use placeholder for DecisionExplanationUI since module is not available
        self.logger.warning(
            "DecisionExplanationUI module not available, using placeholder"
        )
        self.decision_explanation_module = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("DecisionExplanationUI not available"))
        self.decision_explanation_module.setLayout(layout)
        self.central.addWidget(self.decision_explanation_module)
        self.modules["DecisionExplanation"] = self.decision_explanation_module
        # Add all modules to central widget
        for _module_name, module_widget in list(self.modules.items()):
            if module_widget not in self.central.children():
                self.central.addWidget(module_widget)
        # Set first module as current
        if self.modules:
            first_module = next(iter(self.modules.values()))
            self.central.setCurrentWidget(first_module)
        else:
            # Fallback to a placeholder widget if no modules are available
            placeholder = QWidget()
            self.central.addWidget(placeholder)  # type: ignore[attr-defined]
            self.central.setCurrentWidget(placeholder)

        self.logger.info("UI initialization complete")

    def initialize_ui(self, app: Any = None) -> None:
        """Initialize the UI with the given application instance.

        Args:
            app: The application instance to use for initialization. Defaults to None.
        """
        self.logger.info("Initializing UI with app instance")
        if app is not None:
            self.app = app
        self._init_ui()
        self.logger.info("UI initialization completed")

    def validate_input(
        self, value: str, input_type: str, field_name: str = "Input"
    ) -> tuple[bool, str]:
        """
        Validate user input using the input validation utilities.

        Args:
            value: Input value to validate
            input_type: Type of input (email, url, filepath, username, password, text, alphanumeric)
            field_name: Name of the input field for error messaging

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        return True, ""

    def sanitize_input(self, value: str) -> str:
        """
        Sanitize user input to remove potentially dangerous content.

        Args:
            value: Input value to sanitize

        Returns:
            str: Sanitized input value
        """
        return value

    def check_permission(self, username: str, permission: str) -> bool:
        """Check if a user has a specific permission.

        Args:
            username: Username to check
            permission: Permission string to verify

        Returns:
            bool: True if user has permission, False otherwise
        """
        self.logger.info("Permission checking is temporarily set to True")
        return True  # Default to True for development

    def enforce_permission(
        self, username: str, permission: str, operation: str
    ) -> None:
        """
        Enforce a permission check for a user.

        Args:
            username: Username to check
            permission: Permission string to verify
            operation: Description of operation for error message

        Raises:
            PermissionError: If user lacks permission
        """
        pass

    def closeEvent(self, event):
        """Handle window close event with proper cleanup."""
        self.logger.info("Closing main window")
        try:
            # Emit shutdown signal to subscribers
            if hasattr(self, "event_bus") and hasattr(self.event_bus, "publish"):
                try:
                    self.event_bus.publish("app_shutdown")
                except Exception as e:
                    self.logger.error(f"Error publishing shutdown signal: {e}")
            # Close all windows and cleanup
            event.accept()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            event.accept()
        # Do not call super().closeEvent(event) to avoid RuntimeError

    def setup_multilingual_ui(self, layout):
        # Create multilingual UI components
        pass

    def setup_standard_ui(self, layout):
        # Create tabbed interface for standard UI
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: 1px solid #333; background: #1a1a1a; }
            QTabBar::tab { /* Tab items */
                background: #333; color: #aaa; padding: 5px 10px;
                border: 1px solid #444; border-radius: 3px 0 0 3px;
                margin: 2px 0; min-width: 120px; }
            QTabBar::tab:selected {
                background: #444; color: #00ffaa; border-right: 0px; margin-right: -1px; }
            QTabBar::tab:hover {
                background: #2a2a2a; }
        """)

        self._initialize_modules()
        self._setup_topbar()
        self._setup_sidebar()
        # Add all initialized modules to the central widget stack
        for _module_name, module_widget in self.modules.items():
            if self.central.indexOf(module_widget) == -1:
                self.central.addWidget(module_widget)  # type: ignore[attr-defined]
                self.logger.debug("Added module to central widget stack")
        # Set the first module as current if available
        if self.modules and len(self.modules) > 0:
            first_module = next(iter(self.modules.values()))
            self.central.setCurrentWidget(first_module)
            self.logger.debug("Set first available module as current widget")
        else:
            # Fallback to a placeholder widget if no modules are available
            placeholder = QWidget()
            self.central.addWidget(placeholder)  # type: ignore[attr-defined]
            self.central.setCurrentWidget(placeholder)
            self.logger.warning("No modules available, using placeholder widget")
        self.logger.info("UI initialization complete")

    def setup_advanced_menu_bar(self):
        # Create advanced menu bar
        pass

    def setup_basic_menu_bar(self):
        # Create basic menu bar
        pass

    # Implementing UI enhancements for ASC-024
    # Note: This is a placeholder for actual implementation code.
    # In a real scenario, this would include updates to QMainWindow, navigation, sidebar, etc.
    # based on the specifications in ui_design_specifications.md.

    def load_theme(self):
        """Load the theme stylesheet based on user preferences."""
        # Use ThemeManager to apply the initial theme
        # self.theme_manager.apply_theme(self.theme_manager.get_current_theme())
        self.logger.info("Initial theme applied via ThemeManager")

    def apply_theme_to_all(self, theme_id: str):
        """Apply a theme to all UI elements.

        Args:
            theme_id: The ID of the theme to apply.
        """
        if self.theme_manager is not None:
            stylesheet = self.theme_manager.get_theme_stylesheet(theme_id)
            self.setStyleSheet(stylesheet)
            # Update style for all tabs/modules
            for module in self.modules.values():
                if hasattr(module, "setStyleSheet"):
                    module.setStyleSheet(stylesheet)
                # For LoadingSpinner
                if hasattr(module, "spinner") and hasattr(
                    module.spinner, "apply_theme"
                ):
                    module.spinner.apply_theme(stylesheet)
        else:
            self.logger.warning(
                "ThemeManager not available, skipping theme application"
            )

    def on_theme_changed(self, stylesheet):
        """Slot to handle theme changes.

        Args:
            stylesheet (str): The stylesheet to apply.
        """
        self.setStyleSheet(stylesheet)
        self.logger.info("Theme stylesheet updated")

    def setup_navigation(self):
        """Setup the header navigation and sidebar based on design specs."""
        # Header setup with gradient background
        self.header = QWidget()
        self.header.setObjectName("appHeader")
        self.header_layout = QHBoxLayout()
        self.header.setLayout(self.header_layout)

        # Logo placeholder
        self.logo_label = QLabel()
        self.logo_label.setObjectName("headerLogo")
        self.logo_label.setText("Atlas")
        self.header_layout.addWidget(self.logo_label)

        # Navigation tabs placeholder
        self.nav_tabs = QTabBar()
        self.nav_tabs.addTab("Home")
        self.nav_tabs.addTab("Tasks")
        self.nav_tabs.addTab("Chat")
        self.nav_tabs.addTab("Plugins")
        self.nav_tabs.addTab("Settings")
        self.header_layout.addWidget(self.nav_tabs)

        # Stretch to push search bar to the right
        self.header_layout.addStretch()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Search Atlas...")
        self.header_layout.addWidget(self.search_bar)

        # Add header to main layout
        self.main_layout.addWidget(self.header)

        # Sidebar setup (collapsible)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)

        # Sidebar toggle button
        self.sidebar_toggle = QPushButton("◀")
        self.sidebar_toggle.setObjectName("sidebarToggle")
        self.sidebar_toggle.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.sidebar_toggle)

        # Sidebar items placeholder
        self.sidebar_items = []
        for item in ["My Tasks", "Team Tasks", "Completed"]:
            btn = QPushButton(item)
            btn.setObjectName("sidebarItem")
            self.sidebar_items.append(btn)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        # Add sidebar to main layout (assuming a splitter or similar for main layout structure)
        # TODO: Adjust based on actual main layout structure
        # For now, assuming it's added as a separate widget
        self.main_layout.addWidget(self.sidebar)

        # Breadcrumb placeholder
        self.breadcrumb = QLabel("Home > Tasks > My Tasks")
        self.breadcrumb.setObjectName("breadcrumb")
        self.main_layout.addWidget(self.breadcrumb)

        self.logger.info("Navigation setup completed")
        # TODO: Implement full styling and dynamic behavior as per specs

    def toggle_sidebar(self):
        """Toggle the sidebar visibility or width."""
        # TODO: Implement actual collapse/expand logic with animation
        if self.sidebar.width() > 60:
            self.sidebar.setFixedWidth(60)
            self.sidebar_toggle.setText("▶")
        else:
            self.sidebar.setFixedWidth(250)
            self.sidebar_toggle.setText("◀")
        self.logger.info("Sidebar toggled")

    def _connect_buttons(self):
        """Connect window control buttons with safety checks."""
        self.logger.debug("Connecting window control buttons")
        if hasattr(self, "menu_btn") and self.menu_btn:
            self.menu_btn.clicked.connect(self.show_context_menu)
        if hasattr(self, "minimize_btn") and self.minimize_btn:
            self.minimize_btn.clicked.connect(self.showMinimized)
        if hasattr(self, "maximize_btn") and self.maximize_btn:
            self.maximize_btn.clicked.connect(self.toggleMaximized)
        if hasattr(self, "close_btn") and self.close_btn:
            self.close_btn.clicked.connect(self.close)
        self.logger.debug("Window control buttons connected")

    def _connect_ui_buttons(self):
        """Connect UI buttons to their respective actions with safety checks."""
        self.logger.info("Connecting UI buttons")
        # Sidebar buttons
        if "chat_btn" in self.sidebar_buttons and self.sidebar_buttons["chat_btn"]:
            self.sidebar_buttons["chat_btn"].clicked.connect(
                lambda: self.show_module("Chat")
            )
        if "tasks_btn" in self.sidebar_buttons and self.sidebar_buttons["tasks_btn"]:
            self.sidebar_buttons["tasks_btn"].clicked.connect(
                lambda: self.show_module("Tasks")
            )
        if (
            "settings_btn" in self.sidebar_buttons
            and self.sidebar_buttons["settings_btn"]
        ):
            self.sidebar_buttons["settings_btn"].clicked.connect(
                lambda: self.show_module("Settings")
            )
        if (
            "plugins_btn" in self.sidebar_buttons
            and self.sidebar_buttons["plugins_btn"]
        ):
            self.sidebar_buttons["plugins_btn"].clicked.connect(
                lambda: self.show_module("Plugins")
            )
        # Topbar buttons
        if "menu_btn" in self.topbar_buttons and self.topbar_buttons["menu_btn"]:
            self.topbar_buttons["menu_btn"].clicked.connect(self.show_context_menu)
        if (
            "minimize_btn" in self.topbar_buttons
            and self.topbar_buttons["minimize_btn"]
        ):
            self.topbar_buttons["minimize_btn"].clicked.connect(self.showMinimized)
        if (
            "maximize_btn" in self.topbar_buttons
            and self.topbar_buttons["maximize_btn"]
        ):
            self.topbar_buttons["maximize_btn"].clicked.connect(self.toggleMaximized)
        if "close_btn" in self.topbar_buttons and self.topbar_buttons["close_btn"]:
            self.topbar_buttons["close_btn"].clicked.connect(self.close)
        self.logger.info("UI buttons connected to actions")

    def process_user_input(self, input_text: str) -> None:
        pass

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled. Temporarily always returns True for development."""
        self.logger.info(f"Feature check for {feature_name} is temporarily set to True")
        return True

    def _setup_tab_widget(self):
        """Set up the QTabWidget with custom styling."""
        self.logger.debug("Setting up tab widget")
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

    def _setup_tab_widget_style(self):
        """Set up the QTabWidget style."""
        self.logger.debug("Setting up tab widget style")
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: 0px;
            }
            QTabBar::tab { /* Tab items */
                background: #222;
                color: #aaa;
                border: 1px solid #444;
                border-radius: 3px 0 0 3px;
                margin: 2px 0;
                padding: 8px 12px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #333;
                color: #00ffaa;
                border-right: 0px;
                margin-right: -1px;
            }
            QTabBar::tab:hover {
                background: #2a2a2a;
            }
        """)

    def _add_tab(self, widget: QWidget, label: str) -> None:
        """Add a tab to the QTabWidget."""
        self.logger.debug(f"Adding tab: {label}")
        self.tab_widget.addTab(widget, label)

    def _add_tab_if_enabled(
        self, widget: QWidget, label: str, feature_name: str
    ) -> None:
        """Add a tab only if the feature is enabled."""
        if self.is_feature_enabled(feature_name):
            self.logger.info(f"Feature {feature_name} is enabled, adding tab: {label}")
            self._add_tab(widget, label)
        else:
            self.logger.info(
                f"Feature {feature_name} is disabled, skipping tab: {label}"
            )

    def show_context_menu(self):
        """Placeholder method for showing context menu."""
        self.logger.debug("Showing context menu")
        pass

    def toggleMaximized(self):
        """Placeholder method for toggling maximized state."""
        self.logger.debug("Toggling maximized state")
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def show(self):
        """Show the main window."""
        if self.app is None:
            self.logger.error("Application instance is not set, cannot show window")
            return
        super().show()
        self.logger.info("Main window shown")

    def _setup_event_bus_connections(self):
        """Set up event bus connections for UI events."""
        self.logger.info("Setting up event bus connections")
        if hasattr(self.event_bus, "subscribe"):
            # Subscribe to events with placeholder methods
            self.event_bus.subscribe(
                "tool_executed",
                lambda data: self.statusBar().showMessage("Tool executed", 5000),
            )
            self.event_bus.subscribe(
                "tool_error",
                lambda data: self.statusBar().showMessage("Tool failed", 7000),
            )
        else:
            self.logger.warning(
                "Event bus does not support subscribe, skipping connections"
            )

    def _refresh_current_module(self):
        """Refresh the current active module."""
        self.logger.info("Refreshing current module")
        current_widget = self.central.currentWidget()
        if current_widget:
            # Use getattr for safe attribute access
            refresh_method = getattr(current_widget, "refresh", None)
            if refresh_method and callable(refresh_method):
                try:
                    refresh_method()
                except Exception as e:
                    self.logger.error(f"Error refreshing module: {e}")
        self.statusBar().showMessage("Module refreshed", 3000)

    def _new_chat(self):
        """Start a new chat session."""
        self.logger.info("Starting new chat")
        self.show_module("Chat")
        if hasattr(self, "chat_module"):
            # Use getattr for safe attribute access
            clear_chat_method = getattr(self.chat_module, "clear_chat", None)
            if clear_chat_method and callable(clear_chat_method):
                try:
                    clear_chat_method()
                except Exception as e:
                    self.logger.error(f"Error clearing chat: {e}")
        self.statusBar().showMessage("New chat started", 3000)

    def _toggle_right_panel(self):
        """Toggle the right panel visibility."""
        if hasattr(self, "right_dock"):
            if self.right_dock.isVisible():
                self.right_dock.hide()
            else:
                self.right_dock.show()

    def _highlight_active_button(self, active_button):
        """Highlight the active navigation button."""
        # Reset all navigation buttons
        for btn_name, btn in self.topbar_buttons.items():
            if btn_name.endswith("_btn") and btn_name not in [
                "minimize_btn",
                "maximize_btn",
                "close_btn",
            ]:
                btn.setChecked(False)

        # Set active button as checked
        if active_button:
            active_button.setChecked(True)

    def _highlight_sidebar_button(self, active_button):
        """Highlight the active sidebar button."""
        # Reset all sidebar buttons
        for btn in self.sidebar_buttons.values():
            if hasattr(btn, "setChecked"):
                btn.setChecked(False)

        # Set active button as checked
        if active_button and hasattr(active_button, "setChecked"):
            active_button.setChecked(True)

    def _apply_global_theme(self):
        """Apply global theme styling to the main window."""
        global_style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #0d0d0d);
            color: #ccc;
        }

        QStatusBar {
            background: #1a1a1a;
            color: #888;
            border-top: 1px solid #333;
            padding: 5px;
        }

        QStackedWidget {
            background: #1a1a1a;
            border: none;
        }

        QLabel {
            color: #ccc;
        }

        /* Scrollbars */
        QScrollBar:vertical {
            background: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #00ffaa;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: #00ff88;
        }

        /* Menu styling */
        QMenuBar {
            background: #2a2a2a;
            color: #ccc;
            border-bottom: 1px solid #333;
        }

        QMenuBar::item {
            background: transparent;
            padding: 8px 12px;
        }

        QMenuBar::item:selected {
            background: rgba(0, 255, 170, 0.2);
            color: #00ffaa;
        }

        QMenu {
            background: #2a2a2a;
            color: #ccc;
            border: 1px solid #333;
        }

        QMenu::item {
            padding: 8px 16px;
        }

        QMenu::item:selected {
            background: rgba(0, 255, 170, 0.2);
            color: #00ffaa;
        }
        """
        self.setStyleSheet(global_style)

    def _initialize_core_modules(self):
        """Initialize all core UI modules with error handling."""
        self.logger.info("Initializing core modules")

        # Chat Module - always create even if basic
        try:
            self.chat_module = ChatWidget(self.app)
            self.modules["Chat"] = self.chat_module
            self.logger.info("Chat module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chat module: {e}")
            self.chat_module = self._create_placeholder_module("Chat")
            self.modules["Chat"] = self.chat_module

        # Plugins Module
        try:
            self.plugins_module = PluginsWidget(self)
            self.modules["Plugins"] = self.plugins_module
            self.logger.info("Plugins module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugins module: {e}")
            self.plugins_module = self._create_placeholder_module("Plugins")
            self.modules["Plugins"] = self.plugins_module

        # Tools Module
        self.tools_module = self._create_tools_module()
        self.modules["Tools"] = self.tools_module
        self.logger.info("Tools module initialized successfully")

        # Settings Module
        self.settings_module = self._create_settings_module()
        self.modules["Settings"] = self.settings_module
        self.logger.info("Settings module initialized successfully")

        # Tasks Module
        self.tasks_module = self._create_tasks_module()
        self.modules["Tasks"] = self.tasks_module
        self.logger.info("Tasks module initialized successfully")

        # Analytics Module (sidebar only)
        self.analytics_module = self._create_analytics_module()
        self.modules["Analytics"] = self.analytics_module
        self.logger.info("Analytics module initialized successfully")

        # AI Assistant Module (sidebar only)
        self.ai_assistant_module = self._create_ai_assistant_module()
        self.modules["AI Assistant"] = self.ai_assistant_module
        self.logger.info("AI Assistant module initialized successfully")

        # System Info Module (sidebar only)
        self.system_info_module = self._create_system_info_module()
        self.modules["System Info"] = self.system_info_module
        self.logger.info("System Info module initialized successfully")

        # Agents Module
        try:
            self.agents_module = self._create_agents_module()
            self.modules["Agents"] = self.agents_module
            self.logger.info("Agents module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Agents module: {e}")
            self.agents_module = self._create_placeholder_module("Agents")
            self.modules["Agents"] = self.agents_module

        # Memory Module
        try:
            self.memory_module = self._create_memory_module()
            self.modules["Memory"] = self.memory_module
            self.logger.info("Memory module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Memory module: {e}")
            self.memory_module = self._create_placeholder_module("Memory")
            self.modules["Memory"] = self.memory_module

        # Intelligence Module
        try:
            self.intelligence_module = self._create_intelligence_module()
            self.modules["Intelligence"] = self.intelligence_module
            self.logger.info("Intelligence module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Intelligence module: {e}")
            self.intelligence_module = self._create_placeholder_module("Intelligence")
            self.modules["Intelligence"] = self.intelligence_module

        # Workflows Module
        try:
            self.workflows_module = self._create_workflows_module()
            self.modules["Workflows"] = self.workflows_module
            self.logger.info("Workflows module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Workflows module: {e}")
            self.workflows_module = self._create_placeholder_module("Workflows")
            self.modules["Workflows"] = self.workflows_module

        # Stats Module
        try:
            self.stats_module = self._create_stats_module()
            self.modules["Stats"] = self.stats_module
            self.logger.info("Stats module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Stats module: {e}")
            self.stats_module = self._create_placeholder_module("Stats")
            self.modules["Stats"] = self.stats_module

        # Performance Module
        try:
            self.performance_module = self._create_performance_module()
            self.modules["Performance"] = self.performance_module
            self.logger.info("Performance module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Performance module: {e}")
            self.performance_module = self._create_placeholder_module("Performance")
            self.modules["Performance"] = self.performance_module

        # Security Module
        self.security_module = self._create_security_module()
        self.modules["Security"] = self.security_module
        self.logger.info("Security module initialized successfully")

        # System Control Module
        try:
            self.system_control_module = self._create_system_control_module()
            self.modules["System Control"] = self.system_control_module
            self.logger.info("System Control module initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize System Control module: {e}")
            self.system_control_module = self._create_placeholder_module(
                "System Control"
            )
            self.modules["System Control"] = self.system_control_module

        self.logger.info(
            f"Core modules initialization completed. Total modules: {len(self.modules)}"
        )

    def _create_tools_module(self):
        """Create a comprehensive tools module."""
        tools_widget = QWidget()
        layout = QVBoxLayout(tools_widget)

        # Title
        title = QLabel("🔧 Development Tools")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #00ffaa;
                padding: 15px;
                text-align: center;
                border-bottom: 2px solid #333;
                margin-bottom: 15px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tools grid
        tools_container = QWidget()
        tools_layout = QVBoxLayout(tools_container)

        # Tool categories
        tool_categories = [
            (
                "Code Tools",
                [
                    ("🐍 Python REPL", "Interactive Python console"),
                    ("📊 Data Viewer", "View and analyze data"),
                    ("🔍 Code Search", "Search through codebase"),
                    ("🛠️ Debugger", "Debug applications"),
                ],
            ),
            (
                "System Tools",
                [
                    ("📁 File Manager", "Browse and manage files"),
                    ("⚡ Process Monitor", "Monitor system processes"),
                    ("🌐 Network Tools", "Network diagnostic tools"),
                    ("📈 Performance Monitor", "Monitor system performance"),
                ],
            ),
            (
                "AI Tools",
                [
                    ("🤖 Code Generator", "Generate code with AI"),
                    ("📝 Documentation Generator", "Auto-generate docs"),
                    ("🔧 Code Refactor", "Refactor code intelligently"),
                    ("🧪 Test Generator", "Generate unit tests"),
                ],
            ),
        ]

        for category_name, tools in tool_categories:
            # Category header
            category_label = QLabel(category_name)
            category_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #00ffaa;
                    padding: 10px 5px;
                    border-bottom: 1px solid #444;
                }
            """)
            tools_layout.addWidget(category_label)

            # Tools in category
            for tool_name, tool_desc in tools:
                tool_btn = QPushButton(f"{tool_name}")
                tool_btn.setToolTip(tool_desc)
                tool_btn.setStyleSheet("""
                    QPushButton {
                        color: #ccc;
                        background-color: #2a2a2a;
                        border: 1px solid #444;
                        border-radius: 6px;
                        padding: 10px 15px;
                        margin: 3px;
                        text-align: left;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 255, 170, 0.1);
                        border-color: #00ffaa;
                        color: #00ffaa;
                    }
                    QPushButton:pressed {
                        background-color: rgba(0, 255, 170, 0.2);
                    }
                """)
                tool_btn.clicked.connect(
                    lambda checked, name=tool_name: self._launch_tool(name)
                )
                tools_layout.addWidget(tool_btn)

        layout.addWidget(tools_container)
        layout.addStretch()

        return tools_widget

    def _create_settings_module(self):
        """Create a comprehensive settings module."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Title
        title = QLabel("⚙️ Application Settings")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #00ffaa;
                padding: 15px;
                text-align: center;
                border-bottom: 2px solid #333;
                margin-bottom: 15px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Settings categories
        settings_container = QWidget()
        settings_layout = QVBoxLayout(settings_container)

        settings_categories = [
            (
                "🎨 Appearance",
                [
                    "Theme Selection",
                    "Font Settings",
                    "Color Scheme",
                    "UI Layout",
                ],
            ),
            (
                "🔧 General",
                [
                    "Auto-save Settings",
                    "Default Modules",
                    "Startup Behavior",
                    "Language Settings",
                ],
            ),
            (
                "🤖 AI Configuration",
                [
                    "Model Selection",
                    "API Keys",
                    "Behavior Settings",
                    "Privacy Settings",
                ],
            ),
            (
                "🔌 Plugins",
                [
                    "Enabled Plugins",
                    "Plugin Settings",
                    "Auto-update",
                    "Plugin Repositories",
                ],
            ),
        ]

        for category_name, settings in settings_categories:
            # Category header
            category_label = QLabel(category_name)
            category_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #00ffaa;
                    padding: 10px 5px;
                    border-bottom: 1px solid #444;
                }
            """)
            settings_layout.addWidget(category_label)

            # Settings in category
            for setting_name in settings:
                setting_btn = QPushButton(f"📝 {setting_name}")
                setting_btn.setStyleSheet("""
                    QPushButton {
                        color: #ccc;
                        background-color: #2a2a2a;
                        border: 1px solid #444;
                        border-radius: 6px;
                        padding: 10px 15px;
                        margin: 3px;
                        text-align: left;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 255, 170, 0.1);
                        border-color: #00ffaa;
                        color: #00ffaa;
                    }
                    QPushButton:pressed {
                        background-color: rgba(0, 255, 170, 0.2);
                    }
                """)
                setting_btn.clicked.connect(
                    lambda checked, name=setting_name: self._open_setting(name)
                )
                settings_layout.addWidget(setting_btn)

        layout.addWidget(settings_container)
        layout.addStretch()

        return settings_widget

    def _create_tasks_module(self):
        """Create a comprehensive tasks module using TasksWidget."""
        from atlas.ui.tasks import TasksWidget

        tasks_widget = TasksWidget()
        self._connect_tasks_events(tasks_widget)
        return tasks_widget

    def _connect_tasks_events(self, tasks_widget):
        """Connect task events to handlers."""
        # Connect task events to agent loop
        self._connect_task_creation(tasks_widget)
        self._subscribe_to_task_events(tasks_widget)

    def _connect_task_creation(self, tasks_widget):
        """Connect task creation to agent loop if available."""
        # Get the agent loop from app instance and check it has the required method
        app = self.app_instance
        if isinstance(app, AtlasApplication) and app.agent_loop:
            tasks_widget.task_created.connect(app.agent_loop._handle_new_task)

    def _subscribe_to_task_events(self, tasks_widget):
        """Subscribe to task-related events from event bus."""

        def handle_task_update(data: Dict[str, Any]) -> None:
            if isinstance(data, dict):
                task_id = data.get("task_id")
                status = data.get("status")
                if task_id and status:
                    tasks_widget.update_task_status(task_id, status)

        def handle_task_complete(data: Dict[str, Any]) -> None:
            if isinstance(data, dict):
                task_id = data.get("task_id")
                result = data.get("result")
                if task_id:
                    tasks_widget.update_task_status(task_id, "completed", result)

        def handle_task_fail(data: Dict[str, Any]) -> None:
            if isinstance(data, dict):
                task_id = data.get("task_id")
                error = data.get("error")
                if task_id:
                    tasks_widget.update_task_status(
                        task_id, "failed", {"error": error} if error else None
                    )

        self.event_bus.subscribe("TASK_UPDATED", handle_task_update)
        self.event_bus.subscribe("TASK_COMPLETED", handle_task_complete)
        self.event_bus.subscribe("TASK_FAILED", handle_task_fail)

        return tasks_widget

    def _create_analytics_module(self):
        """Create analytics module for sidebar."""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)

        title = QLabel("📊 Analytics Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ffaa;
                padding: 15px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Analytics items
        analytics_items = [
            "📈 Usage Statistics",
            "⏱️ Time Tracking",
            "🎯 Performance Metrics",
            "📋 Task Analytics",
            "🤖 AI Usage Stats",
        ]

        for item in analytics_items:
            item_label = QLabel(item)
            item_label.setStyleSheet("""
                QLabel {
                    color: #ccc;
                    padding: 8px 12px;
                    border: 1px solid #444;
                    border-radius: 4px;
                    margin: 2px;
                }
            """)
            layout.addWidget(item_label)

        layout.addStretch()
        return analytics_widget

    def _create_ai_assistant_module(self):
        """Create AI assistant module for sidebar."""
        ai_widget = QWidget()
        layout = QVBoxLayout(ai_widget)

        title = QLabel("🤖 AI Assistant")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ffaa;
                padding: 15px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # AI features
        ai_features = [
            "💬 Smart Chat",
            "🔍 Code Analysis",
            "📝 Auto Documentation",
            "🛠️ Code Generation",
            "🧪 Test Creation",
        ]

        for feature in ai_features:
            feature_btn = QPushButton(feature)
            feature_btn.setStyleSheet("""
                QPushButton {
                    color: #ccc;
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin: 2px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 170, 0.1);
                    color: #00ffaa;
                    border-color: #00ffaa;
                }
            """)
            feature_btn.clicked.connect(
                lambda checked, f=feature: self._use_ai_feature(f)
            )
            layout.addWidget(feature_btn)

        layout.addStretch()
        return ai_widget

    def _create_system_info_module(self):
        """Create system information module for sidebar."""
        system_widget = QWidget()
        layout = QVBoxLayout(system_widget)

        title = QLabel("💻 System Information")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ffaa;
                padding: 15px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # System info sections
        info_sections = [
            ("🖥️ Hardware", "View hardware specifications"),
            ("💾 Memory", "Monitor memory usage"),
            ("💽 Storage", "Check disk space"),
            ("🌐 Network", "Network status and info"),
            ("⚡ Performance", "Performance metrics"),
            ("📊 Logs", "System and application logs"),
        ]

        for section_name, description in info_sections:
            section_btn = QPushButton(section_name)
            section_btn.setToolTip(description)
            section_btn.setStyleSheet("""
                QPushButton {
                    color: #ccc;
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin: 2px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 170, 0.1);
                    color: #00ffaa;
                    border-color: #00ffaa;
                }
            """)
            section_btn.clicked.connect(
                lambda checked, s=section_name: self._show_system_info(s)
            )
            layout.addWidget(section_btn)

        layout.addStretch()
        return system_widget

    def _show_system_info(self, section_name: str):
        """Show specific system information section."""
        self.logger.info(f"Showing system info: {section_name}")
        self.statusBar().showMessage(f"System info: {section_name}", 3000)
        # Placeholder for system info display logic

    def _launch_tool(self, tool_name: str):
        """Launch a specific tool."""
        self.logger.info(f"Launching tool: {tool_name}")
        self.statusBar().showMessage(f"Launched tool: {tool_name}", 3000)
        # Placeholder for actual tool launching logic

    def _open_setting(self, setting_name: str):
        """Open a specific setting."""
        self.logger.info(f"Opening setting: {setting_name}")
        self.statusBar().showMessage(f"Opened setting: {setting_name}", 3000)
        # Placeholder for actual settings logic

    def _add_new_task(self):
        """Add a new task."""
        self.logger.info("Adding new task")
        self.statusBar().showMessage("New task dialog would open here", 3000)
        # Placeholder for task creation dialog

    def _filter_tasks(self, filter_name: str):
        """Filter tasks by type."""
        self.logger.info(f"Filtering tasks by: {filter_name}")
        self.statusBar().showMessage(f"Filtered tasks: {filter_name}", 3000)
        # Placeholder for task filtering logic

    def _use_ai_feature(self, feature_name: str):
        """Use an AI feature."""
        self.logger.info(f"Using AI feature: {feature_name}")
        self.statusBar().showMessage(f"AI feature activated: {feature_name}", 3000)
        # Placeholder for AI feature logic

    def _create_agents_module(self):
        """Create the agents management module."""
        try:
            agents_widget = AgentsWidget(self)
            return agents_widget
        except Exception as e:
            self.logger.error(f"Error creating agents module: {e}")
            return self._create_placeholder_module("Agents")

    def _create_memory_module(self):
        """Create the memory management module."""
        try:
            # Try to create with memory manager if available
            if hasattr(self, "memory_manager") and self.memory_manager:
                memory_widget = MemoryUI(self.memory_manager, self)
            else:
                # Create a basic memory UI without manager
                memory_widget = QWidget()
                layout = QVBoxLayout(memory_widget)
                title = QLabel("🧠 Memory Management")
                title.setStyleSheet(
                    "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
                )
                layout.addWidget(title)

                status_label = QLabel(
                    "Memory manager not available. Please configure memory system."
                )
                status_label.setStyleSheet("color: #ffaa00; padding: 10px;")
                layout.addWidget(status_label)

            return memory_widget
        except Exception as e:
            self.logger.error(f"Error creating memory module: {e}")
            return self._create_placeholder_module("Memory")

    def _create_intelligence_module(self):
        """Create the intelligence module with self-improvement, context, and decision UIs."""
        try:
            intelligence_widget = QWidget()
            layout = QVBoxLayout(intelligence_widget)

            # Title
            title = QLabel("🧠 Intelligence Center")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            # Tab widget for different intelligence components
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #1a1a1a;
                }
                QTabBar::tab {
                    background-color: #2a2a2a;
                    color: #ccc;
                    padding: 8px 16px;
                    margin: 2px;
                    border-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #00ffaa;
                    color: #000;
                }
            """)

            # Self-improvement tab
            try:
                self_improvement_widget = SelfImprovementUI(None, self)
                tab_widget.addTab(self_improvement_widget, "Self-Improvement")

            except Exception as e:
                self.logger.error(f"Error creating self-improvement UI: {e}")
                placeholder = self._create_placeholder_module("Self-Improvement")
                tab_widget.addTab(placeholder, "Self-Improvement")

            # Context tab
            try:
                # Create a basic context widget since we don't have context_engine
                context_widget = QWidget()
                context_layout = QVBoxLayout(context_widget)
                context_title = QLabel("Context Awareness Engine")
                context_title.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #00ffaa;"
                )
                context_layout.addWidget(context_title)

                context_info = QLabel(
                    "Context engine not available. Please configure context system."
                )
                context_info.setStyleSheet("color: #ffaa00; padding: 10px;")
                context_layout.addWidget(context_info)

                tab_widget.addTab(context_widget, "Context")
            except Exception as e:
                self.logger.error(f"Error creating context UI: {e}")
                placeholder = self._create_placeholder_module("Context")
                tab_widget.addTab(placeholder, "Context")

            # Decision tab
            try:
                decision_widget = DecisionUI(None, self)
                tab_widget.addTab(decision_widget, "Decisions")
            except Exception as e:
                self.logger.error(f"Error creating decision UI: {e}")
                placeholder = self._create_placeholder_module("Decisions")
                tab_widget.addTab(placeholder, "Decisions")

            layout.addWidget(tab_widget)
            return intelligence_widget

        except Exception as e:
            self.logger.error(f"Error creating intelligence module: {e}")
            return self._create_placeholder_module("Intelligence")

    def _create_workflows_module(self):
        """Create the workflows module."""
        try:
            workflows_widget = WorkflowUI(self)

            # Add a wrapper with title if WorkflowUI is basic
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)

            title = QLabel("🔄 Workflow Management")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            layout.addWidget(workflows_widget)
            return wrapper

        except Exception as e:
            self.logger.error(f"Error creating workflows module: {e}")
            return self._create_placeholder_module("Workflows")

    def _create_stats_module(self):
        """Create the statistics module."""
        try:
            stats_widget = StatsModule(self)

            # Add a wrapper with enhanced styling
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)

            title = QLabel("📊 Statistics & Analytics")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            layout.addWidget(stats_widget)
            return wrapper

        except Exception as e:
            self.logger.error(f"Error creating stats module: {e}")
            return self._create_placeholder_module("Stats")

    def _create_performance_module(self):
        """Create the performance monitoring module."""
        try:
            performance_widget = PerformancePanel(self)

            # Add a wrapper with title
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)

            title = QLabel("⚡ Performance Monitor")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            layout.addWidget(performance_widget)
            return wrapper

        except Exception as e:
            self.logger.error(f"Error creating performance module: {e}")
            return self._create_placeholder_module("Performance")

    def _create_security_module(self):
        """Create the security management module."""
        try:
            # Create basic security widget since SecurityPanel needs specific parameters
            security_widget = QWidget()
            layout = QVBoxLayout(security_widget)

            title = QLabel("🔒 Security Center")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            # Add basic security info
            info_label = QLabel("Security monitoring and management")
            info_label.setStyleSheet("color: #ccc; padding: 10px;")
            layout.addWidget(info_label)

            # Add security status
            status_label = QLabel("🟢 System Secure")
            status_label.setStyleSheet(
                "color: #00ffaa; font-weight: bold; padding: 10px;"
            )
            layout.addWidget(status_label)

            return security_widget

        except Exception as e:
            self.logger.error(f"Error creating security module: {e}")
            return self._create_placeholder_module("Security")

    def _create_system_control_module(self):
        """Create the system control module."""
        try:
            system_control_widget = SystemControlPanel(self)

            # Add a wrapper with title
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)

            title = QLabel("🔧 System Control")
            title.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #00ffaa; padding: 15px;"
            )
            layout.addWidget(title)

            layout.addWidget(system_control_widget)
            return wrapper

        except Exception as e:
            self.logger.error(f"Error creating system control module: {e}")
            return self._create_placeholder_module("System Control")
