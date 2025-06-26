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

if __name__ == "__main__":
    # Suppress urllib3 warning about OpenSSL compatibility
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')
    
    # Initialize QApplication before ANY other imports that might touch GUI components
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Now safe to import other modules
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("QApplication initialized before other imports")
    
    # Import application logic after GUI app is ready
    from core.application import AtlasApplication
    atlas_app = AtlasApplication()
    
    # Start the application
    logger.info("Starting Atlas application")
    sys.exit(atlas_app.run())