import time
import psutil
import logging
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self, interval: int = 60):
        """
        Initialize the SystemMonitor with a specified monitoring interval.

        Args:
            interval (int): Time interval in seconds between monitoring checks.
        """
        self.interval = interval
        self.is_running = False
        self.metrics = []
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self) -> None:
        """
        Start continuous monitoring of system resources and critical components.
        """
        try:
            self.is_running = True
            self.logger.info("Started system monitoring")
            while self.is_running:
                self.collect_metrics()
                time.sleep(self.interval)
        except Exception as e:
            self.logger.error(f"Error in system monitoring: {e}")
            self.is_running = False

    def stop_monitoring(self) -> None:
        """
        Stop the continuous monitoring process.
        """
        self.is_running = False
        self.logger.info("Stopped system monitoring")

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect system metrics such as CPU, memory, disk, and network usage.

        Returns:
            Dict[str, Any]: Collected system metrics.
        """
        try:
            timestamp = datetime.now().isoformat()
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            metric = {
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'memory_percent': memory.percent,
                'disk_used': disk.used,
                'disk_total': disk.total,
                'disk_percent': disk.percent,
                'network_bytes_sent': net.bytes_sent,
                'network_bytes_recv': net.bytes_recv
            }
            self.metrics.append(metric)
            self.logger.info(f"Collected system metrics at {timestamp}")
            return metric
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}

    def get_metrics_dataframe(self) -> pd.DataFrame:
        """
        Convert collected metrics to a pandas DataFrame for analysis.

        Returns:
            pd.DataFrame: DataFrame containing all collected metrics.
        """
        try:
            return pd.DataFrame(self.metrics)
        except Exception as e:
            self.logger.error(f"Error converting metrics to DataFrame: {e}")
            return pd.DataFrame()

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check the health of critical system components and return status.

        Returns:
            Dict[str, Any]: Health status of critical system components.
        """
        try:
            latest_metrics = self.metrics[-1] if self.metrics else self.collect_metrics()
            health_status = {
                'timestamp': latest_metrics.get('timestamp', datetime.now().isoformat()),
                'cpu_status': 'Healthy' if latest_metrics.get('cpu_percent', 100) < 80 else 'Critical',
                'memory_status': 'Healthy' if latest_metrics.get('memory_percent', 100) < 80 else 'Critical',
                'disk_status': 'Healthy' if latest_metrics.get('disk_percent', 100) < 80 else 'Critical',
                'overall_status': 'Healthy'
            }
            if any(status == 'Critical' for status in [health_status['cpu_status'], health_status['memory_status'], health_status['disk_status']]):
                health_status['overall_status'] = 'Critical'
            self.logger.info(f"System health check: {health_status['overall_status']}")
            return health_status
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            return {'overall_status': 'Unknown', 'error': str(e)}

    def alert_on_threshold(self, thresholds: Dict[str, float]) -> List[str]:
        """
        Check if any metrics exceed defined thresholds and return alerts.

        Args:
            thresholds (Dict[str, float]): Dictionary of metric names and their threshold values.

        Returns:
            List[str]: List of alert messages for metrics exceeding thresholds.
        """
        try:
            alerts = []
            latest_metrics = self.metrics[-1] if self.metrics else self.collect_metrics()
            for metric, threshold in thresholds.items():
                if metric in latest_metrics and latest_metrics[metric] > threshold:
                    alert_msg = f"Alert: {metric} exceeded threshold of {threshold}. Current value: {latest_metrics[metric]}"
                    alerts.append(alert_msg)
                    self.logger.warning(alert_msg)
            return alerts
        except Exception as e:
            self.logger.error(f"Error checking thresholds for alerts: {e}")
            return [f"Error checking thresholds: {str(e)}"]
