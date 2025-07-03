"""
Performance Panel for Atlas AI Platform.

This module provides a comprehensive PySide6-based performance monitoring interface
for tracking system metrics, response times, and resource usage in the Atlas AI platform.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MetricWidget(QFrame):
    """
    Individual metric display widget showing a label, value, and optional progress bar.
    """

    def __init__(
        self, name: str, unit: str = "", show_progress: bool = False, parent=None
    ):
        super().__init__(parent)
        self.name = name
        self.unit = unit
        self.show_progress = show_progress
        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self) -> None:
        """Set up the metric widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(3)

        # Metric name label
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet("font-weight: bold; color: #00ffff;")
        layout.addWidget(self.name_label)

        # Value label
        self.value_label = QLabel("0" + (" " + self.unit if self.unit else ""))
        self.value_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(self.value_label)

        # Optional progress bar
        if self.show_progress:
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)
        else:
            self.progress_bar = None

    def _apply_styling(self) -> None:
        """Apply cyberpunk styling to the metric widget."""
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 5px;
                margin: 2px;
            }

            QProgressBar {
                background-color: #1a1a1a;
                border: 1px solid #555555;
                border-radius: 3px;
                height: 20px;
            }

            QProgressBar::chunk {
                background-color: #00ffff;
                border-radius: 2px;
            }
        """)

    def update_value(self, value: Any, progress: Optional[float] = None) -> None:
        """
        Update the metric value and optional progress.

        Args:
            value: The new metric value
            progress: Optional progress percentage (0-100)
        """
        # Format the value display
        if isinstance(value, float):
            formatted_value = f"{value:.2f}"
        elif isinstance(value, int):
            formatted_value = str(value)
        else:
            formatted_value = str(value)

        display_text = formatted_value + (" " + self.unit if self.unit else "")
        self.value_label.setText(display_text)

        # Update progress bar if present
        if self.progress_bar and progress is not None:
            self.progress_bar.setValue(int(max(0, min(100, progress))))


class PerformancePanel(QFrame):
    """
    Comprehensive performance monitoring panel with real-time metrics display.

    This panel provides functionality for:
    - Real-time system metrics monitoring
    - Performance statistics tracking
    - Resource usage visualization
    - Detailed performance logs
    - Metric clearing and reset capabilities
    """

    # Signals for external communication
    clear_requested = Signal()
    export_requested = Signal()
    metric_threshold_exceeded = Signal(str, float)

    def __init__(
        self,
        parent=None,
        metrics_manager=None,
        on_clear: Optional[Callable[[], None]] = None,
        update_interval: int = 1000,  # milliseconds
    ):
        """
        Initialize the Performance Panel.

        Args:
            parent: Parent widget
            metrics_manager: Performance metrics manager instance
            on_clear: Callback for clearing performance data
            update_interval: Update interval in milliseconds
        """
        super().__init__(parent)

        self.metrics_manager = metrics_manager
        self.on_clear = on_clear
        self.update_interval = update_interval

        # Performance data storage
        self.metrics_history: Dict[str, List[float]] = {}
        self.last_update_time = time.time()

        # Metric widgets storage
        self.metric_widgets: Dict[str, MetricWidget] = {}

        self._setup_ui()
        self._connect_signals()
        self._apply_styling()
        self._start_update_timer()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_label = QLabel("Performance Monitoring")
        header_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #00ffff;"
        )
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Control buttons
        self.clear_button = QPushButton("Clear Data")
        self.clear_button.setMinimumWidth(100)
        header_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export")
        self.export_button.setMinimumWidth(80)
        header_layout.addWidget(self.export_button)

        layout.addWidget(header_frame)

        # Metrics scroll area
        metrics_scroll = QScrollArea()
        metrics_scroll.setWidgetResizable(True)
        metrics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        metrics_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Metrics container
        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout(self.metrics_container)
        self.metrics_layout.setSpacing(5)

        # Initialize default metrics
        self._create_default_metrics()

        metrics_scroll.setWidget(self.metrics_container)
        layout.addWidget(metrics_scroll, 1)  # Takes most space

        # Statistics display area
        stats_group = QGroupBox("Performance Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(150)
        self.stats_display.setPlaceholderText(
            "Performance statistics will appear here..."
        )
        stats_layout.addWidget(self.stats_display)

        layout.addWidget(stats_group)

        # Status bar
        self.status_label = QLabel("Monitoring active - Last updated: Never")
        self.status_label.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(self.status_label)

    def _create_default_metrics(self) -> None:
        """Create default performance metric widgets."""
        default_metrics = [
            ("CPU Usage", "%", True),
            ("Memory Usage", "%", True),
            ("Response Time", "ms", False),
            ("Operations/sec", "ops", False),
            ("Active Agents", "", False),
            ("Queue Size", "", False),
            ("Error Rate", "%", True),
            ("Uptime", "hrs", False),
        ]

        row = 0
        col = 0
        max_cols = 4

        for name, unit, show_progress in default_metrics:
            metric_widget = MetricWidget(name, unit, show_progress)
            self.metric_widgets[name.lower().replace(" ", "_")] = metric_widget

            self.metrics_layout.addWidget(metric_widget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _connect_signals(self) -> None:
        """Connect internal signals to callbacks."""
        self.clear_button.clicked.connect(self._on_clear)
        self.export_button.clicked.connect(self._on_export)

        # Connect to external callbacks
        if self.on_clear:
            self.clear_requested.connect(self.on_clear)

    def _apply_styling(self) -> None:
        """Apply cyberpunk-style theming to the panel."""
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 5px;
            }

            QGroupBox {
                font-weight: bold;
                color: #00ffff;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #00ffff;
                color: #000000;
            }

            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background-color: #00ffff;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #ffffff;
            }
        """)

    def _start_update_timer(self) -> None:
        """Start the automatic update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(self.update_interval)

    def _update_metrics(self) -> None:
        """Update all performance metrics."""
        current_time = time.time()

        # Simulate or collect real metrics
        metrics_data = self._collect_metrics()

        # Update metric widgets
        for metric_name, value in metrics_data.items():
            widget_key = metric_name.lower().replace(" ", "_")
            if widget_key in self.metric_widgets:
                # Calculate progress for percentage metrics
                progress = None
                if isinstance(value, (int, float)) and metric_name.endswith("%"):
                    progress = max(0, min(100, value))

                self.metric_widgets[widget_key].update_value(value, progress)

        # Update status
        self.status_label.setText(
            f"Monitoring active - Last updated: {time.strftime('%H:%M:%S')}"
        )

        # Check thresholds and emit warnings
        self._check_metric_thresholds(metrics_data)

        self.last_update_time = current_time

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics.

        Returns:
            Dictionary of metric names to values
        """
        metrics = {}
        self._populate_metrics(metrics)
        self._collect_uptime(metrics)
        return metrics

    def _populate_metrics(self, metrics: Dict[str, Any]) -> None:
        """Populate metrics dictionary based on availability of metrics_manager."""
        if self.metrics_manager is None:
            self._set_default_metrics(metrics)
        else:
            self._collect_system_metrics(metrics)
            self._collect_performance_metrics(metrics)

    def _set_default_metrics(self, metrics: Dict[str, Any]) -> None:
        """Set default values for all metrics if metrics_manager is None."""
        metrics["CPU Usage"] = 0.0
        metrics["Memory Usage"] = 0.0
        metrics["Response Time"] = 0.0
        metrics["Operations/sec"] = 0.0
        metrics["Active Agents"] = 0
        metrics["Queue Size"] = 0
        metrics["Error Rate"] = 0.0

    def _collect_system_metrics(self, metrics: Dict[str, Any]) -> None:
        """Collect system-related metrics."""
        if hasattr(self.metrics_manager, "get_cpu_usage"):
            cpu_usage = self.metrics_manager.get_cpu_usage()
            metrics["CPU Usage"] = cpu_usage
        else:
            metrics["CPU Usage"] = 0.0

        if hasattr(self.metrics_manager, "get_memory_usage"):
            memory_usage = self.metrics_manager.get_memory_usage()
            if isinstance(memory_usage, dict):
                metrics["Memory Usage"] = memory_usage.get("used_percent", 0.0)
            else:
                metrics["Memory Usage"] = memory_usage
        else:
            metrics["Memory Usage"] = 0.0

    def _collect_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Collect performance-related metrics."""
        if hasattr(self.metrics_manager, "get_response_time"):
            response_time = self.metrics_manager.get_response_time()
            metrics["Response Time"] = response_time
        else:
            metrics["Response Time"] = 0.0

        if hasattr(self.metrics_manager, "get_current_operations_per_second"):
            ops_per_sec = self.metrics_manager.get_current_operations_per_second()
            metrics["Operations/sec"] = ops_per_sec
        elif hasattr(self.metrics_manager, "get_operations_per_second"):
            ops_per_sec = self.metrics_manager.get_operations_per_second()
            metrics["Operations/sec"] = ops_per_sec
        else:
            metrics["Operations/sec"] = 0.0

        if hasattr(self.metrics_manager, "get_active_agents_count"):
            active_agents = self.metrics_manager.get_active_agents_count()
            metrics["Active Agents"] = active_agents
        elif hasattr(self.metrics_manager, "get_active_agents"):
            active_agents = self.metrics_manager.get_active_agents()
            metrics["Active Agents"] = active_agents
        else:
            metrics["Active Agents"] = 0

        if hasattr(self.metrics_manager, "get_current_queue_size"):
            queue_size = self.metrics_manager.get_current_queue_size()
            metrics["Queue Size"] = queue_size
        elif hasattr(self.metrics_manager, "get_queue_size"):
            queue_size = self.metrics_manager.get_queue_size()
            metrics["Queue Size"] = queue_size
        else:
            metrics["Queue Size"] = 0

        if hasattr(self.metrics_manager, "get_current_error_rate"):
            error_rate = self.metrics_manager.get_current_error_rate()
            metrics["Error Rate"] = error_rate
        elif hasattr(self.metrics_manager, "get_error_rate"):
            error_rate = self.metrics_manager.get_error_rate()
            metrics["Error Rate"] = error_rate
        else:
            metrics["Error Rate"] = 0.0

    def _collect_uptime(self, metrics: Dict[str, Any]) -> None:
        """Collect uptime metric."""
        base_time = (
            time.time() - self.last_update_time
            if hasattr(self, "last_update_time")
            else 0.0
        )
        uptime_hours = base_time / 3600
        metrics["Uptime"] = uptime_hours

    def _check_metric_thresholds(self, metrics: Dict[str, Any]) -> None:
        """
        Check metric values against thresholds and emit warnings.

        Args:
            metrics: Current metrics data
        """
        thresholds = {
            "CPU Usage": 80.0,
            "Memory Usage": 80.0,
            "Response Time": 500.0,
            "Error Rate": 10.0,
        }

        for metric_name, threshold in thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if isinstance(value, (int, float)) and value > threshold:
                    self.metric_threshold_exceeded.emit(metric_name, value)

    def _on_clear(self) -> None:
        """Handle clear button click."""
        self.clear_requested.emit()
        self._clear_local_data()

    def _on_export(self) -> None:
        """Handle export button click."""
        self.export_requested.emit()

    def _clear_local_data(self) -> None:
        """Clear local performance data."""
        self.metrics_history.clear()
        self.stats_display.clear()

        # Reset all metric widgets
        for widget in self.metric_widgets.values():
            widget.update_value(0, 0)

        self.update_stats("Performance data cleared.")

    # Public API methods for external control

    def update_stats(self, stats_text: str) -> None:
        """
        Update the statistics display area.

        Args:
            stats_text: Text to display in statistics area
        """
        self.stats_display.setPlainText(stats_text)

    def append_stats(self, stats_text: str) -> None:
        """
        Append text to the statistics display area.

        Args:
            stats_text: Text to append to statistics
        """
        self.stats_display.append(stats_text)

    def add_custom_metric(
        self, name: str, unit: str = "", show_progress: bool = False
    ) -> None:
        """
        Add a custom metric widget to the panel.

        Args:
            name: Name of the metric
            unit: Unit of measurement
            show_progress: Whether to show a progress bar
        """
        widget_key = name.lower().replace(" ", "_")
        if widget_key not in self.metric_widgets:
            metric_widget = MetricWidget(name, unit, show_progress)
            self.metric_widgets[widget_key] = metric_widget

            # Add to layout (find next available position)
            row = len(self.metric_widgets) // 4
            col = len(self.metric_widgets) % 4
            self.metrics_layout.addWidget(metric_widget, row, col)

    def update_metric(
        self, name: str, value: Any, progress: Optional[float] = None
    ) -> None:
        """
        Update a specific metric value.

        Args:
            name: Name of the metric
            value: New value for the metric
            progress: Optional progress percentage (0-100)
        """
        widget_key = name.lower().replace(" ", "_")
        if widget_key in self.metric_widgets:
            self.metric_widgets[widget_key].update_value(value, progress)

    def set_update_interval(self, interval_ms: int) -> None:
        """
        Set the update interval for automatic metric updates.

        Args:
            interval_ms: Update interval in milliseconds
        """
        self.update_interval = interval_ms
        if hasattr(self, "update_timer"):
            self.update_timer.setInterval(interval_ms)

    def start_monitoring(self) -> None:
        """Start the performance monitoring."""
        if hasattr(self, "update_timer"):
            self.update_timer.start()

    def stop_monitoring(self) -> None:
        """Stop the performance monitoring."""
        if hasattr(self, "update_timer"):
            self.update_timer.stop()

    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get the current metrics data.

        Returns:
            Dictionary of current metric values
        """
        return self._collect_metrics()
