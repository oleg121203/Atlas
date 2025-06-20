#!/usr/bin/env python3
"""
Quick verification script for macOS screenshot fix.
This script tests if the 'CGImageRef' object has no attribute 'width' error is resolved.
"""

import sys
import traceback

def test_quartz_fix():
    """Test if the Quartz screenshot fix is working."""
    print("Testing macOS Screenshot Fix")
    print("=" * 40)
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("❌ This test is for macOS only")
        return False
    
    # Test 1: Import check
    print("1. Testing Quartz imports...")
    try:
        from Quartz import (
            CGWindowListCreateImage, CGRectInfinite, kCGWindowListOptionOnScreenOnly,
            CGMainDisplayID, kCGWindowImageDefault, CGImageGetWidth, CGImageGetHeight,
            CGImageGetBytesPerRow, CGImageGetDataProvider, CGDataProviderCopyData
        )
        print("   ✅ All Quartz functions imported successfully")
    except ImportError as e:
        print(f"   ❌ Quartz import failed: {e}")
        return False
    
    # Test 2: CGImage creation
    print("2. Testing CGImage creation...")
    try:
        image_ref = CGWindowListCreateImage(
            CGRectInfinite, kCGWindowListOptionOnScreenOnly, CGMainDisplayID(), kCGWindowImageDefault
        )
        if image_ref:
            print("   ✅ CGImage created successfully")
        else:
            print("   ❌ Failed to create CGImage")
            return False
    except Exception as e:
        print(f"   ❌ CGImage creation failed: {e}")
        return False
    
    # Test 3: Modern API usage (the fix)
    print("3. Testing modern API usage...")
    try:
        # This should NOT cause the 'width' attribute error anymore
        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        
        print(f"   ✅ Image properties: {width}x{height}, bytes_per_row: {bytes_per_row}")
        
        # Test data extraction
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)
        
        if hasattr(data, 'bytes'):
            buffer = data.bytes()
        else:
            buffer = bytes(data)
        
        print(f"   ✅ Image data extracted: {len(buffer)} bytes")
        
    except AttributeError as e:
        if "'CGImageRef' object has no attribute 'width'" in str(e):
            print(f"   ❌ OLD BUG STILL PRESENT: {e}")
            print("   💡 The fix has not been applied or is not working")
            return False
        else:
            print(f"   ❌ Unexpected AttributeError: {e}")
            return False
    except Exception as e:
        print(f"   ❌ Modern API test failed: {e}")
        return False
    
    # Test 4: PIL integration
    print("4. Testing PIL integration...")
    try:
        from PIL import Image
        
        # Create PIL Image from buffer
        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)
        print(f"   ✅ PIL Image created: {img.size[0]}x{img.size[1]}, mode: {img.mode}")
        
        # Test RGB conversion
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])
            print(f"   ✅ RGB conversion successful: {rgb_img.mode}")
        
    except Exception as e:
        print(f"   ❌ PIL integration failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The screenshot fix is working correctly.")
    return True

def test_integrated_tool():
    """Test the integrated screenshot tool."""
    print("\n" + "=" * 40)
    print("Testing Integrated Screenshot Tool")
    print("=" * 40)
    
    try:
        # Import our screenshot tool
        sys.path.insert(0, '.')
        from tools.screenshot_tool import capture_screen
        
        print("1. Screenshot tool imported successfully")
        
        # Test capture
        img = capture_screen()
        if img:
            print(f"2. ✅ Screenshot captured: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}")
            return True
        else:
            print("2. ❌ Screenshot returned None")
            return False
            
    except Exception as e:
        print(f"❌ Integrated tool test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("macOS Screenshot Fix Verification")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print()
    
    success = True
    
    # Test the core fix
    if not test_quartz_fix():
        success = False
    
    # Test the integrated tool
    if not test_integrated_tool():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 VERIFICATION SUCCESSFUL")
        print("The macOS screenshot fix is working correctly!")
    else:
        print("❌ VERIFICATION FAILED")
        print("Some issues were detected. Please check the error messages above.")
        print("\nFor troubleshooting:")
        print("- Run: pip install --upgrade pyobjc-framework-Quartz")
        print("- Check System Preferences → Security & Privacy → Screen Recording")
        print("- Run: python3 test_screenshot_complete.py for detailed diagnostics")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
