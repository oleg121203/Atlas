from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QTextEdit, QHBoxLayout, QLabel, QInputDialog
)
from PySide6.QtCore import QTimer

class SelfImprovementCenter(QWidget):
    def __init__(self, meta_agent, parent=None):
        super().__init__(parent)
        self.meta_agent = meta_agent
        layout = QVBoxLayout(self)
        self.log_view = QListWidget()
        self.stats_label = QLabel("Stats: (success/failure per tool will be shown here)")
        self.patch_view = QTextEdit()
        self.confirm_button = QPushButton('Confirm Patch')
        self.reject_button = QPushButton('Reject Patch')
        self.suggest_button = QPushButton('Suggest Your Own')
        layout.addWidget(QLabel("Live Reasoning Log:"))
        layout.addWidget(self.log_view)
        layout.addWidget(self.stats_label)
        layout.addWidget(QLabel("Patch/Improvement Proposal:"))
        layout.addWidget(self.patch_view)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.confirm_button)
        btn_layout.addWidget(self.reject_button)
        btn_layout.addWidget(self.suggest_button)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Timer for live update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(2000)  # update every 2 seconds

        self.confirm_button.clicked.connect(self.confirm_patch)
        self.reject_button.clicked.connect(self.reject_patch)
        self.suggest_button.clicked.connect(self.suggest_patch)

    def update_log(self):
        self.log_view.clear()
        for entry in self.meta_agent.get_reasoning_log_for_ui():
            self.log_view.addItem(entry['message'])
        # (Optional) Update stats_label with aggregated stats from meta_agent

    def confirm_patch(self):
        patch = self.patch_view.toPlainText()
        file_path, ok = QInputDialog.getText(self, "File to Patch", "Enter file path to patch:")
        if ok and patch and file_path:
            self.meta_agent.apply_patch(file_path, patch)
            self.log_view.addItem(f"Patch applied to {file_path}.")

    def reject_patch(self):
        self.patch_view.clear()
        self.log_view.addItem("Patch rejected by user.")

    def suggest_patch(self):
        suggestion, ok = QInputDialog.getMultiLineText(self, "Suggest Your Own Patch/Strategy", "Enter your suggestion:")
        if ok and suggestion:
            self.meta_agent.save_user_feedback("User suggestion", suggestion)
            self.log_view.addItem(f"User suggested: {suggestion}") 