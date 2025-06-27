#!/usr/bin/env python3
"""
Test script for Self-Regeneration Manager

Tests the self-regeneration system that automatically detects and fixes issues.
"""

import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.agents.self_regeneration_manager import self_regeneration_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_self_regeneration():
    """Test the self-regeneration system."""
    print("🔧 Testing Self-Regeneration System")
    print("=" * 50)

    # Run self-regeneration
    result = self_regeneration_manager.detect_and_fix_issues()

    # Display results
    print(f"🔍 Issues Detected: {result['issues_detected']}")
    print(f"🔧 Fixes Applied: {result['fixes_applied']}")
    print(f"🏥 System Health: {result['system_health']}")

    # Display issues
    if result["issues"]:
        print("\n📋 Issues Found:")
        for i, issue in enumerate(result["issues"], 1):
            print(f"  {i}. {issue['type']}: {issue['description']}")
            print(f"     Severity: {issue['severity']}")

    # Display fixes
    if result["fixes"]:
        print("\n✅ Fixes Applied:")
        for i, fix in enumerate(result["fixes"], 1):
            print(
                f"  {i}. {fix['fix_type']}: {fix.get('method', fix.get('file', fix.get('module', 'Unknown')))}"
            )
            print(f"     Success: {fix['success']}")
            if not fix["success"] and "error" in fix:
                print(f"     Error: {fix['error']}")

    print("\n" + "=" * 50)
    return result


def test_missing_method_detection():
    """Test detection of missing methods."""
    print("🧪 Testing Missing Method Detection")
    print("=" * 50)

    # Check for specific missing methods
    method_checks = [
        ("agents.hierarchical_plan_manager.HierarchicalPlanManager", "execute_plan"),
        (
            "agents.adaptive_execution_manager.AdaptiveExecutionManager",
            "execute_with_adaptation",
        ),
        ("agents.tool_registry.ToolRegistry", "select_tool"),
        ("agents.email_strategy_manager.EmailStrategyManager", "execute_email_task"),
    ]

    for class_path, method_name in method_checks:
        try:
            module_name, class_name = class_path.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            class_obj = getattr(module, class_name)

            if hasattr(class_obj, method_name):
                print(f"✅ {class_path}.{method_name} - EXISTS")
            else:
                print(f"❌ {class_path}.{method_name} - MISSING")

        except (ImportError, AttributeError) as e:
            print(f"⚠️  {class_path}.{method_name} - ERROR: {e}")

    print("=" * 50)


def test_import_issues():
    """Test detection of import issues."""
    print("🧪 Testing Import Issues Detection")
    print("=" * 50)

    # Check critical imports
    critical_imports = [
        ("agents.adaptive_execution_manager", "AdaptiveExecutionManager"),
        ("agents.email_strategy_manager", "EmailStrategyManager"),
        ("agents.tool_registry", "ToolRegistry"),
        ("agents.hierarchical_plan_manager", "HierarchicalPlanManager"),
        ("tools.browser", "BrowserTool"),
        ("tools.email", "EmailTool"),
    ]

    for module_name, class_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name} - EXISTS")
            else:
                print(f"❌ {module_name}.{class_name} - MISSING")
        except ImportError as e:
            print(f"⚠️  {module_name}.{class_name} - IMPORT ERROR: {e}")

    print("=" * 50)


def test_file_existence():
    """Test detection of missing files."""
    print("🧪 Testing File Existence")
    print("=" * 50)

    # Check for important files
    important_files = [
        "agents/self_regeneration_manager.py",
        "agents/adaptive_execution_manager.py",
        "agents/hierarchical_plan_manager.py",
        "tools/browser/__init__.py",
        "tools/email/__init__.py",
        "config/config-macos.ini",
    ]

    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - MISSING")

    print("=" * 50)


def test_regeneration_history():
    """Test regeneration history tracking."""
    print("🧪 Testing Regeneration History")
    print("=" * 50)

    # Get regeneration history
    history = self_regeneration_manager.get_regeneration_history()
    fixes = self_regeneration_manager.get_fixes_applied()

    print(f"📊 Regeneration History: {len(history)} entries")
    print(f"🔧 Fixes Applied: {len(fixes)} fixes")

    if fixes:
        print("\n📋 Recent Fixes:")
        for i, fix in enumerate(fixes[-5:], 1):  # Show last 5 fixes
            print(
                f"  {i}. {fix['fix_type']}: {fix.get('method', fix.get('file', fix.get('module', 'Unknown')))}"
            )
            print(f"     Success: {fix['success']}")

    print("=" * 50)


def main():
    """Run all tests."""
    print("🚀 Starting Self-Regeneration Manager Tests")
    print("=" * 60)

    try:
        # Test file existence
        test_file_existence()

        # Test import issues
        test_import_issues()

        # Test missing method detection
        test_missing_method_detection()

        # Test regeneration history
        test_regeneration_history()

        # Test self-regeneration
        regeneration_result = test_self_regeneration()

        # Summary
        print("📋 Test Summary")
        print("=" * 60)
        print(f"System Health: {regeneration_result['system_health']}")
        print(f"Issues Detected: {regeneration_result['issues_detected']}")
        print(f"Fixes Applied: {regeneration_result['fixes_applied']}")

        if regeneration_result["fixes_applied"] > 0:
            print(
                "✅ Self-regeneration system is working - issues were detected and fixed!"
            )
        else:
            print("ℹ️  No issues detected - system is healthy")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 Self-Regeneration Manager Tests Completed!")


if __name__ == "__main__":
    main()
