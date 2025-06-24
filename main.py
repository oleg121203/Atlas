import sys
from PySide6.QtWidgets import QApplication
from ui_qt.main_window import AtlasMainWindow
import qdarkstyle
from ui.system_control_panel import SystemControlPanel

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = AtlasMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 