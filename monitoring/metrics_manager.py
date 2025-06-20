import threading
from typing import Dict, List, Optional

class MetricsManager:
    _instance: Optional['MetricsManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MetricsManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.tool_load_times: Dict[str, float] = {}
        self.memory_search_latencies: List[float] = []
        self.tool_usage_stats: Dict[str, Dict[str, int]] = {}
        self._initialized = True

    def record_tool_load_time(self, tool_name: str, duration: float):
        """Records the loading time for a specific tool."""
        self.tool_load_times[tool_name] = duration

    def record_memory_search_latency(self, duration: float):
        """Records a memory search latency event."""
        self.memory_search_latencies.append(duration)

    def record_tool_usage(self, tool_name: str, success: bool):
        """Records a tool usage event (success or failure)."""
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {"success": 0, "failure": 0}
        
        if success:
            self.tool_usage_stats[tool_name]["success"] += 1
        else:
            self.tool_usage_stats[tool_name]["failure"] += 1

    def get_tool_load_times(self) -> Dict[str, float]:
        """Returns all recorded tool loading times."""
        return self.tool_load_times.copy()

    def get_memory_search_latencies(self) -> List[float]:
        """Returns all recorded memory search latencies."""
        return self.memory_search_latencies.copy()

    def get_tool_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Returns the success/failure stats for all tools."""
        return self.tool_usage_stats.copy()

    def clear_data(self):
        """Clears all stored metrics."""
        self.tool_load_times.clear()
        self.memory_search_latencies.clear()
        self.tool_usage_stats.clear()

#Singleton instance to be used across the application
metrics_manager = MetricsManager()
