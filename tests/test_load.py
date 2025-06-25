import pytest
import time
from locust import HttpUser, task, between
from memory_profiler import profile
from typing import Dict, Any, Optional
import logging
from plugins.base import PluginBase
from tests.mock_plugin_registry import MockPluginRegistry as PluginRegistry
from tests.mock_main_window import MockMainWindow as MainWindow
from tests.mock_memory_manager import MockMemoryManager as EnhancedMemoryManager
from tests.mock_llm_manager import MockLLMManager as LLMManager
from tests.mock_task_manager import MockTaskManager as TaskManager
from tests.mock_task_manager import MockTaskInstance as TaskInstance
from tests.mock_chat_manager import MockChatContextManager as ChatContextManager
from tests.mock_plugin import TestPlugin
from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata

logger = logging.getLogger(__name__)

class TestPlugin(PluginBase):
    """Test plugin class for load testing."""
    
    def __init__(self):
        self.metadata = PluginMetadata(
            name='test_plugin',
            version='1.0.0',
            description='Test plugin for load testing',
            author='Test',
            dependencies=[],
            min_app_version='1.0.0',
            max_app_version=None,
            icon=None,
            tags=[]
        )
        self.active = False
        self.settings = {}
        super().__init__()

    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata

    def _get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return self.settings

    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Activate the plugin."""
        self.active = True
        self.on_activate(app_context)

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.on_deactivate()
        self.active = False

    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is activated."""
        pass

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass

    def get_widget(self, parent: Optional["QWidget"] = None) -> Optional["QWidget"]:
        """Get the main widget for UI integration."""
        return None

    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set plugin settings."""
        self.settings = settings

    def settings_widget(self, parent: Optional["QWidget"] = None) -> Optional["QWidget"]:
        """Get settings widget for editing."""
        return None

    def info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "active": self.active,
            "settings": self.settings,
            "metadata": self.metadata
        }

    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.active

class AtlasLoadTest:
    """Base class for Atlas load tests."""
    
    def __init__(self, num_users: int = 1000):
        """Initialize load test environment."""
        self.num_users = num_users
        self.metrics: Dict[str, Any] = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'errors': []
        }

    @profile
    def measure_memory_usage(self) -> float:
        """Measure current memory usage."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB

    def measure_cpu_usage(self) -> float:
        """Measure current CPU usage."""
        import psutil
        return psutil.cpu_percent(interval=1)

    def record_metrics(self, response_time: float, error: Exception = None):
        """Record test metrics."""
        self.metrics['response_times'].append(response_time)
        self.metrics['memory_usage'].append(self.measure_memory_usage())
        self.metrics['cpu_usage'].append(self.measure_cpu_usage())
        if error:
            self.metrics['errors'].append(error)

class PluginLoadTest(AtlasLoadTest):
    """Load tests for plugin system."""
    
    def test_plugin_operations(self):
        """Test plugin operations under load."""
        registry = PluginRegistry()
    
        start_time = time.time()
        try:
            # Simulate loading 100 plugins
            plugins = []
            for i in range(100):
                test_plugin = TestPlugin()
                plugins.append(test_plugin)
                registry.register_plugin(test_plugin)
            
            # Simulate activating and deactivating plugins
            for plugin in plugins:
                registry.activate_plugin(plugin.metadata.name)
                registry.deactivate_plugin(plugin.metadata.name)
            
            end_time = time.time()
            response_time = end_time - start_time
            self.record_metrics(response_time)
            
            assert len(registry.plugins) == 100
            
        except Exception as e:
            self.record_metrics(0, e)
            raise

class ChatLoadTest(AtlasLoadTest):
    """Load tests for chat module."""
    
    def test_chat_operations(self):
        """Test chat operations under load."""
        # Initialize required dependencies
        llm_manager = LLMManager()
        memory_manager = EnhancedMemoryManager()
    
        # Initialize chat manager with dependencies
        manager = ChatContextManager(memory_manager, llm_manager)
        
        start_time = time.time()
        try:
            # Generate and process 1000 messages
            messages = [{
                'role': 'user',
                'content': f'Test message {i}'
            } for i in range(1000)]
            
            # Process messages in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                for message in batch:
                    manager.process_message(message)
            
            end_time = time.time()
            response_time = end_time - start_time
            self.record_metrics(response_time)
            
            assert len(manager.get_messages()) >= 1000
            
        except Exception as e:
            self.record_metrics(0, e)
            raise
from tests.mock_task_manager import MockTaskInstance as TaskInstance

class TaskLoadTest(AtlasLoadTest):
    """Load tests for task system."""
    
    def test_task_operations(self):
        """Test task operations under load."""
        # Initialize mock LLM manager
        llm_manager = LLMManager()
        
        # Initialize task manager with dependencies
        manager = TaskManager(llm_manager=llm_manager)
        
        start_time = time.time()
        try:
            # Create and execute 100 tasks
            for i in range(100):
                task = {
                    'id': f'task_{i}',
                    'name': f'Test Task {i}',
                    'priority': 'normal'
                }
                manager.create_task(task)
            
            manager.execute_pending_tasks()
            
            end_time = time.time()
            response_time = end_time - start_time
            self.record_metrics(response_time)
            
            assert len(manager.completed_tasks) == 100
            
        except Exception as e:
            self.record_metrics(0, e)
            raise

class UILoadTest(AtlasLoadTest):
    """Load tests for UI components."""
    
    def test_ui_operations(self):
        """Test UI operations under load."""
        window = MainWindow()
    
        start_time = time.time()
        try:
            # Perform window state changes
            for i in range(100):
                window.show()
                window.hide()
                window.showMaximized()
                window.showNormal()
    
            end_time = time.time()
            response_time = end_time - start_time
            self.record_metrics(response_time)
    
            assert window.isVisible() is True
            
        except Exception as e:
            self.record_metrics(0, e)
            raise

@pytest.mark.load
@pytest.mark.parametrize("test_class", [PluginLoadTest, ChatLoadTest, TaskLoadTest, UILoadTest])
def test_load(test_class):
    """Run load tests for different components."""
    test = test_class()
    
    if isinstance(test, PluginLoadTest):
        test.test_plugin_operations()
    elif isinstance(test, ChatLoadTest):
        test.test_chat_operations()
    elif isinstance(test, TaskLoadTest):
        test.test_task_operations()
    elif isinstance(test, UILoadTest):
        test.test_ui_operations()
    
    # Verify performance metrics
    assert all(rt < 1.0 for rt in test.metrics['response_times'])  # Response time < 1 second
    assert all(mu < 8000 for mu in test.metrics['memory_usage'])  # Memory usage < 8GB
    assert all(cu < 80 for cu in test.metrics['cpu_usage'])      # CPU usage < 80%
    assert len(test.metrics['errors']) == 0
