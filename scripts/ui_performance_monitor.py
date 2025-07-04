#!/usr/bin/env python
"""
UI Performance Monitor

This script implements real-time monitoring of UI performance metrics,
providing feedback on render times, event handling latency, and memory usage.
It helps identify and fix UI performance issues.
"""

import builtins
import contextlib
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time

# Try importing UI libraries - these may vary depending on what's installed
try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    from PySide6.QtCore import QObject, QThread, QTimer, Signal
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QProgressBar,
        QVBoxLayout,
        QWidget,
    )

    UI_LIBRARY = "PySide6"
except ImportError:
    try:
        from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
        from PyQt6.QtCore import QObject, QThread, QTimer
        from PyQt6.QtCore import pyqtSignal as Signal
        from PyQt6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QProgressBar,
            QVBoxLayout,
            QWidget,
        )

        UI_LIBRARY = "PyQt6"
    except ImportError:
        print(
            "Error: Neither PySide6 nor PyQt6 is installed. UI monitoring requires one of these libraries."
        )
        print("You can install PySide6 with: pip install PySide6")
        UI_LIBRARY = None

# Try importing psutil for memory monitoring
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil is not installed. Memory monitoring will be limited.")
    print("You can install psutil with: pip install psutil")


class UIPerformanceCollector(QObject if UI_LIBRARY else object):
    """Collects UI performance metrics."""

    # Define signals if UI library is available
    if UI_LIBRARY:
        data_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.collecting = False
        self.metrics = {
            "render_times": [],
            "event_latency": [],
            "memory_usage": [],
            "timestamps": [],
        }
        self.timer = QTimer() if UI_LIBRARY else None
        if self.timer:
            self.timer.timeout.connect(self.collect_metrics)

        # Monkey patching helpers
        self.original_functions = {}
        self.patched_widgets = set()

        # Start time for measuring render times
        self.render_start_time = None

    def start_collecting(self, interval_ms=1000):
        """Start collecting performance metrics."""
        self.collecting = True
        if self.timer:
            self.timer.start(interval_ms)

    def stop_collecting(self):
        """Stop collecting performance metrics."""
        self.collecting = False
        if self.timer:
            self.timer.stop()

    def collect_metrics(self):
        """Collect current performance metrics."""
        timestamp = datetime.datetime.now()

        # Measure memory usage
        memory_usage = self.measure_memory_usage()

        # Append metrics
        self.metrics["memory_usage"].append(memory_usage)
        self.metrics["timestamps"].append(timestamp.strftime("%H:%M:%S"))

        # Limit the size of the metrics arrays
        max_data_points = 100
        for key in ["render_times", "event_latency", "memory_usage", "timestamps"]:
            if len(self.metrics[key]) > max_data_points:
                self.metrics[key] = self.metrics[key][-max_data_points:]

        # Emit signal if UI library is available
        if UI_LIBRARY and hasattr(self, "data_updated"):
            self.data_updated.emit(dict(self.metrics))

    def measure_memory_usage(self):
        """Measure the current memory usage of the application."""
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        else:
            # Fallback method using subprocess
            if sys.platform == "win32":
                # Windows - use tasklist
                try:
                    cmd = f'tasklist /FI "PID eq {os.getpid()}" /FO CSV'
                    output = subprocess.check_output(cmd, shell=True).decode("utf-8")
                    lines = output.strip().split("\n")
                    if len(lines) >= 2:
                        # Parse the CSV output
                        parts = lines[1].strip('"').split('","')
                        if len(parts) >= 5:
                            # Memory usage is in KB, convert to MB
                            mem_str = parts[4].replace(" K", "").replace(",", "")
                            return float(mem_str) / 1024
                except:
                    pass
            else:
                # Linux/macOS - use ps
                try:
                    cmd = f"ps -p {os.getpid()} -o rss="
                    output = subprocess.check_output(cmd, shell=True).decode("utf-8")
                    # Output is in KB, convert to MB
                    return float(output.strip()) / 1024
                except:
                    pass

        # If all else fails
        return 0

    def patch_widget_render(self, widget_class):
        """Patch a widget class to measure render time."""
        if not UI_LIBRARY or widget_class in self.patched_widgets:
            return

        self.patched_widgets.add(widget_class)

        # Save the original paintEvent method
        original_paint_event = widget_class.paintEvent
        self.original_functions[widget_class] = original_paint_event

        # Create a wrapper method
        def paint_event_wrapper(self_widget, event):
            collector = self  # The collector instance
            collector.render_start_time = time.time()
            # Call the original method
            result = original_paint_event(self_widget, event)
            # Calculate render time
            if collector.render_start_time is not None:
                render_time = (time.time() - collector.render_start_time) * 1000  # ms
                collector.metrics["render_times"].append(render_time)
                collector.render_start_time = None
            return result

        # Replace the original method with the wrapper
        widget_class.paintEvent = paint_event_wrapper

    def patch_event_handler(self, widget_class, event_method_name):
        """Patch an event handler method to measure latency."""
        if not UI_LIBRARY:
            return

        # Get the original method
        if not hasattr(widget_class, event_method_name):
            return

        original_method = getattr(widget_class, event_method_name)

        # Create a wrapper method
        def event_handler_wrapper(self_widget, event):
            collector = self  # The collector instance
            start_time = time.time()
            # Call the original method
            result = original_method(self_widget, event)
            # Calculate latency
            latency = (time.time() - start_time) * 1000  # ms
            collector.metrics["event_latency"].append(latency)
            return result

        # Replace the original method with the wrapper
        setattr(widget_class, event_method_name, event_handler_wrapper)

    def save_metrics(self, filename=None):
        """Save collected metrics to a JSON file."""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ui_performance_{timestamp}.json"

        # Prepare the data for serialization
        serializable_metrics = dict(self.metrics)

        # Convert any non-serializable objects
        if "timestamps" in serializable_metrics:
            serializable_metrics["timestamps"] = [
                ts if isinstance(ts, str) else ts.strftime("%Y-%m-%d %H:%M:%S")
                for ts in serializable_metrics["timestamps"]
            ]

        # Save to file
        with open(filename, "w") as f:
            json.dump(serializable_metrics, f, indent=2)

        print(f"Metrics saved to {filename}")
        return filename


def generate_html_report(metrics_file):
    """Generate an HTML report from the metrics JSON file."""
    if not os.path.exists(metrics_file):
        print(f"Error: Metrics file {metrics_file} not found.")
        return None

    # Read the metrics data
    with open(metrics_file, "r") as f:
        metrics = json.load(f)

    # Generate the HTML report
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UI Performance Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        h1, h2 {{
            color: #333;
        }}
        .chart-container {{
            width: 100%;
            height: 300px;
            margin-bottom: 30px;
        }}
        .stats-container {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}
        .stat-box {{
            flex: 1;
            min-width: 200px;
            margin: 10px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.05);
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>UI Performance Report</h1>
        <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value" id="avg-render-time">-</div>
                <div class="stat-label">Avg Render Time (ms)</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="max-render-time">-</div>
                <div class="stat-label">Max Render Time (ms)</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="avg-event-latency">-</div>
                <div class="stat-label">Avg Event Latency (ms)</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="avg-memory">-</div>
                <div class="stat-label">Avg Memory Usage (MB)</div>
            </div>
        </div>

        <h2>Render Times</h2>
        <div class="chart-container">
            <canvas id="render-times-chart"></canvas>
        </div>

        <h2>Event Latency</h2>
        <div class="chart-container">
            <canvas id="event-latency-chart"></canvas>
        </div>

        <h2>Memory Usage</h2>
        <div class="chart-container">
            <canvas id="memory-usage-chart"></canvas>
        </div>
    </div>

    <script>
        // Parse the metrics data
        const metrics = {json.dumps(metrics)};

        // Calculate statistics
        function calculateStats(data) {{
            if (!data || data.length === 0) return {{ avg: 0, max: 0, min: 0 }};
            const sum = data.reduce((a, b) => a + b, 0);
            return {{
                avg: (sum / data.length).toFixed(2),
                max: Math.max(...data).toFixed(2),
                min: Math.min(...data).toFixed(2)
            }};
        }}

        const renderStats = calculateStats(metrics.render_times);
        const latencyStats = calculateStats(metrics.event_latency);
        const memoryStats = calculateStats(metrics.memory_usage);

        // Update the stats boxes
        document.getElementById('avg-render-time').textContent = renderStats.avg;
        document.getElementById('max-render-time').textContent = renderStats.max;
        document.getElementById('avg-event-latency').textContent = latencyStats.avg;
        document.getElementById('avg-memory').textContent = memoryStats.avg;

        // Create charts
        const renderTimesChart = new Chart(
            document.getElementById('render-times-chart').getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: metrics.timestamps,
                    datasets: [{{
                        label: 'Render Time (ms)',
                        data: metrics.render_times,
                        borderColor: '#0066cc',
                        backgroundColor: 'rgba(0, 102, 204, 0.1)',
                        fill: true
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }}
        );

        const eventLatencyChart = new Chart(
            document.getElementById('event-latency-chart').getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: metrics.timestamps,
                    datasets: [{{
                        label: 'Event Latency (ms)',
                        data: metrics.event_latency,
                        borderColor: '#ff6600',
                        backgroundColor: 'rgba(255, 102, 0, 0.1)',
                        fill: true
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }}
        );

        const memoryUsageChart = new Chart(
            document.getElementById('memory-usage-chart').getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: metrics.timestamps,
                    datasets: [{{
                        label: 'Memory Usage (MB)',
                        data: metrics.memory_usage,
                        borderColor: '#33cc33',
                        backgroundColor: 'rgba(51, 204, 51, 0.1)',
                        fill: true
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }}
        );
    </script>
</body>
</html>
"""

    # Write the HTML report to a file
    report_file = f"ui_performance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_file, "w") as f:
        f.write(html_content)

    print(f"HTML report generated: {report_file}")
    return report_file


class UIPerformanceMonitor(QMainWindow if UI_LIBRARY else object):
    """UI Performance Monitor window."""

    def __init__(self):
        if UI_LIBRARY:
            super().__init__()
            self.setWindowTitle("UI Performance Monitor")
            self.resize(800, 600)

            # Create the central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Add labels for metrics
            self.render_time_label = QLabel("Render Time: 0 ms")
            self.event_latency_label = QLabel("Event Latency: 0 ms")
            self.memory_usage_label = QLabel("Memory Usage: 0 MB")

            layout.addWidget(QLabel("<h2>UI Performance Metrics</h2>"))
            layout.addWidget(self.render_time_label)
            layout.addWidget(self.event_latency_label)
            layout.addWidget(self.memory_usage_label)

            # Add charts for metrics
            self.setup_charts(layout)

            # Create the performance collector
            self.collector = UIPerformanceCollector()
            self.collector.data_updated.connect(self.update_metrics)
            self.collector.start_collecting()
        else:
            # Non-UI mode
            self.collector = UIPerformanceCollector()

    def setup_charts(self, layout):
        """Set up charts for displaying metrics."""
        if not UI_LIBRARY:
            return

        # Render Time Chart
        render_time_series = QLineSeries()
        render_time_chart = QChart()
        render_time_chart.addSeries(render_time_series)
        render_time_chart.setTitle("Render Times (ms)")
        render_time_chart.legend().hide()

        render_time_axisX = QValueAxis()
        render_time_axisX.setRange(0, 100)
        render_time_axisX.setLabelFormat("%d")
        render_time_axisX.setTitleText("Sample")

        render_time_axisY = QValueAxis()
        render_time_axisY.setRange(0, 50)  # 0-50ms
        render_time_axisY.setLabelFormat("%d")
        render_time_axisY.setTitleText("Time (ms)")

        render_time_chart.addAxis(render_time_axisX, 1)  # 1 = Qt.AlignBottom
        render_time_chart.addAxis(render_time_axisY, 0)  # 0 = Qt.AlignLeft
        render_time_series.attachAxis(render_time_axisX)
        render_time_series.attachAxis(render_time_axisY)

        render_time_chart_view = QChartView(render_time_chart)
        layout.addWidget(render_time_chart_view)
        self.render_time_series = render_time_series

        # Memory Usage Chart
        memory_series = QLineSeries()
        memory_chart = QChart()
        memory_chart.addSeries(memory_series)
        memory_chart.setTitle("Memory Usage (MB)")
        memory_chart.legend().hide()

        memory_axisX = QValueAxis()
        memory_axisX.setRange(0, 100)
        memory_axisX.setLabelFormat("%d")
        memory_axisX.setTitleText("Sample")

        memory_axisY = QValueAxis()
        memory_axisY.setRange(0, 500)  # 0-500MB
        memory_axisY.setLabelFormat("%d")
        memory_axisY.setTitleText("Memory (MB)")

        memory_chart.addAxis(memory_axisX, 1)  # 1 = Qt.AlignBottom
        memory_chart.addAxis(memory_axisY, 0)  # 0 = Qt.AlignLeft
        memory_series.attachAxis(memory_axisX)
        memory_series.attachAxis(memory_axisY)

        memory_chart_view = QChartView(memory_chart)
        layout.addWidget(memory_chart_view)
        self.memory_series = memory_series

    def update_metrics(self, metrics):
        """Update the UI with the latest metrics."""
        if not UI_LIBRARY:
            return

        # Update labels
        render_times = metrics.get("render_times", [])
        event_latency = metrics.get("event_latency", [])
        memory_usage = metrics.get("memory_usage", [])

        if render_times:
            avg_render = sum(render_times) / len(render_times)
            self.render_time_label.setText(f"Render Time: {avg_render:.2f} ms")

        if event_latency:
            avg_latency = sum(event_latency) / len(event_latency)
            self.event_latency_label.setText(f"Event Latency: {avg_latency:.2f} ms")

        if memory_usage:
            latest_memory = memory_usage[-1]
            self.memory_usage_label.setText(f"Memory Usage: {latest_memory:.2f} MB")

        # Update charts
        self.render_time_series.clear()
        for i, value in enumerate(render_times[-100:]):
            self.render_time_series.append(i, value)

        self.memory_series.clear()
        for i, value in enumerate(memory_usage[-100:]):
            self.memory_series.append(i, value)


def monitor_ui_application():
    """Start monitoring a UI application."""
    if not UI_LIBRARY:
        print(
            "Error: UI monitoring requires PySide6 or PyQt6. Please install one of these libraries."
        )
        return

    app = QApplication(sys.argv)
    monitor = UIPerformanceMonitor()
    monitor.show()
    sys.exit(app.exec())


def inject_into_existing_app(app_script_path):
    """Inject performance monitoring into an existing application."""
    if not os.path.exists(app_script_path):
        print(f"Error: Application script not found: {app_script_path}")
        return

    # Create a temporary script that runs the application with monitoring
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        temp_script_path = f.name
        f.write(f"""
 import sys
import os

# Add the current directory to sys.path
sys.path.insert(0, os.getcwd())

# Import the original script
original_script_path = {repr(app_script_path)}
original_module_name = os.path.basename(original_script_path).replace('.py', '')

# Import the monitoring module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_performance_monitor

# Create a collector instance
collector = ui_performance_monitor.UIPerformanceCollector()

# Execute the original script with monitoring injected
with open(original_script_path, 'r') as f:
    script_content = f.read()

# Automatically patch UI widget classes for monitoring
def monkey_patch_ui():
    try:
        from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit
        widgets = [QWidget, QPushButton, QLabel, QLineEdit, QTextEdit]
        for widget in widgets:
            collector.patch_widget_render(widget)
            collector.patch_event_handler(widget, 'mousePressEvent')
            collector.patch_event_handler(widget, 'keyPressEvent')
    except ImportError:
        try:
            from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit
            widgets = [QWidget, QPushButton, QLabel, QLineEdit, QTextEdit]
            for widget in widgets:
                collector.patch_widget_render(widget)
                collector.patch_event_handler(widget, 'mousePressEvent')
                collector.patch_event_handler(widget, 'keyPressEvent')
        except ImportError:
            pass

# Call the monkey patching function
monkey_patch_ui()

# Start collecting metrics
collector.start_collecting(500)  # 500ms interval

# Define cleanup function to save metrics when the app exits
old_exit = sys.exit
def exit_handler(code=0):
    collector.stop_collecting()
    metrics_file = collector.save_metrics()
    ui_performance_monitor.generate_html_report(metrics_file)
    old_exit(code)

sys.exit = exit_handler

# Redirect print to collect output
old_print = print
def print_handler(*args, **kwargs):
    old_print(*args, **kwargs)
    if 'Monitoring UI performance' not in str(args):
        old_print('Monitoring UI performance... Press Ctrl+C to stop and generate report')

print = print_handler

# Run the original script
exec(script_content, {{'__name__': '__main__'}})
        """)

    print(f"Temporary monitoring script created at: {temp_script_path}")
    print("Running application with performance monitoring injected...")
    print("Press Ctrl+C to stop the application and generate a performance report.")

    # Run the temporary script
    try:
        subprocess.run([sys.executable, temp_script_path], check=False)
    except KeyboardInterrupt:
        print("Application stopped. Generating performance report...")
    finally:
        # Clean up the temporary script
        with contextlib.suppress(builtins.BaseException):
            os.unlink(temp_script_path)


def main():
    """Main function to run the script."""
    print("Atlas UI Performance Monitor")
    print("============================")

    if len(sys.argv) == 1:
        # No arguments provided, show the standalone monitor
        print("Starting standalone UI performance monitor...")
        monitor_ui_application()
    elif len(sys.argv) == 2:
        # Application script path provided, inject monitoring
        app_script = sys.argv[1]
        print(f"Injecting performance monitoring into: {app_script}")
        inject_into_existing_app(app_script)
    else:
        # Invalid arguments
        print("Usage:")
        print(
            "  python ui_performance_monitor.py                  # Start standalone monitor"
        )
        print(
            "  python ui_performance_monitor.py path/to/app.py   # Monitor existing app"
        )


if __name__ == "__main__":
    main()
