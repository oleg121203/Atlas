#!/usr/bin/env python
"""
Test Runner Script

This script runs the test suite to verify that everything works after package updates.
"""

import os
import subprocess
import sys
import time


def run_tests(with_coverage=False, coverage_target=75, fail_under=70):
    """Run the test suite.

    Args:
        with_coverage: Whether to run with coverage reporting
        coverage_target: Target percentage for coverage (for reporting)
        fail_under: Minimum acceptable coverage percentage
    """
    print("\n" + "=" * 60)
    print("Running test suite to verify functionality after package updates")
    print("=" * 60 + "\n")

    # First, make sure pytest is installed with the latest version
    print("Ensuring pytest and required plugins are up to date...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pytest",
            "pytest-cov",
            "pytest-qt",
            "pytest-html",
        ],
        check=False,
    )

    # Get the test directory
    if os.path.isdir("tests"):
        test_dir = "tests"
    else:
        print("Tests directory not found. Please run from the project root.")
        return False

    # Prepare command
    cmd = [sys.executable, "-m", "pytest", test_dir, "-v"]

    # Add coverage parameters if requested
    if with_coverage:
        print(
            f"Running with coverage reporting (target: {coverage_target}%, minimum: {fail_under}%)"
        )
        cmd.extend(
            [
                "--cov=core",
                "--cov=tools",
                "--cov=utils",
                "--cov=ui",
                "--cov=plugins",
                "--cov-report=html",
                "--cov-report=term",
                "--cov-report=xml",
                f"--cov-fail-under={fail_under}",
            ]
        )

        # Create .coveragerc if it doesn't exist to fix coverage measurement issues
        if not os.path.exists(".coveragerc"):
            with open(".coveragerc", "w") as f:
                f.write("""[run]
    source =
    core
    tools
    utils
    ui
    plugins

    [report]
    exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError

    [html]
    directory = coverage_html_report
    """)
            print("Created .coveragerc file to ensure accurate coverage reporting")

    print(f"\nRunning tests from {test_dir}...\n")
    start_time = time.time()

    # Run the tests
    result = subprocess.run(cmd, check=False)

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nTest run completed in {duration:.2f} seconds.")

    if result.returncode == 0:
        print("✅ All tests passed successfully!")

        if with_coverage:
            print("\nCoverage report generated in 'coverage_html_report/' directory")
            print(
                "Open 'coverage_html_report/index.html' in a browser to view detailed results"
            )

            # Check if coverage target was met
            if os.path.exists("coverage.xml"):
                try:
                    import xml.etree.ElementTree as ET

                    tree = ET.parse("coverage.xml")
                    root = tree.getroot()
                    if "line-rate" in root.attrib:
                        line_rate = float(root.attrib["line-rate"]) * 100
                        print(
                            f"Overall coverage: {line_rate:.2f}% (target: {coverage_target}%)"
                        )
                        if line_rate >= coverage_target:
                            print("🎉 Coverage target met!")
                        else:
                            print(
                                f"⚠️ Coverage below target by {coverage_target - line_rate:.2f}%"
                            )
                            print(
                                "  Run 'python scripts/test_coverage_enhancer.py' to improve coverage"
                            )
                except Exception as e:
                    print(f"Error parsing coverage report: {e}")

        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False


def main():
    """Main function to run the script."""
    print("Atlas Test Runner")

    # Parse arguments
    import argparse

    parser = argparse.ArgumentParser(description="Run tests for the Atlas application")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage reporting"
    )
    parser.add_argument(
        "--target",
        "-t",
        type=float,
        default=75.0,
        help="Target coverage percentage (default: 75%%)",
    )
    parser.add_argument(
        "--fail-under",
        "-f",
        type=float,
        default=70.0,
        help="Fail if coverage is below this percentage (default: 70%%)",
    )
    args = parser.parse_args()

    success = run_tests(
        with_coverage=args.coverage,
        coverage_target=args.target,
        fail_under=args.fail_under,
    )

    if success:
        print(
            "\nApplication appears to be working correctly with the updated packages."
        )
        if args.coverage:
            print(
                "\nReview the coverage report to identify areas that need more testing."
            )
            print(
                "Run 'python scripts/test_coverage_enhancer.py' to generate test templates for low-coverage modules."
            )
    else:
        print("\nPlease fix any failing tests before continuing development.")
        print(
            "You can restore the previous requirements by renaming requirements.txt.bak to requirements.txt"
        )


if __name__ == "__main__":
    main()
