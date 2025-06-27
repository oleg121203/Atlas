import logging
import traceback
from typing import Any, Dict, Optional

# Import Atlas modules
from modules.agents.context_analyzer import ContextAnalyzer
from modules.agents.self_learning_agent import SelfLearningAgent
from modules.agents.task_planner_agent import TaskPlannerAgent
from PySide6.QtCore import (
    QObject,
    QRunnable,
    QSize,
    Qt,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QColor, QFont, QIcon, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.event_bus import EventBus
from core.feature_flags import is_feature_enabled
from ui.chat_module import ChatModule
from ui.consent_manager import ConsentManager
from ui.decision_explanation import DecisionExplanation
from ui.i18n import _, set_language
from ui.input_validation import sanitize_ui_input, validate_ui_input
from ui.plugin_manager import PluginManager
from ui.plugin_marketplace_module import PluginMarketplace
from ui.plugins_module import PluginsModule
from ui.settings_module import SettingsModule
from ui.stats_module import StatsModule
from ui.system_control_module import SystemControlModule
from ui.tasks_module import TasksModule
from utils.event_bus import EventBus
from utils.logger import get_logger
from utils.memory_management import MemoryManager

logger = get_logger()

print("DEBUG: Importing modules for main_window")
try:
    from PySide6.QtCore import (
        QObject,
        QRunnable,
        QSize,
        Qt,
        QThreadPool,
        QTimer,
        Signal,
        Slot,
    )
    from PySide6.QtGui import QColor, QFont, QIcon, QTextCharFormat
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDockWidget,
        QFrame,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QPushButton,
        QStackedWidget,
        QStatusBar,
        QTabWidget,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError as e:
    QT_AVAILABLE = False
    print(f"Failed to import Qt dependencies: {e}")

# Workaround for potential module misplacement
try:
    from PySide6.QtCore import (
        QObject,
        QRunnable,
        QSize,
        Qt,
        QThreadPool,
        QTimer,
        Signal,
        Slot,
    )
    from PySide6.QtGui import QColor, QFont, QIcon, QTextCharFormat
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDockWidget,
        QFrame,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QPushButton,
        QStackedWidget,
        QStatusBar,
        QTabWidget,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError as e:
    QT_AVAILABLE = False
    print(f"Failed to import Qt dependencies: {e}")

# Use absolute imports based on project structure
from modules.chat.chat_logic import ChatProcessor
from PySide6.QtWidgets import QAction, QTabBar

from core.event_bus import EventBus
from ui.ai_assistant_widget import AIAssistantWidget
from ui.chat_widget import ChatWidget
from ui.plugins_widget import PluginsWidget
from ui.settings_widget import SettingsWidget
from ui.task_widget import TaskWidget
from ui.user_management_widget import UserManagementWidget
from utils.event_bus import EventBus
from utils.logger import get_logger

logger = logging.getLogger(__name__)

print("DEBUG: Importing modules for main_window")
try:
    from ui.chat_module import ChatModule

    print("DEBUG: Imported ChatModule")
    from ui.tasks_module import TasksModule

    print("DEBUG: Imported TasksModule")
    from ui.plugins_module import PluginsModule

    print("DEBUG: Imported PluginsModule")
    from ui.settings_module import SettingsModule

    print("DEBUG: Imported SettingsModule")
    from ui.stats_module import StatsModule

    print("DEBUG: Imported StatsModule")
    from ui.plugin_manager import PluginManager

    print("DEBUG: Imported PluginManager")
    from ui.i18n import _, set_language

    print("DEBUG: Imported i18n")
    from ui.system_control_module import SystemControlModule

    print("DEBUG: Imported SystemControlModule")
    from ui.plugin_marketplace_module import PluginMarketplace

    print("DEBUG: Imported PluginMarketplace")
    from ui.consent_manager import ConsentManager

    print("DEBUG: Imported ConsentManager")
    from ui.decision_explanation import DecisionExplanation

    print("DEBUG: Imported DecisionExplanation")
except ImportError as e:
    print(f"DEBUG: Import error: {e}")
    traceback.print_exc()

try:
    from ui.self_improvement_center import SelfImprovementCenter

    print("DEBUG: Imported SelfImprovementCenter")
except ImportError as e:
    print(f"DEBUG: Import error for SelfImprovementCenter: {e}")
    traceback.print_exc()

    # Fallback for missing module
    class SelfImprovementCenter(QWidget):
        def __init__(self, *args, **kwargs):
            logger.warning(
                "Fallback SelfImprovementCenter used, original module not found"
            )
            super().__init__()


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
        self, meta_agent: Optional[Any] = None, parent: Optional[QWidget] = None
    ):
        print("DEBUG: Starting AtlasMainWindow initialization")
        super().__init__(parent)
        logger.debug("Starting AtlasMainWindow initialization")
        self.meta_agent = meta_agent
        self.setWindowTitle("Atlas - Autonomous Task Planning")
        self.setGeometry(100, 100, 1200, 800)
        # Initialize core components
        from PySide6.QtWidgets import QApplication

        self.app_instance = QApplication.instance()
        self.event_bus = EventBus()
        self.memory_manager = MemoryManager()
        self.modules = {}
        self.self_learning_agent = SelfLearningAgent(memory_manager=self.memory_manager)
        self.task_planner_agent = TaskPlannerAgent(memory_manager=self.memory_manager)
        self.context_analyzer = ContextAnalyzer(memory_manager=self.memory_manager)
        self.chat_processor = ChatProcessor()  # Update initialization of ChatProcessor
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        self.sidebar = QToolBar()
        self.sidebar.setOrientation(Qt.Vertical)
        self.topbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.topbar)
        self.dock = QDockWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self.sidebar)
        # Delay UI initialization to ensure QApplication is ready
        QTimer.singleShot(0, self._init_ui)
        logger.debug("AtlasMainWindow initialization completed")

    def _init_ui(self):
        """Initialize UI elements after QApplication is ready."""
        logger.debug("Initializing UI elements")
        self.setStyleSheet("""
            QMainWindow {
                background: #121518;
                color: #fff;
            }
            QToolBar {
                background: #181c20;
                border: 0px;
                spacing: 8px;
            }
            QToolButton {
                background: transparent;
                color: #fff;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QToolButton:hover {
                background: #00ff7f22;
                border: 1px solid #00ff7f44;
            }
            QToolButton:pressed {
                background: #00ff7f11;
            }
            QLineEdit {
                background: #181c20;
                color: #fff;
                border: 1px solid #00fff7;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff7f;
            }
            QPushButton {
                background: transparent;
                color: #fff;
                border: 1px solid #00fff7;
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #00ff7f11;
            }
            QPushButton:pressed {
                background: #00ff7f22;
            }
            QLabel {
                color: #fff;
            }
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
        logger.debug("Creating menu bar")
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)  # Ensure menu bar is visible on macOS

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
        logger.debug(f"Executing tool: {tool_name} with params: {params}")
        if hasattr(self.meta_agent, "execute_tool"):
            return self.meta_agent.execute_tool(tool_name, params)
        else:
            logger.warning("meta_agent does not have execute_tool method")
            return {"status": "error", "message": "Tool execution not available"}

    def _initialize_modules(self):
        """Initialize all UI modules."""
        logger.info("Initializing modules")
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

        from ui.chat_module import ChatModule
        from ui.plugins_module import PluginsModule
        from ui.settings_module import SettingsModule
        from ui.stats_module import StatsModule
        from ui.tasks_module import TasksModule

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
                    pass  # Placeholder method

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
        # Set the active module (typically chat as default)
        self.central.setCurrentWidget(self.chat_module)
        logger.info("Modules initialized")

    def _setup_topbar(self):
        """Create the topbar with necessary actions."""
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
        memory_timer.start(300000)  # 5 minutes in milliseconds
        print("DEBUG: Memory management timer started")

    def _memory_management_task(self):
        """Periodic task to log memory stats and perform cleanup if needed."""
        self.memory_manager.log_memory_stats()
        current_usage = self.memory_manager.get_memory_usage()
        # Perform cleanup if memory usage is high (e.g., over 500MB)
        if current_usage > 500:
            print(
                f"DEBUG: High memory usage detected ({current_usage:.2f} MB), performing cleanup"
            )
            self.memory_manager.perform_cleanup()
        else:
            print(
                f"DEBUG: Memory usage normal ({current_usage:.2f} MB), no cleanup needed"
            )

    def _switch_module(self, module_name):
        """Switch to a different module with lazy loading."""
        if self._active_module_name == module_name:
            return

        module = self._load_module(module_name)
        if module:
            self.central.setCurrentWidget(module)
            self._active_module_name = module_name
            logger.debug(f"Switched to module: {module_name}")
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
        return validate_ui_input(value, input_type, field_name)

    def sanitize_input(self, value: str) -> str:
        """
        Sanitize user input to remove potentially dangerous content.

        Args:
            value: Input value to sanitize

        Returns:
            str: Sanitized input value
        """
        return sanitize_ui_input(value)

    def check_permission(self, username: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            username: Username to check
            permission: Permission string to verify

        Returns:
            bool: True if user has permission, False otherwise
        """
        try:
            from security.rbac import Permission

            perm = Permission(permission)
            return self.app_instance.rbac_manager.check_permission(username, perm)
        except ValueError:
            logger.error("Invalid permission requested: %s", permission)
            return False

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
        try:
            from security.rbac import Permission

            perm = Permission(permission)
            self.app_instance.rbac_manager.enforce_permission(username, perm, operation)
        except ValueError:
            logger.error("Invalid permission requested for enforcement: %s", permission)
            raise PermissionError(f"Invalid permission check for {operation}")

    def closeEvent(self, event):
        """Handle window close event with proper cleanup."""
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
                self.app_instance.closeAllWindows()
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()
        # Do not call super().closeEvent(event) to avoid RuntimeError

    def setup_ui(self) -> None:
        """Set up the user interface components based on feature flags."""
        self.logger.info("Setting up UI components")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create sidebar or tab widget based on feature flags
        if is_feature_enabled("multilingual_ui"):
            self.setup_multilingual_ui(layout)
        else:
            self.setup_standard_ui(layout)

        # Add menu bar if feature is enabled
        if is_feature_enabled("advanced_settings"):
            self.setup_advanced_menu_bar()
        else:
            self.setup_basic_menu_bar()

        self.logger.info("UI setup complete")

    def setup_multilingual_ui(self, layout):
        # Create multilingual UI components
        pass

    def setup_standard_ui(self, layout):
        # Create standard UI components
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Initialize core widgets for standard UI
        self.chat_widget = ChatWidget(self.app_instance)
        self.tasks_widget = TaskWidget(self.app_instance)
        self.settings_widget = SettingsWidget(self.app_instance)
        self.plugins_widget = PluginsWidget(self.app_instance)
        self.user_management_widget = UserManagementWidget(self.app_instance)
        self.ai_assistant_widget = AIAssistantWidget(self.app_instance)

        # Add tabs to tab widget with feature flag checks
        if is_feature_enabled("chat_module"):
            self.tab_widget.addTab(self.chat_widget, "Chat")
        if is_feature_enabled("task_management"):
            self.tab_widget.addTab(self.tasks_widget, "Tasks")
        if is_feature_enabled("ai_assistant"):
            self.tab_widget.addTab(self.ai_assistant_widget, "AI Assistant")
        if is_feature_enabled("settings_ui"):
            self.tab_widget.addTab(self.settings_widget, "Settings")
        if is_feature_enabled("plugin_system"):
            self.tab_widget.addTab(self.plugins_widget, "Plugins")

        # Add User Management tab with permission check
        if self.app_instance.rbac_manager.has_permission("manage_users"):
            self.tab_widget.addTab(self.user_management_widget, "User Management")

        self.logger.info("Standard UI setup with tabs")

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
        self.theme_manager.apply_theme(self.theme_manager.get_current_theme())
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
            self.sidebar.setFixedWidth(60)  # Collapsed width
            self.sidebar_toggle.setText("▶")
        else:
            self.sidebar.setFixedWidth(250)  # Expanded width
            self.sidebar_toggle.setText("◀")
        logger.info("Sidebar toggled")
