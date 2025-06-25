from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.i18n import _

class StatsModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatsModule")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("📊 Stats"))
        self.title.setStyleSheet("color: #ffea00; font-size: 22px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(self.title)

        self.stats_label = QLabel(_("No stats available yet."))
        self.stats_label.setStyleSheet("color: #fff; font-size: 15px;")
        layout.addWidget(self.stats_label)

    def update_ui(self):
        self.title.setText(_("📊 Stats"))
        self.stats_label.setText(_("No stats available yet.")) 