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
sys.path.append(os.path.join(base_dir, 'ui'))

# Disable Posthog analytics to prevent segmentation fault
os.environ['POSTHOG_DISABLED'] = '1'

def main():
    try:
        logger.debug("Starting Atlas application with module loading disabled in source")
        from PySide6.QtWidgets import QApplication
        import qdarkstyle
        
        from core.application import AtlasApplication
        app = AtlasApplication()
        logger.debug("AtlasApplication created successfully")
        
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
        
        from ui.main_window import AtlasMainWindow
        logger.debug("AtlasMainWindow imported successfully")
        
        window = AtlasMainWindow(meta_agent=dummy_meta_agent)
        logger.debug("AtlasMainWindow created successfully")
        
        window.show()
        logger.debug("AtlasMainWindow shown")
        
        sys.exit(app.run())
    except Exception as e:
        logger.error(f"Atlas application failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()