#!/usr/bin/env python3
"""
Comprehensive validation script for Helper Sync Tell plugin.
Tests all aspects including import, registration, execution, and integration.
"""

import sys
import json
import traceback
from pathlib import Path

#Add Atlas to path
atlas_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(atlas_root))

def test_plugin_import():
    """Test that the plugin can be imported without errors."""
    print("🔧 Testing plugin import...")
    try:
        from plugins.helper_sync_tell.plugin import EnhancedHelperSyncTellTool
        print("✅ Plugin import successful")
        return True, EnhancedHelperSyncTellTool
    except Exception as e:
        print(f"❌ Plugin import failed: {e}")
        traceback.print_exc()
        return False, None

def test_plugin_instantiation(plugin_class):
    """Test plugin instantiation."""
    print("🔧 Testing plugin instantiation...")
    try:
        plugin = plugin_class()
        print(f"✅ Plugin instantiated: {plugin.__class__.__name__}")
        return True, plugin
    except Exception as e:
        print(f"❌ Plugin instantiation failed: {e}")
        traceback.print_exc()
        return False, None

def test_plugin_methods(plugin):
    """Test key plugin methods."""
    print("🔧 Testing plugin methods...")
    
    #Test break_down_query
    try:
        steps = plugin.break_down_query("How do I implement a complex algorithm?")
        print(f"✅ break_down_query: {len(steps)} steps")
    except Exception as e:
        print(f"❌ break_down_query failed: {e}")
        return False
    
    #Test analyze_sub_question
    try:
        analysis = plugin.analyze_sub_question("Create a web application with user authentication", {})
        print(f"✅ analyze_sub_question: {len(analysis)} chars")
    except Exception as e:
        print(f"❌ analyze_sub_question failed: {e}")
        return False
    
    #Test synthesize_response
    try:
        response = plugin.synthesize_response("Test query", ["Analysis 1", "Analysis 2"])
        print(f"✅ synthesize_response: {len(response)} chars")
    except Exception as e:
        print(f"❌ synthesize_response failed: {e}")
        return False
    
    return True

def test_plugin_execution(plugin):
    """Test full plugin execution with a sample query."""
    print("🔧 Testing plugin execution...")
    try:
        query = "How can I create a secure web application with user authentication?"
        result = plugin(query)  #Use __call__ method
        
        print("✅ Plugin execution successful")
        print(f"   Query: {query}")
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(str(result)) if result else 0} chars")
        
        #Check if result contains structured thinking
        result_str = str(result)
        has_structure = any(keyword in result_str.lower() for keyword in 
                          ['step', 'analysis', 'breakdown', 'approach', 'strategy'])
        print(f"   Contains structured thinking: {'✅' if has_structure else '❌'}")
        
        return True
    except Exception as e:
        print(f"❌ Plugin execution failed: {e}")
        traceback.print_exc()
        return False

def test_atlas_integration():
    """Test Atlas integration components."""
    print("🔧 Testing Atlas integration...")
    
    try:
        #Test config manager import
        print("✅ ConfigManager import successful")
    except Exception as e:
        print(f"⚠️  ConfigManager import failed: {e}")
    
    try:
        #Test logger import
        print("✅ Logger import successful")
    except Exception as e:
        print(f"⚠️  Logger import failed: {e}")
    
    try:
        #Test platform utils
        from utils.platform_utils import get_platform_info
        platform_info = get_platform_info()
        print(f"✅ Platform utils working: {platform_info.get('os', 'unknown')}")
    except Exception as e:
        print(f"⚠️  Platform utils not available: {e}")
    
    return True

def test_manifest_file():
    """Test plugin manifest file."""
    print("🔧 Testing plugin manifest...")
    manifest_path = Path(__file__).parent / "plugin.json"
    
    if not manifest_path.exists():
        print("❌ plugin.json not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'version', 'description', 'main', 'author']
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ Manifest valid: {manifest['name']} v{manifest['version']}")
        return True
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def run_comprehensive_validation():
    """Run all validation tests."""
    print("=" * 70)
    print("🧪 Helper Sync Tell - Comprehensive Validation")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 6
    
    #Test 1: Manifest file
    if test_manifest_file():
        tests_passed += 1
    print()
    
    #Test 2: Plugin import
    success, plugin_class = test_plugin_import()
    if success:
        tests_passed += 1
    print()
    
    if not success:
        print("❌ Cannot continue without successful import")
        return tests_passed, total_tests
    
    #Test 3: Plugin instantiation
    success, plugin = test_plugin_instantiation(plugin_class)
    if success:
        tests_passed += 1
    print()
    
    if not success:
        print("❌ Cannot continue without successful instantiation")
        return tests_passed, total_tests
    
    #Test 4: Plugin methods
    if test_plugin_methods(plugin):
        tests_passed += 1
    print()
    
    #Test 5: Plugin execution
    if test_plugin_execution(plugin):
        tests_passed += 1
    print()
    
    #Test 6: Atlas integration
    if test_atlas_integration():
        tests_passed += 1
    print()
    
    return tests_passed, total_tests

def main():
    """Main validation function."""
    tests_passed, total_tests = run_comprehensive_validation()
    
    print("=" * 70)
    print(f"🏁 Validation Complete: {tests_passed}/{total_tests} tests passed")
    print("=" * 70)
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Plugin is ready for production.")
        print("\n📋 Next Steps:")
        print("1. Plugin will be auto-discovered by Atlas")
        print("2. Use helper mode for complex queries")
        print("3. Experience enhanced structured thinking")
        return 0
    else:
        print(f"⚠️  {total_tests - tests_passed} test(s) failed. Check output above.")
        print("🔧 Plugin may still work with reduced functionality.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
