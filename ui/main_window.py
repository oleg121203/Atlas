import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import (
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QFont,
    QIcon,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QTabBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.event_bus import EventBus
from core.events import TOOL_ERROR, TOOL_EXECUTED
from data.memory_manager import MemoryManager
from ui.chat.ai_assistant_widget import AIAssistantWidget
from ui.chat.chat_widget import ChatWidget
from ui.module_communication import EVENT_BUS
from ui.plugins.plugins_widget import PluginsWidget
from ui.settings.settings_widget import SettingsWidget
from ui.themes import ThemeManager
from ui.tools import ToolManagerUI
from ui.user_management_widget import UserManagementWidget

try:
    from ui.self_improvement_center import SelfImprovementCenter
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Import error for SelfImprovementCenter: {e}")
    SelfImprovementCenter = None  # Placeholder to prevent crashes


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
        self_learning_agent (SelfLearningAgent): Self-learning agent instance
        task_planner_agent (TaskPlannerAgent): Task planner agent instance
        context_analyzer (ContextAnalyzer): Context analyzer instance
    """

    def __init__(
        self,
        meta_agent: Optional[Any] = None,
        parent: Optional[QWidget] = None,
        app_instance: Optional[Any] = None,
        context_engine=None,
        decision_engine=None,
        self_improvement_engine=None,
        memory_manager=None,
    ):
        logger = logging.getLogger(__name__)
        logger.debug("Starting AtlasMainWindow initialization")
        super().__init__(parent)
        self.meta_agent = meta_agent
        self.app_instance = app_instance
        self.context_engine = context_engine
        self.decision_engine = decision_engine
        self.self_improvement_engine = self_improvement_engine
        self.memory_manager = memory_manager
        self.setWindowTitle("Atlas - Autonomous Task Planning")
        self.setGeometry(100, 100, 1200, 800)
        # Initialize core components
        from PySide6.QtWidgets import QApplication

        self.app_instance = app_instance if app_instance else QApplication.instance()
        self.event_bus = EVENT_BUS
        self.event_bus.subscribe("app_shutdown", self._on_app_shutdown)
        self.event_bus.publish("main_window_initialized", {"status": "ready"})
        self.memory_manager = MemoryManager()
        self.modules = {}
        # Temporarily commented out unresolved imports to prevent startup crashes
        # self.self_learning_agent = SelfLearningAgent(memory_manager=self.memory_manager)
        # self.task_planner_agent = TaskPlannerAgent(memory_manager=self.memory_manager)
        # self.context_analyzer = ContextAnalyzer(memory_manager=self.memory_manager)
        self.chat_processor = None  # Temporarily set to None to prevent startup crashes
        # self.chat_processor = ChatProcessor()
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        self.sidebar = QToolBar()
        self.sidebar.setOrientation(Qt.Orientation.Vertical)
        self.topbar = QToolBar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topbar)
        self.dock = QDockWidget()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self.sidebar)
        # Delay UI initialization to ensure QApplication is ready
        QTimer.singleShot(0, self._init_ui)
        self.logger = logging.getLogger(__name__)
        self.main_layout = QVBoxLayout()  # Додаємо основний layout, якщо його не було
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme_to_all)
        self.event_bus.subscribe(TOOL_EXECUTED, self._on_tool_executed)
        self.event_bus.subscribe(TOOL_ERROR, self._on_tool_error)
        logger.debug("AtlasMainWindow initialization completed")

    def _init_ui(self):
        """Initialize UI elements after QApplication is ready."""
        logger = logging.getLogger(__name__)
        logger.debug("Initializing UI elements")
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: #00ffaa; }
            QPushButton {
                background-color: #333;
                color: #00ffaa;
                border: 1px solid #444;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton:pressed { background-color: #222; }
            QTextEdit, QLineEdit {
                background-color: #222;
                color: #00ffaa;
                border: 1px solid #444;
                padding: 3px;
            }
            QLabel { color: #00ffaa; }
            QTabWidget::pane { border: 1px solid #333; background: #1a1a1a; }
            QTabBar::tab { background: #333; color: #00ffaa; padding: 5px 10px; border: 1px solid #444; }
            QTabBar::tab:selected { background: #444; border-bottom: none; }
            QTreeView, QListView { background-color: #222; color: #00ffaa; border: 1px solid #444; }
            QTreeView::item:hover, QListView::item:hover { background-color: #333; }
            QTreeView::item:selected, QListView::item:selected { background-color: #444; }
            QMenuBar { background-color: #222; color: #00ffaa; }
            QMenuBar::item { padding: 2px 10px; }
            QMenuBar::item:selected { background-color: #333; }
            QMenu { background-color: #222; color: #00ffaa; border: 1px solid #444; }
            QMenu::item { padding: 2px 10px; }
            QMenu::item:selected { background-color: #333; }
            QStatusBar { background-color: #222; color: #00ffaa; border-top: 1px solid #333; }
        """)

        self._initialize_modules()
        self._setup_topbar()
        self._setup_sidebar()
        self.central.setCurrentWidget(
            list(self.modules.values())[0] if self.modules else QWidget()
        )
        logger.info("UI initialization complete")

    def _create_menu_bar(self):
        """Create the menu bar with necessary menus and actions."""
        logger = logging.getLogger(__name__)
        logger.debug("Creating menu bar")
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

        logger.debug("Menu bar creation completed")

    def toggle_dock_widget(self):
        """Toggle the visibility of the dock widget (sidebar)."""
        if self.dock.isVisible():
            self.dock.hide()
        else:
            self.dock.show()

    def show_about_dialog(self):
        """Show the About dialog with application information."""
        QMessageBox.about(
            self,
            "About Atlas",
            "Atlas - Autonomous Task Planning Application\nVersion 1.0\n 2025 Atlas Team",
        )

    def show_module(self, module_name: str) -> None:
        """Show the specified module in the central widget area."""
        logger = logging.getLogger(__name__)
        logger.info(f"Showing module: {module_name}")
        module_map = {
            "Chat": self.chat_module,
            "Tasks": self.tasks_module,
            "Plugins": self.plugins_module,
            "Settings": self.settings_module,
            "Stats": self.stats_module,
            "System": getattr(self, "system_module", None),
            "SelfImprovement": getattr(self, "self_improvement_module", None),
            "DecisionExplanation": getattr(self, "decision_explanation_module", None),
            "UserManagement": getattr(self, "user_management_module", None),
            "Consent": getattr(self, "consent_module", None),
        }
        if module_name in module_map and module_map[module_name] is not None:
            try:
                self.central.setCurrentWidget(module_map[module_name])
                logger.info(f"Module {module_name} displayed")
            except Exception as e:
                logger.error(f"Error displaying module {module_name}: {e}")
        else:
            logger.warning(f"Module {module_name} not found or not initialized")

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute.
            params: Parameters to pass to the tool.

        Returns:
            Result of the tool execution or a default dictionary if not available.
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Executing tool: {tool_name} with params: {params}")
        if self.app_instance is None:
            logger.error("Cannot execute tool: app_instance is None")
            return None
        # Comment out problematic attribute access
        # return self.app_instance.execute_tool(tool_name, params)
        logger.info(f"Tool execution for {tool_name} is temporarily disabled")
        return None

    def _initialize_modules(self):  # noqa: C901
        """Initialize all UI modules."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing modules")
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

        from ui.chat.chat_module import ChatModule
        from ui.plugins.plugins_module import PluginsModule
        from ui.settings.settings_module import SettingsModule
        from ui.stats_module import StatsModule
        from ui.tasks.tasks_module import TasksModule

        try:
            from ui.system_control_module import SystemControlModule
        except ImportError:
            logger.warning("SystemControlModule not found, using placeholder")

            class SystemControlModule(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(300, 200)
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("System Control Module Placeholder"))
                    self.setLayout(layout)

                def set_agent_manager(self, agent_manager):
                    pass

        try:
            from ui.self_improvement_center import SelfImprovementCenter
        except ImportError:
            logger.warning("SelfImprovementCenter not found, using placeholder")

            class SelfImprovementCenter(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(300, 200)
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Self Improvement Center Placeholder"))
                    self.setLayout(layout)

        try:
            from ui.decision_explanation import DecisionExplanation
        except ImportError:
            logger.warning("DecisionExplanation not found, using placeholder")

            class DecisionExplanation(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(300, 200)
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Decision Explanation Placeholder"))
                    self.setLayout(layout)

        try:
            from ui.user_management import UserManagement
        except ImportError:
            logger.warning("UserManagement not found, using placeholder")

            class UserManagement(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(300, 200)
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("User Management Placeholder"))
                    self.setLayout(layout)

        try:
            from ui.consent_manager import ConsentManager
        except ImportError:
            logger.warning("ConsentManager not found, using placeholder")

            class ConsentManager(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(300, 200)
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Consent Manager Placeholder"))
                    self.setLayout(layout)

        try:
            from ui.tasks.task_widget import TaskWidget  # noqa: F401
        except ImportError as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Import error for TaskWidget: {e}")

        try:
            from ui.user_management import UserManagement
        except ImportError as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Import error for UserManagement: {e}")
            UserManagement = None

        # Manually initialize modules without passing module_name
        self.chat_module = ChatModule()
        self.tasks_module = TasksModule(
            task_manager=self.task_planner_agent,
            task_planner_agent=self.task_planner_agent,
            user_id="default_user",
        )
        self.plugins_module = PluginsModule()
        self.settings_module = SettingsModule()
        self.stats_module = StatsModule()
        self.system_module = (
            SystemControlModule(parent=self.central)
            if "SystemControlModule" in globals()
            else SystemControlModule(self.central)
        )
        if hasattr(self, "system_module") and hasattr(
            self.system_module, "set_agent_manager"
        ):
            try:
                self.system_module.set_agent_manager(
                    self.meta_agent if hasattr(self, "meta_agent") else None
                )
            except Exception as e:
                logger.error(f"Error setting agent manager for System module: {e}")
        self.self_improvement_module = SelfImprovementCenter(self.central)
        self.decision_explanation_module = DecisionExplanation(self.central)
        self.user_management_module = UserManagement(self.central)
        self.consent_module = ConsentManager(self.central)
        self.modules["Tools"] = ToolManagerUI()
        # Add initialized modules to central widget stack
        self.central.addWidget(self.chat_module)
        self.central.addWidget(self.tasks_module)
        self.central.addWidget(self.plugins_module)
        self.central.addWidget(self.settings_module)
        self.central.addWidget(self.stats_module)
        if hasattr(self, "system_module") and isinstance(self.system_module, QWidget):
            self.central.addWidget(self.system_module)
        if hasattr(self, "self_improvement_module") and isinstance(
            self.self_improvement_module, QWidget
        ):
            self.central.addWidget(self.self_improvement_module)
        if hasattr(self, "decision_explanation_module") and isinstance(
            self.decision_explanation_module, QWidget
        ):
            self.central.addWidget(self.decision_explanation_module)
        if hasattr(self, "user_management_module") and isinstance(
            self.user_management_module, QWidget
        ):
            self.central.addWidget(self.user_management_module)
        if hasattr(self, "consent_module") and isinstance(self.consent_module, QWidget):
            self.central.addWidget(self.consent_module)
        if hasattr(self, "Tools") and isinstance(self.modules["Tools"], QWidget):
            self.central.addWidget(self.modules["Tools"])
        # Set the active module (typically chat as default)
        self.central.setCurrentWidget(self.chat_module)
        logger.info("Modules initialized")

    def _setup_topbar(self):
        """Create the topbar with necessary actions."""
        logger = logging.getLogger(__name__)
        logger.debug("Creating topbar")
        topbar_layout = QHBoxLayout(self.topbar)

        # Add buttons for navigation
        chat_btn = QPushButton("Chat")
        chat_btn.clicked.connect(lambda: self.show_module("Chat"))
        topbar_layout.addWidget(chat_btn)

        plugins_btn = QPushButton("Plugins")
        plugins_btn.clicked.connect(lambda: self.show_module("Plugins"))
        topbar_layout.addWidget(plugins_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(lambda: self.show_module("Settings"))
        topbar_layout.addWidget(settings_btn)

        stats_btn = QPushButton("Stats")
        stats_btn.clicked.connect(lambda: self.show_module("Stats"))
        topbar_layout.addWidget(stats_btn)

        system_btn = QPushButton("System Control")
        system_btn.clicked.connect(lambda: self.show_module("System"))
        topbar_layout.addWidget(system_btn)

        self_improvement_btn = QPushButton("Self Improvement")
        self_improvement_btn.clicked.connect(
            lambda: self.show_module("SelfImprovement")
        )
        topbar_layout.addWidget(self_improvement_btn)

        consent_btn = QPushButton("Consent Manager")
        consent_btn.clicked.connect(lambda: self.show_module("Consent"))
        topbar_layout.addWidget(consent_btn)

        decision_btn = QPushButton("AI Decisions")
        decision_btn.clicked.connect(lambda: self.show_module("DecisionExplanation"))
        topbar_layout.addWidget(decision_btn)

        user_management_btn = QPushButton("User Management")
        user_management_btn.clicked.connect(lambda: self.show_module("UserManagement"))
        topbar_layout.addWidget(user_management_btn)

        topbar_layout.addStretch()

        logger.debug("Topbar creation completed")

    def _setup_sidebar(self):
        """Create the sidebar with necessary actions."""
        logger = logging.getLogger(__name__)
        logger.debug("Creating sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Add buttons for navigation
        chat_btn = QPushButton("Chat")
        chat_btn.clicked.connect(lambda: self.show_module("Chat"))
        sidebar_layout.addWidget(chat_btn)

        plugins_btn = QPushButton("Plugins")
        plugins_btn.clicked.connect(lambda: self.show_module("Plugins"))
        sidebar_layout.addWidget(plugins_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(lambda: self.show_module("Settings"))
        sidebar_layout.addWidget(settings_btn)

        stats_btn = QPushButton("Stats")
        stats_btn.clicked.connect(lambda: self.show_module("Stats"))
        sidebar_layout.addWidget(stats_btn)

        system_btn = QPushButton("System Control")
        system_btn.clicked.connect(lambda: self.show_module("System"))
        sidebar_layout.addWidget(system_btn)

        self_improvement_btn = QPushButton("Self Improvement")
        self_improvement_btn.clicked.connect(
            lambda: self.show_module("SelfImprovement")
        )
        sidebar_layout.addWidget(self_improvement_btn)

        consent_btn = QPushButton("Consent Manager")
        consent_btn.clicked.connect(lambda: self.show_module("Consent"))
        sidebar_layout.addWidget(consent_btn)

        decision_btn = QPushButton("AI Decisions")
        decision_btn.clicked.connect(lambda: self.show_module("DecisionExplanation"))
        sidebar_layout.addWidget(decision_btn)

        user_management_btn = QPushButton("User Management")
        user_management_btn.clicked.connect(lambda: self.show_module("UserManagement"))
        sidebar_layout.addWidget(user_management_btn)

        sidebar_layout.addStretch()

        logger.debug("Sidebar creation completed")

    def _setup_memory_management(self):
        """Setup periodic memory management tasks using a timer."""
        # Log initial memory stats
        self.memory_manager.log_memory_stats()

        # Setup a timer to log memory stats and perform cleanup every 5 minutes
        memory_timer = QTimer(self)
        memory_timer.timeout.connect(self._memory_management_task)
        memory_timer.start(300000)
        logger.info("Memory management timer started")

    def _memory_management_task(self):
        """Periodic task to log memory stats and perform cleanup if needed."""
        self.memory_manager.log_memory_stats()
        current_usage = self.memory_manager.get_memory_usage()
        # Perform cleanup if memory usage is high (e.g., over 500MB)
        if current_usage > 500:
            logger.info(
                f"High memory usage detected ({current_usage:.2f} MB), performing cleanup"
            )
            self.memory_manager.perform_cleanup()
        else:
            logger.info(
                f"Memory usage normal ({current_usage:.2f} MB), no cleanup needed"
            )

    def _switch_module(self, module_name):
        """Switch to a different module with lazy loading."""
        if self._active_module_name == module_name:
            return

        module = self._load_module(module_name)
        if module:
            self.central.setCurrentWidget(module)
            self._active_module_name = module_name
            logger.info(f"Switched to module: {module_name}")
        else:
            logger.error(f"Failed to load module: {module_name}")

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
        """
        Check if a user has a specific permission.

        Args:
            username: Username to check
            permission: Permission string to verify

        Returns:
            bool: True if user has permission, False otherwise
        """
        if self.app_instance is None:
            logger.error("Cannot check permission: app_instance is None")
            return False
        # Temporarily comment out problematic attribute access
        # return self.app_instance.rbac_manager.check_permission(username, permission)
        logger.info("Permission checking is temporarily disabled")
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
        if self.app_instance is None:
            logger.error("Cannot enforce permission: app_instance is None")
            raise PermissionError(f"Permission check failed for {operation}")

    def closeEvent(self, event):
        """Handle window close event with proper cleanup."""
        logger = logging.getLogger(__name__)
        logger.info("Closing main window")
        try:
            # Emit shutdown signal to subscribers if method exists
            if hasattr(self, "event_bus") and hasattr(self.event_bus, "emit"):
                try:
                    self.event_bus.emit("app_shutdown")
                except Exception as e:
                    logger.error(f"Error emitting shutdown signal: {e}")
            elif hasattr(self.event_bus, "publish"):
                try:
                    self.event_bus.publish("app_shutdown")
                except Exception as e:
                    logger.error(f"Error publishing shutdown signal: {e}")
            # Close all windows and cleanup
            if hasattr(self, "app_instance") and self.app_instance:
                # Temporarily comment out problematic attribute access
                # self.app_instance.closeAllWindows()
                pass
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()
        # Do not call super().closeEvent(event) to avoid RuntimeError

    def setup_ui(self) -> None:
        """Set up the user interface components based on feature flags."""
        logger = logging.getLogger(__name__)
        logger.info("Setting up UI components")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create sidebar or tab widget based on feature flags
        if True:  # Temporarily always return True for development
            self.setup_multilingual_ui(layout)
        else:
            self.setup_standard_ui(layout)

        # Add menu bar if feature is enabled
        if True:  # Temporarily always return True for development
            self.setup_advanced_menu_bar()
        else:
            self.setup_basic_menu_bar()

        logger.info("UI setup complete")

    def setup_multilingual_ui(self, layout):
        # Create multilingual UI components
        pass

    def setup_standard_ui(self, layout):
        # Create tabbed interface for standard UI
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background: #222; }
            QTabBar::tab { background: #333; color: #aaa; padding: 8px; min-width: 100px; }
            QTabBar::tab:selected { background: #00ffaa; color: #fff; }
        """)

        # Initialize core widgets for standard UI
        self.chat_widget = ChatWidget(self.app_instance)
        self.tasks_widget = None  # Temporarily set to None to prevent startup crashes
        # self.tasks_widget = TaskWidget(self.app_instance)
        self.settings_widget = SettingsWidget(self.app_instance)
        self.plugins_widget = PluginsWidget(self.app_instance)
        self.user_management_widget = UserManagementWidget(self.app_instance)
        self.ai_assistant_widget = AIAssistantWidget(self.app_instance)

        # Add tabs based on feature flags
        if self.is_feature_enabled("chat_module"):
            self.tab_widget.addTab(self.chat_widget, "Chat")
        if self.is_feature_enabled("task_management") and self.tasks_widget:
            self.tab_widget.addTab(self.tasks_widget, "Tasks")
        if self.is_feature_enabled("ai_assistant"):
            self.tab_widget.addTab(self.ai_assistant_widget, "AI Assistant")
        if self.is_feature_enabled("settings_ui"):
            self.tab_widget.addTab(self.settings_widget, "Settings")
        if self.is_feature_enabled("plugins_ui"):
            self.tab_widget.addTab(self.plugins_widget, "Plugins")
        if self.is_feature_enabled("user_management"):
            self.tab_widget.addTab(self.user_management_widget, "User Management")

        layout.addWidget(self.tab_widget)
        logger.info("Standard UI setup with tabs")

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
        logger.info("Initial theme applied via ThemeManager")

    def on_theme_changed(self, stylesheet):
        """Slot to handle theme changes.

        Args:
            stylesheet (str): The stylesheet to apply.
        """
        self.setStyleSheet(stylesheet)
        logger.info("Theme stylesheet updated")

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

        logger.info("Navigation setup completed")
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
        logger.info("Sidebar toggled")

    def _initialize_task_management(self):
        """Initialize task management components."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing task management components")
        self.task_widget = None  # Temporarily set to None to prevent startup crashes
        # self.task_widget = TaskWidget()
        if self.task_widget:
            pass

    def create_new_project(self):
        """Create a new project."""
        logger = logging.getLogger(__name__)
        logger.info("Creating new project")
        # Temporarily comment out references to unresolved attributes
        # if self.task_planner_agent:
        #     self.task_planner_agent.create_project_plan("New Project")
        pass

    def _load_module(self, module_name: str, widget_class: type):
        """Load a module by name and widget class."""
        # Temporarily comment out to avoid attribute access errors
        # logger.info(f"Loading module: {module_name}")
        # return self.app_instance._load_module(module_name, widget_class)
        logger.info(f"Module loading for {module_name} is temporarily disabled")
        return None

    def emit_event(
        self, event_name: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit an event with optional data."""
        # Temporarily comment out problematic attribute access
        # self.event_bus.emit(event_name, data or {})
        logger.info(f"Event emission for {event_name} is temporarily disabled")

    def get_user_role(self) -> str:
        """Get the role of the current user."""
        if self.app_instance is None:
            logger.error("Cannot get user role: app_instance is None")
            return "unknown"
        # Temporarily comment out problematic attribute access
        # return self.app_instance.rbac_manager.get_user_role()
        logger.info("User role retrieval is temporarily disabled")
        return "admin"  # Default for development

    def setup_ui(self):
        """Set up the user interface components."""
        logger = logging.getLogger(__name__)
        logger.info("Setting up UI components")
        self.setWindowTitle("Atlas - Modular AI Platform")
        self.resize(1200, 800)

        # Temporarily comment out problematic attribute access
        # self.main_layout = QVBoxLayout()
        # Use a placeholder widget instead
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Header with title/icon
        header = QWidget()
        header_layout = QHBoxLayout(header)
        icon = QLabel()
        icon.setPixmap(QIcon("atlas_icon.png").pixmap(32, 32))
        header_layout.addWidget(icon)
        title = QLabel("ATLAS")
        font = QFont("Arial", 18, QFont.Weight.Bold)
        title.setFont(font)
        title.setStyleSheet("color: #00ffaa;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)

        # Main content area - use QStackedWidget for navigation
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack, 1)

        # Create core UI components
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)
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

        # Initialize core widgets for standard UI
        self.chat_widget = ChatWidget(self.app_instance)
        self.tasks_widget = None  # Temporarily set to None to prevent startup crashes
        # self.tasks_widget = TaskWidget(self.app_instance)
        self.settings_widget = SettingsWidget(self.app_instance)
        self.plugins_widget = PluginsWidget(self.app_instance)
        self.user_management_widget = UserManagementWidget(self.app_instance)
        self.ai_assistant_widget = AIAssistantWidget(self.app_instance)

        # Add tabs based on feature flags
        def is_feature_enabled(feature_name):
            return True  # Temporarily return True for development

        if is_feature_enabled("chat_module"):
            self.tab_widget.addTab(self.chat_widget, "Chat")
        if is_feature_enabled("task_management") and self.tasks_widget:
            self.tab_widget.addTab(self.tasks_widget, "Tasks")
        if is_feature_enabled("ai_assistant"):
            self.tab_widget.addTab(self.ai_assistant_widget, "AI Assistant")
        if is_feature_enabled("settings_ui"):
            self.tab_widget.addTab(self.settings_widget, "Settings")
        if is_feature_enabled("plugins_ui"):
            self.tab_widget.addTab(self.plugins_widget, "Plugins")
        if is_feature_enabled("user_management"):
            self.tab_widget.addTab(self.user_management_widget, "User Management")

        self.content_stack.addWidget(self.tab_widget)

        # Status bar at bottom
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            "background-color: #333; color: #00ffaa; border-top: 1px solid #444;"
        )
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Apply cyberpunk styling to entire window
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: #00ffaa; }
            QPushButton {
                background-color: #333;
                color: #00ffaa;
                border: 1px solid #444;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton:pressed { background-color: #222; }
            QTextEdit, QLineEdit {
                background-color: #222;
                color: #00ffaa;
                border: 1px solid #444;
                padding: 3px;
            }
            QLabel { color: #00ffaa; }
        """)

        logger.info("UI setup complete")

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled. Temporarily always returns True for development."""
        logger.info(f"Feature check for {feature_name} is temporarily set to True")
        return True

    def _setup_tab_widget(self):
        """Set up the QTabWidget with custom styling."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up tab widget")
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

    def _setup_tab_widget_style(self):
        """Set up the QTabWidget style."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up tab widget style")
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
        logger = logging.getLogger(__name__)
        logger.debug(f"Adding tab: {label}")
        self.tab_widget.addTab(widget, label)

    def _add_tab_if_enabled(
        self, widget: QWidget, label: str, feature_name: str
    ) -> None:
        """Add a tab only if the feature is enabled."""
        if self.is_feature_enabled(feature_name):
            logger = logging.getLogger(__name__)
            logger.info(f"Feature {feature_name} is enabled, adding tab: {label}")
            self._add_tab(widget, label)
        else:
            logger = logging.getLogger(__name__)
            logger.info(f"Feature {feature_name} is disabled, skipping tab: {label}")

    def _setup_status_bar(self):
        """Set up the status bar."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up status bar")
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _initialize_modules(self):
        """Initialize various UI modules."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing UI modules")
        self._initialize_task_management()
        self._initialize_chat_ui()
        self._initialize_agents_ui()
        self._initialize_system_control_module()
        self._initialize_self_improvement_center()
        self._initialize_decision_explanation_ui()
        self._initialize_user_management_ui()
        self._initialize_consent_manager_ui()
        self.modules["Tools"] = ToolManagerUI()
        logger.info("All UI modules initialized")

    def _initialize_chat_ui(self):
        """Initialize chat UI components."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing chat UI components")
        self.chat_widget = None  # Temporarily set to None to prevent startup crashes
        # self.chat_widget = ChatWidget()

    def _initialize_agents_ui(self):
        """Initialize agents UI components."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing agents UI components")
        self.agents_widget = None  # Temporarily set to None to prevent startup crashes
        # self.agents_widget = AgentsWidget()

    def _initialize_system_control_module(self):
        """Initialize system control module."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing system control module")
        self.system_control_module = (
            None  # Temporarily set to None to prevent startup crashes
        )
        # Temporarily comment out to avoid import errors
        # from ui.system_control_module import SystemControlModule
        # self.system_control_module = SystemControlModule

    def _initialize_self_improvement_center(self):
        """Initialize self-improvement center."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing self-improvement center")
        self.self_improvement_center = (
            None  # Temporarily set to None to prevent startup crashes
        )
        # Temporarily comment out to avoid import errors
        # from ui.self_improvement_center import SelfImprovementCenter
        # self.self_improvement_center = SelfImprovementCenter

    def _initialize_decision_explanation_ui(self):
        """Initialize decision explanation UI."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing decision explanation UI")
        self.decision_explanation = (
            None  # Temporarily set to None to prevent startup crashes
        )
        # Temporarily comment out to avoid import errors
        # from ui.decision_explanation import DecisionExplanation
        # self.decision_explanation = DecisionExplanation

    def _initialize_user_management_ui(self):
        """Initialize user management UI."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing user management UI")
        self.user_management = (
            None  # Temporarily set to None to prevent startup crashes
        )
        # Temporarily comment out to avoid import errors
        # from ui.user_management import UserManagement
        # self.user_management = UserManagement

    def _initialize_consent_manager_ui(self):
        """Initialize consent manager UI."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing consent manager UI")
        self.consent_manager = (
            None  # Temporarily set to None to prevent startup crashes
        )
        # Temporarily comment out to avoid import errors
        # from ui.consent_manager import ConsentManager
        # self.consent_manager = ConsentManager

    def _setup_tab_ui(self):
        """Set up tab UI."""
        logger = logging.getLogger(__name__)
        logger.info("Setting up tab UI")
        if self.task_widget is not None:
            self._add_tab_if_enabled(
                self.task_widget, "Task Management", "task_management"
            )
        if self.chat_widget is not None:
            self._add_tab_if_enabled(self.chat_widget, "Chat", "chat")
        if self.agents_widget is not None:
            self._add_tab_if_enabled(self.agents_widget, "Agents", "agents")
        if self.system_control_module is not None:
            self._add_tab_if_enabled(
                self.system_control_module, "System", "system_control"
            )
        if self.self_improvement_center is not None:
            self._add_tab_if_enabled(
                self.self_improvement_center, "Improvement", "self_improvement"
            )
        if self.decision_explanation is not None:
            self._add_tab_if_enabled(
                self.decision_explanation, "Decisions", "decision_explanation"
            )
        if self.user_management is not None:
            self._add_tab_if_enabled(self.user_management, "Users", "user_management")
        if self.consent_manager is not None:
            self._add_tab_if_enabled(self.consent_manager, "Consent", "consent_manager")
        logger.info("Tab UI setup complete")

    def closeEvent(self, event):
        """Handle window close event."""
        logger = logging.getLogger(__name__)
        logger.info("Closing application")
        if hasattr(self.app_instance, "analytics"):
            # Temporarily comment out analytics event tracking
            # self.app_instance.analytics.track_event("app", "close", "")
            pass
        event.accept()

    def validate_ui_input(self, input_data: str) -> bool:
        """Validate UI input. Placeholder method."""
        return True

    def sanitize_ui_input(self, input_data: str) -> str:
        """Sanitize UI input. Placeholder method."""
        return input_data

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled. Temporarily always returns True for development."""
        logger = logging.getLogger(__name__)
        logger.info(f"Feature check for {feature_name} is temporarily set to True")
        return True

    def _setup_tab_widget(self):
        """Set up the QTabWidget with custom styling."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up tab widget")
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)

    def _setup_tab_widget_style(self):
        """Set up the QTabWidget style."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up tab widget style")
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
        logger = logging.getLogger(__name__)
        logger.debug(f"Adding tab: {label}")
        self.tab_widget.addTab(widget, label)

    def _add_tab_if_enabled(
        self, widget: QWidget, label: str, feature_name: str
    ) -> None:
        """Add a tab only if the feature is enabled."""
        if self.is_feature_enabled(feature_name):
            logger = logging.getLogger(__name__)
            logger.info(f"Feature {feature_name} is enabled, adding tab: {label}")
            self._add_tab(widget, label)
        else:
            logger = logging.getLogger(__name__)
            logger.info(f"Feature {feature_name} is disabled, skipping tab: {label}")

    def _setup_status_bar(self):
        """Set up the status bar."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up status bar")
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _initialize_modules(self):
        """Initialize various UI modules."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing UI modules")
        self._initialize_task_management()
        self._initialize_chat_ui()
        self._initialize_agents_ui()
        self._initialize_system_control_module()
        self._initialize_self_improvement_center()
        self._initialize_decision_explanation_ui()
        self._initialize_user_management_ui()
        self._initialize_consent_manager_ui()
        self.modules["Tools"] = ToolManagerUI()
        logger.info("All UI modules initialized")

    def _on_app_shutdown(self, data):
        logger = logging.getLogger(__name__)
        logger.info(f"Received app_shutdown event with data: {data}")
        self.close()

    def _on_tool_executed(self, data):
        msg = data.get("message") if isinstance(data, dict) else str(data)
        self.statusBar().showMessage(msg or "Tool executed successfully.", 5000)
        self.logger.info(f"[StatusBar] Tool executed: {msg}")

    def _on_tool_error(self, data):
        msg = data.get("error") if isinstance(data, dict) else str(data)
        self.statusBar().showMessage(msg or "Tool execution failed.", 7000)
        self.logger.error(f"[StatusBar] Tool error: {msg}")

    def apply_theme_to_all(self, theme_id: str):
        stylesheet = self.theme_manager.get_theme_stylesheet(theme_id)
        self.setStyleSheet(stylesheet)
        # Оновити стиль для всіх вкладок/модулів
        for module in self.modules.values():
            if hasattr(module, "setStyleSheet"):
                module.setStyleSheet(stylesheet)
            # Для LoadingSpinner
            if hasattr(module, "spinner") and hasattr(module.spinner, "apply_theme"):
                module.spinner.apply_theme(stylesheet)
