#!/usr/bin/env python
"""
Code Quality Check Tool

This script runs code quality checks using linters and static analyzers.
It helps identify and fix code style issues, potential bugs, and other quality problems.
"""

import os
import subprocess
import sys
import time
from datetime import datetime


def ensure_dependencies():
    """Ensure all required linting packages are installed."""
    required_packages = ["ruff", "mypy", "pylint", "black"]
    for package in required_packages:
        try:
            subprocess.run(
                [package, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError:
            print(f"Installing required package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def run_ruff(path, fix=False):
    """Run ruff linter on the specified path."""
    print(f"\n{'-' * 20} Running Ruff {'-' * 20}")

    cmd = ["ruff", "check", path]
    if fix:
        cmd.append("--fix")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Ruff found no issues!")
    else:
        print("⚠️ Ruff found issues:")
        print(result.stdout)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"ruff_results_{timestamp}.txt"
    with open(result_file, "w") as f:
        f.write(result.stdout)

    return result.returncode == 0


def run_mypy(path):
    """Run mypy type checker on the specified path."""
    print(f"\n{'-' * 20} Running MyPy {'-' * 20}")

    cmd = ["mypy", path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ MyPy found no type issues!")
    else:
        print("⚠️ MyPy found type issues:")
        print(result.stdout)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"mypy_results_{timestamp}.txt"
    with open(result_file, "w") as f:
        f.write(result.stdout)

    return result.returncode == 0


def run_pylint(path):
    """Run pylint on the specified path."""
    print(f"\n{'-' * 20} Running Pylint {'-' * 20}")

    cmd = ["pylint", path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Pylint returns a bitmask as the exit code, so we need to check if it's 0
    if result.returncode == 0:
        print("✅ Pylint found no issues!")
    else:
        print("⚠️ Pylint found issues:")
        print(result.stdout)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"pylint_results_{timestamp}.txt"
    with open(result_file, "w") as f:
        f.write(result.stdout)

    return result.returncode == 0


def run_black(path, check_only=True):
    """Run black formatter on the specified path."""
    print(f"\n{'-' * 20} Running Black {'-' * 20}")

    cmd = ["black"]
    if check_only:
        cmd.append("--check")
    cmd.append(path)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Black found no formatting issues!")
    else:
        print("⚠️ Black found formatting issues:")
        print(result.stdout)

        if check_only:
            print("\nTo fix formatting issues, run:")
            print(f"black {path}")

    return result.returncode == 0


def generate_summary(results):
    """Generate a summary of the linting results."""
    print(f"\n{'-' * 20} Summary {'-' * 20}")

    total_issues = 0
    for tool, success in results.items():
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{tool}: {status}")
        if not success:
            total_issues += 1

    print(f"\nTotal tools with issues: {total_issues} out of {len(results)}")

    if total_issues == 0:
        print("\n🎉 All code quality checks passed!")
    else:
        print(
            "\n⚠️ Some code quality checks failed. Please fix the issues before committing."
        )


def main():
    """Main function to run the script."""
    print("Atlas Code Quality Check Tool")
    print("============================")

    # Ensure required packages are installed
    ensure_dependencies()

    # Get path from arguments or use current directory
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = (
            input(
                "Enter the path to check (or press Enter for current directory): "
            ).strip()
            or "."
        )

    # Verify the path exists
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    # Ask if fixes should be applied
    apply_fixes = input("Apply automatic fixes where possible? (y/N): ").lower() == "y"

    # Run the linters and collect results
    results = {}

    start_time = time.time()

    results["ruff"] = run_ruff(path, fix=apply_fixes)
    results["mypy"] = run_mypy(path)
    results["pylint"] = run_pylint(path)
    results["black"] = run_black(path, check_only=not apply_fixes)

    end_time = time.time()
    duration = end_time - start_time

    # Generate summary
    generate_summary(results)

    print(f"\nAnalysis completed in {duration:.2f} seconds.")

    # Return non-zero exit code if any tool failed
    sys.exit(1 if False in results.values() else 0)


if __name__ == "__main__":
    main()
