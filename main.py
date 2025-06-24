import sys
from PySide6.QtWidgets import QApplication
from ui_qt.main_window import AtlasMainWindow
import qdarkstyle
from ui.system_control_panel import SystemControlPanel
# --- Add agent imports ---
from agents.token_tracker import TokenTracker
from utils.llm_manager import LLMManager
from agents.master_agent import MasterAgent
from agents.meta_agent import MetaAgent
from utils.config_manager import config_manager

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    # --- Instantiate agent stack ---
    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker, config_manager)
    master_agent = MasterAgent(llm_manager)
    meta_agent = MetaAgent(master_agent)
    window = AtlasMainWindow(meta_agent=meta_agent)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 