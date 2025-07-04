#!/usr/bin/env python
"""
Package Update Script

This script checks for outdated packages and updates them.
It also generates an updated requirements.txt file.
"""

import os
import subprocess
import sys


def check_outdated_packages():
    """Check for outdated packages and return the results."""
    print("Checking for outdated packages...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error checking outdated packages: {result.stderr}")
        return []

    import json

    try:
        outdated = json.loads(result.stdout)
        if outdated:
            print(f"Found {len(outdated)} outdated package(s):")
            for pkg in outdated:
                print(f"  {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
        else:
            print("All packages are up to date!")
        return outdated
    except json.JSONDecodeError:
        print(f"Error parsing pip output: {result.stdout}")
        return []


def update_packages(packages):
    """Update the specified packages."""
    if not packages:
        return

    print("\nUpdating packages...")
    for pkg in packages:
        pkg_name = pkg["name"]
        latest_version = pkg["latest_version"]
        print(f"Updating {pkg_name} to {latest_version}...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                f"{pkg_name}=={latest_version}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  ✓ Successfully updated {pkg_name} to {latest_version}")
        else:
            print(f"  ✗ Failed to update {pkg_name}: {result.stderr}")


def generate_requirements():
    """Generate updated requirements.txt file."""
    print("\nGenerating updated requirements.txt file...")

    # First create a backup of the current requirements.txt
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            original_content = f.read()

        with open("requirements.txt.bak", "w") as f:
            f.write(original_content)
        print("Created backup at requirements.txt.bak")

    # Generate new requirements with precise versions
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True
    )

    if result.returncode == 0:
        # Parse the original requirements file to preserve comments and structure
        with open("requirements.txt", "r") as f:
            lines = f.readlines()

        # Create a dictionary of all installed packages
        freeze_output = result.stdout.strip().split("\n")
        installed_packages = {}
        for line in freeze_output:
            if "==" in line:
                pkg_name, version = line.split("==", 1)
                installed_packages[pkg_name.lower()] = version

        # Update versions in the original requirements file
        updated_lines = []
        for line in lines:
            line = line.rstrip()
            if line and not line.startswith("#") and "==" in line:
                pkg_info = line.split("==", 1)
                pkg_name = pkg_info[0].strip().lower()
                if pkg_name in installed_packages:
                    updated_lines.append(
                        f"{pkg_info[0]}=={installed_packages[pkg_name]}"
                    )
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Write the updated requirements file
        with open("requirements.txt", "w") as f:
            f.write("\n".join(updated_lines) + "\n")

        print("Requirements file updated successfully!")
    else:
        print(f"Error generating requirements: {result.stderr}")


def main():
    """Main function to run the script."""
    print("Python Package Update Tool\n")
    outdated = check_outdated_packages()

    if outdated:
        response = input("\nDo you want to update these packages? (y/n): ")
        if response.lower() == "y":
            update_packages(outdated)
            generate_requirements()
            print(
                "\nPackage update completed! Please test your application to ensure everything works correctly."
            )
        else:
            print("\nUpdate cancelled.")
    else:
        print("\nNo packages to update.")


if __name__ == "__main__":
    main()
