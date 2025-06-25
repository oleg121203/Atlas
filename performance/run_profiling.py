"""Run Performance Profiling for Atlas (ASC-025)

This script integrates profiling into the Atlas application to collect performance data as part of ASC-025. It uses the PerformanceProfiler class to profile key areas during runtime.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from performance.profiling_setup import PerformanceProfiler
import logging
from main import main  # Assuming main.py is the entry point for Atlas

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_with_profiling():
    """Run the Atlas application with performance profiling enabled."""
    profiler = PerformanceProfiler()
    
    # Start profiling the entire application
    profiler.start_profiling()
    logger.info("Starting Atlas with performance profiling")
    
    try:
        # Run the main application
        main()
    except Exception as e:
        logger.error(f"Error running Atlas: {e}")
    finally:
        # Stop profiling and save results
        profiler.stop_profiling("atlas_full_run.txt")
        logger.info("Profiling completed for full application run")


if __name__ == "__main__":
    run_with_profiling()
