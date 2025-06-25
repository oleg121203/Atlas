import os
import sys
import traceback
from PySide6.QtWidgets import QApplication
# --- Add agent imports ---
from agents.token_tracker import TokenTracker
from utils.llm_manager import LLMManager
from agents.master_agent import MasterAgent
from agents.meta_agent import MetaAgent
from utils.config_manager import config_manager

# Disable Posthog analytics to prevent segmentation fault
os.environ['POSTHOG_DISABLED'] = '1'

print("DEBUG: Starting application initialization")
try:
    print("DEBUG: Importing AtlasMainWindow")
    from ui_qt.main_window import AtlasMainWindow
    print("DEBUG: AtlasMainWindow imported successfully")
except ImportError as e:
    print(f"Failed to import AtlasMainWindow: {e}")
    traceback.print_exc()
    exit(1)

import qdarkstyle

print("DEBUG: Starting main execution")
def main():
    print("DEBUG: Creating QApplication")
    app = QApplication(sys.argv)
    print("DEBUG: Setting stylesheet")
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    # --- Instantiate agent stack ---
    print("DEBUG: Creating TokenTracker")
    token_tracker = TokenTracker()
    print("DEBUG: Creating LLMManager")
    llm_manager = LLMManager(token_tracker, config_manager)
    print("DEBUG: Creating MasterAgent")
    master_agent = MasterAgent(llm_manager)
    print("DEBUG: Creating MetaAgent")
    meta_agent = MetaAgent(master_agent)
    print("DEBUG: Creating AtlasMainWindow")
    window = AtlasMainWindow(meta_agent=meta_agent)
    print("DEBUG: Showing window")
    window.show()
    print("DEBUG: Entering application event loop")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()