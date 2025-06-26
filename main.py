import logging
import sys
import os
import argparse
import asyncio
import uuid
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory and specific subdirectories to sys.path to ensure modules can be found
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.join(base_dir, 'core'))
sys.path.append(os.path.join(base_dir, 'agents'))
sys.path.append(os.path.join(base_dir, 'plugins'))
sys.path.append(os.path.join(base_dir, 'ui'))

# Ensure path for config and utils are in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "config"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from sentry_config import init_sentry
from core.data_cache import DataCache
from utils.db_optimizer import DatabaseOptimizer
from analytics.onboarding_analytics import OnboardingAnalytics
from integration.websocket_integration import CollaborationManager

# Initialize Sentry for crash reporting
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    init_sentry(SENTRY_DSN, environment=os.environ.get("ATLAS_ENV", "development"), release="atlas@1.0.0")
else:
    print("Sentry DSN not found in environment variables. Crash reporting disabled.")

# Initialize DataCache for performance optimization
async def init_cache():
    cache = DataCache()
    await cache.initialize()
    return cache

# Initialize DatabaseOptimizer for query performance
def init_db_optimizer():
    db_path = os.environ.get("ATLAS_DB_PATH", ":memory:")  # Replace with actual path
    optimizer = DatabaseOptimizer(db_path)
    optimizer.connect()
    # Define indexes for common queries - adjust based on actual schema
    indexes = [
        {"name": "idx_tasks_user_id", "table": "tasks", "columns": ["user_id"]},
        {"name": "idx_tasks_completed", "table": "tasks", "columns": ["completed"]}
    ]
    optimizer.create_indexes(indexes)
    return optimizer

# Initialize OnboardingAnalytics to track user behavior during onboarding
def init_analytics():
    analytics = OnboardingAnalytics()
    # Start a session for a new user - in a real scenario, use a unique user ID
    analytics.start_session("new_user")
    return analytics

class AtlasApp:
    def __init__(self):
        self.data_cache = DataCache()
        self.db_optimizer = DatabaseOptimizer(os.environ.get("ATLAS_DB_PATH", ":memory:"))
        self.onboarding_analytics = OnboardingAnalytics()
        self.collab_manager = None  # Initialize later with user data

    async def initialize(self):
        """Initialize app components."""
        await self.data_cache.initialize()
        self.db_optimizer.connect()
        self.onboarding_analytics.initialize()
        # Collaboration manager would be initialized after user login with proper IDs
        # For now, placeholder initialization
        user_id = "placeholder_user"
        team_id = "placeholder_team"
        server_url = "ws://localhost:8765"
        self.collab_manager = CollaborationManager(server_url, user_id, team_id)
        self.collab_manager.set_task_update_callback(self.handle_task_update)
        self.collab_manager.start()

    def _setup_collaboration(self):
        """Set up team collaboration features via WebSocket."""
        try:
            print("Setting up collaboration features...")
            team_id = "default_team"  # Replace with dynamic team ID in production
            user_id = "user_" + str(uuid.uuid4())[:8]  # Generate a simple unique user ID
            print(f"User ID: {user_id}, Team ID: {team_id}")
            
            self.collaboration_manager = CollaborationManager(team_id, user_id)
            
            # Set callback for task updates to update UI
            if hasattr(self, 'task_view') and self.task_view:
                self.collaboration_manager.set_task_update_callback(self.task_view.handle_websocket_task_update)
            else:
                print("Task view not available, using direct callback")
                self.collaboration_manager.set_task_update_callback(self.handle_task_update)
            
            print("Collaboration setup complete")
        except Exception as e:
            print(f"Error setting up collaboration: {e}")

    def handle_task_update(self, data: Dict[str, Any]):
        """Handle real-time task updates from WebSocket."""
        print(f"Task update received: {data}")
        if hasattr(self, 'task_view') and self.task_view:
            self.task_view.handle_websocket_task_update(data)

    def shutdown(self):
        """Shut down app components."""
        if self.collab_manager:
            self.collab_manager.stop()

# Optional profiling for ASC-025
try:
    from performance.profiling_setup import PerformanceProfiler
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    PerformanceProfiler = None

# Startup optimization for ASC-025
try:
    from performance.startup_optimization import optimize_startup, SplashScreenManager
    STARTUP_OPTIMIZATION_AVAILABLE = True
except ImportError:
    STARTUP_OPTIMIZATION_AVAILABLE = False
    optimize_startup = None
    SplashScreenManager = None

# Disable Posthog analytics to prevent segmentation fault
os.environ['POSTHOG_DISABLED'] = '1'

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Atlas Application')
    parser.add_argument('--profile', action='store_true', help='Run with performance profiling (ASC-025)')
    parser.add_argument('--no-splash', action='store_true', help='Disable splash screen during startup')
    return parser.parse_args()

async def main():
    """Main entry point for the Atlas application."""
    args = parse_arguments()
    
    profiler = None
    if args.profile and PROFILING_AVAILABLE:
        logger.info("Starting Atlas with performance profiling enabled (ASC-025)")
        profiler = PerformanceProfiler()
        profiler.start_profiling()
    else:
        logger.info("Starting Atlas normally")
    
    # Setup startup optimizations
    lazy_loader = None
    splash_manager = None
    if STARTUP_OPTIMIZATION_AVAILABLE:
        lazy_loader = optimize_startup()
        if not args.no_splash:
            splash_manager = SplashScreenManager()
            splash_manager.show_splash()
            splash_manager.update_progress(10, "Initializing...")
        logger.info("Startup optimizations applied (ASC-025)")
    
    app = AtlasApp()
    await app.initialize()
    
    try:
        logger.debug("Starting Atlas application with module loading disabled in source")
        from PySide6.QtWidgets import QApplication
        if splash_manager:
            splash_manager.update_progress(30, "Loading UI...")
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
        
        if splash_manager:
            splash_manager.update_progress(70, "Creating main window...")
        window = AtlasMainWindow(meta_agent=dummy_meta_agent)
        logger.debug("AtlasMainWindow created successfully")
        
        window.show()
        logger.debug("AtlasMainWindow shown")
        
        if splash_manager:
            splash_manager.update_progress(90, "Finalizing...")
            splash_manager.close_splash()
        sys.exit(app.run())
    except Exception as e:
        logger.error(f"Atlas application failed: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        if profiler:
            profiler.stop_profiling("main_execution_profile.txt")
            logger.info("Performance profiling completed and saved")
        app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())