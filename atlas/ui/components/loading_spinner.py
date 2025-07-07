import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel


class LoadingSpinner(QLabel):
    def __init__(self, parent=None, size=32):
        super().__init__(parent)
        self.setObjectName("LoadingSpinner")
        spinner_path = os.path.join(os.path.dirname(__file__), "spinner.gif")
        self.movie = QMovie(spinner_path)
        self.setMovie(self.movie)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(size, size)
        self.hide()

    def start(self):
        self.show()
        self.movie.start()

    def stop(self):
        self.movie.stop()
        self.hide()

    def apply_theme(self, stylesheet: str):
        self.setStyleSheet("")
        self.setStyleSheet(stylesheet)
