from typing import Optional, Any
from PySide6.QtWidgets import QMainWindow, QToolBar, QStackedWidget, QDockWidget, QLabel, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMenuBar, QMenu, QFrame, QCheckBox
from PySide6.QtCore import Qt, QSize, QTimer, Signal, Slot, QThreadPool, QRunnable, QObject
from PySide6.QtGui import QIcon, QFont, QTextCharFormat, QColor

import sys
import os
import json
import logging
import traceback
import threading

# Import Atlas modules
from agents.task_planner_agent import TaskPlannerAgent
from agents.context_analyzer import ContextAnalyzer
from chat.chat_logic import ChatProcessor
from tasks.task_manager import TaskManager
from plugins.plugin_manager import PluginManager
from ui_qt.tasks_module import TasksModule
from ui_qt.chat_module import ChatModule
from ui_qt.plugins_module import PluginsModule
from utils.logger import get_logger
from utils.memory_management import MemoryManager
from utils.event_bus import EventBus
from ui_qt.module_communication import EVENT_BUS, register_module_events, publish_module_event
from utils.memory_management import MEMORY_MANAGER
from core.event_bus import EventBus
from core.agents.meta_agent import MetaAgent
from agents.self_learning_agent import SelfLearningAgent
from agents.task_planner_agent import TaskPlannerAgent
from agents.context_analyzer import ContextAnalyzer

logger = get_logger()

print("DEBUG: Importing modules for main_window")
try:
    from ui_qt.chat_module import ChatModule
    print("DEBUG: Imported ChatModule")
    from ui_qt.tasks_module import TasksModule
    print("DEBUG: Imported TasksModule")
    from ui_qt.agents_module import AgentsModule
    print("DEBUG: Imported AgentsModule")
    from ui_qt.plugins_module import PluginsModule
    print("DEBUG: Imported PluginsModule")
    from ui_qt.settings_module import SettingsModule
    print("DEBUG: Imported SettingsModule")
    from ui_qt.stats_module import StatsModule
    print("DEBUG: Imported StatsModule")
    from ui_qt.plugin_manager import PluginManager
    print("DEBUG: Imported PluginManager")
    from ui_qt.i18n import _, set_language
    print("DEBUG: Imported i18n")
    from ui_qt.system_control_module import SystemControlModule
    print("DEBUG: Imported SystemControlModule")
    from ui.self_improvement_center import SelfImprovementCenter
    print("DEBUG: Imported SelfImprovementCenter")
    from ui_qt.plugin_marketplace_module import PluginMarketplace
    print("DEBUG: Imported PluginMarketplace")
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

    def __init__(self, meta_agent: MetaAgent, parent=None):
        print("DEBUG: Starting AtlasMainWindow initialization")
        super().__init__(parent)
        self.meta_agent = meta_agent
        print("DEBUG: Meta agent assigned")
        self.setWindowTitle("Atlas")
        print("DEBUG: Window title set")
        self.setGeometry(100, 100, 1200, 800)
        print("DEBUG: Window geometry set")
        self.event_bus = EventBus()
        print("DEBUG: Event bus initialized")
        self.memory_manager = MEMORY_MANAGER
        print("DEBUG: Memory manager initialized")
        self.self_learning_agent = SelfLearningAgent(memory_manager=self.memory_manager)
        print("DEBUG: Self-learning agent initialized")
        self.task_planner_agent = TaskPlannerAgent(memory_manager=self.memory_manager, self_learning_agent=self.self_learning_agent)
        print("DEBUG: Task planner agent initialized")
        self.context_analyzer = ContextAnalyzer(memory_manager=self.memory_manager)
        print("DEBUG: Context analyzer initialized")
        self._init_ui()
        print("DEBUG: UI initialization completed")
        self._setup_memory_management()
        print("DEBUG: Memory management setup completed")

    def _init_ui(self):
        """Initialize the user interface components."""
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create menu bar
        self._create_menu_bar()

        # Create tab widget for different modules
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Initialize modules
        self.chat_module = ChatModule(self.chat_processor, self.current_user_id)
        self.tasks_module = TasksModule(self.task_manager, self.task_planner_agent, self.current_user_id)
        self.plugins_module = PluginsModule(self.plugin_manager)

        # Add tabs
        self.tabs.addTab(self.chat_module, "Chat")
        self.tabs.addTab(self.tasks_module, "Tasks & Plans")
        self.tabs.addTab(self.plugins_module, "Plugins")

        # Create status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Create AI status widget for the status bar
        self.ai_status_widget = QWidget()
        ai_status_layout = QHBoxLayout(self.ai_status_widget)
        ai_status_label = QLabel("AI Status:")
        self.ai_status_indicator = QLabel("Operational")
        self.ai_status_indicator.setStyleSheet("color: green;")
        ai_status_layout.addWidget(ai_status_label)
        ai_status_layout.addWidget(self.ai_status_indicator)
        self.status_bar.addPermanentWidget(self.ai_status_widget)

        logger.debug("UI initialization completed")

    def on_task_updated(self, task_data):
        """Handle task update events."""
        logger.debug("Task updated event received: %s", task_data)
        self.tasks_module.update_task_list()

    def on_chat_message(self, message_data):
        """Handle chat message events."""
        logger.debug("Chat message event received: %s", message_data)
        if isinstance(message_data, dict) and message_data.get("message_type") == "ai_plan_suggestion":
            plan_id = message_data.get("plan_id")
            plan_details = self.task_planner_agent.get_plan_details(plan_id) if plan_id else None
            if plan_details:
                self.tasks_module.display_plan_details(plan_details)

    def on_plan_updated(self, plan_data):
        """Handle plan update events."""
        logger.debug("Plan updated event received: %s", plan_data)
        if isinstance(plan_data, dict):
            plan_id = plan_data.get("plan_id", "")
            if plan_id:
                plan_details = self.task_planner_agent.get_plan_details(plan_id)
                if plan_details:
                    self.tasks_module.display_plan_details(plan_details)
                    self.tasks_module.update_plan_list()

    def update_ui_elements(self):
        """Periodically update UI elements."""
        active_plans = self.task_planner_agent.get_active_plans(self.current_user_id)
        if active_plans:
            self.status_label.setText(f"Active Plans: {len(active_plans)}")
        else:
            self.status_label.setText("No active plans")

    def refresh_context(self):
        """Periodically refresh user context."""
        try:
            self.context_analyzer.refresh_current_state(self.current_user_id)
            logger.debug("User context refreshed")
        except Exception as e:
            logger.error(f"Error refreshing context: {e}")

    def _init_modules(self, meta_agent=None):
        """Initialize application modules with error handling and fallbacks."""
        print("DEBUG: Starting modules initialization")
        self.modules = {}
        
        # Safely retrieve agent_manager from meta_agent if available
        agent_manager = None
        if meta_agent is not None:
            try:
                agent_manager = meta_agent.agent_manager
                print("DEBUG: AgentManager retrieved from meta_agent")
            except AttributeError:
                print("WARNING: meta_agent does not have agent_manager attribute")
        else:
            print("WARNING: meta_agent not provided, using None")

        try:
            self.modules["chat"] = ChatModule()
            print("DEBUG: Chat module initialized")
            register_module_events(self.modules["chat"], {
                "task_added": lambda data: print(f"DEBUG: Chat received task_added event with data: {data}"),
                "settings_updated": lambda data: print(f"DEBUG: Chat received settings_updated event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize ChatModule: {e}")
            self.modules["chat"] = QWidget()
            self._log_recovery_action("ChatModule", str(e))

        try:
            self.modules["agents"] = AgentsModule()
            print("DEBUG: Agents module initialized")
            register_module_events(self.modules["agents"], {
                "agent_updated": lambda data: print(f"DEBUG: Agents received agent_updated event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize AgentsModule: {e}")
            self.modules["agents"] = QWidget()
            self._log_recovery_action("AgentsModule", str(e))

        try:
            self.modules["tasks"] = TasksModule()
            print("DEBUG: Tasks module initialized")
            register_module_events(self.modules["tasks"], {
                "task_added": lambda data: print(f"DEBUG: Tasks received task_added event with data: {data}"),
                "task_completed": lambda data: print(f"DEBUG: Tasks received task_completed event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize TasksModule: {e}")
            self.modules["tasks"] = QWidget()
            self._log_recovery_action("TasksModule", str(e))

        try:
            self.modules["plugins"] = PluginsModule()
            print("DEBUG: Plugins module initialized")
            register_module_events(self.modules["plugins"], {
                "plugin_activated": lambda data: print(f"DEBUG: Plugins received plugin_activated event with data: {data}"),
                "plugin_deactivated": lambda data: print(f"DEBUG: Plugins received plugin_deactivated event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize PluginsModule: {e}")
            self.modules["plugins"] = QWidget()
            self._log_recovery_action("PluginsModule", str(e))

        try:
            plugin_manager = getattr(self.meta_agent, 'plugin_manager', None)
            if plugin_manager:
                self.modules['marketplace'] = PluginMarketplace(plugin_manager=plugin_manager, parent=self)
                register_module_events(self.modules['marketplace'], {
                    "plugin_installed": lambda data: print(f"DEBUG: Plugin Marketplace received plugin_installed event with data: {data}"),
                    "plugin_updated": lambda data: print(f"DEBUG: Plugin Marketplace received plugin_updated event with data: {data}")
                })
                print("DEBUG: Plugin Marketplace module initialized")
            else:
                print("WARNING: plugin_manager not available for Plugin Marketplace")
                self.modules['marketplace'] = QWidget()
                print("DEBUG: Fallback widget created for Plugin Marketplace")
        except Exception as e:
            print(f"ERROR: Failed to initialize PluginMarketplaceModule: {e}")
            self.modules['marketplace'] = QWidget()
            print("DEBUG: Fallback widget created for Plugin Marketplace")
            self._log_recovery_action("PluginMarketplaceModule", str(e))

        try:
            self.modules["settings"] = SettingsModule()
            print("DEBUG: Settings module initialized")
            register_module_events(self.modules["settings"], {
                "settings_updated": lambda data: print(f"DEBUG: Settings received settings_updated event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize SettingsModule: {e}")
            self.modules["settings"] = QWidget()
            self._log_recovery_action("SettingsModule", str(e))

        try:
            self.modules["stats"] = StatsModule()
            print("DEBUG: Stats module initialized")
            register_module_events(self.modules["stats"], {
                "stats_updated": lambda data: print(f"DEBUG: Stats received stats_updated event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize StatsModule: {e}")
            self.modules["stats"] = QWidget()
            self._log_recovery_action("StatsModule", str(e))

        # Initialize SystemControlModule with agent_manager if available
        try:
            if agent_manager:
                self.modules["system"] = SystemControlModule(agent_manager=agent_manager)
            else:
                self.modules["system"] = SystemControlModule()
                print("WARNING: AgentManager not available, using None")
            print("DEBUG: SystemControl module initialized")
            register_module_events(self.modules["system"], {
                "system_event": lambda data: print(f"DEBUG: System received system_event with data: {data}")
            })
        except Exception as e:
            print(f"ERROR: Failed to initialize SystemControlModule: {e}")
            self.modules["system"] = QWidget()
            self._log_recovery_action("SystemControlModule", str(e))

        # Initialize SelfImprovementCenter with meta_agent if available
        try:
            if meta_agent:
                self.self_improvement_module = SelfImprovementCenter(meta_agent=meta_agent)
                print("DEBUG: SelfImprovementCenter initialized")
                register_module_events(self.self_improvement_module, {
                    "improvement_update": lambda data: print(f"DEBUG: SelfImprovement received improvement_update event with data: {data}")
                })
            else:
                print("WARNING: meta_agent not available for SelfImprovementCenter")
                self.self_improvement_module = QWidget()
                print("DEBUG: Fallback widget created for SelfImprovementCenter")
        except Exception as e:
            print(f"ERROR: Failed to initialize SelfImprovementCenter: {e}")
            self.self_improvement_module = QWidget()
            print("DEBUG: Fallback widget created for SelfImprovementCenter")
            self._log_recovery_action("SelfImprovementCenter", str(e))

        # Add modules to central widget
        try:
            self.central.addWidget(self.modules["chat"])
            print("DEBUG: Chat module added to central widget")
            self.central.addWidget(self.modules["agents"])
            print("DEBUG: Agents module added to central widget")
            self.central.addWidget(self.modules["tasks"])
            print("DEBUG: Tasks module added to central widget")
            self.central.addWidget(self.modules["plugins"])
            print("DEBUG: Plugins module added to central widget")
            self.central.addWidget(self.modules["marketplace"])
            print("DEBUG: Plugin Marketplace module added to central widget")
            self.central.addWidget(self.modules["settings"])
            print("DEBUG: Settings module added to central widget")
            self.central.addWidget(self.modules["stats"])
            print("DEBUG: Stats module added to central widget")
            self.central.addWidget(self.modules["system"])
            print("DEBUG: System module added to central widget")
            self.central.addWidget(self.self_improvement_module)
            print("DEBUG: SelfImprovement module added to central widget")
        except Exception as e:
            print(f"ERROR: Failed to add modules to central widget: {e}")
            self._log_recovery_action("CentralWidgetAddition", str(e))

        # Connect PluginManager to modules if available
        try:
            if hasattr(self, 'plugin_manager'):
                if "plugins" in self.modules and isinstance(self.modules["plugins"], PluginsModule):
                    self.modules["plugins"].set_plugin_manager(self.plugin_manager)
                    print("DEBUG: PluginManager set for plugins module")
                if "tasks" in self.modules and isinstance(self.modules["tasks"], TasksModule):
                    self.modules["tasks"].set_plugin_manager(self.plugin_manager)
                    print("DEBUG: PluginManager set for tasks module")
                if "chat" in self.modules and isinstance(self.modules["chat"], ChatModule):
                    self.modules["chat"].set_plugin_manager(self.plugin_manager)
                    print("DEBUG: PluginManager set for chat module")
                if "agents" in self.modules and isinstance(self.modules["agents"], AgentsModule):
                    self.modules["agents"].set_plugin_manager(self.plugin_manager)
                    print("DEBUG: PluginManager set for agents module")
                if "settings" in self.modules and isinstance(self.modules["settings"], SettingsModule):
                    self.modules["settings"].set_plugin_manager(self.plugin_manager)
                    print("DEBUG: PluginManager set for settings module")
            else:
                print("WARNING: plugin_manager not available")
        except Exception as e:
            print(f"ERROR: Failed to connect PluginManager to modules: {e}")
            self._log_recovery_action("PluginManagerConnection", str(e))

        # Initialize sidebar actions for each module
        try:
            self._init_sidebar_icons()
            print("DEBUG: Sidebar actions initialized")
        except Exception as e:
            print(f"ERROR: Failed to initialize sidebar actions: {e}")
            self._log_recovery_action("SidebarActionsInitialization", str(e))

        # Set initial module
        try:
            self.central.setCurrentWidget(self.modules["chat"])
            print("DEBUG: Central area current widget set")
        except Exception as e:
            print(f"ERROR: Failed to set initial module: {e}")
            self._log_recovery_action("InitialModuleSetting", str(e))

        print("DEBUG: Modules initialization finished")

    def _init_sidebar_icons(self):
        """Initialize sidebar icons for each module."""
        self._add_sidebar_action(_("Chat"), "chat", "💬")
        print("DEBUG: Chat sidebar action added")
        self._add_sidebar_action(_("Agents"), "agents", "🤖")
        print("DEBUG: Agents sidebar action added")
        self._add_sidebar_action(_("Tasks"), "tasks", "✅")
        print("DEBUG: Tasks sidebar action added")
        self._add_sidebar_action(_("Plugins"), "plugins", "🔌")
        print("DEBUG: Plugins sidebar action added")
        self._add_sidebar_action(_("Marketplace"), "marketplace", "🛍️")
        print("DEBUG: Marketplace sidebar action added")
        self._add_sidebar_action(_("Settings"), "settings", "⚙️")
        print("DEBUG: Settings sidebar action added")
        self._add_sidebar_action(_("Stats"), "stats", "📊")
        print("DEBUG: Stats sidebar action added")
        self._add_sidebar_action(_("System Control"), "system", "🖥️")
        print("DEBUG: System control sidebar action added")
        # Add sidebar action for Self-Improvement Center
        if hasattr(self, 'self_improvement_module'):
            self._add_sidebar_action(_("Self-Improvement"), "self_improvement", "🛠️")
            print("DEBUG: Self improvement sidebar action added")

    def _add_sidebar_action(self, text, module_name, emoji):
        """Add an action to the sidebar with the specified text, module name, and emoji icon."""
        action = QAction(emoji + " " + text, self)
        action.setData(module_name)
        action.triggered.connect(lambda: self._switch_module(module_name))
        self.sidebar.addAction(action)

    def _switch_module(self, module_name):
        """Switch to the specified module."""
        if module_name == "self_improvement":
            self.central.setCurrentWidget(self.self_improvement_module)
        else:
            self.central.setCurrentWidget(self.modules[module_name])
        print(f"DEBUG: Switched to module: {module_name}")

    def _connect_signals(self) -> None:
        print("DEBUG: Starting signal connection")
        """Connect signals and slots."""
        # Sidebar actions are now initialized in _init_sidebar_icons()
        # Do not add them here again to prevent duplication
        
        # Add topbar actions that are not language dependent
        profile_action = QAction("👤", self)
        profile_action.triggered.connect(lambda: print("Profile clicked"))
        self.topbar.addAction(profile_action)
        print("DEBUG: Profile topbar action added")
        
        theme_action = QAction("🎨", self)
        theme_action.triggered.connect(lambda: print("Theme switch clicked"))
        self.topbar.addAction(theme_action)
        print("DEBUG: Theme topbar action added")
        
        refresh_action = QAction("🔄", self)
        refresh_action.triggered.connect(lambda: print("Refresh clicked"))
        self.topbar.addAction(refresh_action)
        print("DEBUG: Refresh topbar action added")

        print("DEBUG: Signal connection finished")

    def change_language(self) -> None:
        print("DEBUG: Starting language change")
        """Change application language and update UI."""
        code = self.lang_combo.currentData()
        print("DEBUG: Language code retrieved")
        set_language(code)
        print("DEBUG: Language set")
        for module in list(self.modules.values()) + [self.self_improvement_module] if hasattr(self, 'self_improvement_module') else list(self.modules.values()):
            if hasattr(module, 'update_ui'):
                module.update_ui()
                print("DEBUG: Module UI updated")

        # Clear existing sidebar actions before adding updated ones
        self.sidebar.clear()
        print("DEBUG: Sidebar cleared")

        # Re-add sidebar actions with updated translations
        self._init_sidebar_icons()
        print("DEBUG: Sidebar actions re-initialized with new language")

        # Clear topbar and re-add language-independent items
        self.topbar.clear()
        print("DEBUG: Topbar cleared")
        self.topbar.addWidget(self.lang_combo)
        print("DEBUG: Language selector added to topbar")
        self.topbar.addWidget(self.search_box)
        print("DEBUG: Search box added to topbar")

        # Re-add other topbar actions
        profile_action = QAction("👤", self)
        profile_action.triggered.connect(lambda: print("Profile clicked"))
        self.topbar.addAction(profile_action)
        print("DEBUG: Profile topbar action added")
        
        theme_action = QAction("🎨", self)
        theme_action.triggered.connect(lambda: print("Theme switch clicked"))
        self.topbar.addAction(theme_action)
        print("DEBUG: Theme topbar action added")
        
        refresh_action = QAction("🔄", self)
        refresh_action.triggered.connect(lambda: print("Refresh clicked"))
        self.topbar.addAction(refresh_action)
        print("DEBUG: Refresh topbar action added")

        print("DEBUG: Language change finished")

    def on_search_text_changed(self, text):
        print("DEBUG: Starting search text change")
        if not text.strip():
            self.search_results.hide()
            print("DEBUG: Search results hidden")
            return
        results = self.search_all(text.strip())
        print("DEBUG: Search results retrieved")
        self.search_results.clear()
        print("DEBUG: Search results cleared")
        for r in results:
            item = QListWidgetItem(r['label'])
            print("DEBUG: Search result item created")
            item.setData(Qt.UserRole, r)
            print("DEBUG: Search result item data set")
            self.search_results.addItem(item)
            print("DEBUG: Search result item added to search results")
        if results:
            self.show_search_results()
            print("DEBUG: Search results shown")
        else:
            self.search_results.hide()
            print("DEBUG: Search results hidden")

    def show_search_results(self):
        print("DEBUG: Starting search results show")
        # Позиціонуємо під search_box
        pos = self.search_box.mapToGlobal(self.search_box.rect().bottomLeft())
        print("DEBUG: Search results position calculated")
        self.search_results.move(pos)
        print("DEBUG: Search results moved")
        self.search_results.resize(self.search_box.width(), 200)
        print("DEBUG: Search results resized")
        self.search_results.show()
        print("DEBUG: Search results shown")

    def on_search_result_clicked(self, item):
        print("DEBUG: Starting search result click")
        data = item.data(Qt.UserRole)
        print("DEBUG: Search result data retrieved")
        module = data.get('module')
        print("DEBUG: Search result module retrieved")
        key = data.get('key')
        print("DEBUG: Search result key retrieved")
        self.central.setCurrentWidget(self.modules[module])
        print("DEBUG: Central area current widget set")
        # Передати у відповідний модуль для виділення/відкриття
        if hasattr(self.modules[module], 'select_by_key'):
            self.modules[module].select_by_key(key)
            print("DEBUG: Module select by key called")
        self.search_results.hide()
        print("DEBUG: Search results hidden")

    def search_all(self, query):
        print("DEBUG: Starting search all")
        results = []
        print("DEBUG: Search results list created")
        # Tasks
        if hasattr(self.modules['tasks'], 'search'):
            for r in self.modules['tasks'].search(query):
                results.append({'label': f"📋 {r['label']}", 'module': 'tasks', 'key': r['key']})
                print("DEBUG: Tasks search result added")
        # Agents
        if hasattr(self.modules['agents'], 'search'):
            for r in self.modules['agents'].search(query):
                results.append({'label': f"🤖 {r['label']}", 'module': 'agents', 'key': r['key']})
                print("DEBUG: Agents search result added")
        # Chat
        if hasattr(self.modules['chat'], 'search'):
            for r in self.modules['chat'].search(query):
                results.append({'label': f"💬 {r['label']}", 'module': 'chat', 'key': r['key']})
                print("DEBUG: Chat search result added")
        # Plugins
        if hasattr(self.modules['plugins'], 'search'):
            for r in self.modules['plugins'].search(query):
                results.append({'label': f"🧩 {r['label']}", 'module': 'plugins', 'key': r['key']})
                print("DEBUG: Plugins search result added")
        # Marketplace
        if hasattr(self.modules['marketplace'], 'search'):
            for r in self.modules['marketplace'].search(query):
                results.append({'label': f"🛍️ {r['label']}", 'module': 'marketplace', 'key': r['key']})
                print("DEBUG: Marketplace search result added")
        return results

    def eventFilter(self, obj, event):
        print("DEBUG: Starting event filter")
        if obj == self.search_box:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Down:
                    if self.search_results.isVisible() and self.search_results.count():
                        self.search_results.setCurrentRow(0)
                        self.search_results.setFocus()
                        print("DEBUG: Search results focus set")
                        return True
                elif event.key() == Qt.Key_Escape:
                    self.search_results.hide()
                    print("DEBUG: Search results hidden")
                    return True
            elif event.type() == event.FocusOut:
                QTimer.singleShot(100, self.search_results.hide)
                print("DEBUG: Search results hide timer set")
        elif obj == self.search_results:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.search_results.hide()
                    print("DEBUG: Search results hidden")
                    self.search_box.setFocus()
                    print("DEBUG: Search box focus set")
                    return True
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    item = self.search_results.currentItem()
                    if item:
                        self.on_search_result_clicked(item)
                        print("DEBUG: Search result clicked")
                    return True
            elif event.type() == event.FocusOut:
                QTimer.singleShot(100, self.search_results.hide)
                print("DEBUG: Search results hide timer set")
        return super().eventFilter(obj, event)

    def _log_recovery_action(self, component: str, error: str) -> None:
        """Log detailed error information and recovery actions for debugging.

        Args:
            component: The component or module that failed.
            error: The error message or exception details.
        """
        print(f"RECOVERY: Action taken for {component} failure. Error details: {error}")
        # Here you could add more sophisticated logging to a file or external system for production use
        # Example: self.logger.error(f"Recovery action for {component}: {error}")

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
            print(f"DEBUG: High memory usage detected ({current_usage:.2f} MB), performing cleanup")
            self.memory_manager.perform_cleanup()
        else:
            print(f"DEBUG: Memory usage normal ({current_usage:.2f} MB), no cleanup needed")