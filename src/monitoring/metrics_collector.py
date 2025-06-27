import time
from dataclasses import dataclass
from typing import Dict, List

import psutil


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict
    process_count: int
    timestamp: float


class MetricsCollector:
    def __init__(self, collection_interval: int = 30):
        self.collection_interval = collection_interval
        self.metrics_history: List[SystemMetrics] = []
        self.alerts_config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
        }
        self.running = False

    def collect_metrics(self) -> SystemMetrics:
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage("/").percent,
            network_io=psutil.net_io_counters()._asdict(),
            process_count=len(psutil.pids()),
            timestamp=time.time(),
        )

    def check_alerts(self, metrics: SystemMetrics):
        alerts = []
        if metrics.cpu_percent > self.alerts_config["cpu_threshold"]:
            alerts.append(f"High CPU usage: {metrics.cpu_percent}%")
        if metrics.memory_percent > self.alerts_config["memory_threshold"]:
            alerts.append(f"High memory usage: {metrics.memory_percent}%")
        if metrics.disk_usage > self.alerts_config["disk_threshold"]:
            alerts.append(f"High disk usage: {metrics.disk_usage}%")
        return alerts
