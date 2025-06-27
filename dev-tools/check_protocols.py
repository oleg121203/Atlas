#!/usr/bin/env python3
"""
Atlas Protocols Diagnostic Tool

Checks if critical protocol files and security mechanisms are in place.
"""

import importlib.util
import os


def check_file_exists(path, description):
    """Check if a file exists and print its status."""
    exists = os.path.isfile(path)
    print(f"[{'✓' if exists else '✗'}] {description}: {path}")
    return exists


def import_and_check_class(module_path, class_name, description):
    """Import a module and check if a class exists."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_path.replace("/", "."), module_path
        )
        if not spec or not spec.loader:
            print(f"[✗] Could not load module: {module_path}")
            return False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class_exists = hasattr(module, class_name)
        print(
            f"[{'✓' if class_exists else '✗'}] {description}: {class_name} in {module_path}"
        )

        if class_exists:
            cls = getattr(module, class_name)
            # Check for specific methods
            methods = [
                m
                for m in dir(cls)
                if not m.startswith("_") and callable(getattr(cls, m))
            ]
            print(
                f"    - Methods: {', '.join(methods[:5])}{'...' if len(methods) > 5 else ''}"
            )

        return class_exists
    except Exception as e:
        print(f"[✗] Error checking {module_path}: {e}")
        return False


def run_protocol_diagnostic():
    """Run diagnostic checks for Atlas protocols."""
    print("=" * 60)
    print("ATLAS PROTOCOLS DIAGNOSTIC TOOL")
    print("=" * 60)

    # Current working directory
    cwd = os.getcwd()
    print(f"Working directory: {cwd}")
    print("-" * 60)

    # Check essential files
    critical_files = [
        ("main.py", "Main entry point"),
        ("agents/encrypted_creator_protocols.py", "Encrypted Creator Protocols"),
        ("agents/creator_authentication.py", "Creator Authentication System"),
        ("utils/security_doc_crypto.py", "Security Documentation Crypto"),
        (
            "docs/reports/security/SECURITY_SYSTEM_REPORT.md.encrypted",
            "Encrypted Security Report",
        ),
    ]

    all_files_exist = True
    for file_path, description in critical_files:
        all_files_exist &= check_file_exists(file_path, description)

    print("-" * 60)

    # Check classes
    critical_classes = [
        (
            "agents/encrypted_creator_protocols.py",
            "EncryptedCreatorProtocols",
            "Creator Protocol System",
        ),
        (
            "agents/creator_authentication.py",
            "CreatorAuthentication",
            "Creator Authentication System",
        ),
    ]

    all_classes_exist = True
    for module_path, class_name, description in critical_classes:
        all_classes_exist &= import_and_check_class(
            module_path, class_name, description
        )

    print("-" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("-" * 60)
    print(
        f"Essential files status: {'All present' if all_files_exist else 'Some missing'}"
    )
    print(
        f"Critical classes status: {'All present' if all_classes_exist else 'Some missing'}"
    )

    if all_files_exist and all_classes_exist:
        print("\n✅ Atlas protocols appear to be intact.")
        print("The system should be able to authenticate the creator correctly.")
    else:
        print("\n❌ Some critical components are missing.")
        print("Atlas may not be able to properly authenticate the creator.")

    print("=" * 60)


if __name__ == "__main__":
    run_protocol_diagnostic()
