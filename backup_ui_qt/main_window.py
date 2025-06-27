import logging
import time
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
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QTextCharFormat
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

from core.event_bus import EventBus
from ui.chat_module import ChatModule
from ui.consent_manager import ConsentManager
from ui.decision_explanation import DecisionExplanation
from ui.i18n import _, set_language
from ui.plugin_manager import PluginManager
from ui.plugin_marketplace_module import PluginMarketplace
from ui.plugins_module import PluginsModule
from ui.self_improvement_center import SelfImprovementCenter
from ui.settings_module import SettingsModule
from ui.stats_module import StatsModule
from ui.system_control_module import SystemControlModule
from ui.tasks_module import TasksModule
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
    from ui.self_improvement_center import SelfImprovementCenter

    print("DEBUG: Imported SelfImprovementCenter")
    from ui.plugin_marketplace_module import PluginMarketplace

    print("DEBUG: Imported PluginMarketplace")
    from ui.consent_manager import ConsentManager

    print("DEBUG: Imported ConsentManager")
    from ui.decision_explanation import DecisionExplanation

    print("DEBUG: Imported DecisionExplanation")
except ImportError as e:
    print(f"DEBUG: Import error: {e}")
    traceback.print_exc()


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
        self.event_bus = EventBus()
        self.memory_manager = MemoryManager()
        self.self_learning_agent = SelfLearningAgent(memory_manager=self.memory_manager)
        self.task_planner_agent = TaskPlannerAgent(memory_manager=self.memory_manager)
        self.context_analyzer = ContextAnalyzer(memory_manager=self.memory_manager)
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        self.dock = QDockWidget("Sidebar", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.sidebar = QWidget()
        self.dock.setWidget(self.sidebar)
        self._is_closing = False
        self._module_loading_in_progress = False
        self._active_module_name = None
        self._module_load_times = {}
        self._chat_module = None
        self._tasks_module = None
        self._plugins_module = None
        self._settings_module = None
        self._stats_module = None
        self._system_control_module = None
        self._self_improvement_module = None
        self._plugin_marketplace_module = None
        self._consent_manager_module = None
        self._decision_explanation_module = None
        self._init_ui()
        logger.debug("AtlasMainWindow initialization completed")

    def _init_ui(self):
        """Initialize the UI components."""
        logger.debug("Starting UI initialization")
        self._create_menu_bar()
        self._initialize_modules()
        self._create_sidebar()
        self._setup_memory_management()
        logger.debug("UI initialization completed")

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
        """Show the specified module in the central widget.

        Args:
            module_name: Name of the module to display.
        """
        if module_name in self.modules:
            self.central.setCurrentWidget(self.modules[module_name])
            logger.debug(f"Switched to module: {module_name}")
        else:
            logger.warning(f"Module not found: {module_name}")

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
        """Initialize all modules and add them to the central widget."""
        logger.debug("Starting modules initialization")
        # Load Chat and Tasks modules to debug segmentation fault
        logger.debug("Loading Chat and Tasks modules for debugging")

        # Initialize modules dictionary if not already defined
        if not hasattr(self, "modules"):
            self.modules = {}

        module_names = ["chat", "tasks"]
        for module_name in module_names:
            logger.debug(f"Loading module: {module_name}")
            module = self._load_module(module_name)
            if module:
                logger.debug(f"Adding module {module_name} to central widget")
                self.central.addWidget(module)
                self.modules[module_name] = module
                if module_name == "chat":
                    self.central.setCurrentWidget(module)
            else:
                logger.warning(f"Module not loaded: {module_name}")

        # Keep other modules disabled for now
        logger.info("Other modules remain disabled for debugging")
        return

        # Original module loading logic commented out
        # module_load_order = [
        #     "chat",
        #     "tasks",
        #     "plugins",
        #     "settings",
        #     "stats",
        #     "system_control",
        #     "self_improvement",
        #     "consent_manager",
        #     "decision_explanation"
        # ]
        #
        # for module_name in module_load_order:
        #     logger.debug(f"Loading module: {module_name}")
        #     module = self._load_module(module_name)
        #     if module:
        #         logger.debug(f"Adding module {module_name} to central widget")
        #         self.central.addWidget(module)
        #         self.modules[module_name] = module
        #     else:
        #         logger.warning(f"Module not loaded: {module_name}")
        #
        # if self.modules:
        #     self.central.setCurrentWidget(list(self.modules.values())[0])

    def _load_module(self, module_name):
        """Load a module lazily if not already loaded."""
        if self._module_loading_in_progress:
            logger.debug(f"Module loading already in progress, skipping {module_name}")
            return None
        if module_name in self._module_load_times:
            return getattr(self, f"_{module_name}_module")

        self._module_loading_in_progress = True
        start_time = time.time()
        logger.debug(f"Loading module: {module_name}")
        try:
            if module_name == "chat":
                from ui.chat_module import ChatModule

                self._chat_module = ChatModule(self)
            elif module_name == "tasks":
                from ui.tasks_module import TasksModule

                self._tasks_module = TasksModule(
                    self.task_planner_agent,
                    self.task_planner_agent,
                    user_id="default_user",
                    parent=self,
                )
            elif module_name == "plugins":
                from ui.plugins_module import PluginsModule

                self._plugins_module = PluginsModule(self)
            elif module_name == "settings":
                from ui.settings_module import SettingsModule

                self._settings_module = SettingsModule(self)
            elif module_name == "stats":
                from ui.stats_module import StatsModule

                self._stats_module = StatsModule(self)
            elif module_name == "system_control":
                from ui.system_control_module import SystemControlModule

                self._system_control_module = SystemControlModule(self)
            elif module_name == "self_improvement":
                from ui.self_improvement_center import SelfImprovementCenter

                self._self_improvement_center_module = SelfImprovementCenter(self)
            elif module_name == "plugin_marketplace":
                from ui.plugin_marketplace_module import PluginMarketplace

                self._plugin_marketplace_module = PluginMarketplace(self)
            elif module_name == "consent_manager":
                from ui.consent_manager import ConsentManager

                self._consent_manager_module = ConsentManager(self)
            elif module_name == "decision_explanation":
                from ui.decision_explanation import DecisionExplanation

                self._decision_explanation_module = DecisionExplanation(self)

            load_time = time.time() - start_time
            self._module_load_times[module_name] = load_time
            logger.info(f"Loaded module {module_name} in {load_time:.2f} seconds")
            return getattr(self, f"_{module_name}_module")
        finally:
            self._module_loading_in_progress = False

    def _create_sidebar(self):
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
