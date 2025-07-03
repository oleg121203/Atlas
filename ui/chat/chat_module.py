import datetime
import json
from typing import Any, Callable, Dict, List, Optional

import markdown2
from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.logging import get_logger
from ui.components.loading_spinner import LoadingSpinner
from ui.i18n import _
from ui.plugins.plugin_manager import PluginManager

EMOJI_LIST = [
    ":smile:",
    ":rocket:",
    ":fire:",
    ":star:",
    ":robot:",
    ":zap:",
    ":sunglasses:",
    ":thumbsup:",
    ":wave:",
    ":bulb:",
]
EMOJI_MAP = {
    ":smile:": "😄",
    ":rocket:": "🚀",
    ":fire:": "🔥",
    ":star:": "⭐",
    ":robot:": "🤖",
    ":zap:": "⚡",
    ":sunglasses:": "😎",
    ":thumbsup:": "👍",
    ":wave:": "👋",
    ":bulb:": "💡",
}


class ChatModule(QWidget):
    """Chat interface module with cyberpunk styling.

    Attributes:
        llm_callback: Callback function for LLM/agent responses
        history: List of chat messages with role, text, and timestamp
        plugin_manager: Plugin manager instance
        tool_widgets: List of tool UI widgets
        completer: QCompleter for input suggestions
        chat_history: QTextBrowser for chat messages
        input_line: QLineEdit for user input
        send_btn: QPushButton for sending messages
        tools_frame: QFrame for plugin tools
        tools_layout: QVBoxLayout for tool widgets
        title: QLabel for module title
        history_btn: QPushButton for history management
        spinner: LoadingSpinner instance
    """

    message_sent = Signal(str)

    def __init__(self, parent=None):
        """Initialize the chat module.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.module_name = (
            "chat"  # Store for reference if needed, but don't pass to QWidget
        )
        self.setObjectName("ChatModule")
        self.llm_callback: Optional[Callable[[str, Callable[[str], None]], None]] = None
        self.history: List[Dict[str, Any]] = []
        self.plugin_manager: Optional[PluginManager] = None
        self.tool_widgets: List[QWidget] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Заголовок
        self.title = QLabel(_("💬 Chat (Cyberpunk)"))
        self.title.setStyleSheet(
            "color: #00fff7; font-size: 22px; font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(self.title)

        # Кнопка для історії
        self.history_btn = QPushButton(_("History"))
        self.history_btn.setStyleSheet(
            "background: #23272e; color: #00fff7; border-radius: 6px; padding: 4px 12px;"
        )
        self.history_btn.clicked.connect(self.show_history_dialog)
        layout.addWidget(self.history_btn, alignment=Qt.AlignRight)

        # Історія чату (QTextBrowser для markdown)
        self.chat_history = QTextBrowser()
        self.chat_history.setOpenExternalLinks(True)
        self.chat_history.setStyleSheet(
            "background: #181c20; color: #e0e0e0; border: 1px solid #00fff7; border-radius: 8px; font-size: 15px;"
        )
        self.chat_history.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_history.customContextMenuRequested.connect(self.show_context_menu)
        self.chat_history.setAcceptDrops(True)
        layout.addWidget(self.chat_history, stretch=1)

        # Ввід + кнопка
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText(
            _("Type your message… (Markdown, emoji supported)")
        )
        self.input_line.setStyleSheet(
            "background: #23272e; color: #fff; border: 1px solid #00fff7; border-radius: 6px; font-size: 15px;"
        )
        self.input_line.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_line, stretch=1)
        self.send_btn = QPushButton(_("Send"))
        self.send_btn.setStyleSheet(
            "background: #00fff7; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;"
        )
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        # QCompleter для підказок (історія + emoji)
        self.completer = QCompleter(self.get_completer_list())
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_line.setCompleter(self.completer)

        # Drag&Drop
        self.chat_history.installEventFilter(self)
        self.chat_history.viewport().installEventFilter(self)

        # Тулси-плагіни
        self.tools_frame = QFrame()
        self.tools_layout = QVBoxLayout(self.tools_frame)
        self.tools_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.tools_frame)

        self.feedback_layout = QVBoxLayout()
        self.feedback_widget = QWidget()
        self.feedback_widget.setLayout(self.feedback_layout)
        layout.addWidget(self.feedback_widget)

        self.spinner = LoadingSpinner(self)
        layout.addWidget(self.spinner)

        self._connect_buttons()

    def _connect_buttons(self):
        """Connect buttons to their respective actions."""
        if hasattr(self, "send_btn"):
            self.send_btn.clicked.connect(self.send_message)
        if hasattr(self, "history_btn"):
            self.history_btn.clicked.connect(self.show_history_dialog)
        logger = get_logger()
        logger.info("Chat module buttons connected")

    def update_ui(self) -> None:
        """Update UI elements with translated text."""
        self.title.setText(str(_("💬 Chat (Cyberpunk)")) or "💬 Chat (Cyberpunk)")
        self.history_btn.setText(str(_("History")) or "History")
        self.input_line.setPlaceholderText(
            str(_("Type your message… (Markdown, emoji supported)"))
            or "Type your message… (Markdown, emoji supported)"
        )
        self.send_btn.setText(str(_("Send")) or "Send")
        self.update_tools()

    # LLM інтеграція
    def set_llm_callback(
        self, callback: Callable[[str, Callable[[str], None]], None]
    ) -> None:
        """Set the LLM callback function.

        Args:
            callback: Function to handle LLM responses
        """
        self.llm_callback = callback

    def send_message(self) -> None:
        """Send user message to chat.

        Raises:
            ValueError: If message is empty
        """
        text = self.input_line.text().strip()
        if not text:
            return

        try:
            text = self.replace_emoji(text)
            html = markdown2.markdown(f"**🧑 You:** {text}")
            self.chat_history.append(html)
            self.append_history("user", text)
            self.input_line.clear()
            self.scroll_to_bottom()
            self.get_agent_response(text)
            self.update_completer()
            self.message_sent.emit(text)
        except Exception as e:
            self.chat_history.append(
                f'<span style="color:#ff00a0;">⚠️ Error:</span> {str(e)}'
            )
            self.scroll_to_bottom()

    def get_agent_response(self, user_text: str) -> None:
        """Get response from LLM/agent.

        Args:
            user_text: User input text
        """
        self.spinner.start()
        self.send_btn.setEnabled(False)
        if self.llm_callback:

            def handle_response(response: str) -> None:
                self.show_agent_response(response)

            self.llm_callback(user_text, handle_response)
        else:
            QTimer.singleShot(
                900,
                lambda: self.show_agent_response(
                    f"🤖 Atlas: *Echo:* {user_text[::-1]}"
                ),
            )

    def show_agent_response(self, text: str) -> None:
        """Show agent's response in chat.

        Args:
            text: Agent's response text
        """
        self.spinner.stop()
        self.send_btn.setEnabled(True)
        try:
            text = self.replace_emoji(text)
            html = markdown2.markdown(text)
            self.chat_history.append(html)
            self.append_history("agent", text)
            self.scroll_to_bottom()
            self.add_feedback_widget(text)
        except Exception as e:
            self.chat_history.append(
                f'<span style="color:#ff00a0;">⚠️ Error:</span> {str(e)}'
            )
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    # --- Історія ---
    def append_history(self, role, text):
        self.history.append(
            {
                "role": role,
                "text": text,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    def save_history(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.history = json.load(f)
        self.chat_history.clear()
        for msg in self.history:
            prefix = "🧑 You:" if msg["role"] == "user" else "🤖 Atlas:"
            html = markdown2.markdown(f"**{prefix}** {msg['text']}")
            self.chat_history.append(html)
        self.scroll_to_bottom()

    def show_history_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Відкрити історію чату", "", "JSON Files (*.json)"
        )
        if path:
            self.load_history(path)

    # --- Підказки (autocomplete) ---
    def get_completer_list(self):
        # Підказки: всі унікальні слова з історії + emoji
        words = set()
        for msg in self.history:
            for w in msg["text"].split():
                words.add(w)
        return list(words) + EMOJI_LIST

    def update_completer(self):
        self.completer.model().setStringList(self.get_completer_list())

    def replace_emoji(self, text):
        for k, v in EMOJI_MAP.items():
            text = text.replace(k, v)
        return text

    # --- Drag&Drop ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            if event.mimeData().hasUrls() or event.mimeData().hasText():
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Drop:
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    path = url.toLocalFile()
                    self.chat_history.append(
                        f'<span style="color:#ff00a0;">📎 File dropped:</span> {path}'
                    )
                    self.append_history("file", path)
                self.scroll_to_bottom()
                return True
            elif event.mimeData().hasText():
                text = event.mimeData().text()
                self.chat_history.append(
                    f'<span style="color:#ff00a0;">📋 Dropped text:</span> {text}'
                )
                self.append_history("dropped", text)
                self.scroll_to_bottom()
                return True
        return super().eventFilter(obj, event)

    # --- Контекстне меню ---
    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        save_action = menu.addAction("Save history…")
        action = menu.exec_(self.chat_history.mapToGlobal(pos))
        if action == copy_action:
            cursor = self.chat_history.textCursor()
            if cursor.hasSelection():
                QApplication.clipboard().setText(cursor.selectedText())
            else:
                QApplication.clipboard().setText(self.chat_history.toPlainText())
        elif action == save_action:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Зберегти історію чату",
                "chat_history.json",
                "JSON Files (*.json)",
            )
            if path:
                self.save_history(path)

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.update_tools()

    def update_tools(self):
        for w in self.tool_widgets:
            w.setParent(None)
        self.tool_widgets.clear()
        if not self.plugin_manager:
            return
        for _name, plugin in self.plugin_manager.plugins.items():
            if plugin.active and hasattr(plugin, "get_widget"):
                widget = plugin.get_widget(self)
                if widget:
                    self.tools_layout.addWidget(widget)
                    self.tool_widgets.append(widget)

    def search(self, query):
        """Повертає список словників: {'label': фрагмент повідомлення, 'key': timestamp}"""
        results = []
        for msg in self.history:
            if query.lower() in msg["text"].lower():
                label = msg["text"][:60] + ("…" if len(msg["text"]) > 60 else "")
                results.append({"label": label, "key": msg["timestamp"]})
        return results

    def select_by_key(self, key):
        # Знаходимо повідомлення з відповідним timestamp і виділяємо його у QTextBrowser
        for _i, msg in enumerate(self.history):
            if msg["timestamp"] == key:
                # Прокручуємо QTextBrowser до цього повідомлення
                # (простий спосіб — знайти текст і виділити)
                cursor = self.chat_history.textCursor()
                self.chat_history.moveCursor(cursor.Start)
                found = self.chat_history.find(msg["text"])
                if found:
                    self.chat_history.setTextCursor(self.chat_history.textCursor())
                break

    def add_feedback_widget(self, text):
        layout = QHBoxLayout()
        rating_label = QLabel("Rate this response:")
        rating_label.setStyleSheet("QLabel { color: #AAAAAA; font-size: 12px; }")
        layout.addWidget(rating_label)

        for rating in range(1, 6):
            btn = QPushButton(str(rating))
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                "QPushButton { background: #3A3A3A; color: white; border: none; } "
                "QPushButton:hover { background: #4A4A4A; }"
            )
            btn.clicked.connect(lambda checked, r=rating: self.submit_feedback(r))
            layout.addWidget(btn)

        self.feedback_layout.addLayout(layout)

    def submit_feedback(self, rating):
        """Submit feedback for the last AI response."""
        user_id = "default_user" if not hasattr(self, "user_id") else self.user_id

        if hasattr(self, "last_message_id") and self.last_message_id:
            from utils.memory_management import MEMORY_MANAGER

            MEMORY_MANAGER.store_feedback(user_id, self.last_message_id, rating)
        else:
            logger = get_logger()
            logger.warning("No last message ID found for feedback submission")
            from utils.memory_management import MEMORY_MANAGER

            MEMORY_MANAGER.store_feedback(user_id, "unknown_message", rating)
        logger = get_logger()
        logger.info(f"Feedback submitted: Rating {rating}")
        # Optionally notify self_learning_agent here if accessible
        print(f"DEBUG: Feedback submitted: Rating {rating}")
