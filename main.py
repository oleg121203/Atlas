import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory and specific subdirectories to sys.path to ensure modules can be found
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, 'core'))
sys.path.append(os.path.join(base_dir, 'agents'))
sys.path.append(os.path.join(base_dir, 'plugins'))
sys.path.append(os.path.join(base_dir, 'ui_qt'))

# Disable Posthog analytics to prevent segmentation fault
os.environ['POSTHOG_DISABLED'] = '1'

def main():
    try:
        logger.debug("Starting Atlas application with module loading disabled in source")
        from PySide6.QtWidgets import QApplication
        import qdarkstyle
        
        app = QApplication(sys.argv)
        logger.debug("QApplication created successfully")
        
        app.setStyleSheet(qdarkstyle.load_stylesheet())
        logger.debug("Stylesheet set successfully")
        
        # Create a dummy MetaAgent-like object for testing
        class DummyMetaAgent:
            def __init__(self):
                self.agent_manager = None
                
            def execute_tool(self, tool_name, params):
                logger.warning(f"Dummy execute_tool called for {tool_name} with params {params}")
                if tool_name == "system_event":
                    if params.get("event") == "get_volume":
                        return {"status": "success", "data": {"volume": 50}}
                    return {"status": "success", "data": {}}
                return None
        
        dummy_meta_agent = DummyMetaAgent()
        logger.debug("DummyMetaAgent created successfully")
        
        from ui_qt.main_window import AtlasMainWindow
        logger.debug("AtlasMainWindow imported successfully")
        
        window = AtlasMainWindow(meta_agent=dummy_meta_agent)
        logger.debug("AtlasMainWindow created successfully")
        
        window.show()
        logger.debug("AtlasMainWindow shown")
        
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Atlas application failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()