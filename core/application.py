"""
Main application class for Atlas.

This module defines the central application logic, orchestrating the initialization
and lifecycle management of core systems, modules, and plugins.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication
from ui.main_window import AtlasMainWindow
from modules.agents.token_tracker import TokenTracker
from utils.llm_manager import LLMManager
from modules.agents.master_agent import MasterAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AtlasApplication:
    """Central application class for Atlas."""

    def __init__(self):
        """Initialize the Atlas application with core components."""
        logger.info("Initializing Atlas Application")
        self.app = QApplication(sys.argv)
        
        # Initialize core systems
        self.token_tracker = TokenTracker()
        self.llm_manager = LLMManager(self.token_tracker)
        self.master_agent = MasterAgent(self.llm_manager)
        self.meta_agent = self.master_agent  # For compatibility
        
        # Initialize main window
        self.main_window = AtlasMainWindow(
            master_agent=self.master_agent,
            meta_agent=self.meta_agent,
            llm_manager=self.llm_manager
        )
        
    def run(self):
        """Start the application event loop."""
        logger.info("Starting Atlas Application")
        self.main_window.show()
        return self.app.exec()

if __name__ == "__main__":
    app = AtlasApplication()
    sys.exit(app.run())
