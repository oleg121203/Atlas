#!/usr/bin/env python3
"""
Linux-specific utilities for Atlas development environment

This module provides utilities specifically for Linux development environment,
focusing on headless operation and CI/CD compatibility.
"""

import os
import subprocess
import sys
from typing import Any, Dict


def is_headless() -> bool:
    """Check if running in headless environment"""
    return not bool(os.environ.get("DISPLAY"))


def setup_linux_dev_environment() -> Dict[str, Any]:
    """Setup Linux development environment"""
    env_info = {
        "platform": "linux",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "headless": is_headless(),
        "docker_available": check_docker_availability(),
    }

    return env_info


def check_docker_availability() -> bool:
    """Check if Docker is available"""
    try:
        result = subprocess.run(
            ["docker", "--version"], check=False, capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_linux_dependencies() -> list:
    """Get Linux-specific dependencies"""
    return [
        "python3-dev",
        "python3-pip",
        "python3-venv",
        "build-essential",
        "git",
    ]


def configure_headless_operation():
    """Configure for headless operation"""
    if is_headless():
        # Set environment variables for headless mode
        os.environ["MPLBACKEND"] = "Agg"  # For matplotlib
        os.environ["QT_QPA_PLATFORM"] = "offscreen"  # For Qt applications

        print("✅ Configured for headless operation")
    else:
        print("ℹ️ GUI environment detected, headless configuration not needed")


if __name__ == "__main__":
    print("🐧 Linux Development Utilities")
    env = setup_linux_dev_environment()
    for key, value in env.items():
        print(f"  {key}: {value}")
