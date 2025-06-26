"""
Monitoring system for the Atlas application.

This module provides functionality to monitor critical components, track performance metrics,
and detect anomalies or performance regressions in the application.
"""

import time
from typing import Dict, List, Optional, Callable
from threading import Thread
import psutil
import os
from collections import deque
import logging

from core.config import get_config
from core.logging import get_logger

# Logger specifically for monitoring
logger = get_logger("Monitoring")

# Performance metrics storage (recent 100 measurements per component)
PERFORMANCE_METRICS: Dict[str, deque] = {}
METRICS_MAX_SIZE = 100

# Thresholds for performance warnings (in milliseconds)
PERFORMANCE_THRESHOLDS: Dict[str, float] = {
    "screen_tools": 100.0,  # Screen/input tools should be <100ms
    "planning_ops": 500.0,  # Planning operations should be <500ms
    "memory_ops": 200.0,    # Memory operations should be <200ms
}

# Alert handlers
_alert_handlers: List[Callable[[str, str, dict], None]] = []

# Background monitoring thread
_monitoring_thread: Optional[Thread] = None
_monitoring_active = False


def initialize_monitoring() -> bool:
    """
    Initialize the monitoring system and start background monitoring thread.
    
    Returns:
        bool: True if initialization successful
    """
    global _monitoring_thread, _monitoring_active
    if _monitoring_thread is not None:
        return True
    
    try:
        config = get_config()
        monitoring_enabled = config.get("monitoring_enabled", True)
        if not monitoring_enabled:
            logger.info("Monitoring system disabled by configuration")
            return False
            
        _monitoring_active = True
        _monitoring_thread = Thread(target=__monitoring_loop, daemon=True)
        _monitoring_thread.start()
        logger.info("Monitoring system initialized and background thread started")
        return True
    except Exception as e:
        logger.error("Failed to initialize monitoring system: %s", str(e))
        return False


def start_monitoring():
    """Start the monitoring system."""
    logger.info("Starting monitoring system")
    # Placeholder for actual monitoring initialization
    return True


def track_performance(component: str, category: str, duration_ms: float, 
                     details: Optional[dict] = None) -> None:
    """
    Track performance metrics for a component operation.
    
    Args:
        component (str): Name of the component
        category (str): Category of operation (screen_tools, planning_ops, memory_ops)
        duration_ms (float): Duration of operation in milliseconds
        details (dict, optional): Additional details about the operation
    """
    if component not in PERFORMANCE_METRICS:
        PERFORMANCE_METRICS[component] = deque(maxlen=METRICS_MAX_SIZE)
    
    metric = {
        "timestamp": time.time(),
        "category": category,
        "duration_ms": duration_ms,
        "details": details or {}
    }
    PERFORMANCE_METRICS[component].append(metric)
    
    # Check if operation exceeds performance threshold
    threshold = PERFORMANCE_THRESHOLDS.get(category, 1000.0)
    if duration_ms > threshold:
        alert(
            f"Performance Warning: {component}",
            f"Operation in category {category} exceeded threshold: {duration_ms:.2f}ms > {threshold:.2f}ms",
            metric
        )
    
    logger.debug("Performance tracked for %s (%s): %.2fms", component, category, duration_ms)


def get_performance_stats(component: str) -> Optional[dict]:
    """
    Get performance statistics for a component.
    
    Args:
        component (str): Name of component to get stats for
        
    Returns:
        dict: Statistics including average, min, max duration, and count of measurements
    """
    if component not in PERFORMANCE_METRICS or not PERFORMANCE_METRICS[component]:
        return None
    
    durations = [m["duration_ms"] for m in PERFORMANCE_METRICS[component]]
    return {
        "component": component,
        "count": len(durations),
        "average_ms": sum(durations) / len(durations),
        "min_ms": min(durations),
        "max_ms": max(durations),
        "last_10_measurements": list(PERFORMANCE_METRICS[component])[-10:]
    }


def register_alert_handler(handler: Callable[[str, str, dict], None]) -> None:
    """
    Register a handler for alerts.
    
    Args:
        handler: Function that takes title, message, and data dict as arguments
    """
    _alert_handlers.append(handler)
    logger.debug("New alert handler registered, total handlers: %d", len(_alert_handlers))


def alert(title: str, message: str, data: Optional[dict] = None) -> None:
    """
    Raise an alert to all registered handlers and log it.
    
    Args:
        title (str): Alert title
        message (str): Alert message
        data (dict, optional): Additional data associated with alert
    """
    logger.warning("ALERT: %s - %s", title, message)
    for handler in _alert_handlers:
        try:
            handler(title, message, data or {})
        except Exception as e:
            logger.error("Error in alert handler: %s", str(e))


def system_monitoring_loop() -> None:
    """
    Background thread loop to monitor system resources and application health.
    """
    global _monitoring_active
    check_interval = 300  # Check every 5 minutes
    process = psutil.Process(os.getpid())
    
    logger.info("System monitoring loop started")
    while _monitoring_active:
        try:
            # Monitor memory usage
            mem_info = process.memory_info()
            memory_mb = mem_info.rss / 1024 / 1024  # Convert to MB
            if memory_mb > 2048:  # Alert if using more than 2GB
                alert(
                    "High Memory Usage",
                    f"Atlas is using {memory_mb:.2f}MB of memory",
                    {"memory_mb": memory_mb, "memory_info": str(mem_info)}
                )
            
            # Monitor CPU usage
            cpu_percent = process.cpu_percent(interval=1)
            if cpu_percent > 80:
                alert(
                    "High CPU Usage",
                    f"Atlas CPU usage at {cpu_percent:.1f}%",
                    {"cpu_percent": cpu_percent}
                )
            
            # Check performance metrics for anomalies
            for component, metrics in PERFORMANCE_METRICS.items():
                if not metrics:
                    continue
                stats = get_performance_stats(component)
                if stats and stats["average_ms"] > PERFORMANCE_THRESHOLDS.get(
                        stats["last_10_measurements"][0]["category"], 1000.0):
                    alert(
                        f"Performance Degradation: {component}",
                        f"Average operation time {stats['average_ms']:.2f}ms exceeds threshold",
                        stats
                    )
            
            time.sleep(check_interval)
        except Exception as e:
            logger.error("Error in system monitoring loop: %s", str(e))
            time.sleep(check_interval)


def stop_monitoring() -> None:
    """
    Stop the background monitoring thread.
    """
    global _monitoring_active, _monitoring_thread
    _monitoring_active = False
    if _monitoring_thread is not None:
        _monitoring_thread.join(timeout=2.0)
        _monitoring_thread = None
    logger.info("Monitoring system stopped")
