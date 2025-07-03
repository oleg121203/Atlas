"""
System Monitor Plugin for Atlas.

This plugin provides system monitoring capabilities including:
- CPU usage monitoring
- Memory usage tracking
- Disk space monitoring
- Network activity tracking
- Process monitoring
"""

import asyncio
import contextlib
import logging
import platform
from typing import Any, Dict, List, Optional

import psutil

from core.plugin_system import PluginBase

logger = logging.getLogger(__name__)


class SystemMonitorPlugin(PluginBase):
    """
    System monitoring plugin for Atlas.

    Provides real-time system resource monitoring with configurable
    alerts and historical data tracking.
    """

    def __init__(self, name: str = "system_monitor", version: str = "1.0.0"):
        """Initialize the System Monitor plugin."""
        super().__init__(name, version)
        self.monitoring = False
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
        }
        self.monitoring_task = None

    async def initialize(self) -> None:
        """Initialize the plugin."""
        try:
            super().initialize()

            # Test psutil availability
            psutil.cpu_percent()
            psutil.virtual_memory()

            logger.info(f"System Monitor plugin initialized on {platform.system()}")
            self.is_active = True

        except Exception as e:
            logger.error(f"Failed to initialize System Monitor plugin: {e}")
            self.is_active = False
            raise

    async def shutdown(self) -> None:
        """Shut down the plugin and stop monitoring."""
        try:
            await self.stop_monitoring()
            super().shutdown()
            logger.info("System Monitor plugin shut down")

        except Exception as e:
            logger.error(f"Error shutting down System Monitor plugin: {e}")

    async def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information and current usage."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "load_avg": psutil.getloadavg()
                if hasattr(psutil, "getloadavg")
                else None,
            }
        except Exception as e:
            logger.error(f"Error getting CPU info: {e}")
            return {"error": str(e)}

    async def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information and current usage."""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()

            return {
                "virtual_memory": {
                    "total": virtual_mem.total,
                    "used": virtual_mem.used,
                    "free": virtual_mem.free,
                    "percent": virtual_mem.percent,
                    "available": virtual_mem.available,
                },
                "swap_memory": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "free": swap_mem.free,
                    "percent": swap_mem.percent,
                },
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {"error": str(e)}

    async def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information and usage for all mounted drives."""
        try:
            disk_info = {}
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100,
                    }
                except PermissionError:
                    # Some partitions may not be accessible
                    disk_info[partition.device] = {"error": "Permission denied"}

            return disk_info

        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return {"error": str(e)}

    async def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information and statistics."""
        try:
            net_io = psutil.net_io_counters(pernic=True)
            net_connections = len(psutil.net_connections())

            network_info = {
                "interfaces": {},
                "total_connections": net_connections,
            }

            for interface, stats in net_io.items():
                network_info["interfaces"][interface] = {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                    "dropin": stats.dropin,
                    "dropout": stats.dropout,
                }

            return network_info

        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {"error": str(e)}

    async def get_process_info(self, limit: int = 10) -> Dict[str, Any]:
        """Get information about running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                    processes.append(proc.info)

            # Sort by CPU usage
            processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)

            return {
                "total_processes": len(processes),
                "top_processes": processes[:limit],
                "system_boot_time": psutil.boot_time(),
            }

        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {"error": str(e)}

    async def get_system_summary(self) -> Dict[str, Any]:
        """Get a comprehensive system summary."""
        try:
            tasks = await asyncio.gather(
                self.get_cpu_info(),
                self.get_memory_info(),
                self.get_disk_info(),
                self.get_network_info(),
                self.get_process_info(5),
                return_exceptions=True,
            )

            cpu_info, memory_info, disk_info, network_info, process_info = tasks

            return {
                "timestamp": asyncio.get_event_loop().time(),
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                },
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info,
                "processes": process_info,
            }

        except Exception as e:
            logger.error(f"Error getting system summary: {e}")
            return {"error": str(e)}

    async def start_monitoring(self, interval: float = 5.0) -> bool:
        """Start continuous system monitoring."""
        if self.monitoring:
            logger.warning("Monitoring already running")
            return False

        try:
            self.monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
            logger.info(f"Started system monitoring with {interval}s interval")
            return True

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self.monitoring = False
            return False

    async def stop_monitoring(self) -> bool:
        """Stop continuous system monitoring."""
        if not self.monitoring:
            return True

        try:
            self.monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self.monitoring_task
                self.monitoring_task = None

            logger.info("Stopped system monitoring")
            return True

        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return False

    async def _monitoring_loop(self, interval: float) -> None:
        """Internal monitoring loop."""
        while self.monitoring:
            try:
                summary = await self.get_system_summary()

                # Check for threshold alerts
                await self._check_alerts(summary)

                # Sleep for the specified interval
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

    async def _check_alerts(self, summary: Dict[str, Any]) -> None:
        """Check system metrics against alert thresholds."""
        try:
            alerts = []

            # Check CPU usage
            cpu_info = summary.get("cpu", {})
            cpu_percent = cpu_info.get("cpu_percent", 0)
            if cpu_percent > self.alert_thresholds["cpu_percent"]:
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")

            # Check memory usage
            memory_info = summary.get("memory", {})
            memory_percent = memory_info.get("virtual_memory", {}).get("percent", 0)
            if memory_percent > self.alert_thresholds["memory_percent"]:
                alerts.append(f"High memory usage: {memory_percent:.1f}%")

            # Check disk usage
            disk_info = summary.get("disk", {})
            for device, info in disk_info.items():
                if isinstance(info, dict) and "percent" in info:
                    disk_percent = info["percent"]
                    if disk_percent > self.alert_thresholds["disk_percent"]:
                        alerts.append(
                            f"High disk usage on {device}: {disk_percent:.1f}%"
                        )

            # Log alerts
            for alert in alerts:
                logger.warning(f"SYSTEM ALERT: {alert}")

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    def set_alert_threshold(self, metric: str, threshold: float) -> bool:
        """Set alert threshold for a specific metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            logger.info(f"Set {metric} alert threshold to {threshold}")
            return True
        else:
            logger.error(f"Unknown metric: {metric}")
            return False

    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        metadata = super().get_metadata()
        metadata.update(
            {
                "description": "System monitoring and resource tracking",
                "author": "Atlas System",
                "category": "monitoring",
                "monitoring_active": self.monitoring,
                "alert_thresholds": self.alert_thresholds,
                "capabilities": [
                    "cpu_monitoring",
                    "memory_monitoring",
                    "disk_monitoring",
                    "network_monitoring",
                    "process_monitoring",
                    "system_alerts",
                ],
            }
        )
        return metadata


# Export the plugin class for discovery
SystemMonitorPlugin = SystemMonitorPlugin
