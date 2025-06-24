from PySide6.QtWidgets import QMainWindow, QToolBar, QAction, QStackedWidget, QDockWidget, QWidget, QLabel, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QFrame
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QTimer, QSize
from ui_qt.chat_module import ChatModule
from ui_qt.tasks_module import TasksModule
from ui_qt.agents_module import AgentsModule
from ui_qt.plugins_module import PluginsModule
from ui_qt.settings_module import SettingsModule
from ui_qt.stats_module import StatsModule
from ui_qt.plugin_manager import PluginManager
from ui_qt.i18n import _, set_language
from ui_qt.system_control_module import SystemControlModule
from ui.self_improvement_center import SelfImprovementCenter

class AtlasMainWindow(QMainWindow):
    def __init__(self, meta_agent=None):
        super().__init__()
        self.setWindowTitle("Atlas — Cyberpunk Edition")
        self.resize(1400, 900)

        # Sidebar (ToolBar)
        self.sidebar = QToolBar(str(_("Sidebar")) or "")
        self.sidebar.setOrientation(Qt.Orientation.Vertical)
        self.sidebar.setMovable(False)
        self.sidebar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.sidebar)

        # Topbar
        self.topbar = QToolBar(str(_("Topbar")) or "")
        self.topbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topbar)

        # Language selector
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Українська", "uk")
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        self.topbar.addWidget(self.lang_combo)

        # Global search (підготовка до наступного кроку)
        self.search_box = QLineEdit()
        placeholder = str(_("Search…")) or ""
        self.search_box.setPlaceholderText(placeholder)
        self.search_box.textChanged.connect(self.on_search_text_changed)
        self.search_box.installEventFilter(self)
        self.topbar.addWidget(self.search_box)

        # Search results list (показується під пошуком)
        self.search_results = QListWidget()
        self.search_results.setWindowFlags(Qt.WindowType.Popup)
        self.search_results.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.search_results.setStyleSheet("background: #181c20; color: #fff; border: 1px solid #00fff7; border-radius: 8px; font-size: 15px;")
        self.search_results.itemClicked.connect(self.on_search_result_clicked)
        self.search_results.installEventFilter(self)
        self.search_results.hide()

        # Central area (StackedWidget)
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)

        # Right panel (DockWidget)
        right_panel_title = str(_("Statistics / Log")) or ""
        self.right_panel = QDockWidget(right_panel_title, self)
        self.right_panel.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.right_panel.setWidget(QLabel(str(_("Статистика та лог тут")) or ""))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_panel)

        # --- Plugin Manager ---
        self.plugin_manager = PluginManager()

        # Модулі (тепер QWidget-класи)
        agent_manager = getattr(self.plugin_manager, 'agent_manager', None)
        self.modules = {
            "chat": ChatModule(),
            "agents": AgentsModule(),
            "tasks": TasksModule(),
            "plugins": PluginsModule(),
            "settings": SettingsModule(),
            "stats": StatsModule(),
            "system_control": SystemControlModule(agent_manager),
        }
        # Add SelfImprovementCenter as a new module/tab
        if meta_agent is not None:
            self.modules["self_improvement"] = SelfImprovementCenter(meta_agent)
            self.central.addWidget(self.modules["self_improvement"])
        for w in self.modules.values():
            if w not in self.central:  # Avoid duplicate addWidget
                self.central.addWidget(w)
        self.central.setCurrentWidget(self.modules["chat"])

        # Передати plugin_manager у PluginsModule, TasksModule, ChatModule, AgentsModule, SettingsModule
        self.modules["plugins"].set_plugin_manager(self.plugin_manager)
        self.modules["tasks"].set_plugin_manager(self.plugin_manager)
        self.modules["chat"].set_plugin_manager(self.plugin_manager)
        self.modules["agents"].set_plugin_manager(self.plugin_manager)
        self.modules["settings"].set_plugin_manager(self.plugin_manager)

        # Після активації/деактивації плагіна оновлювати тулси у всіх модулях
        orig_enable = self.modules["plugins"].enable_plugin
        orig_disable = self.modules["plugins"].disable_plugin
        def enable_and_update():
            orig_enable()
            self.modules["tasks"].update_tools()
            self.modules["chat"].update_tools()
            self.modules["agents"].update_tools()
        def disable_and_update():
            orig_disable()
            self.modules["tasks"].update_tools()
            self.modules["chat"].update_tools()
            self.modules["agents"].update_tools()
        self.modules["plugins"].enable_plugin = enable_and_update
        self.modules["plugins"].disable_plugin = disable_and_update

        # Sidebar actions (через _(text))
        self._add_sidebar_action(_("Chat"), "chat", "💬")
        self._add_sidebar_action(_("Agents"), "agents", "🤖")
        self._add_sidebar_action(_("Tasks"), "tasks", "📋")
        self._add_sidebar_action(_("Plugins"), "plugins", "🧩")
        self._add_sidebar_action(_("Settings"), "settings", "⚙️")
        self._add_sidebar_action(_("Stats"), "stats", "📊")
        self._add_sidebar_action(_("System Control"), "system_control", "🖥️")
        # Add sidebar action for Self-Improvement Center
        if "self_improvement" in self.modules:
            self._add_sidebar_action(_("Self-Improvement"), "self_improvement", "🛠️")

        # Topbar actions (через _(text))
        self.topbar.addAction(QAction(_("Profile"), self))
        self.topbar.addAction(QAction(_("Theme"), self))
        self.topbar.addAction(QAction(_("Refresh"), self))

    def _add_sidebar_action(self, text, key, emoji):
        action = QAction(QIcon(), f"{emoji} {str(text) if text is not None else ''}", self)
        action.setCheckable(True)
        action.triggered.connect(lambda: self.central.setCurrentWidget(self.modules[key]))
        self.sidebar.addAction(action)

    def change_language(self):
        lang_code = self.lang_combo.currentData()
        set_language(lang_code)
        # Оновити всі модулі та елементи UI
        for m in self.modules.values():
            if hasattr(m, 'update_ui'):
                m.update_ui()
        self.sidebar.clear()
        self._add_sidebar_action(_("Chat"), "chat", "💬")
        self._add_sidebar_action(_("Agents"), "agents", "🤖")
        self._add_sidebar_action(_("Tasks"), "tasks", "📋")
        self._add_sidebar_action(_("Plugins"), "plugins", "🧩")
        self._add_sidebar_action(_("Settings"), "settings", "⚙️")
        self._add_sidebar_action(_("Stats"), "stats", "📊")
        self._add_sidebar_action(_("System Control"), "system_control", "🖥️")
        # Add sidebar action for Self-Improvement Center
        if "self_improvement" in self.modules:
            self._add_sidebar_action(_("Self-Improvement"), "self_improvement", "🛠️")
        self.topbar.clear()
        self.topbar.addWidget(self.lang_combo)
        self.topbar.addWidget(self.search_box)
        self.topbar.addAction(QAction(_("Profile"), self))
        self.topbar.addAction(QAction(_("Theme"), self))
        self.topbar.addAction(QAction(_("Refresh"), self)) 

    def on_search_text_changed(self, text):
        if not text.strip():
            self.search_results.hide()
            return
        results = self.search_all(text.strip())
        self.search_results.clear()
        for r in results:
            item = QListWidgetItem(r['label'])
            item.setData(Qt.UserRole, r)
            self.search_results.addItem(item)
        if results:
            self.show_search_results()
        else:
            self.search_results.hide()

    def show_search_results(self):
        # Позиціонуємо під search_box
        pos = self.search_box.mapToGlobal(self.search_box.rect().bottomLeft())
        self.search_results.move(pos)
        self.search_results.resize(self.search_box.width(), 200)
        self.search_results.show()

    def on_search_result_clicked(self, item):
        data = item.data(Qt.UserRole)
        module = data.get('module')
        key = data.get('key')
        self.central.setCurrentWidget(self.modules[module])
        # Передати у відповідний модуль для виділення/відкриття
        if hasattr(self.modules[module], 'select_by_key'):
            self.modules[module].select_by_key(key)
        self.search_results.hide()

    def search_all(self, query):
        results = []
        # Tasks
        if hasattr(self.modules['tasks'], 'search'):
            for r in self.modules['tasks'].search(query):
                results.append({'label': f"📋 {r['label']}", 'module': 'tasks', 'key': r['key']})
        # Agents
        if hasattr(self.modules['agents'], 'search'):
            for r in self.modules['agents'].search(query):
                results.append({'label': f"🤖 {r['label']}", 'module': 'agents', 'key': r['key']})
        # Chat
        if hasattr(self.modules['chat'], 'search'):
            for r in self.modules['chat'].search(query):
                results.append({'label': f"💬 {r['label']}", 'module': 'chat', 'key': r['key']})
        # Plugins
        if hasattr(self.modules['plugins'], 'search'):
            for r in self.modules['plugins'].search(query):
                results.append({'label': f"🧩 {r['label']}", 'module': 'plugins', 'key': r['key']})
        return results 

    def eventFilter(self, obj, event):
        if obj == self.search_box:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Down:
                    if self.search_results.isVisible() and self.search_results.count():
                        self.search_results.setCurrentRow(0)
                        self.search_results.setFocus()
                        return True
                elif event.key() == Qt.Key_Escape:
                    self.search_results.hide()
                    return True
            elif event.type() == event.FocusOut:
                QTimer.singleShot(100, self.search_results.hide)
        elif obj == self.search_results:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Escape:
                    self.search_results.hide()
                    self.search_box.setFocus()
                    return True
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    item = self.search_results.currentItem()
                    if item:
                        self.on_search_result_clicked(item)
                    return True
            elif event.type() == event.FocusOut:
                QTimer.singleShot(100, self.search_results.hide)
        return super().eventFilter(obj, event) 