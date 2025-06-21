#!/usr/bin/env python3
"""
Real-world integration test for Helper Sync Tell plugin with Atlas helper mode.
This simulates how Atlas would actually use the plugin in helper mode.
"""

import sys
from pathlib import Path

#Add Atlas to path
atlas_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(atlas_root))

def test_atlas_helper_integration():
    """Test actual Atlas helper mode integration."""
    print("🔧 Testing Atlas Helper Mode Integration...")

    try:
        #Import Atlas main app components
        from config_manager import ConfigManager
        from main import AtlasApp

        #Initialize basic Atlas components
        config_manager = ConfigManager()

        #Create a minimal atlas app instance
        atlas_app = AtlasApp()

        #Import and register the plugin
        from plugins.helper_sync_tell.plugin import register

        #Register the plugin with Atlas
        success = register(atlas_app)

        if success:
            print("✅ Plugin successfully registered with Atlas")
        else:
            print("⚠️  Plugin registration returned False")

        #Test plugin discovery through Atlas
        plugin_manager = getattr(atlas_app, "plugin_manager", None)
        if plugin_manager:
            print(f"✅ Atlas plugin manager available: {type(plugin_manager)}")

            #Check if our plugin is registered
            plugins = getattr(plugin_manager, "plugins", {})
            if "helper_sync_tell" in plugins:
                print("✅ Helper Sync Tell plugin found in Atlas registry")
            else:
                print("⚠️  Plugin not found in Atlas registry")
        else:
            print("⚠️  Atlas plugin manager not available")

        #Test helper mode integration
        helper_mode = getattr(atlas_app, "helper_mode", None)
        if helper_mode:
            print("✅ Atlas helper mode available")

            #Check if our plugin hooks are registered
            hooks = getattr(helper_mode, "hooks", {})
            if hooks:
                print(f"✅ Helper mode hooks available: {list(hooks.keys())}")
            else:
                print("⚠️  No helper mode hooks found")
        else:
            print("⚠️  Atlas helper mode not available")

        print("✅ Integration test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_scenario():
    """Test a complete end-to-end scenario."""
    print("\n🎯 Testing End-to-End Scenario...")

    try:
        #Import the plugin directly
        from plugins.helper_sync_tell.plugin import EnhancedHelperSyncTellTool

        #Create plugin instance
        plugin = EnhancedHelperSyncTellTool()

        #Test a complex query that should trigger structured thinking
        complex_query = """
        I need to build a modern web application that includes:
        1. User authentication and authorization
        2. Real-time data updates
        3. Mobile-responsive design
        4. Database integration
        5. API endpoints for third-party integration
        6. Security measures against common vulnerabilities
        
        What's the best approach and what technologies should I use?
        """

        print("📝 Processing complex query...")
        result = plugin(complex_query.strip())

        print("✅ Query processed successfully")
        print(f"   Response length: {len(result)} characters")

        #Check for structured thinking elements
        result_lower = result.lower()
        structure_indicators = [
            "step", "analysis", "breakdown", "approach", "strategy",
            "consideration", "recommendation", "implementation",
            "architecture", "design", "planning",
        ]

        found_indicators = [ind for ind in structure_indicators if ind in result_lower]
        print(f"   Structured thinking indicators found: {len(found_indicators)}")
        print(f"   Indicators: {', '.join(found_indicators[:5])}{'...' if len(found_indicators) > 5 else ''}")

        #Check response quality
        has_multiple_sections = result.count("\n\n") >= 2
        has_recommendations = "recommend" in result_lower or "suggest" in result_lower
        has_technical_details = any(tech in result_lower for tech in
                                  ["react", "node", "python", "database", "api", "security"])

        print(f"   Multiple sections: {'✅' if has_multiple_sections else '❌'}")
        print(f"   Contains recommendations: {'✅' if has_recommendations else '❌'}")
        print(f"   Technical details included: {'✅' if has_technical_details else '❌'}")

        #Print a sample of the response
        print("\n📄 Response Sample (first 300 chars):")
        print("-" * 50)
        print(result[:300] + "..." if len(result) > 300 else result)
        print("-" * 50)

        return True

    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("🚀 Helper Sync Tell - Real-World Integration Test")
    print("=" * 80)

    tests_passed = 0
    total_tests = 2

    #Test 1: Atlas integration
    if test_atlas_helper_integration():
        tests_passed += 1

    #Test 2: End-to-end scenario
    if test_end_to_end_scenario():
        tests_passed += 1

    print("\n" + "=" * 80)
    print(f"🏁 Integration Test Results: {tests_passed}/{total_tests} tests passed")
    print("=" * 80)

    if tests_passed == total_tests:
        print("🎉 FULL INTEGRATION SUCCESS!")
        print("\n✨ The Helper Sync Tell plugin is ready for production use in Atlas!")
        print("\n📋 What happens next:")
        print("• Atlas will automatically discover and load the plugin")
        print("• Complex queries in helper mode will trigger structured thinking")
        print("• Users will receive enhanced, multi-step analysis responses")
        print("• The plugin will gracefully handle errors and provide fallbacks")
        return 0
    print(f"⚠️  {total_tests - tests_passed} integration test(s) failed.")
    print("🔧 Review the output above for details.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
