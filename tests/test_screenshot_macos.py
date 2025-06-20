#!/usr/bin/env python3
"""Test screenshot functionality on macOS."""

import sys
from pathlib import Path

#Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_screenshots():
    """Test all available screenshot methods."""
    print("🍎 Testing Atlas screenshot functionality on macOS...")
    
    try:
        from utils.platform_utils import get_platform_info
        platform_info = get_platform_info()
        
        print("\n📊 Platform Information:")
        for key, value in platform_info.items():
            if any(k in key.lower() for k in ['macos', 'system', 'display']):
                print(f"  {key}: {value}")
        
        if not platform_info.get('is_macos', False):
            print("❌ This test is designed for macOS")
            return False
            
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
        return False
    
    #Test native macOS screenshot
    print("\n🔍 Testing native macOS screenshot methods...")
    
    try:
        from utils.macos_screenshot import test_screenshot_methods
        available_methods = test_screenshot_methods()
        
        if available_methods:
            print(f"✅ Available methods: {', '.join(available_methods)}")
        else:
            print("❌ No native screenshot methods available")
            
    except Exception as e:
        print(f"❌ Native screenshot test failed: {e}")
    
    #Test main screenshot function
    print("\n📸 Testing main screenshot function...")
    
    try:
        from tools.screenshot_tool import capture_screen
        
        #Capture a test screenshot
        img = capture_screen()
        
        if img:
            print(f"✅ Screenshot captured: {img.size} pixels ({img.mode})")
            
            #Save test screenshot
            test_path = Path("test_screenshot.png")
            img.save(test_path)
            print(f"✅ Screenshot saved to: {test_path}")
            
            #Clean up
            test_path.unlink(missing_ok=True)
            
            return True
        else:
            print("❌ Screenshot capture returned None")
            return False
            
    except Exception as e:
        print(f"❌ Main screenshot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_screenshots()
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed'}")
    sys.exit(0 if success else 1)
