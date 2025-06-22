#!/usr/bin/env python3
"""
Atlas Performance Monitor and Recovery
Continuously monitors Atlas performance and implements automatic recovery strategies
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AtlasPerformanceMonitor:
    """Monitors Atlas performance and implements recovery strategies."""

    PERFORMANCE_TARGETS = {
        "screen_tools": 100,    # ms
        "input_tools": 100,     # ms
        "planning": 500,        # ms
        "execution": 1000,      # ms
        "memory_search": 200,   # ms
    }

    def __init__(self):
        self.data_dir = project_root / "data"
        self.performance_log = self.data_dir / "atlas_performance_focused.json"
        self.diagnostic_log = self.data_dir / "atlas_diagnostic_report.json"
        self.last_check = time.time()
        self.recovery_attempts: Dict[str, int] = {}

    def check_performance(self) -> List[Dict]:
        """Check performance metrics and identify issues."""
        try:
            with open(self.performance_log) as f:
                perf_data = json.load(f)

            issues = []
            for result in perf_data.get("results", []):
                operation = result.get("operation")
                duration = result.get("duration_ms", 0)
                target = result.get("target_ms")

                if duration > (target * 2):  # Critical performance issue
                    issues.append({
                        "operation": operation,
                        "severity": "critical",
                        "duration": duration,
                        "target": target,
                        "ratio": duration / target
                    })
                elif duration > (target * 1.5):  # Warning level
                    issues.append({
                        "operation": operation,
                        "severity": "warning",
                        "duration": duration,
                        "target": target,
                        "ratio": duration / target
                    })

            return issues
        except Exception as e:
            logger.error(f"Error checking performance: {e}")
            return []

    def implement_recovery(self, issues: List[Dict]) -> None:
        """Implement recovery strategies for performance issues."""
        for issue in issues:
            operation = issue["operation"]
            severity = issue["severity"]

            # Increment recovery attempts
            if operation not in self.recovery_attempts:
                self.recovery_attempts[operation] = 0
            self.recovery_attempts[operation] += 1

            # Log the issue
            logger.warning(
                f"Performance issue detected: {operation} "
                f"({severity}, {issue['duration']:.1f}ms vs target {issue['target']}ms)"
            )

            # Implement recovery strategies
            if severity == "critical":
                self._handle_critical_issue(operation, issue)
            else:
                self._handle_warning_issue(operation, issue)

    def _handle_critical_issue(self, operation: str, issue: Dict) -> None:
        """Handle critical performance issues."""
        attempts = self.recovery_attempts[operation]

        if attempts == 1:
            # First attempt: Try clearing caches and reducing load
            logger.info(f"Attempting recovery for {operation}: Clearing caches")
            self._clear_caches()

        elif attempts == 2:
            # Second attempt: Switch to fallback implementation
            logger.info(f"Attempting recovery for {operation}: Switching to fallback")
            self._switch_to_fallback(operation)

        else:
            # Final attempt: Disable feature temporarily
            logger.warning(f"Disabling {operation} temporarily due to performance issues")
            self._disable_feature(operation)

    def _handle_warning_issue(self, operation: str, issue: Dict) -> None:
        """Handle warning-level performance issues."""
        logger.info(f"Implementing optimizations for {operation}")
        self._optimize_operation(operation)

    def _clear_caches(self) -> None:
        """Clear system caches to improve performance."""
        cache_dir = project_root / ".cache"
        if cache_dir.exists():
            try:
                for cache_file in cache_dir.glob("*"):
                    if cache_file.is_file():
                        cache_file.unlink()
                logger.info("Successfully cleared caches")
            except Exception as e:
                logger.error(f"Error clearing caches: {e}")

    def _switch_to_fallback(self, operation: str) -> None:
        """Switch to fallback implementation for an operation."""
        config_file = project_root / "config.ini"
        try:
            self._update_config(config_file, operation, "use_fallback", "true")
            logger.info(f"Switched {operation} to fallback implementation")
        except Exception as e:
            logger.error(f"Error switching to fallback: {e}")

    def _disable_feature(self, operation: str) -> None:
        """Temporarily disable a feature due to performance issues."""
        config_file = project_root / "config.ini"
        try:
            self._update_config(config_file, operation, "enabled", "false")
            logger.warning(f"Disabled {operation} due to performance issues")
        except Exception as e:
            logger.error(f"Error disabling feature: {e}")

    def _optimize_operation(self, operation: str) -> None:
        """Apply optimization strategies for an operation."""
        # Log optimization task
        dev_plan = project_root / "DEV_PLAN.md"
        if dev_plan.exists():
            try:
                with open(dev_plan, "a") as f:
                    f.write(f"\n- [ ] Optimize {operation} for better performance\n")
                logger.info(f"Added optimization task for {operation} to DEV_PLAN.md")
            except Exception as e:
                logger.error(f"Error updating DEV_PLAN.md: {e}")

    def _update_config(self, config_file: Path, section: str, key: str, value: str) -> None:
        """Update a configuration value."""
        import configparser
        config = configparser.ConfigParser()
        
        if config_file.exists():
            config.read(config_file)
            
            if section not in config:
                config[section] = {}
            
            config[section][key] = value
            
            with open(config_file, "w") as f:
                config.write(f)

    def monitor_continuously(self, check_interval: int = 600) -> None:
        """Continuously monitor performance and implement recovery strategies."""
        logger.info("Starting continuous performance monitoring")
        
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_check >= check_interval:
                    issues = self.check_performance()
                    if issues:
                        self.implement_recovery(issues)
                    self.last_check = current_time
                
                time.sleep(60)  # Check every minute if it's time for full analysis
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error before retrying

if __name__ == "__main__":
    monitor = AtlasPerformanceMonitor()
    monitor.monitor_continuously()
