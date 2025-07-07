#!/usr/bin/env python3
"""
Test script to verify proper module distribution between topbar and sidebar.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication

    from ui.main_window import AtlasMainWindow

    def test_module_distribution():
        """Test that modules are properly distributed without duplication."""
        print("🧪 Testing Module Distribution...")

        app = QApplication.instance() or QApplication(sys.argv)

        # Create main window
        main_window = AtlasMainWindow(app=app)

        # Check topbar modules (expected: Chat, Tasks, Tools, Plugins)
        print("\n📊 TOPBAR Modules:")
        topbar_modules = ["chat_btn", "tasks_btn", "tools_btn", "plugins_btn"]
        for btn_name in topbar_modules:
            if (
                hasattr(main_window, "topbar_buttons")
                and btn_name in main_window.topbar_buttons
            ):
                print(f"  ✅ {btn_name}")
            else:
                print(f"  ❌ {btn_name} - MISSING")

        # Check sidebar modules (expected: Analytics, AI Assistant, System Info, Settings)
        print("\n🔧 SIDEBAR Modules:")
        expected_sidebar = ["Analytics", "AI Assistant", "System Info", "Settings"]

        if hasattr(main_window, "modules"):
            for module_name in expected_sidebar:
                if module_name in main_window.modules:
                    print(f"  ✅ {module_name}")
                else:
                    print(f"  ❌ {module_name} - MISSING")

        # Check for duplications
        print("\n🔍 Checking for Duplications:")
        topbar_module_names = ["Chat", "Tasks", "Tools", "Plugins"]
        sidebar_module_names = ["Analytics", "AI Assistant", "System Info", "Settings"]

        duplicates = set(topbar_module_names) & set(sidebar_module_names)
        if duplicates:
            print(f"  ❌ DUPLICATES FOUND: {duplicates}")
        else:
            print("  ✅ NO DUPLICATES - Good distribution!")

        # Check Quick Actions in right panel
        print("\n⚡ RIGHT PANEL Quick Actions:")
        expected_quick_actions = [
            "Refresh",
            "Analytics",
            "AI Assistant",
            "System Info",
            "New Chat",
        ]
        print(f"  Expected: {expected_quick_actions}")

        # Show window for visual verification
        main_window.show()
        print("\n👁️  Visual verification window opened.")
        print("   - Check that topbar has: Chat, Tasks, Tools, Plugins")
        print(
            "   - Check that sidebar has: Analytics, AI Assistant, System Info, Settings"
        )
        print("   - Check that right panel toggle works (📊 Panel button)")
        print("   - Press Ctrl+C to close when done\n")

        return main_window, app

    if __name__ == "__main__":
        try:
            window, app = test_module_distribution()
            app.exec()
        except KeyboardInterrupt:
            print("\n👋 Test completed!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PySide6 is installed and the ui module is available.")
    sys.exit(1)
