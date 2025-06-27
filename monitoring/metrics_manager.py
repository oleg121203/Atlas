import threading
from typing import Dict, List, Optional


class MetricsManager:
    _instance: Optional["MetricsManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "MetricsManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MetricsManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized: bool = True
        self.tool_load_times: Dict[str, float] = {}
        self.memory_search_latencies: List[float] = []
        self.tool_usage_stats: Dict[str, Dict[str, int]] = {}
        # Performance metrics
        self.plan_generation_latencies: List[float] = []
        self.plan_execution_latencies: List[float] = []

    def record_tool_load_time(self, tool_name: str, duration: float) -> None:
        """Records the loading time for a specific tool."""
        self.tool_load_times[tool_name] = duration

    def record_memory_search_latency(self, duration: float) -> None:
        """Records a memory search latency event."""
        self.memory_search_latencies.append(duration)

    def record_plan_generation_latency(self, duration: float) -> None:
        """Records the latency for plan generation (seconds)."""
        self.plan_generation_latencies.append(duration)

    def record_plan_execution_latency(self, duration: float) -> None:
        """Records the latency for full plan execution (seconds)."""
        self.plan_execution_latencies.append(duration)

    def record_tool_usage(self, tool_name: str, success: bool) -> None:
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

    def get_plan_generation_latencies(self) -> List[float]:
        """Returns all recorded plan generation latencies."""
        return self.plan_generation_latencies.copy()

    def get_plan_execution_latencies(self) -> List[float]:
        """Returns all recorded plan execution latencies."""
        return self.plan_execution_latencies.copy()

    # ---- Aggregate helpers -------------------------------------------------
    def get_average_plan_generation_latency(self) -> float:
        """Returns the average plan generation latency in seconds (0.0 if none)."""
        if not self.plan_generation_latencies:
            return 0.0
        return sum(self.plan_generation_latencies) / len(self.plan_generation_latencies)

    def get_average_plan_execution_latency(self) -> float:
        """Returns the average plan execution latency in seconds (0.0 if none)."""
        if not self.plan_execution_latencies:
            return 0.0
        return sum(self.plan_execution_latencies) / len(self.plan_execution_latencies)

    def get_percentile_plan_generation_latency(self, percentile: float = 90.0) -> float:
        """Returns the P-th percentile latency for plan generation (default P90)."""
        if not self.plan_generation_latencies:
            return 0.0
        if not 0 < percentile < 100:
            raise ValueError("percentile must be between 0 and 100, exclusive")
        sorted_latencies = sorted(self.plan_generation_latencies)
        k = int(round((len(sorted_latencies) - 1) * (percentile / 100.0)))
        return sorted_latencies[k]

    def get_percentile_plan_execution_latency(self, percentile: float = 90.0) -> float:
        """Returns the P-th percentile latency for plan execution (default P90)."""
        if not self.plan_execution_latencies:
            return 0.0
        if not 0 < percentile < 100:
            raise ValueError("percentile must be between 0 and 100, exclusive")
        sorted_latencies = sorted(self.plan_execution_latencies)
        k = int(round((len(sorted_latencies) - 1) * (percentile / 100.0)))
        return sorted_latencies[k]

    def get_tool_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Returns the success/failure stats for all tools."""
        return self.tool_usage_stats.copy()

    def clear_data(self) -> None:
        """Clears all stored metrics."""
        self.tool_load_times.clear()
        self.memory_search_latencies.clear()
        self.tool_usage_stats.clear()
        self.plan_generation_latencies.clear()
        self.plan_execution_latencies.clear()


# Singleton instance to be used across the application
metrics_manager: MetricsManager = MetricsManager()
